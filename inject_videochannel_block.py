#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
视频号快照 → 看板注入
======================
把「微信视频号」截图 OCR 出的全国鱼价播报，结构化注入
「鳜鱼鲈鱼价格看板.html」的「补充 · 塘口价快照」板块末尾。

数据源：video_channel_snapshots_YYYYMMDD.json（人工核校，非自动爬取）
锚点：<!-- VIDEOCHANNEL_LIVE_START --> ... <!-- VIDEOCHANNEL_LIVE_END -->
      首次运行会自动在 <!-- /塘口价快照 ... --> 之前插入锚点对，此后幂等替换。

用法：
  python3 inject_videochannel_block.py            # 用最新快照 JSON
  python3 inject_videochannel_block.py --json xxx.json
  python3 inject_videochannel_block.py --no-version   # 不 bump 版本号
"""
import os, re, sys, json, glob, argparse
from datetime import datetime

HERE = os.path.dirname(os.path.abspath(__file__))
DASHBOARD = os.path.join(HERE, "鳜鱼鲈鱼价格看板.html")

VC_START = "<!-- VIDEOCHANNEL_LIVE_START -->"
VC_END = "<!-- VIDEOCHANNEL_LIVE_END -->"

SNAPSHOT_ANCHOR = "<!-- /塘口价快照"

RED = "#dc2626"    # 涨
GREEN = "#12a150"  # 跌
GRAY = "#6b7280"   # 平


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


def trend_cell(text: str) -> str:
    if not text:
        return "<td></td>"
    return (f'<td style="color:{vs_color(text)};font-size:12px;'
            f'white-space:nowrap">{esc(text)}</td>')


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


# ---------------------------------------------------------------------------
# 各快照卡片
# ---------------------------------------------------------------------------
def card_huinong(snaps) -> str:
    """互联惠农小洁 逐日对比表（动态多日，snaps 按日期升序）"""
    date_cn = lambda d: f"{int(d[5:7])}月{int(d[8:10])}日"
    days = [s["price_date"] for s in snaps]
    span = f"{date_cn(days[0])}–{date_cn(days[-1])}" if len(days) > 1 else date_cn(days[0])
    latest, prev = snaps[-1], snaps[-2] if len(snaps) > 1 else None
    prev_map = {r["species"]: r for r in prev["rows"]} if prev else {}
    date_cols = "".join(f"<th>{date_cn(d)}</th>" for d in days)
    trs = []
    for r in latest["rows"]:
        p = prev_map.get(r["species"], {})
        delta = delta_text(p.get("price", ""), r["price"]) if prev else "—"
        arrow = {"up": "↗", "down": "↘", "flat": "→"}.get(r.get("trend", ""), "")
        dcolor = vs_color(delta)
        cells = "".join(
            f'<td class="price"><b>{esc(r["price"])}</b></td>' if s2["price_date"] == latest["price_date"]
            else f'<td class="price">{esc(next((x["price"] for x in s2["rows"] if x["species"] == r["species"]), "—"))}</td>'
            for s2 in snaps)
        trs.append(
            f'<tr><td><span class="tag {tag_for(r["species"])}">{esc(r["species"])}</span></td>'
            f'<td><span class="spec {spec_cls(r["spec"])}">{esc(r["spec"])}</span></td>'
            f'{cells}'
            f'<td style="color:{dcolor};font-size:12px;white-space:nowrap">{esc(delta)}</td>'
            f'<td style="color:{dcolor};font-size:12px;white-space:nowrap">{esc(arrow)}</td></tr>')
    gui = next((r for r in latest["rows"] if "鳜" in r["species"]), None)
    lu = next((r for r in latest["rows"] if "鲈" in r["species"]), None)
    gui_txt = f'鳜鱼（{esc(gui["spec"])}）{esc(gui["price"])} 元/斤' if gui else ""
    lu_txt = f'鲈鱼（{esc(lu["spec"])}）{esc(lu["price"])} 元/斤' if lu else ""
    legends = "、".join(
        f'{s["price_date"]}《{esc(s.get("title", ""))}》' for s in snaps)
    return (
        f'    <div class="card" style="margin-top:14px">\n'
        f'      <h3>🎬 {span} · 视频号「互联惠农小洁」全国参考塘口价（元/斤）</h3>\n'
        f'      <div class="csub">同一账号连续 {len(days)} 日播报，口径一致，可做逐日对比。'
        f'最新（{date_cn(latest["price_date"])}）：<b>{lu_txt}，{gui_txt}</b>——'
        f'以区间中值计算的最新日变化见表内「日变化」列。'
        f'视频原始涨跌标注（↗/↘）单列末列，与本表按区间中值计算的日变化可互相印证。</div>\n'
        f'      <table>\n'
        f'        <thead><tr><th>品种</th><th>规格</th>{date_cols}'
        f'<th>日变化(中值)</th><th>原始标注</th></tr></thead>\n'
        f'        <tbody>{"".join(trs)}</tbody>\n'
        f'      </table>\n'
        f'      <div class="callout" style="margin-top:10px"><b>口径提示：</b>'
        f'原始标注为视频箭头趋势（较昨日），「日变化」列按报价区间中值计算，'
        f'两种口径偶有方向差异（区间报价正常波动），并存如实记录不作调整。</div>\n'
        f'      <div class="legend">来源：微信视频号「互联惠农小洁」{legends}'
        f'（截图核校录入）· 注：箭头为原视频标注的较昨日涨跌趋势，各地塘口价有差异，仅供参考</div>\n'
        f'    </div>\n')


def card_youyang(snap) -> str:
    """悠扬水产 10.8"""
    groups = {}
    for r in snap["rows"]:
        groups.setdefault(r.get("group", "其他"), []).append(r)
    cols = []
    for gname, rows in groups.items():
        trs = "".join(
            f'<tr><td><span class="tag {tag_for(r["species"])}">{esc(r["species"])}</span></td>'
            f'<td><span class="spec {spec_cls(r["spec"])}">{esc(r["spec"])}</span></td>'
            f'<td class="price">{esc(r["price"])}</td>'
            f'{trend_cell(r.get("vs", ""))}</tr>'
            for r in rows)
        cols.append(
            f'<div><h3 style="font-size:14px;margin:6px 0 8px">{esc(gname)}'
            f'<span style="font-size:12px;color:#6b7280;font-weight:400"> · 塘口出塘价</span></h3>'
            f'<table><thead><tr><th>品种</th><th>规格</th><th>元/斤</th><th>趋势</th></tr></thead>'
            f'<tbody>{trs}</tbody></table></div>')
    return (
        f'    <div class="card" style="margin-top:14px">\n'
        f'      <h3>📊 10月8日 · 视频号「悠扬水产」全国鱼价（普水鱼 + 特种水产，元/斤）</h3>\n'
        f'      <div class="csub">覆盖面最全的一条播报（14 个品种）。<b>特种水产两极：</b>'
        f'<b style="color:{RED}">鳜鱼（1.2斤起）26.5~28.0 走强</b>、叉尾鮰/翘嘴微涨；'
        f'<b style="color:{GREEN}">黄颡鱼（3两上）10.8~11.5 偏弱</b>；加州鲈（1斤起）11.2~12.0 震荡。'
        f'普水鱼以平稳为主，鳊鱼、花鲢小幅上涨。</div>\n'
        f'      <div class="grid2">{"".join(cols)}</div>\n'
        f'      <div class="legend">来源：微信视频号「悠扬水产」2026-10-08《2026.10.8全国鱼价 买鱼卖鱼作为参考》'
        f'（截图核校录入）· 塘口出塘价，随行就市，仅供参考</div>\n'
        f'    </div>\n')


def card_laoshi(snap) -> str:
    """水产养殖服务于老师 10.7"""
    trs = "".join(
        f'<tr><td><span class="tag {tag_for(r["species"])}">{esc(r["species"])}</span></td>'
        f'<td><span class="spec {spec_cls(r["spec"])}">{esc(r["spec"])}</span></td>'
        f'<td class="price">{esc(r["price"])}</td>'
        f'{trend_cell(r.get("vs", ""))}</tr>'
        for r in snap["rows"])
    return (
        f'    <div class="card" style="margin-top:14px">\n'
        f'      <h3>📉 10月7日 · 视频号「水产养殖服务于老师」全国鱼价（元/斤）</h3>\n'
        f'      <div class="csub">整体<b style="color:{GREEN}">偏弱</b>：13 个品种中 6 跌 6 平 1 涨。'
        f'最弱为鳜鱼（1.2斤上）<b>22~25 元/斤</b>、白鲢（2斤上）2.2~2.6、鲫鱼 6-8两 7.2~7.8 持续低迷；'
        f'唯一上行是黑鱼（2斤上统货）7.6~9.2。加州鲈（1斤上）8.0~11 持续震荡。</div>\n'
        f'      <table>\n'
        f'        <thead><tr><th>品种</th><th>规格</th><th>参考价</th><th>趋势</th></tr></thead>\n'
        f'        <tbody>{trs}</tbody>\n'
        f'      </table>\n'
        f'      <div class="callout" style="margin-top:10px"><b>与该账号同口径提示：</b>'
        f'本条鳜鱼报价 22~25 元/斤，低于同日的「互联惠农小洁」29.5~31.2（规格 0.8-1.2斤）'
        f'与「悠扬水产」26.5~28.0（规格 1.2斤起）——<b>差异主要来自规格与产区口径</b>，'
        f'不可直接横向比较。三条源共同指向的结论是：<b>鳜鱼仍在底部区域震荡，未走出下行通道</b>。</div>\n'
        f'      <div class="legend">来源：微信视频号「水产养殖服务于老师」2026-10-07《2026.10.7全国鱼价 '
        f'涨跌一目了然，卖鱼收鱼参考》（截图核校录入）· 行情为市场参考价，各地有区域差价，实际成交以塘口现场议价为准</div>\n'
        f'    </div>\n')


def card_article(art) -> str:
    """水产养殖网 10-05 周报"""
    gy = art["guiyu"]
    gy_trs = "".join(
        f'<tr><td>{esc(r["region"])}</td>'
        f'<td><span class="spec {spec_cls(r["spec"])}">{esc(r["spec"])}</span></td>'
        f'<td class="price">{esc(r["price"])}</td></tr>'
        for r in gy["rows"])
    jl = art["jialu"]
    jl_trs = "".join(
        f'<tr><td>{esc(r["region"])}</td>'
        f'<td><span class="spec {spec_cls(r["spec"])}">{esc(r["spec"])}</span></td>'
        f'<td class="price">{esc(r["price"])}</td></tr>'
        for r in jl["rows"])
    other = art["other_species"]
    other_li = "".join(
        f'<li><b>{esc(k)}：</b>{esc(v)}</li>' for k, v in other.items())
    return (
        f'    <div class="card" style="margin-top:14px">\n'
        f'      <h3>📰 {esc(art["publish_date"])} · 水产养殖网（强渔）周报：鳜鱼再跌 3 元，加州鲈低位僵持</h3>\n'
        f'      <div class="csub">{esc(art["summary"])}</div>\n'
        f'      <div class="grid2">'
        f'<div><h3 style="font-size:14px;margin:6px 0 8px"><span class="tag tag-gui">鳜鱼</span>'
        f' 分产区塘口价（元/斤）</h3><table><thead><tr><th>产区</th><th>规格</th><th>塘口价</th></tr></thead>'
        f'<tbody>{gy_trs}</tbody></table></div>'
        f'<div><h3 style="font-size:14px;margin:6px 0 8px"><span class="tag tag-lu">加州鲈</span>'
        f' 分产区塘口价（元/斤）</h3><table><thead><tr><th>产区</th><th>规格</th><th>塘口价</th></tr></thead>'
        f'<tbody>{jl_trs}</tbody></table></div></div>\n'
        f'      <div class="callout" style="margin-top:12px"><b>鳜鱼原文要点：</b>{esc(gy["comment"])}<br>'
        f'<b>加州鲈原文要点：</b>{esc(jl["comment"])}<br>'
        f'<b>其他品种（超出本项目核心范围，仅摘录）：</b>'
        f'<ul style="margin:6px 0 0;padding-left:20px;line-height:1.8">{other_li}</ul></div>\n'
        f'      <div class="legend">来源：微信公众号「水产养殖网」2026-10-05 16:29《消费太差！鳜鱼再跌3元、'
        f'黄骨鱼鮰鱼下滑，黑鱼还能撑几天？》· <a class="plink" href="{esc(art["url"])}" target="_blank" '
        f'rel="noopener">📄 阅读原文（水产养殖网 10-05 周报）</a> · 价格受规格、卖相等因素影响较大，仅供参考</div>\n'
        f'    </div>\n')


def build_block(data) -> str:
    snaps = {s["source_account"] + "|" + s["price_date"]: s for s in data["snapshots"]}
    hn = sorted((s for s in data["snapshots"] if s["source_account"] == "互联惠农小洁"),
                key=lambda s: s["price_date"])
    youyang = snaps["悠扬水产|2026-10-08"]
    laoshi = snaps["水产养殖服务于老师|2026-10-07"]

    cards = [card_huinong(hn),
             card_youyang(youyang),
             card_laoshi(laoshi)]
    for art in data.get("articles", []):
        cards.append(card_article(art))

    # 小结卡片
    summary = (
        f'    <div class="card" style="margin-top:14px;border-left:4px solid #7c3aed;background:#faf5ff">\n'
        f'      <h3>🧭 10月7–9日 四源交叉小结：鳜鱼磨底、鲈鱼低位僵持</h3>\n'
        f'      <div class="csub">本期共 <b>4 个独立来源</b>（3 条视频号播报 + 1 篇公众号周报，'
        f'其中「互联惠农小洁」含 10-07/08/09 连续三日），覆盖 10-05 ~ 10-09。</div>\n'
        f'      <table>\n'
        f'        <thead><tr><th>品种</th><th>来源（日期 · 规格）</th><th>报价（元/斤）</th>'
        f'<th>信号</th></tr></thead>\n'
        f'        <tbody>\n'
        f'          <tr><td rowspan="5"><span class="tag tag-gui">鳜鱼</span></td>'
        f'<td>水产养殖网（10-05 · 广东鱼仔鳜）</td><td class="price">24~25</td>'
        f'<td style="color:{GREEN};font-size:12px">↓ 周跌 3 元，探底</td></tr>\n'
        f'          <tr><td>水产养殖服务于老师（10-07 · 1.2斤上）</td><td class="price">22~25</td>'
        f'<td style="color:{GREEN};font-size:12px">↓ 小幅震荡</td></tr>\n'
        f'          <tr><td>悠扬水产（10-08 · 1.2斤起）</td><td class="price"><b>26.5~28.0</b></td>'
        f'<td style="color:{RED};font-size:12px">↑ 走强（较 22~25 回升）</td></tr>\n'
        f'          <tr><td>互联惠农小洁（10-08 · 0.8-1.2斤）</td><td class="price">29.5~31.2</td>'
        f'<td style="color:{RED};font-size:12px">↗ 标注上涨（区间微降 0.3）</td></tr>\n'
        f'          <tr><td>互联惠农小洁（10-09 · 0.8-1.2斤）</td><td class="price"><b>30.0~31.5</b></td>'
        f'<td style="color:{RED};font-size:12px">↗ 连续两日标注上涨（中值 +0.15）</td></tr>\n'
        f'          <tr><td rowspan="4"><span class="tag tag-lu">鲈鱼<br>（加州鲈）</span></td>'
        f'<td>水产养殖网（10-05 · 广东佛山 1斤以上）</td><td class="price">9</td>'
        f'<td style="color:{GRAY};font-size:12px">→ 弱势僵持</td></tr>\n'
        f'          <tr><td>水产养殖服务于老师（10-07 · 1斤上）</td><td class="price">8.0~11</td>'
        f'<td style="color:{GREEN};font-size:12px">↓ 持续震荡</td></tr>\n'
        f'          <tr><td>悠扬水产（10-08 · 1斤起）</td><td class="price">11.2~12.0</td>'
        f'<td style="color:{GRAY};font-size:12px">→ 震荡</td></tr>\n'
        f'          <tr><td>互联惠农小洁（10-09 · 0.8-1.2斤）</td><td class="price"><b>13.5~15.0</b></td>'
        f'<td style="color:{GREEN};font-size:12px">↘ 连续两日标注回落</td></tr>\n'
        f'        </tbody>\n'
        f'      </table>\n'
        f'      <div class="callout" style="margin-top:12px"><b>结论：</b>\n'
        f'<ul style="margin:6px 0 0;padding-left:20px;line-height:1.85">\n'
        f'<li><b>鳜鱼：</b>8 月中旬 42 元的高位已回落到 22~31 元区间，'
        f'10-05 周报定性「跌势暂未见底、冷库未大规模收鱼」；10-07 的 22~25 为当前可见最低档，'
        f'10-08 悠扬报 1.2 斤起 26.5~28.0 走强、10-09 小洁 30.0~31.5 连续标注 ↗——'
        f'<b>底部区域出现规格间分化与局部企稳迹象，但尚不构成反转</b>。'
        f'与本看板「水产前沿第 35 期（09-29）江苏标鳜 31」相比，标鱼口径已进一步下探至 25~26（10-05）。</li>\n'
        f'<li><b>鲈鱼（加州鲈）：</b>四源一致指向<b>低位僵持</b>——广东 8~9、江苏 10.5、四川 12，'
        f'产区价差明显；广东受天气影响病鱼增多、挑鱼压价突出。小洁口径 0.8-1.2 斤 13.5~15.0 连续回落，'
        f'存塘偏高、消费疲软，短期无上行驱动。</li>\n'
        f'<li><b>共性驱动：</b>节日红利消退 + 供给充裕 + 消费疲软；鳜鱼另有「三年增产 20 万吨」的结构性压力，'
        f'加州鲈则受新鱼上市与病鱼压价双重压制。</li>\n'
        f'<li><b>给塘口（江苏/宜兴）的提示：</b>规格够的顺势分批出、避免节后扎堆踩踏；'
        f'关注 ISKNV 等病害防控与水温应激（近期昼夜温差 7~8℃）；价格口径以<b>塘口议价</b>为准，'
        f'视频号/公众号报价仅作趋势参考。</li>\n'
        f'</ul></div>\n'
        f'      <div class="legend">本小结由上述 4 个来源交叉比对生成，'
        f'各源规格/产区口径不同，绝对值不可直接横向比较 · 数据录入时间 2026-10-09</div>\n'
        f'    </div>\n')

    cards.append(summary)
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
        # 回退到 </section> 之前插入
        sec_end = html.rindex("</section>", 0, k)
        html = html[:sec_end] + block + "\n  " + html[sec_end:]
        print("[OK] 首次插入 VIDEOCHANNEL_LIVE 锚点与区块")

    # 板块标题 + note 同步日期
    html = html.replace(
        "补充 · 塘口价快照（2026-09-10/11/13/14/29/30 · 10-05/07/08 · 公众号/视频号 OCR）",
        "补充 · 塘口价快照（2026-09-10/11/13/14/29/30 · 10-05/07/08/09 · 公众号/视频号 OCR）")
    html = html.replace("无锡盛阳食品城（9.29）", "无锡盛阳食品城（10.9）")
    html = html.replace(
        "视频号「互联惠农小洁」「悠扬水产」「水产养殖服务于老师」（10.7/10.8）",
        "视频号「互联惠农小洁」「悠扬水产」「水产养殖服务于老师」（10.7/10.8/10.9）")

    open(DASHBOARD, "w", encoding="utf-8").write(html)
    print(f"[OK] 已注入 {len(data['snapshots'])} 条视频号快照 + "
          f"{len(data.get('articles', []))} 篇文章摘要")

    if not args.no_version:
        try:
            from dashboard_version import bump_dashboard, stamp_updated_at
            v = bump_dashboard(
                reason="视频号三方播报(10-07/08 互联惠农小洁·悠扬水产·水产养殖服务于老师)+"
                       "水产养殖网10-05周报，四源交叉小结(鳜鱼磨底22~31/鲈鱼低位僵持)",
                level="minor")
            ts = stamp_updated_at()
            print(f"[OK] 版本 {v} · 看板更新时间戳 {ts}")
        except Exception as e:
            print(f"[WARN] 版本号/时间戳更新失败: {e}", file=sys.stderr)


if __name__ == "__main__":
    main()
