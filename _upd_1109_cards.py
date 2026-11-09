#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""2026-11-09 批次：5 张新卡插入 + chip 快览日期同步（幂等、单 div 插入）。

有效数据：
  1. 全国渔业价格 11-09《渔飞鱼水产行情日报》（加州鲈佛山 15.00 为 11/7 沿用，非当日新价）
  2. 淡水渔业 11-06 批发价（鳜鱼/加州鲈各 8 条，元/公斤）
  3. 江苏凌家塘 11-07 一周行情 11/1~11/7（桂鱼约 30 / 鲈鱼约 12）
  4. 视频号「水产养殖服务于老师」11-09
  5. 视频号「互联惠农小洁」11-09
重复弃用：鳜康泰特约 11-07（tsvYI116...）上一批已录入，不新增。
"""
import re, sys

HTML = "鳜鱼鲈鱼价格看板.html"

CARD_MINJIAN = """    <div class="card" style="margin-top:14px">
      <h3>📰 全国渔业价格 ·《渔飞鱼水产行情日报 2026-11-09》（发布 11-09 07:47 · 阿冷今夜到、出鱼窗口关闭）</h3>
      <div class="csub">据「全国渔业价格」2026-11-09 07:47（河南）：明日 21 品种<b>「普水反弹、特水止涨」</b>——草鱼白沙洲 9.40 元/公斤（4.70 元/斤）▲+3.3% 反弹、黄鳝 64.00 元/公斤（32.0 元/斤）▼-1.5% 止涨回落、鲫鱼 16.00 元/公斤（8.00 元/斤）▼-1.2%、大黄鱼批发 19.15 元/斤 ▼-1.64%。<b>本看板只跟踪鳜鱼 / 加州鲈两类</b>：本期<b>加州鲈佛山 15.00 元/斤（11/7 沿用）</b>，<b>鳜鱼本期正文未给报价，如实留空</b>。天气：冷空气 8 日夜到、9 日降温 5~9℃，11/10 早晨粤北及珠三角北部仅 8~12℃，原文建议<b>不安排大宗出鱼、先稳水保鱼</b>，等 11/11 回暖再恢复出鱼节奏。</div>
      <table><thead><tr><th>品种 / 产区</th><th>规格 / 口径</th><th>价格（元/斤）</th><th>原文标注</th></tr></thead><tbody>
        <tr><td><span class="tag tag-lu">加州鲈</span> 广东佛山</td><td>塘头供货</td><td class="price"><b>15.00</b></td><td style="color:#6b7280;font-size:12px">佛山 15（11/7 沿用）</td></tr>
        <tr><td><span class="tag tag-gui">鳜鱼</span></td><td>—</td><td class="price">原文未给报价</td><td style="color:#6b7280;font-size:12px">本期 21 品种表中无鳜鱼条目</td></tr>
      </tbody></table>
      <div class="callout" style="margin-top:10px"><b>口径提示：</b>① 15.00 为<b>11/7 沿用值、非 11-09 当日新采价</b>，与本看板 11-06 早报卡「加州鲈 广东佛山 通货供货 15.00（11/5 惠农）」同值同口径，<b>不重复计数、不据此推断涨跌</b>；② 「塘头供货 / 通货供货」为<b>供货报价、非成交均价</b>，与于老师 1 斤上塘口 10.0-11.5、通威/腾氏全国塘口均价 10.5、凌家塘批发约 12 <b>规格与渠道三重不同，多口径并存、禁止互减</b>；③ 原文标题含「渔飞鱼水产行情日报」但发布公众号为「全国渔业价格」，本卡按<b>发布公众号</b>归入全国渔业价格日报源，与看板「渔飞鱼」系列（另一账号）分开计数。</div>
      <div class="legend">来源：微信公众号「全国渔业价格」2026-11-09 07:47《渔飞鱼水产行情日报（2026年11月9日）阿冷今夜到！黄鳝止涨·草鱼反弹明天别急着出鱼》· <a class="plink" href="https://mp.weixin.qq.com/s/ss0avnvWo36ETl6TezMtfQ" target="_blank" rel="noopener">📄 阅读原文（11-09 日报）</a> · 元/斤 · 报价仅供参考</div>
    </div>
