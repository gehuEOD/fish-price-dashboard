#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""2026-11-16 批次：3 链接 + 3 截图判定 → 3 张新卡 + chip 快览同步（幂等）。

链接判定：
  1. 通威农牧《涨跌互现：特水大规格撑价…｜一周鱼价行情》（发布 2026-11-13 18:27）
     —— 与看板「🐟 通威农牧 · 一周鱼价行情 2026-11-13」同文（tongwei 已 11-13），
     重复链接，跳过。
  2. 全国渔业价格《渔飞鱼水产行情日报（2026年11月16日）》（发布 2026-11-15 18:00）
     —— 录入。21food 产区价 11/15 鳜鱼三档全线上升（≥750g 58.5→60.5 元/公斤
     ≈30.25 元/斤 +3.4%，连涨第三天）；白沙洲 11/15 未刷新、表内沿用 11/14 值；
     加州鲈惠农产地均价 11.69 元/斤 平（vs 11/15）。
  3. 绿色水产技术《渔飞鱼水产 鱼虾蟹每日行情报价 2026年11月16日》（发布 11-16 07:34）
     —— 录入（新源 lvse_baojia）。加州鲈三产区（佛山 1斤上 11.0 / 湖州 10.5 /
     成都 11.5，均周跌 0.1）；本篇无鳜鱼段，如实留空。该系列与 11-05 卡之间
     11-06~11-15 未采集，隔期只列本期数值与原文箭头，不作两期比较。

截图判定：
  A. 科学养鱼「11月13日黄颡鱼、乌鳢、泥鳅…」正文 加州鲈 / 鳜鱼 两张列表截图
     —— 与看板已有「🌊 11月13日 · 全国分市场批发价（科学养鱼）」卡逐项一致
     （鳜鱼 12 条、加州鲈 12 条全部同值同规格同市场），重复，跳过。
  B. 盛阳食品城 2026.11.16 批发价表 —— 录入。鳜鱼（桂鱼）25~30、鲈鱼 10~14，
     与 11.15 卡逐项同值、未标沿用 → 同值并列。

口径：只录鳜鱼 / 加州鲈；多口径禁止互减；同值未标「沿用」不推断涨跌；
跨期核校仅限同市场同规格且原文明确给出涨跌；行情建议（「按 30 元/斤谈」）
不作为价格数据录入。

V2 桥接注意：
  - 日报 11-16 卡标题含「📰 全国渔业价格」→ CLUE_SPECS 自动按日期取最新，
    线索随之更新；盛阳卡同理（「🛒 + 无锡盛阳食品城」）。
  - 鱼虾蟹报价系列历来不入 CLUE_SPECS（11-04/11-05 期同），线索容量 12
    恰好容纳 11-16×2 + 11-15×1 + 11-14×1 + 11-13×7 + 11-12×1，不扩容。
  - 新卡不含「江苏」加州鲈绝对价行 → 不会被 LU_POND_SPECS 误选，assert 不触发。
  - 日报/鱼虾蟹卡标题不含 GUI_POND_SPECS / WEEKLY_SPECS 关键词，不干扰 KPI。
