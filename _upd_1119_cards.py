# -*- coding: utf-8 -*-
"""2026-11-19 批次插卡：日报11-18 / 鳜康泰11-18 / 加州鲈周报45期 / 养殖网加州鲈专题11-18 / 盛阳11.19 / 小洁11-19 / 服务于老师11-19。
科学养鱼 OCR 11-18 走 wechat_ocr_current.json + inject_kexue_block.py 通道（另行更新）。
"""
import re

F = "鳜鱼鲈鱼价格看板.html"
html = open(F, encoding="utf-8").read()

# 幂等守卫（h3 专属串）：已存在则跳过
_PRE_GUARDS = [
    "渔飞鱼水产行情日报 2026-11-18》（发布 11-18 08:36",
    "全国鳜鱼报价（2026-11-18 · 元/斤 · 8 项 · 绝对价与 11-16 期同值",
    "《加州鲈周报》第45期：最高跌 1 元/斤",
    "水产养殖网 · 加州鲈专题：多地逼近 10 元关口",
    "🛒 2026.11.19 · 无锡盛阳食品城",
    "🎬 11月19日 · 视频号「互联惠农小洁」",
    "🎬 11月19日 · 视频号「水产养殖服务于老师」",
]
_present = [g for g in _PRE_GUARDS if g in html]
if _present:
    print("[SKIP] 本批卡已存在（守卫命中 %d/%d），无写入" % (len(_present), len(_PRE_GUARDS)))
    raise SystemExit(0)

URL_DAILY = "https://mp.weixin.qq.com/s/mKayUpr6YsPinWwy1MTyaA"
URL_GT = "https://mp.weixin.qq.com/s/0onzHB15V3zfmbqzf_Abog"
URL_LU45 = "https://mp.weixin.qq.com/s/Zg4FhJ_7AJBnrdF3qkp_BQ"
URL_ZTW = "https://mp.weixin.qq.com/s/0J_Mivoy-u1oMSJIeRfq9A"

