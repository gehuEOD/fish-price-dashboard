# -*- coding: utf-8 -*-
"""11-23 晚间批：6 链接 + 5 截图 → 新增 5 张卡 + chip 日期串同步。

判定结论（原文 / 截图三路核校）：
  rCpArgbbahT2jsDLoDuNfw  通威农牧 11-20 一周鱼价 —— 已录，跳过
  2S68t_7Anqpu_2K7fieFog  全国渔业价格 11-24 早报 —— 新卡
  HhkAFKbelQp_0_tQWvUF6Q  水产养殖网（强渔）11-23 特水鱼周报 —— 新卡
  0fXyBh5y8a4kHDQ9Kk3elw  渔无忧在线 11-23 次日预报 —— 新卡
  o1taaGFc5g-vWB-l_7sT5Q  科学养鱼 11-23 正文图分市场批发价 —— 新卡（kexue_web）
  6CGBdtPqWmczRefl9RLfDg  江苏凌家塘 11/15~11/21 一周行情 —— 新卡

红线：多口径并存禁止互减；鮰鱼 / 花鲈 / 黑鱼 / 黄颡 / 麦鲮等非目标品种不录；
      原文未给绝对价如实留空；同号隔期不互减不推断统一涨跌。
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
HTML = ROOT / "鳜鱼鲈鱼价格看板.html"

# ── 幂等守卫：每张卡 h3 的专属唯一串，必须与卡内 h3 逐字一致 ────────────────
GUARDS = [
    "📰 全国渔业价格 ·《渔飞鱼水产行情日报 2026-11-24》",
    "📰 2026-11-23 · 水产养殖网（强渔）· 特水鱼周报",
    "预报 📅 渔无忧在线 ·《最新水产行情预报》（发布 11月23日 16:05",
    "🌊 2026-11-23 · 科学养鱼 分市场批发价（鳜鱼 7 市场",
    "🏪 江苏凌家塘市场 · 一周价格行情（2026/11/15~11/21",
]

TAGS = ["div", "table", "thead", "tbody", "tr", "td", "th", "h3",
        "span", "a", "b", "section", "sup", "li"]


def balance(s):
    """用 <tag(?=[\\s>]) 精确匹配开标签，避免 <th 误算 <thead、<b 误算 <body/br。"""
    out = {}
    for t in TAGS:
        o = len(re.findall(r"<" + t + r"(?=[\s>])", s))
        c = len(re.findall(r"</" + t + r">", s))
        out[t] = (o, c)
    return out


def assert_balanced(s, label):
    bad = {t: v for t, v in balance(s).items() if v[0] != v[1]}
    if bad:
        print("[FATAL] 标签不配平 @", label, bad)
        sys.exit(2)
    print("[ok] 标签配平 @", label)


def rep(s, old, new, label):
    n = s.count(old)
    if n != 1:
        print(f"[FATAL] 锚点不唯一 @ {label}: count={n} old={old[:60]!r}")
        sys.exit(2)
    print(f"[ok] rep {label}")
    return s.replace(old, new, 1)


def insert_before(s, anchor, card, label):
    n = s.count(anchor)
    if n != 1:
        print(f"[FATAL] 插入锚点不唯一 @ {label}: count={n}")
        sys.exit(2)
    # 卡片自身必须配平，否则插入后整页失衡
    assert_balanced(card, label + " / 卡片自身")
    print(f"[ok] insert {label} ({len(card)} B)")
    return s.replace(anchor, card + "\n" + anchor, 1)


# ══════════════════════════════════════════════════════════════════════
# 卡 1 · 全国渔业价格《渔飞鱼水产行情日报 2026-11-24》（次日 11/24 早报口径）
# ══════════════════════════════════════════════════════════════════════
CARD_MINJIAN = """<div class="card" style="margin-top:14px">
  <h3>📰 全国渔业价格 ·《渔飞鱼水产行情日报 2026-11-24》（发布 11-23 18:00 · 次日 11/24 周二早报参考价 · 鳜鱼 30.25 回吐 / 加州鲈 11.80 平 / 鲈鱼 9.68 回落）</h3>
  <div class="csub">「全国渔业价格」2026-11-23 18:00 发布 11-24 期《渔飞鱼水产行情日报》，原文标注「11月24日 星期二 · 全国水产品行情早报」，通篇为<b>次日（11/24）出鱼参考价与行情预判口径</b>，非 11-23 实测成交。原文自述「<b>鲈鱼鳜鱼回吐</b>」：<b>鳜鱼 30.25 元/斤</b>（白沙洲 ≥750g 60.50 元/公斤，03 段另列宜昌 66.00 元/公斤、价差 2.75 元/斤）、<b>鲈鱼 ≥500g 19.65→19.35 元/公斤＝9.68 元/斤（-1.5%）</b>、<b>加州鲈产地均价 11.80 元/斤，原文标「平（11/23）」</b>。原文 02 表「<b>鮰鱼 两湖绿谷 500-1000 10.00（11/23新报）</b>」为斑点叉尾鮰，<b>非鳜鱼，按红线不录入</b>。</div>
  <table><thead><tr><th>品种</th><th>渠道 · 规格</th><th>11-24 早报参考价（元/斤）</th><th>原文标注</th></tr></thead><tbody>
        <tr><td><span class="tag tag-gui">鳜鱼</span></td><td>白沙洲 ≥750g（60.50 元/公斤）</td><td class="price"><b>30.25</b></td><td style="font-size:12px">原文「回吐」；宜昌 66.00 元/公斤，原文自述价差 2.75 元/斤</td></tr>
        <tr><td><span class="tag tag-lu">加州鲈</span></td><td>产地均价 · 鲜活</td><td class="price"><b>11.80</b></td><td style="font-size:12px">平（11/23）</td></tr>
        <tr><td>鲈鱼（白沙洲）</td><td>≥500g</td><td class="price"><b>9.68</b></td><td style="color:#12a150;font-size:12px">19.65→19.35 元/公斤（原文「一天掉1毛5」· -1.5%）</td></tr>
        <tr><td><span class="tag tag-gui">鳜鱼</span></td><td>500~750g / 250~500g</td><td class="price"><b>—</b></td><td style="font-size:12px">本期原文未给该两档绝对价，如实留空</td></tr>
  </tbody></table>
  <div class="callout" style="margin-top:10px"><b>口径说明：</b>① 本卡为<b>次日（11-24 周二）早报参考价 / 预判口径</b>（11-23 18:00 发布），与 11-23 期日报、白沙洲实测成交价、塘口价、视频号全国区间、渔无忧次日预测价<b>多口径并存、禁止互减</b>；<b>参考价 / 预测价与实测成交价禁止互减、不作命中率评价</b>。② 与 11-23 期日报（鳜 30.75 / 加州鲈 11.80 / 鲈 9.83）为<b>同号隔期</b>：原文仅定性写「鳜鱼鲈鱼回吐」、未给鳜鱼逐档前值，<b>按原文照录、不作两期数值相减、不推断统一涨跌</b>；加州鲈 11.80 同值且原文标「平」，与 11-23 期<b>如实并列、不重复计数</b>。③ 03 段「宜昌 66.00 / 白沙洲 60.50 元/公斤」为<b>分市场销地价</b>，与塘口价口径不同，价差 2.75 元/斤为原文自述照录，<b>不与其他口径互减</b>。④ 原文 02 表「鮰鱼 两湖绿谷 500-1000 10.00」经截图核校确认为<b>斑点叉尾鮰</b>，非本看板跟踪品种，<b>不录入</b>；黄颡、泥鳅、草鱼、大黄鱼、河蟹、虾类、生鱼、黄鳝等亦按约定不录入。</div>
  <div class="legend">来源：微信公众号「全国渔业价格」2026-11-23 18:00《渔飞鱼水产行情日报（2026年11月24日）》· <a class="plink" href="https://mp.weixin.qq.com/s/2S68t_7Anqpu_2K7fieFog" target="_blank" rel="noopener">📄 阅读原文（11-24 早报）</a> · 元/斤 · 次日早报参考价 · 正文 + 截图核校录入</div>
