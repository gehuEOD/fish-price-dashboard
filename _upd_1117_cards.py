#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""2026-11-17 批次：7 链接 + 3 截图判定 → 8 张新卡 + chip 快览同步（幂等）。

链接判定：
  1. 全国渔业价格《渔飞鱼水产行情日报（2026年11月17日）》（发布 11-17 08:50）—— 录入。
     白沙洲官网已更新到 11/15：鳜鱼 ≥750g 58.50→60.50 元/公斤＝30.25 元/斤（+1.00/+3.4%，连涨第四天）、
     500~750g 56.00→58.00、250~500g 46.50→47.50 三档全涨；鲈鱼 ≥500g 20.50→19.80＝9.90（-3.4%）、
     <500g 18.50→19.00＝9.50（+0.25）；21food 11/16 ≥750g 60.5 平稳；加州鲈产地均价 11.69 平（11/16）。
  2. 海大农牧 11-13《全球最新塘头价》—— 与看板已有卡同 URL（DaTlPM_gUvRACIAlGHf4VA），重复，跳过。
  3. 渔知识指导《全国最新水产行情日报 2026-11-17》（发布 11-17 05:55）—— 录入。一线塘头表仅 3 项相关：
     鳜鱼武汉 25.5 持平 / 宣城 25.0 持平、加州鲈佛山 1斤上 10.6 ↑0.1；产地均价 16 日 11.07 连两日回升。
  4. 水产养殖网（强渔）《涨跌交织！广东鳜跌至19元、加州鲈横盘》（11-16 16:53）—— 录入。
     鳜鱼：广东鱼仔鳜 23-24 / 饲料鳜 19-22、江苏标鱼 25.5、安徽 25、湖南 24.5、湖北 26；
     加州鲈横盘 9-11 区间，江苏 1斤起 10.5~11。
  5. 兴渔派-鳜鱼通《11月16日鳜鱼价格行情丨鳜康泰特约》（11-16 17:59）—— 录入。正文 8 项
     （小鳜 19 / 标鳜 23 / 中鳜 20 / 鄂 24 / 皖 24 / 赣 25.5 / 湘 24.5 / 苏 24.5），原文自述「保持稳定」，
     微信摘要「广东、湖南鳜价小跌，多地鳜价持稳」——两处照录。
  6. 渔有福水产《鳜鱼行情播报｜11月16日》（11-16 09:01）—— 录入。「广东标鳜、中鳜下调 0.5，
     湖南同步下跌 0.5，其余主产区稳住」；8 项与鳜康泰 11-16 逐项同值。
  7. 渔无忧在线《最新水产行情预报》（11-16 14:28，次日 11-17 预测口径）—— 录入。
     白沙洲 11/15 鲈鱼 ≥500g 19.80 元/公斤≈9.90、<500g 9.50；无鳜鱼条目，留空。

截图判定：
  A. 视频号「水产养殖服务于老师」2026.11.17 全国鱼价 —— 录入。鳜鱼 1斤上 23~26 ↑小幅上涨、
     加州鲈 1斤上 10.0~11 基本持平；封面与描述日期一致（11.17）。
  B. 视频号「互联惠农小洁」11月17日 塘口价 —— 录入。鲈鱼 0.8-1.2斤 12.0~13.3、
     鳜鱼 0.8-1.2斤 33.0~34.5（该号全国参考区间口径，与服务于老师同日 23~26 差异大，各自照录不互减）。
  C. 盛阳食品城 640.png —— 表头日期 2026.11.16、数值与昨日已录 11.16 卡一致，重复，跳过。

口径：只录鳜鱼 / 加州鲈；多口径禁止互减；同值未标「沿用」不推断涨跌；跨期核校仅限
同市场同规格且原文明确给出涨跌；隔期（中间有未采集期次）只列本期数值与原文箭头。

V2 桥接注意：
  - 鳜康泰 11-16 与渔有福 11-16 同日期：GUI_POND_SPECS 按声明序稳定排序取鳜康泰，
    故鳜康泰卡 csub 不得含「下跌 / 上涨 / 未给涨跌」（原文自述「保持稳定」→ trend=flat）。
  - 强渔 11-16 卡 tbody#0=鳜鱼表、tbody#1=加州鲈表（region_first），tbody#1 含江苏 1斤起
    10.5~11 绝对价 → V2 加州鲈 KPI 更新到 11-16 江苏 10.5（assert any(local) 可满足）。
  - 线索容量 12：11-17×4（日报/渔知识/小洁/于老师）+ 11-16×5（盛阳/强渔/鳜康泰/渔有福/渔无忧）
    + 11-13×2 + 11-12×1 = 12，恰好容纳，无需扩容（11-10 及更旧行自然淘汰）。