"""
import re
import sys

HTML = "鳜鱼鲈鱼价格看板.html"
URL_DAILY = "https://mp.weixin.qq.com/s/8HmZMDMMGr5-I4PCwHvlUA"
URL_BAOJIA = "https://mp.weixin.qq.com/s/71quxR-N1Fk4peiDr_Zs_A"

ANCHOR_DAILY = "📰 全国渔业价格 ·《渔飞鱼水产行情日报 2026-11-15》"
ANCHOR_SY = "🛒 2026.11.15 · 无锡盛阳食品城"
GUARDS = [
    "渔飞鱼水产行情日报 2026-11-16",
    "《鱼虾蟹每日行情报价 2026年11月16日》（发布 11-16 07:34",
    "🛒 2026.11.16 · 无锡盛阳食品城",
]

CARD_DAILY = """
<div class="card" style="margin-top:14px">
  <h3>📰 全国渔业价格 ·《渔飞鱼水产行情日报 2026-11-16》（发布 11-15 18:00 · 白沙洲沿用 11/14 · 鳜鱼产区连涨第三天 / 鲈鱼产地均价持平）</h3>
  <div class="csub">「全国渔业价格」11-15 18:00 发布 11-16 期日报。原文自述「明日 21 品种呈 2 涨 0 跌、19 行持平或沿用」，<b>白沙洲官网 11/15 最新发布仍停在 11/14、表内 12 个白沙洲品种全部沿用 14 日值</b>。本看板只跟踪鳜鱼 / 加州鲈两类：<b>鳜鱼 21food 产区价（11/15）三档全线上升</b>——≥750g 58.5→60.5 元/公斤 ≈ 30.25 元/斤（+2 元 / +3.4%）、500~750g 58.0 ≈ 29.00 元/斤（+2 元）、250~500g 47.5 ≈ 23.75 元/斤（+1 元），原文称<b>连涨第三天</b>；白沙洲鳜鱼 ≥750g 仍 58.50 元/公斤（11/14 值，今日未刷新）；<b>加州鲈惠农产地均价 11.69 元/斤、平（vs 11/15）</b>。</div>
  <table><thead><tr><th>品种</th><th>口径 · 来源</th><th>价格</th><th>原文标注</th></tr></thead><tbody>
        <tr><td><b>鳜鱼</b></td><td><span class="spec spec-s">21food 产区价 · 条重≥750g（11/15）</span></td><td class="price"><b>58.5 → 60.5 元/公斤 ≈ 30.25 元/斤</b></td><td style="font-size:12px">▲ +2 元/公斤 / +3.4% · 连涨第三天</td></tr>
        <tr><td><b>鳜鱼</b></td><td><span class="spec spec-s">21food 产区价 · 500≤条重&lt;750g（11/15）</span></td><td class="price"><b>58.0 元/公斤 ≈ 29.00 元/斤</b></td><td style="font-size:12px">▲ +2 元/公斤</td></tr>
        <tr><td><b>鳜鱼</b></td><td><span class="spec spec-s">21food 产区价 · 250≤条重&lt;500g（11/15）</span></td><td class="price"><b>47.5 元/公斤 ≈ 23.75 元/斤</b></td><td style="font-size:12px">▲ +1 元/公斤</td></tr>
        <tr><td><b>鳜鱼</b></td><td><span class="spec spec-s">武汉白沙洲批发 · ≥750g（11/14 沿用）</span></td><td class="price"><b>58.50 元/公斤 ≈ 29.25 元/斤</b></td><td style="font-size:12px">沿用值 · 原文「今日未刷新」</td></tr>
        <tr><td><b>加州鲈</b></td><td><span class="spec spec-s">惠农产地均价 · 鲜活（11/15）</span></td><td class="price"><b>11.69 元/斤</b></td><td style="font-size:12px">平（vs 11/15）</td></tr>
  </tbody></table>
  <div class="callout" style="margin-top:12px"><b>跨期核校 / 多口径说明：</b>① 原文标题为 11-16 期、发布时间 11-15 18:00、正文多处把 11/16 称「明日 / 明天」，本卡按 21food <b>11/15 产区价</b> + 白沙洲 <b>11/14 沿用值</b>分口径记录，不推断采集日。② <b>产区 vs 批发</b>：原文自比「产区比批发端高出 1 元/斤，说明这轮涨价还没走到市场」，<b>按原文照录</b>；21food 产区价与白沙洲销地批发为不同渠道，渠道间不作互减。③ 跨期核校（仅限同市场同规格）：白沙洲 ≥750g 的 58.50 与 11-15 期卡同值（沿用，原文明确「今日未刷新」），<b>不作两期比较</b>；21food 11/15 与 11-15 期卡白沙洲 58.50 渠道不同，<b>不互减</b>。④ 本卡为<b>批发 / 产区参考价（元/公斤，折元/斤仅供阅读）</b>，与鳜康泰 11-14 塘口报价（江苏标鳜 24.5 元/斤）、科学养鱼 11-13 分市场批发、通威 11-13 全国塘口均价、视频号全国参考区间、渔无忧 11-14 次日预测<b>规格·时间·渠道三重不同，多口径并存、禁止互减</b>；原文「明天按 30 元/斤谈」为卖鱼谈判建议，<b>不作为价格数据录入</b>。⑤ 原文称「四个规格全线上升」但正文仅列三档绝对价，<b>按原文照录、不自行补足</b>。</div>
  <div class="legend">来源：微信公众号「全国渔业价格」11-15 18:00《渔飞鱼水产行情日报（2026年11月16日），冷空气推迟！17日热到28℃ 沼虾一天跳涨10.5% 鳜鱼全国均价破60元》· <a class="plink" href="__URL_DAILY__" target="_blank" rel="noopener">📄 阅读原文（日报 11-16）</a> · 21food 产区 11/15 + 白沙洲 11/14 沿用 · 元/公斤 / 元/斤 多口径，仅供参考</div>
