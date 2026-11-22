# -*- coding: utf-8 -*-
"""11-22 深夜批插卡脚本（幂等）
2 张新卡：
1) 全国渔业价格·渔飞鱼水产行情日报 11-23（发布 11-22 19:20 · 鳜鱼大鱼独涨 30.75 / 加州鲈产地均价 11.80 平 / 鲈鱼 9.83）
2) 渔知识指导·明日水产行情预报 11-22（发布 11-21 19:00 · 数据基准 11/21 · 加州鲈 11.80 平稳、本期无鳜鱼）
跳过：科学养鱼 11-20 正文图片表格（鳜鱼 6 行与已录 OCR 逐项同值、无加州鲈）。
"""
import re, sys

F = "鳜鱼鲈鱼价格看板.html"
html = open(F, encoding="utf-8").read()

U_MJ1123 = "https://mp.weixin.qq.com/s/HowVrJUQChH4zdArhLms8Q"
U_YZS1122 = "https://mp.weixin.qq.com/s/okkzeHAOe0P8MyCQJSdMSQ"

GUARDS = [
    "渔飞鱼水产行情日报 2026-11-23",
    "明日水产行情预报 2026-11-22",
]
present = [g for g in GUARDS if html.count(g) >= 1]
if len(present) == len(GUARDS):
    print("[SKIP] 2 张新卡均已存在，幂等退出")
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


# ---------------- 1) 全国渔业价格 11-23 日报 ----------------
CARD_MJ1123 = """
<div class="card" style="margin-top:14px">
  <h3>📰 全国渔业价格 ·《渔飞鱼水产行情日报 2026-11-23》（发布 11-22 19:20 · 鳜鱼大鱼独涨 30.75 / 加州鲈产地均价 11.80 平 / 鲈鱼 9.83 走低）</h3>
  <div class="csub">「全国渔业价格」2026-11-22 19:20 发布 11-23 期日报。原文自述「明日鲫鱼 / 河蟹 / 鳜鱼在涨，普水和特水还在掉」，<b>本看板只跟踪鳜鱼 / 加州鲈两类</b>：<b>鳜鱼大鱼独涨 1 元——白沙洲 ≥750g 60.50→61.50 元/公斤＝30.75 元/斤（+1.7%），500~750g 59.00、250~500g 47.50 未动</b>，原文「婚宴订桌带动统货，大鱼能等就等一下，小鱼别学」；<b>加州鲈产地均价 11.80 元/斤，原文标注「平（11/22）」</b>；<b>鲈鱼 ≥500g 19.85→19.65 元/公斤＝9.83 元/斤</b>（原文归入「特水继续泄气」段）。文中「鳜鱼 30.75、加州鲈 11.80、鲈鱼 9.83 元/斤」为当日报价小结。天气：23 日白天小雨 23/18℃ 为本轮最暖最湿窗口、夜里冷空气进粤，24 日只剩 19/14℃，水霉高发拖到 25 日。</div>
  <table><thead><tr><th>品种</th><th>渠道 / 规格</th><th>前值</th><th>本期（元/斤）</th><th>原文标注</th></tr></thead><tbody>
        <tr><td rowspan="3"><span class="tag tag-gui">鳜鱼</span></td><td>白沙洲 ≥750g</td><td class="price">30.25</td><td class="price"><b>30.75</b></td><td style="color:#d32029;font-size:12px">▲ +1.7%（61.50 元/公斤）</td></tr>
        <tr><td>白沙洲 500~750g</td><td class="price">29.50</td><td class="price"><b>29.50</b></td><td style="font-size:12px">59.00 元/公斤 · 未动</td></tr>
        <tr><td>白沙洲 250~500g</td><td class="price">23.75</td><td class="price"><b>23.75</b></td><td style="font-size:12px">47.50 元/公斤 · 未动</td></tr>
        <tr><td><span class="tag tag-lu">加州鲈</span></td><td>产地均价 · 鲜活</td><td class="price">11.80</td><td class="price"><b>11.80</b></td><td style="font-size:12px">平（11/22）</td></tr>
        <tr><td>鲈鱼（白沙洲）</td><td>≥500g</td><td class="price">9.93</td><td class="price"><b>9.83</b></td><td style="color:#12a150;font-size:12px">19.85→19.65 元/公斤</td></tr>
  </tbody></table>
  <div class="callout" style="margin-top:10px"><b>口径说明：</b>① 鳜鱼三档、鲈鱼 ≥500g 为<b>白沙洲批发市场价（原文以元/公斤给出、本卡照录其元/斤折算）</b>；加州鲈 11.80 为<b>产地均价（元/斤）</b>，原文标注「平（11/22）」——<b>渠道与规格不同，禁止互减</b>。② 与 11-18 同号卡（鳜鱼 ≥750g 30.25、鲈鱼 ≥500g 9.90、加州鲈 11.80）为同系列连续期：鳜鱼大档 30.25→30.75、加州鲈 11.80 同值同口径，<b>鳜鱼本期原文明确给出 +1.7% 按原文照录，加州鲈同值不推断涨跌、不作两期比较</b>；鲈鱼 9.90→9.83 与原文「特水泄气」方向一致，<b>不自行相减</b>。③ 本卡为<b>次日（11/23）行情早报口径</b>，原文以「今日下午先谈好」给出次日报价，<b>与实测成交价为不同性质，不作命中率评价</b>；④ 与鳜康泰 11-22 江苏标鳜 24、通威 11-20 全国塘口均价 23.0、科学养鱼分市场批发（元/公斤）、盛阳 25~30、视频号全国参考区间、次日预测<b>多口径并存、禁止互减</b>；⑤ 文中河蟹、鲫鱼、黄颡鱼、生鱼、草鱼、鲤鱼等非跟踪品种按约定不录入。</div>
  <div class="legend">来源：微信公众号「全国渔业价格」2026-11-22 19:20《渔飞鱼水产行情日报（2026年11月23日）鲫鱼河蟹鳜鱼齐涨 黄颡生鱼再掉两个点》· <a class="plink" href="__U_MJ1123__" target="_blank" rel="noopener">📄 阅读原文（日报 11-23）</a> · 元/公斤 + 元/斤多口径 · 正文文字核校录入</div>
</div>
""".replace("__U_MJ1123__", U_MJ1123)


