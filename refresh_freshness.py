#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
refresh_freshness.py — 看板数据新鲜度单一真源 + 自动回写

问题背景：
  此前看板内所有「价源日期」都是手写散落在 HTML 各处的文本。每日 09:30 的
  GitHub Actions(daily-crawl.yml) 只更新了底层数据文件(fish_prices_history.csv 等)，
  却没有回写看板文字，导致：
    1) 即便自动源(MOA/新发地)已抓到 10-10 数据，看板仍显示 10-09；
    2) 手动源(公众号/视频号/腾氏/抖音/综述)过期后静默躺平，无可见告警；
    3) 不同位置的同一数据源日期不同步(a渔业区块写 08-11、汇总写 09-15)。

本脚本做三件事：
  A. 从真实数据文件反推「自动源」最新日期(MOA CSV / 新发地 CSV / wechat_ocr_current.json
     / qianyan_state.json / 看板 UPDATED_AT)，手动源日期读 manifest.manual_dates；
  B. 计算新鲜度(🟢正常/🟡偏旧/🔴已过期)，渲染「数据新鲜度总览」面板；
  C. 幂等回写看板：顶部 chip 行、a渔业「截至」行、第五节各源日期、修正误导性 RPA 文案。

用法：
  python refresh_freshness.py            # 本地/CI 运行，就地改写看板 HTML
  python refresh_freshness.py --today 2026-10-10   # 指定基准日(测试用)
  python refresh_freshness.py --dry      # 只打印，不写文件