</div>"""

# ══════════════════════════════════════════════════════════════════════
# 卡 2 · 水产养殖网（强渔）11-23 特水鱼周报
# ⚠️ LU_POND_SPECS 取 tidx=1（第二张 tbody）· region_first：
#    tds[0]=产区 / tds[1]=规格 / tds[2]=价格 / tds[3]=备注
#    江苏行第 1 列必须为纯「江苏」且给出绝对价（v2「加州鲈·出塘价」KPI 只认 local 行）
#    备注刻意不写「涨/跌/+/-」字面，避免逐行 trend 被统一触发
# ══════════════════════════════════════════════════════════════════════
CARD_QIANGYU = """<div class="card" style="margin-top:14px">
  <h3>📰 2026-11-23 · 水产养殖网（强渔）· 特水鱼周报：鳜鱼多产区普跌 0.5~1 元、加州鲈出鱼加快行情回落（元/斤 · 塘口参考价）</h3>
  <div class="csub">「水产养殖网 / 强渔」2026-11-23 16:53 发布特水鱼周报。原文自述<b>鳜鱼本周全面回落</b>：广东饲料鳜集中上市，江苏、湖北、安徽同步下行，<b>多产区同步跌 0.5~1 元/斤</b>；江苏蟹塘套养鳜鱼集中起捕冲击精养塘，华中存塘基数偏大。<b>加州鲈各地加快出鱼、行情随之回落</b>，仅广东大规格优质鱼货源偏紧存在小幅抬价机会；浙江新鱼上市但走货偏慢。原文注「<b>受规格卖相等因素影响较大，仅供参考</b>」。本看板只跟踪鳜鱼 / 加州鲈两段，黑鱼、黄颡鱼、鮰鱼、麦鲮鱼等按约定不录入。</div>
  <table><thead><tr><th>鳜鱼 产区</th><th>规格</th><th>本期塘口价（元/斤）</th><th>原文要点</th></tr></thead><tbody>
        <tr><td><span class="tag tag-gui">广东</span></td><td><span class="spec spec-s">鱼仔鳜</span></td><td class="price"><b>22.5-23</b></td><td style="font-size:12px">饲料鳜集中上市、鱼价持续走弱</td></tr>
        <tr><td><span class="tag tag-gui">广东</span></td><td><span class="spec spec-s">饲料鳜</span></td><td class="price"><b>19-20</b></td><td style="font-size:12px">与鱼仔鳜分档并列，规格不同不可互减</td></tr>
        <tr><td><span class="tag tag-gui">江苏</span></td><td><span class="spec spec-s">标鱼</span></td><td class="price"><b>25</b></td><td style="font-size:12px">蟹塘套养鳜鱼集中起捕，货源流入市场</td></tr>
        <tr><td><span class="tag tag-gui">安徽</span></td><td><span class="spec spec-s">标鱼</span></td><td class="price"><b>24</b></td><td style="font-size:12px">与江苏同步下行（原文定性）</td></tr>
        <tr><td><span class="tag tag-gui">湖南</span></td><td><span class="spec spec-s">标鱼</span></td><td class="price"><b>24.5</b></td><td style="font-size:12px">原文照录</td></tr>
        <tr><td><span class="tag tag-gui">湖北</span></td><td><span class="spec spec-s">标鱼</span></td><td class="price"><b>25</b></td><td style="font-size:12px">华中存塘基数偏大、终端走货乏力</td></tr>
  </tbody></table>
  <table style="margin-top:12px"><thead><tr><th>加州鲈 产区</th><th>规格</th><th>本期塘口价（元/斤）</th><th>原文要点</th></tr></thead><tbody>
        <tr><td><span class="tag tag-lu">广东佛山</span></td><td><span class="spec spec-s">8 两起</span></td><td class="price"><b>9</b></td><td style="font-size:12px">原文「9 元/斤左右」</td></tr>
        <tr><td><span class="tag tag-lu">广东佛山</span></td><td><span class="spec spec-s">1 斤以上</span></td><td class="price"><b>10.3</b></td><td style="font-size:12px">大规格优质鱼货源偏紧</td></tr>
        <tr><td><span class="tag tag-lu">四川成都</span></td><td><span class="spec spec-s">1 斤起</span></td><td class="price"><b>11</b></td><td style="font-size:12px">原文照录</td></tr>
        <tr><td><span class="tag tag-lu">湖北</span></td><td><span class="spec spec-s">9 两起</span></td><td class="price"><b>10</b></td><td style="font-size:12px">原文照录</td></tr>
        <tr><td><span class="tag tag-lu">湖南华容</span></td><td><span class="spec spec-s">8 两起</span></td><td class="price"><b>10</b></td><td style="font-size:12px">原文照录</td></tr>
        <tr><td><span class="tag tag-lu">河南郑州</span></td><td><span class="spec spec-s">1 斤起</span></td><td class="price"><b>10.5</b></td><td style="font-size:12px">原文照录</td></tr>
        <tr><td><span class="tag tag-lu">江苏</span></td><td><span class="spec spec-s">1 斤起</span></td><td class="price"><b>9.5-10.5</b></td><td style="font-size:12px">环太湖本地锚点 · 原文自述各地加快出鱼、行情回落</td></tr>
        <tr><td><span class="tag tag-lu">浙江湖州</span></td><td><span class="spec spec-s">1 斤（原文「平1斤」）</span></td><td class="price"><b>10.5-11</b></td><td style="font-size:12px">原文「平1斤」按原文照录，不作推断</td></tr>
  </tbody></table>
  <div class="callout" style="margin-top:10px"><b>口径说明：</b>① 本卡为<b>产区塘口参考价周报</b>（11-23 16:53 发布，元/斤），与通威 / 腾氏全国均价、白沙洲日度批发、盛阳无锡本地批发、凌家塘周均价、视频号全国区间、渔无忧次日预测价<b>多口径并存、禁止互减</b>。② 原文「鳜鱼多产区同步跌 0.5~1 元/斤」「加州鲈行情回落」均为<b>定性描述，未给逐产区前值与涨跌幅度</b>；本表<b>只照录本期绝对价，不倒推前值、不推断统一涨跌、不作两期比较</b>。③ 鳜鱼广东分「鱼仔鳜 / 饲料鳜」两档、加州鲈分「8 两起 / 1 斤以上 / 1 斤起」等规格，<b>规格差异不可互减</b>；原文「受规格卖相等因素影响较大，仅供参考」照录。④ 江苏「1 斤起 9.5-10.5 元/斤」为环太湖本地行，供 2.0「加州鲈 · 出塘价」KPI 取用（该 KPI 只认带本地标记的行，取不到会渲染「—」）。⑤ 黑鱼、黄颡鱼、鮰鱼、麦鲮鱼（饵料鱼）等非目标品种按约定不录入。</div>
  <div class="legend">来源：微信公众号「水产养殖网 / 强渔」2026-11-23 16:53《利好显现！黑鱼反弹回暖，鳜鱼普跌1元，鮰鱼标涨、黄颡鱼稳中走强》· <a class="plink" href="https://mp.weixin.qq.com/s/HhkAFKbelQp_0_tQWvUF6Q" target="_blank" rel="noopener">📄 阅读原文（11-23 特水鱼周报）</a> · 元/斤 · 塘口参考价，仅供参考 · 正文核校录入</div>