"""
import re
import sys

HTML = "鳜鱼鲈鱼价格看板.html"
URL_DAILY = "https://mp.weixin.qq.com/s/iXb6Z52-adVZk7ogBeBitA"
URL_YZ = "https://mp.weixin.qq.com/s/MhV7IvztJFnxbPmkmaqHpA"
URL_QY = "https://mp.weixin.qq.com/s/Yq_c2RkGRXD5qbJGT9wPEA"
URL_GKT = "https://mp.weixin.qq.com/s/X6MV_ZC1GEVYXdI-5Y18hQ"
URL_YF = "https://mp.weixin.qq.com/s/X3dA2GDleRsxFE67UVo1xg"
URL_WY = "https://mp.weixin.qq.com/s/d_mt9j-9y-aXMCq-m_0dsg"

ANCHORS = {
    "daily": "📰 全国渔业价格 ·《渔飞鱼水产行情日报 2026-11-16》",
    "gkt": "🐟 鳜康泰特约 · 全国鳜鱼报价（2026-11-14",
    "yf": "🐟 11月13日 · 渔有福水产",
    "ywy": "预报 📅 渔无忧在线 ·《最新水产行情预报》（发布 11月13日 16:06",
    "qy": "📰 2026-11-09 · 水产养殖网（强渔）",
    "xj": "🎬 11月15日 · 视频号「互联惠农小洁」",
    "ysl": "🎬 11月13日 · 视频号「水产养殖服务于老师」",
}
GUARDS = [
    "渔飞鱼水产行情日报 2026-11-17",
    "《全国最新水产行情日报 2026-11-17》",
    "鳜康泰特约 · 全国鳜鱼报价（2026-11-16",
    "渔有福水产 鳜鱼塘口报价（粤湘回落 0.5",
    "（发布 11月16日 14:28",
    "📰 2026-11-16 · 水产养殖网（强渔）",
    "🎬 11月17日 · 视频号「互联惠农小洁」",
    "🎬 11月17日 · 视频号「水产养殖服务于老师」",
]

CARD_DAILY = """
<div class="card" style="margin-top:14px">
  <h3>📰 全国渔业价格 ·《渔飞鱼水产行情日报 2026-11-17》（发布 11-17 08:50 · 白沙洲 11/15 · 鳜鱼三档全涨追平产区 30.25 / 鲈鱼大规格松动）</h3>
  <div class="csub">「全国渔业价格」11-17 08:50 发布 11-17 期日报。原文自述「明日 21 品种呈 1 涨 5 跌、15 行持平或沿用」，<b>白沙洲官网今天已更新到 11/15、表内白沙洲各行换成 15 日值</b>。本看板只跟踪鳜鱼 / 加州鲈两类：<b>鳜鱼 ≥750g 58.50→60.50 元/公斤＝30.25 元/斤（+1.00 元/+3.4%）、500~750g 56.00→58.00（+1.00）、250~500g 46.50→47.50（+0.50）三档全涨</b>，原文判断「昨天报 29.25 的今天能报 30.25，30 元/斤整数关口已站住，连涨第四天」；<b>鲈鱼 ≥500g 20.50→19.80＝9.90 元/斤（-0.35/-3.4%）、&lt;500g 18.50→19.00＝9.50（+0.25）</b>；21food 11/16 ≥750g 60.5 元/公斤页面由「上升」转「平稳」；<b>加州鲈产地均价 11.69 元/斤平稳（11/16）</b>。</div>
  <table><thead><tr><th>品种</th><th>口径 · 来源</th><th>价格</th><th>原文标注</th></tr></thead><tbody>
        <tr><td><b>鳜鱼</b></td><td><span class="spec spec-s">武汉白沙洲批发 · ≥750g（11/15）</span></td><td class="price"><b>58.50 → 60.50 元/公斤 ≈ 30.25 元/斤</b></td><td style="font-size:12px">▲ +1.00 元/+3.4% · 连涨第四天</td></tr>
        <tr><td><b>鳜鱼</b></td><td><span class="spec spec-s">武汉白沙洲批发 · 500~750g（11/15）</span></td><td class="price"><b>56.00 → 58.00 元/公斤 ≈ 29.00 元/斤</b></td><td style="font-size:12px">▲ +1.00 元</td></tr>
        <tr><td><b>鳜鱼</b></td><td><span class="spec spec-s">武汉白沙洲批发 · 250~500g（11/15）</span></td><td class="price"><b>46.50 → 47.50 元/公斤 ≈ 23.75 元/斤</b></td><td style="font-size:12px">▲ +0.50 元</td></tr>
        <tr><td><b>鳜鱼</b></td><td><span class="spec spec-s">21food 产区 · ≥750g（11/16）</span></td><td class="price"><b>60.50 元/公斤</b></td><td style="font-size:12px">平稳（页面由「上升」转「平稳」）</td></tr>
        <tr><td><b>鲈鱼</b></td><td><span class="spec spec-s">武汉白沙洲批发 · ≥500g（11/15）</span></td><td class="price"><b>20.50 → 19.80 元/公斤 ≈ 9.90 元/斤</b></td><td style="font-size:12px">▼ -0.35 元/-3.4%</td></tr>
        <tr><td><b>鲈鱼</b></td><td><span class="spec spec-s">武汉白沙洲批发 · &lt;500g（11/15）</span></td><td class="price"><b>18.50 → 19.00 元/公斤 ≈ 9.50 元/斤</b></td><td style="font-size:12px">▲ +0.25 元（原文「反而」）</td></tr>
        <tr><td><b>加州鲈</b></td><td><span class="spec spec-s">惠农产地均价 · 鲜活（11/16）</span></td><td class="price"><b>11.69 元/斤</b></td><td style="font-size:12px">平稳 · 原文另给淡水鲈 12.31（+2.36%）</td></tr>
  </tbody></table>
  <div class="callout" style="margin-top:12px"><b>跨期核校 / 多口径说明：</b>① 与 11-16 期卡为连续两期、同市场同规格，白沙洲鳜鱼 ≥750g 11/14 值 58.50（上期沿用值）→ 本期 11/15 60.50，原文明确给出「58.50→60.50（+1.00/+3.4%）」，<b>按原文照录</b>；鲈鱼 ≥500g 22.50（11/13）→20.50（11/14）→19.80（11/15）链条中本期段原文给出，照录。② 产区 vs 批发：21food 11/16 60.5 与白沙洲 11/15 60.50 两端齐平，原文称「产区涨价终于传导到批发端」，<b>按原文照录</b>；渠道间不作互减。③ 本卡为<b>批发 / 产区参考价（元/公斤，折元/斤仅供阅读）</b>，与鳜康泰 11-16 塘口报价（江苏标鳜 24.5 元/斤）、强渔 11-16 周报、科学养鱼 11-13 分市场批发、视频号全国参考区间、渔无忧 11-16 次日预测<b>规格·时间·渠道三重不同，多口径并存、禁止互减</b>；原文「鳜鱼按 30.25 报、鲈鱼 9.90」为卖鱼谈判建议，<b>不作为价格数据录入</b>。④ 大小规格走势相反（≥500 跌、&lt;500 反涨 0.25），原文称「大小规格差从 1 元缩到 0.4 元」，照录。</div>
  <div class="legend">来源：微信公众号「全国渔业价格」11-17 08:50《渔飞鱼水产行情日报（2026年11月17日）鳜鱼补涨1元 追平30.25 黄颡一天掉1元 全市场最惨》· <a class="plink" href="__URL_DAILY__" target="_blank" rel="noopener">📄 阅读原文（日报 11-17）</a> · 白沙洲 11/15 + 21food 11/16 · 元/公斤 / 元/斤 多口径，仅供参考</div>
