#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""2026-11-17 晚间批次：8 链接 + 4 截图判定 → 7 张新卡 + 强渔卡海大同源合并注 + chip 8 处（幂等）。

链接判定：
  1. 水产前沿《特水鱼周报2026第39期》（发布 11-17 18:23）—— 录入（qianyan 源首次落值 11-17）。
     鳜鱼塘头（11.2 vs 11.17）：佛山中鳜 ↑0.5~1、湖北标鳜 25-26→26 ↑1，江苏 24-25 →；
     饲料鳜 22.5 低于鱼仔鳜。加州鲈：佛山 1 斤上 11-11.5→10.3 ↘0.7-1.2（较半月前跌 1.2）、
     河南 11.5→11 ↘0.5，广东统货开价 9.5-10，其余产区 →。
  2. 通威 11-13 —— 重复跳过（链接 lKr9j5sidKetnkeaQc50yA 与已有卡一致）。
  3. 江苏凌家塘市场《一周价格行情（2026/11/8~11/14）》（发布 11-14 15:25）—— 录入。
     仅鲈鱼约 12 元/斤（周均价口径）；本期原文未见鳜鱼报价，如实留空。
  4. 渔飞鱼日报 11-16（8HmZMDMMGr5-I4PCwHvlUA）—— 重复跳过（昨日已录）。
  5. 渔飞鱼水产《明日水产行情预报 2026-11-18》（发布 11-17 10:02）—— 录入（yufeiyu 通道）。
     白沙洲 11/16 鲈鱼 ≥500g 9.90 → 预测 9.8~10.0、<500g 9.50→9.5；无鳜鱼条目，留空。
  6. 淡水渔业 11-16 分市场批发价（发布 11-16 17:04）—— 录入。鳜鱼 8 市场 + 加州鲈 8 市场（元/公斤）。
  7. 腾氏「高端水产·看上上报价㊺」（11-16 18:58）—— 录入（加州鲈塘口：广东 1 斤上 10 ↓0.2-0.3
     有价无市、环太湖 9.8-11、湖南华容/湖北武汉 9 两起 10 持平、成都 1 斤上 10.5-11 持平）。
  8. 海大农牧 11-17 17:55《"同鱼不同价"撕裂市场》—— 鳜鲈数值与强渔 11-16 周报逐项同值
     （鱼仔鳜 23-24/饲料鳜 19-22/江苏 25.5/安徽 25/湖南 24.5/湖北 26；鲈鱼同值），
     判同源合并，在强渔卡 callout 加双出处注，不重复计数、不另建卡。

截图判定：
  A. 科学养鱼 11-17 分市场批发价（App 截图）—— 录入（kexue_web 更新至 11-17）。
     仅鳜鱼段部分行可见：太原五龙口 65.00、南环桥 50.50/55.50（与淡水渔业 11-16 同值并列）、
     乌鲁木齐北园春 120.00、凌家塘 54.00、黄沙 ≥750 54.00；宜昌行价格被截断不录；加州鲈段未见。
  B. 服务于老师 11-17 / C. 小洁 11-17 视频号 —— 今早已录，重复跳过。
  D. 盛阳食品城 11.17 —— 录入（鳜鱼 25~30 / 鲈鱼 10~14，与 11.15/11.16 同值三连并列）。

V2 桥接注意：
  - CLUE_SPECS 新增「看上上报价」「水产前沿 特水鱼周报」两条；容量 12→16 三处同步
    （sync_v2_from_v1.py build_clues rows[:16] + build_dashboard_v2.py clue_rows[:16] / posts[:16]）。
  - GUI_POND_SPECS / LU_POND_SPECS 不加水产前沿（其表为 5 列双日期对照、产区跨行合并，
    与 tds[0]产区/tds[1]规格/tds[2]价格 解析模式不兼容）；V2 鳜鱼/加州鲈 KPI 保持 11-16。
