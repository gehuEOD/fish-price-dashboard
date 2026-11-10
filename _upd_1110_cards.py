#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""2026-11-10 批次：7 张新卡插入 + chip 快览日期同步（幂等、单 div 插入）。

有效数据：
  1. 水产养殖网（强渔）11-09 16:53 特水鱼周报（鳜鱼多产区 + 加州鲈 8 产区）
  2. 鳜康泰特约 11-09 全国鳜鱼报价 —— 与渔有福水产 11-10 08:57《11月9日鳜鱼行情》
     8 项报价及跌幅逐项一致，判为同一份报价的两个发布渠道 → 合并一卡、双出处留痕
  3. 海大农牧 水产一线 11-09 17:35 塘头聚焦（江浙加州鲈）
  4. 渔飞鱼水产 11-10 09:59《明日水产行情预报 11-11》（加州鲈 2~3 斤预测口径；鳜鱼无报价留空）
  5. 视频号「水产养殖服务于老师」11-10
  6. 视频号「互联惠农小洁」11-10（与 11-09 同值同箭头，不重复计数、不推断）
  7. 无锡盛阳食品城 2026.11.9 批发价（与 11-08 同值）

弃用：
  - 淡水渔业 11-09 17:23 普水鱼 7 品种批发价（草鱼/青鱼/鳙/鲤/鲫/罗非/团头鲂），
    全文无鳜鱼/加州鲈报价 → 不录卡、danshui 日期保持 11-06。
  - GiNBjLuidnsMhU4Bn1N2Aw 在用户提交中重复出现两次，只抓取/录入一次。
