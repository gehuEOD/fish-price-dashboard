# -*- coding: utf-8 -*-
"""11-20 晚批插卡脚本（幂等）
8 张卡/注：腾氏㊻11-19、淡水渔业11-20、海大11-20、鳜康泰11-19、
盛阳11.20、小洁11-20、于老师11-20、45期卡同源合并双出处注。
+ chip 快览 10 处同步。
"""
import re, sys

F = "鳜鱼鲈鱼价格看板.html"
html = open(F, encoding="utf-8").read()

U_TENGSHI = "https://mp.weixin.qq.com/s/NvvrBkQ2L9uDMaE4bgmC0w"
U_DANSHUI = "https://mp.weixin.qq.com/s/SHmMgeuq3aqhmIyxZQvpPg"
U_HAIDA   = "https://mp.weixin.qq.com/s/uN4NVOPqeZOE9nVKXhA0yA"
U_GUIKT   = "https://mp.weixin.qq.com/s/i2m3zpZ5A3BCI2ipX3ua_A"
U_QY36    = "https://mp.weixin.qq.com/s/uYwWgedj_YvbOeJnO8K76g"

# ---------------- 幂等守卫（每个 h3 / 追加段的专属唯一串） ----------------
GUARDS = [
    "海南卓越联合播报㊻ · 广东 3~5 成中鳜",
    "🌊 2026-11-20 · 淡水渔业 分市场批发价",
    "「全球最新塘头价」：鳜鱼佛山 3 点 + 加州鲈多产区",
    "全国鳜鱼报价（2026-11-19 · 元/斤 · 8 项",
    "🛒 2026.11.20 · 无锡盛阳食品城",
    "🎬 11月20日 · 视频号「互联惠农小洁」",
    "🎬 11月20日 · 视频号「水产养殖服务于老师」",
    "同源合并·双出处",
]
present = [g for g in GUARDS if html.count(g) >= 1]
if len(present) == len(GUARDS):
    print("[SKIP] 8 张卡/注均已存在，幂等退出")
    sys.exit(0)
if present:
    raise SystemExit("[ERROR] 部分守卫已存在，拒绝半途重跑: %r" % present)

# ---------------- 1) 腾氏 海南卓越联合播报㊻ 11-19 ----------------
CARD_TENGSHI = """
<div class="card" style="margin-top:14px">
  <h3>🐟 腾氏水产 · 鳜鱼塘头价（2026-11-19 · 海南卓越联合播报㊻ · 广东 3~5 成中鳜 / 湖南标鳜周跌 0.5、其余持平）</h3>
  <div class="csub">据「腾氏水产商务网」2026-11-19 17:28（郑思桃）《微跌0.5元/斤！病害压力缓解，鳜鱼价格为何还是涨不动？｜海南卓越联合播报㊻》：过去一周鳜鱼稳中有跌，<b>广东 3~5 成中鳜再跌 0.5 元/斤、湖南标鳜跟跌 0.5 元/斤，湖北 / 江苏 / 广西标鳜与上周持平</b>。附图《各地区鳜鱼塘头价》为 <b>11.11 → 11.18 双日期对照 + 涨跌列（9 行）</b>，<b>按发布期 11-19 归档、表格数据基准 11.18 写明</b>。降温后病害压力缓解、病鱼减少，养殖户心态分化（惜售观望 vs 资金周转被迫出鱼）；原文判断短期价位可稳住到月底，<b>后市研判不录入价格数据</b>。</div>
  <table><thead><tr><th>产区 / 规格</th><th>11.11 塘口价（元/斤）</th><th>11.18 塘口价（元/斤）</th><th>周涨跌（原文）</th></tr></thead><tbody>
        <tr><td>广东 1成中鳜、2成小鳜（鱼仔鳜）</td><td class="price">23</td><td class="price"><b>23</b></td><td style="color:#64748b;font-size:12px">→ 持平</td></tr>
        <tr><td>广东 1成中鳜、1成小鳜（鱼仔鳜）</td><td class="price">23.5</td><td class="price"><b>23.5</b></td><td style="color:#64748b;font-size:12px">→ 持平</td></tr>
        <tr><td>广东 1成小鳜、2成中鳜</td><td class="price">23</td><td class="price"><b>23</b></td><td style="color:#64748b;font-size:12px">→ 持平</td></tr>
        <tr><td>广东 3成中鳜（鱼仔鳜）</td><td class="price">22.5</td><td class="price"><b>22</b></td><td style="color:#16a34a;font-size:12px">↓0.5</td></tr>
        <tr><td>广东 4~5成中鳜（鱼仔鳜）</td><td class="price">21.5</td><td class="price"><b>21</b></td><td style="color:#16a34a;font-size:12px">↓0.5</td></tr>
        <tr><td>湖北 标鳜</td><td class="price">25</td><td class="price"><b>25</b></td><td style="color:#64748b;font-size:12px">→ 持平</td></tr>
        <tr><td><span class="tag tag-gui">江苏</span> 标鳜</td><td class="price">24.5</td><td class="price"><b>24.5</b></td><td style="color:#64748b;font-size:12px">→ 持平（蟹塘清塘集中出鱼，供应承压）</td></tr>
        <tr><td>广西 标鳜</td><td class="price">26</td><td class="price"><b>26</b></td><td style="color:#64748b;font-size:12px">→ 持平</td></tr>
        <tr><td>湖南 标鳜</td><td class="price">24.5~25</td><td class="price"><b>24.5</b></td><td style="color:#16a34a;font-size:12px">↓0.5</td></tr>
  </tbody></table>
  <div class="callout" style="margin-top:12px"><b>跨期核校 / 口径说明：</b>① 与 11-12「㊺」同号同系列连续周报、<b>同市场同规格</b>：㊺ 卡当期值（23 / 23.5 / 23 / 22.5 / 21.5、湖北 25、江苏 24.5、湖南 24.5~25、广西 26）与本期 <b>11.11 对照列逐项同值</b>，本期原文逐项标注周涨跌（3 成 / 4~5 成中鳜、湖南标鳜各 ↓0.5，其余持平），<b>按原文照录，不自行相减、不取区间中值互减</b>。② 正文文字段「1成中鳜、1成小鳜（鱼仔鳜）26 元/斤、较上周涨 2.5」与<b>附图对照表同规格 23.5→23.5 持平不一致</b>，<b>按原文两处各自照录、不互相订正、不推断统一涨跌</b>，主表以附图正式报价表为准。③ 广东按鱼仔鳜成数分档报价，与「标鳜 0.8~1.5 斤」规格口径不同，<b>不可直接对比</b>。④ 江苏标鳜 24.5 与鳜康泰 11-19（24.5）、渔有福 11-16（24.5）同值但各源涨跌口径不同，<b>不互减、不互相订正</b>。⑤ 本卡为<b>周报塘头价（元/斤，周环比）</b>，与日报塘口报价、科学养鱼 / 淡水渔业分市场批发（元/公斤）、白沙洲批发 30.25、盛阳 25~30、视频号全国参考区间、渔无忧次日预测<b>多口径并存、禁止互减</b>。附图另 14 张为广告 / 分隔 / 二维码图，逐张核校后弃用。</div>
  <div class="legend">来源：微信公众号「腾氏水产商务网」2026-11-19 17:28《微跌0.5元/斤！病害压力缓解，鳜鱼价格为何还是涨不动？｜海南卓越联合播报㊻》· <a class="plink" href="__U_TENGSHI__" target="_blank" rel="noopener">📄 阅读原文（播报㊻）</a> · 元/斤 · 塘头价 · 正文文字 + 附图逐张核校录入</div>
</div>

""".replace("__U_TENGSHI__", U_TENGSHI)

