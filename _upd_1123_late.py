# -*- coding: utf-8 -*-
"""11-23 深夜批：插入 4 张新卡（鳜康泰 11-23 / 水产前沿 40 期 / 腾氏㊻ / 盛阳 11-23）
幂等守卫 + chip 4 处 + 精确标签配平。跳过杰大 42 期旧数据、4 篇病害软文、重复视频号截图。
"""
import re, sys
TAGS = ["div","table","thead","tbody","tr","td","th","h3","span","a","b","section","sup","li"]

def balance(s):
    return {t:(len(re.findall(r"<"+t+r"(?=[\s>])",s)), len(re.findall(r"</"+t+r">",s))) for t in TAGS}

def assert_balanced(s, label):
    bad = {t:v for t,v in balance(s).items() if v[0]!=v[1]}
    if bad:
        print("[FATAL] 标签不配平", label, bad); sys.exit(2)

def rep(s, old, new, label):
    n=s.count(old)
    if n!=1:
        print(f"[FATAL] 替换锚点不唯一 @ {label}: count={n}"); sys.exit(2)
    print(f"[ok] rep {label}")
    return s.replace(old,new,1)

def insert_before(s, anchor, card, label):
    n=s.count(anchor)
    if n!=1:
        print(f"[FATAL] 插入锚点不唯一 @ {label}: count={n}"); sys.exit(2)
    assert_balanced(card, label+" / 卡片自身")
    print(f"[ok] insert {label} ({len(card.encode('utf-8'))} B)")
    return s.replace(anchor, card+"\n"+anchor, 1)

# ── 卡1 鳜康泰 11-23（兴渔派-鳜鱼通 18:24 · 小鳜涨 0.5）──
# ⚠️ GUI_POND_SPECS 会命中「🐟 鳜康泰特约」，与渔有福 11-23 同日期。
# 主表严格 3 列（产区/规格/塘口价），江苏行第 1 列纯「江苏」。
# csub 规避「上涨/下跌/未给涨跌」字面触发词（涨跌表述放 callout）。
CARD_GUIKANGTAI = """<div class="card" style="margin-top:14px">
  <h3>🐟 鳜康泰特约 · 全国鳜鱼报价（2026-11-23 · 元/斤 · 8 项 · 小鳜 19.5→20 涨 0.5、其余 7 项与 11-22 同值）</h3>
  <div class="csub">「兴渔派-鳜鱼通」2026-11-23 18:24 发布《11月23日鳜鱼价格行情!丨鳜康泰特约·全国鳜鱼报价》。原文「<b>11月23日，小鳜价格涨0.5元/斤</b>」。规格价：<b>小鳜（0.8斤以下）20、标鳜（0.8~1.5斤）22.5、中鳜（1.5~2斤）19</b> 元/斤；分省标鳜：湖北 24.5、安徽 23.5、江西 25.5、湖南 24.5、江苏 24 元/斤左右。与同号 11-22 卡（小鳜 19.5 / 标鳜 22.5 / 中鳜 19，五省标鳜同值）逐项对照，仅<b>小鳜 19.5→20</b> 一项变化，其余七项同值。</div>
  <table><thead><tr><th>产区</th><th>规格</th><th>塘口价（元/斤）</th></tr></thead><tbody>
        <tr><td>全国</td><td>小鳜（0.8 斤以下）</td><td class="price"><b>20</b></td></tr>
        <tr><td>全国</td><td>标鳜（0.8~1.5 斤）</td><td class="price"><b>22.5</b></td></tr>
        <tr><td>全国</td><td>中鳜（1.5~2 斤）</td><td class="price"><b>19</b></td></tr>
        <tr><td>湖北</td><td>标鳜</td><td class="price"><b>24.5</b></td></tr>
        <tr><td>安徽</td><td>标鳜</td><td class="price"><b>23.5</b></td></tr>
        <tr><td>江西</td><td>标鳜</td><td class="price"><b>25.5</b></td></tr>
        <tr><td>湖南</td><td>标鳜</td><td class="price"><b>24.5</b></td></tr>
        <tr><td><span class="tag tag-gui">江苏</span></td><td>标鳜（原文「24 元/斤左右」）</td><td class="price"><b>24</b></td></tr>
  </tbody></table>
  <div class="callout" style="margin-top:10px"><b>跨期核校 / 口径说明：</b>① 本卡与同号 11-22 卡<b>同市场同规格</b>：原文明确「小鳜价格涨 0.5 元/斤」（19.5→20），其余七项逐项同值；<b>按原文照录，不自行相减、不推断其余项涨跌</b>。② 「全国规格价」（小鳜 20 / 标鳜 22.5 / 中鳜 19）与「分省标鳜」（23.5~25.5）<b>口径不同（全国 vs 分省、含规格档差异），不可直接比较、不互减</b>。③ 江苏标鳜 24 与渔有福 11-23 江苏 24 同值同渠道，<b>两份独立发布各自照录，不重复计数、不推断涨跌</b>；与腾氏㊻ 11-23 环太湖实际成交 8.8~9 元/斤（加州鲈、非鳜鱼）品种不同。④ 本卡为<b>塘口价（元/斤）</b>，与通威全国均价、分市场批发（元/公斤）、盛阳本地批发、视频号参考区间、次日预测<b>多口径并存、禁止互减</b>。</div>
  <div class="legend">来源：微信公众号「兴渔派-鳜鱼通」2026-11-23 18:24《11月23日鳜鱼价格行情!丨鳜康泰特约·全国鳜鱼报价》· <a class="plink" href="https://mp.weixin.qq.com/s/X47fx6v4VX7zJqwQRvnz-g" target="_blank" rel="noopener">📄 阅读原文</a> · 元/斤 · 塘口价 · 正文核校录入</div>
</div>"""