"""
import re
import sys

HTML = "鳜鱼鲈鱼价格看板.html"

CARD_QIANGYU = """    <div class="card" style="margin-top:14px">
      <h3>📰 2026-11-09 · 水产养殖网（强渔）· 特水鱼周报：鳜鱼止跌反弹夭折、粤苏皖大跌 2 元；加州鲈维稳但规格分化</h3>
      <div class="csub">据「水产养殖网（强渔）」2026-11-09 16:53（安徽）《涨！黄颡鱼多地冲破12元，鳜鱼黑鱼全线转跌、鮰鱼标货走强》：本周鳜鱼上周刚止跌反弹即再度走弱，<b>广东、江苏、安徽产区大跌 2 元</b>；<b>加州鲈整体维稳、呈严重规格分化，仅大规格鱼货源紧缺行情坚挺</b>。<b>本卡只列鳜鱼 / 加州鲈两类</b>（黄颡鱼 / 黑鱼 / 鮰鱼等按约定不录入）。</div>
      <table><thead><tr><th>品种 / 产区</th><th>规格 / 交易环节</th><th>塘口价（元/斤）</th><th>原文要点</th></tr></thead><tbody>
        <tr><td><span class="tag tag-gui">广东</span> 中鳜</td><td>开塘价</td><td class="price"><b>23</b></td><td style="font-size:12px">上车价多在 22 上下，偏大规格低至 20</td></tr>
        <tr><td><span class="tag tag-gui">广东</span> 鱼仔鳜</td><td>鱼仔鳜</td><td class="price">24~24.5</td><td style="font-size:12px">新鱼集中上市、终端消费乏力</td></tr>
        <tr><td><span class="tag tag-gui">广东</span> 饲料鳜</td><td>饲料鳜</td><td class="price">22~22.5</td><td style="font-size:12px">鱼仔鳜基本依靠包销走货</td></tr>
        <tr><td><span class="tag tag-gui">江苏</span> 标鱼</td><td>标鱼</td><td class="price"><b>23</b></td><td style="color:#12a150;font-size:12px">本周大跌 2 元</td></tr>
        <tr><td><span class="tag tag-gui">安徽</span> 标鱼</td><td>标鱼</td><td class="price"><b>24</b></td><td style="color:#12a150;font-size:12px">本周大跌 2 元</td></tr>
        <tr><td><span class="tag tag-gui">湖南</span> 标鱼</td><td>标鱼</td><td class="price">24</td><td style="font-size:12px">外省货源同步放量</td></tr>
        <tr><td><span class="tag tag-gui">湖北</span> 标鱼</td><td>标鱼</td><td class="price">25</td><td style="font-size:12px">仅条形品相好的标鳜走货顺畅</td></tr>
      </tbody></table>
      <table style="margin-top:12px"><thead><tr><th>产区</th><th>规格 / 口径</th><th>塘口价（元/斤）</th><th>原文要点</th></tr></thead><tbody>
        <tr><td>广东佛山</td><td>8 两起</td><td class="price">9 左右</td><td style="font-size:12px">秋鱼普遍规格偏小、统货成交偏弱</td></tr>
        <tr><td>广东佛山</td><td>1 斤以上</td><td class="price"><b>11</b></td><td style="font-size:12px">大规格鱼货源紧缺、行情走俏</td></tr>
        <tr><td>四川成都</td><td>1 斤起</td><td class="price">10.5</td><td style="font-size:12px">外省老鱼存塘基本消耗见底</td></tr>
        <tr><td>湖北</td><td>9 两起</td><td class="price">10</td><td style="font-size:12px">—</td></tr>
        <tr><td>湖南华容</td><td>8 两起</td><td class="price">10</td><td style="font-size:12px">—</td></tr>
        <tr><td>河南郑州</td><td>1 斤起</td><td class="price">11 左右</td><td style="font-size:12px">—</td></tr>
        <tr><td>江苏</td><td>1 斤起</td><td class="price"><b>10.5~11</b></td><td style="font-size:12px">离宜兴官林最近的分产区口径</td></tr>
        <tr><td>浙江湖州</td><td>平 1 斤</td><td class="price">11</td><td style="font-size:12px">新鱼陆续上市但规格偏小</td></tr>
      </tbody></table>
      <div class="callout" style="margin-top:10px"><b>口径提示：</b>① 本周鳜鱼「大跌 2 元」为<b>原文叙述</b>，原文未给上周逐点基准价，故<b>不与 11-07 鳜康泰标鳜 24 或 11-07 通威/腾氏全国均价 25 逐条相减</b>；② 广东「开塘价 / 上车价 / 偏大规格」为不同交易环节，与鱼仔鳜、饲料鳜、分省标鱼并列照录，<b>多口径并存、禁止互减</b>；③ 加州鲈 8 两起 / 9 两起 / 1 斤起 / 平 1 斤规格不同且产区不同，与渔飞鱼 11-11 预报 2~3 斤 11.5~12.5、于老师 1 斤上 10.0-11、盛阳销地批发 10~14 <b>只看方向不看绝对值</b>。</div>
      <div class="legend">来源：微信公众号「水产养殖网（强渔）」2026-11-09 16:53（安徽）《涨！黄颡鱼多地冲破12元，鳜鱼黑鱼全线转跌、鮰鱼标货走强》· <a class="plink" href="https://mp.weixin.qq.com/s/gbaRWBZnGcTTulp53_7TFQ" target="_blank" rel="noopener">📄 阅读原文（强渔 11-09 周报）</a> · 元/斤 · 塘口价，受规格卖相影响仅供参考</div>
    </div>