</div>
""".replace("__URL_DAILY__", URL_DAILY)

CARD_BAOJIA = """
<div class="card" style="margin-top:14px">
  <h3>🐟 渔飞鱼 ·《鱼虾蟹每日行情报价 2026年11月16日》（发布 11-16 07:34 · 加州鲈三产区周跌 0.1）</h3>
  <div class="csub">该号 11-16 日报（绿色水产技术公众号）。<b>加州鲈：广东佛山 1斤上 11.0 元/斤（周跌 0.1）、浙江湖州 10.5（周跌 0.1）、四川成都 11.5（周跌 0.1）</b>。<b>本篇无鳜鱼段，如实留空</b>。今日重点：周一塘口行情偏弱、常规淡水鱼多数小幅回调（鲫鱼湖南常德 3~4 两 10.8 跌 0.2）、白虾佛山 30 头 18.4 微跌、河蟹苏州 3 两母 65 回落、罗氏沼虾三地各周跌 0.5。</div>
  <table style="width:100%;border-collapse:collapse;font-size:13px"><thead><tr><th>品种</th><th>产区/规格</th><th>价格（元/斤）</th><th>备注</th></tr></thead><tbody>
        <tr><td><span class="tag tag-lu">加州鲈</span></td><td><span class="spec spec-m">广东佛山 1斤上</span></td><td class="price"><b>11.0</b></td><td style="color:#16a34a;font-size:12px">周跌 0.1</td></tr>
        <tr><td><span class="tag tag-lu">加州鲈</span></td><td><span class="spec spec-m">浙江湖州</span></td><td class="price"><b>10.5</b></td><td style="color:#16a34a;font-size:12px">周跌 0.1</td></tr>
        <tr><td><span class="tag tag-lu">加州鲈</span></td><td><span class="spec spec-m">四川成都</span></td><td class="price"><b>11.5</b></td><td style="color:#16a34a;font-size:12px">周跌 0.1</td></tr>
  </tbody></table>
  <div class="callout" style="margin-top:10px"><b>口径提示：</b>① 本刊为<b>周报口径</b>（「周跌 0.1」相对上周基准），<b>上周绝对价原文未直给，不倒推、不补值</b>。② <b>隔期并列</b>：与看板 11-05 卡（佛山 12.1 / 湖州 11.6 / 成都 12.6）之间 11-06~11-15 该系列未采集、隔多期，<b>只列本期数值与原文箭头，不作两期比较、不推断连续走势</b>。③ 佛山 11.0 为塘口/产区口径（元/斤 1斤上），与该号日报产地均价（11-16 期 11.69）、于老师 / 小洁视频号全国区间、通威 11-13 塘口均价、强渔周报规格不同，<b>多口径并存、只能比方向、不能比绝对值</b>。④ 养护提示原文：降雨期稳水改底，够规格鱼分批出塘，<b>防小瓜虫</b>。</div>
  <div class="legend">来源：微信公众号「绿色水产技术」（渔飞鱼）2026-11-16 07:34《渔飞鱼水产 鱼虾蟹每日行情报价 2026年11月16日》· <a class="plink" href="__URL_BAOJIA__" target="_blank" rel="noopener">📄 阅读原文（渔飞鱼行情报价 11-16）</a> · 塘口/批发综合参考价</div>
