# -*- coding: utf-8 -*-
"""11-22 晚批插卡脚本（幂等）
7 张新卡：通威农牧一周鱼价行情11-20、鳜康泰11-22、绿色水产技术·渔飞鱼加州鲈播报11-22、
渔无忧在线行情预报11-20、视频号小洁11-21、视频号服务于老师11-21、盛阳11.22。
+ chip 快览多处同步。
跳过：海大11-20/腾氏㊻11-19/加州鲈36期(已合并)/养殖网加州鲈专题/科学养鱼11-20截图(OCR已录)。
弃用：双胞胎普水鱼周报44期(无鳜鲈)、通威分市场表(数值11-09/11-04已录)。
"""
import re, sys

F = "鳜鱼鲈鱼价格看板.html"
html = open(F, encoding="utf-8").read()

U_TONGWEI = "https://mp.weixin.qq.com/s/rCpArgbbahT2jsDLoDuNfw"
U_GUIKT   = "https://mp.weixin.qq.com/s/oTCNHZuCvteTdrvWT68syA"
U_LVSE    = "https://mp.weixin.qq.com/s/0D8zGXNyxfM_9Sxz_xSVOg"
U_YUWUYOU = "https://mp.weixin.qq.com/s/8VbOm-JebNRDq6iW9RRZ2Q"

# ---------------- 幂等守卫（每个 h3 专属唯一串） ----------------
GUARDS = [
    "通威农牧 · 一周鱼价行情 2026-11-20",
    "全国鳜鱼报价（2026-11-22 · 元/斤",
    "绿色水产技术 · 渔飞鱼《加州鲈每日行情播报》11-22",
    "《最新水产行情预报》（发布 11月20日",
    "🎬 11月21日 · 视频号「互联惠农小洁」",
    "🎬 11月21日 · 视频号「水产养殖服务于老师」",
    "🛒 2026.11.22 · 无锡盛阳食品城",
]
present = [g for g in GUARDS if html.count(g) >= 1]
if len(present) == len(GUARDS):
    print("[SKIP] 7 张新卡均已存在，幂等退出")
    sys.exit(0)
if present:
    raise SystemExit("[ERROR] 部分守卫已存在，拒绝半途重跑: %r" % present)


def insert_before(anchor, card, label):
    global html
    assert html.count(anchor) == 1, (label, "锚点计数", html.count(anchor))
    html = html.replace(anchor, card.strip() + "\n      " + anchor, 1)
    print("  [OK] 插入", label)


def rep(old, new, label):
    global html
    assert html.count(old) == 1, (label, "替换锚点计数", html.count(old))
    html = html.replace(old, new, 1)
    print("  [OK] chip 同步", label)