</div>
""".replace("__URL_DAILY__", URL_DAILY)

CARD_YZ = """
<div class="card" style="margin-top:14px">
  <h3>🐟 渔飞鱼·董小月 ·《全国最新水产行情日报 2026-11-17》（发布 11-17 05:55 · 一线塘头表鄂皖鳜持平 / 佛山鲈 ↑0.1）</h3>
  <div class="csub">「渔知识指导」（渔飞鱼·董小月）2026-11-17 05:55 发布。本期一线塘头表与本看板相关仅 <b>3 项</b>：鳜鱼湖北武汉标鳜1斤上 <b>25.5 持平</b>、安徽宣城标鳜 <b>25.0 持平</b>；加州鲈广东佛山1斤上 <b>10.6 ↑0.1</b>。正文另给：<b>加州鲈产地均价 16 日 11.07 元/斤</b>（11/13 11.23 → 15 日 11.00 → 16 日 11.07，连两日回升；7 日均价 10.90、最低 10.82）；区域价差段：广东塘头 1斤上 10.5~10.6 vs 浙江湖州平打 1 斤 13.5、江苏苏州 9 成以上 12.1、四川成都 1 斤上 11.0；鳜鱼武汉销区 16 日三档 60.50 / 58.00 / 47.50 元/公斤（与 11-16 日报 21food 同源同值），塘头广东佛山 1 斤上 31.5 元/斤（原文如此、与该号 11-13 卡同值）、江苏南通统货 26.0、安徽宣城标鳜 25.0、湖北武汉标鳜 25.5。</div>
  <table><thead><tr><th>品种 / 地区</th><th>规格</th><th>塘头价（元/斤）</th><th>原文标注</th></tr></thead><tbody>
        <tr><td><span class="tag tag-gui">鳜鱼</span> 湖北武汉</td><td><span class="spec spec-s">标鳜 1 斤上</span></td><td class="price"><b>25.5</b></td><td style="font-size:12px">持平</td></tr>
        <tr><td><span class="tag tag-gui">鳜鱼</span> 安徽宣城</td><td><span class="spec spec-s">标鳜</span></td><td class="price"><b>25.0</b></td><td style="font-size:12px">持平</td></tr>
        <tr><td><span class="tag tag-lu">加州鲈</span> 广东佛山</td><td><span class="spec spec-s">1 斤上</span></td><td class="price"><b>10.6</b></td><td style="font-size:12px">▲ +0.1</td></tr>
        <tr><td><span class="tag tag-lu">加州鲈</span> 产地均价（16 日）</td><td><span class="spec spec-s">鲜活</span></td><td class="price"><b>11.07</b></td><td style="font-size:12px">连两日回升（11/13 11.23 → 11/15 11.00 → 11/16 11.07）</td></tr>
  </tbody></table>
  <div class="callout" style="margin-top:10px"><b>隔期并列 / 口径说明：</b>① 与该号 11-13 卡之间 11-14~11-16 未采集、隔多期，<b>只列本期数值与原文箭头，不作两期比较</b>；鳜鱼两项与 11-13 卡同值且原文标「持平」，按原文照录。② 本期塘头表鲈鱼行为「佛山 1 斤上 10.6」，11-13 卡为「佛山 9 成以上 11.9 / 苏州 12.1 / 成都 12.5 / 湖州 13.5」，<b>规格口径不同、不可直接对比</b>。③ 佛山鳜鱼「1 斤上 31.5 元/斤」为<b>原文如此</b>（该号 11-13 卡同值），与鳜康泰 11-16 佛山标鳜 23、白沙洲批发 30.25 规格渠道不同，<b>多口径并存、不互减、不互相订正</b>。④ 原文行情判断「涨价主力｜加州鲈·草鱼」属叙述，不作数据录入。</div>
  <div class="legend">来源：微信公众号「渔知识指导」（渔飞鱼·董小月）2026-11-17 05:55《全国最新水产行情日报 2026年11月17日 星期二》· <a class="plink" href="__URL_YZ__" target="_blank" rel="noopener">📄 阅读原文（日报 11-17）</a> · 元/斤 · 塘头参考价，仅供参考</div>
