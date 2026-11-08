#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""2026-11-08 批次：5 张新卡插入 + chip 快览日期同步（幂等、单 div 插入）。

有效数据：
  1. 通威农牧 11-06 / 腾氏水产 11-07 一周鱼价（同一份数据，合并一卡双出处）
  2. 海大农牧 11-06 加州鲈四产区塘头价
  3. 鳜康泰特约 11-07 全国鳜鱼报价
  4. 视频号「互联惠农小洁」11-08
  5. 盛阳食品城 11-08 批发价
弃用：水产养殖网（强渔）11-07 鮰鱼专题（全文无鳜鱼/加州鲈价格）
重复：视频号「水产养殖服务于老师」11-06（看板已有同值卡，不新增）
"""
import re, sys

HTML = "鳜鱼鲈鱼价格看板.html"

CARD_WEEKLY = """    <div class="card" style="margin-top:14px">
      <h3>🔥 11月7日 · 通威农牧 / 腾氏水产 一周鱼价（全国塘口均价 · 元/斤 · 环比）</h3>
      <div class="csub">据「通威农牧」2026-11-06 17:12《这条鱼最高上涨0.9元/斤，凭什么逆势走强？｜一周鱼价行情》与「腾氏水产商务网」2026-11-07 15:25《最高涨2元/斤！鱼蛙蟹都涨了！生鱼短期回落，但后市仍看涨｜一周鱼价行情》，两篇正文逐项一致、数据源同标注「通威农发市场一线行情报价组」——<b>属同一期周报的两个发布渠道，本看板合并为一卡、双出处留痕，不重复计数、不作两期比较</b>。本周特水鱼普涨、普水鱼普跌：<b>加州鲈全国塘口均价 10.5 元/斤（环比 +2.4%）、鳜鱼 25 元/斤（环比 -1.3%）</b>。</div>
      <table><thead><tr><th>品种</th><th>口径</th><th>本周均价（元/斤）</th><th>环比</th><th>同比</th></tr></thead><tbody>
        <tr><td><span class="tag tag-lu">加州鲈</span></td><td>全国塘口均价</td><td class="price"><b>10.5</b></td><td style="color:#dc2626;font-size:12px">+2.4%</td><td style="color:#12a150;font-size:12px">-4%</td></tr>
        <tr><td><span class="tag tag-gui">鳜鱼</span></td><td>全国塘口均价</td><td class="price"><b>25</b></td><td style="color:#12a150;font-size:12px">-1.3%</td><td style="color:#12a150;font-size:12px">-4%</td></tr>
      </tbody></table>
      <table style="margin-top:10px"><thead><tr><th>品种</th><th>产区 / 规格</th><th>塘口价（元/斤）</th><th>原文变动</th></tr></thead><tbody>
        <tr><td><span class="tag tag-lu">加州鲈</span></td><td>广东 · 1斤上占7成</td><td class="price">10.5</td><td style="color:#6b7280;font-size:12px">市场流通稳定、价格稳定</td></tr>
        <tr><td><span class="tag tag-lu">加州鲈</span></td><td>江苏 · 新口6.5两左右（部分8两）</td><td class="price">原文未标绝对价</td><td style="color:#dc2626;font-size:12px">较上周 +0.5 元/斤</td></tr>
        <tr><td><span class="tag tag-lu">加州鲈</span></td><td>浙江 · 1斤</td><td class="price">10</td><td style="color:#6b7280;font-size:12px">基本平稳</td></tr>
        <tr><td><span class="tag tag-lu">加州鲈</span></td><td>四川 · 9两 / 1斤</td><td class="price">11</td><td style="color:#6b7280;font-size:12px">稳定</td></tr>
        <tr><td><span class="tag tag-gui">鳜鱼</span></td><td>广东肇庆 · 1.3斤（新口）</td><td class="price">23</td><td style="color:#12a150;font-size:12px">较上周 -1 元</td></tr>
        <tr><td><span class="tag tag-gui">鳜鱼</span></td><td>湖北 · 1斤以上（新鱼）</td><td class="price">26</td><td style="color:#6b7280;font-size:12px">稳定</td></tr>
      </tbody></table>
      <div class="callout" style="margin-top:10px"><b>口径提示：</b>「全国塘口均价」为周报环比口径（相对上周基准），「分产区」为当地当周塘口报价，两者与视频号 0.8-1.2 斤通货区间、鳜康泰标鳜、盛阳销地批发、MOA 元/公斤批发价<b>规格、时间、渠道三重不同，多口径并存、禁止互减</b>；江苏一栏原文只给涨幅未给绝对价，按原文如实留空，不做推算。鳜鱼均价环比 -1.3%、加州鲈 +2.4% 与 11-07 鳜康泰标鳜 24、海大湖州标鱼 10.6 方向不悖，但绝对值不可横比。</div>
      <div class="legend">来源：微信公众号「通威农牧」2026-11-06 17:12《这条鱼最高上涨0.9元/斤，凭什么逆势走强？｜一周鱼价行情》· <a class="plink" href="https://mp.weixin.qq.com/s/uBczfDLKjM7mlruM6EPZHQ" target="_blank" rel="noopener">📄 阅读原文（通威 11-06）</a>；「腾氏水产商务网」2026-11-07 15:25《最高涨2元/斤！…｜一周鱼价行情》· <a class="plink" href="https://mp.weixin.qq.com/s/rOe8Bj-z2Nr5rAaWY8cEFA" target="_blank" rel="noopener">📄 阅读原文（腾氏 11-07）</a> · 数据源：通威农发市场一线行情报价组 · 元/斤 · 报价仅供参考，具体鱼价以当地为准</div>
    </div>