"""
import re
import sys

HTML = "鳜鱼鲈鱼价格看板.html"
URL_QYQY = "https://mp.weixin.qq.com/s/Xqbk_JMSOdkAS5b9VbR8Rg"
URL_LJT = "https://mp.weixin.qq.com/s/N_qqS2yV0TiIfVMj6sMmEg"
URL_YFY = "https://mp.weixin.qq.com/s/9BS96lPCjX1ivxBz_KO_8w"
URL_DS = "https://mp.weixin.qq.com/s/WnPgOc2RHesxzWYPGGEyMQ"
URL_KSS = "https://mp.weixin.qq.com/s/lt0kxKImOCCrx3jP1vawzQ"

ANCHORS = {
    "qyqy": "渔飞鱼水产行情日报 2026-11-17",          # 日报 11-17 卡前
    "ljt": "🏪 江苏凌家塘市场 · 一周价格行情（2026/11/1~11/7",  # 凌家塘最近一期卡前
    "yfy": "明日水产行情预报 · 11-11 周三",            # 渔飞鱼预报系列最近一期卡前
    "kx": "11月13日 · 全国分市场批发价（科学养鱼",      # 科学养鱼 11-13 卡前（先插截图卡）
    "ds": "11月13日 · 全国分市场批发价（科学养鱼",      # 再插淡水渔业 11-16 卡在其前
    "kss": "广东「火箭鲈」熄火",                        # 看上上报价 11-02 卡前
    "sy": "🛒 2026.11.16 · 无锡盛阳食品城",            # 盛阳 11.16 卡前
}
GUARDS = [
    "特水鱼周报 2026 第 39 期",
    "一周价格行情（2026/11/8~11/14 · 水产摘录",
    "明日水产行情预报 2026-11-18",
    "🌊 2026-11-16 · 淡水渔业 分市场批发价",
    "🌊 11月17日 · 科学养鱼 分市场批发价（App 截图核校",
    "看上上报价㊺」：广东 1 斤上跌至 10 元",
    "🛒 2026.11.17 · 无锡盛阳食品城",
]

CARD_QYQY = """
<div class="card" style="margin-top:14px">
  <h3>📰 2026-11-17 · 水产前沿 · 特水鱼周报 2026 第 39 期：鳜鱼回暖最高涨 1 元/斤、加州鲈较半月前跌 1.2 元/斤（元/斤）</h3>
  <div class="csub">「水产前沿」2026-11-17 18:23 发布第 39 期特水鱼周报，双列对照 11.2 vs 11.17。<b>鳜鱼：发病减少、鱼价回暖</b>——佛山中鳜上涨 0.5~1 元/斤（3成中鳜 21-22→22、2成中鳜 22-23→23、1成中鳜1成小鳜 23-24→24-24.5）、小鳜持平、<b>湖北标鳜 25-26→26 ↑1</b>、<b>江苏标鳜 24-25 持平</b>、湖南/江西/广西/安徽持平；<b>饲料鳜报价约 22.5 元/斤、低于鱼仔鳜</b>，实际成交看规格与条形。<b>加州鲈：清塘+集中上市</b>——佛山 1 斤上 11-11.5→10.3（较上周跌 0.7-1.2、较半月前大跌 1.2 元/斤），统货开价 9.5-10；河南 1 斤上 11.5→11 ↘0.5；浙江/江苏/四川/湖南/湖北基本维稳。临近年底养户集中出鱼回笼资金。</div>
  <table><thead><tr><th>鳜鱼 产区/规格</th><th>11.2（元/斤）</th><th>11.17（元/斤）</th><th>环比</th></tr></thead><tbody>
        <tr><td><span class="tag tag-gui">佛山</span> 3成中鳜</td><td class="price"><b>21-22</b></td><td class="price"><b>22</b></td><td style="font-size:12px">▲ 1↑</td></tr>
        <tr><td><span class="tag tag-gui">佛山</span> 2成中鳜</td><td class="price"><b>22-23</b></td><td class="price"><b>23</b></td><td style="font-size:12px">▲ 1↑</td></tr>
        <tr><td><span class="tag tag-gui">佛山</span> 1成中鳜 1成小鳜</td><td class="price"><b>23-24</b></td><td class="price"><b>24-24.5</b></td><td style="font-size:12px">▲ 0.5-1↑</td></tr>
        <tr><td><span class="tag tag-gui">佛山</span> 2成小鳜</td><td class="price"><b>21-22</b></td><td class="price"><b>21-22</b></td><td style="font-size:12px">→ 持平</td></tr>
        <tr><td><span class="tag tag-gui">佛山</span> 3成小鳜</td><td class="price"><b>19-20</b></td><td class="price"><b>19-20</b></td><td style="font-size:12px">→ 持平</td></tr>
        <tr><td><span class="tag tag-gui">江苏</span> 标鳜</td><td class="price"><b>24-25</b></td><td class="price"><b>24-25</b></td><td style="font-size:12px">→ 持平 · 离宜兴官林最近的分产区口径</td></tr>
        <tr><td><span class="tag tag-gui">湖南</span> 标鳜</td><td class="price"><b>24.5</b></td><td class="price"><b>24.5</b></td><td style="font-size:12px">→ 持平</td></tr>
        <tr><td><span class="tag tag-gui">湖北</span> 标鳜</td><td class="price"><b>25-26</b></td><td class="price"><b>26</b></td><td style="font-size:12px">▲ 1↑</td></tr>
        <tr><td><span class="tag tag-gui">江西</span> 标鳜</td><td class="price"><b>25-26</b></td><td class="price"><b>25-26</b></td><td style="font-size:12px">→ 持平</td></tr>
        <tr><td><span class="tag tag-gui">广西</span> 标鳜</td><td class="price"><b>26</b></td><td class="price"><b>26</b></td><td style="font-size:12px">→ 持平</td></tr>
        <tr><td><span class="tag tag-gui">安徽</span> 标鳜</td><td class="price"><b>26</b></td><td class="price"><b>26</b></td><td style="font-size:12px">→ 持平</td></tr>
  </tbody></table>
  <table style="margin-top:8px"><thead><tr><th>加州鲈 产区/规格</th><th>11.02（元/斤）</th><th>11.17（元/斤）</th><th>环比</th></tr></thead><tbody>
        <tr><td><span class="tag tag-lu">广东佛山</span> 9两上</td><td class="price"><b>9.2-9.5</b></td><td class="price"><b>9.2-9.5</b></td><td style="font-size:12px">→ 持平</td></tr>
        <tr><td><span class="tag tag-lu">广东佛山</span> 1斤上</td><td class="price"><b>11-11.5</b></td><td class="price"><b>10.3</b></td><td style="font-size:12px">▼ 0.7-1.2 · 较半月前跌 1.2</td></tr>
        <tr><td><span class="tag tag-lu">浙江</span> 8成统货</td><td class="price"><b>11-11.5</b></td><td class="price"><b>11-11.5</b></td><td style="font-size:12px">→ 持平</td></tr>
        <tr><td><span class="tag tag-lu">江苏</span> 9两上</td><td class="price"><b>10.5-11.5</b></td><td class="price"><b>10.5-11.5</b></td><td style="font-size:12px">→ 持平 · 离宜兴官林最近的分产区口径</td></tr>
        <tr><td><span class="tag tag-lu">四川</span> 9两上</td><td class="price"><b>10.5</b></td><td class="price"><b>10.5</b></td><td style="font-size:12px">→ 持平</td></tr>
        <tr><td><span class="tag tag-lu">四川</span> 1斤上</td><td class="price"><b>11</b></td><td class="price"><b>11</b></td><td style="font-size:12px">→ 持平</td></tr>
        <tr><td><span class="tag tag-lu">湖南</span> 9两上</td><td class="price"><b>10.5</b></td><td class="price"><b>10.5</b></td><td style="font-size:12px">→ 持平</td></tr>
        <tr><td><span class="tag tag-lu">湖北</span> 8.5两上</td><td class="price"><b>10.5</b></td><td class="price"><b>10.5</b></td><td style="font-size:12px">→ 持平</td></tr>
        <tr><td><span class="tag tag-lu">河南</span> 1斤上</td><td class="price"><b>11.5</b></td><td class="price"><b>11</b></td><td style="font-size:12px">▼ 0.5↓</td></tr>
  </tbody></table>
  <div class="callout" style="margin-top:10px"><b>多口径说明：</b>① 本卡为<b>塘头/出塘参考价（元/斤）</b>，双列对照为该报自身给出的环比口径，仅照录原文；与鳜康泰 11-16（江苏标鳜 24.5）、强渔 11-16（江苏标鱼 25.5）、白沙洲批发 30.25 元/斤折算、科学养鱼/淡水渔业分市场批发（元/公斤）<b>渠道·规格·时间三重不同，多口径并存、禁止互减</b>——如湖北标鳜本卡 26 与鳜康泰 24、渔有福 24 为不同成数/渠道口径，不作订正。② 佛山「成鳜」按中鳜/小鳜成数分档，与鳜康泰小鳜 19/标鳜 23 规格口径不同。③ 广东统货开价 9.5-10 与分规格价并存照录。④ 黄颡/生鱼/江团/金鲳按约定不录入。</div>
  <div class="legend">来源：微信公众号「水产前沿」2026-11-17 18:23《爽市最高涨1.5元/斤，黄颡、鳜鱼齐涨价！生鱼加州鲈惨淡跌1.2元/斤，江团金鲳稳定｜特水鱼周报2026第39期》· <a class="plink" href="__URL_QYQY__" target="_blank" rel="noopener">📄 阅读原文（特水鱼周报第 39 期）</a> · 元/斤 · 塘头/出塘参考价，受规格条形影响仅供参考</div>