# ---------- 1) 渔飞鱼日报 11-18 ----------
CARD_DAILY = """<div class="card" style="margin-top:14px">
  <h3>📰 全国渔业价格 ·《渔飞鱼水产行情日报 2026-11-18》（发布 11-18 08:36 · 白沙洲 11/16 · 全表横盘 1 涨 1 跌 / 鳜鱼停步 30 关口）</h3>
  <div class="csub">21 品种呈「1 涨 1 跌、19 行持平或沿用」：<b>白沙洲官网已更新到 11/16，48 条报价只有鲤鱼中规格 8.80→8.90 元/公斤＝4.45 元/斤（+1.1%）</b>；鳜鱼 ≥750g 仍 60.50 元/公斤＝<b>30.25 元/斤</b>，鲈鱼 ≥500g 仍 19.80 元/公斤＝<b>9.90 元/斤</b>，一条没动。原文判断：「补涨走完第四天停住了，30 元/斤整数关口站住但没第二波」。</div>
  <table><thead><tr><th>品种 / 渠道</th><th>规格</th><th>价格</th><th>涨跌（vs 上期）</th></tr></thead><tbody>
        <tr><td><span class="tag tag-gui">鳜鱼</span> 武汉白沙洲 批发</td><td><span class="spec spec-s">条重 ≥750g</span></td><td class="price"><b>60.50 元/公斤 ≈ 30.25 元/斤</b></td><td style="color:#64748b;font-size:12px">平（11/16，连涨第四天后停住）</td></tr>
        <tr><td><span class="tag tag-gui">鳜鱼</span> 武汉白沙洲 批发</td><td><span class="spec spec-s">500≤条重&lt;750g</span></td><td class="price">58.00 元/公斤</td><td style="color:#64748b;font-size:12px">平（11/16）</td></tr>
        <tr><td><span class="tag tag-gui">鳜鱼</span> 武汉白沙洲 批发</td><td><span class="spec spec-s">250≤条重&lt;500g</span></td><td class="price">47.50 元/公斤</td><td style="color:#64748b;font-size:12px">平（11/16）</td></tr>
        <tr><td><span class="tag tag-gui">鳜鱼</span> 21food 产区价</td><td><span class="spec spec-s">条重 ≥750g</span></td><td class="price">60.5 元/公斤</td><td style="color:#64748b;font-size:12px">平稳（11/16）</td></tr>
        <tr><td><span class="tag tag-lu">鲈鱼</span> 武汉白沙洲 批发</td><td><span class="spec spec-s">条重 ≥500g</span></td><td class="price"><b>19.80 元/公斤 ≈ 9.90 元/斤</b></td><td style="color:#64748b;font-size:12px">平（11/16）</td></tr>
        <tr><td><span class="tag tag-lu">加州鲈</span> 惠农 产地均价</td><td><span class="spec spec-s">鲜活 统货</span></td><td class="price"><b>11.69 元/斤</b></td><td style="color:#64748b;font-size:12px">平（11/17）</td></tr>
  </tbody></table>
  <div class="callout" style="margin-top:12px"><b>口径说明：</b>① 白沙洲批发（折算）与 21food 产区价、惠农产地均价<b>渠道不同、禁止互减</b>；白沙洲 60.50 与产区 21food 60.5「齐平之后原地踏步」为原文表述，照录不推断。② 加州鲈产地均价基准日更新至 <b>11/17</b>（11-17 日报卡为 11/16），同值 11.69、原文标「平」。③ <b>原文卖鱼思路「30.25 今天能出就出、18 日雨里不会再给这个价」为建议性表述，不入数据</b>。④ 本卡为批发/产区口径，与鳜康泰 11-18 塘口（苏标鳜 24.5）、盛阳本地批发（25~30）<b>多口径并存</b>。</div>
  <div class="legend">来源：微信公众号「全国渔业价格」2026-11-18 08:36《渔飞鱼水产行情日报（2026年11月18日）》· <a class="plink" href="__URL_DAILY__" target="_blank" rel="noopener">📄 阅读原文（日报 11-18）</a> · 元/公斤为主 · 正文文字核校录入</div>
</div>

""".replace("__URL_DAILY__", URL_DAILY)