# ---------------- 2) 淡水渔业 11-20 分市场批发价 ----------------
CARD_DANSHUI = """
<div class="card" style="margin-top:14px">
  <h3>🌊 2026-11-20 · 淡水渔业 分市场批发价（鳜鱼 8 市场 + 加州鲈 8 市场 · 元/公斤）</h3>
  <div class="csub">「淡水渔业」2026-11-20 16:55 发布《11月20日黄颡鱼、鳜鱼、加州鲈、黄鳝、乌鳢、泥鳅、斑点叉尾鮰批发价格》，正文文字表格汇总全国多地主流市场当日报价。<b>鳜鱼 8 市场：乌鲁木齐北园春 120.00 最高、云南华潮 100.00（≥750g）、上海江阳 71.00、安徽合肥周谷堆 65.00（250~500g）、南昌 56.00、江苏凌家塘 54.00、长沙马王堆 53.00、武汉白沙洲 47.50（250~500g）</b>；<b>加州鲈 ≥500g：上海江杨 30.00 最高、广州黄沙 / 萍乡城南 26.00、上饶 25.00、两湖绿谷 23.90、湖州菱湖 23.00（&lt;500g 20.40）、上海江阳 22.00</b>。黄颡 / 黄鳝 / 乌鳢 / 泥鳅 / 鮰鱼等非目标品种按约定不录入。</div>
  <table><thead><tr><th>鳜鱼 市场</th><th>规格（条重 g）</th><th>11-20 批发价</th><th>备注</th></tr></thead><tbody>
        <tr><td><span class="tag tag-gui">乌鲁木齐北园春</span></td><td><span class="spec spec-s">500~750</span></td><td class="price"><b>120.00 元/公斤</b></td><td style="font-size:12px">本表最高 · 远端销区照录（跨区价差须过滤）</td></tr>
        <tr><td><span class="tag tag-gui">云南华潮</span></td><td><span class="spec spec-s">≥750</span></td><td class="price"><b>100.00 元/公斤</b></td><td style="font-size:12px">—</td></tr>
        <tr><td><span class="tag tag-gui">上海江阳</span></td><td><span class="spec spec-s">500~750</span></td><td class="price"><b>71.00 元/公斤</b></td><td style="font-size:12px">—</td></tr>
        <tr><td><span class="tag tag-gui">安徽合肥周谷堆</span></td><td><span class="spec spec-s">250~500</span></td><td class="price"><b>65.00 元/公斤</b></td><td style="font-size:12px">—</td></tr>
        <tr><td><span class="tag tag-gui">江西南昌</span></td><td><span class="spec spec-s">500~750</span></td><td class="price"><b>56.00 元/公斤</b></td><td style="font-size:12px">—</td></tr>
        <tr><td><span class="tag tag-gui">江苏凌家塘</span></td><td><span class="spec spec-s">500~750</span></td><td class="price"><b>54.00 元/公斤</b></td><td style="font-size:12px">江苏本地销区口径</td></tr>
        <tr><td><span class="tag tag-gui">长沙马王堆</span></td><td><span class="spec spec-s">500~750</span></td><td class="price"><b>53.00 元/公斤</b></td><td style="font-size:12px">—</td></tr>
        <tr><td><span class="tag tag-gui">武汉白沙洲</span></td><td><span class="spec spec-s">250~500</span></td><td class="price"><b>47.50 元/公斤</b></td><td style="font-size:12px">—</td></tr>
  </tbody></table>
  <table style="margin-top:8px"><thead><tr><th>加州鲈 市场</th><th>规格</th><th>11-20 批发价</th><th>备注</th></tr></thead><tbody>
        <tr><td><span class="tag tag-lu">上海江杨</span></td><td><span class="spec spec-s">≥500g</span></td><td class="price"><b>30.00 元/公斤</b></td><td style="font-size:12px">本表最高 · 销区口径</td></tr>
        <tr><td><span class="tag tag-lu">广州黄沙</span></td><td><span class="spec spec-s">≥500g</span></td><td class="price"><b>26.00 元/公斤</b></td><td style="font-size:12px">—</td></tr>
        <tr><td><span class="tag tag-lu">江西萍乡城南</span></td><td><span class="spec spec-s">≥500g</span></td><td class="price"><b>26.00 元/公斤</b></td><td style="font-size:12px">—</td></tr>
        <tr><td><span class="tag tag-lu">中国供销上饶</span></td><td><span class="spec spec-s">≥500g</span></td><td class="price"><b>25.00 元/公斤</b></td><td style="font-size:12px">—</td></tr>
        <tr><td><span class="tag tag-lu">两湖绿谷</span></td><td><span class="spec spec-s">≥500g</span></td><td class="price"><b>23.90 元/公斤</b></td><td style="font-size:12px">—</td></tr>
        <tr><td><span class="tag tag-lu">湖州菱湖乌板桥</span></td><td><span class="spec spec-s">≥500g</span></td><td class="price"><b>23.00 元/公斤</b></td><td style="font-size:12px">同市场 &lt;500g 另报 20.40</td></tr>
        <tr><td><span class="tag tag-lu">湖州菱湖乌板桥</span></td><td><span class="spec spec-s">&lt;500g</span></td><td class="price"><b>20.40 元/公斤</b></td><td style="font-size:12px">规格价差，不与 ≥500g 行互减</td></tr>
        <tr><td><span class="tag tag-lu">上海江阳</span></td><td><span class="spec spec-s">≥500g</span></td><td class="price"><b>22.00 元/公斤</b></td><td style="font-size:12px">与「上海江杨」近似市场名不同，不作同点比较</td></tr>
  </tbody></table>
  <div class="callout" style="margin-top:10px"><b>同源 / 多口径说明：</b>① 本卡 6 条鳜鱼（上海江阳 71.00、乌鲁木齐 120.00、云南华潮 100.00、江苏凌家塘 54.00、合肥周谷堆 65.00、白沙洲 47.50）与<b>科学养鱼 App 11-20 截图（OCR 通道）逐项同值</b>，判为同一份全国批发价数据的两个采集通道，<b>分源登记、同值并列、不重复计数、不推断涨跌</b>；该截图另含团头鲂 / 泥鳅行，非目标品种不录。② 市场名近似但不同（上海江阳 vs 上海江杨）、公蟹 vs 母蟹、不同规格档（250~500 vs 500~750 vs ≥750）<b>均不作同点比较、不逐条相减</b>；原文未给涨跌列，<b>不推断涨跌</b>。③ 本卡为<b>分市场批发价（元/公斤）</b>，与塘口价（鳜康泰 11-19 江苏标鳜 24.5 元/斤、腾氏㊻ 24.5 元/斤）、白沙洲日报 30.25 元/斤、盛阳 25~30 元/斤、视频号全国参考区间、次日预测<b>多口径并存、禁止互减</b>；跨区价差须过滤乌鲁木齐 / 云南等远端销区。</div>
  <div class="legend">来源：微信公众号「淡水渔业」2026-11-20 16:55《11月20日黄颡鱼、鳜鱼、加州鲈、黄鳝、乌鳢、泥鳅、斑点叉尾鮰批发价格》· <a class="plink" href="__U_DANSHUI__" target="_blank" rel="noopener">📄 阅读原文</a> · 元/公斤 · 正文文字表格核校录入</div>
</div>

""".replace("__U_DANSHUI__", U_DANSHUI)

