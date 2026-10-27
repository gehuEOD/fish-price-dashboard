#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
看板版本号管理 — 三个注入脚本共享
==================================

- 当前版本号 / 日期集中在 DASHBOARD_VERSION / DASHBOARD_VERSION_DATE
- bump_dashboard() 一次性同步：
    * HTML <title> 的版本号后缀
    * <meta name="dashboard-version"> 与 dashboard-version-date
    * Hero 区 chip-version 文本
    * 底部 VERSION_HISTORY 块里追加本次变更摘要
    * VERSION.md 表格追加一行

调用方式（注入脚本尾部）：
    from dashboard_version import bump_dashboard
    bump_dashboard(
        reason="天气数据刷新（无新增异常）",
        level="patch",            # patch / minor / major
    )

语义版本号规则（与 VERSION.md 对齐）：
- PATCH：数据/文案微调、社媒数据追加
- MINOR：新增板块、接入新数据源、引入双源校验
- MAJOR：整体改版、迁移到非 HTML 载体
"""
from __future__ import annotations
import os, re
from datetime import datetime

WS = os.path.dirname(os.path.abspath(__file__))
HTML = os.path.join(WS, "鳜鱼鲈鱼价格看板.html")
VERSION_MD = os.path.join(WS, "VERSION.md")
HISTORY_CSV = os.path.join(WS, "fish_prices_history.csv")

# ============================================================
# 版本号常量 —— 改这里，所有脚本同步
# ============================================================
DASHBOARD_VERSION       = "v1.0.1"
DASHBOARD_VERSION_DATE  = "2026-09-01"
DASHBOARD_OPERATOR      = "江苏环荟"
DASHBOARD_LOCATION      = "江苏环荟·宜兴官林镇数字低碳生态养殖项目"


# ============================================================
# 内部 helper
# ============================================================
def _today_str() -> str:
    return datetime.now().strftime("%Y-%m-%d")


def _current_version_from_html() -> str:
    """从看板 HTML 里读当前已落地的 DASHBOARD_VERSION（避免模块常量与 HTML 漂移）"""
    if not os.path.exists(HTML):
        return DASHBOARD_VERSION
    try:
        with open(HTML, encoding="utf-8") as f:
            text = f.read()
    except OSError:
        return DASHBOARD_VERSION
    m = re.search(r'<meta name="dashboard-version" content="(v\d+\.\d+\.\d+)"', text)
    return m.group(1) if m else DASHBOARD_VERSION


def _bump(level: str, current: str) -> str:
    """语义化 bump：v1.2.3 + patch → v1.2.4"""
    m = re.match(r"^v(\d+)\.(\d+)\.(\d+)$", current.strip())
    if not m:
        raise ValueError(f"非法版本号: {current}")
    maj, minor, pat = map(int, m.groups())
    if level == "patch":
        pat += 1
    elif level == "minor":
        minor += 1
        pat = 0
    elif level == "major":
        maj += 1
        minor = 0
        pat = 0
    else:
        raise ValueError(f"未知 level: {level}，须为 patch/minor/major")
    return f"v{maj}.{minor}.{pat}"


def _sync_html(html_text: str, version: str, date_str: str, summary_line: str) -> str:
    """把新版号 + 变更摘要同步到看板 HTML（含 5 处锚点）"""
    # 1) <title> 里替换旧日期/版本号
    html_text = re.sub(
        r"（\d{4}-\d{2}-\d{2} 更新(?: · v\d+\.\d+\.\d+)?）",
        f"（{date_str} 更新 · {version}）",
        html_text,
        count=1,
    )
    # 2) <meta name="dashboard-version"> 版本号
    html_text = re.sub(
        r'(<meta name="dashboard-version" content=")v\d+\.\d+\.\d+(">)',
        rf"\g<1>{version}\g<2>",
        html_text,
    )
    # 3) <meta name="dashboard-version-date">
    html_text = re.sub(
        r'(<meta name="dashboard-version-date" content=")\d{4}-\d{2}-\d{2}(">)',
        rf"\g<1>{date_str}\g<2>",
        html_text,
    )
    # 3.5) HTML 头部注释 <!-- Dashboard vX.Y.Z · YYYY-MM-DD · 变更摘要见 VERSION.md -->
    html_text = re.sub(
        r"<!-- Dashboard v\d+\.\d+\.\d+ · \d{4}-\d{2}-\d{2} · 变更摘要见 VERSION\.md -->",
        f"<!-- Dashboard {version} · {date_str} · 变更摘要见 VERSION.md -->",
        html_text,
        count=1,
    )
    # 4) chip-version 文本
    html_text = re.sub(
        r'<span class="chip chip-version"[^>]*>🏷️ 版本 v\d+\.\d+\.\d+ · \d{4}-\d{2}-\d{2}</span>',
        f'<span class="chip chip-version" data-page-node-id="VER01CHIP0001" title="看板版本号 · 完整历史见 VERSION.md">🏷️ 版本 {version} · {date_str}</span>',
        html_text,
    )
    # 5) 底部 VERSION_HISTORY 块：在 start/end 锚点之间替换「本次更新」h3 与首条 li（其余保留）
    new_block = re.sub(
        r"<strong[^>]*>本次更新 · v\d+\.\d+\.\d+（\d{4}-\d{2}-\d{2}）</strong>",
        f"<strong style=\"font-size:15px;letter-spacing:.5px\">本次更新 · {version}（{date_str}）</strong>",
        "",
        count=1,
    )  # 此处仅统计是否命中；下面单独做替换更稳

    block_re = re.compile(
        r"(<!-- VERSION_HISTORY_START -->)(.*?)(<!-- VERSION_HISTORY_END -->)",
        re.S,
    )
    m = block_re.search(html_text)
    if not m:
        return html_text

    head, body, tail = m.group(1), m.group(2), m.group(3)
    # 在 body 的第一个 <li> 前插入新变更摘要，再把"本次更新"标题改成最新
    body = re.sub(
        r"<strong[^>]*>本次更新 · v\d+\.\d+\.\d+（\d{4}-\d{2}-\d{2}）</strong>",
        f"<strong style=\"font-size:15px;letter-spacing:.5px\">本次更新 · {version}（{date_str}）</strong>",
        body,
        count=1,
    )
    new_li = f'      <li><b>{version} · {date_str}</b> · {summary_line}</li>\n'
    body = re.sub(
        r"(<ul[^>]*>\n)",
        r"\1" + new_li,
        body,
        count=1,
    )
    html_text = html_text[:m.start()] + head + body + tail + html_text[m.end():]
    return html_text


def _sync_version_md(version: str, date_str: str, summary_line: str) -> None:
    """在 VERSION.md 表格里追加一行"""
    if not os.path.exists(VERSION_MD):
        return
    with open(VERSION_MD, encoding="utf-8") as f:
        text = f.read()
    # 找到"## 历史记录"下方表格的"---"线，在其后插入新行
    marker = "| 版本 | 日期 | 变更摘要 |\n|------|------|---------|"
    new_row = f"| **{version}** | {date_str} | {summary_line} |\n"
    if marker in text:
        # 在 marker 紧跟着的下一行（即历史第一条 v1.0.1 那行）之前插入
        text = text.replace(marker, marker + "\n" + new_row, 1)
    else:
        # 兜底：直接在文件末尾追加
        text = text.rstrip() + "\n\n" + new_row
    with open(VERSION_MD, "w", encoding="utf-8") as f:
        f.write(text)


# ============================================================
# 「看板更新」时间戳（Hero 区版本行下方单独一行）
# ============================================================
UPDATED_START = "<!-- UPDATED_AT_START -->"
UPDATED_END   = "<!-- UPDATED_AT_END -->"


def _cn_datetime(dt: datetime) -> str:
    """2026-09-11 09:52 → 2026年9月11日 09:52"""
    return f"{dt.year}年{dt.month}月{dt.day}日 {dt.hour:02d}:{dt.minute:02d}"


def stamp_updated_at(dt: datetime | None = None, html_path: str = HTML) -> str:
    """
    刷新看板 Hero 区「看板更新：YYYY年M月D日 HH:MM」时间戳（Asia/Shanghai）。

    幂等：只替换 UPDATED_AT_START..END 区块内的 <b> 文本与 data-updated-at 属性；
    区块不存在则原样返回（不破坏看板）。任何注入脚本跑完都应调用一次，
    这样打开看板就能知道「什么时候更的、有没有更过」。

    返回: 形如 '2026年9月11日 09:52' 的字符串
    """
    try:
        from zoneinfo import ZoneInfo
        now = dt or datetime.now(ZoneInfo("Asia/Shanghai"))
    except Exception:
        now = dt or datetime.now()

    cn = _cn_datetime(now)
    iso = now.strftime("%Y-%m-%dT%H:%M:%S") + "+08:00"

    if not os.path.exists(html_path):
        return cn
    with open(html_path, encoding="utf-8") as f:
        text = f.read()

    if UPDATED_START not in text or UPDATED_END not in text:
        return cn

    s = text.index(UPDATED_START)
    e = text.index(UPDATED_END) + len(UPDATED_END)
    block = text[s:e]

    block = re.sub(
        r"看板更新：\d{4}年\d{1,2}月\d{1,2}日 \d{2}:\d{2}",
        f"看板更新：{cn}",
        block,
    )
    block = re.sub(
        r'data-updated-at="[^"]*"',
        f'data-updated-at="{iso}"',
        block,
        count=1,
    )

    with open(html_path, "w", encoding="utf-8") as f:
        f.write(text[:s] + block + text[e:])
    return cn


# ============================================================
# 公共入口
# ============================================================
def bump_dashboard(
    reason: str,
    level: str = "patch",
    version: str = "",
    date_str: str = "",
) -> str:
    """
    把看板版本号升级到下一级；同时把变更摘要同步到 HTML + VERSION.md

    参数:
        reason  : 本次变更摘要（中文一句话，写入 VERSION_HISTORY 第一个 <li> 与 VERSION.md 表格）
        level   : 'patch' / 'minor' / 'major'（默认 patch）
        version : 可选，强制指定版本号（默认按 level 从 HTML 当前值自动 bump）
        date_str: 可选，强制日期（默认今天）

    返回: 升级后的版本号字符串，如 'v1.0.2'
    """
    # 始终从 HTML 读当前值（而非模块常量），杜绝多次 bump 后模块常量与 HTML 漂移
    base = _current_version_from_html() or DASHBOARD_VERSION
    target_version = version or _bump(level, base)
    target_date    = date_str or _today_str()

    summary_line = reason.strip()
    if not summary_line:
        summary_line = "数据/文案微调"

    # 1) 同步看板 HTML
    if os.path.exists(HTML):
        with open(HTML, encoding="utf-8") as f:
            html_text = f.read()
        html_text = _sync_html(html_text, target_version, target_date, summary_line)
        with open(HTML, "w", encoding="utf-8") as f:
            f.write(html_text)

    # 2) 同步 VERSION.md
    _sync_version_md(target_version, target_date, summary_line)

    # 2.5) 同步派生元信息（统计周期 / TikHub 抓取说明）——从数据文件推导，防脱钩
    try:
        sync_meta(HTML, verbose=False)
    except Exception as e:
        print(f"[warn] 派生元信息同步跳过：{e}")

    # 3) 更新模块常量（让调用方后续 print 用得到；下次 import 时仍以源文件为准，
    #    但 bump_dashboard 内部总是从 HTML 重新读，所以即使常量停留也安全）
    DASHBOARD_VERSION = target_version
    DASHBOARD_VERSION_DATE = target_date

    return target_version


# ============================================================
# 派生元信息自动同步（统计周期 / 抖音抓取日期）
# ------------------------------------------------------------
# 背景：这两处历史上手工维护，曾出现 Hero chip 停在 10-10、页脚停在 10-19、
# 而历史数据实际已到 10-26 的「三处互不相等」脱钩事故。现改为从数据文件推导。
# ============================================================
def period_range():
    """从 fish_prices_history.csv 推导批发价历史序列的真实日期范围。

    返回: (start, end, rows)；读不到有效数据时返回 (None, None, 0)
    """
    import csv
    if not os.path.exists(HISTORY_CSV):
        return None, None, 0
    dates, rows = [], 0
    try:
        with open(HISTORY_CSV, encoding="utf-8-sig") as f:
            for r in csv.DictReader(f):
                rows += 1
                d = (r.get("日期") or "").strip()
                if re.match(r"^\d{4}-\d{2}-\d{2}$", d):
                    dates.append(d)
    except Exception:
        return None, None, 0
    if not dates:
        return None, None, 0
    return min(dates), max(dates), rows


def latest_douyin_snapshot():
    """从 TikHub 快照 douyin_live_YYYYMMDD.json 取最新快照日期与条数。"""
    cands = sorted(os.path.join(WS, p) for p in os.listdir(WS)
                   if re.match(r"^douyin_live_\d{8}\.json$", p))
    if not cands:
        return None, 0
    last = cands[-1]
    m = re.search(r"(\d{8})", os.path.basename(last))
    if not m:
        return None, 0
    s = m.group(1)
    d = f"{s[:4]}-{s[4:6]}-{s[6:8]}"
    try:
        import json
        n = len(json.loads(open(last, encoding="utf-8").read()))
    except Exception:
        n = 0
    return d, n


def sync_period(html_path: str = HTML, verbose: bool = True):
    """把「统计周期」同步为历史批发价序列的真实起止日期（Hero chip + 页脚两处）。

    幂等：只做正则替换，匹配不到就原样返回并给警告，不破坏文件。
    """
    start, end, rows = period_range()
    if not (start and end):
        if verbose:
            print("[warn] 统计周期同步失败：fish_prices_history.csv 无有效日期")
        return None
    period = f"{start} ~ {end}"
    try:
        with open(html_path, encoding="utf-8") as f:
            text = f.read()
    except Exception as e:
        print(f"[warn] 读取看板失败：{e}")
        return None

    before = text
    pat_chip = r"(📅\s*统计周期：)\d{4}-\d{2}-\d{2}\s*~\s*\d{4}-\d{2}-\d{2}"
    pat_foot = r"(统计周期\s+)\d{4}-\d{2}-\d{2}\s*~\s*\d{4}-\d{2}-\d{2}"
    n_chip = len(re.findall(pat_chip, text))
    n_foot = len(re.findall(pat_foot, text))
    text = re.sub(pat_chip, r"\g<1>" + period, text)
    text = re.sub(pat_foot, r"\g<1>" + period, text)

    if text != before:
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(text)
    if verbose:
        print(f"[ok] 统计周期 -> {period}（{rows} 行 · chip {n_chip} 处 / 页脚 {n_foot} 处）")
    return period


def sync_douyin_note(html_path: str = HTML, verbose: bool = True):
    """把 Hero 段「抖音社媒互动数据由 TikHub 抖音搜索接口 于 YYYY-MM-DD 实时抓取」
    的日期同步为最新 TikHub 快照日期。"""
    d, n = latest_douyin_snapshot()
    if not d:
        if verbose:
            print("[warn] TikHub 说明同步失败：未找到 douyin_live_YYYYMMDD.json")
        return None
    try:
        with open(html_path, encoding="utf-8") as f:
            text = f.read()
    except Exception as e:
        print(f"[warn] 读取看板失败：{e}")
        return None

    pat = r"(TikHub 抖音搜索接口</b>\s*于\s*)\d{4}-\d{2}-\d{2}( 实时抓取)"
    before = text
    text = re.sub(pat, r"\g<1>" + d + r"\g<2>", text)
    if text != before:
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(text)
    if verbose:
        print(f"[ok] TikHub 抓取说明 -> {d}（{n} 条快照）")
    return d


def sync_meta(html_path: str = HTML, verbose: bool = True):
    """统一入口：同步所有「可从数据文件推导」的派生元信息。
    任何注入脚本 / bump 之后跑一次即可，避免手工维护再次失同步。"""
    p = sync_period(html_path, verbose)
    d = sync_douyin_note(html_path, verbose)
    return {"period": p, "douyin_live": d}


if __name__ == "__main__":
    # 单独调试：bump_dashboard(reason="手动测试 bump", level="patch")
    import sys, argparse
    ap = argparse.ArgumentParser(description="手动 bump 看板版本号")
    ap.add_argument("--reason", default="手动 bump")
    ap.add_argument("--level", default="patch", choices=["patch", "minor", "major"])
    ap.add_argument("--dry-run", action="store_true", help="只打印新版本号，不写文件")
    args = ap.parse_args()

    if args.dry_run:
        base = _current_version_from_html()
        new_v = _bump(args.level, base)
        print(f"[DRY-RUN] {base} → {new_v}（{_today_str()}）· {args.reason}")
        sys.exit(0)

    new_v = bump_dashboard(reason=args.reason, level=args.level)
    print(f"✅ 已 bump 到 {new_v}（{_today_str()}） · {args.reason}")
    print(f"   HTML: {HTML}")
    print(f"   VERSION.md: {VERSION_MD}")
