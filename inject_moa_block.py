#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
把农业农村部（MOA）当日批发价快照注入 v1 看板（幂等）
=====================================================
背景
----
v1 的「MOA 批发价」区块（KPI 卡 + 明细表 + 数据说明）历史上是**纯手工维护**，
爬虫只更新 fish_prices*.json/csv/js，不回写 HTML。结果反复出现
「数据文件已到 10-27、卡片还写 10-18」的脱钩，以及口径漂移
（曾用算术平均，被乌鲁木齐 145 元/kg 单侧拉高到 43 元/斤）。

本脚本负责把该区块的**机器可算部分**全部从数据文件重新推导并幂等替换，
手工叙述（历史对比、销地新闻）留在锚点之外不受影响。

注入的 4 个锚点
---------------
  <!-- MOA_KPI_LU_START --> … <!-- MOA_KPI_LU_END -->      鲈鱼·批发价 KPI 卡的 sub/val/trend
  <!-- MOA_GUI_FRAG_START --> … <!-- MOA_GUI_FRAG_END -->  鳜鱼·批发价 KPI 趋势行内的 MOA 片段
  <!-- MOA_ROWS_START --> … <!-- MOA_ROWS_END -->          MOA 明细表 tbody 行
  <!-- MOA_CALLOUT_START --> … <!-- MOA_CALLOUT_END -->    数据说明 callout 的自动统计段

口径（2026-10-28 固化，与 v2 决策版一致）
----------------------------------------
1. 全国中枢一律取**中位数**——算术平均会被远距离销区（乌鲁木齐/甘肃/宁夏/拉萨…）
   单侧拉高约 50%，仅在说明里作为「反面参照」列出并标注弃用；
2. 远距离销区报价只作销地参考，**不构成跨区调运套利空间**（运费+损耗吞掉账面价差）；
3. 批发价**不可直接当收购上限**，须倒扣流通成本（鳜鱼 3 元/斤、鲈鱼 1 元/斤）。

用法
----
  python inject_moa_block.py            # 注入并写回 HTML
  python inject_moa_block.py --check    # 只体检不写回（CI 断言用）
  python inject_moa_block.py --dry-run  # 打印将生成的内容，不落盘
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import re
import statistics as st
import sys

WS = os.path.dirname(os.path.abspath(__file__))
HTML = os.path.join(WS, "鳜鱼鲈鱼价格看板.html")
SNAP = os.path.join(WS, "fish_prices.json")
HIST = os.path.join(WS, "fish_prices_history.csv")

VARIETY_GUI = "活鳜鱼"
VARIETY_LU = "淡水鲈鱼"

# 远距离销区：报价不代表产区行情，不进中枢、不做套利推荐
FAR_KW = ["乌鲁木齐", "北园春", "甘肃", "兰州", "酒泉", "宁夏", "西宁", "青海",
          "拉萨", "西藏", "内蒙古", "呼和浩特", "新疆"]

# 市场简称（缺失时走自动简化）
MARKET_SHORT = {
    "乌鲁木齐北园春果业经营管理有限责任公司": "乌鲁木齐 北园春",
    "江西九江琵琶湖农产品物流有限公司": "江西 九江琵琶湖",
    "江苏凌家塘市场发展有限公司": "江苏 凌家塘",
    "马鞍山市安民农副产品贸易有限公司": "安徽 马鞍山",
    "长治市紫坊农产品综合交易市场有限公司": "山西 长治紫坊",
    "云南华潮实业有限公司": "云南 华潮",
    "北京朝阳区大洋路综合市场": "北京 大洋路",
    "青岛市城阳蔬菜水产品批发市场有限公司": "山东 青岛城阳",
    "山东威海水产品批发市场": "山东 威海",
    "山东滨州(六街）鲁北蔬菜批发市场": "山东 滨州六街",
    "甘肃酒泉春光农产品市场有限责任公司": "甘肃 酒泉春光",
    "宁夏四季鲜农产品综合批发市场": "宁夏 四季鲜",
    "河南万邦国际农产品物流股份有限公司": "河南 万邦",
    "安徽合肥周谷堆农产品批发市场": "安徽 周谷堆",
    "江苏苏州南环桥农副产品批发市场": "江苏 南环桥",
    "龙门实业（集团）有限公司西三街农副水产品市场": "重庆 龙门西三街",
}

ANCHORS = ["MOA_KPI_LU", "MOA_GUI_FRAG", "MOA_ROWS", "MOA_CALLOUT"]