# ---------------- 1) 通威农牧 一周鱼价行情 11-20 ----------------
CARD_TONGWEI = """
<div class="card" style="margin-top:14px">
  <h3>🐟 通威农牧 · 一周鱼价行情 2026-11-20（全国塘口均价 · 鳜鱼环比 -9.2% / 加州鲈 -8.3% · 元/斤）</h3>
  <div class="csub">「通威农牧」2026-11-20 19:15 发布《草鱼跌至3.9元/斤，后市这些水产品行情或将继续走低!｜一周鱼价行情》，数据来源「通威农发市场一线行情报价组」。<b>本周全国塘口均价：鳜鱼 23.0 元/斤（环比 -9.2%、同比 -4%、周跌 2.3、去年同期 24.0、上周 25.3）、加州鲈 9.5 元/斤（环比 -8.3%、同比 -9%、周跌 0.9、去年同期 10.4、上周 10.3）</b>；原文归因「新鱼陆续上市叠加部分养户回笼资金，加大出鱼量影响」。分省：加州鲈广东 1斤上占5成 9.1、江苏 1斤 9.5（较上周跌 0.5）、浙江 1斤 9.8、四川 1斤 10.5~11；鳜鱼广东肇庆 1.3斤 23~24。<b>本卡只列鳜鱼 / 加州鲈两类</b>，同篇草鱼、鲫鱼、叉尾鮰、生鱼、黄颡鱼、牛蛙、虾蟹等按约定不录入。</div>
  <table><thead><tr><th>品种</th><th>上周</th><th>本周（元/斤）</th><th>周涨跌</th><th>同比</th><th>环比</th></tr></thead><tbody>
        <tr><td><span class="tag tag-lu">加州鲈 · 全国均价</span></td><td class="price">10.3</td><td class="price"><b>9.5</b></td><td style="color:#12a150;font-weight:600">-0.9</td><td style="color:#12a150;font-size:12px">-9%</td><td style="color:#12a150;font-size:12px">-8.3%</td></tr>
        <tr><td><span class="tag tag-gui">鳜鱼 · 全国均价</span></td><td class="price">25.3</td><td class="price"><b>23.0</b></td><td style="color:#12a150;font-weight:600">-2.3</td><td style="color:#12a150;font-size:12px">-4%</td><td style="color:#12a150;font-size:12px">-9.2%</td></tr>
  </tbody></table>
  <table style="margin-top:8px"><thead><tr><th>产区 · 规格</th><th>加州鲈（元/斤）</th><th>原文标注</th></tr></thead><tbody>
        <tr><td>广东 · 1斤上占5成</td><td class="price"><b>9.1</b></td><td style="font-size:12px">新口鱼陆续上市、供需失衡</td></tr>
        <tr><td><span class="tag tag-lu">江苏 · 1斤</span></td><td class="price"><b>9.5</b></td><td style="color:#12a150;font-size:12px">较上周下跌 0.5</td></tr>
        <tr><td>浙江 · 1斤</td><td class="price"><b>9.8</b></td><td style="font-size:12px">新鱼上市、价格持续低位</td></tr>
        <tr><td>四川 · 1斤</td><td class="price"><b>10.5~11</b></td><td style="font-size:12px">旧鱼少量 + 新口 8两以上</td></tr>
  </tbody></table>
  <div class="callout" style="margin-top:10px"><b>跨期核校 / 口径说明：</b>① 与 11-13 同号同系列周报<b>同口径（全国塘口均价，元/斤）</b>：11-13 鳜 25.3 / 鲈 10.3 与本期「上周」列<b>逐项同值</b>，本期原文逐项标注周涨跌（鳜 -2.3 / 鲈 -0.9），<b>按原文照录、不自行相减、不取区间中值互减</b>。② 同篇附图「各市场批发均价表」（鳜鱼上海江阳 50 / 仙桃 34.14、加州鲈上海江阳 15 / 湖州菱湖 11.2 等）为<b>分市场批发价（元/斤）</b>，其数值已在看板 11-09 / 11-04 通威分市场卡录入，本期作为同一批附图的<b>历史口径说明</b>，<b>不另建卡、不与全国均价互减</b>（均价 vs 分市场统计口径不同）。③ 本卡为<b>全国 / 分省塘口均价周报</b>，与塘口价（鳜康泰 11-22 江苏标鳜 24、腾氏㊻ 24.5）、分市场批发（淡水渔业 11-20 元/公斤、科学养鱼 OCR）、白沙洲批发、盛阳 25~30、视频号全国参考区间、渔无忧次日预测<b>多口径并存、禁止互减</b>。</div>
  <div class="legend">来源：微信公众号「通威农牧」2026-11-20 19:15《草鱼跌至3.9元/斤，后市这些水产品行情或将继续走低!｜一周鱼价行情》· <a class="plink" href="__U_TONGWEI__" target="_blank" rel="noopener">📄 阅读原文</a> · 元/斤 · 全国塘口均价 · 正文文字 + 附图核校录入</div>
</div>
""".replace("__U_TONGWEI__", U_TONGWEI)