</div>
""".replace("__URL_QYQY__", URL_QYQY)

CARD_LJT = """
<div class="card" style="margin-top:14px">
  <h3>🏪 江苏凌家塘市场 · 一周价格行情（2026/11/8~11/14 · 水产摘录）</h3>
  <div class="csub">「江苏凌家塘市场」官方号 2026-11-14 15:25 发布一周价格行情（2026/11/8~11/14）。水产部分与本看板相关仅 <b>1 项：鲈鱼约 12 元/斤（周均价口径）</b>；本期原文<b>未见鳜鱼报价，如实留空</b>。牛蛙约 11 元/斤、河虾约 60 元/斤等其他品种按约定不录入。</div>
  <table><thead><tr><th>品种</th><th>口径</th><th>价格</th><th>原文标注</th></tr></thead><tbody>
        <tr><td><span class="tag tag-lu">鲈鱼</span></td><td><span class="spec spec-s">常州凌家塘销区 · 周均价（11/8~11/14）</span></td><td class="price"><b>约 12 元/斤</b></td><td style="font-size:12px">周度区间均值口径，未给涨跌</td></tr>
        <tr><td><span class="tag tag-gui">鳜鱼</span></td><td><span class="spec spec-s">常州凌家塘销区</span></td><td class="price"><b>—</b></td><td style="font-size:12px">本期原文未见鳜鱼报价，如实留空</td></tr>
  </tbody></table>
  <div class="callout" style="margin-top:10px"><b>口径说明：</b>① 凌家塘为<b>常州本地销区批发市场</b>（离宜兴官林最近的大宗销区之一），周均价口径与日度批发/塘口价<b>时间基准不同，禁止互减</b>；与盛阳 11.17 无锡本地批发（鲈鱼 10~14）、白沙洲日度批发（9.90）并列照录、不互减。② 历史同期对比：本市场 10 月周报鲈鱼约 12 元/斤，本期同值，属周均价口径稳定，<b>不推断涨跌</b>。③ 另：科学养鱼 11-17 截图显示该市场 11/17 鳜鱼 500~750g 54.00 元/公斤（约 27 元/斤）为<b>日度分市场批发口径</b>，与本卡周均价口径不同、分别照录。</div>
  <div class="legend">来源：微信公众号「江苏凌家塘市场」2026-11-14 15:25《江苏凌家塘市场一周价格行情（2026/11/8~2026/11/14）》· <a class="plink" href="__URL_LJT__" target="_blank" rel="noopener">📄 阅读原文（凌家塘一周行情 11/8~14）</a> · 元/斤 · 周均价，仅供参考</div>