"""

CARD_HAINONG = """    <div class="card" style="margin-top:14px">
      <h3>🐟 11月6日 · 海大农牧 水产一线「全球最新塘头价」：加州鲈四产区（元/斤）</h3>
      <div class="csub">据「海大农牧 水产一线」2026-11-06 17:33（广东）《鱼价行情 | 最高涨2块！年底扎堆出鱼，有人降价却没车拉……11月6日全球最新塘头价》：全国鱼价行情<b>每周五更新</b>。本期加州鲈覆盖浙 / 闽 / 豫 / 鄂四产区，<b>标鱼集中在 10.5~11.3 元/斤</b>；广东珠海一段只述品相压价与秋鱼集中上市，<b>无数字报价，按原文留空不录入</b>。本篇未涉及鳜鱼。</div>
      <table><thead><tr><th>产区</th><th>规格 / 口径</th><th>塘头价（元/斤）</th><th>原文要点</th></tr></thead><tbody>
        <tr><td>浙江湖州</td><td>塘口发价（原文单位 元/两）</td><td class="price">1~1.1 元/两</td><td style="font-size:12px">新口早苗批量上市、鱼价整体维稳</td></tr>
        <tr><td>浙江湖州</td><td>平打 1.1 斤以上标鱼</td><td class="price"><b>10.6 左右</b></td><td style="font-size:12px">同段另报大统货 9.5~10</td></tr>
        <tr><td>福建龙岩</td><td>8两~1.3斤</td><td class="price"><b>10.5~11</b></td><td style="font-size:12px">平 1.4 斤及以上 11.5 元/斤</td></tr>
        <tr><td>河南</td><td>1.3斤以上</td><td class="price"><b>11.3</b></td><td style="font-size:12px">统货 10.5；短暂上涨后回落</td></tr>
        <tr><td>湖北武汉</td><td>9两起、平 1.2 斤以上</td><td class="price"><b>最高 10.5</b></td><td style="font-size:12px">流通量不大，市场仍以 10 块鱼为主</td></tr>
        <tr><td>广东珠海</td><td>秋鱼集中上市</td><td class="price">原文未标数字</td><td style="font-size:12px">烂身/出血/伤口会被压价扣损耗，品相决定到手价</td></tr>
      </tbody></table>
      <div class="callout" style="margin-top:10px"><b>口径提示：</b>① 湖州的「塘口发价 1~1.1 元/两」与「标鱼 10.6 元/斤」<b>单位与货品口径均不同，禁止直接互减或换算比较</b>；标鱼 / 统货 / 平打规格价差属正常，看板按原文分列。② 本卡为<b>塘头发价</b>，与通威/腾氏周报<b>全国塘口均价 10.5</b>、视频号小洁 0.8-1.2 斤通货 12.6~13.9、盛阳销地批发 10~14 属不同渠道口径，多口径并存、禁止互减。③ 原文自述「价格及行情可能因区域、规格、品质和时间不同而产生差异，仅供参考」。</div>
      <div class="legend">来源：微信公众号「海大农牧 水产一线」2026-11-06 17:33《鱼价行情 | 最高涨2块！年底扎堆出鱼，有人降价却没车拉……11月6日全球最新塘头价》· <a class="plink" href="https://mp.weixin.qq.com/s/hahDNe9PAOsgsHTpDqM1Kw" target="_blank" rel="noopener">📄 阅读原文（海大 11-06）</a> · 元/斤（湖州发价行保留原文元/两）· 每周五更新</div>
    </div>