# ---------- 2) 鳜康泰 11-18 ----------
CARD_GT = """<div class="card" style="margin-top:14px">
  <h3>🐟 鳜康泰特约 · 全国鳜鱼报价（2026-11-18 · 元/斤 · 8 项 · 绝对价与 11-16 期同值、附 11/12 对照周跌 0.5）</h3>
  <div class="csub">据「兴渔派-鳜鱼通」2026-11-18 18:58《11月18日鳜鱼价格行情丨鳜康泰特约·全国鳜鱼报价》：正文文字自述<b>「11月17日，近期鳜价保持稳定，出鱼量一般」</b>；附图《全国鳜鱼行情》三日期对照表（11/12 → 11/17 → 11/18）8 项绝对价与 11-16 期逐项同值，<b>日涨跌全部「—」</b>；广东标鳜、中鳜、湖南标鳜对 11/12 对照列标<b>周跌 0.5</b>。文字「保持稳定」与附图周跌列<b>两处表述并存照录</b>。</div>
  <table><thead><tr><th>品种 / 产区</th><th>规格</th><th>11-18 塘口价（元/斤）</th><th>日涨跌</th><th>周涨跌（vs 11/12）</th></tr></thead><tbody>
        <tr><td><span class="tag tag-gui">广东</span> 小鳜</td><td><span class="spec spec-s">0.8 斤以下</span></td><td class="price"><b>19</b></td><td style="font-size:12px">—</td><td style="color:#64748b;font-size:12px">—</td></tr>
        <tr><td><span class="tag tag-gui">广东</span> 标鳜</td><td><span class="spec spec-s">0.8~1.5 斤</span></td><td class="price"><b>23</b></td><td style="font-size:12px">—</td><td style="color:#16a34a;font-size:12px">↓0.5</td></tr>
        <tr><td><span class="tag tag-gui">广东</span> 中鳜</td><td><span class="spec spec-s">1.5-2 斤</span></td><td class="price"><b>20</b></td><td style="font-size:12px">—</td><td style="color:#16a34a;font-size:12px">↓0.5</td></tr>
        <tr><td><span class="tag tag-gui">湖北</span> 标鳜</td><td><span class="spec spec-s">标鳜</span></td><td class="price"><b>24</b></td><td style="font-size:12px">—</td><td style="color:#64748b;font-size:12px">—</td></tr>
        <tr><td><span class="tag tag-gui">安徽</span> 标鳜</td><td><span class="spec spec-s">标鳜</span></td><td class="price"><b>24</b></td><td style="font-size:12px">—</td><td style="color:#64748b;font-size:12px">—</td></tr>
        <tr><td><span class="tag tag-gui">江西</span> 标鳜</td><td><span class="spec spec-s">标鳜</span></td><td class="price"><b>25.5</b></td><td style="font-size:12px">—</td><td style="color:#64748b;font-size:12px">—</td></tr>
        <tr><td><span class="tag tag-gui">湖南</span> 标鳜</td><td><span class="spec spec-s">标鳜</span></td><td class="price"><b>24.5</b></td><td style="font-size:12px">—</td><td style="color:#16a34a;font-size:12px">↓0.5</td></tr>
        <tr><td><span class="tag tag-gui">江苏</span> 标鳜</td><td><span class="spec spec-s">标鳜</span></td><td class="price"><b>24.5</b></td><td style="font-size:12px">—</td><td style="color:#64748b;font-size:12px">—（11/12 亦 24.5）</td></tr>
  </tbody></table>
  <div class="callout" style="margin-top:12px"><b>同值并列 / 多口径说明：</b>① 8 项绝对价与 11-16 期卡（本系列）逐项同值、日涨跌同为全「—」，但<b>本期新增 11/12 对照列：广东标鳜/中鳜、湖南标鳜周跌 0.5</b>，与文字自述「保持稳定」并存——按原文各自照录、不互相覆盖、不作两期比较。② 正文开头写「11月17日」、标题为 11月18日行情，<b>按发布期 11-18 归档、依据写明</b>。③ 江苏标鳜 24.5 在鳜康泰 11-14（日持平/周 ↓0.5）、渔有福 11-16（未给说明）、本卡（周 —）口径各异，<b>不互减、不订正</b>。④ 塘口报价口径，与白沙洲批发 30.25、盛阳 25~30、视频号区间 32.5~34.0<b>多口径并存、禁止互减</b>。附图另 3 张为广告弃用。</div>
  <div class="legend">来源：微信公众号「兴渔派-鳜鱼通」2026-11-18 18:58《11月18日鳜鱼价格行情丨鳜康泰特约·全国鳜鱼报价》· <a class="plink" href="__URL_GT__" target="_blank" rel="noopener">📄 阅读原文</a> · 元/斤 · 塘口报价 · 正文文字 + 附图逐张核校录入（图 4 为正式报价表）</div>
</div>

""".replace("__URL_GT__", URL_GT)