# ---------------- 2) 鳜康泰 11-22 全国鳜鱼报价 ----------------
CARD_GUIKT = """
<div class="card" style="margin-top:14px">
  <h3>🐟 鳜康泰特约 · 全国鳜鱼报价（2026-11-22 · 元/斤 · 8 项 · 鳜价稳定浮动不大）</h3>
  <div class="csub">「兴渔派-鳜鱼通」2026-11-22 18:52 发布《11月22日鳜鱼价格行情!丨鳜康泰特约·全国鳜鱼报价》。原文：「<b>11月22日，鳜价保持稳定，浮动不大</b>」。规格价：<b>小鳜（0.8斤以下）19.5、标鳜（0.8~1.5斤）22.5、中鳜（1.5~2斤）19</b> 元/斤；分省标鳜：湖北 24.5、安徽 23.5、江西 25.5、湖南 24.5、江苏 24 元/斤左右。原文未给逐项涨跌说明，本卡<b>只如实并列、不推断涨跌、不作两期比较</b>。</div>
  <table><thead><tr><th>产区</th><th>规格</th><th>塘口价（元/斤）</th></tr></thead><tbody>
        <tr><td>全国</td><td>小鳜（0.8斤以下）</td><td class="price"><b>19.5</b></td></tr>
        <tr><td>全国</td><td>标鳜（0.8~1.5斤）</td><td class="price"><b>22.5</b></td></tr>
        <tr><td>全国</td><td>中鳜（1.5~2斤）</td><td class="price"><b>19</b></td></tr>
        <tr><td>湖北</td><td>标鳜</td><td class="price"><b>24.5</b></td></tr>
        <tr><td>安徽</td><td>标鳜</td><td class="price"><b>23.5</b></td></tr>
        <tr><td>江西</td><td>标鳜</td><td class="price"><b>25.5</b></td></tr>
        <tr><td>湖南</td><td>标鳜</td><td class="price"><b>24.5</b></td></tr>
        <tr><td><span class="tag tag-gui">江苏</span></td><td>标鳜（原文「24 元/斤左右」）</td><td class="price"><b>24</b></td></tr>
  </tbody></table>
  <div class="callout" style="margin-top:10px"><b>跨期核校 / 口径说明：</b>① 与 11-19 同号同系列周报<b>同市场同规格</b>：江苏标鳜 11-19 为 24、本期 24 同值，原文本期只述「鳜价稳定、浮动不大」<b>未给逐项涨跌</b>，按原文照录、<b>不自行相减、不推断逐项涨跌</b>。② 本期「全国规格价」（小鳜 19.5 / 标鳜 22.5 / 中鳜 19）与「分省标鳜」（23.5~25.5）<b>口径不同（全国 vs 分省、含规格档差异），不可直接比较、不互减</b>。③ 江苏标鳜 24 与腾氏㊻ 11-19 江苏标鳜 24.5、通威 11-20 分省鳜 23~24 <b>同值 / 近似值但各源口径不同，不互减、不互相订正</b>。④ 本卡为<b>塘口价（元/斤）</b>，与通威全国均价 23.0、分市场批发（元/公斤）、白沙洲批发、盛阳、视频号参考区间、次日预测<b>多口径并存、禁止互减</b>。</div>
  <div class="legend">来源：微信公众号「兴渔派-鳜鱼通」2026-11-22 18:52《11月22日鳜鱼价格行情!丨鳜康泰特约·全国鳜鱼报价》· <a class="plink" href="__U_GUIKT__" target="_blank" rel="noopener">📄 阅读原文</a> · 元/斤 · 塘口价 · 正文核校录入</div>
</div>
""".replace("__U_GUIKT__", U_GUIKT)