"""

CARD_GUIKANGTAI = """    <div class="card" style="margin-top:14px">
      <h3>🐟 鳜康泰特约 · 全国鳜鱼报价（2026-11-07 · 元/斤 · 8 项 · 原文自述稳定）</h3>
      <div class="csub">据「兴渔派-鳜鱼通」2026-11-07 20:35（广东）《11月7日鳜鱼价格行情丨鳜康泰特约·全国鳜鱼报价》：原文一句话结论为<b>「11月7日，鳜鱼价格保持稳定」</b>。<b>标鳜（0.8-1.5斤）24 元/斤左右、小鳜 19、中鳜 21.5</b>；分省标鳜江西 25.5 领跑，湖北/安徽 24.5、湖南 25、江苏 25。</div>
      <table><thead><tr><th>品种 / 产区</th><th>规格</th><th>报价（元/斤）</th></tr></thead><tbody>
        <tr><td><span class="tag tag-gui">广东</span> 小鳜</td><td><span class="spec spec-s">0.8斤以下</span></td><td class="price"><b>19 左右</b></td></tr>
        <tr><td><span class="tag tag-gui">广东</span> 标鳜</td><td><span class="spec spec-s">0.8-1.5斤</span></td><td class="price"><b>24 左右</b></td></tr>
        <tr><td><span class="tag tag-gui">广东</span> 中鳜</td><td><span class="spec spec-m">1.5-2斤</span></td><td class="price"><b>21.5 左右</b></td></tr>
        <tr><td><span class="tag tag-gui">湖北</span> 标鳜</td><td><span class="spec spec-s">标鳜</span></td><td class="price">24.5 左右</td></tr>
        <tr><td><span class="tag tag-gui">安徽</span> 标鳜</td><td><span class="spec spec-s">标鳜</span></td><td class="price">24.5 左右</td></tr>
        <tr><td><span class="tag tag-gui">江西</span> 标鳜</td><td><span class="spec spec-s">标鳜</span></td><td class="price">25.5 左右</td></tr>
        <tr><td><span class="tag tag-gui">湖南</span> 标鳜</td><td><span class="spec spec-s">标鳜</span></td><td class="price">25 左右</td></tr>
        <tr><td><span class="tag tag-gui">江苏</span> 标鳜</td><td><span class="spec spec-s">标鳜</span></td><td class="price">25 左右</td></tr>
      </tbody></table>
      <div class="callout" style="margin-top:10px"><b>口径提示：</b>① 原文自述「价格保持稳定」，但本看板 11-05 同号卡记录的中鳜 22、安徽 25、江苏 26 与本期 21.5 / 24.5 / 25 有小幅差异——<b>原文未给涨跌说明与基准，按多口径并存如实并列，不据此推断趋势、不做互减</b>；以原文结论为准。② 本卡为塘口/批发参考价（元/斤），与 MOA 批发中位数（元/公斤）、视频号 0.8-1.2 斤通货区间 32.0~33.5、盛阳销地批发 25~30 规格渠道不同，<b>禁止互减</b>；③ 原文注明「仅供参考，请以实际交易价为准」。</div>
      <div class="legend">来源：微信公众号「兴渔派-鳜鱼通」2026-11-07 20:35《11月7日鳜鱼价格行情丨鳜康泰特约·全国鳜鱼报价》· <a class="plink" href="https://mp.weixin.qq.com/s/tsvYI116fpv4KFlKK5MpBw" target="_blank" rel="noopener">📄 阅读原文（11-07）</a> · 元/斤</div>
    </div>