BADGE_NEW = '<span class="badge b-new" style="font-size:11px">本次</span>'
BADGE_FAR = '<span class="badge" style="font-size:11px">远距离销区</span>'
C_UP, C_DOWN, C_FLAT = "#dc2626", "#12a150", "#6b7280"


# ---------------------------------------------------------------- 数据读取
def load_snapshot() -> list[dict]:
    if not os.path.exists(SNAP):
        sys.exit(f"[ERR] 找不到 {SNAP}，先跑 moa_fish_crawler.py")
    with open(SNAP, encoding="utf-8") as f:
        rows = json.load(f)
    for r in rows:
        r["批发价_元公斤"] = float(r["批发价_元公斤"])
    return rows


def load_history() -> list[dict]:
    if not os.path.exists(HIST):
        return []
    with open(HIST, encoding="utf-8-sig") as f:
        return [
            {**r, "批发价_元公斤": float(r["批发价_元公斤"])}
            for r in csv.DictReader(f)
            if r.get("批发价_元公斤")
        ]


def prev_price(hist: list[dict], variety: str, market: str, latest: str) -> float | None:
    """同品种同市场、日期早于 latest 的最近一条报价"""
    cand = [r for r in hist
            if r["品种"] == variety and r["市场"] == market and r["日期"] < latest]
    if not cand:
        return None
    return max(cand, key=lambda r: r["日期"])["批发价_元公斤"]


# ---------------------------------------------------------------- 工具
def short_market(name: str) -> str:
    if name in MARKET_SHORT:
        return MARKET_SHORT[name]
    s = re.sub(r"（集团）|有限责任公司|股份有限公司|有限公司|集团|实业|发展", "", name)
    return s.strip() or name


def is_far(name: str) -> bool:
    return any(k in name for k in FAR_KW)


def city(name: str) -> str:
    """KPI 里的短名：优先取简称末段；末段过短（如「华潮」）则回退完整简称"""
    s = short_market(name)
    last = s.split()[-1]
    return last if len(last) >= 3 else s.replace(" ", "")


def delta_html(cur: float, prev: float | None) -> str:
    """涨跌标记：涨=红 ▲、跌=绿 ▼、持平=灰 ■（国内习惯）"""
    if prev is None:
        return '<small style="color:%s">首报</small>' % C_FLAT
    d = cur - prev
    if abs(d) < 0.05:
        return '<small style="color:%s">■ 持平</small>' % C_FLAT
    color, arrow = (C_UP, "▲") if d > 0 else (C_DOWN, "▼")
    return '<small style="color:%s">%s%g</small>' % (color, arrow, abs(d))


def fmt(v: float) -> str:
    """价格显示：整数不带小数，否则保留 1 位"""
    return str(int(v)) if abs(v - round(v)) < 1e-9 else f"{v:.1f}"


def median_of(rows: list[dict]) -> float:
    return st.median([r["批发价_元公斤"] for r in rows])


def trend_class(cur: float, prev: float | None) -> str:
    if prev is None or abs(cur - prev) < 0.05:
        return "t-flat"
    return "t-up" if cur > prev else "t-down"


# ---------------------------------------------------------------- 段落生成
def build_gui_rows(rows: list[dict], hist: list[dict], latest: str) -> str:
    """MOA 明细表的活鳜鱼行：按价格降序，含涨跌与远距离标记"""
    gui = sorted([r for r in rows if r["品种"] == VARIETY_GUI],
                 key=lambda r: -r["批发价_元公斤"])
    if not gui:
        return '<tr><td colspan="5">当日活鳜鱼无报价（接口 data=null）</td></tr>'
    med = median_of(gui)
    out = []
    for r in gui:
        p = r["批发价_元公斤"]
        prev = prev_price(hist, r["品种"], r["市场"], latest)
        far = is_far(r["市场"])
        name = short_market(r["市场"])
        left = f"<b>{name}</b> {BADGE_FAR if far else BADGE_NEW}"
        val = f"<b>{fmt(p)}</b>" if abs(p - med) < 1e-9 else fmt(p)
        out.append(
            "<tr>"
            f'<td>{left}</td>'
            '<td><span class="spec spec-l">活鳜鱼 统货</span></td>'
            f'<td class="price">{val} <small>元/公斤</small></td>'
            f"<td>≈ {fmt(p / 2)} {delta_html(p, prev)}</td>"
            f"<td>{latest}</td>"
            "</tr>"
        )
    return "\n            ".join(out)