</div>"""

# ══════════════════════════════════════════════════════════════════════
# 卡 3 · 渔无忧在线 11-23《最新水产行情预报》（次日 11/24 周二预测）
# ══════════════════════════════════════════════════════════════════════
CARD_YUWUYOU = """<div class="card" style="margin-top:14px">
  <h3>预报 📅 渔无忧在线 ·《最新水产行情预报》（发布 11月23日 16:05 · 次日 11月24日 周二预测口径）</h3>
  <div class="csub">「渔无忧在线」2026-11-23 16:05 发布《最新水产行情预报》，预测 <b>11-24（周二 · 腌腊备货）</b>口径。原文「<b>鲈类、蛙类平稳</b>」段与 29 品种表给出多口径鲈类价格：<b>加州鲈 11.80 平稳（惠农网 11/22 热门品种均价）→ 明日 11.6~11.9</b>、<b>淡水鲈 12.31（前 12.45）→ 12.1~12.4</b>、<b>海鲈鱼 11.06 平稳 → 11.0~11.2</b>、<b>鲈鱼（白沙洲）≥500g 19.85 元/公斤 ÷2 ＝ 9.93（前 10.03）→ 9.8~10.0</b>；另列「鲈鱼 7 日均价 11.04、区间 10.97~11.10」「加州鲈产地 10.2~11 元/斤，走货快、后市看平」。<b>本期原文 29 品种表与五个重点品种均未给鳜鱼绝对价，如实留空</b>。</div>
  <table><thead><tr><th>口径 · 来源</th><th>基准价（元/斤）</th><th>明日预测（11-24）</th><th>原文标注</th></tr></thead><tbody>
        <tr><td>加州鲈 · 惠农网 11/22 热门品种均价</td><td class="price"><b>11.80</b></td><td class="price"><b>11.6-11.9</b></td><td style="font-size:12px">平稳；产地通货 10.2~11、走货快、后市看平</td></tr>
        <tr><td>淡水鲈 · 惠农网热门</td><td class="price"><b>12.31</b></td><td class="price"><b>12.1-12.4</b></td><td style="font-size:12px">前值 12.45，原文标「平稳」</td></tr>
        <tr><td>海鲈鱼 · 惠农网 11/22</td><td class="price"><b>11.06</b></td><td class="price"><b>11.0-11.2</b></td><td style="font-size:12px">平稳</td></tr>
        <tr><td>鲈鱼（白沙洲）≥500g</td><td class="price"><b>9.93</b></td><td class="price"><b>9.8-10.0</b></td><td style="font-size:12px">19.85 元/公斤 ÷2 换算；前值 10.03；白沙洲 11/21 发布</td></tr>
        <tr><td>鲈鱼 · 7 日均价（参考）</td><td class="price"><b>11.04</b></td><td class="price"><b>—</b></td><td style="font-size:12px">区间 10.97~11.10，原文称波动不足 0.15 元；非明日预测，照录</td></tr>
        <tr><td><span class="tag tag-gui">鳜鱼</span></td><td class="price"><b>—</b></td><td class="price"><b>—</b></td><td style="font-size:12px">本期原文未列鳜鱼绝对价，如实留空、不推算</td></tr>
  </tbody></table>
  <div class="callout" style="margin-top:10px"><b>口径提示：</b>① 本卡为<b>次日（11-24 周二）预测口径</b>；基准价取自惠农网 11/22、白沙洲 11/21 发布、一亩田 11/23 等<b>不同日期、不同渠道的实测 / 均价</b>，与塘口价、批发价、产地供货价、周均价、视频号区间<b>多口径并存、禁止互减</b>；<b>预测价与实测成交价禁止互减、不作命中率评价</b>。② <b>即便同为「白沙洲鲈鱼 ≥500g」，本卡次日预测区间 9.8~10.0 与白沙洲实测成交价也禁止互减</b>；9.93 为原文 19.85 元/公斤 ÷2 的换算值，按原文照录。③ 加州鲈 11.80「平稳」、淡水鲈 12.31（前 12.45）、海鲈 11.06、白沙洲鲈鱼 9.93 为<b>不同品种 / 不同市场 / 不同口径</b>，逐个照录，<b>不互减、不统一涨跌</b>。④ 本期原文<b>未给鳜鱼绝对价</b>，按红线如实留空、不推算。⑤ 与渔无忧 11-20 卡（11-21 次日预测）为<b>同号隔期，隔期并列、不作两期比较</b>；与全国渔业价格 11-24 早报、渔飞鱼明日预报为<b>不同发布号，分别照录、不互减</b>。⑥ 罗氏沼虾、稻田蟹、黄颡、黑鱼、牛蛙、金鲳鱼、大宗淡水鱼等非目标品种按约定不录入。</div>
  <div class="legend">来源：微信公众号「渔无忧在线」2026-11-23 16:05《最新水产行情预报》· <a class="plink" href="https://mp.weixin.qq.com/s/0fXyBh5y8a4kHDQ9Kk3elw" target="_blank" rel="noopener">📄 阅读原文（11-23 预报）</a> · 元/斤 · 实测基准 + 次日预测口径 · 正文核校录入</div>