# ---------------- 3) 海大农牧 11-20 全球最新塘头价 ----------------
CARD_HAIDA = """
<div class="card" style="margin-top:14px">
  <h3>🐟 11月20日 · 海大农牧 水产一线「全球最新塘头价」：鳜鱼佛山 3 点 + 加州鲈多产区（元/斤）</h3>
  <div class="csub">据「海大农牧」2026-11-20 17:43《鱼价行情 | 有涨！多条鱼价格抬升，有人仍惜售等再涨！11月20日全球最新塘头价》：全国鱼价行情<b>每周五更新</b>，「以下数据及行情分析仅供参考」。正文「主要特种鱼」文字段仅列黄颡鱼 / 加州鲈 / 鮰鱼、<b>未列鳜鱼</b>；但附图长表逐张核校后<b>含《鳜鱼（元/斤）》报价表（佛山 3 点）与《加州鲈（元/斤）》报价表（多产区 11.13 → 11.20 双日期对照 + 周涨跌 + 去年同期 + 同比）</b>，按红线「公众号正文图片必须逐张下载核校」补录。主表按原文照录 11.13 / 11.20 两列与周涨跌，<b>去年同期 / 同比为衍生指标不录入</b>。</div>
  <table><thead><tr><th>鳜鱼 产区 / 规格</th><th>11.13 塘头价</th><th>11.20 塘头价</th><th>周涨跌</th></tr></thead><tbody>
        <tr><td>广东 佛山乐从 0.8~1.5斤</td><td class="price">23</td><td class="price"><b>22.5</b></td><td style="color:#16a34a;font-size:12px">↓0.5</td></tr>
        <tr><td>广东 佛山高明 0.8~1.5斤</td><td class="price">23.5</td><td class="price"><b>22.5</b></td><td style="color:#16a34a;font-size:12px">↓1</td></tr>
        <tr><td>广东 佛山南海 0.8~1斤</td><td class="price">23</td><td class="price"><b>22.5</b></td><td style="color:#16a34a;font-size:12px">↓0.5</td></tr>
  </tbody></table>
  <table style="margin-top:8px"><thead><tr><th>加州鲈 产区</th><th>规格</th><th>11.13</th><th>11.20</th><th>周涨跌</th></tr></thead><tbody>
        <tr><td>广东 南海九江</td><td><span class="spec spec-s">1斤上</span></td><td class="price">10.3</td><td class="price"><b>10.3</b></td><td style="color:#64748b;font-size:12px">→</td></tr>
        <tr><td>广东 珠海金湾</td><td><span class="spec spec-s">1斤</span></td><td class="price">—</td><td class="price"><b>8.8</b></td><td style="color:#64748b;font-size:12px">上期未给，不倒推</td></tr>
        <tr><td>广东 珠海金湾</td><td><span class="spec spec-s">1.3斤</span></td><td class="price">—</td><td class="price"><b>9.1</b></td><td style="color:#64748b;font-size:12px">上期未给，不倒推</td></tr>
        <tr><td>福建 漳州</td><td><span class="spec spec-s">0.8~1.5斤</span></td><td class="price">11.3</td><td class="price"><b>10.8</b></td><td style="color:#16a34a;font-size:12px">↓0.5</td></tr>
        <tr><td>福建 龙岩上杭</td><td><span class="spec spec-s">8两以上</span></td><td class="price">11</td><td class="price"><b>11</b></td><td style="color:#64748b;font-size:12px">→</td></tr>
        <tr><td>福建 龙岩连城</td><td><span class="spec spec-s">9两以上</span></td><td class="price">10</td><td class="price"><b>10</b></td><td style="color:#64748b;font-size:12px">→</td></tr>
        <tr><td>两湖 湖南钱粮湖</td><td><span class="spec spec-s">8两起</span></td><td class="price">10</td><td class="price"><b>10</b></td><td style="color:#64748b;font-size:12px">→</td></tr>
        <tr><td>湖北 武汉白沙洲</td><td><span class="spec spec-s">9两起</span></td><td class="price">10</td><td class="price"><b>10</b></td><td style="color:#64748b;font-size:12px">→</td></tr>
        <tr><td>河南 郑州</td><td><span class="spec spec-s">1斤起</span></td><td class="price">10.5</td><td class="price"><b>10.5</b></td><td style="color:#64748b;font-size:12px">→</td></tr>
        <tr><td>四川 成都邛崃</td><td><span class="spec spec-s">9两起</span></td><td class="price">10</td><td class="price"><b>11</b></td><td style="color:#dc2626;font-size:12px">↑1</td></tr>
        <tr><td>四川 成都邛崃</td><td><span class="spec spec-s">1斤</span></td><td class="price">11</td><td class="price"><b>11</b></td><td style="color:#64748b;font-size:12px">→</td></tr>
        <tr><td>四川 眉山东坡</td><td><span class="spec spec-s">9两起</span></td><td class="price">10</td><td class="price"><b>11</b></td><td style="color:#dc2626;font-size:12px">↑1</td></tr>
        <tr><td>江浙 浙江湖州</td><td><span class="spec spec-s">8两起</span></td><td class="price">10.5</td><td class="price"><b>10</b></td><td style="color:#16a34a;font-size:12px">↓0.5</td></tr>
        <tr><td>江浙 浙江湖州</td><td><span class="spec spec-s">统货</span></td><td class="price">9.8</td><td class="price"><b>9</b></td><td style="color:#16a34a;font-size:12px">↓0.8</td></tr>
  </tbody></table>
  <div class="callout" style="margin-top:12px"><b>口径说明：</b>① <b>同一篇文章内正文文字段与附图长表口径不同，按原文各自照录、不互减、不互相订正</b>：文字段加州鲈「浙江湖州平打 9 两~1 斤统货 8.8-9.3 元/斤、河南 1 斤起挑 1.3 斤以上 10.5-10.8 元/斤、湖北武汉平 1.1 斤以上统货 9.5 / 大鱼 1.4 斤以上 10.5」为塘口发价 / 统货区间描述；附表为分规格 11.13→11.20 塘头价对照，两者<b>规格 · 时间 · 渠道均不同，只看方向不看绝对值</b>。② 珠海金湾 11.13 列原文为空（「—」），<b>如实留空、不倒推涨跌</b>。③ 与 11-13 该号同系列四产区卡、11-17 同值并入强渔周报卡<b>产区与规格不完全对应，不作逐点比较、不推断涨跌</b>；本卡为<b>周报塘头价（元/斤，周环比）</b>，与鳜康泰 11-19 塘口报价、腾氏㊻ 周报、加州鲈周报 45 / 36 期、白沙洲批发、盛阳本地批发、视频号全国参考区间、次日预测<b>多口径并存、禁止互减</b>。④ 同为附图的草鱼 / 鲫鱼 / 罗非鱼 / 鲤鱼 / 黄颡鱼 / 鮰鱼 / 泥鳅 / 海鲈 / 金鲳 / 石斑 / 牛蛙 / 甲鱼 / 鳗鱼及海外鱼价表均非本看板跟踪品种，按约定不录入。</div>
  <div class="legend">来源：微信公众号「海大农牧」2026-11-20 17:43《鱼价行情 | 有涨！多条鱼价格抬升，有人仍惜售等再涨！11月20日全球最新塘头价》· <a class="plink" href="__U_HAIDA__" target="_blank" rel="noopener">📄 阅读原文（海大农牧 11-20）</a> · 元/斤 · 每周五更新，仅供参考 · 正文文字 + 4 张长图逐段核校录入</div>
</div>

""".replace("__U_HAIDA__", U_HAIDA)