"""

CARD_DANSHUI = """    <div class="card">
      <h3>🌊 淡水渔业公众号 全国水产品批发价（分市场 · 2026-11-06）</h3>
      <div class="csub">来源：公众号文章（WebFetch 直接提取，非图片，可信度高）；报价日期 <b>2026-11-06</b>（11-06 16:47 发布）；单位<b>元/公斤</b>（÷2 ≈ 元/斤）。本卡只列跟踪品种 <b>鳜鱼（桂花鱼）、加州鲈</b> 完整明细（各 8 条），同篇黄颡鱼/黄鳝/乌鳢/泥鳅/斑点叉尾鮰按约定不录入。<b style="color:#dc2626">本期鳜鱼最高：上海江杨 500≤条重&lt;750g 100 元/公斤（50 元/斤）</b>；加州鲈 8 条集中在 21.20~30.00 元/公斤。</div>
      <div class="grid2"><div><h3 style="font-size:14px;margin:6px 0 8px"><span class="tag tag-gui">鳜鱼（桂花鱼）</span> 批发价（元/公斤）</h3><table><thead><tr><th>市场</th><th>规格</th><th>价格</th></tr></thead><tbody>
        <tr><td>上海江杨水产品批发市场经营管理有限公司</td><td><span class="spec spec-s">500≤条重&lt;750</span></td><td class="price"><b style="color:#dc2626">100.00</b></td></tr>
        <tr><td>福州名成水产品市场有限公司</td><td><span class="spec spec-s">条重≥750g</span></td><td class="price">75.00</td></tr>
        <tr><td>北京大红门京深海鲜批发市场有限公司</td><td><span class="spec spec-s">条重≥750g</span></td><td class="price">72.00</td></tr>
        <tr><td>江西省萍乡市城南水产批发市场</td><td><span class="spec spec-s">250≤条重&lt;500</span></td><td class="price">68.00</td></tr>
        <tr><td>中国供销上饶农产品交易城</td><td><span class="spec spec-s">500≤条重&lt;750</span></td><td class="price">62.00</td></tr>
        <tr><td>南京市众彩批发市场有限公司</td><td><span class="spec spec-s">500≤条重&lt;750</span></td><td class="price">54.00</td></tr>
        <tr><td>北京京丰岳各庄农副产品批发市场中心</td><td><span class="spec spec-s">500≤条重&lt;750</span></td><td class="price">54.00</td></tr>
        <tr><td>广州黄沙水产交易市场有限公司</td><td><span class="spec spec-s">条重≥750g</span></td><td class="price">52.00</td></tr>
      </tbody></table></div><div><h3 style="font-size:14px;margin:6px 0 8px"><span class="tag tag-lu">加州鲈</span> 批发价（元/公斤）</h3><table><thead><tr><th>市场</th><th>规格</th><th>价格</th></tr></thead><tbody>
        <tr><td>上海江杨水产品批发市场经营管理有限公司</td><td><span class="spec spec-s">条重&gt;500</span></td><td class="price"><b>30.00</b></td></tr>
        <tr><td>湖北中和农产品大市场有限责任公司</td><td><span class="spec spec-s">条重&gt;500</span></td><td class="price">26.00</td></tr>
        <tr><td>中国供销上饶农产品交易城</td><td><span class="spec spec-s">条重&gt;500</span></td><td class="price">26.00</td></tr>
        <tr><td>广州黄沙水产交易市场有限公司</td><td><span class="spec spec-s">条重&gt;500</span></td><td class="price">26.00</td></tr>
        <tr><td>江西省萍乡市城南水产批发市场</td><td><span class="spec spec-s">条重&gt;500</span></td><td class="price">26.00</td></tr>
        <tr><td>两湖绿谷淡水鱼市场</td><td><span class="spec spec-s">条重&gt;500</span></td><td class="price">24.30</td></tr>
        <tr><td>湖州菱湖乌板桥水产品批发市场</td><td><span class="spec spec-s">条重&gt;500</span></td><td class="price">22.60</td></tr>
        <tr><td>湖州菱湖乌板桥水产品批发市场</td><td><span class="spec spec-s">条重&lt;500</span></td><td class="price">21.20</td></tr>
      </tbody></table></div></div>
      <div class="callout" style="margin-top:12px"><b>跨期核校（11-06 vs 11-02，仅同市场同规格 8 项可比）：</b>① 6 项持平——上饶鳜鱼 500-750g 62.00→62.00、上饶加州鲈 &gt;500g 26.00→26.00、广州黄沙加州鲈 26.00→26.00、两湖绿谷加州鲈 24.30→24.30、湖州菱湖乌板桥加州鲈 &gt;500g 22.60→22.60 / &lt;500g 21.20→21.20；② 2 项鳜鱼下行——广州黄沙 ≥750g 54.00→52.00、福州名成 ≥750g 93.00→75.00，<b>原文未给涨跌说明，按原文如实并列、不推断趋势</b>；③ 两期样本轮换大（11-02 的太原五龙口/南昌/马王堆/苏州南环桥/上海江阳退出，11-06 新增北京大红门/萍乡城南/南京众彩/京丰岳各庄/湖北中和/上海江杨），<b>「上海江阳」与「上海江杨」为原文不同市场名，不作同点比较</b>，其余轮换样本不可逐条相减。<br><b>口径提示：</b>本卡为<b>批发市场端</b>价格（元/公斤），与塘口价、视频号全国参考区间、供货报价口径不同，<b>多口径并存、禁止互减</b>；批发端含销区溢价，扣运费及损耗后不构成跨区调运套利空间。</div>
      <div class="legend">来源：微信公众号「淡水渔业」2026-11-06 16:47《11月6日黄颡鱼、鳜鱼、加州鲈、黄鳝、乌鳢、泥鳅、斑点叉尾鮰批发价格》· <a class="plink" href="https://mp.weixin.qq.com/s/lFLAP-vlbxhyK1yXFEqu3g" target="_blank" rel="noopener">📄 阅读原文（淡水渔业 11-06）</a> · 元/公斤（÷2 ≈ 元/斤）</div>
    </div>