</div>
""".replace("__URL_LJT__", URL_LJT)

CARD_YFY = """
<div class="card" style="margin-top:14px">
  <h3>🐟 渔飞鱼 ·《明日水产行情预报 2026-11-18》（发布 11月17日 10:02 · 次日预测口径 · 白沙洲鲈鱼低位企稳）</h3>
  <div class="csub">「渔飞鱼水产」2026-11-17 10:02 发布《明日水产行情预报 | 2026年11月18日》。与本看板相关仅加州鲈一项：<b>武汉白沙洲 11/16 鲈鱼均价 19.80 元/公斤（约 9.90 元/斤）与上一采价持平，前期回落后暂时企稳</b>，预测 ≥500g 9.8~10.0（基准 9.90）、&lt;500g 9.5（基准 9.50）；「存塘偏少对价格有一定支撑，预计周内低位震荡」。<b>本期原文未见鳜鱼条目，如实留空</b>。操作建议「达规格按周内走货节奏出塘、不建议压塘惜售」为原文叙述，照录不作数据。</div>
  <table><thead><tr><th>品种</th><th>口径 · 基准</th><th>基准价（11/16）</th><th>次日预测（11-18）</th></tr></thead><tbody>
        <tr><td><span class="tag tag-lu">加州鲈</span></td><td><span class="spec spec-s">武汉白沙洲 ≥500g</span></td><td class="price"><b>9.90 元/斤</b></td><td style="font-size:12px"><b>9.8~10.0</b> · 低位震荡企稳</td></tr>
        <tr><td><span class="tag tag-lu">加州鲈</span></td><td><span class="spec spec-s">武汉白沙洲 &lt;500g</span></td><td class="price"><b>9.50 元/斤</b></td><td style="font-size:12px"><b>9.5</b> · 持稳</td></tr>
        <tr><td><span class="tag tag-gui">鳜鱼</span></td><td><span class="spec spec-s">—</span></td><td class="price"><b>—</b></td><td style="font-size:12px">本期原文未见鳜鱼条目，如实留空</td></tr>
  </tbody></table>
  <div class="callout" style="margin-top:10px"><b>预测口径说明：</b>① 本卡为<b>次日预测价</b>，与白沙洲实测成交价（日报 11-17 卡 11/15 实测 ≥500g 9.90）虽同值，但<b>口径与时间基准不同，禁止互减、不作命中率评价</b>（渔无忧 11-13 预报 vs 11-14 实测同一约定）。② 基准取白沙洲 11/16 报价，预测日为 11-18，中间隔 11-17 一日，照原文照录。③ 与渔无忧 11-16 独立预报（白沙洲 9.90/9.50）为<b>不同公众号的预测通道</b>，同基准同值并列、不重复计数、不推断涨跌。④ 原文「鲫鱼/鲤鱼/白鲢小幅回落」等其他品种按约定不录入。</div>
  <div class="legend">来源：微信公众号「渔飞鱼水产」2026-11-17 10:02《明日水产行情预报 | 2026年11月18日》· <a class="plink" href="__URL_YFY__" target="_blank" rel="noopener">📄 阅读原文（明日预报 11-18）</a> · 元/斤 · 次日预测口径，仅供参考</div>
