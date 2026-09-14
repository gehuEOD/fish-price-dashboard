#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
价源日期自动注入脚本
=====================
从 fish_prices_history.csv 自动读取农业农村部（MOA）最新日期，
结合命令行指定的科学养鱼 / a渔业行情日期，统一刷新 HTML 看板中所有价源日期标签，
避免手动 chip 日期与数据实际日期脱节。

用法：
    python3 inject_price_source_dates.py \
        --html 鳜鱼鲈鱼价格看板.html \
        --keyu-date 2026-09-14 \
        --afish-date 2026-09-11 \
        --afish-article-date 2026-09-13 \
        --塘口-dates 2026-09-10,2026-09-11,2026-09-13,2026-09-14

参数说明：
    --html                    目标 HTML 文件路径（默认：./鳜鱼鲈鱼价格看板.html）
    --moa-date                强制指定 MOA 最新日期；省略则从 fish_prices_history.csv 自动读取
    --keyu-date               「科学养鱼」公众号截图报价日期
    --afish-date              「a渔业行情」公众号截图报价日期
    --afish-article-date      「a渔业行情」公众号文章发布日期（用于 csub 说明）
    --塘口-dates               塘口价快照包含的日期，逗号分隔
    --history-csv             MOA 历史 CSV 路径（默认：./fish_prices_history.csv）
    --dry-run                 只打印变更预览，不写入文件