# ---------------- 4) 鳜康泰 11-19 ----------------
CARD_GUIKT = """
<div class="card" style="margin-top:14px">
  <h3>🐟 鳜康泰特约 · 全国鳜鱼报价（2026-11-19 · 元/斤 · 8 项 · 广东标鳜 / 中鳜日跌 0.5、湖南周跌 0.5）</h3>
  <div class="csub">据「兴渔派-鳜鱼通」2026-11-19 18:27《广东鳜价跌！11月19日鳜鱼价格行情!丨鳜康泰特约·全国鳜鱼报价》：正文文字给出 8 项塘口报价；附图《全国鳜鱼行情》为 <b>11.18 → 11.19 → 11.13 三日期对照表</b>，含<b>日涨跌（vs 11/18）与周涨跌（vs 11/13）两列</b>。本期 <b>广东标鳜 23→22.5、中鳜 20→19.5 两档日环比各 ↓0.5</b>，其余 6 产区日持平；<b>湖南标鳜对 11/13 周跌 0.5，广东标鳜 / 中鳜周跌 1</b>。主表第 3 列固定为本期价，三日期对照绝对值在下方 callout 列明。附图另 3 张为广告 / 动保产品图，逐张核校后弃用。</div>
  <table><thead><tr><th>品种 / 产区</th><th>规格</th><th>11-19 塘口价（元/斤）</th><th>日涨跌（vs 11/18）</th><th>周涨跌（vs 11/13）</th></tr></thead><tbody>
        <tr><td><span class="tag tag-gui">广东</span> 小鳜</td><td><span class="spec spec-s">0.8 斤以下</span></td><td class="price"><b>19</b></td><td style="font-size:12px">—</td><td style="color:#64748b;font-size:12px">—</td></tr>
        <tr><td><span class="tag tag-gui">广东</span> 标鳜</td><td><span class="spec spec-s">0.8~1.5 斤</span></td><td class="price"><b>22.5</b></td><td style="color:#16a34a;font-size:12px">↓0.5</td><td style="color:#16a34a;font-size:12px">↓1</td></tr>
        <tr><td><span class="tag tag-gui">广东</span> 中鳜</td><td><span class="spec spec-s">1.5 斤以上</span></td><td class="price"><b>19.5</b></td><td style="color:#16a34a;font-size:12px">↓0.5</td><td style="color:#16a34a;font-size:12px">↓1</td></tr>
        <tr><td><span class="tag tag-gui">湖北</span> 标鳜</td><td><span class="spec spec-s">标鳜</span></td><td class="price"><b>24</b></td><td style="font-size:12px">—</td><td style="color:#64748b;font-size:12px">—</td></tr>
        <tr><td><span class="tag tag-gui">安徽</span> 标鳜</td><td><span class="spec spec-s">标鳜</span></td><td class="price"><b>24</b></td><td style="font-size:12px">—</td><td style="color:#64748b;font-size:12px">—</td></tr>
        <tr><td><span class="tag tag-gui">江西</span> 标鳜</td><td><span class="spec spec-s">标鳜</span></td><td class="price"><b>25.5</b></td><td style="font-size:12px">—</td><td style="color:#64748b;font-size:12px">—</td></tr>
        <tr><td><span class="tag tag-gui">湖南</span> 标鳜</td><td><span class="spec spec-s">标鳜</span></td><td class="price"><b>24.5</b></td><td style="font-size:12px">—</td><td style="color:#16a34a;font-size:12px">↓0.5</td></tr>
        <tr><td><span class="tag tag-gui">江苏</span> 标鳜</td><td><span class="spec spec-s">标鳜</span></td><td class="price"><b>24.5</b></td><td style="font-size:12px">—</td><td style="color:#64748b;font-size:12px">—（11/13 亦 24.5）</td></tr>
  </tbody></table>
  <div class="callout" style="margin-top:12px"><b>同值并列 / 多口径说明：</b>① 附图三日期对照绝对值：广东小鳜 19 / 19 / 19、标鳜 23 / 22.5 / 23.5、中鳜 20 / 19.5 / 20.5、湖北 24 / 24 / 24、安徽 24 / 24 / 24、江西 25.5 / 25.5 / 25.5、湖南 24.5 / 24.5 / 25、江苏 24.5 / 24.5 / 24.5（依次为 11/18、11/19、11/13）。<b>本期按原文给出的日 / 周涨跌列照录，不自行相减、不取区间中值互减</b>。② 与 11-18 卡（同号同系列连续期、同市场同规格）对照：小鳜 19、湖北 24、安徽 24、江西 25.5、湖南 24.5、江苏 24.5 逐项同值，广东标鳜 23→22.5、中鳜 20→19.5 为本期新变动；<b>同值项如实并列、不重复计数、不作两期比较</b>。③ 江苏标鳜 24.5 在腾氏㊻ 11-18 / 11.11 双列（持平）、海大 11-20 佛山口径、渔有福 11-16 卡中<b>规格 · 时间 · 涨跌口径各不相同，不互减、不互相订正、不推断统一涨跌</b>。④ 塘口报价（元/斤）与白沙洲批发 30.25、分市场批发（元/公斤）、盛阳 25~30、视频号全国区间 32.0~33.5 / 23-26<b>多口径并存、禁止互减</b>。</div>
  <div class="legend">来源：微信公众号「兴渔派-鳜鱼通」2026-11-19 18:27《广东鳜价跌！11月19日鳜鱼价格行情!丨鳜康泰特约·全国鳜鱼报价》· <a class="plink" href="__U_GUIKT__" target="_blank" rel="noopener">📄 阅读原文</a> · 元/斤 · 塘口报价 · 正文文字 + 附图逐张核校录入（图 3 为正式报价表）</div>
</div>

""".replace("__U_GUIKT__", U_GUIKT)