"""

CARD_GUIKANGTAI = """    <div class="card" style="margin-top:14px">
      <h3>🐟 鳜康泰特约 · 全国鳜鱼报价（2026-11-09 · 元/斤 · 8 项 · 广东跌 1 / 鄂皖苏跌 0.5；与渔有福同源合并）</h3>
      <div class="csub">据「兴渔派-鳜鱼通」2026-11-09 21:12（广东）《11月9日鳜鱼价格行情丨鳜康泰特约·全国鳜鱼报价》与「渔有福水产」2026-11-10 08:57《11月9日鳜鱼行情｜多产区集体走跌》：两篇 <b>8 项报价与跌幅描述逐项一致</b>，判为<b>同一份报价的两个发布渠道</b>，<b>合并一卡、双出处留痕，不重复计数、不作两期比较</b>。<b>广东小鳜 / 标鳜 / 中鳜统一下跌 1 元/斤；湖北、安徽、江苏标鳜下跌 0.5 元/斤</b>；<b>标鳜（0.8-1.5斤）23 元/斤左右</b>，小鳜 18、中鳜 20.5。</div>
      <table><thead><tr><th>品种 / 产区</th><th>规格</th><th>报价（元/斤）</th><th>原文涨跌</th></tr></thead><tbody>
        <tr><td><span class="tag tag-gui">广东</span> 小鳜</td><td><span class="spec spec-s">0.8斤以下</span></td><td class="price"><b>18 左右</b></td><td style="color:#12a150;font-size:12px">↓ 跌 1 元/斤</td></tr>
        <tr><td><span class="tag tag-gui">广东</span> 标鳜</td><td><span class="spec spec-s">0.8-1.5斤</span></td><td class="price"><b>23 左右</b></td><td style="color:#12a150;font-size:12px">↓ 跌 1 元/斤</td></tr>
        <tr><td><span class="tag tag-gui">广东</span> 中鳜</td><td><span class="spec spec-m">1.5-2斤</span></td><td class="price"><b>20.5 左右</b></td><td style="color:#12a150;font-size:12px">↓ 跌 1 元/斤</td></tr>
        <tr><td><span class="tag tag-gui">湖北</span> 标鳜</td><td><span class="spec spec-s">标鳜</span></td><td class="price">24 左右</td><td style="color:#12a150;font-size:12px">↓ 跌 0.5 元/斤</td></tr>
        <tr><td><span class="tag tag-gui">安徽</span> 标鳜</td><td><span class="spec spec-s">标鳜</span></td><td class="price">24 左右</td><td style="color:#12a150;font-size:12px">↓ 跌 0.5 元/斤</td></tr>
        <tr><td><span class="tag tag-gui">江西</span> 标鳜</td><td><span class="spec spec-s">标鳜</span></td><td class="price">25.5 左右</td><td style="color:#6b7280;font-size:12px">原文未列涨跌</td></tr>
        <tr><td><span class="tag tag-gui">湖南</span> 标鳜</td><td><span class="spec spec-s">标鳜</span></td><td class="price">25 左右</td><td style="color:#6b7280;font-size:12px">原文未列涨跌</td></tr>
        <tr><td><span class="tag tag-gui">江苏</span> 标鳜</td><td><span class="spec spec-s">标鳜</span></td><td class="price">24.5 左右</td><td style="color:#12a150;font-size:12px">↓ 跌 0.5 元/斤</td></tr>
      </tbody></table>
      <div class="callout" style="margin-top:10px"><b>口径提示：</b>① 与看板 11-07 同号卡（标鳜 24、小鳜 19、中鳜 21.5、鄂/皖 24.5、江苏 25、江西 25.5、湖南 25）<b>同号同规格可比</b>：标鳜 24→23、小鳜 19→18、中鳜 21.5→20.5、鄂/皖 24.5→24、江苏 25→24.5，方向与原文「广东跌 1 / 鄂皖苏跌 0.5」一致；江西、湖南持平，原文未列涨跌故不推断。② 0.8-1.5 斤标鳜口径与于老师 1 斤上 22-25、小洁 0.8-1.2 斤通货 32.2~33.8、强渔 11-09 江苏标鱼 23、盛阳销地批发 25~30、凌家塘批发约 30 <b>规格与渠道不同，多口径并存、禁止互减</b>。③ 两篇均未标注「沿用」，按新采价录入；<b>同一份报价被两个公众号转载不重复计数</b>。</div>
      <div class="legend">来源：微信公众号「兴渔派-鳜鱼通」2026-11-09 21:12（广东）· <a class="plink" href="https://mp.weixin.qq.com/s/GiNBjLuidnsMhU4Bn1N2Aw" target="_blank" rel="noopener">📄 鳜康泰特约 11-09</a>；同文转载「渔有福水产」2026-11-10 08:57 · <a class="plink" href="https://mp.weixin.qq.com/s/kmicNkEzxcR_Rfvc-PyCNw" target="_blank" rel="noopener">📄 渔有福 11-09 鳜鱼行情</a> · 元/斤 · 塘口成交参考价，实际以现场谈价为准</div>
    </div>
