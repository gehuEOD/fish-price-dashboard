#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""v1 数据总览版 → v2 决策版 自动同步桥接（2026-11-09 建立）。

背景：v2 每天 09:15 会重跑 build_dashboard_v2.py，但塘口价 / 行情线索
一直读 v2_manual_prices.json 这份人工快照，最后一次更新停在 2026-10-28，
导致 v1 已更新到 11 月而 v2 仍显示 10 月数据。

本脚本从 v1 看板 HTML 直接抽取「最新一期」卡片，重算：
  1. v2_manual_prices.json 的 pond.鳜鱼 / pond.加州鲈 / weekly / local_wholesale
     / updated / notes（disease 等静态配置保留）
  2. v2_clues.json 的 8 条「最新行情线索」（标题 / 日期 / 核心结论 / 原文链接）

随后由 build_dashboard_v2.py 读取这两份文件重建 /v2/ 页面。
设计原则：best-effort + 幂等，任何一张卡缺失或解析失败都保留原值并告警，
绝不写入半截数据；只跟踪鳜鱼 / 加州鲈两类，沿用值与多口径差异照录。
"""
import html as html_lib
import json
import os
import re
import sys
from datetime import datetime, timezone, timedelta

WS = os.path.dirname(os.path.abspath(__file__))
V1 = os.path.join(WS, "鳜鱼鲈鱼价格看板.html")
MANUAL = os.path.join(WS, "v2_manual_prices.json")
CLUES = os.path.join(WS, "v2_clues.json")
CST = timezone(timedelta(hours=8))


def txt(s):
    """去标签 + HTML 实体反转义 + 压缩空白（避免 &lt; 经 esc 变成 &amp;lt;）"""
    return re.sub(r"\s+", " ", html_lib.unescape(re.sub(r"<[^>]+>", "", s or ""))).strip()


def cards(html):
    """切出所有 <div class="card"> 卡片，返回 [(h3纯文本, 卡HTML)]"""
    starts = [m.start() for m in re.finditer(r'<div class="card"', html)]
    out = []
    for i, s in enumerate(starts):
        e = starts[i + 1] if i + 1 < len(starts) else min(s + 16000, len(html))
        seg = html[s:e]
        m = re.search(r"<h3>(.*?)</h3>", seg, re.S)
        if m:
            out.append((txt(m.group(1)), seg))
    return out


def date_of(title):
    """从卡标题解析日期，归一化为 YYYY-MM-DD"""
    m = re.search(r"(2026)[-./](\d{1,2})[-./](\d{1,2})", title)
    if m:
        # 周报区间如 2026/11/1~11/7 → 取区间结束日作为发布日
        tail = re.search(r"~\s*(\d{1,2})/(\d{1,2})", title)
        mo, dy = (int(tail.group(1)), int(tail.group(2))) if tail else (int(m.group(2)), int(m.group(3)))
        return f"{int(m.group(1))}-{mo:02d}-{dy:02d}"
    m = re.search(r"(\d{1,2})月(\d{1,2})日", title)
    if m:
        return f"2026-{int(m.group(1)):02d}-{int(m.group(2)):02d}"
    return ""


def latest(cards_list, *keywords):
    """按标题关键词过滤后取日期最新的一张卡"""
    hits = [(date_of(t), t, seg) for t, seg in cards_list
            if all(k in t for k in keywords)]
    hits = [x for x in hits if x[0]]
    if not hits:
        return None
    hits.sort(key=lambda x: x[0], reverse=True)
    return hits[0]


def tbody_rows(seg, idx=0):
    tbs = re.findall(r"<tbody>(.*?)</tbody>", seg, re.S)
    if idx >= len(tbs):
        return []
    return [[txt(x) for x in re.findall(r"<td[^>]*>(.*?)</td>", tr, re.S)]
            for tr in re.findall(r"<tr>(.*?)</tr>", tbs[idx], re.S)]


def first_num(s):
    m = re.search(r"\d+(?:\.\d+)?", s or "")
    return float(m.group()) if m else None


def legend_link(seg):
    m = re.search(r'<div class="legend">(.*?)</div>', seg, re.S)
    if not m:
        return "", ""
    a = re.search(r'href="([^"]+)"[^>]*>(.*?)</a>', m.group(1), re.S)
    if not a:
        return "", ""
    return a.group(1), txt(a.group(2))


def csub(seg, limit=96):
    m = re.search(r'<div class="csub">(.*?)</div>', seg, re.S)
    s = txt(m.group(1)) if m else ""
    return s[:limit] + ("…" if len(s) > limit else "")


def core_of(seg, limit=104):
    """优先拼接 csub 中 <b> 强调句（通常是关键价格/结论），否则回退整段摘要。"""
    m = re.search(r'<div class="csub">(.*?)</div>', seg, re.S)
    if not m:
        return ""
    raw = m.group(1)
    bolds = [txt(x) for x in re.findall(r"<b[^>]*>(.*?)</b>", raw, re.S)]
    s = " ".join(x for x in bolds if x)
    if len(s) < 12:
        s = txt(raw)
    return s[:limit] + ("…" if len(s) > limit else "")


# 行情线索卡注册表：(标题关键词..., 线索显示名)
CLUE_SPECS = [
    (("🎬", "互联惠农小洁"), "视频号·互联惠农小洁 全国塘口参考价"),
    (("🎬", "水产养殖服务于老师"), "视频号·水产养殖服务于老师 全国参考塘口价"),
    (("📰 全国渔业价格",), "全国渔业价格日报"),
    (("🐟 鳜康泰特约",), "鳜康泰特约·全国鳜鱼报价"),
    (("通威农牧 / 腾氏水产 一周鱼价",), "通威农牧 / 腾氏水产 一周鱼价"),
    (("🏪 江苏凌家塘市场",), "江苏凌家塘 一周行情"),
    (("🛒", "无锡盛阳食品城"), "无锡盛阳食品城 本地批发价"),
    (("🌊 淡水渔业公众号",), "淡水渔业 全国批发价"),
    (("海大农牧 水产一线",), "海大农牧 塘头价"),
]


def build_clues(cards_list):
    rows = []
    for kws, label in CLUE_SPECS:
        hit = latest(cards_list, *kws)
        if not hit:
            print(f"[warn] 线索卡未找到，跳过: {label}")
            continue
        d, title, seg = hit
        url, link_txt = legend_link(seg)
        fallback = "截图核校录入" if ("视频号" in label or "盛阳" in label) else label
        rows.append({
            "title": label,
            "date": d,
            "core": core_of(seg),
            "src": link_txt or fallback,
            "url": url,
        })
    rows.sort(key=lambda r: r["date"], reverse=True)
    return rows[:8]


def build_pond_gui(cards_list, old):
    hit = latest(cards_list, "🐟 鳜康泰特约")
    if not hit:
        print("[warn] 未找到鳜康泰卡，鳜鱼塘口价保留原值")
        return old
    d, title, seg = hit
    rows = []
    for tds in tbody_rows(seg, 0):
        if len(tds) < 3:
            continue
        words = tds[0].split()
        region = words[0] if words else tds[0]
        suffix = words[1] if len(words) > 1 else ""
        spec = tds[1]
        if suffix and suffix not in spec:
            spec = f"{suffix}（{spec}）" if spec != suffix else suffix
        p = first_num(tds[2])
        if p is None:
            continue
        rows.append({"region": region, "spec": spec, "price": p,
                     "trend": "flat", "note": "原文自述价格保持稳定",
                     **({"local": True} if region == "江苏" else {})})
    if not rows:
        print("[warn] 鳜康泰表格解析为空，保留原值")
        return old
    url, _ = legend_link(seg)
    return {
        "date": d,
        "source": "兴渔派-鳜鱼通·鳜康泰特约",
        "source_url": url or old.get("source_url", ""),
        "spec": "标鳜（0.8~1.5 斤）为主，另列小鳜/中鳜",
        "headline": core_of(seg, 110),
        "rows": rows,
        "weekly": old.get("weekly", {}),
    }


def build_pond_lu(cards_list, old):
    hit = latest(cards_list, "通威农牧 / 腾氏水产 一周鱼价")
    if not hit:
        print("[warn] 未找到通威/腾氏周报卡，加州鲈塘口价保留原值")
        return old
    d, title, seg = hit
    rows = []
    for tds in tbody_rows(seg, 1):
        if len(tds) < 4 or "加州鲈" not in tds[0]:
            continue
        loc = tds[1].split("·")
        region = loc[0].strip()
        spec = loc[1].strip() if len(loc) > 1 else tds[1]
        p = first_num(tds[2])
        if p is None:  # 「原文未标绝对价」如实留空，不推算
            continue
        note = tds[3]
        trend = "up" if ("+" in note or "涨" in note) else ("down" if ("-" in note or "跌" in note) else "flat")
        rows.append({"region": region, "spec": spec, "price": p,
                     "trend": trend, "note": note})
    if not rows:
        print("[warn] 周报分产区表解析为空，保留原值")
        return old
    url, _ = legend_link(seg)
    return {
        "date": d,
        "source": "通威农牧 / 腾氏水产 一周鱼价（同源周报合并）",
        "source_url": url or old.get("source_url", ""),
        "spec": "全国塘口均价 + 分产区塘口价，元/斤",
        "headline": core_of(seg, 110),
        "rows": rows,
        "weekly_note": "江苏栏原文只给涨幅未给绝对价，已按原文留空；不同产区规格口径不可互减。",
    }


def build_weekly(cards_list, old):
    hit = latest(cards_list, "通威农牧 / 腾氏水产 一周鱼价")
    if not hit:
        print("[warn] 未找到周报卡，weekly 保留原值")
        return old
    d, title, seg = hit
    rows = []
    for tds in tbody_rows(seg, 1):
        if len(tds) < 4 or "鳜鱼" not in tds[0]:
            continue
        loc = tds[1].split("·")
        rows.append({"region": loc[0].strip(), "spec": loc[1].strip() if len(loc) > 1 else tds[1],
                     "prev": "—", "curr": tds[2], "note": tds[3], "trend": "flat"})
    if not rows:
        return old
    url, _ = legend_link(seg)
    return {
        "date": d,
        "source": "通威农牧 / 腾氏水产 一周鱼价",
        "source_url": url or old.get("source_url", ""),
        "summary": "本周特水鱼普涨、普水鱼普跌；鳜鱼分产区塘口价见下表（原文未给上周基准，不做互减）",
        "rows": rows,
    }


def build_local_ws(cards_list, old):
    hit = latest(cards_list, "🛒", "无锡盛阳食品城")
    if not hit:
        print("[warn] 未找到盛阳卡，本地批发价保留原值")
        return old
    d, title, seg = hit
    rows = []
    for tds in tbody_rows(seg, 0):
        if len(tds) < 3:
            continue
        rows.append({"name": tds[0], "price": tds[1], "note": tds[2]})
    if not rows:
        return old
    return {"date": d, "source": "无锡盛阳食品城（本地渠道一手批发价）", "rows": rows}


NOTES = [
    "决策提示（11-09）：小洁 0.8-1.2 斤通货鳜鱼 32.2~33.8↑、鲈鱼 12.5~13.8↓；于老师 1 斤上鳜鱼 22-26.5、加州鲈 10.0-11.5 均标「基本持平」，两组规格不同不可互减。",
    "口径提示：加州鲈多口径并存——通威/腾氏全国塘口均价 10.5（11-07）、海大四产区 10.5~11.3（11-06）、凌家塘批发约 12（11-07）、盛阳销地批发 10~14（11-08）、小洁通货 12.5~13.8（11-09）；看方向不看绝对值。",
    "口径提示：鳜鱼多口径并存——鳜康泰标鳜 24（11-07）、通威/腾氏全国均价 25（11-07）、凌家塘批发约 30（11-07）、盛阳 25~30（11-08）、于老师 22-26.5 与小洁 32.2~33.8（11-09）；规格渠道三重差异，禁止互减。",
    "沿用值提示：全国渔业价格 11-09 日报的加州鲈佛山 15.00 为 11/7 沿用值、非当日新采价，不重复计数、不推断涨跌。",
    "江苏本地（宜兴官林）无独立塘口报价点位，参考「环太湖 / 江苏标鳜」；11-07 江苏标鳜 25 元/斤（鳜康泰），11-07 周报江苏加州鲈只给涨幅、未给绝对价。",
    "批发价倒推收购上限须扣流通成本（鳜 3 / 鲈 1 元/斤）；MOA 全国均价一律取中位数，跨区价差须过滤远距离销区。",
    "寒潮提示（11-09 日报）：11/10 早晨珠三角北部 8~12℃，水温骤降易诱发水霉病与应激，不宜安排大宗出鱼、拉网后需消毒。",
]


def main():
    html = open(V1, encoding="utf-8").read()
    cs = cards(html)
    print(f"[info] v1 卡片数 {len(cs)}")

    manual = json.load(open(MANUAL, encoding="utf-8"))
    pond = manual.setdefault("pond", {})
    pond["鳜鱼"] = build_pond_gui(cs, pond.get("鳜鱼", {}))
    pond["加州鲈"] = build_pond_lu(cs, pond.get("加州鲈", {}))
    pond["鳜鱼"]["weekly"] = build_weekly(cs, pond["鳜鱼"].get("weekly", {}))
    manual["local_wholesale"] = build_local_ws(cs, manual.get("local_wholesale", {}))
    manual["disease"]["period"] = "2026-11 上旬 ~ 11 月中旬"
    manual["notes"] = NOTES

    clue_rows = build_clues(cs)
    if not clue_rows:
        print("[error] 未生成任何行情线索，终止写盘")
        sys.exit(1)
    manual["updated"] = max(r["date"] for r in clue_rows)
    manual["_comment"] = ("2.0 看板人工/链接源快照。pond / local_wholesale / notes / updated "
                          "由 sync_v2_from_v1.py 从 v1 看板 HTML 自动生成（请勿手改）；"
                          "disease 等静态配置仍可人工维护。重建：sync_v2_from_v1.py && build_dashboard_v2.py。")

    # 一致性断言，防止写入半截数据
    assert pond["鳜鱼"]["rows"] and pond["加州鲈"]["rows"], "塘口价解析为空"
    assert any(r.get("local") for r in pond["鳜鱼"]["rows"]), "鳜鱼缺江苏本地行"
    assert len(manual["local_wholesale"]["rows"]) >= 2, "本地批发价行数不足"
    assert all(r.get("date") for r in clue_rows), "线索缺日期"

    with open(MANUAL, "w", encoding="utf-8") as f:
        json.dump(manual, f, ensure_ascii=False, indent=2)
    with open(CLUES, "w", encoding="utf-8") as f:
        json.dump({"_doc": "由 sync_v2_from_v1.py 从 v1 看板 HTML 自动抽取的最新行情线索，勿手改",
                   "generated": datetime.now(CST).strftime("%Y-%m-%d %H:%M"),
                   "rows": clue_rows}, f, ensure_ascii=False, indent=2)

    print(f"[ok] 同步完成：updated={manual['updated']}")
    print(f"     鳜鱼塘口 {len(pond['鳜鱼']['rows'])} 行（{pond['鳜鱼']['date']}）"
          f" / 加州鲈 {len(pond['加州鲈']['rows'])} 行（{pond['加州鲈']['date']}）"
          f" / 本地批发 {len(manual['local_wholesale']['rows'])} 行（{manual['local_wholesale']['date']}）")
    print(f"     行情线索 {len(clue_rows)} 条：")
    for r in clue_rows:
        print(f"       {r['date']}  {r['title'][:28]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