# ---------------- 2) 渔知识指导 明日预报 11-22 ----------------
CARD_YZS1122 = """
<div class="card" style="margin-top:14px">
  <h3>预报 📅 渔知识指导 ·《明日水产行情预报 2026-11-22》（发布 11-21 19:00 · 数据基准 11/21 · 加州鲈 11.80 企稳 · 本期无鳜鱼条目）</h3>
  <div class="csub">「渔知识指导」2026-11-21 19:00 发布《明日水产行情预报 | 2026年11月22日 星期日》，<b>数据基准 11/21</b>、覆盖 28 品种。与本看板相关的加州鲈 / 鲈鱼类：<b>惠农网 11/20 加州鲈热门品种 11.80 元/斤、价格平稳，预测 11.6~11.9 →（置信度高）；淡水鲈 12.45 元/斤 +2.45%；海鲈鱼 11.06 元/斤平稳；产地供货（成都 / 江门）12.00~14.00 元/斤</b>。原文「大量上市、货源充足、客商积极性高、走货快，后市预测看平」，操作建议「达规格大鱼正常出塘，冬季冻伤风险上升、不建议压塘惜售」。<b>本期 28 品种表及预测概览均无鳜鱼条目，如实留空</b>。</div>
  <table><thead><tr><th>口径 · 来源</th><th>规格</th><th>基准价（元/斤）</th><th>明日预测（元/斤）</th><th>原文标注</th></tr></thead><tbody>
        <tr><td>惠农网 · 加州鲈热门品种</td><td>热门品种均价</td><td class="price"><b>11.80</b></td><td class="price">11.6~11.9</td><td style="font-size:12px">价格平稳 · 后市看平</td></tr>
        <tr><td>惠农网 · 淡水鲈</td><td>综合均价</td><td class="price"><b>12.45</b></td><td class="price">看平</td><td style="color:#d32029;font-size:12px">+2.45%</td></tr>
        <tr><td>惠农网 · 海鲈鱼</td><td>热门品种均价</td><td class="price">11.06</td><td class="price">11.0~11.2</td><td style="font-size:12px">价格平稳（海水鲈、非跟踪口径）</td></tr>
        <tr><td>产地供货 · 成都 / 江门</td><td>通货</td><td class="price">12.00~14.00</td><td class="price">→</td><td style="font-size:12px">供货价 · 原文照录</td></tr>
  </tbody></table>
  <div class="callout" style="margin-top:10px"><b>口径说明：</b>① 本刊为<b>次日预测性质、非实测成交价</b>，基准价与预测区间不等值，<b>按原文照录、不据此推断实际涨跌、不作命中率评价</b>。② <b>发布公众号为「渔知识指导」</b>，按发布号归入本源，与全国渔业价格 11-23 日报、绿色水产技术 11-22 加州鲈播报（均为其他公众号）分开计数。③ 加州鲈 11.80 与 11-22 批次「渔无忧在线 11-20 预报」、本批「全国渔业价格 11-23 日报」加州鲈产地均价<b>同值</b>，但<b>发布号 / 期次 / 基准日不同，不重复计数、不推断涨跌、不作两期比较</b>。④ 淡水鲈 12.45（+2.45%）与加州鲈 11.80、海鲈鱼 11.06 为<b>不同平台品种口径</b>，按原文分列、不互减；产地供货 12~14 元/斤为供货报价、非成交均价。⑤ 与塘口（鳜康泰 11-22 江苏标鳜 24）、分市场批发（元/公斤）、白沙洲批发、盛阳本地批发、视频号全国参考区间<b>多口径并存、禁止互减</b>；⑥ 稻田蟹、罗氏沼虾、生鱼、大宗淡水鱼、牛蛙等非跟踪品种按约定不录入。</div>
  <div class="legend">来源：微信公众号「渔知识指导」2026-11-21 19:00《明日水产行情预报 | 2026年11月22日 星期日》· <a class="plink" href="__U_YZS1122__" target="_blank" rel="noopener">📄 阅读原文（明日预报 11-22）</a> · 数据基准 11/21 · 元/斤 · 次日预测口径，仅供参考</div>
</div>
""".replace("__U_YZS1122__", U_YZS1122)