"""

CARD_HAINONG = """    <div class="card" style="margin-top:14px">
      <h3>🐟 11月9日 · 海大农牧 水产一线「塘头聚焦」：江浙加州鲈（元/斤）</h3>
      <div class="csub">据「海大农牧 水产一线」2026-11-09 17:35（广东）《鱼价观察 | 病害压价、流通困难、盈利有限……这个冬天怎么过？11月9日塘头聚焦》：常州海大技术服务部江浙养殖盘点。<b>加州鲈（江苏吴江、浙江绍兴）0.5-1.1 斤存塘约 85%，塘口发价 1-1.1 元/两、大统货 9.5-10 元/斤</b>，行情波动不大、较去年同期持平或略高；<b>盈利空间有限、出鱼积极性一般，预计短期内趋向稳定</b>。本篇<b>未涉及鳜鱼，如实留空</b>。</div>
      <table><thead><tr><th>产区 / 口径</th><th>规格</th><th>价格（元/斤）</th><th>原文要点</th></tr></thead><tbody>
        <tr><td>江苏吴江 · 浙江绍兴</td><td>0.5-1.1 斤存塘量</td><td class="price">约 85%（存塘结构）</td><td style="font-size:12px">早苗 9 两~1.1 斤、暖棚苗 0.8-1 斤、外塘苗 7-9 两</td></tr>
        <tr><td>江浙</td><td>塘口发价（原文单位 元/两）</td><td class="price"><b>1~1.1 元/两</b></td><td style="font-size:12px">折约 10~11 元/斤，原文并列给出</td></tr>
        <tr><td>江浙</td><td>大统货</td><td class="price"><b>9.5~10</b></td><td style="font-size:12px">行情波动不大、较去年同期持平或略高</td></tr>
        <tr><td><span class="tag tag-gui">鳜鱼</span></td><td>—</td><td class="price">原文未涉及</td><td style="font-size:12px">本期为江浙特水 / 普水盘点，无鳜鱼条目</td></tr>
      </tbody></table>
      <div class="callout" style="margin-top:10px"><b>口径提示：</b>① <b>1~1.1 元/两折约 10~11 元/斤</b>，与大统货 9.5~10 为发价 / 统货两种口径，<b>并列照录、不互减</b>；② 本期为江浙产区聚焦，与 11-06 该号四产区（浙 / 闽 / 豫 / 鄂 10.5~11.3）<b>产区与期次不同，不作逐点比较</b>；③ 与强渔 11-09 周报江苏 1 斤起 10.5~11、渔飞鱼 11-11 预报 2~3 斤 11.5~12.5、于老师 1 斤上 10.0-11 <b>规格与渠道不同，多口径并存、禁止互减</b>。</div>
      <div class="legend">来源：微信公众号「海大农牧 水产一线」2026-11-09 17:35（广东）《鱼价观察 | 11月9日塘头聚焦》· <a class="plink" href="https://mp.weixin.qq.com/s/Lj1umEIOcwn1AbYny_FSMw" target="_blank" rel="noopener">📄 阅读原文（海大农牧 11-09）</a> · 元/斤（原文塘口发价另用元/两）</div>
    </div>
"""

CARD_YUFEIYU = """    <div class="card" style="margin-top:14px">
      <h3>🐟 渔飞鱼 · 11月10日发布《明日水产行情预报 · 11-11 周三》（次日预测口径）</h3>
      <div class="csub">据「渔飞鱼水产」2026-11-10 09:59（河南）《明日水产行情预报 | 2026年11月11日》：数据基准 11/9-10、覆盖 28 品种；11/9 水产品价格指数 115.23，比上周五<b>下降 0.45</b>。<b>本卡只跟踪鳜鱼 / 加州鲈两类</b>：<b>加州鲈鱼 1-1.5 公斤规格基准 11.5–12.5 元/斤、明日预测 11.5–12.5 → 平稳（置信度高）</b>；<b>鳜鱼本期 28 品种表及预测概览中均无条目，如实留空</b>。</div>
      <table><thead><tr><th>品种</th><th>规格 / 渠道</th><th>基准价（元/斤）</th><th>明日预测</th></tr></thead><tbody>
        <tr><td><span class="tag tag-lu">加州鲈鱼</span></td><td><span class="spec spec-m">1-1.5 公斤规格</span></td><td class="price"><b>11.5~12.5</b></td><td style="color:#6b7280;font-size:12px">11.5~12.5 → 平稳（置信度 高）</td></tr>
        <tr><td><span class="tag tag-gui">鳜鱼</span></td><td>—</td><td class="price">原文未给报价</td><td style="color:#6b7280;font-size:12px">28 品种表与预测概览均无鳜鱼条目</td></tr>
      </tbody></table>
      <div class="callout" style="margin-top:10px"><b>口径提示：</b>① 本刊为<b>次日预测性质、非实测成交价</b>（原文自述「受流通、突发因素影响可能与实际存在偏差」），基准价与预测价同值，<b>不据此推断涨跌</b>；② <b>1-1.5 公斤 = 2~3 斤大规格</b>，与塘口 1 斤上（于老师 10.0-11、强渔江苏 10.5~11）、海大 1~1.1 元/两（折 10~11）、盛阳销地批发 10~14 <b>规格不同，不可互减</b>；③ 该 11.5~12.5 与本看板 11-04「渔无忧在线 · 最新水产行情预报」卡<b>同值同规格</b>，但为两个公众号、两期预报，<b>不重复计数、不作趋势推断</b>；④ 发布公众号为「渔飞鱼水产」，按<b>发布公众号</b>归渔飞鱼系列，与「全国渔业价格」发布的日报分开计数。</div>
      <div class="legend">来源：微信公众号「渔飞鱼水产」2026-11-10 09:59（河南）《明日水产行情预报 | 2026年11月11日》· <a class="plink" href="https://mp.weixin.qq.com/s/lzLVoaa14X3bdaa6IbuvYQ" target="_blank" rel="noopener">📄 阅读原文（渔飞鱼 11-11 预报）</a> · 数据基准 11/9-10，预测价仅为次日参考</div>
    </div>