</div>
""".replace("__URL_YZ__", URL_YZ)

CARD_GKT = """
<div class="card" style="margin-top:14px">
  <h3>🐟 鳜康泰特约 · 全国鳜鱼报价（2026-11-16 · 元/斤 · 8 项 · 原文自述保持稳定）</h3>
  <div class="csub">据「兴渔派-鳜鱼通」2026-11-16 17:59《11月16日鳜鱼价格行情丨鳜康泰特约·全国鳜鱼报价》：原文自述<b>「11月16日，鳜价保持稳定」</b>；正文文字给出 8 项塘口报价（元/斤），本期未附对照表格，微信摘要另述「广东、湖南鳜价小跌，多地鳜价持稳」——<b>正文与摘要两处表述均按原文照录</b>。本卡为塘口报价口径；<b>本篇无加州鲈条目，如实留空</b>。</div>
  <table><thead><tr><th>品种 / 产区</th><th>规格</th><th>11-16 塘口价（元/斤）</th><th>原文说明</th></tr></thead><tbody>
        <tr><td><span class="tag tag-gui">广东</span> 小鳜</td><td><span class="spec spec-s">0.8 斤以下</span></td><td class="price"><b>19</b></td><td style="font-size:12px">原文自述保持稳定</td></tr>
        <tr><td><span class="tag tag-gui">广东</span> 标鳜</td><td><span class="spec spec-s">0.8~1.5 斤</span></td><td class="price"><b>23</b></td><td style="font-size:12px">原文自述保持稳定</td></tr>
        <tr><td><span class="tag tag-gui">广东</span> 中鳜</td><td><span class="spec spec-s">1.5-2 斤</span></td><td class="price"><b>20</b></td><td style="font-size:12px">原文自述保持稳定</td></tr>
        <tr><td><span class="tag tag-gui">湖北</span> 标鳜</td><td><span class="spec spec-s">标鳜</span></td><td class="price"><b>24</b></td><td style="font-size:12px">—</td></tr>
        <tr><td><span class="tag tag-gui">安徽</span> 标鳜</td><td><span class="spec spec-s">标鳜</span></td><td class="price"><b>24</b></td><td style="font-size:12px">—</td></tr>
        <tr><td><span class="tag tag-gui">江西</span> 标鳜</td><td><span class="spec spec-s">标鳜</span></td><td class="price"><b>25.5</b></td><td style="font-size:12px">—</td></tr>
        <tr><td><span class="tag tag-gui">湖南</span> 标鳜</td><td><span class="spec spec-s">标鳜</span></td><td class="price"><b>24.5</b></td><td style="font-size:12px">—</td></tr>
        <tr><td><span class="tag tag-gui">江苏</span> 标鳜</td><td><span class="spec spec-s">标鳜</span></td><td class="price"><b>24.5</b></td><td style="font-size:12px">—</td></tr>
  </tbody></table>
  <div class="callout" style="margin-top:12px"><b>同值并列 / 多口径说明：</b>① 与看板 <b>11-16「渔有福水产」卡 8 项逐项同值</b>（小鳜 19、标鳜 23、中鳜 20、鄂 24、皖 24、赣 25.5、湘 24.5、苏 24.5）。渔有福原文明确给出「广东标鳜、中鳜下调 0.5 元/斤，湖南同步下跌 0.5 元/斤，其余主产区稳住」，本卡正文仅自述「保持稳定」、摘要称「广东、湖南鳜价小跌」——<b>三处表述不同但均按原文照录、不互相覆盖</b>；两卡之间<b>不重复计数、不作两期比较</b>。② 与 11-14 本系列卡之间隔 11-15 期（该号 11-15 期未采集），<b>隔期只列本期数值，不作两期比较</b>。③ 江苏标鳜 24.5 在鳜康泰 11-14（日持平/周 ↓0.5）、渔有福 11-13（未逐项给说明）、腾氏 11-12（较上周跌 1）与本卡（自述稳定）涨跌口径各异，<b>按原文各自照录，不互减、不互相订正</b>。④ 本卡为<b>塘口报价（元/斤）</b>，与白沙洲批发（30.25 元/斤折算）、科学养鱼分市场批发、强渔周报、视频号全国区间<b>多口径并存、禁止互减</b>。</div>
  <div class="legend">来源：微信公众号「兴渔派-鳜鱼通」2026-11-16 17:59《11月16日鳜鱼价格行情丨鳜康泰特约·全国鳜鱼报价》· <a class="plink" href="__URL_GKT__" target="_blank" rel="noopener">📄 阅读原文</a> · 元/斤 · 塘口报价 · 正文文字核校录入</div>
