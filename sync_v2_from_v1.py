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


def num_range(s):
    """解析价格文本 → (lo, hi, 原文显示串)；支持 10.5~11 / 10-11 / 9 左右 / 11.0。

    区间同时保留上下限与中值，供 v2 KPI 显示「10.5~11」并按中值做盈亏测算，
    避免只取首个数字把区间压成单点、或把「原文未标绝对价」误当成价格。
    """
    t = txt(s).replace("元/斤", "").strip()
    m = re.search(r"(\d+(?:\.\d+)?)\s*[~～\-—–]\s*(\d+(?:\.\d+)?)", t)
    if m:
        lo, hi = float(m.group(1)), float(m.group(2))
        if lo <= hi:
            return lo, hi, t
    m = re.search(r"\d+(?:\.\d+)?", t)
    if m:
        v = float(m.group())
        return v, v, t
    return None


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
    # 11-10 期淡水渔业与科学养鱼合并为一卡，标题不含「淡水渔业公众号」前缀，
    # 改用「🌊 + 淡水渔业」双关键词，兼容新旧两种命名并按日期取最新。
    (("🌊", "淡水渔业"), "淡水渔业 / 科学养鱼 同源批发价"),
    (("🐟 通威农牧 · 特水鱼类批发均价",), "通威农牧 分市场批发均价（截图核校）"),
    # 11-14 批次：科学养鱼 11-13 单独成卡（无淡水渔业同日发布），标题不含「淡水渔业」
    (("🌊", "科学养鱼"), "科学养鱼 分市场批发价（正文表格）"),
    (("🐟 通威农牧 · 一周鱼价行情",), "通威农牧 一周鱼价行情（全国塘口均价）"),
    (("渔飞鱼·董小月",), "渔知识指导·渔飞鱼日报"),
    (("海大农牧 水产一线",), "海大农牧 塘头价"),
    (("水产养殖网", "强渔"), "水产养殖网（强渔）特水鱼周报"),
    (("渔飞鱼", "明日水产行情预报"), "渔飞鱼 明日水产行情预报（次日预测）"),
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
    # 涨跌标注随当期卡片变化，不能写死（11-07 期自述稳定，11-09 期为下跌）
    cm = re.search(r'<div class="csub">(.*?)</div>', seg, re.S)
    ctxt = txt(cm.group(1)) if cm else ""
    if "下跌" in ctxt:
        trend, note = "down", "原文标注下跌，按原文照录"
    elif "上涨" in ctxt:
        trend, note = "up", "原文标注上涨，按原文照录"
    else:
        trend, note = "flat", "原文自述价格保持稳定"
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
                     "trend": trend, "note": note,
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


# 加州鲈分产区塘口价候选卡：(标题关键词..., tbody 索引, 解析模式, 来源显示名)
# 按卡片日期自动选最新的一期；某源停更时不会把整张表锁死在旧日期。
# region_first = 第 1 列产区 / 第 2 列规格 / 第 3 列价格（强渔特水鱼周报）
# species_first = 第 1 列品种 / 第 2 列「产区 · 规格」/ 第 3 列价格（通威/腾氏周报）
LU_POND_SPECS = [
    (("水产养殖网", "强渔", "特水鱼周报"), 1, "region_first", "水产养殖网（强渔）特水鱼周报"),
    (("通威农牧 / 腾氏水产 一周鱼价",), 1, "species_first", "通威农牧 / 腾氏水产 一周鱼价（同源周报合并）"),
    # 11-14 批次：通威 11-13 周报单表（species_first，tds[0] 含「加州鲈」、tds[1] 为「地区 · 规格」），
    # 江苏 1 斤 10 元/斤 为环太湖本地锚点；按日期取最新，会自动覆盖 11-09 强渔周报。
    (("🐟 通威农牧 · 一周鱼价行情",), 0, "species_first", "通威农牧 一周鱼价行情 11-13"),
]
LOCAL_KW = ("江苏", "吴江", "苏州", "环太湖", "江浙")