"""

CARD_YULAOSHI = """    <div class="card" style="margin-top:14px">
      <h3>🎬 11月10日 · 视频号「水产养殖服务于老师」全国参考塘口价（元/斤）</h3>
      <div class="csub">据视频号「水产养殖服务于老师」2026-11-10《2026.11.10全国鱼价 涨跌一目了然》：14 品种<b>基本持平</b>，仅黄颡鱼「小幅上涨」、鲤鱼 / 白鲢「持续低迷」。<b>本看板只跟踪鳜鱼 / 加州鲈两类</b>（其余 12 品种不录入）。<b>鳜鱼 1 斤上 22-25 元/斤（基本持平）</b>、<b>加州鲈 1 斤上 10.0-11 元/斤（基本持平）</b>。行情仅做参考，具体以塘口现场议价为准。</div>
      <table><thead><tr><th>品种</th><th>规格</th><th>11-10 报价（元/斤）</th><th>原始标注</th><th>较 11-09（同号）</th></tr></thead><tbody>
        <tr><td><span class="tag tag-gui">鳜鱼</span></td><td>1 斤上</td><td class="price"><b>22-25</b></td><td style="color:#6b7280;font-size:12px">基本持平</td><td style="color:#6b7280;font-size:12px">22-26.5 → 上限 -1.5（区间收窄）</td></tr>
        <tr><td><span class="tag tag-lu">加州鲈</span></td><td>1 斤上</td><td class="price"><b>10.0-11</b></td><td style="color:#6b7280;font-size:12px">基本持平</td><td style="color:#6b7280;font-size:12px">10.0-11.5 → 上限 -0.5（区间收窄）</td></tr>
      </tbody></table>
      <div class="callout" style="margin-top:10px"><b>口径提示：</b>① 两品种区间较 11-09 均收窄，但<b>原文标注仍为「基本持平」，按原文照录、不推断涨跌</b>；该号区间宽度本身随产区报价浮动（11-05 为 22-26、11-06 收窄至 22-25、11-09 放大至 22-26.5）。② 该号「1 斤上」全国参考塘口区间与小洁 0.8-1.2 斤通货（32.2~33.8 / 12.5~13.8）、鳜康泰标鳜 23（11-09）、强渔 11-09 江苏标鱼 23 / 加州鲈 10.5~11、盛阳销地批发 25~30 / 10~14 <b>规格与渠道不同，多口径并存、禁止互减</b>，只看方向不看绝对值。③ 原文底部提示照录：「行情仅做参考 具体以塘口现场议价为准」。</div>
      <div class="legend">来源：微信视频号「水产养殖服务于老师」2026-11-10《2026.11.10全国鱼价》（截图核校录入）· 元/斤 · 行情仅做参考，具体以塘口现场议价为准</div>
    </div>
