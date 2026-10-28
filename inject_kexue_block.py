#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""科学养鱼公众号批发价区块自动注入（v1 看板）

数据源：wechat_ocr_current.json 的「科学养鱼」段
（每日文章由用户提供链接/截图 → 人工核校后写入该状态文件）
作用区间：HTML 注释 <!-- 科学养鱼公众号 OCR 数据 --> ... <!-- /科学养鱼公众号 OCR 数据 -->
特性：幂等（内容无变化不写回）；单位为元/千克；涨跌按 vs 字段着色。

用法：
  python3 inject_kexue_block.py            # 写回 HTML
  python3 inject_kexue_block.py --check    # 只体检
  python3 inject_kexue_block.py --dry-run  # 打印将生成的区块
"""
import argparse
import json
import statistics as st

HTML = "鳜鱼鲈鱼价格看板.html"
STATE = "wechat_ocr_current.json"
SRC = "科学养鱼"
START = "<!-- 科学养鱼公众号 OCR 数据 -->"
END = "<!-- /科学养鱼公众号 OCR 数据 -->"

SPECIES_ORDER = ["鳜鱼（桂花鱼）", "加州鲈鱼"]
TAG = {"鳜鱼（桂花鱼）": "tag-gui", "加州鲈鱼": "tag-lu"}
C_NEW, C_FLAT, C_UP, C_DOWN = "#2563eb", "#6b7280", "#dc2626", "#12a150"


def load_rows():
    with open(STATE, encoding="utf-8") as f:
        data = json.load(f)
    return data.get(SRC, [])


def vs_color(vs: str) -> str:
    if "新增" in vs:
        return C_NEW
    if "持平" in vs:
        return C_FLAT
    if "↑" in vs:
        return C_UP
    if "↓" in vs:
        return C_DOWN
    return C_FLAT


def esc(t: str) -> str:
    return (t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


def build_table(species: str, rows: list, vs_header: str) -> str:
    rows = sorted(rows, key=lambda r: -r["price"])
    trs = []
    for r in rows:
        col = vs_color(r.get("vs", ""))
        trs.append(
            "<tr><td>" + esc(r["market"]) + "</td>"
            '<td><span class="spec spec-s">' + esc(r["spec"]) + "</span></td>"
            '<td class="price">' + "{:.2f}".format(r["price"]) + "</td>"
            '<td style="color:' + col + ';font-size:12px;white-space:nowrap">'
            + esc(r.get("vs", "")) + "</td></tr>"
        )
    return (
        '<div><h3 style="font-size:14px;margin:6px 0 8px">'
        '<span class="tag ' + TAG.get(species, "tag-gui") + '">' + esc(species) + "</span>"
        " 批发价（元/千克）</h3><table><thead><tr><th>市场</th><th>规格</th><th>价格</th><th>"
        + esc(vs_header) + "</th></tr></thead><tbody>" + "".join(trs) + "</tbody></table></div>"
    )


def build_block(rows: list) -> str:
    if not rows:
        return None
    date = max(r["price_date"] for r in rows)
    vs_header = rows[0].get("vs_header", "vs 上期")
    gui = [r for r in rows if r["species"] == "鳜鱼（桂花鱼）"]
    lu = [r for r in rows if r["species"] == "加州鲈鱼"]
    med_gui = st.median([r["price"] for r in gui]) if gui else None
    med_lu = st.median([r["price"] for r in lu]) if lu else None

    note = date + " · 元/千克 · 已按原文数字录入"
    csub = (
        "来源：微信公众号「科学养鱼」《" + date + "批发价格》，单位<b>元/千克</b>；"
        "报价日期 <b>" + date + "</b>。本次含 <b>鳜鱼（桂花鱼）" + str(len(gui)) + " 条 / 加州鲈鱼 "
        + str(len(lu)) + " 条</b>，共 " + str(len(rows)) + " 条。"
    )
    if med_gui:
        csub += ("　鳜鱼中位数 <b>" + "{:.0f}".format(med_gui) + " 元/千克（≈"
                 + "{:.1f}".format(med_gui / 2) + " 元/斤）</b>；")
    if med_lu:
        csub += ("加州鲈中位数 <b>" + "{:.0f}".format(med_lu) + " 元/千克（≈"
                 + "{:.1f}".format(med_lu / 2) + " 元/斤）</b>。")

    tables = "".join(build_table(sp, [r for r in rows if r["species"] == sp], vs_header)
                     for sp in SPECIES_ORDER if any(r["species"] == sp for r in rows))

    callout = (
        '<div class="callout" style="margin-top:14px"><b>数据说明：</b>'
        "该公众号价格以<b>图片/图文混排</b>形式发布，纯文本爬虫取不到数字；由原文数字人工核校录入。"
        "① 单位已确认为<b>元/千克</b>（括号内元/斤按 1 千克 = 2 斤换算，仅便于比对）；"
        "② 属<b>批发价</b>，可与农业农村部（MOA）统货口径互补；"
        "③ 全国中枢一律取<b>中位数</b>，避免乌鲁木齐等远距离销区极值单侧拉动；"
        "④ 历史期数据保留于 <code>wechat_ocr_prices_*.json</code> 快照，"
        "更新只需改 <code>wechat_ocr_current.json</code> 后重跑本脚本。"
        "<br><b>口径提示：</b>批发价不可直接当收购上限，须倒扣流通成本（鳜鱼约 3 元/斤、鲈鱼约 1 元/斤）；"
        "远距离销区（乌鲁木齐、甘肃、宁夏等）只作销地参考，不构成跨区套利。"
        "</div>"
    )

    return (
        START + "\n"
        '  <section class="collapsible">\n'
        '    <div class="sec-head">\n'
        '      <span class="bar" style="background:#7c3aed"></span>\n'
        '      <h2>补充 · 「科学养鱼」公众号批发价（OCR 提取）</h2>\n'
        '      <span class="note">' + esc(note) + "</span>\n"
        "    </div>\n"
        '    <div class="card">\n'
        "      <h3>🌟 科学养鱼公众号 全国水产品批发价</h3>\n"
        '      <div class="csub">' + csub + "</div>\n"
        '      <div class="grid2">' + tables + "</div>\n"
        "      " + callout + "\n"
        "    </div>\n"
        "  </section>\n"
        "  "
    )


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    rows = load_rows()
    block = build_block(rows)
    if block is None:
        print("[WARN] 无科学养鱼数据，保留看板原值")
        return 0

    with open(HTML, encoding="utf-8") as f:
        html = f.read()
    i, j = html.index(START), html.index(END)
    new_html = html[:i] + block + html[j:]

    if args.dry_run:
        print(block)
        return 0
    if args.check:
        print("[check] 数据日 {} · 共 {} 条 · HTML {}".format(
            max(r["price_date"] for r in rows), len(rows),
            "需更新" if new_html != html else "已最新"))
        return 0
    if new_html != html:
        with open(HTML, "w", encoding="utf-8") as f:
            f.write(new_html)
        print("[OK] 已注入科学养鱼区块 · 数据日 {} · {} 条".format(
            max(r["price_date"] for r in rows), len(rows)))
    else:
        print("[OK] 无需改动（已是最新）")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