</div>"""

# ══════════════════════════════════════════════════════════════════════
# 卡 4 · 科学养鱼 11-23 正文图片分市场批发价（kexue_web，非 kexue OCR 通道）
# ══════════════════════════════════════════════════════════════════════
CARD_KEXUE_WEB = """<div class="card" style="margin-top:14px">
  <h3>🌊 2026-11-23 · 科学养鱼 分市场批发价（鳜鱼 7 市场 · 元/千克 · 正文图片表格核校）</h3>
  <div class="csub">「科学养鱼」2026-11-23 16:31 发布《11月23日最新全国水产品批发市场价格》，报价表<b>全部以图片形式嵌在正文</b>（淡水鱼类 / 海水鱼类 / 甲壳类 · <b>元/千克</b>）。逐张下载核校 24 张正文图：<b>仅 08 号为鳜鱼（桂花鱼）7 行</b>——四川西部冷都 70.00、长沙马王堆 53.00、江苏凌家塘 54.00、云南华潮 120.00（条重≥750）、中国供销上饶 60.00、江西南昌 60.00、甘肃兰州 68.00（条重≥750）；<b>14 号「花鲈」为海水鲈、非加州鲈 / 非本看板跟踪口径，不录入</b>；<b>本期未见加州鲈段，如实留空</b>。原文未给涨跌说明，只列本期绝对值与规格标注。</div>
  <table><thead><tr><th>鳜鱼 市场（原文全称）</th><th>规格（条重 g）</th><th>11-23 批发价（元/千克）</th><th>备注</th></tr></thead><tbody>
        <tr><td><span class="tag tag-gui">四川西部冷都商业管理有限公司</span></td><td><span class="spec spec-s">500≤条重&lt;750</span></td><td class="price"><b>70.00</b></td><td style="font-size:12px">原文照录</td></tr>
        <tr><td><span class="tag tag-gui">长沙马王堆农产品股份有限公司海鲜水产批发市场</span></td><td><span class="spec spec-s">500≤条重&lt;750</span></td><td class="price"><b>53.00</b></td><td style="font-size:12px">原文照录</td></tr>
        <tr><td><span class="tag tag-gui">江苏凌家塘市场发展有限公司</span></td><td><span class="spec spec-s">500≤条重&lt;750</span></td><td class="price"><b>54.00</b></td><td style="font-size:12px">本看板本地销区锚点</td></tr>
        <tr><td><span class="tag tag-gui">云南华潮水产品批发市场</span></td><td><span class="spec spec-s">条重≥750</span></td><td class="price"><b>120.00</b></td><td style="font-size:12px">规格与前三行不同，不可互减</td></tr>
        <tr><td><span class="tag tag-gui">中国供销上饶农产品交易城</span></td><td><span class="spec spec-s">500≤条重&lt;750</span></td><td class="price"><b>60.00</b></td><td style="font-size:12px">原文照录</td></tr>
        <tr><td><span class="tag tag-gui">江西南昌市水产品综合交易市场</span></td><td><span class="spec spec-s">500≤条重&lt;750</span></td><td class="price"><b>60.00</b></td><td style="font-size:12px">原文照录</td></tr>
        <tr><td><span class="tag tag-gui">甘肃省兰州市绿色食品市场</span></td><td><span class="spec spec-s">条重≥750</span></td><td class="price"><b>68.00</b></td><td style="font-size:12px">原文照录</td></tr>
        <tr><td><span class="tag tag-lu">加州鲈</span></td><td><span class="spec spec-s">—</span></td><td class="price"><b>—</b></td><td style="font-size:12px">本期正文图未见加州鲈段，如实留空</td></tr>
  </tbody></table>
  <div class="callout" style="margin-top:10px"><b>口径说明：</b>① 本卡为<b>科学养鱼公众号正文图片表格</b>通道，与 <b>App 截图 OCR 通道（kexue，当前 11-20）分源登记</b>；本批只更新 <code>kexue_web</code>，<b>不回写 <code>kexue</code> 日期、不覆盖 OCR 快照</b>。② 单位 <b>元/千克</b>，与塘口价（元/斤）、凌家塘周均价、盛阳本地批发、白沙洲日度批发（元/公斤 ÷2）、视频号全国区间<b>多口径并存、禁止互减</b>；本卡<b>不作元/斤换算展示</b>，避免口径混用。③ 24 张正文图逐张核校：仅 08 号为鳜鱼（7 行）；<b>14 号「花鲈」为海水鲈，非加州鲈、非本看板跟踪口径，不录入</b>；其余团头鲂、黄颡鱼、海水鱼类、甲壳类等按约定不录入。④ 与淡水渔业 11-20 分市场批发价卡为<b>不同公众号、不同日期、市场样本不同</b>（本卡无乌鲁木齐北园春 / 上海江阳 / 合肥周谷堆 / 武汉白沙洲，新增四川西部冷都、中国供销上饶、甘肃兰州）；<b>跨期核校仅限同市场同规格</b>，江苏凌家塘 54.00、长沙马王堆 53.00、云南华潮 120.00（条重≥750）等近值 / 同值<b>按原文照录、不推断涨跌、不作两期比较、不重复计数</b>。⑤ 原文<b>未给涨跌说明</b>，本卡只列本期绝对值与规格标注。</div>
  <div class="legend">来源：微信公众号「科学养鱼」2026-11-23 16:31《11月23日最新全国水产品批发市场价格》· <a class="plink" href="https://mp.weixin.qq.com/s/o1taaGFc5g-vWB-l_7sT5Q" target="_blank" rel="noopener">📄 阅读原文（11-23 分市场批发价）</a> · 元/千克 · 正文图片逐张下载核校录入</div>