# ── 卡2 水产前沿特水鱼周报 40 期（19:10 · 鳜鱼/加州鲈 11.17 vs 11.23 双列）──
CARD_QIANYAN40 = """<div class="card" style="margin-top:14px">
  <h3>📰 2026-11-23 · 水产前沿 · 特水鱼周报 2026 第 40 期：鳜鱼最高跌 1.5 元、加州鲈最高跌 1 元（11.17 vs 11.23 · 元/斤）</h3>
  <div class="csub">「水产前沿」2026-11-23 19:10 发布第 40 期特水鱼周报，双列对照 11.17 vs 11.23。<b>鳜鱼：最高跌 1.5 元/斤</b>——佛山 3成中鳜 22→21、2成中鳜 23→22、1成中鳜 24-24.5→22.5-23（跌 1.5），1成小鳜 21-22 持平、2成小鳜 19-20 持平；<b>江苏标鳜 24-25 持平</b>，湖南 24.5 持平，<b>湖北 26→25-26 跌 1</b>，江西 25-26 / 广西 26 持平，安徽 24→23-25（原文环比标「→」）。<b>加州鲈：最高跌 1 元/斤</b>——佛山 8两上 9-10 / 1斤上 10.3 持平，<b>浙江湖州 11-11.5→10.5-11 跌 0.5</b>、<b>江苏吴江 10.5-11.5→9.5-10.5 跌 1</b>、<b>河南郑州 11→10.5 跌 0.5</b>，四川 / 湖南 / 湖北持平。生鱼、黄颡鱼、江团、金鲳鱼按约定不录入。</div>
  <table><thead><tr><th>鳜鱼 产区/规格</th><th>11.17（元/斤）</th><th>11.23（元/斤）</th><th>环比</th></tr></thead><tbody>
        <tr><td><span class="tag tag-gui">佛山</span> 3成中鳜</td><td class="price"><b>22</b></td><td class="price"><b>21</b></td><td style="color:#12a150;font-size:12px">▼ 1↓</td></tr>
        <tr><td><span class="tag tag-gui">佛山</span> 2成中鳜</td><td class="price"><b>23</b></td><td class="price"><b>22</b></td><td style="color:#12a150;font-size:12px">▼ 1↓</td></tr>
        <tr><td><span class="tag tag-gui">佛山</span> 1成中鳜</td><td class="price"><b>24-24.5</b></td><td class="price"><b>22.5-23</b></td><td style="color:#12a150;font-size:12px">▼ 1.5↓</td></tr>
        <tr><td><span class="tag tag-gui">佛山</span> 1成小鳜</td><td class="price"><b>21-22</b></td><td class="price"><b>21-22</b></td><td style="font-size:12px">→</td></tr>
        <tr><td><span class="tag tag-gui">佛山</span> 2成小鳜</td><td class="price"><b>19-20</b></td><td class="price"><b>19-20</b></td><td style="font-size:12px">→</td></tr>
        <tr><td><span class="tag tag-gui">江苏</span> 标鳜</td><td class="price"><b>24-25</b></td><td class="price"><b>24-25</b></td><td style="font-size:12px">→ · 离宜兴官林最近的分产区口径</td></tr>
        <tr><td><span class="tag tag-gui">湖南</span> 标鳜</td><td class="price"><b>24.5</b></td><td class="price"><b>24.5</b></td><td style="font-size:12px">→</td></tr>
        <tr><td><span class="tag tag-gui">湖北</span> 标鳜</td><td class="price"><b>26</b></td><td class="price"><b>25-26</b></td><td style="color:#12a150;font-size:12px">▼ 1↓</td></tr>
        <tr><td><span class="tag tag-gui">江西</span> 标鳜</td><td class="price"><b>25-26</b></td><td class="price"><b>25-26</b></td><td style="font-size:12px">→</td></tr>
        <tr><td><span class="tag tag-gui">广西</span> 标鳜</td><td class="price"><b>26</b></td><td class="price"><b>26</b></td><td style="font-size:12px">→</td></tr>
        <tr><td><span class="tag tag-gui">安徽</span> 标鳜</td><td class="price"><b>24</b></td><td class="price"><b>23-25</b></td><td style="font-size:12px">原文环比标「→」，照录不推断</td></tr>
  </tbody></table>
  <table style="margin-top:8px"><thead><tr><th>加州鲈 产区/规格</th><th>11.17（元/斤）</th><th>11.23（元/斤）</th><th>环比</th></tr></thead><tbody>
        <tr><td><span class="tag tag-lu">广东佛山</span> 8两上</td><td class="price"><b>9-10</b></td><td class="price"><b>9-10</b></td><td style="font-size:12px">→</td></tr>
        <tr><td><span class="tag tag-lu">广东佛山</span> 1斤上</td><td class="price"><b>10.3</b></td><td class="price"><b>10.3</b></td><td style="font-size:12px">→</td></tr>
        <tr><td><span class="tag tag-lu">浙江湖州</span> 8成统货</td><td class="price"><b>11-11.5</b></td><td class="price"><b>10.5-11</b></td><td style="color:#12a150;font-size:12px">▼ 0.5↓</td></tr>
        <tr><td><span class="tag tag-lu">江苏吴江</span> 9两上</td><td class="price"><b>10.5-11.5</b></td><td class="price"><b>9.5-10.5</b></td><td style="color:#12a150;font-size:12px">▼ 1↓</td></tr>
        <tr><td><span class="tag tag-lu">四川成都</span> 9两上</td><td class="price"><b>10.5</b></td><td class="price"><b>10.5</b></td><td style="font-size:12px">→</td></tr>
        <tr><td><span class="tag tag-lu">湖南华容</span> 9两上</td><td class="price"><b>10.5</b></td><td class="price"><b>10.5</b></td><td style="font-size:12px">→</td></tr>
        <tr><td><span class="tag tag-lu">湖北武汉</span> 8.5两上</td><td class="price"><b>10.5</b></td><td class="price"><b>10.5</b></td><td style="font-size:12px">→</td></tr>
        <tr><td><span class="tag tag-lu">河南郑州</span> 1斤上</td><td class="price"><b>11</b></td><td class="price"><b>10.5</b></td><td style="color:#12a150;font-size:12px">▼ 0.5↓</td></tr>
  </tbody></table>
  <div class="callout" style="margin-top:10px"><b>多口径说明：</b>① 本卡为<b>塘头/出塘参考价（元/斤）</b>，双列对照为该报自身给出的环比口径，仅照录原文。② 与同日 11-23「水产养殖网（强渔）」卡口径不同：强渔仅给本期绝对价、原文定性「多产区跌 0.5~1」，本卡给出 11.17 vs 11.23 双列及逐项环比；<b>两源分列照录、不互减、不互相订正</b>（如江苏标鳜本卡 24-25 vs 强渔 25、加州鲈江苏本卡吴江 9两上 9.5-10.5 vs 强渔 1斤起 9.5-10.5，规格口径不同）。③ 与鳜康泰 11-23（江苏 24）、渔有福 11-23（江苏 24）、通威全国均价、分市场批发（元/公斤）、盛阳本地批发、视频号参考区间、次日预测<b>规格·渠道·时间三重不同，多口径并存、禁止互减</b>。④ 生鱼 / 黄颡鱼 / 江团 / 金鲳鱼等非目标品种按约定不录入。</div>
  <div class="legend">来源：微信公众号「水产前沿」2026-11-23 19:10《逆势反弹生鱼涨0.5元/斤！鳜鱼、加州鲈双双下跌，黄颡、江团、金鲳？｜特水鱼周报2026第40期》· <a class="plink" href="https://mp.weixin.qq.com/s/YAED-9DEp7BC-wGo66C_gw" target="_blank" rel="noopener">📄 阅读原文（特水鱼周报第 40 期）</a> · 元/斤 · 塘头/出塘参考价，受规格条形影响仅供参考 · 截图 + 正文双核录入</div>
</div>"""