# ---------------- 5) 盛阳 11.20 ----------------
CARD_SHENGYANG = """
<div class="card" style="margin-top:14px">
  <h3>🛒 2026.11.20 · 无锡盛阳食品城 水产类批发价（鳜鱼 / 鲈鱼）</h3>
  <div class="csub">用户提交「盛阳食品城」2026.11.20 水产类批发价表格截图（表头「当日均价、仅供参考」）：<b>鳜鱼（桂鱼）25~30 元/斤、鲈鱼 10~14 元/斤</b>，与 11.15 / 11.16 / 11.17 / 11.19 四期卡<b>逐项同值</b>，五期连续同区间、<b>原文未标「沿用」，如实并列照录、不推断涨跌、不重复计数</b>。其余水产行按约定不录入。</div>
  <table><thead><tr><th>品种</th><th>口径</th><th>11.20 批发价</th><th>备注</th></tr></thead><tbody>
        <tr><td><span class="tag tag-gui">鳜鱼</span>（桂鱼）</td><td><span class="spec spec-s">无锡盛阳 · 批发</span></td><td class="price"><b>25~30 元/斤</b></td><td style="font-size:12px">与 11.15 / 11.16 / 11.17 / 11.19 同值五连并列，未标沿用</td></tr>
        <tr><td><span class="tag tag-lu">鲈鱼</span></td><td><span class="spec spec-s">无锡盛阳 · 批发</span></td><td class="price"><b>10~14 元/斤</b></td><td style="font-size:12px">与 11.15 / 11.16 / 11.17 / 11.19 同值五连并列，未标沿用</td></tr>
  </tbody></table>
  <div class="callout" style="margin-top:10px"><b>口径说明：</b>① 本卡为<b>无锡本地销区批发价（元/斤）</b>，离宜兴官林最近的本地批发锚点；与塘口价（鳜康泰 11-19 江苏标鳜 24.5）、白沙洲批发（30.25 / 9.90 折算）、加州鲈周报 45 期江苏 9.5-10.5、淡水渔业分市场批发（元/公斤）<b>多口径并存、禁止互减</b>。② 五日连续同值且原文未标「沿用」，<b>同值并列、不推断涨跌、不重复计数</b>。③ 区间宽（鳜鱼 25~30 跨 5 元）为该市场统货口径，未给规格细分，照录。</div>
  <div class="legend">来源：「盛阳食品城」2026.11.20 水产类批发价表格（当日均价、仅供参考）· 📷 用户截图核校录入 · 元/斤 · 本地批发参考价</div>
</div>

"""