"""

CARD_LINGJIATANG = """    <div class="card" style="margin-top:14px">
      <h3>🏪 江苏凌家塘市场 · 一周价格行情（2026/11/1~11/7 · 水产摘录）</h3>
      <div class="csub">常州凌家塘市场官方公众号周报（离宜兴最近的大型批发市场之一），2026-11-07 15:17 发布，统计区间 11/1~11/7。本周货源充足、运行平稳，<b>特种水产「上市增加，价格稳定」：桂鱼（鳜鱼）约 30 元/斤、鲈鱼约 12、昂公约 13</b>；淡水鱼「销量回落、价格下行」：鲫鱼约 8、草鱼约 7、鳊鱼约 7；虾蟹类供应充足、价格平稳（河虾约 60、基围虾约 20、罗氏虾约 30、公蟹 3/4/5 两约 30/45/50）。<b>本卡按跟踪范围只列鳜鱼 / 鲈鱼两行，其余品种不录入</b>。</div>
      <table><thead><tr><th>品种</th><th>本周价（元/斤）</th><th>较上期（10/25~10/31）</th><th>原文走势</th></tr></thead><tbody>
        <tr><td><span class="tag tag-gui">鳜鱼（桂鱼）</span></td><td class="price"><b>约 30</b></td><td style="color:#6b7280;font-size:12px">约 30 → 约 30（持平）</td><td style="font-size:12px">上市增加、价格稳定</td></tr>
        <tr><td><span class="tag tag-lu">鲈鱼</span></td><td class="price"><b>约 12</b></td><td style="color:#6b7280;font-size:12px">约 12 → 约 12（持平）</td><td style="font-size:12px">上市增加、价格稳定</td></tr>
      </tbody></table>
      <div class="callout" style="margin-top:10px"><b>口径提示：</b>① 周报为<b>「约数」口径、未分规格</b>，趋势参考为主，不能与分规格塘口/批发报价逐点相减；② 与上期同为 30 / 12，原文结论由「走量放缓、价格下跌」转为「上市增加、价格稳定」，<b>按原文表述照录，不据此推断绝对价变化</b>；③ 桂鱼约 30 与盛阳 11-08 销地批发 25~30 上限吻合、鲈鱼约 12 落在盛阳 10~14 区间内，但两者渠道不同；与鳜康泰标鳜 24、小洁 0.8-1.2 斤通货 32.2~33.8、于老师 1 斤上 22-26.5 <b>规格、时间、渠道三重不同，多口径并存、禁止互减</b>；④ 本期虾蟹为公蟹分规格、上期为母蟹分规格，<b>不跨期比较</b>。</div>
      <div class="legend">来源：微信公众号「江苏凌家塘市场」2026-11-07 15:17《江苏凌家塘市场一周价格行情（2026/11/1~2026/11/7）》· <a class="plink" href="https://mp.weixin.qq.com/s/FFFq9tvKUHwv4FfYZyDyQQ" target="_blank" rel="noopener">📄 阅读原文（凌家塘周报 11-07）</a> · 周报约数口径，未分规格，仅供参考</div>
    </div>