# ── 卡3 腾氏看上上报价㊻（19:34 · 加州鲈塘口专题）──
CARD_TENGSHI46 = """<div class="card" style="margin-top:14px">
  <h3>🔥 11月23日 · 腾氏水产商务网「高端水产 · 看上上报价㊻」：广东 1 斤上 9.7-9.8、多地跌 0.5（元/斤）</h3>
  <div class="csub">「腾氏水产商务网」2026-11-23 19:34 发布看上上报价第 46 期（加州鲈塘口专题；与 11-16 ㊺ 期间隔一期，<b>隔期照录、不作两期比较</b>）。<b>广东 1 斤上 9.7-9.8、8成1斤上 9.5-9.6、5-6成1斤上 9</b>（要求条形好，看鱼头 / 大鱼比例发价）；流通商称 9成1斤上靓鱼「卖不动」，养殖户年底清塘付饲料款、外省水车带动有限。<b>环太湖平 9 两打样价 1 元/两左右、实际成交 8.8-9 元/斤</b>（按鱼头大小 / 条形 / 均重定价；「元/两」为另一口径，<b>不折算不互减</b>）。<b>湖南华容 9 两起 9.5、湖北武汉 9 两上起 9.5，均较上周跌 0.5</b>；四川成都 1 斤上 10.5-11 持平。本卡为加州鲈塘口专题，<b>无鳜鱼条目，如实留空</b>。</div>
  <table><thead><tr><th>加州鲈 产区</th><th>规格</th><th>11-23 塘口价（元/斤）</th><th>原文标注</th></tr></thead><tbody>
        <tr><td><span class="tag tag-lu">广东</span></td><td><span class="spec spec-s">1 斤上</span></td><td class="price"><b>9.7-9.8</b></td><td style="font-size:12px">较上周下跌 0.3 元（原文标题）</td></tr>
        <tr><td><span class="tag tag-lu">广东</span></td><td><span class="spec spec-s">8 成 1 斤上</span></td><td class="price"><b>9.5-9.6</b></td><td style="font-size:12px">—</td></tr>
        <tr><td><span class="tag tag-lu">广东</span></td><td><span class="spec spec-s">5-6 成 1 斤上</span></td><td class="price"><b>9</b></td><td style="font-size:12px">要求条形好、看鱼头发价</td></tr>
        <tr><td><span class="tag tag-lu">环太湖</span></td><td><span class="spec spec-s">平 9 两</span></td><td class="price"><b>8.8-9</b></td><td style="font-size:12px">实际成交价 · 打样价 1 元/两（另一口径不折算）</td></tr>
        <tr><td><span class="tag tag-lu">湖南华容</span></td><td><span class="spec spec-s">9 两起抓</span></td><td class="price"><b>9.5</b></td><td style="color:#12a150;font-size:12px">较上周跌 0.5</td></tr>
        <tr><td><span class="tag tag-lu">湖北武汉</span></td><td><span class="spec spec-s">9 两上起抓</span></td><td class="price"><b>9.5</b></td><td style="color:#12a150;font-size:12px">较上周跌 0.5</td></tr>
        <tr><td><span class="tag tag-lu">四川成都</span></td><td><span class="spec spec-s">1 斤上</span></td><td class="price"><b>10.5-11</b></td><td style="font-size:12px">与上周持平</td></tr>
  </tbody></table>
  <div class="callout" style="margin-top:10px"><b>口径说明：</b>① 本卡为<b>加州鲈塘口价（元/斤）</b>，与强渔 11-23（江苏 1 斤起 9.5-10.5）、水产前沿 40 期 11-23（吴江 9 两上 9.5-10.5）、通威全国塘口均价、白沙洲批发、盛阳本地批发 10~14、次日预测<b>渠道·规格·时间三重不同，多口径并存、禁止互减</b>。② 环太湖「打样价 1 元/两」与「实际成交 8.8-9 元/斤」为同一产区并列的两种口径，<b>只照录实际成交（元/斤），不折算、不互减</b>。③ 与 11-16 ㊺ 卡隔期，<b>只列本期数值与原文涨跌标注，不作两期比较</b>。④ 「看上上报价」与「腾氏一周鱼价播报（通威同源）」「海南卓越联合播报」为三个不同内容系列，分源登记。</div>
  <div class="legend">来源：微信公众号「腾氏水产商务网」2026-11-23 19:34《广东鲈价再跌0.3元！靓鱼卖不动、空塘在增多，加州鲈年底"两头冷"｜高端水产·看上上报价㊻》· <a class="plink" href="https://mp.weixin.qq.com/s/8fWQMvXnk5WVVL97akYcWw" target="_blank" rel="noopener">📄 阅读原文（看上上报价㊻ 11-23）</a> · 元/斤 · 塘口价，受条形均重影响仅供参考 · 正文核校录入</div>
</div>"""