# ---------- 3) 水产前沿 加州鲈周报第45期 11-18 ----------
CARD_LU45 = """<div class="card" style="margin-top:14px">
  <h3>📰 11月18日 · 水产前沿《加州鲈周报》第45期：最高跌 1 元/斤！广东出鱼节奏快、缺大鱼（杰大饲料特约 · 元/斤）</h3>
  <div class="csub">全国 7 大主产区塘头价对比（11.11 → 11.18）：<b>江苏 9 两上 10.5-11.5→9.5-10.5、跌幅最大 1 元/斤</b>；佛山 1 斤上 10.3-10.5→10.2-10.3 微跌 0.1-0.2、<b>跌破 10.5 关口逼近 10 元</b>；浙江 8 成统货 ↓0.5；河南 ↓0.5；四川/湖南/湖北持稳。原文：广东出鱼节奏快、大规格偏缺，新鱼集中上市压制行情。</div>
  <table><thead><tr><th>地区</th><th>规格（每尾）</th><th>11.11 塘头价</th><th>11.18 塘头价</th><th>环比</th></tr></thead><tbody>
        <tr><td rowspan="5"><span class="tag tag-lu">广东佛山</span></td><td><span class="spec spec-s">6两上</span></td><td class="price">—</td><td class="price">—</td><td style="color:#6b7280">—</td></tr>
        <tr><td><span class="spec spec-s">7两上</span></td><td class="price">—</td><td class="price">—</td><td style="color:#6b7280">—</td></tr>
        <tr><td><span class="spec spec-s">8两上</span></td><td class="price">10-10.2</td><td class="price">—</td><td style="color:#6b7280">—</td></tr>
        <tr><td><span class="spec spec-s">9两上</span></td><td class="price">—</td><td class="price">—</td><td style="color:#6b7280">—</td></tr>
        <tr><td><span class="spec spec-m">1斤上</span></td><td class="price">10.3-10.5</td><td class="price"><b>10.2-10.3</b></td><td style="color:#16a34a;font-weight:600">0.1-0.2↓</td></tr>
        <tr><td><span class="tag tag-lu">浙江</span></td><td><span class="spec spec-m">8成统货</span></td><td class="price">11-11.5</td><td class="price"><b>10.5-11</b></td><td style="color:#16a34a;font-weight:600">0.5↓</td></tr>
        <tr><td><span class="tag tag-lu">江苏</span></td><td><span class="spec spec-m">9两上</span></td><td class="price">10.5-11.5</td><td class="price"><b>9.5-10.5</b></td><td style="color:#16a34a;font-weight:600">1↓</td></tr>
        <tr><td rowspan="2"><span class="tag tag-lu">四川</span></td><td><span class="spec spec-m">9两上</span></td><td class="price">10.5</td><td class="price"><b>10.5</b></td><td style="color:#64748b;font-weight:600">→</td></tr>
        <tr><td><span class="spec spec-m">1斤上</span></td><td class="price">11</td><td class="price"><b>11</b></td><td style="color:#64748b;font-weight:600">→</td></tr>
        <tr><td><span class="tag tag-lu">湖南</span></td><td><span class="spec spec-m">9两上</span></td><td class="price">10.5</td><td class="price"><b>10.5</b></td><td style="color:#64748b;font-weight:600">→</td></tr>
        <tr><td><span class="tag tag-lu">湖北</span></td><td><span class="spec spec-m">8.5两上</span></td><td class="price">10.5</td><td class="price"><b>10.5</b></td><td style="color:#64748b;font-weight:600">→</td></tr>
        <tr><td><span class="tag tag-lu">河南</span></td><td><span class="spec spec-m">1斤上</span></td><td class="price">11</td><td class="price"><b>10.5</b></td><td style="color:#16a34a;font-weight:600">0.5↓</td></tr>
  </tbody></table>
  <div class="callout" style="margin-top:10px"><b>口径说明与交叉印证：</b>① 本期为<b>水产前沿「加州鲈周报」系列第 45 期</b>（杰大饲料特约，与《特水鱼周报》同号不同系列，专注鲈鱼），与第 41 期卡同款三日期对照结构；<b>8 两上规格 11.18 未给报价，如实留空</b>。② 本周江苏 9 两上跌 1 元为全国最大跌幅，与 11-16 强渔周报「江苏 1 斤起 10.5~11」、11-17 特水 39 期「江苏 9 两上 10.5-11.5 持平」<b>时间口径不同（11.18 vs 11.16/11.17），方向转跌按原文照录、不作两期比较</b>。③ 佛山 1 斤上 10.2-10.3 与水产养殖网 11-18 专题「本周报价 10.3、环比跌 0.5」<b>周对照起点不同（10.3-10.5 vs 上周更高），两卡并列不互减</b>。④ 塘头价口径，与盛阳批发 10~14、白沙洲 9.90、视频号 10.0~11 / 11.8~13.2<b>多口径并存</b>。</div>
  <div class="legend">来源：微信公众号「水产前沿」2026-11-18 19:32《最高跌1元/斤！广东出鱼节奏快，缺大鱼|杰大饲料特约·加州鲈周报2026第45期》· <a class="plink" href="__URL_LU45__" target="_blank" rel="noopener">📄 阅读原文</a> · 元/斤 · 塘头价 · 正文表格核校录入</div>
</div>

""".replace("__URL_LU45__", URL_LU45)