</div>
""".replace("__URL_GKT__", URL_GKT)

CARD_YF = """
<div class="card" style="margin-top:14px">
  <h3>🐟 11月16日 · 渔有福水产 鳜鱼塘口报价（粤湘回落 0.5 · 8 产区 · 元/斤）</h3>
  <div class="csub">据「渔有福水产」2026-11-16 09:01《鳜鱼行情播报｜11 月 16 日：粤湘鳜价小幅回落，虹彩病毒防控不能松》：原文自述<b>「局部回落、多数地区持稳——广东标鳜、中鳜下调 0.5 元/斤，湖南同步下跌 0.5 元/斤，其余主产区价格暂时稳住」</b>。原文提醒：<b>当前正是虹彩病毒高发窗口期</b>，昼夜温差大、水质不稳、鱼体应激时风险直线上升，核心思路为减少应激、稳住水质、增强鱼体抗逆、切断传播路径。</div>
  <table><thead><tr><th>品种 / 产区</th><th>规格</th><th>11-16 塘口价（元/斤）</th><th>原文标注</th></tr></thead><tbody>
        <tr><td><span class="tag tag-gui">广东</span> 小鳜</td><td><span class="spec spec-s">0.8 斤以下</span></td><td class="price"><b>19</b></td><td style="font-size:12px">约 19</td></tr>
        <tr><td><span class="tag tag-gui">广东</span> 标鳜</td><td><span class="spec spec-s">0.8~1.5 斤</span></td><td class="price"><b>23</b></td><td style="font-size:12px">▼ 下调 0.5</td></tr>
        <tr><td><span class="tag tag-gui">广东</span> 中鳜</td><td><span class="spec spec-s">1.5~2 斤</span></td><td class="price"><b>20</b></td><td style="font-size:12px">▼ 下调 0.5</td></tr>
        <tr><td><span class="tag tag-gui">湖北</span> 标鳜</td><td><span class="spec spec-s">标鳜</span></td><td class="price"><b>24</b></td><td style="font-size:12px">稳住</td></tr>
        <tr><td><span class="tag tag-gui">安徽</span> 标鳜</td><td><span class="spec spec-s">标鳜</span></td><td class="price"><b>24</b></td><td style="font-size:12px">稳住</td></tr>
        <tr><td><span class="tag tag-gui">江西</span> 标鳜</td><td><span class="spec spec-s">标鳜</span></td><td class="price"><b>25.5</b></td><td style="font-size:12px">稳住</td></tr>
        <tr><td><span class="tag tag-gui">湖南</span> 标鳜</td><td><span class="spec spec-s">标鳜</span></td><td class="price"><b>24.5</b></td><td style="font-size:12px">▼ 同步下跌 0.5</td></tr>
        <tr><td><span class="tag tag-gui">江苏</span> 标鳜</td><td><span class="spec spec-s">标鳜</span></td><td class="price"><b>24.5</b></td><td style="font-size:12px">稳住</td></tr>
  </tbody></table>
  <div class="callout" style="margin-top:10px"><b>口径说明：</b>① 8 项与鳜康泰 11-16 卡<b>逐项同值</b>，涨跌表述不同（本卡明确粤湘 ↓0.5、鳜康泰自述稳定），<b>按原文各自照录、不互相覆盖、不重复计数</b>。② 与 11-13 本系列卡之间 11-14~11-15 未采集、隔期，<b>不作两期比较</b>；原文「下调 0.5 / 下跌 0.5」未给基准期日期，<b>只录箭头不倒推基准值</b>。③ 广东作为流通大省价格下滑会慢慢传导、存塘可结合规格成本择机出鱼——属原文建议，不作数据录入。④ 塘口口径与白沙洲批发（鳜鱼 ≥750g 30.25 元/斤折算）、强渔周报（江苏标鱼 25.5）、视频号区间<b>多口径并存、禁止互减</b>。</div>
  <div class="legend">来源：微信公众号「渔有福水产」2026-11-16 09:01《鳜鱼行情播报｜11 月 16 日：粤湘鳜价小幅回落，虹彩病毒防控不能松》· <a class="plink" href="__URL_YF__" target="_blank" rel="noopener">📄 阅读原文</a> · 元/斤 · 塘口报价 · 文字核校录入</div>