"""

CARD_XIAOJIE = """    <div class="card" style="margin-top:14px">
      <h3>🎬 11月10日 · 视频号「互联惠农小洁」全国参考塘口价（元/斤）</h3>
      <div class="csub">据视频号「互联惠农小洁」2026-11-10《11月10日全国最新塘口鱼价出炉！涨跌博弈持续！出鱼前务必看清这波行情！》：本期 8 品种（草鱼 / 鲫鱼 / 鲤鱼 / 鲈鱼 / 鳜鱼 / 黄颡鱼 / 黑鱼 / 青鱼）。<b>本看板只跟踪鳜鱼 / 鲈鱼两类</b>（其余 6 品种不录入）。<b>鳜鱼（0.8-1.2斤）32.2~33.8 元/斤 ↑</b>、<b>鲈鱼（0.8-1.2斤）12.5~13.8 元/斤 ↓</b>——<b>与 11-09 逐项同值同箭头，原文未标注「沿用」，按原文照录、不重复计数、不推断涨跌</b>。</div>
      <table><thead><tr><th>品种</th><th>规格</th><th>11-10 报价（元/斤）</th><th>原始标注</th><th>较 11-09（同号）</th></tr></thead><tbody>
        <tr><td><span class="tag tag-gui">鳜鱼</span></td><td><span class="spec spec-m">0.8-1.2斤</span></td><td class="price"><b>32.2~33.8</b></td><td style="color:#dc2626;font-size:12px">↑ 涨</td><td style="color:#6b7280;font-size:12px">32.2~33.8 → 同值，不重复计数</td></tr>
        <tr><td><span class="tag tag-lu">鲈鱼</span></td><td><span class="spec spec-m">0.8-1.2斤</span></td><td class="price"><b>12.5~13.8</b></td><td style="color:#12a150;font-size:12px">↓ 跌</td><td style="color:#6b7280;font-size:12px">12.5~13.8 → 同值，不重复计数</td></tr>
      </tbody></table>
      <div class="callout" style="margin-top:10px"><b>口径提示：</b>① 本期与 11-09 <b>逐项同值同箭头</b>，可能是沿用 / 重发，但<b>原文未明确标注「沿用」</b>，故如实并列、<b>不重复计数、不推断涨跌、不作两期比较</b>（区别于 11-09 全国渔业价格日报明确标注的「11/7 沿用值」）；② 0.8-1.2 斤通货区间与于老师 1 斤上 22-25 / 10.0-11、鳜康泰标鳜 23、强渔 11-09 塘口、盛阳销地批发 25~30 / 10~14 <b>规格与渠道不同，多口径并存、禁止互减</b>；③ 视频原文核心提醒照录：「咱们水产人起早贪黑不容易，行情咱们左右不了，但一定要把水调好、把鱼养好！记住：规格大、皮毛好（活力足），鱼贩子抢着要！」</div>
      <div class="legend">来源：微信视频号「互联惠农小洁」2026-11-10《11月10日全国最新塘口鱼价出炉！涨跌博弈持续！出鱼前务必看清这波行情！》（截图核校录入）· 报价只是全国塘口参考价，各地有差价，仅供参考</div>
    </div>
"""

CARD_SHENGYANG = """    <div class="card" style="margin-top:14px">
      <h3>🛒 2026.11.9 · 无锡盛阳食品城水产批发价（元/斤）</h3>
      <div class="csub">无锡盛阳食品城水产类批发价（当日均价、仅供参考），表头日期 <b>2026.11.9</b>。<b>鳜鱼（桂鱼）25~30、鲈鱼 10~14</b>——与 11-08 同值，鳜鱼延续 25~30 横盘、鲈鱼 10~14 持平。离宜兴官林最近的销地批发口径之一。</div>
      <table><thead><tr><th>品种</th><th>当日均价（元/斤）</th><th>较 11-08</th></tr></thead><tbody>
        <tr><td><b>鳜鱼（桂鱼）</b></td><td class="price"><b>25~30</b></td><td style="color:#6b7280;font-size:12px">持平（延续横盘）</td></tr>
        <tr><td><b>鲈鱼</b></td><td class="price"><b>10~14</b></td><td style="color:#6b7280;font-size:12px">持平</td></tr>
      </tbody></table>
      <div class="callout" style="margin-top:10px"><b>口径说明：</b>销地批发「当日均价」口径（元/斤），与塘口收购价、农业农村部全国批发均价（元/公斤）、视频号全国参考区间、渔飞鱼 11-11 预报 2~3 斤 11.5~12.5 并存，<b>禁止互减</b>。本期截图另含杂货类（黄鳝 / 甲鱼 / 牛蛙 / 黑鱼等）、虾类（河虾 / 基围虾 / 罗氏虾）、蟹类（公母蟹分规格）完整报价，<b>均非本看板跟踪品种，按约定不录入</b>，仅截图存档。</div>
      <div class="legend">来源：盛阳食品城水产类批发价 2026.11.9（截图核校录入）· 元/斤 · 当日均价仅供参考</div>
    </div>