# ---------------- 6) 小洁 11-20 视频号 ----------------
CARD_XIAOJIE = """
<div class="card" style="margin-top:14px">
  <h3>🎬 11月20日 · 视频号「互联惠农小洁」全国参考塘口价（元/斤）</h3>
  <div class="csub">用户提交视频号截图：封面「<b>11月20日！全国塘口最新鱼价！</b>」与底部描述「#11月20日鱼价」<b>日期一致，按 11-20 归期</b>。原文分「📈 飘红上涨区」与「📉 弱势下跌区」两栏：本看板仅录<b>鳜鱼 0.8~1.2 斤 32.0~33.5（飘红上涨区 ✓）</b>与<b>鲈鱼 0.8~1.2 斤 12.3~13.0（弱势下跌区 📉）</b>；草鱼 / 鲤鱼 / 鮰鱼 / 白鲢 / 鲫鱼 / 黑鱼 / 罗非鱼等非目标品种按约定不录入。原文「把你本地真实塘口收购价打在评论区，同行互相参考」，属全国参考区间口径。</div>
  <table><thead><tr><th>品种</th><th>规格</th><th>11-20 全国参考塘口价</th><th>原文分区标记</th></tr></thead><tbody>
        <tr><td><span class="tag tag-gui">鳜鱼</span></td><td><span class="spec spec-s">0.8~1.2 斤</span></td><td class="price"><b>32.0~33.5 元/斤</b></td><td style="color:#dc2626;font-size:12px">📈 飘红上涨区 ✓</td></tr>
        <tr><td><span class="tag tag-lu">鲈鱼</span></td><td><span class="spec spec-s">0.8~1.2 斤</span></td><td class="price"><b>12.3~13.0 元/斤</b></td><td style="color:#16a34a;font-size:12px">📉 弱势下跌区</td></tr>
  </tbody></table>
  <div class="callout" style="margin-top:10px"><b>口径说明：</b>① 分区标记（✓ / 📉）为原文栏目归类，<b>非逐项涨跌数值，不推断具体涨跌幅度</b>；与 11-19 期同号卡数值略有差异，按约定<b>只列本期数值与原文标记、不作两期比较、不推断涨跌、不重复计数</b>。② 视频号「全国参考塘口价」为宽区间口径，与塘口报价（鳜康泰 11-19 江苏标鳜 24.5）、白沙洲批发、盛阳本地批发 25~30 / 10~14、加州鲈周报塘头价、次日预测<b>多口径并存、禁止互减</b>，只看方向不看绝对值。</div>
  <div class="legend">来源：微信视频号「互联惠农小洁」2026-11-20《11月20日！全国塘口最新鱼价！》（封面与描述日期一致）· 📷 用户截图核校录入 · 元/斤 · 全国塘口参考价，仅供参考</div>
</div>

"""

