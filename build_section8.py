#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生成看板「第八部分 · 月度价格对比 / 2026 预测 / 养殖排产反推」
============================================================
读 monthly_xinfadi_prices.json（北京新发地 2024-01~2026-08 真实月度批发均价，元/公斤）
  - 月度对比：2024 / 2025 / 2026(实际1-8月) 三条线
  - 2026 预测：9-12 月 = 历史同期(2024/2025)均值 × 年际偏差系数 k
              k = 2026前8月均值 / 历史(2024+2025)前8月均值
  - 拐点：基于 2024+2025 两年 12 月真实均值的低点月 / 高点月
  - 排产反推：出塘目标=价格高点月，投苗月=高点月−养殖周期(行业经验值)

产出：一段完整 <section> + 内联 window.SEC8_DATA + Chart.js 初始化，
      注入到 鳜鱼鲈鱼价格看板.html 的 </body> 之前。
"""
import json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
HTML = os.path.join(HERE, "鳜鱼鲈鱼价格看板.html")
DATA = os.path.join(HERE, "monthly_xinfadi_prices.json")

data = json.load(open(DATA, encoding="utf-8"))
idx = {}
for r in data:
    idx[(r["品种"], r["年份"], r["月份"])] = r["月均价_元公斤"]

def ys(sp, y):
    return [idx.get((sp, y, m)) for m in range(1, 13)]

gui = {"2024": ys("鳜鱼", 2024), "2025": ys("鳜鱼", 2025), "2026": ys("鳜鱼", 2026)}
lu  = {"2024": ys("鲈鱼", 2024), "2025": ys("鲈鱼", 2025), "2026": ys("鲈鱼", 2026)}


def predict(y26, y24, y25):
    """返回 (k, [(月, 预测, 下限, 上限), ...])，预测 9-12 月。"""
    h = (sum(y24[:8]) + sum(y25[:8])) / 16.0
    c = sum(y26[:8]) / 8.0
    k = round(c / h, 3) if h else 1.0
    out = []
    for m in range(8, 12):  # 9-12 月
        base = (y24[m] + y25[m]) / 2.0
        p = base * k
        lo = min(y24[m], y25[m]) * k
        hi = max(y24[m], y25[m]) * k
        out.append((m + 1, round(p, 1), round(lo, 1), round(hi, 1)))
    return k, out


kg_gui, preds_gui = predict(gui["2026"], gui["2024"], gui["2025"])
kg_lu,  preds_lu  = predict(lu["2026"],  lu["2024"],  lu["2025"])


def avg12(y24, y25):
    return [round((y24[m] + y25[m]) / 2.0, 1) for m in range(12)]

avg_gui = avg12(gui["2024"], gui["2025"])
avg_lu  = avg12(lu["2024"],  lu["2025"])
lo_gui = avg_gui.index(min(avg_gui)) + 1
hi_gui = avg_gui.index(max(avg_gui)) + 1
lo_lu  = avg_lu.index(min(avg_lu)) + 1
hi_lu  = avg_lu.index(max(avg_lu)) + 1

# 2026 年内剩余（9-12 预测）高点月 —— 面向当下排产的可操作高点
peak_gui = max(preds_gui, key=lambda x: x[1])[0]
peak_lu  = max(preds_lu,  key=lambda x: x[1])[0]
peak_gui_val = dict((m, p) for m, p, _, _ in preds_gui).get(peak_gui)
peak_lu_val  = dict((m, p) for m, p, _, _ in preds_lu).get(peak_lu)

cycles = {"鳜鱼": (6, 8), "鲈鱼": (5, 7)}
def sow_window(peak, cyc):
    lo_c, hi_c = cyc
    s, e = peak - hi_c, peak - lo_c
    if s <= 0: s += 12
    if e <= 0: e += 12
    return s, e


# ---------- 月度均价对比表 ----------
MONTHS = [f"{m}月" for m in range(1, 13)]

def fnum(v):
    return f"{v:.1f}" if v is not None else "—"

def monthly_table(sp_key, preds):
    """sp_key: 'gui' / 'lu'；生成 12 行 × (2024/2025/2026) 表。"""
    d = gui if sp_key == "gui" else lu
    pred_map = {mm: p for mm, p, _, _ in preds}
    rows = ""
    for m in range(12):
        v24 = fnum(d["2024"][m])
        v25 = fnum(d["2025"][m])
        if m < 8:
            v26 = fnum(d["2026"][m])
            v26_cell = v26
        else:
            pv = pred_map.get(m + 1)
            v26_cell = f'<span style="color:#e5484d;font-weight:600">{pv:.1f}*</span>' if pv else "—"
        rows += (f"<tr><td>{MONTHS[m]}</td><td>{v24}</td><td>{v25}</td>"
                 f"<td>{v26_cell}</td></tr>\n")
    return rows

rows_gui = monthly_table("gui", preds_gui)
rows_lu  = monthly_table("lu", preds_lu)

# ---------- 排产反推表 ----------
sg, eg = sow_window(peak_gui, cycles["鳜鱼"])
sl, el = sow_window(peak_lu,  cycles["鲈鱼"])

sow_rows = f"""
  <tr><td><span class="tag tag-gui">鳜鱼</span></td>
      <td>{hi_gui}月（两年均值峰值，中秋国庆前）</td>
      <td>{peak_gui}月（预测高点，约 {peak_gui_val:.0f} 元/公斤）</td>
      <td>{peak_gui}月（年内剩余最高点）</td>
      <td>6–8</td>
      <td>当年 {sg}–{eg} 月（针对 2026 年 9 月出塘；当下 8 月底该批苗已养 5–7 个月，临近上市）</td></tr>
  <tr><td><span class="tag tag-lu">鲈鱼</span></td>
      <td>{lo_lu}–{hi_lu}月（夏季至初秋，两年均值高区）</td>
      <td>{peak_lu}月（预测高点，约 {peak_lu_val:.0f} 元/公斤）</td>
      <td>{peak_lu}月（年内剩余最高点）</td>
      <td>5–7</td>
      <td>当年 {sl}–{el} 月（针对 2026 年 9 月出塘；当前临近上市）</td></tr>