</div>
""".replace("__URL_YFY__", URL_YFY)

CARD_KX = """
<div class="card" style="margin-top:14px">
  <h3>🌊 11月17日 · 科学养鱼 分市场批发价（App 截图核校 · 鳜鱼段部分行）</h3>
  <div class="csub">用户提供「科学养鱼」App 截图，标题《11月17日最新全国水产品批发价格》，表内各行标注<b>11月17日</b>。本批截图<b>仅见鳜鱼段部分行</b>（6 条，湖北宜昌行价格被截断不可见、不录；加州鲈段未见）；数值为<b>元/公斤口径</b>，苏州南环桥两档与「淡水渔业」11-16 卡<b>同值</b>，分别照录不合并。泥鳅等其他品种行按约定不录入。</div>
  <table><thead><tr><th>鳜鱼 市场</th><th>规格（条重 g）</th><th>11-17 批发价</th><th>备注</th></tr></thead><tbody>
        <tr><td><span class="tag tag-gui">太原五龙口</span></td><td><span class="spec spec-s">500~750</span></td><td class="price"><b>65.00 元/公斤</b></td><td style="font-size:12px">—</td></tr>
        <tr><td><span class="tag tag-gui">苏州南环桥</span></td><td><span class="spec spec-s">250~500</span></td><td class="price"><b>50.50 元/公斤</b></td><td style="font-size:12px">与淡水渔业 11-16 同值并列，未标沿用不推断涨跌</td></tr>
        <tr><td><span class="tag tag-gui">苏州南环桥</span></td><td><span class="spec spec-s">500~750</span></td><td class="price"><b>55.50 元/公斤</b></td><td style="font-size:12px">同上 · 与 11-13 本系列卡南环桥行隔多期不作比较</td></tr>
        <tr><td><span class="tag tag-gui">乌鲁木齐北园春</span></td><td><span class="spec spec-s">500~750</span></td><td class="price"><b>120.00 元/公斤</b></td><td style="font-size:12px">远端销区极端价，照录不参与跨区价差分析</td></tr>
        <tr><td><span class="tag tag-gui">江苏凌家塘</span></td><td><span class="spec spec-s">500~750</span></td><td class="price"><b>54.00 元/公斤</b></td><td style="font-size:12px">约 27 元/斤 · 与凌家塘官方周均价卡（鲈鱼）口径不同分列</td></tr>
        <tr><td><span class="tag tag-gui">广州黄沙</span></td><td><span class="spec spec-s">≥750</span></td><td class="price"><b>54.00 元/公斤</b></td><td style="font-size:12px">—</td></tr>
  </tbody></table>
  <div class="callout" style="margin-top:10px"><b>截图核校说明：</b>① 本卡为<b>分市场批发价（元/公斤）</b>，与塘口价、白沙洲单品批发、本地销区周均价<b>多口径并存、禁止互减</b>。② 乌鲁木齐 120 元/公斤为远端销区极端价（运输成本主导），按原文照录但<b>不参与跨区价差分析</b>（FAR_MARKETS 约定）。③ 苏州南环桥 250~500 50.50 / 500~750 55.50 与「淡水渔业」11-16 卡逐项同值，两卡分属不同公众号/采集通道（kexue_web vs danshui），<b>分源登记、同值并列、不重复计数、不推断涨跌</b>；未标「沿用」不作沿用判定。④ 宜昌行价格被截图截断，未见数值不录、不推算。⑤ 加州鲈段本期未见，如实留空。</div>
  <div class="legend">来源：「科学养鱼」App《11月17日最新全国水产品批发价格》用户截图（2026-11-17 提交）· 📷 截图核校录入 · 元/公斤 · 分市场批发价，仅供参考</div>
</div>
"""

CARD_DS = """
<div class="card" style="margin-top:14px">
  <h3>🌊 2026-11-16 · 淡水渔业 分市场批发价（鳜鱼 8 市场 + 加州鲈 8 市场 · 元/公斤）</h3>
  <div class="csub">「淡水渔业」2026-11-16 17:04 发布《11月16日黄颡鱼、鳜鱼、加州鲈、黄鳝、乌鳢、泥鳅、斑点叉尾鮰批发价格》，正文文字表格汇总全国多地主流市场当日报价。<b>鳜鱼 8 市场：福州名成 ≥750 最高 75.00、上饶 62.00、临沂 60.00、萍乡 60.00、南环桥 55.50/50.50、马王堆 53.00、岳各庄 51.00（均为元/公斤）</b>；<b>加州鲈 ≥500g：上海江杨 30.00 最高、岳各庄 29.40、重庆涪陵 28.00、萍乡 26.00、南京众彩 24.50、两湖绿谷 23.90、湖州菱湖 22.80（&lt;500g 20.40）</b>。黄颡/黄鳝等其他品种按约定不录入。</div>
  <table><thead><tr><th>鳜鱼 市场</th><th>规格（条重 g）</th><th>11-16 批发价</th><th>备注</th></tr></thead><tbody>
        <tr><td><span class="tag tag-gui">福州名成</span></td><td><span class="spec spec-s">≥750</span></td><td class="price"><b>75.00 元/公斤</b></td><td style="font-size:12px">本表最高 · 销区口径</td></tr>
        <tr><td><span class="tag tag-gui">上饶供销</span></td><td><span class="spec spec-s">500~750</span></td><td class="price"><b>62.00 元/公斤</b></td><td style="font-size:12px">—</td></tr>
        <tr><td><span class="tag tag-gui">临沂华东</span></td><td><span class="spec spec-s">≥750</span></td><td class="price"><b>60.00 元/公斤</b></td><td style="font-size:12px">—</td></tr>
        <tr><td><span class="tag tag-gui">萍乡城南</span></td><td><span class="spec spec-s">250~500</span></td><td class="price"><b>60.00 元/公斤</b></td><td style="font-size:12px">—</td></tr>
        <tr><td><span class="tag tag-gui">苏州南环桥</span></td><td><span class="spec spec-s">500~750</span></td><td class="price"><b>55.50 元/公斤</b></td><td style="font-size:12px">与科学养鱼 11-17 截图同值并列，不重复计数</td></tr>
        <tr><td><span class="tag tag-gui">长沙马王堆</span></td><td><span class="spec spec-s">500~750</span></td><td class="price"><b>53.00 元/公斤</b></td><td style="font-size:12px">—</td></tr>
        <tr><td><span class="tag tag-gui">北京岳各庄</span></td><td><span class="spec spec-s">500~750</span></td><td class="price"><b>51.00 元/公斤</b></td><td style="font-size:12px">—</td></tr>
        <tr><td><span class="tag tag-gui">苏州南环桥</span></td><td><span class="spec spec-s">250~500</span></td><td class="price"><b>50.50 元/公斤</b></td><td style="font-size:12px">同上 · 与科学养鱼 11-17 截图同值并列</td></tr>
  </tbody></table>
  <table style="margin-top:8px"><thead><tr><th>加州鲈 市场</th><th>规格</th><th>11-16 批发价</th><th>备注</th></tr></thead><tbody>
        <tr><td><span class="tag tag-lu">上海江杨</span></td><td><span class="spec spec-s">≥500g</span></td><td class="price"><b>30.00 元/公斤</b></td><td style="font-size:12px">本表最高 · 销区口径</td></tr>
        <tr><td><span class="tag tag-lu">北京岳各庄</span></td><td><span class="spec spec-s">≥500g</span></td><td class="price"><b>29.40 元/公斤</b></td><td style="font-size:12px">—</td></tr>
        <tr><td><span class="tag tag-lu">重庆涪陵</span></td><td><span class="spec spec-s">≥500g</span></td><td class="price"><b>28.00 元/公斤</b></td><td style="font-size:12px">远端销区照录</td></tr>
        <tr><td><span class="tag tag-lu">萍乡城南</span></td><td><span class="spec spec-s">≥500g</span></td><td class="price"><b>26.00 元/公斤</b></td><td style="font-size:12px">—</td></tr>
        <tr><td><span class="tag tag-lu">南京众彩</span></td><td><span class="spec spec-s">≥500g</span></td><td class="price"><b>24.50 元/公斤</b></td><td style="font-size:12px">约 12.25 元/斤 · 江苏本地销区最近口径</td></tr>
        <tr><td><span class="tag tag-lu">两湖绿谷</span></td><td><span class="spec spec-s">≥500g</span></td><td class="price"><b>23.90 元/公斤</b></td><td style="font-size:12px">—</td></tr>
        <tr><td><span class="tag tag-lu">湖州菱湖</span></td><td><span class="spec spec-s">≥500g</span></td><td class="price"><b>22.80 元/公斤</b></td><td style="font-size:12px">—</td></tr>
        <tr><td><span class="tag tag-lu">湖州菱湖</span></td><td><span class="spec spec-s">&lt;500g</span></td><td class="price"><b>20.40 元/公斤</b></td><td style="font-size:12px">小规格约 10.20 元/斤</td></tr>
  </tbody></table>
  <div class="callout" style="margin-top:10px"><b>口径说明：</b>① 本卡为<b>分市场批发价（元/公斤）</b>，折元/斤仅供阅读；与塘口价（鳜康泰 11-16 / 强渔 11-16）、白沙洲单品批发（30.25 / 9.90 元/斤折算）、本地销区周均价<b>多口径并存、禁止互减</b>。② 南环桥两行与「科学养鱼」11-17 截图逐项同值——两卡分属 danshui / kexue_web 不同通道，<b>分源登记、同值并列、不重复计数、未标沿用不推断涨跌</b>；与 11-10 淡水渔业（与科学养鱼合并）卡之间隔多期，<b>只列本期数值、不作两期比较</b>。③ 上海江杨与北京岳各庄为高价销区、与历史 11-10 期同市场行口径可对照但原文未给涨跌，不推断。④ 跨区价差按约定过滤远端销区（重庆/乌鲁木齐等），不参与产地-销区流通成本分析。</div>
  <div class="legend">来源：微信公众号「淡水渔业」2026-11-16 17:04《11月16日黄颡鱼、鳜鱼、加州鲈、黄鳝、乌鳢、泥鳅、斑点叉尾鮰批发价格》· <a class="plink" href="__URL_DS__" target="_blank" rel="noopener">📄 阅读原文（淡水渔业 11-16）</a> · 元/公斤 · 分市场批发价，仅供参考</div>