# ================= 插入（最新同期卡之前） =================
print("=== 插卡 ===")
insert_before("  <h3>📰 全国渔业价格 ·《渔飞鱼水产行情日报 2026-11-18》", CARD_MJ1123, "全国渔业价格 11-23 日报")
insert_before("  <h3>🐟 渔飞鱼·董小月 ·《全国最新水产行情日报 2026-11-17》", CARD_YZS1122, "渔知识指导 11-22 明日预报")

# ================= chip 快览同步 =================
print("=== chip 同步 ===")
rep("/11-17日报/11-18日报）+ 渔飞鱼日报",
    "/11-17日报/11-18日报/11-23日报）+ 渔飞鱼日报",
    "全国渔业价格 11-23 日报")
rep("渔知识指导日报（11-03/11-05/11-06/11-13/11-17）",
    "渔知识指导日报（11-03/11-05/11-06/11-13/11-17/11-22预报）",
    "渔知识指导 11-22 预报")


# ================= 标签精确配平 =================
def balance(s):
    for tag in ["div", "table", "thead", "tbody", "tr", "td", "th", "h3", "span", "a", "b"]:
        o = len(re.findall(r"<%s(?=[\s>])" % tag, s))
        c = len(re.findall(r"</%s>" % tag, s))
        assert o == c, ("标签不配平", tag, o, c)


balance(html)
print("  [OK] 标签精确配平通过")

open(F, "w", encoding="utf-8").write(html)
print("\n[DONE] 2 张新卡 + chip 2 处同步已写入", F)
print("HTML chars:", len(html))