# ---------------- 7) 于老师 11-20 视频号 ----------------
CARD_YULAOSHI = """
<div class="card" style="margin-top:14px">
  <h3>🎬 11月20日 · 视频号「水产养殖服务于老师」全国参考塘口价（封面 2026.11.20 · 元/斤）</h3>
  <div class="csub">用户提交视频号截图：封面「<b>2026.11.20 全国鱼价 · 收鱼</b>」与底部描述「2026年11月20日全国鱼价（塘头价）」<b>日期一致，按 11-20 归期</b>。表格 13 个品种除白鲢 2 斤上标「↓持续低迷」外，<b>其余全部标「→基本持平」</b>；本看板仅录<b>加州鲈 1 斤上 9.0~10.5（→基本持平）</b>与<b>鳜鱼 1 斤上 23~26（→基本持平）</b>。原文注「行情仅做参考，具体以塘口现场议价为准」。</div>
  <table><thead><tr><th>品种</th><th>规格</th><th>11-20 收鱼参考价</th><th>原文标注</th></tr></thead><tbody>
        <tr><td><span class="tag tag-gui">鳜鱼</span></td><td><span class="spec spec-s">1 斤上</span></td><td class="price"><b>23~26 元/斤</b></td><td style="color:#64748b;font-size:12px">→基本持平</td></tr>
        <tr><td><span class="tag tag-lu">加州鲈</span></td><td><span class="spec spec-s">1 斤上</span></td><td class="price"><b>9.0~10.5 元/斤</b></td><td style="color:#64748b;font-size:12px">→基本持平</td></tr>
  </tbody></table>
  <div class="callout" style="margin-top:10px"><b>口径说明：</b>① 与 11-19 期同号卡（鳜 23-26 ↑ / 鲈 10.0-11 持平）相比，本期数值与箭头均有变化，<b>按原文各自照录、不互减、不互相订正、不推断统一涨跌、不作两期比较</b>。② 本卡为「<b>收鱼 / 塘头价</b>」全国参考区间，与鳜康泰 11-19 塘口报价、腾氏㊻ 周报塘头价、白沙洲批发、盛阳本地批发、淡水渔业分市场批发、小洁视频号区间、次日预测<b>多口径并存、禁止互减</b>。③ 生鱼 / 鮰鱼 / 黄颡鱼 / 青鱼 / 花鲢 / 罗非鱼 / 草鱼 / 鲫鱼 / 鳊鱼 / 鲤鱼 / 白鲢等 11 个非目标品种按约定不录入。</div>
  <div class="legend">来源：微信视频号「水产养殖服务于老师」2026-11-20《2026.11.20 全国鱼价（收鱼）》（封面与描述日期一致）· 📷 用户截图核校录入 · 元/斤 · 行情仅做参考，具体以塘口现场议价为准</div>
</div>

"""

# ---------------- 插入动作 ----------------
def insert_before(h3_marker, card_html, label):
    """在含 h3_marker 的卡片之前插入新卡"""
    global html
    at = html.find(h3_marker)
    assert at > 0, ("锚点未找到", label, h3_marker)
    pos = html.rfind('<div class="card"', 0, at)
    if pos < 0:
        pos = html.rfind('<div class="card ', 0, at)
    assert pos > 0, ("卡片起点未找到", label)
    html = html[:pos] + card_html + html[pos:]
    print("[OK] 插入", label, "@", pos)

insert_before("🐟 腾氏水产 · 鳜鱼塘头价（2026-11-12", CARD_TENGSHI, "腾氏㊻ 11-19")
insert_before("🌊 2026-11-16 · 淡水渔业", CARD_DANSHUI, "淡水渔业 11-20")
insert_before("🐟 11月13日 · 海大农牧", CARD_HAIDA, "海大 11-20")
insert_before("🐟 鳜康泰特约 · 全国鳜鱼报价（2026-11-18", CARD_GUIKT, "鳜康泰 11-19")
insert_before("🛒 2026.11.19 · 无锡盛阳食品城", CARD_SHENGYANG, "盛阳 11.20")
insert_before("🎬 11月19日 · 视频号「互联惠农小洁」", CARD_XIAOJIE, "小洁 11-20")
insert_before("🎬 11月19日 · 视频号「水产养殖服务于老师」", CARD_YULAOSHI, "于老师 11-20")