"""

CARD_YULAOSHI = """    <div class="card" style="margin-top:14px">
      <h3>🎬 11月9日 · 视频号「水产养殖服务于老师」全国参考塘口价（元/斤）</h3>
      <div class="csub">据视频号「水产养殖服务于老师」2026-11-09《2026.11.09全国鱼价 涨跌一目了然》：14 品种<b>基本持平</b>，仅鲤鱼、白鲢「持续低迷」。<b>本看板只跟踪鳜鱼 / 加州鲈两类</b>（其余 12 品种不录入）。<b>鳜鱼 1 斤上：22-26.5 元/斤（原文标注基本持平）</b>、<b>加州鲈 1 斤上：10.0-11.5 元/斤（连续六期不变）</b>。行情仅做参考，具体以塘口现场议价为准。</div>
      <table><thead><tr><th>品种</th><th>规格</th><th>11-09 报价（元/斤）</th><th>原始标注</th><th>较 11-06（同号）</th></tr></thead><tbody>
        <tr><td><span class="tag tag-gui">鳜鱼</span></td><td>1 斤上</td><td class="price"><b>22-26.5</b></td><td style="color:#6b7280;font-size:12px">基本持平</td><td style="color:#6b7280;font-size:12px">22-25 → 上限 +1.5（区间放大）</td></tr>
        <tr><td><span class="tag tag-lu">加州鲈</span></td><td>1 斤上</td><td class="price"><b>10.0-11.5</b></td><td style="color:#6b7280;font-size:12px">基本持平</td><td style="color:#6b7280;font-size:12px">10.0-11.5 → 六期不变</td></tr>
      </tbody></table>
      <div class="callout" style="margin-top:10px"><b>口径提示：</b>① 鳜鱼区间上限由 11-06 的 22-25 放大至 22-26.5，但<b>原文仍标注「基本持平」，按原文照录、不推断趋势</b>；该号 11-05 为 22-26、11-06 收窄至 22-25，区间宽度本身随产区报价浮动。② 该号「1 斤上」全国参考塘口区间与小洁 0.8-1.2 斤通货（32.2~33.8 / 12.5~13.8）、鳜康泰标鳜 0.8-1.5 斤 24、通威/腾氏全国均价 25 / 10.5、凌家塘批发约 30 / 12、盛阳销地批发 25~30 / 10~14 <b>规格与渠道不同，多口径并存、禁止互减</b>，只看方向不看绝对值。③ 原文底部提示照录：「行情仅做参考 具体以塘口现场议价为准」。</div>
      <div class="legend">来源：微信视频号「水产养殖服务于老师」2026-11-09《2026.11.09全国鱼价》（截图核校录入）· 元/斤 · 行情仅做参考，具体以塘口现场议价为准</div>
    </div>
"""

CARD_XIAOJIE = """    <div class="card" style="margin-top:14px">
      <h3>🎬 11月9日 · 视频号「互联惠农小洁」全国参考塘口价（元/斤）</h3>
      <div class="csub">据视频号「互联惠农小洁」2026-11-09《11月9日全国最新塘口鱼价出炉！涨跌博弈持续！出鱼前务必看清这波行情！》：本期 8 品种 5 涨 3 跌，<b>本看板只跟踪鳜鱼 / 鲈鱼两类</b>（其余 6 品种不录入）。<b>鳜鱼（0.8-1.2斤）32.2~33.8 元/斤 ↑</b>、<b>鲈鱼（0.8-1.2斤）12.5~13.8 元/斤 ↓</b>。</div>
      <table><thead><tr><th>品种</th><th>规格</th><th>11-09 报价（元/斤）</th><th>原始标注</th><th>较 11-08（同号中值）</th></tr></thead><tbody>
        <tr><td><span class="tag tag-gui">鳜鱼</span></td><td><span class="spec spec-m">0.8-1.2斤</span></td><td class="price"><b>32.2~33.8</b></td><td style="color:#dc2626;font-size:12px">↑ 涨</td><td style="color:#dc2626;font-size:12px">32.75 → 33.00（↑0.25，同向）</td></tr>
        <tr><td><span class="tag tag-lu">鲈鱼</span></td><td><span class="spec spec-m">0.8-1.2斤</span></td><td class="price"><b>12.5~13.8</b></td><td style="color:#12a150;font-size:12px">↓ 跌</td><td style="color:#12a150;font-size:12px">13.25 → 13.15（↓0.10，同向）</td></tr>
      </tbody></table>
      <div class="callout" style="margin-top:10px"><b>口径提示：</b>① 中值对比仅在该号<b>同一口径</b>内做逐期参照（11-08 为 32.0~33.5 / 12.6~13.9），本期原始箭头与中值方向一致；② 0.8-1.2 斤通货区间与于老师 11-09 的 1 斤上（22-26.5 / 10.0-11.5）、鳜康泰标鳜 24、凌家塘批发约 30 / 12、盛阳销地批发 25~30 / 10~14 为<b>不同规格与渠道口径，多口径并存、禁止互减</b>，看方向不看绝对值；③ 视频原文核心提醒照录：「好鱼才能卖好价！同品种下，规格大小和皮毛（活力、体色）好坏，差价极大！出鱼前务必做好打样评估，别让好鱼贱卖了！」</div>
      <div class="legend">来源：微信视频号「互联惠农小洁」2026-11-09《11月9日全国最新塘口鱼价出炉！涨跌博弈持续！出鱼前务必看清这波行情！》（截图核校录入）· 报价只是全国塘口参考价，各地有差价，仅供参考</div>
    </div>