# ---------------- 3) 绿色水产技术 · 渔飞鱼加州鲈每日播报 11-22 ----------------
CARD_LVSE = """
<div class="card" style="margin-top:14px">
  <h3>🐟 绿色水产技术 · 渔飞鱼《加州鲈每日行情播报》11-22（佛山 / 湖州 / 成都 三产区 · 三规格周跌 0.1 · 元/斤）</h3>
  <div class="csub">「绿色水产技术」2026-11-22 08:48 发布《渔飞鱼水产 鱼虾蟹每日行情报价 2026年11月22日》，内含《渔飞鱼｜加州鲈每日行情播报 2026年11月22日》长图。<b>今日重点：广东佛山 1斤上 10.5、浙江湖州 10.0、四川成都 11.0 元/斤，均周跌 0.1</b>；降温期稳水改底，够规格鱼分批出塘、防小瓜虫。长图分产区三规格表（周环比列）照录于下；同篇南美白对虾 / 螃蟹 / 小龙虾 / 罗氏沼虾等非目标品种按约定不录入。</div>
  <table><thead><tr><th>产区</th><th>规格</th><th>塘口价（元/斤）</th><th>周环比</th></tr></thead><tbody>
        <tr><td rowspan="3"><span class="tag tag-lu">广东佛山</span></td><td>1斤上</td><td class="price"><b>10.5</b></td><td style="color:#12a150;font-size:12px">↓0.1</td></tr>
        <tr><td>1.5斤上</td><td class="price"><b>12.5</b></td><td style="color:#12a150;font-size:12px">↓0.1</td></tr>
        <tr><td>2斤上</td><td class="price"><b>14.5</b></td><td style="color:#12a150;font-size:12px">↓0.1</td></tr>
        <tr><td rowspan="3">浙江湖州</td><td>1斤上</td><td class="price"><b>10.0</b></td><td style="color:#12a150;font-size:12px">↓0.1</td></tr>
        <tr><td>1.5斤上</td><td class="price"><b>12.0</b></td><td style="color:#12a150;font-size:12px">↓0.1</td></tr>
        <tr><td>2斤上</td><td class="price"><b>14.0</b></td><td style="color:#12a150;font-size:12px">↓0.1</td></tr>
        <tr><td rowspan="3">四川成都</td><td>1斤上</td><td class="price"><b>11.0</b></td><td style="color:#12a150;font-size:12px">↓0.1</td></tr>
        <tr><td>1.5斤上</td><td class="price"><b>13.0</b></td><td style="color:#12a150;font-size:12px">↓0.1</td></tr>
        <tr><td>2斤上</td><td class="price"><b>15.0</b></td><td style="color:#12a150;font-size:12px">↓0.1</td></tr>
  </tbody></table>
  <div class="callout" style="margin-top:10px"><b>口径说明：</b>① 本卡为<b>塘口价播报（元/斤，原文标注周环比）</b>，与 11-16 同通道《鱼虾蟹每日行情报价》加州鲈三产区「周跌 0.1」为同系列连续期，<b>隔期并列、按原文各自照录、不作两期比较</b>。② 佛山 / 湖州 / 成都 三产区 1斤上 10.5 / 10.0 / 11.0 与通威 11-20 分省加州鲈（广东 9.1、江苏 9.5、浙江 9.8、四川 10.5~11）<b>来源与统计口径不同、时间不同，不互减</b>；原文「今日重点」为 1斤上规格，价格表含 1斤上/1.5斤上/2斤上三档，<b>不同规格档不互相比较</b>。③ 与分市场批发（元/公斤）、白沙洲批发、视频号全国参考区间、渔无忧次日预测<b>多口径并存、禁止互减</b>。</div>
  <div class="legend">来源：微信公众号「绿色水产技术」2026-11-22 08:48《渔飞鱼水产 鱼虾蟹每日行情报价 2026年11月22日》· <a class="plink" href="__U_LVSE__" target="_blank" rel="noopener">📄 阅读原文</a> · 元/斤 · 塘口价 · 正文 + 长图逐张核校录入</div>
</div>
""".replace("__U_LVSE__", U_LVSE)


