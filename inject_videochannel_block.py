#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
视频号快照 → 看板注入（数据驱动版）
====================================
把「微信视频号」截图 OCR 出的全国鱼价播报，结构化注入
「鳜鱼鲈鱼价格看板.html」的「补充 · 塘口价快照」板块末尾。

数据源：video_channel_snapshots_YYYYMMDD.json（人工核校，非自动爬取）
        - snapshots：按 source_account 分组，每个账号生成一张多期对比卡
        - articles ：公众号周报卡（鳜鱼/加州鲈分产区表 + 原文要点）
        - analysis ：交叉小结的手写分析段
锚点：<!-- VIDEOCHANNEL_LIVE_START --> ... <!-- VIDEOCHANNEL_LIVE_END -->
      首次运行会自动在 <!-- /塘口价快照 ... --> 之前插入锚点对，此后幂等替换。

用法：
  python3 inject_videochannel_block.py            # 用最新快照 JSON
  python3 inject_videochannel_block.py --json xxx.json
  python3 inject_videochannel_block.py --no-version   # 不 bump 版本号
"""
import os, re, sys, json, glob, argparse

HERE = os.path.dirname(os.path.abspath(__file__))
DASHBOARD = os.path.join(HERE, "鳜鱼鲈鱼价格看板.html")

VC_START = "<!-- VIDEOCHANNEL_LIVE_START -->"
VC_END = "<!-- VIDEOCHANNEL_LIVE_END -->"

SNAPSHOT_ANCHOR = "<!-- /塘口价快照"

RED = "#dc2626"    # 涨
GREEN = "#12a150"  # 跌
GRAY = "#6b7280"   # 平

EMOJI = {"互联惠农小洁": "🎬", "水产养殖服务于老师": "📈", "悠扬水产": "📊"}


def esc(s: str) -> str:
    return (str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


def tag_for(species: str) -> str:
    if "鳜" in species or "桂" in species:
        return "tag-gui"
    if "鲈" in species:
        return "tag-lu"
    return "tag"


def spec_cls(spec: str) -> str:
    if any(k in spec for k in ("斤", "两")):
        if "两" in spec and "斤" not in spec:
            return "spec-s"
        if "斤上" in spec or "起" in spec or "斤以上" in spec:
            return "spec-l"
        return "spec-m"
    return "spec"


def vs_color(text: str) -> str:
    if not text:
        return GRAY
    if "↑" in text or "涨" in text:
        return RED
    if "↓" in text or "跌" in text or "回落" in text or "低迷" in text:
        return GREEN
    return GRAY


def num_span(s: str):
    """'7.3~8.0' -> (7.3, 8.0)；解析失败返回 None"""
    m = re.findall(r"\d+(?:\.\d+)?", str(s) or "")
    if not m:
        return None
    vals = [float(x) for x in m]
    return (min(vals), max(vals))


def delta_text(prev: str, cur: str) -> str:
    a, b = num_span(prev), num_span(cur)
    if not a or not b:
        return "—"
    mid_a, mid_b = (a[0] + a[1]) / 2, (b[0] + b[1]) / 2
    d = round(mid_b - mid_a, 2)
    if abs(d) < 0.05:
        return "持平"
    return f"{'↑' if d > 0 else '↓'}{abs(d):g}"


def date_cn(d: str) -> str:
    return f"{int(d[5:7])}月{int(d[8:10])}日"


def signal_cell(row: dict) -> str:
    """原始标注单元格：优先 vs 文本，其次 trend 箭头"""
    vs = (row.get("vs") or "").strip()
    if vs:
        return (f'<td style="color:{vs_color(vs)};font-size:12px;'
                f'white-space:nowrap">{esc(vs)}</td>')
    arrow = {"up": "↗", "down": "↘", "flat": "→"}.get(row.get("trend", ""), "")
    if arrow:
        return f'<td style="color:{vs_color(arrow)};font-size:12px">{esc(arrow)}</td>'
    return "<td></td>"


# ---------------------------------------------------------------------------
# 卡片：按账号多期对比（通用）
# ---------------------------------------------------------------------------
def card_account(account: str, snaps) -> str:
    snaps = sorted(snaps, key=lambda s: s["price_date"])
    days = [s["price_date"] for s in snaps]
    span = (f"{date_cn(days[0])}–{date_cn(days[-1])}" if len(days) > 1
            else date_cn(days[0]))
    latest, prev = snaps[-1], (snaps[-2] if len(snaps) > 1 else None)
    prev_map = {r["species"]: r for r in prev["rows"]} if prev else {}
    date_cols = "".join(f"<th>{date_cn(d)}</th>" for d in days)

    trs = []
    for r in latest["rows"]:
        p = prev_map.get(r["species"], {})
        delta = delta_text(p.get("price", ""), r["price"]) if prev else "—"
        dcolor = vs_color(delta)
        cells = "".join(
            f'<td class="price"><b>{esc(r["price"])}</b></td>'
            if s2["price_date"] == latest["price_date"]
            else f'<td class="price">{esc(next((x["price"] for x in s2["rows"] if x["species"] == r["species"]), "—"))}</td>'
            for s2 in snaps)
        trs.append(
            f'<tr><td><span class="tag {tag_for(r["species"])}">{esc(r["species"])}</span></td>'
            f'<td><span class="spec {spec_cls(r["spec"])}">{esc(r["spec"])}</span></td>'
            f'{cells}'
            f'<td style="color:{dcolor};font-size:12px;white-space:nowrap">{esc(delta)}</td>'
            f'{signal_cell(r)}</tr>')

    gui = next((r for r in latest["rows"] if "鳜" in r["species"]), None)
    lu = next((r for r in latest["rows"] if "鲈" in r["species"]), None)
    gui_txt = f'鳜鱼（{esc(gui["spec"])}）{esc(gui["price"])} 元/斤' if gui else ""
    lu_txt = f'鲈鱼（{esc(lu["spec"])}）{esc(lu["price"])} 元/斤' if lu else ""
    head = "，".join(x for x in (lu_txt, gui_txt) if x)

    n = len(days)
    csub = (f'同一账号共 {n} 期播报，口径一致，可做逐期对比。'
            f'最新（{date_cn(latest["price_date"])}）：'
            + (f'<b>{head}</b>' if head else "本条无鳜鱼/鲈鱼报价")
            + '——以区间中值计算的最新期变化见表内「日变化」列。'
              '视频原始涨跌标注单列末列，与按区间中值计算的日变化可互相印证。')

    legends = "、".join(f'{s["price_date"]}《{esc(s.get("title", ""))}》' for s in snaps)
    comment = (latest.get("comment") or "").strip()

    parts = [
        '    <div class="card" style="margin-top:14px">\n',
        f'      <h3>{EMOJI.get(account, "🎬")} {span} · 视频号「{esc(account)}」全国参考塘口价（元/斤）</h3>\n',
        f'      <div class="csub">{csub}</div>\n',
        '      <table>\n',
        f'        <thead><tr><th>品种</th><th>规格</th>{date_cols}'
        f'<th>日变化(中值)</th><th>原始标注</th></tr></thead>\n',
        f'        <tbody>{"".join(trs)}</tbody>\n',
        '      </table>\n',
    ]
    if comment:
        parts.append(f'      <div class="callout" style="margin-top:10px">{esc(comment)}</div>\n')
    parts.append(
        f'      <div class="legend">来源：微信视频号「{esc(account)}」{legends}'
        f'（截图核校录入）· 注：箭头为原视频标注的较上期涨跌趋势，各地塘口价有差异，仅供参考</div>\n')
    parts.append('    </div>\n')
    return "".join(parts)


# ---------------------------------------------------------------------------
# 卡片：公众号周报（通用）
# ---------------------------------------------------------------------------
def card_article(art) -> str:
    gy = art.get("guiyu", {})
    jl = art.get("jialu", {})

    def tbl(rows):
        trs = "".join(
            f'<tr><td>{esc(r["region"])}</td>'
            f'<td><span class="spec {spec_cls(r["spec"])}">{esc(r["spec"])}</span></td>'
            f'<td class="price">{esc(r["price"])}</td></tr>'
            for r in rows)
        return trs

    other = art.get("other_species", {})
    other_li = "".join(f'<li><b>{esc(k)}：</b>{esc(v)}</li>' for k, v in other.items())
    gy_c = gy.get("comment", "")
    jl_c = jl.get("comment", "")
    callout = f'<b>鳜鱼原文要点：</b>{esc(gy_c)}<br><b>加州鲈原文要点：</b>{esc(jl_c)}'
    if other_li:
        callout += (f'<br><b>其他品种（超出本项目核心范围，仅摘录）：</b>'
                    f'<ul style="margin:6px 0 0;padding-left:20px;line-height:1.8">{other_li}</ul>')
    return (
        f'    <div class="card" style="margin-top:14px">\n'
        f'      <h3>📰 {esc(art["publish_date"])} · {esc(art.get("source_account", ""))} 周报</h3>\n'
        f'      <div class="csub">{esc(art.get("summary", ""))}</div>\n'
        f'      <div class="grid2">'
        f'<div><h3 style="font-size:14px;margin:6px 0 8px"><span class="tag tag-gui">鳜鱼</span>'
        f' 分产区塘口价（元/斤）</h3><table><thead><tr><th>产区</th><th>规格</th><th>塘口价</th></tr></thead>'
        f'<tbody>{tbl(gy.get("rows", []))}</tbody></table></div>'
        f'<div><h3 style="font-size:14px;margin:6px 0 8px"><span class="tag tag-lu">加州鲈</span>'
        f' 分产区塘口价（元/斤）</h3><table><thead><tr><th>产区</th><th>规格</th><th>塘口价</th></tr></thead>'
        f'<tbody>{tbl(jl.get("rows", []))}</tbody></table></div></div>\n'
        f'      <div class="callout" style="margin-top:12px">{callout}</div>\n'
        f'      <div class="legend">来源：{esc(art.get("source_account", ""))} {esc(art["publish_date"])}'
        f'《{esc(art["title"])}》· <a class="plink" href="{esc(art["url"])}" target="_blank" '
        f'rel="noopener">📄 阅读原文</a> · 价格受规格、卖相等因素影响较大，仅供参考</div>\n'
        f'    </div>\n')


# ---------------------------------------------------------------------------
# 交叉小结（计算生成 + 手写分析）
# ---------------------------------------------------------------------------
def build_summary(data) -> str:
    snaps = data["snapshots"]
    accounts = sorted({s["source_account"] for s in snaps})

    def latest_quote(account, kw):
        best = None
        for s in snaps:
            if s["source_account"] != account:
                continue
            r = next((r for r in s["rows"] if kw in r["species"]), None)
            if r and (best is None or s["price_date"] > best[0]):
                best = (s["price_date"], r)
        return best

    trs = []
    for label, kw in (("鳜鱼", "鳜"), ("鲈鱼（加州鲈）", "鲈")):
        rows = [(a, latest_quote(a, kw)) for a in accounts]
        rows = [(a, q) for a, q in rows if q]
        if not rows:
            continue
        for idx, (a, q) in enumerate(rows):
            name_cell = (f'<td rowspan="{len(rows)}"><span class="tag {tag_for(kw)}">{label}</span></td>'
                         if idx == 0 else "")
            trs.append(f'<tr>{name_cell}'
                       f'<td>{esc(a)}（{date_cn(q[0])} · {esc(q[1]["spec"])}）</td>'
                       f'<td class="price"><b>{esc(q[1]["price"])}</b></td>'
                       f'{signal_cell(q[1])}</tr>')

    analysis = (data.get("analysis") or "").strip()
    first, last = min(s["price_date"] for s in snaps), max(s["price_date"] for s in snaps)
    gen = data.get("generated_at_cst", "")[:10]
    callout = (f'      <div class="callout" style="margin-top:12px"><b>结论：</b>{esc(analysis)}</div>\n'
               if analysis else "")
    return (
        f'    <div class="card" style="margin-top:14px;border-left:4px solid #7c3aed;background:#faf5ff">\n'
        f'      <h3>🧭 跨源交叉小结（{date_cn(first)}–{date_cn(last)}）</h3>\n'
        f'      <div class="csub">共 <b>{len(accounts)} 个视频号</b>'
        f'（{"、".join(esc(a) for a in accounts)}）+ <b>{len(data.get("articles", []))} 篇公众号周报</b>，'
        f'下表为各号<b>最新一期</b>的鳜鱼/鲈鱼报价。</div>\n'
        f'      <table>\n'
        f'        <thead><tr><th>品种</th><th>来源（日期 · 规格）</th><th>报价（元/斤）</th>'
        f'<th>原始标注</th></tr></thead>\n'
        f'        <tbody>{"".join(trs)}</tbody>\n'
        f'      </table>\n'
        f'{callout}'
        f'      <div class="legend">本小结由上述来源交叉比对自动生成，'
        f'各源规格/产区口径不同，绝对值不可直接横向比较 · 数据录入时间 {esc(gen)}</div>\n'
        f'    </div>\n')


def build_block(data) -> str:
    by_account = {}
    for s in data["snapshots"]:
        by_account.setdefault(s["source_account"], []).append(s)
    accounts = sorted(by_account, key=lambda a: max(s["price_date"] for s in by_account[a]),
                      reverse=True)
    cards = [card_account(a, by_account[a]) for a in accounts]
    for art in data.get("articles", []):
        cards.append(card_article(art))
    cards.append(build_summary(data))
    return VC_START + "\n" + "".join(cards) + "    " + VC_END


def find_latest_json(override=None) -> str:
    if override:
        return override
    files = sorted(glob.glob(os.path.join(HERE, "video_channel_snapshots_*.json")))
    if not files:
        raise SystemExit("[ERR] 未找到 video_channel_snapshots_*.json")
    return files[-1]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", help="快照 JSON 路径")
    ap.add_argument("--no-version", action="store_true", help="不 bump 版本号")
    args = ap.parse_args()

    path = find_latest_json(args.json)
    data = json.load(open(path, encoding="utf-8"))
    block = build_block(data)

    html = open(DASHBOARD, encoding="utf-8").read()

    if VC_START in html and VC_END in html:
        i = html.index(VC_START)
        j = html.index(VC_END) + len(VC_END)
        html = html[:i] + block + html[j:]
        print("[OK] 幂等替换 VIDEOCHANNEL_LIVE 区块")
    else:
        k = html.index(SNAPSHOT_ANCHOR)
        sec_end = html.rindex("</section>", 0, k)
        html = html[:sec_end] + block + "\n  " + html[sec_end:]
        print("[OK] 首次插入 VIDEOCHANNEL_LIVE 锚点与区块")

    # 板块标题同步（幂等：已是目标文本则不再改）
    new_sub = (data.get("section_subtitle") or "").strip()
    if new_sub:
        target = f"<h2>{esc(new_sub)}</h2>"
        if target not in html:
            html, n = re.subn(r"<h2>补充 · 塘口价快照（[^<]*）</h2>", target, html, count=1)
            print(f"[OK] 板块标题{'已更新' if n else '未找到(跳过)'}")

    open(DASHBOARD, "w", encoding="utf-8").write(html)
    print(f"[OK] 已注入 {len(data['snapshots'])} 条视频号快照 + "
          f"{len(data.get('articles', []))} 篇文章摘要")

    if not args.no_version:
        try:
            from dashboard_version import bump_dashboard, stamp_updated_at
            v = bump_dashboard(
                reason="视频号快照刷新（inject_videochannel_block.py 数据驱动重构）",
                level="patch")
            ts = stamp_updated_at()
            print(f"[OK] 版本 {v} · 看板更新时间戳 {ts}")
        except Exception as e:
            print(f"[WARN] 版本号/时间戳更新失败: {e}", file=sys.stderr)


if __name__ == "__main__":
    main()