</div>"""

# ══════════════════════════════════════════════════════════════════════
# 卡 5 · 江苏凌家塘 11/15~11/21 一周行情
# ══════════════════════════════════════════════════════════════════════
CARD_LINGJIATANG = """<div class="card" style="margin-top:14px">
  <h3>🏪 江苏凌家塘市场 · 一周价格行情（2026/11/15~11/21 · 水产摘录）</h3>
  <div class="csub">「江苏凌家塘市场」官方号 2026-11-21 15:55 发布一周价格行情（2026/11/15~11/21）。水产类「<b>特种水产：集中上市，价格下跌</b>」段给出<b>桂鱼约 28 元/斤、鲈鱼约 13 元/斤</b>（均为<b>周均价约数口径</b>）；本期原文<b>对鳜鱼 / 鲈鱼均未给逐日涨跌幅度</b>，只给约数与定性判断。淡水鱼段鲫鱼约 8、草鱼约 7、鳊鱼约 7，以及昂公、河虾、基围虾、罗氏虾、白虾、螃蟹、澳龙等<b>非目标品种按约定不录入</b>。</div>
  <table><thead><tr><th>品种</th><th>口径</th><th>价格</th><th>原文标注</th></tr></thead><tbody>
        <tr><td><span class="tag tag-gui">鳜鱼（原文「桂鱼」）</span></td><td><span class="spec spec-s">常州凌家塘销区 · 周均价（11/15~11/21）</span></td><td class="price"><b>约 28 元/斤</b></td><td style="font-size:12px">「特种水产：集中上市，价格下跌」为定性，未给幅度</td></tr>
        <tr><td><span class="tag tag-lu">鲈鱼</span></td><td><span class="spec spec-s">常州凌家塘销区 · 周均价（11/15~11/21）</span></td><td class="price"><b>约 13 元/斤</b></td><td style="font-size:12px">周度约数口径，未给涨跌幅度</td></tr>
  </tbody></table>
  <div class="callout" style="margin-top:10px"><b>口径说明：</b>① 本卡为<b>周均价 / 约数口径</b>，与日度批发价、塘口价、产地均价、次日预测价<b>时间基准与口径不同，禁止互减</b>。② 与 11/8~11/14 期（鲈鱼约 12 元/斤、鳜鱼本期原文未给）为<b>同市场隔期周报</b>：本期新增桂鱼约 28，<b>不作两期数值相减、不推断涨跌</b>；原文「价格下跌」为定性描述、未给幅度，照录不量化。③ 原文用字「<b>桂鱼</b>」即本看板所跟踪的鳜鱼，归一口径照录并标明原文用字。④ 与科学养鱼 11-23 该市场鳜鱼 54.00 元/千克（日度分市场批发）、白沙洲日度批发、盛阳无锡本地批发、视频号全国区间<b>多口径并存、禁止互减</b>。⑤ 鲫鱼 / 草鱼 / 鳊鱼 / 昂公 / 虾蟹 / 海鲜 / 荤食 / 蛋类 / 粮副等非目标品种按约定不录入。</div>
  <div class="legend">来源：微信公众号「江苏凌家塘市场」2026-11-21 15:55《江苏凌家塘市场一周价格行情（2026/11/15~2026/11/21）》· <a class="plink" href="https://mp.weixin.qq.com/s/6CGBdtPqWmczRefl9RLfDg" target="_blank" rel="noopener">📄 阅读原文（凌家塘一周行情 11/15~21）</a> · 元/斤 · 周均价约数，仅供参考</div>