</div>
""".replace("__URL_DS__", URL_DS)

CARD_KSS = """
<div class="card" style="margin-top:14px">
  <h3>🔥 11月16日 · 腾氏水产商务网「高端水产 · 看上上报价㊺」：广东 1 斤上跌至 10 元、有价无市（元/斤）</h3>
  <div class="csub">「腾氏水产商务网」2026-11-16 18:58 发布看上上报价第 45 期（加州鲈塘口专题；10-26 ㊷、11-02 期后中间期次未采集，<b>隔期照录、不作两期比较</b>）。<b>广东 1 斤上 10 元/斤，较上周跌 0.2-0.3</b>，流通商称「有价无市」——降温后出鱼增加、饲料涨价、养殖户信心不足；8 成 1 斤上 9.8、5-6 成 1 斤上 9.3（要求条形好）。<b>环太湖与上周持平</b>：平 9 两 9.8-9.9、平 1.1 斤 10.5、平 1.2 斤最高 10.5-11；上市鱼少、市场跑不动，部分流通商到华中收大鱼。湖南华容 9 两起 10 持平（封顶价）、湖北武汉 9 两上 10 持平（实际跌 2-3 毛）、四川成都 1 斤上 10.5-11 持平。本卡为加州鲈塘口价专题，<b>无鳜鱼条目，如实留空</b>。</div>
  <table><thead><tr><th>加州鲈 产区</th><th>规格</th><th>11-16 塘口价（元/斤）</th><th>原文标注</th></tr></thead><tbody>
        <tr><td><span class="tag tag-lu">广东</span></td><td><span class="spec spec-s">1 斤上</span></td><td class="price"><b>10</b></td><td style="font-size:12px">▼ 跌 0.2-0.3 · 有价无市（上周 10.2-10.3）</td></tr>
        <tr><td><span class="tag tag-lu">广东</span></td><td><span class="spec spec-s">8 成 1 斤上</span></td><td class="price"><b>9.8</b></td><td style="font-size:12px">—</td></tr>
        <tr><td><span class="tag tag-lu">广东</span></td><td><span class="spec spec-s">5-6 成 1 斤上</span></td><td class="price"><b>9.3</b></td><td style="font-size:12px">要求条形好</td></tr>
        <tr><td><span class="tag tag-lu">环太湖</span></td><td><span class="spec spec-s">平 9 两</span></td><td class="price"><b>9.8-9.9</b></td><td style="font-size:12px">→ 与上周持平</td></tr>
        <tr><td><span class="tag tag-lu">环太湖</span></td><td><span class="spec spec-s">平 1.1 斤</span></td><td class="price"><b>10.5</b></td><td style="font-size:12px">→ 与上周持平</td></tr>
        <tr><td><span class="tag tag-lu">环太湖</span></td><td><span class="spec spec-s">平 1.2 斤</span></td><td class="price"><b>10.5-11</b></td><td style="font-size:12px">→ 最高价口径</td></tr>
        <tr><td><span class="tag tag-lu">湖南华容</span></td><td><span class="spec spec-s">9 两起</span></td><td class="price"><b>10</b></td><td style="font-size:12px">→ 持平 · 10 元为封顶价</td></tr>
        <tr><td><span class="tag tag-lu">湖北武汉</span></td><td><span class="spec spec-s">9 两上起</span></td><td class="price"><b>10</b></td><td style="font-size:12px">原文自述跌 2-3 毛、表值持平，两处照录</td></tr>
        <tr><td><span class="tag tag-lu">四川成都</span></td><td><span class="spec spec-s">1 斤上</span></td><td class="price"><b>10.5-11</b></td><td style="font-size:12px">→ 与上周持平</td></tr>
  </tbody></table>
  <div class="callout" style="margin-top:10px"><b>口径说明：</b>① 本卡为<b>加州鲈塘口价（元/斤）</b>，与强渔 11-16（江苏 1 斤起 10.5~11）、水产前沿 11-17（江苏 9 两上 10.5-11.5）、通威 11-13 全国塘口均价、白沙洲批发 9.90、盛阳本地批发 10~14 <b>渠道·规格·时间三重不同，多口径并存、禁止互减</b>。② 湖北行「表值 10 持平」与正文叙述「价格跌了 2-3 毛」<b>两处照录、不互相订正</b>（口径：表为 11-16 报价 vs 上周报表格、叙述为实际成交感受）。③ 与本系列 11-02 卡之间隔期（中间期次未采集），<b>只列本期数值与原文标注，不作两期比较</b>。④ 「看上上报价」系列与「腾氏一周鱼价播报（通威同源）」「海南卓越联合播报」为三个不同内容系列，分源登记。</div>
  <div class="legend">来源：微信公众号「腾氏水产商务网」2026-11-16 18:58《跌0.2-0.3元/斤！广东加州鲈"有价无市"，养殖户信心承压 ｜高端水产·看上上报价㊺》· <a class="plink" href="__URL_KSS__" target="_blank" rel="noopener">📄 阅读原文（看上上报价㊺ 11-16）</a> · 元/斤 · 塘口价，受条形均重影响仅供参考</div>