def build_lu_kpi(rows: list[dict], hist: list[dict], latest: str) -> str:
    """鲈鱼·批发价 KPI 卡（sub / val / trend 三行）"""
    lu = sorted([r for r in rows if r["品种"] == VARIETY_LU],
                key=lambda r: r["批发价_元公斤"])
    if not lu:
        return ('<div class="sub">全国中位数口径 · MOA</div>\n'
                '      <div class="val">— <small>元/斤</small></div>\n'
                '      <div class="trend t-flat">■ 当日淡水鲈鱼无报价</div>')
    med, avg = median_of(lu), st.mean([r["批发价_元公斤"] for r in lu])
    market_txt = " / ".join(f"{city(r['市场'])} {fmt(r['批发价_元公斤'])}" for r in lu)
    # 环比：与上一期同品种中位数比
    hist_dates = sorted({r["日期"] for r in hist if r["品种"] == VARIETY_LU and r["日期"] < latest})
    prev_med = None
    if hist_dates:
        prev_rows = [r for r in hist if r["品种"] == VARIETY_LU and r["日期"] == hist_dates[-1]]
        if prev_rows:
            prev_med = st.median([r["批发价_元公斤"] for r in prev_rows])
    cls = trend_class(med, prev_med)
    delta = "" if prev_med is None else f"，上期 {fmt(prev_med / 2)} 元/斤"
    avg_note = (f"算术平均 {fmt(avg)} 元/kg 会受极值单侧拉动，已弃用"
                if abs(avg - med) > 0.05 else "算术平均与中位数一致")
    return (
        f'<div class="sub" data-page-node-id="nDNr137Xf8pedK9ngpdbQ5s">全国中位数口径 · MOA {latest[5:]}</div>\n'
        f'      <div class="val" data-page-node-id="RGZDW7VFkOEyqZeAgc8D4v">{fmt(med / 2)} '
        f'<small data-page-node-id="GdYlHOdYclIQacjQovMojr">元/斤</small> '
        f'<span style="font-size:11px;opacity:.7">批发·{fmt(med)}元/kg</span></div>\n'
        f'      <div class="trend {cls}" data-page-node-id="pkLCLgV0f8DJMSfpvKPMpU">■ {len(lu)} 市场取中位数：'
        f'{market_txt}（元/kg）→ <b>中位 {fmt(med)} = {fmt(med / 2)} 元/斤</b>'
        f'（{avg_note}）{delta} · 对比塘口 10.5 元/斤含流通加价</div>'
    )


def build_gui_frag(rows: list[dict], latest: str) -> str:
    """鳜鱼·批发价 KPI 趋势行内的 MOA 片段（行内，不含外层 div）"""
    gui = sorted([r for r in rows if r["品种"] == VARIETY_GUI],
                 key=lambda r: -r["批发价_元公斤"])
    if not gui:
        return "MOA 当日活鳜无报价"
    med = median_of(gui)
    core = [r for r in gui if not is_far(r["市场"])]
    far = [r for r in gui if is_far(r["市场"])]
    core_txt = " / ".join(f"{short_market(r['市场']).split()[-1]} {fmt(r['批发价_元公斤'])}"
                          for r in core[:4]) or "—"
    frag = (f"<b>MOA {latest[5:]} 活鳜：{core_txt} 元/kg，中位数 {fmt(med)} ≈ {fmt(med / 2)} 元/斤</b>")
    if far:
        far_txt = "、".join(f"{short_market(r['市场'])} {fmt(r['批发价_元公斤'])}" for r in far)
        frag += f"（{far_txt} 系远距离销区，不纳入全国中枢口径）"
    return frag


def build_callout(rows: list[dict], latest: str) -> str:
    """数据说明 callout 的自动统计段"""
    gui = [r for r in rows if r["品种"] == VARIETY_GUI]
    if not gui:
        return "<b>数据说明：</b>当日活鳜鱼无报价（接口 data=null），待下一交易日重取。"
    med = median_of(gui)
    avg = st.mean([r["批发价_元公斤"] for r in gui])
    dev = (avg / med - 1) * 100 if med else 0
    names = "、".join(
        f"{short_market(r['市场'])} {fmt(r['批发价_元公斤'])}"
        + ("（远距离销区）" if is_far(r["市场"]) else "")
        for r in sorted(gui, key=lambda r: -r["批发价_元公斤"])
    )
    parts = [
        "<b>数据说明：</b>本表由爬虫直连农业农村部官方批发价接口"
        '（品种码 <b data-page-node-id="s1Q00TF0POF5yVqQud9t36">AM01013003</b>）解密所得，'
        f'<b data-page-node-id="CcdYkUaKKXB89kQcLbapv8">最新抓取日期 {latest}</b>，'
        f'当日活鳜鱼共 <b data-page-node-id="rFqB7rlTfkAp0KvBLbSpHG">{len(gui)} 条</b>报价：{names}（元/公斤）。',
        '<b style="color:#dc2626">⚠️ 口径（2026-10-28 固化，本段由 inject_moa_block.py 自动生成）：</b>'
        f"① 全国中枢一律取<b>中位数</b>——本次中位数 <b>{fmt(med)} 元/公斤 ≈ {fmt(med / 2)} 元/斤</b>；"
        + (f"若用算术平均则为 {fmt(avg)} 元/公斤（≈{fmt(avg / 2)} 元/斤），"
           f"被远距离销区单侧拉高 {dev:.0f}%，<b>不予采用</b>；" if abs(dev) >= 3 else "算术平均与中位数一致；")
        + "② 乌鲁木齐、甘肃、宁夏、青海、拉萨等<b>远距离销区报价仅作销地参考，不代表产区行情，"
          "也不构成跨区调运的套利空间</b>（运距长，运费与损耗吞掉账面价差）；"
          "③ 批发价<b>不可直接当作收购上限</b>——须先倒扣流通成本"
          "（鳜鱼约 3 元/斤、鲈鱼约 1 元/斤），再按规格与成活率折算。",
    ]
    return "\n".join(parts)