"""

# ---------- 图表数据 ----------
def fcst_arr(y26, preds):
    actual = y26[:8] + [None] * 4
    f = [None] * 8 + [p for _, p, _, _ in preds]
    return actual, f

ga, gf = fcst_arr(gui["2026"], preds_gui)
la, lf = fcst_arr(lu["2026"],  preds_lu)

sec8_data = {
    "labels": MONTHS,
    "gui": {"y2024": gui["2024"], "y2025": gui["2025"], "y2026a": ga, "y2026f": gf},
    "lu":  {"y2024": lu["2024"],  "y2025": lu["2025"],  "y2026a": la, "y2026f": lf},
}

# ---------- 组装 section8 ----------
section = f"""
  <!-- 八、月度价格对比 · 2026预测 · 养殖排产反推 start -->
  <section>
    <div class="sec-head">
      <span class="bar" style="background:#e5484d"></span>
      <h2>八、月度价格对比 · 2026 预测 · 养殖排产反推</h2>
      <span class="note">数据口径：北京新发地批发价（元/公斤）· 真实历史 2024-01~2026-08</span>
    </div>

    <div class="callout" style="margin-bottom:14px">
      <b>核心目的：</b>用 2024–2025 真实月度均价看清价格季节性拐点，结合 2026 年实际（1–8 月）外推 9–12 月预测，
      <b>反推出塘时间 → 倒推鱼苗投放窗口</b>，争取在价格高点出塘。
      <br>· 当月均价 = 该月全部交易日 avgPrice 平均（即你建议的「当月平均价」）。
      · 预测 = 历史同期（2024/2025）均值 × 年际偏差系数 k；鳜鱼 k={kg_gui}（今年偏强）、鲈鱼 k={kg_lu}（今年偏弱）。
      · 拐点基于 2024+2025 两年 12 月真实均价。<b>新发地为北京销地批发价，绝对价高于塘头价；但季节性拐点月份对排产决策可靠，绝对价格请结合本地塘头价与当年供需微调。</b>
      历史实际峰值：鳜鱼多在 8–9 月（2025-09 达 118 元/公斤）、鲈鱼夏季 6–8 月——规律与下方预测一致。
    </div>

    <div class="card">
      <h3>📈 鳜鱼（桂鱼）月度批发均价对比（元/公斤）</h3>
      <div style="position:relative;height:340px"><canvas id="sec8Gui"></canvas></div>
      <div class="csub" style="margin-top:8px">实线为真实月度均价；红色虚线为 2026 年 9–12 月预测。
      规律：冬季（11–3 月）低谷 ~57–72，夏季走高，<b>9 月中秋国庆前暴涨至全年峰值</b>（2024-07 达 116、2025-09 达 118）。</div>
      <table style="margin-top:12px">
        <thead><tr><th>月份</th><th>2024</th><th>2025</th><th>2026（实际/预测*）</th></tr></thead>
        <tbody>
{rows_gui}        </tbody>
      </table>
    </div>

    <div class="card">
      <h3>📈 鲈鱼月度批发均价对比（元/公斤）</h3>
      <div style="position:relative;height:340px"><canvas id="sec8Lu"></canvas></div>
      <div class="csub" style="margin-top:8px">实线为真实月度均价；红色虚线为 2026 年 9–12 月预测。
      规律：冬季（12–3 月）低谷 ~30–35，<b>夏季（6–8 月）走高、初秋次高</b>，高点比鳜鱼早；2026 年整体偏弱（夏季仅 ~33–35）。</div>
      <table style="margin-top:12px">
        <thead><tr><th>月份</th><th>2024</th><th>2025</th><th>2026（实际/预测*）</th></tr></thead>
        <tbody>
{rows_lu}        </tbody>
      </table>
    </div>

    <div class="card">
      <h3>🎯 价格拐点与养殖排产反推（抢高点出塘）</h3>
      <div class="csub">逻辑：<b>出塘目标月 = 价格高点月</b>；<b>投苗月 = 高点月 − 养殖周期</b>。
      养殖周期为行业经验值（受水温/模式/病害影响，需结合本地实际微调）。</div>
      <table style="margin-top:12px">
        <thead><tr><th>品种</th><th>历史价格高点月</th><th>2026 预测高点月</th><th>建议出塘目标窗口</th><th>养殖周期(月)</th><th>建议投苗窗口</th></tr></thead>
        <tbody>
{sow_rows}        </tbody>
      </table>
      <div class="callout" style="margin-top:14px"><b>排产要点：</b>
      ① 鳜鱼 2026 年剩余高点为 <b>9 月</b>（预测约 {peak_gui_val:.0f} 元/公斤，仅次于 8 月实际值），对应投苗期 <b>今年 1–3 月</b>——当前 8 月底这批苗已养至 5–7 个月，正临近出塘，应做分批次上市准备；
      ② 鲈鱼 2026 年剩余高点为 <b>9 月</b>（预测约 {peak_lu_val:.0f} 元/公斤），对应投苗期 <b>今年 1–4 月</b>，同样临近上市；
      ③ 若错过 9 月主高峰，今年内价格将回落（鳜鱼 10–12 月降至 56–77、鲈鱼降至 31–38），建议转向布局 <b>下一年</b>高峰：按同逻辑整体前移 12 个月（如 2027 年 9 月出塘 → 2027 年 1–3 月投苗）；
      ④ 实际落地须叠加：本地塘头价经验、水温窗口（低温缓长）、病害与存塘节奏，避免「踩点」失误。</div>
    </div>

    <div class="callout" style="margin-top:14px"><b>方法与局限说明：</b>
    ① 历史为北京新发地单一销地市场批发价（元/公斤），不代表全国塘头价，绝对价仅供量级参考；
    ② 预测采用「历史同期均值 × 年际偏差系数」简洁模型，区间取历史同期 min/max × k，<b>仅为趋势参考，非承诺值</b>；
    ③ 2026 年 1–8 月为真实抓取，9–12 月为预测（图中红虚线，表中 * 标）；
    ④ 养殖周期为通用经验区间，请按你的养殖模式（标鳜/加州鲈、早苗/常规、配套饵料鱼）校准后使用。</div>
  </section>

  <script>
  window.SEC8_DATA = {json.dumps(sec8_data, ensure_ascii=False)};
  (function(){{
    const d = window.SEC8_DATA;
    if(typeof Chart==='undefined') return;
    function mk(canvasId, s, palette){{
      const cv = document.getElementById(canvasId);
      if(!cv) return;
      const y24=s.y2024, y25=s.y2025, y26a=s.y2026a, y26f=s.y2026f;
      new Chart(cv, {{
        type:'line',
        data:{{labels:d.labels, datasets:[
          {{label:'2024', data:y24, borderColor:'#94a3b8', backgroundColor:'#94a3b8', tension:.25, spanGaps:true, pointRadius:3, borderWidth:2}},
          {{label:'2025', data:y25, borderColor:'#12a150', backgroundColor:'#12a150', tension:.25, spanGaps:true, pointRadius:3, borderWidth:2}},
          {{label:'2026 实际', data:y26a, borderColor:'#e5484d', backgroundColor:'#e5484d', tension:.25, spanGaps:true, pointRadius:3, borderWidth:2.5}},
          {{label:'2026 预测', data:y26f, borderColor:'#e5484d', backgroundColor:'#e5484d', borderDash:[6,4], tension:.25, spanGaps:true, pointRadius:3, borderWidth:2, pointStyle:'rectRot'}}
        ]}},
        options:{{
          responsive:true, maintainAspectRatio:false,
          plugins:{{legend:{{position:'right',labels:{{boxWidth:10,font:{{size:11}}}}}},
            tooltip:{{callbacks:{{label:c=>c.dataset.label+'：'+(c.parsed.y==null?'—':c.parsed.y+' 元/公斤')}}}}}},
          scales:{{y:{{title:{{display:true,text:'元/公斤'}},grid:{{color:'#eef1f5'}}}},
                  x:{{grid:{{display:false}},title:{{display:true,text:'月份'}}}}}}
        }}
      }});
    }}
    mk('sec8Gui', d.gui);
    mk('sec8Lu', d.lu);
  }})();
  </script>
  <!-- 八、月度价格对比 · 2026预测 · 养殖排产反推 end -->
