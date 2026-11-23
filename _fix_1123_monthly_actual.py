#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
2026-11-23 修复：第九部分「月度价格对比 · 2026 预测」中 2026 年 10 月仍标预测值。

背景：10 月已收盘，MOA 接口历史库 fish_prices_history.json 已累积 10 月全月报价。
     9 月已按「MOA 实测月均」标注（鳜鱼 84.0 = 江苏凌家塘活鳜鱼 n=2；
     鲈鱼 34.1 = 全部淡水/海水鲈鱼 n=165），10 月沿用**完全相同口径**：
       鳜鱼 = 江苏凌家塘活鳜鱼 n=20 → 66.05 → 66.0
       鲈鱼 = 全部鲈鱼样本      n=317 → 33.6517 → 33.7
     11/12 月未收盘，保留模型预测。

红线遵守：9–10 月实测与 11–12 月预测为不同性质数据，禁止互减、不作命中率评价；
          原 10 月预测值 76.9 / 31.0 仅作历史模型留痕，不再作为当期值。

⚠️ 本段为手工维护，切勿重跑 build_section8.py（旧「第八部分」生成器会整体覆盖本段）。
"""
import re
import sys

HTML = "鳜鱼鲈鱼价格看板.html"

s = open(HTML, encoding="utf-8").read()

# ---- 幂等守卫 ----
if '66.0<sup' in s and '33.7<sup' in s and '76.9*' not in s and '31.0*' not in s:
    print("[SKIP] 10 月实测已回填，无需重复执行")
    sys.exit(0)
if ('66.0<sup' in s) != ('33.7<sup' in s):
    print("[ABORT] 检测到部分回填状态，人工检查后再跑")
    sys.exit(1)

SUP = '<sup style="color:#0ea5a4;font-size:9px;font-weight:600"> 实测</sup>'

REPS = [
    # 1) 数据口径 note
    (
        '数据口径：北京新发地批发价（元/公斤）· 真实历史 2024-01~2026-08；2026 年 9 月起切换为农业农村部全国批发价实测月均（MOA 接口日更累积，鳜鱼取江苏凌家塘市场）',
        '数据口径：北京新发地批发价（元/公斤）· 真实历史 2024-01~2026-08；2026 年 9–10 月已回填农业农村部全国批发价实测月均（MOA 接口日更累积，鳜鱼取江苏凌家塘市场、鲈鱼取全部样本），11–12 月为模型预测',
        1,
    ),
    # 2) 核心目的
    (
        '结合 2026 年实际（1–8 月新发地 + 9 月起 MOA 实测）外推 10–12 月预测，',
        '结合 2026 年实际（1–8 月新发地 + 9–10 月 MOA 实测）外推 11–12 月预测，',
        1,
    ),
    # 3) 预测算法说明段（整段替换）
    (
        '      · 预测算法（2026-10-10 校准）：原「历史同期（2024/2025）均值 × 年际偏差系数 k（鳜鱼 0.903、鲈鱼 0.904）」纯反推法<b>对鲈鱼 9 月预测 39.2、实际 34.1，高估 5.1 元/公斤（+15%）</b>——已改为<b>「最新实测锚定 + 历史季节性衰减」</b>：鲈鱼 10 月以 MOA 10-01~09 实测日均 35.4 元/公斤（日度 39.4→31.7 单边下行）外推全月 ≈31.0；11/12 月按 2024/2025 同期降幅（10→11 月 −4.2~−5.8、11→12 月 −1.4~−3.5）递推 ≈27.0 / ≈26.0。现货佐证：科学养鱼 10-09 加州鲈批发 21.8~32 元/公斤、盛阳 10~14.5 元/斤，与下修后预测吻合；鳜鱼 10 月预测 76.9 与 MOA 10 月实测（剔除乌鲁木齐孤本后均值 77.9、中位数 71）基本一致，维持不变。',
        '      · 预测算法（2026-10-10 校准 / 2026-11-23 回填）：原「历史同期（2024/2025）均值 × 年际偏差系数 k（鳜鱼 0.903、鲈鱼 0.904）」纯反推法<b>对鲈鱼 9 月预测 39.2、实际 34.1，高估 5.1 元/公斤（+15%）</b>——已改为<b>「最新实测锚定 + 历史季节性衰减」</b>：11/12 月按 2024/2025 同期降幅（10→11 月 −4.2~−5.8、11→12 月 −1.4~−3.5）递推鲈鱼 ≈27.0 / ≈26.0、鳜鱼 61.2 / 55.8，<b>仍为模型预测</b>（表中 * 标、图中红虚线）。<b>2026 年 10 月已收盘，按与 9 月完全相同的 MOA 口径回填全月实测月均</b>：鳜鱼取江苏凌家塘市场「活鳜鱼」有效报价 20 条 → <b>66.0 元/公斤</b>；鲈鱼取全部「淡水鲈鱼 + 鲈鱼(海水)」样本 317 条 → <b>33.7 元/公斤</b>（9 月同口径为 84.0 / 34.1）。<b>9–10 月实测与 11–12 月预测属不同性质数据，禁止互减、不作命中率评价</b>；原 10 月预测值 76.9 / 31.0 仅作历史模型留痕，不再作为当期值。现货佐证：科学养鱼 10-09 加州鲈批发 21.8~32 元/公斤、盛阳 10~14.5 元/斤。',
        1,
    ),
    # 4) 两张图下方 csub（2 处）
    (
        '实线为真实月度均价；红色虚线为 2026 年 10–12 月预测（9 月起为实际·MOA 实测）。',
        '实线为真实月度均价；红色虚线为 2026 年 11–12 月预测（9–10 月为实测·MOA 全月月均）。',
        2,
    ),
    # 5) 鳜鱼表 10 月行
    (
        '<td data-page-node-id="KWPdsJq7qNkVh3Ty2m5cMH"><span style="color:#e5484d;font-weight:600" data-page-node-id="Uv2pa3XuWDmRplkrtYpEzc">76.9*</span></td>',
        '<td data-page-node-id="KWPdsJq7qNkVh3Ty2m5cMH">66.0' + SUP + '</td>',
        1,
    ),
    # 6) 鲈鱼表 10 月行
    (
        '<td data-page-node-id="OohyiVizkHqzLZv7uxSCeM"><span style="color:#e5484d;font-weight:600" data-page-node-id="WVoyIkZs8oXoGQo31E3whk">31.0*</span></td>',
        '<td data-page-node-id="OohyiVizkHqzLZv7uxSCeM">33.7' + SUP + '</td>',
        1,
    ),
    # 7) 排产表列头
    (
        '<th data-page-node-id="iHZohNHMBEnSkKzhKraNMn">2026 预测高点月</th>',
        '<th data-page-node-id="iHZohNHMBEnSkKzhKraNMn">2026 年内高点月（实测/预测）</th>',
        1,
    ),
    # 8) 排产表鳜鱼 9 月
    (
        '<td data-page-node-id="GE3qvyx7JEbpPMHglEgR01">9月（预测高点，约 92 元/公斤）</td>',
        '<td data-page-node-id="GE3qvyx7JEbpPMHglEgR01">9月（实测 84.0 元/公斤）</td>',
        1,
    ),
    # 9) 排产表鲈鱼 9 月
    (
        '<td data-page-node-id="8gZr1yW28btEj6bEPLOnBh">9月（预测高点，约 39 元/公斤）</td>',
        '<td data-page-node-id="8gZr1yW28btEj6bEPLOnBh">9月（实测 34.1 元/公斤）</td>',
        1,
    ),
    # 10) 排产要点 ①
    (
        '<b data-page-node-id="sVxVeBzDiTgKAK2vOGmbsE">9 月</b>（预测约 92 元/公斤，仅次于 8 月实际值）',
        '<b data-page-node-id="sVxVeBzDiTgKAK2vOGmbsE">9 月</b>（实测 84.0 元/公斤，仅次于 8 月实际值 107.9）',
        1,
    ),
    # 11) 排产要点 ②
    (
        '<b data-page-node-id="k1yHgazqSGyhuAMaDJIh0k">9 月</b>（预测约 39 元/公斤）',
        '<b data-page-node-id="k1yHgazqSGyhuAMaDJIh0k">9 月</b>（实测 34.1 元/公斤）',
        1,
    ),
    # 12) 排产要点 ③
    (
        '③ 若错过 9 月主高峰，今年内价格将回落（鳜鱼 10–12 月降至 56–77、鲈鱼降至 31–38），建议转向布局',
        '③ 若错过 9 月主高峰，10 月实测已录（鳜鱼 66.0、鲈鱼 33.7 元/公斤），11–12 月模型预测为鳜鱼 61.2 / 55.8、鲈鱼 27.0 / 26.0（<b>实测与预测不同性质、禁止互减</b>），建议转向布局',
        1,
    ),
    # 13) 方法与局限 ②
    (
        '② 预测采用「历史同期均值 × 年际偏差系数」简洁模型，区间取历史同期 min/max × k，<b data-page-node-id="341kPiK8FynUNKHTNgxygI">仅为趋势参考，非承诺值</b>；',
        '② 11–12 月预测采用「最新实测锚定 + 历史季节性衰减」模型（2026-10-10 校准），<b data-page-node-id="341kPiK8FynUNKHTNgxygI">仅为趋势参考，非承诺值</b>；9–10 月为已收盘实测、不参与预测模型；',
        1,
    ),
    # 14) 方法与局限 ③
    (
        '③ 2026 年 1–8 月为真实抓取，9–12 月为预测（图中红虚线，表中 * 标）；',
        '③ 2026 年 1–8 月为真实抓取、9–10 月为 MOA 接口全月实测月均（表中「实测」标）、11–12 月为预测（图中红虚线，表中 * 标）；实测与预测不同性质、禁止互减、不作命中率评价；',
        1,
    ),
    # 15) 图表数据 · 鳜鱼
    (
        '"y2026a": [62.27, 68.25, 59.14, 63.18, 69.36, 76.27, 75.96, 107.89, 84.0, null, null, null], "y2026f": [null, null, null, null, null, null, null, null, null, 76.9, 61.2, 55.8]',
        '"y2026a": [62.27, 68.25, 59.14, 63.18, 69.36, 76.27, 75.96, 107.89, 84.0, 66.0, null, null], "y2026f": [null, null, null, null, null, null, null, null, null, null, 61.2, 55.8]',
        1,
    ),
    # 16) 图表数据 · 鲈鱼
    (
        '"y2026a": [34.0, 34.5, 34.59, 34.05, 33.18, 34.94, 33.79, 32.95, 34.1, null, null, null], "y2026f": [null, null, null, null, null, null, null, null, null, 31.0, 27.0, 26.0]',
        '"y2026a": [34.0, 34.5, 34.59, 34.05, 33.18, 34.94, 33.79, 32.95, 34.1, 33.7, null, null], "y2026f": [null, null, null, null, null, null, null, null, null, null, 27.0, 26.0]',
        1,
    ),
    # 17) 防回归注释
    (
        '<!-- 九、月度价格对比 · 2026预测 · 养殖排产反推 start -->',
        '<!-- 九、月度价格对比 · 2026预测 · 养殖排产反推 start -->\n  <!-- ⚠️ 本段为手工维护（含 MOA 实测回填），勿重跑 build_section8.py：该脚本是旧「第八部分」生成器，会整体覆盖本段 -->',
        1,
    ),
]

for old, new, expected in REPS:
    cnt = s.count(old)
    if cnt != expected:
        print(f"[ABORT] 匹配数 {cnt} != 期望 {expected}\n  片段: {old[:110]}")
        sys.exit(1)
    s = s.replace(old, new)

# ---- 图表数据一致性校验 ----
m = re.search(r"window\.SEC8_DATA = (\{.*?\});", s, re.S)
assert m, "SEC8_DATA 未找到"
import json
d = json.loads(m.group(1))
assert d["gui"]["y2026a"][9] == 66.0 and d["gui"]["y2026f"][9] is None
assert d["lu"]["y2026a"][9] == 33.7 and d["lu"]["y2026f"][9] is None
assert d["gui"]["y2026f"][10:] == [61.2, 55.8]
assert d["lu"]["y2026f"][10:] == [27.0, 26.0]
print("[OK] SEC8_DATA：10 月转入实线、11/12 月保留预测虚线")

# ---- 标签配平 ----
for t in ["div", "table", "thead", "tbody", "tr", "td", "th", "h3", "span", "a", "b", "section", "sup"]:
    o = len(re.findall(r"<%s(?=[\s>])" % t, s))
    c = len(re.findall(r"</%s>" % t, s))
    if o != c:
        print(f"[ABORT] 标签不配平 <{t}>: {o} / {c}")
        sys.exit(1)
print("[OK] 13 类标签全配平")

# ---- 残留检查 ----
assert "76.9*" not in s and "31.0*" not in s
assert "10–12 月预测" not in s
assert "9–12 月为预测" not in s
print("[OK] 无「10–12 月预测」等过时表述残留")

open(HTML, "w", encoding="utf-8").write(s)
print(f"[DONE] 已回填 10 月实测（鳜 66.0 / 鲈 33.7），共 {len(REPS)} 处替换")