# ── 卡4 盛阳 11-23（当日均价 · 鳜鱼栏空白；25-30 实为「翘嘴」行）──
CARD_SHENGYANG = """<div class="card" style="margin-top:14px">
  <h3>🛒 2026.11.23 · 无锡盛阳食品城 水产类批发价（鳜鱼栏本期空白 / 鲈鱼 10~14 元/斤同值）</h3>
  <div class="csub">用户提交「盛阳食品城」2026.11.23 水产类批发价表格截图，表头「当日均价、仅供参考」。杂鱼 / 淡水鱼类批发价：<b>鲈鱼 10~14 元/斤</b>；<b>鳜鱼一行价格栏为空白</b>——同表「25~30」对应的是上一行<b>翘嘴</b>，<b>非鳜鱼，按红线不录入、不以同值沿用填充</b>。其他品种（白鱼、鲫鱼、白鲳、草鱼、花鲢、鳊鱼、青鱼、鲤鱼等）及虾蟹、龟鳖类按约定不录入。</div>
  <table><thead><tr><th>品种</th><th>口径</th><th>批发价（元/斤）</th></tr></thead><tbody>
        <tr><td><span class="tag tag-gui">鳜鱼（桂鱼）</span></td><td>当日均价 · 仅供参考</td><td class="price"><b>—</b></td></tr>
        <tr><td><span class="tag tag-lu">鲈鱼</span></td><td>当日均价 · 仅供参考</td><td class="price"><b>10~14</b></td></tr>
  </tbody></table>
  <div class="callout" style="margin-top:10px"><b>口径说明：</b>① 本期表格<b>鳜鱼价格栏为空白</b>，按红线<b>如实留空、不以 11-22 的 25~30 沿用填充、不推断涨跌</b>；同表「25~30」经截图逐行核校为「翘嘴」行价格，<b>不可误录为鳜鱼</b>。② 鲈鱼 10~14 与 11-19 / 11-20 / 11-22 卡逐项同值，为不同日期的当日报价快照，<b>同值并列、原文未给涨跌、不推断涨跌、不作两期比较</b>。③ 本卡为<b>本地销区批发价（元/斤，当日均价）</b>，与塘口价（鳜康泰 11-23 江苏标鳜 24、渔有福 11-23 江苏 24、腾氏㊻ 11-23 加州鲈广东 9.7-9.8）、全国均价、分市场批发（元/公斤）、白沙洲批发、视频号参考区间、次日预测<b>多口径并存、禁止互减</b>。</div>
  <div class="legend">来源：无锡盛阳食品城水产类批发价表 2026.11.23 · 当日均价 · 仅供参考 · 📷 用户截图核校录入（鳜鱼空白如实留空）</div>
</div>"""