# ---------------- 4) 渔无忧在线 最新水产行情预报 11-20 ----------------
CARD_YUWUYOU = """
<div class="card" style="margin-top:14px">
  <h3>预报 📅 渔无忧在线 ·《最新水产行情预报》（发布 11月20日 15:28 · 次日 11月21日 周六预测口径）</h3>
  <div class="csub">「渔无忧在线」2026-11-20 15:28 发布《最新水产行情预报》，预测 11-21（周六）口径。加州鲈专项：<b>惠农网 11/20 热门品种 11.80 元/斤，价格平稳（前一日 +2.42% 反弹后企稳）；产地通货 10.2~11 元/斤（大量上市、货源充足、走货快）、供货 12.00~14.00 元/斤；原文后市预测「价格企稳、走货较快，达规格大鱼可正常出塘，冬季冻伤风险上升、不建议压塘惜售，后市看平」</b>。本篇引用的鳜鱼等条目原文未给明确塘口价，<b>不录入、如实留空</b>。</div>
  <table><thead><tr><th>口径 · 来源</th><th>价格（元/斤）</th><th>原文标注</th></tr></thead><tbody>
        <tr><td>惠农网 11/20 热门品种（实测）</td><td class="price"><b>11.80</b></td><td style="font-size:12px">价格平稳，前一日 +2.42% 反弹后企稳</td></tr>
        <tr><td>产地通货</td><td class="price"><b>10.2~11</b></td><td style="font-size:12px">大量上市、走货快</td></tr>
        <tr><td>供货参考</td><td class="price"><b>12.00~14.00</b></td><td style="font-size:12px">供货口径</td></tr>
  </tbody></table>
  <div class="callout" style="margin-top:10px"><b>口径提示：</b>① 本卡为<b>预报号引用实测（惠农网 11/20）+ 次日（11-21）预测</b>双口径：11.80 为 11/20 实测、后市「看平 / 建议正常出塘」为原文预测结论，<b>预测价与实测成交价禁止互减、不作命中率评价</b>。② 与渔无忧 11-16 卡（11-17 次日预测）为同号隔期周报，<b>隔期并列、不作两期比较</b>。③ 与通威 11-20 全国均价 9.5、绿色水产技术 11-22 佛山 10.5、白沙洲批发、视频号区间、塘口价<b>多口径并存、禁止互减</b>。④ 本篇同列稻田蟹 / 罗氏沼虾 / 南美白对虾 / 大宗淡水鱼等非目标品种按约定不录入。</div>
  <div class="legend">来源：微信公众号「渔无忧在线」2026-11-20 15:28《最新水产行情预报》· <a class="plink" href="__U_YUWUYOU__" target="_blank" rel="noopener">📄 阅读原文</a> · 元/斤 · 实测 + 次日预测口径 · 正文核校录入</div>
</div>
""".replace("__U_YUWUYOU__", U_YUWUYOU)


# ---------------- 5) 视频号小洁 11-21 ----------------
CARD_XIAOJIE = """
<div class="card" style="margin-top:14px">
  <h3>🎬 11月21日 · 视频号「互联惠农小洁」全国参考塘口价（元/斤）</h3>
  <div class="csub">视频号「互联惠农小洁」11月21日发布「全国塘口最新鱼价出炉」，封面与描述日期一致（11月21日）。<b>鳜鱼 0.8~1.2斤 32.0~33.5 元/斤（✓ 飘红上涨区）、鲈鱼 0.8~1.2斤 12.3~13.0 元/斤（📉 弱势下跌区）</b>。原文标注「以上是参考均价，各地实际收购价有差异」，本卡按<b>全国参考区间</b>照录，不作逐条相减。</div>
  <table><thead><tr><th>品种</th><th>规格</th><th>参考价（元/斤）</th><th>原文涨跌区</th></tr></thead><tbody>
        <tr><td><span class="tag tag-gui">鳜鱼</span></td><td>0.8~1.2斤</td><td class="price"><b>32.0~33.5</b></td><td style="color:#dc2626;font-size:12px">✓ 飘红上涨区</td></tr>
        <tr><td><span class="tag tag-lu">鲈鱼</span></td><td>0.8~1.2斤</td><td class="price"><b>12.3~13.0</b></td><td style="color:#12a150;font-size:12px">📉 弱势下跌区</td></tr>
  </tbody></table>
  <div class="callout" style="margin-top:10px"><b>口径说明：</b>① 本卡为<b>视频号全国参考区间（元/斤）</b>，与 11-20 同号卡鳜 32.0~33.5 / 鲈 12.3~13.0 <b>逐项同值</b>：本期原文各自标注涨跌区（鳜飘红上涨、鲈弱势下跌），<b>同值并列、不推断涨跌、不作两期比较</b>（未标「沿用」）。② 与服务于老师 11-21 卡（鳜 21~26 / 加州鲈 9.0~10.5）同为视频号全国区间但数值不同，<b>按各自原文照录、不互减</b>。③ 与塘口价（鳜康泰 11-22 江苏 24）、全国均价（通威 23.0 / 9.5）、分市场批发、白沙洲批发、次日预测<b>多口径并存、禁止互减</b>；其他鱼种（草鱼/鲤鱼/鲫鱼/白鲢等）按约定不录入。</div>
  <div class="legend">来源：视频号「互联惠农小洁」2026-11-21 · 全国参考塘口价 · 封面与描述日期一致 · 截图核校录入</div>
</div>
"""