</div>
""".replace("__URL_YF__", URL_YF)

CARD_WY = """
<div class="card" style="margin-top:14px">
  <h3>预报 📅 渔无忧在线 ·《最新水产行情预报》（发布 11月16日 14:28 · 次日 11月17日 周二预测口径）</h3>
  <div class="csub">「渔无忧在线」2026-11-16 14:28 发布，预测 11-17（周二）口径。原文整体趋势：「周二工作日批发交易正常、周内需求平稳延续；<b>华中产地鲈鱼、黑鱼、黄颡大规格较上周五小幅回落</b>，草鱼供强需弱」。鲈鱼专项：<b>武汉白沙洲 11/15 鲈鱼 ≥500g 均价 19.80 元/公斤（约 9.90 元/斤）、&lt;500g 9.50 元/斤</b>；原文称「较上周五 22.50 元/公斤回落约一成，短期价格走弱，预计周内价格以震荡偏弱为主」。<b>本篇无鳜鱼条目，如实留空</b>。</div>
  <table><thead><tr><th>品种</th><th>口径 · 来源</th><th>价格</th><th>原文标注</th></tr></thead><tbody>
        <tr><td><b>鲈鱼</b></td><td><span class="spec spec-s">武汉白沙洲批发 · ≥500g（11/15 实测）</span></td><td class="price"><b>19.80 元/公斤 ≈ 9.90 元/斤</b></td><td style="font-size:12px">较上周五 22.50 回落约一成（原文口径）</td></tr>
        <tr><td><b>鲈鱼</b></td><td><span class="spec spec-s">武汉白沙洲批发 · &lt;500g（11/15 实测）</span></td><td class="price"><b>9.50 元/斤</b></td><td style="font-size:12px">原文预测表「高」行</td></tr>
  </tbody></table>
  <div class="callout" style="margin-top:10px"><b>口径提示：</b>① 本卡为<b>预报号引用实测 + 次日预测</b>双口径：白沙洲 11/15 实测值与 11-17 日报卡白沙洲行<b>同源同值（≥500g 9.90）</b>，并列照录、不重复计数；「较上周五 22.50 回落约一成」为原文自比口径，<b>照录、不与日报卡 22.50→20.50→19.80 链条互相订正</b>。② 预测结论「周内震荡偏弱、达规格按周内节奏出塘、不压塘惜售」属原文建议。③ 与渔无忧 11-13 卡（11-14 次日预测口径）之间隔 11-14~11-15 期未采集，<b>隔期并列、不作两期比较、不作命中率评价</b>。④ 与产地均价（11.69）、佛山塘头（10.6/11.0）、视频号区间<b>多口径并存、禁止互减</b>。</div>
  <div class="legend">来源：微信公众号「渔无忧在线」2026-11-16 14:28《最新水产行情预报》· <a class="plink" href="__URL_WY__" target="_blank" rel="noopener">📄 阅读原文</a> · 白沙洲 11/15 + 次日预测口径 · 仅供参考</div>