def _lu_rows(seg, tidx, mode):
    """把一张产区周报卡解析成行；跳过无绝对价 / 非元每斤口径的行，不推算。"""
    rows = []
    for tds in tbody_rows(seg, tidx):
        if len(tds) < 3:
            continue
        if mode == "species_first":
            if "加州鲈" not in tds[0]:
                continue
            loc = tds[1].split("·")
            region = loc[0].strip()
            spec = loc[1].strip() if len(loc) > 1 else tds[1]
        else:
            region, spec = tds[0].strip(), tds[1].strip()
        price_s, note = tds[2], (tds[3] if len(tds) > 3 else "")
        if "元/两" in price_s:  # 元/两是另一口径，禁止当元/斤录入
            continue
        rng = num_range(price_s)
        if not rng:  # 「原文未标绝对价」如实留空
            continue
        lo, hi, ptxt = rng
        trend = "up" if ("涨" in note or "+" in note) else ("down" if ("跌" in note or "-" in note) else "flat")
        rows.append({"region": region, "spec": spec, "price": lo,
                     "price_lo": lo, "price_hi": hi, "price_mid": (lo + hi) / 2,
                     "price_txt": ptxt, "trend": trend, "note": note,
                     **({"local": True} if any(k in region for k in LOCAL_KW) else {})})
    return rows


def build_pond_lu(cards_list, old):
    """加州鲈塘口价：选「日期最新且含江苏/环太湖绝对价」的产区周报。

    v2 的「加州鲈 · 出塘价」KPI 只认 rows 里带 local:true 的行；早期此函数
    只抽通威/腾氏周报，而该期江苏行「原文未标绝对价」被跳过，导致 KPI 长期
    渲染为「—」（2026-11-10 用户指出）。现改为多源候选 + 强制本地行断言。
    """
    hits = []
    for kws, tidx, mode, src in LU_POND_SPECS:
        hit = latest(cards_list, *kws)
        if not hit:
            continue
        d, _title, seg = hit
        rows = _lu_rows(seg, tidx, mode)
        if rows:
            hits.append((d, src, seg, rows))
    if not hits:
        print("[warn] 未找到任何加州鲈产区周报卡，塘口价保留原值")
        return old
    hits.sort(key=lambda x: x[0], reverse=True)
    usable = [x for x in hits if any(r.get("local") for r in x[3])]
    if not usable:
        print("[error] 所有候选周报都无江苏/环太湖绝对价行，保留原值（v2 KPI 会显示 —，需人工补源）")
        return old
    d, src, seg, rows = usable[0]
    url, _ = legend_link(seg)
    lrow = next(r for r in rows if r.get("local"))
    return {
        "date": d,
        "source": src,
        "source_url": url or old.get("source_url", ""),
        "spec": "分产区塘口价（元/斤）· 多口径并存，禁止互减",
        "headline": core_of(seg, 110),
        "rows": rows,
        # 本地锚点单独留痕：KPI 的日期/来源跟随这一行，不跟随整张表的周报期
        "local_date": d,
        "local_source": src,
        "local_region": lrow["region"],
        "local_spec": lrow["spec"],
        "local_note": lrow["note"],
        "weekly_note": "不同产区规格口径不可互减；原文只给涨幅未给绝对价的行如实留空。",
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


def build_notes(cs):
    """决策提示语按 v1 最新卡片动态生成，避免日期/数值写死后长期陈旧。"""
    rows = []
    specs = [
        (("🎬", "互联惠农小洁"), "决策提示·小洁 全国塘口参考价"),
        (("🎬", "水产养殖服务于老师"), "决策提示·于老师 全国参考塘口价"),
        (("🐟 鳜康泰特约",), "塘口基准·鳜康泰标鳜报价"),
        (("🛒", "无锡盛阳食品城"), "本地批发·盛阳食品城"),
        (("水产养殖网", "强渔"), "产区周报·水产养殖网（强渔）"),
    ]
    for kws, label in specs:
        hit = latest(cs, *kws)
        if not hit:
            continue
        d, _t, seg = hit
        rows.append(f"{label}（{d}）：{core_of(seg, 100)}")
    rows += [
        "口径提示：塘口价 / 批发价 / 供货报价 / 次日预测价 / 视频号全国参考区间为不同规格与渠道口径，多口径并存、禁止互减，只看方向不看绝对值。",
        "沿用值提示：标注「沿用」「11/7 沿用」的价格不是当日新采价，不重复计数、不推断涨跌；同一份报价被多个公众号转载时合并一卡、双出处留痕。",
        "批发价倒推收购上限须扣流通成本（鳜 3 / 鲈 1 元/斤）；MOA 全国均价一律取中位数，跨区价差须过滤远距离销区。",
        "江苏本地（宜兴官林）无独立塘口报价点位，参考「环太湖 / 江苏标鳜」；跨期核校仅限同市场同规格。",
    ]
    return rows[:9]


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
    manual["notes"] = build_notes(cs)

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
    # 关键防复发：没有本地行 → v2 的「加州鲈 · 出塘价」KPI 会渲染成「—」
    assert any(r.get("local") for r in pond["加州鲈"]["rows"]), "加州鲈缺江苏/环太湖本地行"
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
