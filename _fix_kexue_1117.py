#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""2026-11-17 纠偏：科学养鱼 OCR 通道更新至 11-17 + 数据归属修正（幂等）。

用户指出「科学养鱼数据还停在 2026-11-05」。检测结论：
  1. kexue（OCR 截图快照通道，eff 由 wechat_ocr_current.json 的 price_date 反推）停在 11-05——
     用户 11-17 提交的科学养鱼 App 截图本质属该通道，昨批误挂到 kexue_web（正文表格通道）。
  2. 修正：把 11-17 截图 6 条鳜鱼行写入 wechat_ocr_current.json「科学养鱼」段 → 重跑
     inject_kexue_block.py 更新 OCR 自动区块；删除昨批误插的 kexue_web 截图卡；
     kexue_web 日期回退 11-13（该通道最新正文表格期）。
  3. qianyan 显示 11-02 的原因：eff["qianyan"] 读 qianyan_state.json（不读 manual_dates）——
     昨晚只更新了 manual_dates，状态文件没动。更新 qianyan_state.json 为第 39 期 / 2026-11-17。
  4. 周报源 cadence 修正：tengshi 2→7、tengshi_gui 2→7、tongwei 1→7、hainong 1→7
     （周报源按 3 天判定会误报红；周期与实际发布节奏对齐）。
  5. 无新数据如实保持的源：ayu（a渔业行情 OCR，2026-09-15 后用户未再提供截图）、
     tengshi（腾氏一周鱼价播报最新期仍 11-07，通威同源 11-13 已在 tongwei 通道）、
     tengshi_gui（海南卓越联合播报最新期 11-12）——不伪造日期。