"""

import argparse
import csv
import re
import sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="自动注入价源日期到鳜鱼鲈鱼价格看板 HTML")
    parser.add_argument("--html", default="鳜鱼鲈鱼价格看板.html", help="目标 HTML 文件")
    parser.add_argument("--moa-date", default=None, help="农业农村部最新日期（YYYY-MM-DD，默认自动读取 CSV）")
    parser.add_argument("--keyu-date", default=None, help="科学养鱼截图报价日期（YYYY-MM-DD）")
    parser.add_argument("--afish-date", default=None, help="a渔业行情截图报价日期（YYYY-MM-DD）")
    parser.add_argument("--afish-article-date", default=None, help="a渔业行情文章发布日期（YYYY-MM-DD）")
    parser.add_argument("--塘口-dates", default=None, help="塘口价快照日期，逗号分隔（YYYY-MM-DD,...）")
    parser.add_argument("--history-csv", default="fish_prices_history.csv", help="MOA 历史 CSV 文件")
    parser.add_argument("--dry-run", action="store_true", help="仅预览，不写入")
    return parser.parse_args()


def read_moa_latest_date(csv_path: str) -> str:
    """从 fish_prices_history.csv 读取最大日期。"""
    path = Path(csv_path)
    if not path.exists():
        raise FileNotFoundError(f"找不到 MOA CSV 文件：{csv_path}")

    latest = ""
    with path.open(encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        if "日期" not in reader.fieldnames:
            raise ValueError(f"CSV 缺少 '日期' 列，字段名：{reader.fieldnames}")
        for row in reader:
            d = row.get("日期", "").strip()
            if d and d > latest:
                latest = d
    if not latest:
        raise ValueError("CSV 中未找到任何日期数据")
    return latest


def count_moa_lates(csv_path: str, date: str) -> dict:
    """统计指定日期 MOA 数据中各品种的样本数。"""
    counts = {"鳜鱼": 0, "鲈鱼": 0, "淡水鲈鱼": 0, "海水鲈鱼": 0}
    path = Path(csv_path)
    with path.open(encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get("日期", "").strip() != date:
                continue
            breed = row.get("品种", "").strip()
            if breed == "鳜鱼(活鳜)":
                counts["鳜鱼"] += 1
            elif breed == "淡水鲈鱼":
                counts["鲈鱼"] += 1
                counts["淡水鲈鱼"] += 1
            elif breed == "鲈鱼(海水)":
                counts["鲈鱼"] += 1
                counts["海水鲈鱼"] += 1
    return counts


def short_date(d: str) -> str:
    """2026-09-14 -> 09-14"""
    return d[5:]


def dot_date(d: str) -> str:
    """2026-09-14 -> 9.14"""
    m = int(d[5:7])
    day = int(d[8:10])
    return f"{m}.{day}"


def slash_date(d: str) -> str:
    """2026-09-14 -> 9/14"""
    m = int(d[5:7])
    day = int(d[8:10])
    return f"{m}/{day}"


def update_html(html_path: str, moa_date: str, keyu_date: str | None,
                afish_date: str | None, afish_article_date: str | None,
                塘口_dates: list[str] | None, history_csv: str, dry_run: bool) -> None:
    path = Path(html_path)
    if not path.exists():
        raise FileNotFoundError(f"找不到 HTML 文件：{html_path}")

    text = path.read_text(encoding="utf-8")
    original = text

    counts = count_moa_lates(history_csv, moa_date)

    # 1) 统计周期
    text = re.sub(
        r'(<span class="chip" data-page-node-id="sTnENG1kszfxF6zJ1kDy3a">📅 统计周期：2026-07-13 ~ )\d{4}-\d{2}-\d{2}(</span>)',
        rf'\g<1>{moa_date}\g<2>',
        text,
    )

    # 2) 价源来源 chip：科学养鱼OCR（MM-DD）+ a渔业行情OCR（MM-DD）
    k_short = short_date(keyu_date) if keyu_date else "??"
    a_short = short_date(afish_date) if afish_date else "??"
    text = re.sub(
        r'(科学养鱼OCR（)\d{2}-\d{2}(）[+]a渔业行情OCR（)\d{2}-\d{2}(）)',
        rf'\g<1>{k_short}\g<2>+ a渔业行情OCR（{a_short}\g<3>',
        text,
    )

    # 3) 鳜鱼/鲈鱼批发价 section 标题
    text = re.sub(
        r'(批发价（农业农村部接口爬虫 · )\d{4}-\d{2}-\d{2}(）)',
        rf'\g<1>{moa_date}\g<2>',
        text,
    )

    # 4) 鳜鱼 callout：最新抓取日期 + 当日
    text = re.sub(
        r'(最新抓取日期 )\d{4}-\d{2}-\d{2}',
        rf'\g<1>{moa_date}',
        text,
    )
    # 注意：上一条有效报价日期不应被替换，保持历史真实值

    # 5) 鲈鱼 callout
    freshwater = counts["淡水鲈鱼"]
    seawater = counts["海水鲈鱼"]
    total = freshwater + seawater
    text = re.sub(
        r'(※ )\d{4}-\d{2}-\d{2}( 爬虫实测：农业农村部接口返回 )\d+( 条鲈鱼样本（淡水鲈鱼 )\d+( 条、海水鲈鱼 )\d+( 条）。)',
        rf'※ {moa_date} 爬虫实测：农业农村部接口返回 {total} 条鲈鱼样本（淡水鲈鱼 {freshwater} 条、海水鲈鱼 {seawater} 条）。',
        text,
    )

    # 6) 科学养鱼 section note / csub 日期
    if keyu_date:
        text = re.sub(
            r'(<span class="note">)\d{4}-\d{2}-\d{2}( · 元/千克 · 已按图片数字录入</span>)',
            rf'\g<1>{keyu_date}\g<2>',
            text,
        )
        text = re.sub(
            r'(报价日期 )\d{4}-\d{2}-\d{2}(。本次含)',
            rf'\g<1>{keyu_date}\g<2>',
            text,
        )

    # 7) a渔业行情 section note / csub 日期
    if afish_date:
        text = re.sub(
            r'(<span class="note">)\d{4}-\d{2}-\d{2}( 全国水产塘口价 · 元/斤</span>)',
            rf'\g<1>{afish_date}\g<2>',
            text,
        )
        # 标题：分产区塘口价（M.D）
        ad = dot_date(afish_date)
        text = re.sub(
            r'(分产区塘口价\()\d\.\d+(\))',
            rf'\g<1>{ad}\g<2>',
            text,
        )
        if afish_article_date:
            text = re.sub(
                r'(公众号「a渔业行情」)\d{4}-\d{2}-\d{2}( 推送)',
                rf'\g<1>{afish_article_date}\g<2>',
                text,
            )
            text = re.sub(
                r'(表头标注报价日期 <b>)\d\.\d+(</b>)',
                rf'\g<1>{ad}\g<2>',
                text,
            )

    # 8) 塘口价快照标题与注释
    if 塘口_dates:
        sorted_dates = sorted(塘口_dates)
        display = "/".join(dot_date(d) for d in sorted_dates)
        text = re.sub(
            r'(补充 · 塘口价快照\()\d{4}-\d{2}-\d{2}(/\d{2}-\d{2}/\d{2}-\d{2}/\d{2}-\d{2} · 公众号/视频号 OCR\))',
            rf'补充 · 塘口价快照（{display} · 公众号/视频号 OCR）',
            text,
        )
        # 注释中的 9.10/9.11/9.13/9.14
        note_dates = "/".join(dot_date(d) for d in sorted_dates)
        text = re.sub(
            r'(兴渔派-鳜鱼通\()\d\.\d+/\d\.\d+(\) · 视频号)',
            rf'兴渔派-鳜鱼通（{note_dates}） · 视频号',
            text,
        )

    # 9) footer 元数据（批量替换）
    now = datetime.now(ZoneInfo("Asia/Shanghai"))
    cn_now = f"{now.year}年{now.month}月{now.day}日 {now.hour:02d}:{now.minute:02d}"
    text = re.sub(
        r'(看板更新 )\d{4}年\d{1,2}月\d{1,2}日 \d{2}:\d{2}',
        rf'看板更新 {cn_now}',
        text,
    )
    # footer 中紧凑格式：YYYY-MM-DD HH:MM
    text = re.sub(
        r'(看板更新 )\d{4}-\d{2}-\d{2} \d{2}:\d{2}',
        rf'看板更新 {cn_now}',
        text,
    )
    text = re.sub(
        r'(统计周期 2026-07-13 ~ )\d{4}-\d{2}-\d{2}',
        rf'\g<1>{moa_date}',
        text,
    )
    text = re.sub(
        r'(农业农村部爬虫抓取 )\d{4}-\d{2}-\d{2}',
        rf'\g<1>{moa_date}',
        text,
    )
    text = re.sub(
        r'(科学养鱼 OCR )\d{2}-\d{2}',
        rf'科学养鱼 OCR {k_short}',
        text,
    )

    # 10) 顶部看板更新时间戳
    iso_now = now.strftime("%Y-%m-%dT%H:%M:%S") + "+08:00"
    text = re.sub(
        r'data-updated-at="[^"]*"',
        f'data-updated-at="{iso_now}"',
        text,
        count=1,
    )

    if text == original:
        print("ℹ️  未检测到可替换的日期标签（可能已是最新）")
        return

    if dry_run:
        print("📝 预览模式（不写入文件）")
        # 简单展示几处关键变化
        print(f"   MOA 最新日期: {moa_date}")
        print(f"   科学养鱼日期: {keyu_date or '未提供'}")
        print(f"   a渔业行情报价日期: {afish_date or '未提供'}")
        print(f"   a渔业行情文章日期: {afish_article_date or '未提供'}")
        print(f"   塘口价快照日期: {塘口_dates or '未提供'}")
        return

    path.write_text(text, encoding="utf-8")
    print(f"✅ 已注入价源日期：MOA={moa_date}, 科学养鱼={keyu_date}, a渔业行情={afish_date}")
    print(f"   文件：{html_path}")


def main() -> int:
    args = parse_args()

    try:
        moa_date = args.moa_date or read_moa_latest_date(args.history_csv)
        塘口_dates = [d.strip() for d in args.塘口_dates.split(",") if d.strip()] if args.塘口_dates else None
        update_html(
            html_path=args.html,
            moa_date=moa_date,
            keyu_date=args.keyu_date,
            afish_date=args.afish_date,
            afish_article_date=args.afish_article_date,
            塘口_dates=塘口_dates,
            history_csv=args.history_csv,
            dry_run=args.dry_run,
        )
    except Exception as e:
        print(f"❌ 错误：{e}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