"""

# (旧卡 h3 锚点, 新卡 HTML) —— 新卡一律插在旧卡开 div 之前
INSERTS = [
    ("📰 2026-11-04 · 水产养殖网（强渔）· 加州鲈冬季冻伤风险上升", CARD_QIANGYU),
    ("🐟 鳜康泰特约 · 全国鳜鱼报价（2026-11-07", CARD_GUIKANGTAI),
    ("🐟 11月6日 · 海大农牧 水产一线「全球最新塘头价」", CARD_HAINONG),
    ("🐟 渔飞鱼·董小月 ·《全国最新水产行情日报 2026年11月6日》", CARD_YUFEIYU),
    ("🎬 11月9日 · 视频号「水产养殖服务于老师」", CARD_YULAOSHI),
    ("🎬 11月9日 · 视频号「互联惠农小洁」", CARD_XIAOJIE),
    ("🛒 2026.11.8 · 无锡盛阳食品城", CARD_SHENGYANG),
]

# chip 快览串：逐项精确替换（每段须唯一命中）
CHIP_SUBS = [
    ("日报11-05/日报11-06）", "日报11-05/日报11-06·预报11-11）"),
    ("/11-08/11-09）+ 老段", "/11-08/11-09/11-10）+ 老段"),
    ("/11-06/11-09）+ 阿洁", "/11-06/11-09/11-10）+ 阿洁"),
    ("/ 11-04 冻伤风险专题）+", "/ 11-04 冻伤风险专题 / 11-09 特水鱼周报）+"),
    ("/11-05/11-06塘口）+ 鳜康泰特约", "/11-05/11-06塘口/11-09同源报价）+ 鳜康泰特约"),
    ("/11-05/11-07）+ 腾氏", "/11-05/11-07/11-09）+ 腾氏"),
    ("/ 11-06 四产区塘头价）+ 盛阳", "/ 11-06 四产区塘头价 / 11-09 江浙塘头聚焦）+ 盛阳"),
    ("/11.6/11.8批发）+", "/11.6/11.8/11.9批发）+"),
]

# 幂等守卫：与卡内实际 h3 逐字一致
GUARD = "📰 2026-11-09 · 水产养殖网（强渔）· 特水鱼周报"


def balance(text):
    """精确标签统计：<tag 后必须跟空白或 >，避免 <thead> 计入 <th、<body>/<br> 计入 <b。"""
    return {t: len(re.findall(r"<" + t + r"(?=[\s>])", text)) - text.count("</" + t + ">")
            for t in ("section", "div", "table", "thead", "tbody", "tr", "td", "th", "b")}


def main():
    html = open(HTML, encoding="utf-8").read()
    if GUARD in html:
        print("[SKIP] 本批次卡片已插入，退出以防重复")
        return 0

    before = balance(html)

    for anchor, card in INSERTS:
        assert html.count(anchor) == 1, (anchor[:44], html.count(anchor))
        idx = html.find(anchor)
        pos = html.rfind('<div class="card"', 0, idx)
        assert pos > 0, anchor[:44]
        html = html[:pos] + card + html[pos:]
        print("[OK] 插卡 →", anchor[:44])

    for old, new in CHIP_SUBS:
        assert html.count(old) == 1, ("chip", old[:40], html.count(old))
        html = html.replace(old, new, 1)
    print("[OK] chip 快览 8 处日期同步")

    after = balance(html)
    assert before == after, f"标签配平差值变化：{before} → {after}"
    assert html.count("VIDEOCHANNEL_LIVE_END") == 1
    end = html.find("VIDEOCHANNEL_LIVE_END")
    for s in ("🎬 11月10日 · 视频号「互联惠农小洁」", "🎬 11月10日 · 视频号「水产养殖服务于老师」"):
        assert html.find(s) > end, f"视频号新卡落入自动注入区块：{s}"

    open(HTML, "w", encoding="utf-8").write(html)
    print("[OK] 写盘完成 · 字节数", len(html.encode("utf-8")), "· 标签差值", after)
    return 0


if __name__ == "__main__":
    sys.exit(main())