"""

CARD_XIAOJIE = """    <div class="card" style="margin-top:14px">
      <h3>🎬 11月8日 · 视频号「互联惠农小洁」全国参考塘口价（元/斤）</h3>
      <div class="csub">据视频号「互联惠农小洁」2026-11-08《11月8日全国最新塘口鱼价出炉！涨跌博弈持续！出鱼前务必看清这波行情！》：本期 8 品种 5 涨 3 跌，<b>本看板只跟踪鳜鱼 / 鲈鱼两类</b>（其余 6 品种不录入）。<b>鳜鱼（0.8-1.2斤）32.0~33.5 元/斤 ↑</b>、<b>鲈鱼（0.8-1.2斤）12.6~13.9 元/斤 ↓</b>。</div>
      <table><thead><tr><th>品种</th><th>规格</th><th>11-08 报价（元/斤）</th><th>原始标注</th><th>较 11-06（同号中值）</th></tr></thead><tbody>
        <tr><td><span class="tag tag-gui">鳜鱼</span></td><td><span class="spec spec-m">0.8-1.2斤</span></td><td class="price"><b>32.0~33.5</b></td><td style="color:#dc2626;font-size:12px">↑ 涨</td><td style="color:#dc2626;font-size:12px">32.25 → 32.75（↑0.5，同向）</td></tr>
        <tr><td><span class="tag tag-lu">鲈鱼</span></td><td><span class="spec spec-m">0.8-1.2斤</span></td><td class="price"><b>12.6~13.9</b></td><td style="color:#12a150;font-size:12px">↓ 跌</td><td style="color:#12a150;font-size:12px">13.5 → 13.25（↓0.25，同向）</td></tr>
      </tbody></table>
      <div class="callout" style="margin-top:10px"><b>口径提示：</b>① 中值对比仅在该号<b>同一口径</b>内做逐期参照（11-06 为 31.5~33.0 / 12.8~14.2），本期原始箭头与中值方向一致，区别于该号 10-30 / 11-02 出现的「箭头基准非上期末」现象；② 0.8-1.2 斤通货区间与于老师 1 斤上（10.0-11.5）、鳜康泰标鳜 0.8-1.5 斤（24）、通威/腾氏全国均价（10.5 / 25）、盛阳批发 25~30 为<b>不同规格与渠道口径，多口径并存、禁止互减</b>，看方向不看绝对值；③ 视频原文核心提醒照录：「好鱼才能卖好价！同品种下，规格大小和皮毛（活力、体色）好坏，差价极大！出鱼前务必做好打样评估，别让好鱼贱卖了！」</div>
      <div class="legend">来源：微信视频号「互联惠农小洁」2026-11-08《11月8日全国最新塘口鱼价出炉！涨跌博弈持续！出鱼前务必看清这波行情！》（截图核校录入）· 报价只是全国塘口参考价，各地有差价，仅供参考</div>
    </div>
"""

CARD_SHENGYANG = """    <div class="card" style="margin-top:14px">
      <h3>🛒 2026.11.8 · 无锡盛阳食品城水产批发价（元/斤）</h3>
      <div class="csub">无锡盛阳食品城水产类批发价（当日均价、仅供参考）。<b>鳜鱼（桂鱼）25~30、鲈鱼 10~14</b>——与 11-06 同值，鳜鱼延续 25~30 横盘、鲈鱼 10~14 持平。离宜兴官林最近的销地批发口径之一。</div>
      <table><thead><tr><th>品种</th><th>当日均价（元/斤）</th><th>较 11-06</th></tr></thead><tbody>
        <tr><td><b>鳜鱼（桂鱼）</b></td><td class="price"><b>25~30</b></td><td style="color:#6b7280;font-size:12px">持平（延续横盘）</td></tr>
        <tr><td><b>鲈鱼</b></td><td class="price"><b>10~14</b></td><td style="color:#6b7280;font-size:12px">持平</td></tr>
      </tbody></table>
      <div class="callout" style="margin-top:10px"><b>口径说明：</b>销地批发「当日均价」口径（元/斤），与塘口收购价、农业农村部全国批发均价（元/公斤）、视频号全国参考区间并存，<b>禁止互减</b>。本期截图另含杂货类（黄鳝/甲鱼/牛蛙/黑鱼等）、虾类（河虾/基围虾/罗氏虾）、蟹类（公母蟹分规格）完整报价，<b>均非本看板跟踪品种，按约定不录入</b>，仅截图存档。</div>
      <div class="legend">来源：盛阳食品城水产类批发价 2026.11.8（截图核校录入）· 元/斤 · 当日均价仅供参考</div>
    </div>