"""

# ---------- 注入 ----------
html = open(HTML, encoding="utf-8").read()

# ⚠️ 防回归护栏（2026-11-23）：本脚本是旧「第八部分」生成器，按月重新计算 9-12 月预测。
# 现网第九部分已由人工维护并回填 9-10 月 MOA 实测（10 月不再是预测价）。
# 由于 marker 用的是「八、」，在这里既匹配不到锚点、又会走 else 分支在 </body> 前
# 追加一份重复的旧版 section，把实测覆盖回预测。故检测到现网第九部分时直接拒绝执行。
if "<!-- 九、月度价格对比" in html:
    print("[ABORT] 现网第九部分为人工维护（含 9-10 月 MOA 实测回填），"
          "本旧「第八部分」生成器会覆盖实测为预测，已拒绝执行。"
          "如需改动请直接编辑 鳜鱼鲈鱼价格看板.html 的第九部分。")
    sys.exit(1)

marker = "<!-- 八、月度价格对比 · 2026预测 · 养殖排产反推 start -->"
if marker in html:
    # 已存在则整体替换（按锚点）
    i = html.find(marker)
    j = html.find("<!-- 八、月度价格对比 · 2026预测 · 养殖排产反推 end -->") + len("<!-- 八、月度价格对比 · 2026预测 · 养殖排产反推 end -->")
    html = html[:i] + section.strip() + "\n" + html[j:]
else:
    html = html.replace("</body>", section + "\n</body>")

open(HTML, "w", encoding="utf-8").write(html)
print(f"[OK] 第八部分已注入。鳜鱼 k={kg_gui} 拐点低{lo_gui}/高{hi_gui}月 预测高点{peak_gui}月；"
      f"鲈鱼 k={kg_lu} 拐点低{lo_lu}/高{hi_lu}月 预测高点{peak_lu}月")