</div>
""".replace("__URL_KSS__", URL_KSS)

CARD_SY = """
<div class="card" style="margin-top:14px">
  <h3>🛒 2026.11.17 · 无锡盛阳食品城 水产类批发价（鳜鱼 / 鲈鱼）</h3>
  <div class="csub">用户提交「盛阳食品城」2026.11.17 水产类批发价表格截图：<b>鳜鱼（桂花）25~30 元/斤、鲈鱼 10~14 元/斤</b>，与 11.15 / 11.16 两期卡<b>逐项同值</b>，三期连续同区间、<b>原文未标「沿用」，如实并列照录、不推断涨跌、不重复计数</b>。其余水产行按约定不录入。</div>
  <table><thead><tr><th>品种</th><th>口径</th><th>11.17 批发价</th><th>备注</th></tr></thead><tbody>
        <tr><td><span class="tag tag-gui">鳜鱼</span>（桂花）</td><td><span class="spec spec-s">无锡盛阳 · 批发</span></td><td class="price"><b>25~30 元/斤</b></td><td style="font-size:12px">与 11.15 / 11.16 同值三连并列，未标沿用</td></tr>
        <tr><td><span class="tag tag-lu">鲈鱼</span></td><td><span class="spec spec-s">无锡盛阳 · 批发</span></td><td class="price"><b>10~14 元/斤</b></td><td style="font-size:12px">与 11.15 / 11.16 同值三连并列，未标沿用</td></tr>
  </tbody></table>
  <div class="callout" style="margin-top:10px"><b>口径说明：</b>① 本卡为<b>无锡本地销区批发价（元/斤）</b>，离宜兴官林最近的本地批发锚点；与塘口价（鳜康泰 11-16 江苏标鳜 24.5）、白沙洲批发（30.25 元/斤折算）、凌家塘周均价<b>多口径并存、禁止互减</b>。② 三日连续同值且原文未标「沿用」，<b>同值并列、不推断涨跌、不重复计数</b>，与明确标「11/7 沿用」的历史卡分开表述。③ 区间宽（鳜鱼 25~30 跨 5 元）为该市场统货口径，未给规格细分，照录。</div>
  <div class="legend">来源：「盛阳食品城」2026.11.17 水产类批发价表格 · 📷 用户截图核校录入 · 元/斤 · 本地批发参考价</div>