</div>
""".replace("__URL_WY__", URL_WY)

CARD_QY = """
<div class="card" style="margin-top:14px">
  <h3>📰 2026-11-16 · 水产养殖网（强渔）· 特水鱼周报：广东鳜跌至 19 元、加州鲈横盘 9-11 元区间</h3>
  <div class="csub">据「水产养殖网（强渔）」2026-11-16 16:53（安徽）《涨跌交织！广东鳜跌至19元、加州鲈横盘，黄颡鱼黑鱼鮰鱼各藏变数》：本周「同鱼不同价」突出——<b>鳜鱼产区涨跌分化：广东跌破 20 元逐日走弱（冷库持续收鱼）、湖北冲高至 26 元</b>，原文引流通商「高价并不代表利润丰厚：湖北存塘紧缺需从广东调货，长途运输叠加流通成本压缩利润」；<b>饲料鳜 19 元已临近成本红线</b>。<b>加州鲈横盘微跌：自 10 月底一轮上涨后横盘近一月、卡在 9-11 元区间多空博弈</b>，大规格存塘逐步消耗、新鱼规格普遍偏小、终端消费偏弱。<b>本卡只列鳜鱼 / 加州鲈两类</b>（黄颡 / 黑鱼 / 鮰鱼等按约定不录入）。</div>
  <table><thead><tr><th>品种 / 产区</th><th>规格 / 交易环节</th><th>塘口价（元/斤）</th><th>原文要点</th></tr></thead><tbody>
        <tr><td><span class="tag tag-gui">广东</span> 鱼仔鳜</td><td>鱼仔鳜</td><td class="price"><b>23~24</b></td><td style="font-size:12px">跌破 20 指饲料鳜低档、鱼仔鳜逐日走弱</td></tr>
        <tr><td><span class="tag tag-gui">广东</span> 饲料鳜</td><td>饲料鳜</td><td class="price"><b>19~22</b></td><td style="font-size:12px">19 元临近成本红线、冷库持续收鱼</td></tr>
        <tr><td><span class="tag tag-gui">江苏</span> 标鱼</td><td>标鱼</td><td class="price"><b>25.5</b></td><td style="font-size:12px">离宜兴官林最近的分产区口径</td></tr>
        <tr><td><span class="tag tag-gui">安徽</span> 标鱼</td><td>标鱼</td><td class="price"><b>25</b></td><td style="font-size:12px">—</td></tr>
        <tr><td><span class="tag tag-gui">湖南</span> 标鱼</td><td>标鱼</td><td class="price"><b>24.5</b></td><td style="font-size:12px">—</td></tr>
        <tr><td><span class="tag tag-gui">湖北</span> 标鱼</td><td>标鱼</td><td class="price"><b>26</b></td><td style="font-size:12px">冲高、存塘紧缺需从广东调货</td></tr>
  </tbody></table>
  <table style="margin-top:12px"><thead><tr><th>产区</th><th>规格 / 口径</th><th>塘口价（元/斤）</th><th>原文要点</th></tr></thead><tbody>
        <tr><td>广东佛山</td><td>8 两起</td><td class="price"><b>9 左右</b></td><td style="font-size:12px">—</td></tr>
        <tr><td>广东佛山</td><td>1 斤以上</td><td class="price"><b>10.5</b></td><td style="font-size:12px">—</td></tr>
        <tr><td>四川成都</td><td>1 斤起</td><td class="price"><b>10.5</b></td><td style="font-size:12px">—</td></tr>
        <tr><td>湖北</td><td>9 两起</td><td class="price"><b>10</b></td><td style="font-size:12px">—</td></tr>
        <tr><td>湖南华容</td><td>8 两起</td><td class="price"><b>10</b></td><td style="font-size:12px">—</td></tr>
        <tr><td>河南郑州</td><td>1 斤起</td><td class="price"><b>10.5 左右</b></td><td style="font-size:12px">—</td></tr>
        <tr><td>江苏</td><td>1 斤起</td><td class="price"><b>10.5~11</b></td><td style="font-size:12px">离宜兴官林最近的分产区口径</td></tr>
        <tr><td>浙江湖州</td><td>平 1 斤</td><td class="price"><b>11</b></td><td style="font-size:12px">—</td></tr>
  </tbody></table>
  <div class="callout" style="margin-top:10px"><b>口径提示：</b>① 本期原文<b>未给上周逐点基准价与涨跌说明</b>，「跌破 20 / 冲高 26 / 横盘」均为原文叙述，<b>不与 11-09 强渔卡或其他源逐条相减</b>，两期卡并列呈现。② 广东「鱼仔鳜 / 饲料鳜」与分省「标鱼」为不同交易环节与规格口径，<b>并列照录、禁止互减</b>。③ 加州鲈 8 两起 / 9 两起 / 1 斤起 / 平 1 斤规格不同且产区不同，与通威 11-13 全国塘口均价、渔知识 11-17 塘头表（佛山 1 斤上 10.6）、产地均价 11.07、渔无忧白沙洲 9.90、盛阳销地批发 10~14、视频号区间<b>只看方向不看绝对值</b>。④ 原文「福建苗种投放基本收尾、河南受南阳需求拉动」等地段细节按约定不录入。</div>
  <div class="legend">来源：微信公众号「水产养殖网（强渔）」2026-11-16 16:53（安徽）《涨跌交织！广东鳜跌至19元、加州鲈横盘，黄颡鱼黑鱼鮰鱼各藏变数》· <a class="plink" href="__URL_QY__" target="_blank" rel="noopener">📄 阅读原文（强渔 11-16 周报）</a> · 元/斤 · 塘口价，受规格卖相影响仅供参考</div>
</div>
""".replace("__URL_QY__", URL_QY)

CARD_XJ = """
<div class="card" style="margin-top:14px">
  <h3>🎬 11月17日 · 视频号「互联惠农小洁」全国参考塘口价（元/斤）</h3>
  <div class="csub">视频号「互联惠农小洁」11月17日发布，封面「11月17日！全国最新塘口鱼价出炉」。原文自述<b>「以上为全国参考均价，各地行情有差异」</b>；本卡<b>只列鳜鱼 / 鲈鱼两类</b>，其余 6 品种（草鱼 / 鲫鱼 / 鲤鱼 / 黄骨鱼 / 黑鱼 / 青鱼）按约定不录入。截图核校录入。</div>
  <table><thead><tr><th>品种</th><th>规格</th><th>全国参考塘口价（元/斤）</th></tr></thead><tbody>
        <tr><td><span class="tag tag-gui">鳜鱼</span></td><td><span class="spec spec-s">0.8-1.2 斤</span></td><td class="price"><b>33.0~34.5</b></td></tr>
        <tr><td><span class="tag tag-lu">鲈鱼</span></td><td><span class="spec spec-s">0.8-1.2 斤</span></td><td class="price"><b>12.0~13.3</b></td></tr>
  </tbody></table>
  <div class="callout" style="margin-top:10px"><b>口径提示：</b>① 该号为<b>视频号全国参考区间口径</b>：鳜鱼 33.0~34.5 与同日「水产养殖服务于老师」鳜鱼 1 斤上 23~26、鳜康泰/渔有福塘口 23~25.5、白沙洲批发 30.25 <b>差异大，按原文各自照录、不互减、不互相订正</b>（各号样本产区与口径不同）。② 与 11-15 卡之间 11-16 未采集、隔期，截图无涨跌标注，<b>只列本期数值、不作两期比较</b>。③ 原文温馨提示「行情左右不了，但一定要把鱼养好，看准当地实际收购价、合理安排出鱼节奏」属建议，不作数据录入。</div>
  <div class="legend">来源：视频号「互联惠农小洁」11月17日（截图核校录入）· 元/斤 · 全国参考均价，具体以塘口现场议价为准</div>