# ---------------------------------------------------------------- 注入
def replace_block(html: str, key: str, body: str) -> tuple[str, bool]:
    start, end = f"<!-- {key}_START -->", f"<!-- {key}_END -->"
    if start not in html or end not in html:
        return html, False
    pattern = re.compile(re.escape(start) + r".*?" + re.escape(end), re.S)
    new = f"{start}\n{body}\n{end}"
    return pattern.sub(lambda _: new, html, count=1), True


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true", help="只体检不写回")
    ap.add_argument("--dry-run", action="store_true", help="打印生成内容，不落盘")
    args = ap.parse_args()

    rows = load_snapshot()
    hist = load_history()
    latest = max(r["日期"] for r in rows)

    # [guard] 某品种当日无报价（接口 data=null）时**跳过该品种的替换**，保留看板原值。
    # 否则会把 KPI 写成「—」、表格清空——重演 refresh_freshness 空值擦除事故。
    has_gui = any(r["品种"] == VARIETY_GUI for r in rows)
    has_lu = any(r["品种"] == VARIETY_LU for r in rows)
    blocks: dict[str, str] = {}
    if has_gui:
        blocks["MOA_GUI_FRAG"] = build_gui_frag(rows, latest)
        blocks["MOA_ROWS"] = build_gui_rows(rows, hist, latest)
        blocks["MOA_CALLOUT"] = build_callout(rows, latest)
    else:
        print(f"[WARN] {VARIETY_GUI} 当日无报价，保留看板原值，跳过 3 个区块", file=sys.stderr)
    if has_lu:
        blocks["MOA_KPI_LU"] = build_lu_kpi(rows, hist, latest)
    else:
        print(f"[WARN] {VARIETY_LU} 当日无报价，保留看板原值，跳过 KPI", file=sys.stderr)
    if not blocks:
        print("[ERR] 两个品种均无报价，不做任何改动", file=sys.stderr)
        return 1

    with open(HTML, encoding="utf-8") as f:
        html = f.read()

    missing = [k for k in ANCHORS
               if f"<!-- {k}_START -->" not in html or f"<!-- {k}_END -->" not in html]
    if missing:
        print(f"[ERR] 缺少锚点：{', '.join(missing)}（应成对出现在 v1 HTML 内）", file=sys.stderr)
        return 2

    new_html = html
    for key, body in blocks.items():
        new_html, ok = replace_block(new_html, key, body)
        if not ok:
            print(f"[ERR] {key} 替换失败", file=sys.stderr)
            return 2

    changed = new_html != html
    gui_rows = [r for r in rows if r["品种"] == VARIETY_GUI]
    med_gui = median_of(gui_rows) if gui_rows else None
    med_txt = (f"活鳜中位数 {fmt(med_gui)} 元/kg ≈ {fmt(med_gui / 2)} 元/斤"
               if med_gui is not None else "当日活鳜无报价，保留原值")

    if args.dry_run:
        for k, v in blocks.items():
            print(f"\n===== {k} =====\n{v}")
        return 0

    if args.check:
        print(f"[check] 数据日 {latest} · {med_txt} · HTML {'需更新' if changed else '已最新'}")
        return 0

    if changed:
        with open(HTML, "w", encoding="utf-8") as f:
            f.write(new_html)
        print(f"[OK] 已注入 MOA 区块 · 数据日 {latest} · {med_txt}")
    else:
        print(f"[OK] 无需改动（已是最新，数据日 {latest}）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