ANCHORS = [
    ('<h3>🐟 鳜康泰特约 · 全国鳜鱼报价（2026-11-22', CARD_GUIKANGTAI, '鳜康泰 11-23'),
    ('<h3>📰 2026-11-17 · 水产前沿 · 特水鱼周报 2026 第 39 期', CARD_QIANYAN40, '水产前沿 40 期'),
    ('<h3>🔥 11月16日 · 腾氏水产商务网「高端水产 · 看上上报价㊺」', CARD_TENGSHI46, '腾氏㊻ 11-23'),
    ('<h3>🛒 2026.11.22 · 无锡盛阳食品城', CARD_SHENGYANG, '盛阳 11-23'),
]

CHIP_SUBS = [
    ('鳜康泰特约（10-28/10-31/11-01/11-02/11-05/11-07/11-09/11-14/11-16/11-18/11-19/11-22）',
     '鳜康泰特约（10-28/10-31/11-01/11-02/11-05/11-07/11-09/11-14/11-16/11-18/11-19/11-22/11-23）', 'chip 鳜康泰'),
    ('水产前沿特水鱼周报（10-26 / 11-02 / 11-17 第39期）',
     '水产前沿特水鱼周报（10-26 / 11-02 / 11-17 第39期 / 11-23 第40期）', 'chip 水产前沿'),
    ('腾氏上上报价加州鲈（10-26 ㊷ / 11-02 / 11-16 ㊺）',
     '腾氏上上报价加州鲈（10-26 ㊷ / 11-02 / 11-16 ㊺ / 11-23 ㊻）', 'chip 看上上'),
    ('11.15/11.16/11.17/11.19/11.20/11.22批发）',
     '11.15/11.16/11.17/11.19/11.20/11.22/11.23批发）', 'chip 盛阳'),
]