# ---------------- 6) 视频号服务于老师 11-21 ----------------
CARD_YULAOSHI = """
<div class="card" style="margin-top:14px">
  <h3>🎬 11月21日 · 视频号「水产养殖服务于老师」全国参考塘口价（封面 2026.11.21 · 元/斤）</h3>
  <div class="csub">视频号「水产养殖服务于老师」11月21日发布「2026.11.21 全国鱼价 · 涨跌一目了然」，封面与描述日期一致（11月21日）。<b>加州鲈 1斤上 9.0~10.5 元/斤 → 基本持平、鳜鱼 1斤上 21~26 元/斤 → 基本持平</b>。原文标注「行情仅做参考、具体以塘口现场议价为准」，本卡按<b>全国参考区间</b>照录。</div>
  <table><thead><tr><th>品种</th><th>规格</th><th>参考价（元/斤）</th><th>原文标注</th></tr></thead><tbody>
        <tr><td><span class="tag tag-gui">鳜鱼</span></td><td>1斤上</td><td class="price"><b>21~26</b></td><td style="font-size:12px">→ 基本持平</td></tr>
        <tr><td><span class="tag tag-lu">加州鲈</span></td><td>1斤上</td><td class="price"><b>9.0~10.5</b></td><td style="font-size:12px">→ 基本持平</td></tr>
  </tbody></table>
  <div class="callout" style="margin-top:10px"><b>口径说明：</b>① 本卡为<b>视频号全国参考区间（元/斤）</b>，与同号 11-20 卡（鳜 23~26 / 加州鲈 9.0~10.5）隔期并列，鳜鱼区间下限由 23 变 21、加州鲈区间同值，原文标注「基本持平」，<b>按原文照录、不推断逐项涨跌、不作两期比较</b>。② 与小洁 11-21 卡（鳜 32.0~33.5 / 鲈 12.3~13.0）同为视频号全国区间但数值不同，<b>按各自原文照录、不互减</b>。③ 与塘口价（鳜康泰 江苏 24）、全国均价（通威 23.0 / 9.5）、分市场批发、白沙洲批发、次日预测<b>多口径并存、禁止互减</b>；其他鱼种按约定不录入。</div>
  <div class="legend">来源：视频号「水产养殖服务于老师」2026-11-21 · 全国参考塘口价 · 封面与描述日期一致 · 截图核校录入</div>
</div>
"""


# ---------------- 7) 盛阳食品城 11.22 ----------------
CARD_SHENGYANG = """
<div class="card" style="margin-top:14px">
  <h3>🛒 2026.11.22 · 无锡盛阳食品城（鳜鱼 25~30 / 鲈鱼 10~14 元/斤 · 同值再录）</h3>
  <div class="csub">「盛阳食品城」水产类批发价表，日期 2026.11.22，表头「当日均价、仅供参考」。杂鱼 / 淡水鱼类批发价：<b>鳜鱼（桂鱼）25~30、鲈鱼 10~14 元/斤</b>。其他品种（白鱼、鳊鱼、草鱼、黄颡鱼等）及虾蟹、龟鳖类按约定不录入。</div>
  <table><thead><tr><th>品种</th><th>口径</th><th>批发价（元/斤）</th></tr></thead><tbody>
        <tr><td><span class="tag tag-gui">鳜鱼（桂鱼）</span></td><td>当日均价 · 仅供参考</td><td class="price"><b>25~30</b></td></tr>
        <tr><td><span class="tag tag-lu">鲈鱼</span></td><td>当日均价 · 仅供参考</td><td class="price"><b>10~14</b></td></tr>
  </tbody></table>
  <div class="callout" style="margin-top:10px"><b>口径说明：</b>① 本卡与 11-19 / 11-20 同市场卡鳜 25~30 / 鲈 10~14 <b>逐项同值</b>，为不同日期的当日报价快照，<b>同值并列、原文未给涨跌、不推断涨跌、不作两期比较</b>。② 本卡为<b>本地批发价（元/斤，当日均价）</b>，与塘口价（鳜康泰 11-22 江苏标鳜 24、腾氏㊻ 24.5）、全国均价（通威 23.0 / 9.5）、分市场批发（元/公斤）、白沙洲批发、视频号参考区间、次日预测<b>多口径并存、禁止互减</b>。</div>
  <div class="legend">来源：无锡盛阳食品城水产类批发价表 2026.11.22 · 当日均价 · 仅供参考 · 截图核校录入</div>
</div>
"""