"""
import json
import re
import sys

HTML = "鳜鱼鲈鱼价格看板.html"
STATE = "wechat_ocr_current.json"

KX_DATE = "2026-11-17"
# 用户 11-17 科学养鱼 App 截图（逐张核校）：鳜鱼段可见 6 条有价行；
# 宜昌三峡物流园行价格被截图截断不录；泥鳅行按约定不录；加州鲈段未见。
# App 列表无涨跌对比列 → vs 统一「—」。
NEW_ROWS = [
    {"source": "科学养鱼", "article_date": KX_DATE, "price_date": KX_DATE,
     "species": "鳜鱼（桂花鱼）", "market": "山西太原五龙口海鲜市场",
     "spec": "500≤条重＜750克", "price": 65.0, "unit": "元/千克", "vs": "—", "note": "App 截图核校"},
    {"source": "科学养鱼", "article_date": KX_DATE, "price_date": KX_DATE,
     "species": "鳜鱼（桂花鱼）", "market": "江苏省苏州市南环桥农副产品批发市场",
     "spec": "250≤条重＜500克", "price": 50.5, "unit": "元/千克", "vs": "—", "note": "与淡水渔业 11-16 同值并列"},
    {"source": "科学养鱼", "article_date": KX_DATE, "price_date": KX_DATE,
     "species": "鳜鱼（桂花鱼）", "market": "江苏省苏州市南环桥农副产品批发市场",
     "spec": "500≤条重＜750克", "price": 55.5, "unit": "元/千克", "vs": "—", "note": "与淡水渔业 11-16 同值并列"},
    {"source": "科学养鱼", "article_date": KX_DATE, "price_date": KX_DATE,
     "species": "鳜鱼（桂花鱼）", "market": "乌鲁木齐北园春果业经营有限责任公司",
     "spec": "500≤条重＜750克", "price": 120.0, "unit": "元/千克", "vs": "—", "note": "远端销区极端价照录"},
    {"source": "科学养鱼", "article_date": KX_DATE, "price_date": KX_DATE,
     "species": "鳜鱼（桂花鱼）", "market": "江苏凌家塘市场发展有限公司",
     "spec": "500≤条重＜750克", "price": 54.0, "unit": "元/千克", "vs": "—", "note": ""},
    {"source": "科学养鱼", "article_date": KX_DATE, "price_date": KX_DATE,
     "species": "鳜鱼（桂花鱼）", "market": "广州黄沙水产交易市场有限公司",
     "spec": "条重≥750克", "price": 54.0, "unit": "元/千克", "vs": "—", "note": ""},
]
VS_HEADER = "涨跌（截图未给）"

# 昨批误挂 kexue_web 的截图卡（整卡精确删除）
KX_CARD_ANCHOR = "🌊 11月17日 · 科学养鱼 分市场批发价（App 截图核校"

CHIP_OLD = "科学养鱼分市场批发价（11-05OCR/11-10合并/11-13正文/11-17截图）"
CHIP_NEW = "科学养鱼分市场批发价（11-05OCR/11-10合并/11-13正文/11-17App截图·OCR通道）"

QY_STATE = {
    "latest_issue": 39,
    "latest_date": "2026-11-17",
    "source": "水产前沿《特水鱼周报 2026 第39期》",
    "note": ("2026-11-17 手动录入第39期(11-17 18:23 发布，链接 Xqbk_JMSOdkAS5b9VbR8Rg)；"
             "第38期(10-26/11-02)此前已录。特水鱼周报第 36 期及更早未收录。"),
}


def balance(text):
    return {t: len(re.findall(r"<" + t + r"(?=[\s>])", text)) - text.count("</" + t + ">")
            for t in ("section", "div", "table", "thead", "tbody", "tr", "td", "th", "b")}


def main():
    # ---- 1) wechat_ocr_current.json：科学养鱼段 → 11-17（11-05 已有 prices 快照存档）----
    d = json.load(open(STATE, encoding="utf-8"))
    if d.get("科学养鱼") and d["科学养鱼"][0].get("price_date") == KX_DATE:
        print("[SKIP] wechat_ocr_current.json 已是", KX_DATE)
    else:
        d["科学养鱼"] = [dict(r, vs_header=VS_HEADER) for r in NEW_ROWS]
        json.dump(d, open(STATE, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        print("[OK] wechat_ocr_current.json 科学养鱼段 →", KX_DATE, "共", len(NEW_ROWS), "条（11-05 快照已在 wechat_ocr_prices_20261105.json）")

    # ---- 2) v1 HTML：删除昨批误挂 kexue_web 的截图卡 ----
    html = open(HTML, encoding="utf-8").read()
    before = balance(html)
    n = html.count(KX_CARD_ANCHOR)
    if n == 1:
        i = html.find(KX_CARD_ANCHOR)
        pos = html.rfind('<div class="card"', 0, i)
        # 卡尾：该卡 legend 之后闭合的 </div> —— 从卡起点向后找第一个 "</div> \n" 卡边界不可靠，
        # 改用「下一张卡的 <div class="card"」或区块结束标记兜底
        nxt = html.find('<div class="card"', i)
        # 该卡之后紧跟的元素是下一张卡（淡水渔业 11-16 卡）或锚点区块结尾
        end = html.rfind("</div>", pos, nxt + 200)
        # 精确策略：卡结构为 <div class="card"> ... <div class="legend">...</div> </div>
        li = html.find('<div class="legend">', i)
        assert li > 0
        lend = html.find("</div>", li)
        card_end = html.find("</div>", lend + 6) + 6  # 卡外层闭合
        block = html[pos:card_end]
        assert KX_CARD_ANCHOR in block and block.count('<div class="card"') == 1
        html = html[:pos] + html[card_end:]
        print("[OK] 已删除 kexue_web 误挂截图卡（", len(block.encode('utf-8')), "bytes ）")
    elif n == 0:
        print("[SKIP] kexue_web 误挂截图卡不存在（已删除）")
    else:
        raise AssertionError("kexue 截图卡锚点异常: %d" % n)
    # chip 段说明更新
    if CHIP_NEW in html:
        print("[SKIP] chip 段说明已更新")
    else:
        assert html.count(CHIP_OLD) == 1, ("chip", html.count(CHIP_OLD))
        html = html.replace(CHIP_OLD, CHIP_NEW, 1)
    after = balance(html)
    assert before == after, f"标签配平差值变化：{before} → {after}"
    open(HTML, "w", encoding="utf-8").write(html)
    print("[OK] v1 HTML 写盘 · chip 段说明更新 · 配平", after["div"])

    # ---- 3) manifest：kexue=11-17、kexue_web=11-13、周报 cadence 修正 ----
    m = json.load(open("data_sources_manifest.json", encoding="utf-8"))
    m["manual_dates"]["kexue"] = KX_DATE
    m["manual_dates"]["kexue_web"] = "2026-11-13"
    cad = {"tengshi": 7, "tengshi_gui": 7, "tongwei": 7, "hainong": 7}
    for s in m["sources"]:
        if s["key"] in cad and s.get("cadence") != cad[s["key"]]:
            print(f"[OK] cadence {s['key']}: {s.get('cadence')} → {cad[s['key']]}（周报节奏）")
            s["cadence"] = cad[s["key"]]
    json.dump(m, open("data_sources_manifest.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2)

    # ---- 4) qianyan_state.json → 第 39 期 / 11-17 ----
    old_qy = json.load(open("qianyan_state.json", encoding="utf-8"))
    if old_qy.get("latest_date") != KX_DATE:
        json.dump(QY_STATE, open("qianyan_state.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2)
        print("[OK] qianyan_state.json → 第39期 / 2026-11-17")
    else:
        print("[SKIP] qianyan_state.json 已是 2026-11-17")
    return 0


if __name__ == "__main__":
    sys.exit(main())