GUARDS = [
    '🐟 鳜康泰特约 · 全国鳜鱼报价（2026-11-23',
    '📰 2026-11-23 · 水产前沿 · 特水鱼周报 2026 第 40 期',
    '🔥 11月23日 · 腾氏水产商务网「高端水产 · 看上上报价㊻」',
    '🛒 2026.11.23 · 无锡盛阳食品城 水产类批发价',
]

def main():
    p = '鳜鱼鲈鱼价格看板.html'
    s = open(p, encoding='utf-8').read()
    pre = balance(s)
    bad = {t:v for t,v in pre.items() if v[0]!=v[1]}
    if bad:
        print("[FATAL] 写盘前页面已不配平", bad); sys.exit(2)
    # 幂等：守卫全在 → SKIP；部分在 → 拒绝
    cnt = [s.count(g) for g in GUARDS]
    if all(c==1 for c in cnt):
        print("[SKIP] 4 张卡守卫已全部存在"); return
    if any(c>0 for c in cnt):
        print("[FATAL] 部分守卫已存在，拒绝重跑", cnt); sys.exit(2)
    for a,c,l in ANCHORS:
        s = insert_before(s, a, c, l)
    for o,n,l in CHIP_SUBS:
        s = rep(s, o, n, l)
    post = balance(s)
    bad2 = {t:(pre[t],post[t]) for t in TAGS if pre[t]!=post[t]}
    # 4 卡引入的标签增量应自洽
    print('[info] 标签增量:', {t:(post[t][0]-pre[t][0], post[t][1]-pre[t][1]) for t in TAGS if post[t]!=pre[t]})
    # 最终整页必须配平
    bad3 = {t:v for t,v in post.items() if v[0]!=v[1]}
    if bad3:
        print("[FATAL] 写盘后页面不配平", bad3); sys.exit(2)
    open(p,'w',encoding='utf-8').write(s)
    print(f'[ok] 写盘完成，字节 {len(s.encode("utf-8"))}')
    print('[ok] 4 卡守卫:', [s.count(g) for g in GUARDS])

if __name__=='__main__':
    main()