# ---------------- 8) 45 期卡：同源合并双出处注 ----------------
OLD_CALLOUT = "④ 塘头价口径，与盛阳批发 10~14、白沙洲 9.90、视频号 10.0~11 / 11.8~13.2<b>多口径并存</b>。</div>"
NEW_CALLOUT = ("④ 塘头价口径，与盛阳批发 10~14、白沙洲 9.90、视频号 10.0~11 / 11.8~13.2<b>多口径并存</b>。"
    "⑤ <b>同源合并·双出处</b>：2026-11-20 16:41「鳜鲈前沿」《加州鲈周报 2026 第 36 期：最高跌 1 元/斤！广东缺大鱼，外省多地跌价》给出 <b>11.13 → 11.20</b> 对照表，"
    "与本卡 11.11 → 11.18 对照表在 <b>浙江 8 成统货 11-11.5→10.5-11（↓0.5）、江苏 9 两上 10.5-11.5→9.5-10.5（↓1）、四川 9 两上 10.5→10.5、湖南 9 两上 10.5→10.5、湖北 8.5 两上 10.5→10.5、河南 1 斤上 11→10.5（↓0.5）共 6 产区逐项同值同箭头</b>；"
    "判为<b>同一份周报报价的两个发布渠道 / 不同期号体系</b>（水产前沿第 45 期 11-18 发布 vs 鳜鲈前沿第 36 期 11-20 发布，日期列 11.11→11.18 vs 11.13→11.20）。"
    "按约定<b>合并一卡、双出处留痕、不重复计数、不作两期比较、不推断统一日期</b>；广东佛山口径略异（本卡 1 斤上 10.3-10.5→10.2-10.3 ↓0.1-0.2、8 两上 11.18 未给；第 36 期 1 斤上 10.3→10.3 →、8 两上 9-10→9-10 →），"
    "<b>按原文各自照录、不互减、不互相订正</b>。</div>")
OLD_LEGEND = '· <a class="plink" href="https://mp.weixin.qq.com/s/Zg4FhJ_7AJBnrdF3qkp_BQ" target="_blank" rel="noopener">📄 阅读原文</a> · 元/斤 · 塘头价 · 正文表格核校录入'
NEW_LEGEND = ('· <a class="plink" href="https://mp.weixin.qq.com/s/Zg4FhJ_7AJBnrdF3qkp_BQ" target="_blank" rel="noopener">📄 阅读原文（水产前沿 第45期）</a> '
    '· 同源双出处：<a class="plink" href="__U_QY36__" target="_blank" rel="noopener">📄 鳜鲈前沿 第36期（11-20）</a> · 元/斤 · 塘头价 · 正文表格核校录入').replace("__U_QY36__", U_QY36)
assert html.count(OLD_CALLOUT) == 1, ("45期 callout 锚点", html.count(OLD_CALLOUT))
assert html.count(OLD_LEGEND) == 1, ("45期 legend 锚点", html.count(OLD_LEGEND))
html = html.replace(OLD_CALLOUT, NEW_CALLOUT, 1).replace(OLD_LEGEND, NEW_LEGEND, 1)
print("[OK] 45 期卡追加同源合并双出处注")

# ---------------- chip 快览同步（幂等） ----------------
def rep(old, new, label):
    global html
    c = html.count(old)
    if c == 1:
        html = html.replace(old, new, 1)
        print("[OK] chip", label)
    elif c == 0 and html.count(new) >= 1:
        print("[SKIP] chip", label, "(已是新值)")
    else:
        raise SystemExit("[ERROR] chip 锚点异常 %s c=%d" % (label, c))

rep("11-02/11-06/11-10/11-16）+ 通威农牧批发价", "11-02/11-06/11-10/11-16/11-20）+ 通威农牧批发价", "淡水渔业")
rep("/11-15/11-17/11-19）+ 老段", "/11-15/11-17/11-19/11-20）+ 老段", "小洁")
rep("/11-13/11-17/11-19）+ 阿洁", "/11-13/11-17/11-19/11-20）+ 阿洁", "于老师")
rep("/11-14/11-16/11-18）+ 腾氏一周鱼价播报", "/11-14/11-16/11-18/11-19）+ 腾氏一周鱼价播报", "鳜康泰")
rep("播报㊸㊹㊺（10-29/11-05/11-12）", "播报㊸㊹㊺㊻（10-29/11-05/11-12/11-19）", "腾氏㊻")
rep("/ 11-17 同值并入强渔周报）", "/ 11-17 同值并入强渔周报 / 11-20 鳜鲈双表）", "海大")
rep("/11.17/11.19批发）", "/11.17/11.19/11.20批发）", "盛阳")
rep("/ 第45期（11-18）+ 渔无忧", "/ 第45期（11-18）/ 第36期（11-20 同源双渠道）+ 渔无忧", "加州鲈周报")
rep("11-17App截图·OCR通道）", "11-17/11-18/11-20App截图·OCR通道）", "科学养鱼OCR")

# ---------------- 标签精确配平 ----------------
def balance(s):
    for tag in ["div", "table", "thead", "tbody", "tr", "td", "th", "h3", "span", "a", "b"]:
        o = len(re.findall(r"<%s(?=[\s>])" % tag, s))
        c = len(re.findall(r"</%s>" % tag, s))
        assert o == c, ("标签不配平", tag, o, c)
    print("[OK] 标签精确配平全通过")

balance(html)

open(F, "w", encoding="utf-8").write(html)
print("[DONE] 写盘", F, len(html), "chars")