"""

# (锚点 h3 文本片段, 新卡)
INSERTS = [
    ("🔥 通威农牧 · 一周鱼价（腾氏水产商务网转载", CARD_WEEKLY),
    ("🐟 鳜康泰特约 · 全国鳜鱼报价（2026-11-05", CARD_GUIKANGTAI),
    ("🐟 海大农牧 · 鱼价观察 11月2日", CARD_HAINONG),
    ("🎬 11月6日 · 视频号「互联惠农小洁」", CARD_XIAOJIE),
    ("🛒 2026.11.6 · 无锡盛阳食品城", CARD_SHENGYANG),
]

# chip 快览日期同步（精确串替换，幂等）
CHIP_SUBS = [
    ("视频号·小洁（10-07~09/14/15/17/26/30/11-02/11-03/11-04/11-05/11-06）",
     "视频号·小洁（10-07~09/14/15/17/26/30/11-02/11-03/11-04/11-05/11-06/11-08）"),
    ("鳜康泰特约（10-28/10-31/11-01/11-02/11-05）",
     "鳜康泰特约（10-28/10-31/11-01/11-02/11-05/11-07）"),
    ("海大农牧 塘头聚焦（11-02 广东加州鲈）",
     "海大农牧 塘头聚焦（11-02 广东加州鲈 / 11-06 四产区塘头价）"),
    ("盛阳食品城（10.27/10.28/10.30/11.2/11.3/11.4/11.5/11.6批发）",
     "盛阳食品城（10.27/10.28/10.30/11.2/11.3/11.4/11.5/11.6/11.8批发）"),
    ("腾氏一周鱼价播报（10-25）",
     "腾氏一周鱼价播报（10-25 / 11-07 通威同源周报）"),
]


def balance(text):
    # 用「精确标签」统计：<thead> 不能被 <th 命中，<body>/<br> 不能被 <b 命中
    tags = ("section", "div", "table", "tbody", "tr", "td", "th", "b")
    return {t: len(re.findall(r"<" + t + r"(?=[\s>])", text)) - text.count("</" + t + ">")
            for t in tags}


def main():
    html = open(HTML, encoding="utf-8").read()
    before = balance(html)

    # 防止重跑重复插入
    if "11月7日 · 通威农牧 / 腾氏 一周鱼价" in html:
        print("[SKIP] 已插入过本批次卡片，退出以防重复")
        return 0

    for anchor, card in INSERTS:
        hits = [m.start() for m in re.finditer(re.escape(anchor), html)]
        assert len(hits) == 1, "锚点不唯一: %s -> %d" % (anchor, len(hits))
        card_start = html.rfind('<div class="card"', 0, hits[0])
        assert card_start > 0 and hits[0] - card_start < 200, "卡片起点定位异常: " + anchor
        assert card.count("<div") == card.count("</div>"), "新卡 div 不配平: " + anchor
        html = html[:card_start] + card + "\n" + html[card_start:]
        print("[OK] 插入:", anchor[:34])

    for old, new in CHIP_SUBS:
        assert html.count(old) == 1, "chip 替换串不唯一: " + old[:40]
        html = html.replace(old, new, 1)
        print("[OK] chip:", old[:34])

    after = balance(html)
    assert before == after, "标签配平差值变化: %s -> %s" % (before, after)
    print("[OK] 标签配平差值一致:", after)

    open(HTML, "w", encoding="utf-8").write(html)
    print("[OK] 写入", HTML, "字节数", len(html.encode("utf-8")))
    return 0


if __name__ == "__main__":
    sys.exit(main())