</div>
""".replace("__URL_BAOJIA__", URL_BAOJIA)

CARD_SY = """
<div class="card" style="margin-top:14px">
  <h3>🛒 2026.11.16 · 无锡盛阳食品城水产批发价（元/斤）</h3>
  <div class="csub">盛阳食品城「水产类批发价（当日均价、仅供参考）」表头日期 <b>2026.11.16</b>；<b>本卡只列鳜鱼（桂鱼）/ 鲈鱼两类</b>。鳜鱼 <b>25~30</b>、鲈鱼 <b>10~14</b>，与 11.15 卡<b>逐项同值</b>、原文未标「沿用」→ <b>如实并列、不重复计数、不推断涨跌、不作两期比较</b>。</div>
  <table><thead><tr><th>品种</th><th>批发价（元/斤）</th><th>与 11.15 比较</th></tr></thead><tbody>
        <tr><td><b>鳜鱼（桂鱼）</b></td><td class="price"><b>25~30</b></td><td style="color:#6b7280;font-size:12px">同值（未标沿用）</td></tr>
        <tr><td><b>鲈鱼</b></td><td class="price"><b>10~14</b></td><td style="color:#6b7280;font-size:12px">同值（未标沿用）</td></tr>
  </tbody></table>
  <div class="callout" style="margin-top:10px"><b>口径说明：</b>销地批发「当日均价」口径（元/斤），与塘口收购价、21food 产区价、农业农村部全国批发均价（元/公斤）、视频号全国参考区间并存，<b>禁止互减</b>。本期截图另含杂货类、虾类、蟹类（公母蟹分规格）完整报价，<b>均非本看板跟踪品种，按约定不录入</b>。</div>
  <div class="legend">来源：盛阳食品城水产类批发价 2026.11.16（截图核校录入）· 元/斤 · 当日均价仅供参考</div>
</div>
"""

# chip 快览（VCSRCCHIP0001）来源列举同步；
# ⚠️ 「🤖 批发价」chip（id=4HGb9s5gzmgXv3QvdK82PP）由 refresh_freshness.py 整段重写，勿改。
CHIP_SUBS = [
    ("11-09日报/11-14日报/11-15日报）", "11-09日报/11-14日报/11-15日报/11-16日报）"),
    ("日报11-06·预报11-11）", "日报11-06·预报11-11/报价11-16）"),
    ("11.15批发）", "11.15/11.16批发）"),
]


def balance(text):
    """精确标签统计：<tag 后必须跟空白或 >，避免 <thead> 计入 <th、<body>/<br> 计入 <b。"""
    return {t: len(re.findall(r"<" + t + r"(?=[\s>])", text)) - text.count("</" + t + ">")
            for t in ("section", "div", "table", "thead", "tbody", "tr", "td", "th", "b")}


def insert_before(html, anchor, block, tag_name):
    assert html.count(anchor) == 1, ("锚点", anchor, html.count(anchor))
    idx = html.find(anchor)
    pos = html.rfind('<div class="card"', 0, idx)
    assert pos > 0, "未找到 card 开标签"
    return html[:pos] + block + html[pos:]


def main():
    html = open(HTML, encoding="utf-8").read()
    for g in GUARDS:
        if g in html:
            print("[SKIP] 本批次卡片已插入（命中", g[:30], "），退出以防重复")
            return 0

    before = balance(html)
    html = insert_before(html, ANCHOR_DAILY, CARD_DAILY + CARD_BAOJIA, "daily")
    print("[OK] 已插入 2 张新卡（渔飞鱼日报 11-16 / 鱼虾蟹报价 11-16）")
    html = insert_before(html, ANCHOR_SY, CARD_SY, "shengyang")
    print("[OK] 已插入 1 张新卡（盛阳 11.16）")

    for old, new in CHIP_SUBS:
        assert html.count(old) == 1, ("chip", old[:46], html.count(old))
        html = html.replace(old, new, 1)
    print("[OK] chip 快览 3 处来源列举同步（🤖 批发价 chip 由 refresh_freshness.py 托管，未改动）")

    after = balance(html)
    assert before == after, f"标签配平差值变化：{before} → {after}"
    for g in GUARDS:
        assert html.count(g) == 1, ("guard", g, html.count(g))
    open(HTML, "w", encoding="utf-8").write(html)
    print("[OK] 写盘完成 · 字节数", len(html.encode("utf-8")), "· 标签差值", after)
    return 0


if __name__ == "__main__":
    sys.exit(main())