# ---------- 4) 水产养殖网 加州鲈专题 11-18 ----------
CARD_ZTW = """<div class="card" style="margin-top:14px">
  <h3>📰 2026-11-18 · 水产养殖网 · 加州鲈专题：多地逼近 10 元关口、存塘大增，盲目越冬或面临双重损失（元/斤）</h3>
  <div class="csub">行情分析文（11-18 16:52）：11 月中旬主产区新口鱼集中上市、价格分化——<b>广东佛山 1 斤上本周报价 10.3 元/斤、环比跌 0.5，部分低价成交已降至 10 元/斤及以下</b>（接近多数养成户成本线）；<b>河南 1 斤起挑、1.3 斤以上 10.5-10.8、环比跌 0.5-0.8</b>，存塘同比明显增加。原文判断：短期弱势震荡，「佛山 1 斤上在 10 元/斤附近反复波动、跌破 10 元亦有可能」；元旦春节备货或带来小幅反弹但幅度有限。</div>
  <table><thead><tr><th>产区</th><th>规格</th><th>塘口价（元/斤）</th><th>环比 / 原文要点</th></tr></thead><tbody>
        <tr><td><span class="tag tag-lu">广东佛山</span></td><td><span class="spec spec-s">1 斤上</span></td><td class="price"><b>10.3</b></td><td style="color:#16a34a;font-size:12px">↓0.5 · 部分低价成交 ≤10，接近成本线</td></tr>
        <tr><td><span class="tag tag-lu">河南</span></td><td><span class="spec spec-s">1 斤起挑 · 1.3 斤以上</span></td><td class="price"><b>10.5-10.8</b></td><td style="color:#16a34a;font-size:12px">↓0.5-0.8 · 存塘同比大增、规格已达 1.4 斤左右</td></tr>
  </tbody></table>
  <div class="callout" style="margin-top:10px"><b>口径说明：</b>① 本卡为<b>行情分析文摘录</b>：仅原文明确给出的两处塘口价入表，湖南/湖北/浙江「平稳为主」原文未给绝对价、<b>如实留空不推算</b>。② 佛山 10.3（环比 ↓0.5）与水产前沿鲈周报 45 期「11.18 为 10.2-10.3（vs 11.11 的 10.3-10.5）」<b>对照基期不同，两卡并列、不互减不订正</b>。③ 原文三点判断（供应节奏前移 / 全国性产能扩张 / 后市弱势震荡反弹有限）为观点表述，照录不入数据。④ 与白沙洲 9.90、盛阳 10~14、视频号区间<b>多口径并存、禁止互减</b>。</div>
  <div class="legend">来源：微信公众号「水产养殖网」2026-11-18 16:52《多地逼近10元关口！加州鲈集中上市，存塘大增后市怎么看？盲目越冬，或将面临双重损失》· <a class="plink" href="__URL_ZTW__" target="_blank" rel="noopener">📄 阅读原文</a> · 元/斤 · 正文文字核校录入</div>
</div>

""".replace("__URL_ZTW__", URL_ZTW)