</div>
"""

CARD_YSL = """
<div class="card" style="margin-top:14px">
  <h3>🎬 11月17日 · 视频号「水产养殖服务于老师」全国参考塘口价（封面 2026.11.17 · 元/斤）</h3>
  <div class="csub">视频号「水产养殖服务于老师」发布，封面「2026.11.17 全国鱼价 涨跌一目了然」，描述「2026年11月17日全国鱼价（塘口出鱼价）」——<b>封面与描述日期一致</b>。本卡<b>只列鳜鱼 / 加州鲈两类</b>，其余 11 品种按约定不录入。截图核校录入。</div>
  <table><thead><tr><th>品种</th><th>规格</th><th>全国参考塘口价（元/斤）</th><th>原文箭头</th></tr></thead><tbody>
        <tr><td><span class="tag tag-gui">鳜鱼</span></td><td><span class="spec spec-s">1 斤上</span></td><td class="price"><b>23~26</b></td><td style="font-size:12px">↑ 小幅上涨</td></tr>
        <tr><td><span class="tag tag-lu">加州鲈</span></td><td><span class="spec spec-s">1 斤上</span></td><td class="price"><b>10.0~11</b></td><td style="font-size:12px">→ 基本持平</td></tr>
  </tbody></table>
  <div class="callout" style="margin-top:10px"><b>口径提示：</b>① 与 11-13 卡之间 11-14~11-16 未采集、隔期，<b>只列本期数值与原文箭头，不作两期比较</b>。② 鳜鱼「↑小幅上涨」为原文箭头口径，与鳜康泰 11-16「保持稳定」、渔有福「粤湘回落 0.5」表述各异，<b>按原文各自照录、不互减</b>。③ 与小洁同日鳜鱼 0.8-1.2 斤 33.0~34.5 规格与样本不同，<b>不可比</b>。④ 原文注明「行情仅做参考，具体以塘口现场议价为准」。</div>
  <div class="legend">来源：视频号「水产养殖服务于老师」11月17日（截图核校录入）· 元/斤 · 全国参考塘口价</div>
</div>
"""

CARDS_AT = [
    ("daily", CARD_DAILY + CARD_YZ),
    ("gkt", CARD_GKT),
    ("yf", CARD_YF),
    ("ywy", CARD_WY),
    ("qy", CARD_QY),
    ("xj", CARD_XJ),
    ("ysl", CARD_YSL),
]

CHIP_SUBS = [
    ("11-09日报/11-14日报/11-15日报/11-16日报）", "11-09日报/11-14日报/11-15日报/11-16日报/11-17日报）"),
    ("渔知识指导日报（11-03/11-05/11-06/11-13 同值并列）", "渔知识指导日报（11-03/11-05/11-06/11-13/11-17）"),
    ("11-08/11-09/11-10/11-15）+ 老段", "11-08/11-09/11-10/11-15/11-17）+ 老段"),
    ("11-06/11-09/11-10/11-13）+ 阿洁聊水产", "11-06/11-09/11-10/11-13/11-17）+ 阿洁聊水产"),
    ("11-04 冻伤风险专题 / 11-09 特水鱼周报）", "11-04 冻伤风险专题 / 11-09 / 11-16 特水鱼周报）"),
    ("11-05/11-07/11-09/11-14）+ 腾氏一周鱼价播报", "11-05/11-07/11-09/11-14/11-16）+ 腾氏一周鱼价播报"),
    ("11-09同源报价/11-13塘口）", "11-09同源报价/11-13塘口/11-16塘口）"),
    ("11-13 独立期，次日预测口径）", "11-13/11-16 独立期，次日预测口径）"),
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
    for key, block in CARDS_AT:
        html = insert_before(html, ANCHORS[key], block)
        print("[OK] 已插入卡组:", key)
    for old, new in CHIP_SUBS:
        assert html.count(old) == 1, ("chip", old[:46], html.count(old))
        html = html.replace(old, new, 1)
    print("[OK] chip 快览 8 处来源列举同步")

    after = balance(html)
    assert before == after, f"标签配平差值变化：{before} → {after}"
    for g in GUARDS:
        assert html.count(g) == 1, ("guard", g, html.count(g))
    # 鳜康泰 11-16 卡 csub 不得含 V2 trend 触发词（GUI_POND_SPECS 同日期下取鳜康泰）
    i_gkt = html.find(GUARDS[2])
    i_yf = html.find(GUARDS[3])
    assert 0 < i_gkt < i_yf, "鳜康泰/渔有福卡顺序异常"
    seg = html[i_gkt:i_yf]
    csub = re.search(r'<div class="csub">(.*?)</div>', seg, re.S)
    assert csub, "未找到鳜康泰 csub"
    ctxt = csub.group(1)
    assert "下跌" not in ctxt and "上涨" not in ctxt and "未给涨跌" not in ctxt, \
        "鳜康泰 csub 含 trend 触发词，会误判 V2 鳜鱼 KPI"
    open(HTML, "w", encoding="utf-8").write(html)
    print("[OK] 写盘完成 · 字节数", len(html.encode("utf-8")), "· 标签差值", after)
    return 0


if __name__ == "__main__":
    sys.exit(main())