# ================= 插入（按文档顺序，插入到各自最新同期卡之前） =================
print("=== 插卡 ===")
insert_before("🔥 10月25日 · 腾氏水产商务网一周鱼价播报", CARD_TONGWEI, "通威农牧一周鱼价 11-20")
insert_before("🐟 鳜康泰特约 · 全国鳜鱼报价（2026-11-19", CARD_GUIKT, "鳜康泰 11-22")
insert_before("预报 📅 渔无忧在线 ·《最新水产行情预报》（发布 11月16日", CARD_YUWUYOU, "渔无忧 11-20")
insert_before("🐟 渔飞鱼 ·《鱼虾蟹每日行情报价 2026年11月16日》", CARD_LVSE, "绿色水产技术加州鲈播报 11-22")
insert_before("🎬 11月20日 · 视频号「互联惠农小洁」", CARD_XIAOJIE, "视频号小洁 11-21")
insert_before("🎬 11月20日 · 视频号「水产养殖服务于老师」", CARD_YULAOSHI, "视频号服务于老师 11-21")
insert_before("🛒 2026.11.20 · 无锡盛阳食品城", CARD_SHENGYANG, "盛阳 11.22")

# ================= chip 快览同步 =================
print("=== chip 同步 ===")
rep("（10-28/10-31/11-01/11-02/11-05/11-07/11-09/11-14/11-16/11-18/11-19）",
    "（10-28/10-31/11-01/11-02/11-05/11-07/11-09/11-14/11-16/11-18/11-19/11-22）",
    "鳜康泰 11-22")
rep("（10-07~09/14/15/17/26/30/11-02/11-03/11-04/11-05/11-06/11-08/11-09/11-10/11-15/11-17/11-19/11-20）",
    "（10-07~09/14/15/17/26/30/11-02/11-03/11-04/11-05/11-06/11-08/11-09/11-10/11-15/11-17/11-19/11-20/11-21）",
    "小洁 11-21")
rep("11-17/11-19/11-20）+ 阿洁聊水产",
    "11-17/11-19/11-20/11-21）+ 阿洁聊水产",
    "于老师 11-21")
rep("/11.17/11.19/11.20批发）",
    "/11.17/11.19/11.20/11.22批发）",
    "盛阳 11.22")
rep("11-13/11-16 独立期，次日预测口径）",
    "11-13/11-16/11-20 独立期，次日预测口径）",
    "渔无忧 11-20")
rep("（11-13 塘口均价）",
    "（11-13/11-20 塘口均价）",
    "通威一周鱼价 11-20")
rep("预报11-11/报价11-16）+ 淡水渔业批发价",
    "预报11-11/报价11-16/播报11-22）+ 淡水渔业批发价",
    "渔飞鱼报价 11-22")

# ================= 标签精确配平 =================
def balance(s):
    for tag in ["div","table","thead","tbody","tr","td","th","h3","span","a","b"]:
        o = len(re.findall(r"<%s(?=[\s>])" % tag, s))
        c = len(re.findall(r"</%s>" % tag, s))
        assert o == c, ("标签不配平", tag, o, c)

balance(html)
print("  [OK] 标签精确配平通过")

open(F, "w", encoding="utf-8").write(html)
print("\n[DONE] 7 张新卡 + chip 7 处同步已写入", F)
print("HTML chars:", len(html))