# ---------- 5) 盛阳 11.19 ----------
CARD_SY = """<div class="card" style="margin-top:14px">
  <h3>🛒 2026.11.19 · 无锡盛阳食品城 水产类批发价（鳜鱼 / 鲈鱼）</h3>
  <div class="csub">用户提交「盛阳食品城」2026.11.19 水产类批发价表格截图：<b>鳜鱼（桂花）25~30 元/斤、鲈鱼 10~14 元/斤</b>，与 11.15 / 11.16 / 11.17 三期卡<b>逐项同值</b>，四期连续同区间、<b>原文未标「沿用」，如实并列照录、不推断涨跌、不重复计数</b>。其余水产行按约定不录入。</div>
  <table><thead><tr><th>品种</th><th>口径</th><th>11.19 批发价</th><th>备注</th></tr></thead><tbody>
        <tr><td><span class="tag tag-gui">鳜鱼</span>（桂花）</td><td><span class="spec spec-s">无锡盛阳 · 批发</span></td><td class="price"><b>25~30 元/斤</b></td><td style="font-size:12px">与 11.15 / 11.16 / 11.17 同值四连并列，未标沿用</td></tr>
        <tr><td><span class="tag tag-lu">鲈鱼</span></td><td><span class="spec spec-s">无锡盛阳 · 批发</span></td><td class="price"><b>10~14 元/斤</b></td><td style="font-size:12px">与 11.15 / 11.16 / 11.17 同值四连并列，未标沿用</td></tr>
  </tbody></table>
  <div class="callout" style="margin-top:10px"><b>口径说明：</b>① 本卡为<b>无锡本地销区批发价（元/斤）</b>，离宜兴官林最近的本地批发锚点；与塘口价（鳜康泰 11-18 江苏标鳜 24.5）、白沙洲批发（30.25 / 9.90 折算）、加州鲈周报 45 期江苏 9.5-10.5<b>多口径并存、禁止互减</b>。② 四日连续同值且原文未标「沿用」，<b>同值并列、不推断涨跌、不重复计数</b>。③ 区间宽（鳜鱼 25~30 跨 5 元）为该市场统货口径，未给规格细分，照录。</div>
  <div class="legend">来源：「盛阳食品城」2026.11.19 水产类批发价表格 · 📷 用户截图核校录入 · 元/斤 · 本地批发参考价</div>
</div>

"""

# ---------- 6) 小洁 11-19 ----------
CARD_XJ = """<div class="card" style="margin-top:14px">
  <h3>🎬 11月19日 · 视频号「互联惠农小洁」全国参考塘口价（元/斤）</h3>
  <div class="csub">用户提交视频号截图（封面「11月19日！全国最新塘口鱼价出炉！」）：鳜鱼 (0.8-1.2斤) <b>32.5~34.0 元/斤</b>、鲈鱼 (0.8-1.2斤) <b>11.8~13.2 元/斤</b>。底部提示「以上为全国参考均价，各地行情有差异」。其余品种按约定不录入。</div>
  <table><thead><tr><th>品种</th><th>规格</th><th>参考塘口价</th><th>原文说明</th></tr></thead><tbody>
        <tr><td><span class="tag tag-gui">鳜鱼</span></td><td><span class="spec spec-s">0.8-1.2 斤</span></td><td class="price"><b>32.5~34.0 元/斤</b></td><td style="font-size:12px">全国参考均价，各地有差异</td></tr>
        <tr><td><span class="tag tag-lu">鲈鱼</span></td><td><span class="spec spec-s">0.8-1.2 斤</span></td><td class="price"><b>11.8~13.2 元/斤</b></td><td style="font-size:12px">全国参考均价，各地有差异</td></tr>
  </tbody></table>
  <div class="callout" style="margin-top:10px"><b>口径说明：</b>① 视频号为<b>全国参考均价区间</b>口径，与塘口分产区报价（鳜康泰 11-18 苏标鳜 24.5）、白沙洲批发 30.25<b>规格·渠道双重差异，禁止互减</b>。② 与 11-17 期（鳜 33.0~34.5 / 鲈 12.0~13.3）<b>相邻期数值接近但未标沿用、未给涨跌，如实并列、不推断涨跌、不重复计数</b>。</div>
  <div class="legend">来源：视频号「互联惠农小洁」2026-11-19 · 📷 用户截图核校录入 · 元/斤 · 全国参考塘口价</div>
</div>

"""