"""

# (锚点 h3 文本片段, 新卡)
INSERTS = [
    ("🌊 淡水渔业公众号 全国水产品批发价（分市场 · 2026-11-02", CARD_DANSHUI),
    ("🏪 江苏凌家塘市场 · 一周价格行情（2026/10/25~10/31", CARD_LINGJIATANG),
    ("📰 全国渔业价格 ·《全国水产品行情早报 2026-11-06》", CARD_MINJIAN),
    ("🎬 11月8日 · 视频号「互联惠农小洁」", CARD_XIAOJIE),
    ("🎬 11月6日 · 视频号「水产养殖服务于老师」", CARD_YULAOSHI),
]

# chip 快览日期同步（精确串替换，幂等）
CHIP_SUBS = [
    ("11-04早报/11-06早报）+ 渔飞鱼日报",
     "11-04早报/11-06早报/11-09日报）+ 渔飞鱼日报"),
    ("淡水渔业批发价（10-21/10-23/10-27/10-29/11-02）",
     "淡水渔业批发价（10-21/10-23/10-27/10-29/11-02/11-06）"),
    ("凌家塘一周行情（10-25~31）",
     "凌家塘一周行情（10-25~31 / 11-01~07）"),
    ("11-05/11-06/11-08）+ 老段",
     "11-05/11-06/11-08/11-09）+ 老段"),
    ("11-03/11-04/11-05/11-06）+ 阿洁聊水产",
     "11-03/11-04/11-05/11-06/11-09）+ 阿洁聊水产"),
]


def balance(text):
    # 精确标签统计：<thead> 不能被 <th 命中，<body>/<br> 不能被 <b 命中
    tags = ("section", "div", "table", "tbody", "tr", "td", "th", "b")
    return {t: len(re.findall(r"<" + t + r"(?=[\s>])", text)) - text.count("</" + t + ">")
            for t in tags}


def main():
    html = open(HTML, encoding="utf-8").read()
    before = balance(html)

    # 幂等守卫串与卡内实际 h3 逐字一致
    if "🎬 11月9日 · 视频号「互联惠农小洁」全国参考塘口价（元/斤）" in html:
        print("[SKIP] 已插入过本批次卡片，退出以防重复")
        return 0

    for anchor, card in INSERTS:
        hits = [m.start() for m in re.finditer(re.escape(anchor), html)]
        assert len(hits) == 1, "锚点不唯一: %s -> %d" % (anchor, len(hits))
        card_start = html.rfind('<div class="card"', 0, hits[0])
        assert card_start > 0 and hits[0] - card_start < 200, "卡片起点定位异常: " + anchor
        assert card.count("<div") == card.count("</div>"), "新卡 div 不配平: " + anchor
        html = html[:card_start] + card + "\n" + html[card_start:]
        print("[OK] 插入:", anchor[:38])

    for old, new in CHIP_SUBS:
        assert html.count(old) == 1, "chip 替换串不唯一: %s -> %d" % (old[:40], html.count(old))
        html = html.replace(old, new, 1)
        print("[OK] chip:", old[:38])

    after = balance(html)
    assert before == after, "标签配平差值变化: %s -> %s" % (before, after)
    print("[OK] 标签配平差值一致:", after)

    open(HTML, "w", encoding="utf-8").write(html)
    print("[OK] 写入", HTML, "字节数", len(html.encode("utf-8")))
    return 0


if __name__ == "__main__":
    sys.exit(main())