</div>
"""

# 强渔 11-16 卡 callout 追加海大 11-17 同源合并注（保留原 h3，不新建卡）
QY_APPEND_OLD = "等地段细节按约定不录入。</div>"
QY_APPEND_NEW = ("等地段细节按约定不录入。⑤ <b>同源合并（双出处）</b>：海大农牧 2026-11-17 17:55《\"同鱼不同价\"撕裂市场！谁在吞噬养殖利润？》"
                 "所列鳜鱼（鱼仔鳜 23-24 / 饲料鳜 19-22 / 江苏标鱼 25.5 / 安徽标鱼 25 / 湖南标鱼 24.5 / 湖北标鱼 26）与加州鲈"
                 "（佛山 8 两起 9 / 1 斤上 10.5、成都 1 斤起 10.5-11、湖北 9 两起 10、湖南华容 8 两起 10、郑州 1 斤起 10.5、江苏 1 斤起 10.5-11、湖州平 1 斤 11）"
                 "<b>与本卡逐项同值</b>，判为同一份报价的两个发布渠道（该号 11-13 期与 11-17 期同为转载口径），合并记入本卡、不重复计数；"
                 "海大原文「广东跌破 20 元且逐日走弱、湖北涨至 26」与强渔原文叙述<b>并存照录</b>。</div>")

CHIP_SUBS = [
    ("水产前沿特水鱼周报第38期（10-26 / 11-02 刊）",
     "水产前沿特水鱼周报（10-26 / 11-02 / 11-17 第39期）"),
    ("腾氏上上报价㊷加州鲈（10-26 / 11-02）",
     "腾氏上上报价加州鲈（10-26 ㊷ / 11-02 / 11-16 ㊺）"),
    ("淡水渔业批发价（10-21/10-23/10-27/10-29/11-02/11-06/11-10）",
     "淡水渔业批发价（10-21/10-23/10-27/10-29/11-02/11-06/11-10/11-16）"),
    ("凌家塘一周行情（10-25~31 / 11-01~07）",
     "凌家塘一周行情（10-25~31 / 11-01~07 / 11-08~14）"),
    ("盛阳食品城（10.27/10.28/10.30/11.2/11.3/11.4/11.5/11.6/11.8/11.9/11.10/11.15/11.16批发）",
     "盛阳食品城（10.27/10.28/10.30/11.2/11.3/11.4/11.5/11.6/11.8/11.9/11.10/11.15/11.16/11.17批发）"),
    ("科学养鱼分市场批发价（11-05OCR/11-10合并/11-13正文）",
     "科学养鱼分市场批发价（11-05OCR/11-10合并/11-13正文/11-17截图）"),
    ("海大农牧 塘头聚焦（11-02 广东加州鲈 / 11-06 四产区塘头价 / 11-09 江浙塘头聚焦 / 11-13 四产区塘头价）",
     "海大农牧 塘头聚焦（11-02 广东加州鲈 / 11-06 四产区塘头价 / 11-09 江浙塘头聚焦 / 11-13 四产区塘头价 / 11-17 同值并入强渔周报）"),
    ("渔知识指导日报（11-03/11-05/11-06/11-13/11-17）",
     "渔知识指导日报（11-03/11-05/11-06/11-13/11-17）+ 渔飞鱼水产·明日预报（11-18）"),
]

CARDS_AT = [
    ("qyqy", CARD_QYQY),
    ("ljt", CARD_LJT),
    ("yfy", CARD_YFY),
    ("kx", CARD_KX),
    ("ds", CARD_DS),
    ("kss", CARD_KSS),
    ("sy", CARD_SY),
]


def balance(text):
    """精确标签统计：<tag 后必须跟空白或 >。"""
    return {t: len(re.findall(r"<" + t + r"(?=[\s>])", text)) - text.count("</" + t + ">")
            for t in ("section", "div", "table", "thead", "tbody", "tr", "td", "th", "b")}


def insert_before(html, anchor, block):
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
    # 注意插入顺序：kx（科学养鱼截图卡）先插到 11-13 卡前，ds（淡水渔业卡）再插到截图卡前
    for key, block in CARDS_AT:
        html = insert_before(html, ANCHORS[key], block)
        print("[OK] 已插入卡组:", key)
    # 强渔卡 callout 追加海大同源合并注
    assert html.count(QY_APPEND_OLD) == 1, ("强渔 callout 追加点", html.count(QY_APPEND_OLD))
    html = html.replace(QY_APPEND_OLD, QY_APPEND_NEW, 1)
    print("[OK] 强渔 11-16 卡追加海大 11-17 同源合并注")
    for old, new in CHIP_SUBS:
        assert html.count(old) == 1, ("chip", old[:46], html.count(old))
        html = html.replace(old, new, 1)
    print("[OK] chip 快览 8 处来源列举同步")

    after = balance(html)
    assert before == after, f"标签配平差值变化：{before} → {after}"
    for g in GUARDS:
        assert html.count(g) == 1, ("guard", g, html.count(g))
    open(HTML, "w", encoding="utf-8").write(html)
    print("[OK] 写盘完成 · 字节数", len(html.encode("utf-8")), "· 标签差值", after)
    return 0


if __name__ == "__main__":
    sys.exit(main())