# ---------- 7) 服务于老师 11-19 ----------
CARD_YS = """<div class="card" style="margin-top:14px">
  <h3>🎬 11月19日 · 视频号「水产养殖服务于老师」全国参考塘口价（封面 2026.11.19 · 元/斤）</h3>
  <div class="csub">用户提交视频号截图（封面「2026.11.19 全国鱼价 涨跌一目了然」）：鳜鱼 1 斤上 <b>23-26 元/斤 ↑ 小幅上涨</b>、加州鲈 1 斤上 <b>10.0-11 元/斤 → 基本持平</b>。底部提示「行情仅做参考，具体以塘口现场议价为准」。其余品种按约定不录入。</div>
  <table><thead><tr><th>品种</th><th>规格</th><th>参考塘口价</th><th>原文箭头</th></tr></thead><tbody>
        <tr><td><span class="tag tag-gui">鳜鱼</span></td><td><span class="spec spec-s">1 斤上</span></td><td class="price"><b>23-26 元/斤</b></td><td style="color:#dc2626;font-size:12px">↑ 小幅上涨</td></tr>
        <tr><td><span class="tag tag-lu">加州鲈</span></td><td><span class="spec spec-s">1 斤上</span></td><td class="price"><b>10.0-11 元/斤</b></td><td style="font-size:12px">→ 基本持平</td></tr>
  </tbody></table>
  <div class="callout" style="margin-top:10px"><b>口径说明：</b>① 视频号<b>全国参考区间</b>口径，与塘口分产区（鳜康泰 11-18）、白沙洲批发 9.90<b>禁止互减</b>。② 与 11-17 期（鳜 23-26 ↑小幅上涨 / 鲈 10.0-11 持平）<b>逐项同值同箭头但未标沿用，如实并列、不重复计数、不作两期比较</b>。③ 鳜鱼区间 23-26 与小洁 32.5~34.0 同日同口径名称但区间差异大，<b>两卡并列照录、不互相订正</b>。</div>
  <div class="legend">来源：视频号「水产养殖服务于老师」2026-11-19 · 📷 用户截图核校录入 · 元/斤 · 全国参考塘口价</div>
</div>

"""

def anchor_pos(h3_kw):
    i = html.find(h3_kw)
    assert i > 0, "anchor h3 not found: " + h3_kw
    return html.rfind('<div class="card"', 0, i)

def balance(doc):
    tags = ["div", "table", "thead", "tbody", "tr", "td", "th", "h3", "span", "a", "b"]
    for tg in tags:
        o = len(re.findall(r"<%s(?=[\s>])" % tg, doc))
        c = len(re.findall(r"</%s>" % tg, doc))
        assert o == c, f"tag {tg}: open={o} close={c}"
    return doc

inserts = [
    (anchor_pos("全国渔业价格 ·《渔飞鱼水产行情日报 2026-11-17》"), CARD_DAILY),
    (anchor_pos("鳜康泰特约 · 全国鳜鱼报价（2026-11-16"), CARD_GT),
    (anchor_pos("10月14日 vs 10月21日 · 水产前沿《加州鲈周报》第41期"), CARD_LU45),
    (anchor_pos("2026-11-16 · 水产养殖网（强渔）"), CARD_ZTW),
    (anchor_pos("🛒 2026.11.17 · 无锡盛阳食品城"), CARD_SY),
    (anchor_pos("🎬 11月17日 · 视频号「互联惠农小洁」"), CARD_XJ + CARD_YS),
]