</div>"""

# ── 插入锚点（均验证 count=1）──────────────────────────────────────────────
ANCHORS = [
    ('<div class="card" style="margin-top:14px">\n<div class="card" style="margin-top:14px">\n  <h3>📰 全国渔业价格 ·《渔飞鱼水产行情日报 2026-11-23》',
     CARD_MINJIAN, "卡1 全国渔业价格 11-24 早报"),
    ('<div class="card" style="margin-top:14px">\n  <h3>📰 2026-11-18 · 水产养殖网 · 加州鲈专题：',
     CARD_QIANGYU, "卡2 强渔 11-23 特水鱼周报"),
    ('<div class="card" style="margin-top:14px">\n  <h3><div class="card" style="margin-top:14px">\n  <h3>预报 📅 渔无忧在线 ·《最新水产行情预报》（发布 11月20日 15:28 · 次日 11月21日 周六预测口径）</h3>',
     CARD_YUWUYOU, "卡3 渔无忧 11-23 预报"),
    ('<div class="card" style="margin-top:14px">\n  <h3>🌊 2026-11-20 · 淡水渔业 分市场批发价（鳜鱼 8 市场',
     CARD_KEXUE_WEB, "卡4 科学养鱼 11-23 正文图批发价"),
    ('<div class="card" style="margin-top:14px">\n  <h3>🏪 江苏凌家塘市场 · 一周价格行情（2026/11/8~11/14 · 水产摘录）</h3>',
     CARD_LINGJIATANG, "卡5 凌家塘 11/15~21 一周行情"),
]

# ── chip VCSRCCHIP0001 源清单日期串（5 处，手工维护；chip258 由 refresh_freshness 重建，勿动）
CHIP_SUBS = [
    ("11-17日报/11-18日报/11-23日报）",
     "11-17日报/11-18日报/11-23日报/11-24早报）", "chip 全国渔业价格日报"),
    ("（10-25~31 / 11-01~07 / 11-08~14）",
     "（10-25~31 / 11-01~07 / 11-08~14 / 11-15~21）", "chip 凌家塘一周行情"),
    ("11-13/11-16/11-20 独立期，次日预测口径",
     "11-13/11-16/11-20/11-23 独立期，次日预测口径", "chip 渔无忧在线预报"),
    ("/11-20App截图·OCR通道）",
     "/11-20App截图·OCR通道/11-23正文图）", "chip 科学养鱼分市场批发价"),
    ("/ 11-16 特水鱼周报 / 11-18 加州鲈专题）",
     "/ 11-16 特水鱼周报 / 11-18 加州鲈专题 / 11-23 特水鱼周报）", "chip 水产养殖网"),
]


def main():
    s = HTML.read_text(encoding="utf-8")
    print("[info] 起始字节", len(s.encode("utf-8")))
    assert_balanced(s, "插入前整页")

    present = [g for g in GUARDS if g in s]
    if present:
        print("[FATAL] 幂等守卫已存在，拒绝重跑：", present[:3])
        sys.exit(3)
    print("[ok] 5 个幂等守卫均不存在，可插入")

    for anchor, card, label in ANCHORS:
        s = insert_before(s, anchor, card, label)

    for old, new, label in CHIP_SUBS:
        s = rep(s, old, new, label)

    assert_balanced(s, "插入后整页")

    # 5 张卡必须各出现 1 次；5 个链接必须各出现 1 次
    for g in GUARDS:
        assert s.count(g) == 1, f"守卫异常: {g}"
    for k in ["2S68t_7Anqpu_2K7fieFog", "HhkAFKbelQp_0_tQWvUF6Q",
              "0fXyBh5y8a4kHDQ9Kk3elw", "o1taaGFc5g-vWB-l_7sT5Q",
              "6CGBdtPqWmczRefl9RLfDg"]:
        assert s.count(k) == 1, f"链接异常: {k}"
    print("[ok] 5 卡 / 5 链接均唯一")

    HTML.write_text(s, encoding="utf-8")
    print("[ok] 写盘完成，字节", len(s.encode("utf-8")))


if __name__ == "__main__":
    main()