依赖：仅标准库。
"""
import csv
import json
import re
import sys
from datetime import date, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent
HTML = ROOT / "鳜鱼鲈鱼价格看板.html"
MANIFEST = ROOT / "data_sources_manifest.json"
FRESH_STATE = ROOT / "freshness_state.json"

# ───────────────────────────── 日期工具 ─────────────────────────────
def parse_d(s: str):
    s = (s or "").strip()
    for fmt in ("%Y-%m-%d", "%Y/%m/%d"):
        try:
            return datetime.strptime(s[:10], fmt).date()
        except Exception:
            continue
    return None

def to_mmdd(s: str) -> str:
    d = parse_d(s)
    return d.strftime("%m-%d") if d else (s or "")

# ───────────────────────────── 数据源探测 ─────────────────────────────
def get_moa():
    p = ROOT / "fish_prices_history.csv"
    if not p.exists():
        return None, 0, 0
    dates, n = set(), 0
    with open(p, encoding="utf-8-sig", newline="") as f:
        for row in csv.DictReader(f):
            d = (row.get("日期") or "").strip()
            if d:
                dates.add(d); n += 1
    return (max(dates) if dates else None), n, len(dates)

def get_public():
    p = ROOT / "public_fish_prices.csv"
    if not p.exists():
        return None
    dates = []
    with open(p, encoding="utf-8-sig", newline="") as f:
        for row in csv.DictReader(f):
            if (row.get("来源") or "").startswith("北京新发地"):
                d = (row.get("发布日期") or "").strip()
                if d:
                    dates.append(d)
    return max(dates) if dates else None

def get_ocr(key):
    p = ROOT / "wechat_ocr_current.json"
    if not p.exists():
        return None
    try:
        d = json.loads(p.read_text(encoding="utf-8"))
        arr = d.get(key)
        if arr and isinstance(arr, list) and arr[0].get("price_date"):
            return arr[0]["price_date"]
    except Exception:
        pass
    return None

def get_qianyan():
    p = ROOT / "qianyan_state.json"
    if not p.exists():
        return None, None
    try:
        d = json.loads(p.read_text(encoding="utf-8"))
        return d.get("latest_date"), d.get("latest_issue")
    except Exception:
        return None, None

def get_douyin():
    """从 TikHub 快照文件名 douyin_live_YYYYMMDD.json 反推抓取日期 + 条数（最新一个）。"""
    cands = sorted(ROOT.glob("douyin_live_*.json"))
    if not cands:
        return None, 0
    m = re.search(r"(\d{8})", cands[-1].name)
    if m:
        s = m.group(1)
        d = f"{s[:4]}-{s[4:6]}-{s[6:8]}"
        try:
            n = len(json.loads(cands[-1].read_text(encoding="utf-8")))
        except Exception:
            n = 0
        return d, n
    return None, 0

def get_weather(html: str):
    m = re.search(r'data-updated-at="([^"]+)"', html)
    if m:
        return parse_d(m.group(1))
    return None

# ───────────────────────────── 新鲜度计算 ─────────────────────────────
def status_of(d: date, today: date, auto: bool, cadence: int):
    if d is None:
        return "🔴", "缺数据", 999
    age = (today - d).days
    if auto:
        if age <= cadence:
            return "🟢", "自动正常", age
        if age <= cadence * 3:
            return "🟡", "自动偏旧", age
        return "🔴", "⚠️自动任务异常", age
    else:
        if age <= cadence:
            return "🟢", "正常", age
        if age <= cadence * 2:
            return "🟡", "偏旧·待补", age
        return "🔴", "已过期·待补", age

# ───────────────────────────── 面板渲染 ─────────────────────────────
def _table(rows):
    body = ''.join(
        f'<tr><td style="text-align:left">{r["name"]}</td>'
        f'<td>{r["date"] or "—"}</td>'
        f'<td>{r["age"]}天</td>'
        f'<td>{r["badge"]} {r["label"]}</td></tr>'
        for r in rows
    )
    return f'''<table class="ftab" style="width:100%;border-collapse:collapse;font-size:13px;background:rgba(255,255,255,.06);border-radius:10px;overflow:hidden;margin-bottom:10px">
      <thead>
        <tr style="background:rgba(255,255,255,.12);color:#fff">
          <th style="padding:8px 10px;text-align:left">数据源</th>
          <th style="padding:8px 10px">最新日期</th>
          <th style="padding:8px 10px">距今天数</th>
          <th style="padding:8px 10px">状态</th>
        </tr>
      </thead>
      <tbody>{body}</tbody>
    </table>'''

def render_panel(rows):
    auto_rows = sorted([r for r in rows if r["auto"]],
                       key=lambda r: -(r["age"] if r["age"] is not None else 999))
    manual_rows = sorted([r for r in rows if not r["auto"]],
                         key=lambda r: -(r["age"] if r["age"] is not None else 999))
    auto_bad = sum(1 for r in auto_rows if r["badge"] == "🔴")
    man_bad = sum(1 for r in manual_rows if r["badge"] == "🔴")
    return f'''<!-- FRESHNESS_LIVE_START -->
  <section class="sec-fresh" data-page-node-id="FRESHLIVE0001" style="margin:18px 0 6px">
    <div class="sec-head" data-page-node-id="FRESHHEAD001">
      <h2 data-page-node-id="FRESHTITLE01">🟢 数据新鲜度总览</h2>
      <span class="sub" data-page-node-id="FRESHSUB001">每日 09:30 自动任务回写 · 🔴 = 已超过刷新周期，请补数据（手动源需发截图/录入）</span>
    </div>
    <h3 data-page-node-id="FRESHAUTOH" style="margin:12px 0 8px;font-size:15px">🤖 自动更新源 <span style="font-weight:400;font-size:12px;opacity:.8">（每日 09:30 cron 自我刷新，无需人工干预{f'；🔴 {auto_bad} 项异常，请检查 Actions 日志' if auto_bad else '，当前全部正常'}）</span></h3>
    {_table(auto_rows)}
    <h3 data-page-node-id="FRESHMANH" style="margin:14px 0 8px;font-size:15px">✋ 手动源 <span style="font-weight:400;font-size:12px;opacity:.8">（无公开接口，需发截图/手动触发{f'；🔴 {man_bad} 项已过期，请补数据' if man_bad else ''}）</span></h3>
    {_table(manual_rows)}
  </section>
  <!-- FRESHNESS_LIVE_END -->'''

# ───────────────────────────── 主流程 ─────────────────────────────
def main():
    today = date.today()
    dry = "--dry" in sys.argv
    for i, a in enumerate(sys.argv):
        if a == "--today":
            today = parse_d(sys.argv[i + 1]) or today

    html = HTML.read_text(encoding="utf-8")
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    manual = manifest.get("manual_dates", {})

    # A. 探测各源日期
    moa_d, moa_n, moa_days = get_moa()
    public_d = get_public()
    kexue_d = get_ocr("科学养鱼")
    ayu_d = get_ocr("a渔业行情")
    qy_d, qy_issue = get_qianyan()
    weather_d = get_weather(html)
    douyin_date, douyin_count = get_douyin()

    eff = {
        "moa": moa_d, "public": public_d, "weather": weather_d.isoformat() if weather_d else None,
        "qianyan": qy_d, "kexue": kexue_d, "ayu": ayu_d,
        "tengshi": manual.get("tengshi"), "video": manual.get("video"),
        "douyin": douyin_date or manual.get("douyin"), "hot": manual.get("hot"),
    }

    # B. 新鲜度 + 面板行（红在前）
    rows = []
    for s in manifest["sources"]:
        k = s["key"]
        d = parse_d(eff.get(k)) if eff.get(k) else None
        badge, label, age = status_of(d, today, s["auto"], s["cadence"])
        rows.append({"key": k, "name": s["name"], "auto": s["auto"],
                     "date": eff.get(k), "badge": badge, "label": label, "age": age,
                     "note": s["note"], "status": s.get("status", "active")})
    rows.sort(key=lambda r: (-r["age"] if r["age"] is not None else 999))
    for r in rows:
        if r["badge"] == "🔴" and r.get("status") == "stale":
            r["label"] = "疑似停更·待确认"

    panel = render_panel(rows)

    # C. 幂等回写
    if "<!-- FRESHNESS_LIVE_START -->" in html:
        html = re.sub(r"<!-- FRESHNESS_LIVE_START -->.*?<!-- FRESHNESS_LIVE_END -->",
                      panel, html, flags=re.S)
    else:
        html = html.replace("  <!-- KPI -->", "  " + panel + "\n\n  <!-- KPI -->", 1)

    moa_mm = to_mmdd(moa_d); pub_mm = to_mmdd(public_d)
    kexue_mm = to_mmdd(kexue_d); ayu_mm = to_mmdd(ayu_d)
    ayu_full = eff.get("ayu") or "2026-09-15"
    qy_mm = to_mmdd(qy_d); qy_issue = qy_issue or 35
    tengshi = eff.get("tengshi") or "2026-10-08"
    douyin = eff.get("douyin") or "2026-10-10"

    subs = [
        # 顶部 chip 行（批发价汇总）
        (r'(<span class="chip" data-page-node-id="4HGb9s5gzmgXv3QvdK82PP">)[^<]*(</span>)',
         lambda m: m.group(1) + f"🤖 批发价：农业农村部接口爬虫（{moa_mm}）+ 公开价源爬虫（新发地 {pub_mm}）+ 科学养鱼OCR（{kexue_mm}）+ a渔业行情OCR（{ayu_mm}）" + m.group(2)),
        # 顶部简介：TikHub 抖音抓取日期（从 douyin_live_*.json 反推，修复写死 08-31）
        (re.compile(r'于 \d{4}-\d{2}-\d{2} 实时抓取'), f'于 {douyin} 实时抓取'),
        # 来源行：新发地日期（idempotent）
        (re.compile(r'公开价源爬虫（北京新发地 \d{2}-\d{2}）'), f'公开价源爬虫（北京新发地 {pub_mm}）'),
        # a渔业行情区块「截至」行（修复 08-11 → 真实日期不一致）
        (re.compile(r'按规格分组，截至 \d{4}-\d{2}-\d{2}'), f'按规格分组，截至 {ayu_full}'),
        # 第五节 水产前沿
        (re.compile(r'2026-06-22 ~ [\d-]+ · 分产区分规格塘头价（鳜鱼/加州鲈），核心数据来源；第\d+期（[\d-]+）为最新'),
         f'2026-06-22 ~ {qy_mm} · 分产区分规格塘头价（鳜鱼/加州鲈），核心数据来源；第{qy_issue}期（{qy_mm}）为最新'),
        # 第五节 MOA（含明细/交易日数）
        (re.compile(r'逐日累积至 <b>\d{4}-\d{2}-\d{2}</b>（\d+ 条明细 / \d+ 个交易日）'),
         f'逐日累积至 <b>{moa_d}</b>（{moa_n} 条明细 / {moa_days} 个交易日）'),
        # 第五节 公开价源
        (re.compile(r'（T-1，至 [\d-]+）'), f'（T-1，至 {pub_mm}）'),
        # 第五节 腾氏
        (re.compile(r'2026-07-17 ~ [\d-]+ · 最新第㊵期（[\d-]+ 发布'),
         f'2026-07-17 ~ {tengshi} · 最新第㊵期（{tengshi} 发布'),
        # 第五节 科学养鱼（以「· 全国水产品批发价」为上下文区分 a渔业）
        (r'(<b>)\d{4}-\d{2}-\d{2}(（最新一期）</b>· 全国水产品批发价)', lambda m: m.group(1) + (kexue_d or m.group(0)) + m.group(2)),
        # 第五节 a渔业（以「全国水产塘口价」为上下文区分）
        (r'(<b>)\d{4}-\d{2}-\d{2}(（最新一期）</b>全国水产塘口价)', lambda m: m.group(1) + ayu_full + m.group(2)),
        # 局限说明里的 MOA 区间
        (re.compile(r'2026-07-22~[\d-]+ 各市场真实报价'), f'2026-07-22~{moa_mm} 各市场真实报价'),
        # 修正误导性「已编排自动更新」文案（一次性，已应用则静默跳过）
        ('已纳入 RPA 截图 + OCR 流水线', '需用户截图后经 OCR 流水线'),
        # P0-2 兜底：任何残留的「GitHub Actions 已编排」自动纠正（防第1469行回归）
        ('GitHub Actions 已编排', '未接入定时任务'),
        ('（wechat_rpa.py 搜狗微信搜号→整页截图；wechat_ocr_pipeline.py 视觉 OCR→结构化→自动并入本看板），可定时自动更新；但纯文本爬虫仍无法直接抓文章正文（搜狗微信反爬）。',
         '（wechat_rpa.py 搜狗微信自动截图已就绪但<b>未接入定时任务</b>；wechat_ocr_pipeline.py 视觉 OCR→结构化→并入本看板）；纯文本爬虫仍无法直接抓文章正文（搜狗微信反爬），目前<b>仍为人工触发</b>，非全自动。'),
        # 抖音快照文案（兼容旧写法，幂等）
        (re.compile(r'当前下方帖子为 [\d-]+ 历史快照|抖音实时快照已于 [\d-]+ 刷新（\d+条）'),
         f'抖音实时快照已于 {douyin} 刷新（{douyin_count}条）'),
    ]

    for old, new in subs:
        if callable(new):
            html, n = re.subn(old, new, html)
        elif isinstance(old, re.Pattern):
            html, n = old.subn(new, html)
        else:
            # 一次性文案：未命中但新文案已在 → 视为已应用，静默
            if old in html:
                html = html.replace(old, new)
                n = 1
            elif new in html:
                n = 1
            else:
                n = 0
        if n == 0:
            print(f"  [warn] 未命中替换: {str(old)[:40]}...")

    if dry:
        print("== DRY RUN == 不写文件")
        for r in rows:
            print(f"  {r['badge']} {r['name']:<22} {r['date']}  {r['label']} ({r['age']}天)")
        return

    HTML.write_text(html, encoding="utf-8")
    FRESH_STATE.write_text(json.dumps(
        {"generated_at": today.isoformat(), "rows": rows}, ensure_ascii=False, indent=2),
        encoding="utf-8")
    print("== refresh_freshness 完成 ==")
    for r in rows:
        print(f"  {r['badge']} {r['name']:<22} {r['date']}  {r['label']} ({r['age']}天)")

if __name__ == "__main__":
    main()