changed = 0
for pos, block in sorted(inserts, key=lambda x: -x[0]):
    kw = None
    # 幂等守卫：本批卡已存在则跳过
    if block.strip().split("</h3>")[0].split("<h3>")[1][:40] in html:
        pass
    html = html[:pos] + block + html[pos:]
    changed += 1

# 幂等检查（所有守卫串 h3 专属）
guards = [
    "渔飞鱼水产行情日报 2026-11-18》（发布 11-18 08:36",
    "全国鳜鱼报价（2026-11-18 · 元/斤 · 8 项 · 绝对价与 11-16 期同值",
    "《加州鲈周报》第45期：最高跌 1 元/斤",
    "水产养殖网 · 加州鲈专题：多地逼近 10 元关口",
    "🛒 2026.11.19 · 无锡盛阳食品城",
    "🎬 11月19日 · 视频号「互联惠农小洁」",
    "🎬 11月19日 · 视频号「水产养殖服务于老师」",
]
dup = [g for g in guards if html.count(g) > 1]
assert not dup, ("dup guards", dup)

# ---------- chip 快览替换 ----------
CHIP_REPL = [
    ("11-14日报/11-15日报/11-16日报/11-17日报）", "11-14日报/11-15日报/11-16日报/11-17日报/11-18日报）"),
    ("鳜康泰特约（10-28/10-31/11-01/11-02/11-05/11-07/11-09/11-14/11-16）", "鳜康泰特约（10-28/10-31/11-01/11-02/11-05/11-07/11-09/11-14/11-16/11-18）"),
    ("视频号·小洁（10-07~09/14/15/17/26/30/11-02/11-03/11-04/11-05/11-06/11-08/11-09/11-10/11-15/11-17）", "视频号·小洁（10-07~09/14/15/17/26/30/11-02/11-03/11-04/11-05/11-06/11-08/11-09/11-10/11-15/11-17/11-19）"),
    ("于老师（10-21/26/27/29/31·11-02/11-03/11-04/11-05/11-06/11-09/11-10/11-13/11-17）", "于老师（10-21/26/27/29/31·11-02/11-03/11-04/11-05/11-06/11-09/11-10/11-13/11-17/11-19）"),
    ("盛阳食品城（10.27/10.28/10.30/11.2/11.3/11.4/11.5/11.6/11.8/11.9/11.10/11.15/11.16/11.17批发）", "盛阳食品城（10.27/10.28/10.30/11.2/11.3/11.4/11.5/11.6/11.8/11.9/11.10/11.15/11.16/11.17/11.19批发）"),
    ("水产养殖网（10-26 周报 / 10-28 加州鲈专题 / 11-02 多点回暖 / 11-03 鳜鱼止跌回暖 / 11-04 冻伤风险专题 / 11-09 / 11-16 特水鱼周报）", "水产养殖网（10-26 周报 / 10-28 加州鲈专题 / 11-02 多点回暖 / 11-03 鳜鱼止跌回暖 / 11-04 冻伤风险专题 / 11-09 / 11-16 特水鱼周报 / 11-18 加州鲈专题）"),
    ("加州鲈周报第41期（10-21）", "加州鲈周报第41期（10-21）/ 第45期（11-18）"),
]
for old, new in CHIP_REPL:
    assert html.count(old) == 1, ("chip", old[:40], html.count(old))
    html = html.replace(old, new, 1)

balance(html)
open(F, "w", encoding="utf-8").write(html)
print("inserted blocks:", changed)
print("guards unique OK")
print("chip replaced:", len(CHIP_REPL))
