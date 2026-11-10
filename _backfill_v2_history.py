#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""一次性回填 V2 更新日志历史（幂等）。

问题：dashboard_v2_version.json 的 history 自 v2.0.14 起一直是 []，
生成器 --bump 只改版本号、从不追加历史，导致 /v2/「更新日志」永远只有一条
写死的初创说明。

依据：git log -- dashboard_v2_version.json，取每个版本号**首次出现**的提交
（同一版本每日 daily 提交不重复记录），文案为该提交 subject 的人工精简，
不编造版本、不编造日期。

当前版本（2.0.20）不写入 history，留给随后 --bump patch 自动追加，以此同时
验证「bump 自动追加历史」的新逻辑。
"""
import json
import os
import subprocess
import sys

WS = os.path.dirname(os.path.abspath(__file__))
VERFILE = os.path.join(WS, "dashboard_v2_version.json")

# 与 git commit subject 一一对应的人工精简文案（保留事实，去掉过长价格明细）
NOTES = {
    "v2.0.14": "决策版看板上线：新增 /v2/ 独立链接、三角色行动清单规则引擎、每日 09:15 自动更新工作流",
    "2.0.15": "四源刷新至 10-28：渔有福鳜鱼塘口、全国渔业价格早报、渔飞鱼日报；新增渔有福为注册源，KPI 塘口价改 10-28 口径",
    "2.0.16": "三源刷新：小洁 10-26 / 于老师 10-27 塘口价、盛阳 10-28 批发价；视频号注入脚本重构为全数据驱动",
    "2.0.17": "两源刷新：科学养鱼全国批发价（与 MOA 互证）、强渔加州鲈专题；新增科学养鱼自动注入区块并注册新鲜度源",
    "2.0.18": "建立 v1→v2 自动同步桥接：从 v1 卡片抽取塘口价与行情线索，Pages 发布与每日 09:15 均接入，数据由 10-28 刷新至 11-09",
    "2.0.19": "11-10 批次 7 卡同步；桥接改为动态 notes / 涨跌判定，并纳入强渔周报、渔飞鱼预报两条新线索",
    "2.0.20": "修复加州鲈出塘价 KPI 空白：桥接改多源候选 + 江苏本地锚点，生成器支持价格区间与动态标签；加州鲈数据刷新至 11-09",
}


def milestones():
    """按时间正序返回 [(version, date, note)]，每个版本只取首次出现。"""
    out = subprocess.check_output(
        ["git", "log", "--format=%H|%ad|%s", "--date=short", "--reverse",
         "--", "dashboard_v2_version.json"],
        cwd=WS, text=True,
    )
    seen, rows = set(), []
    for line in out.splitlines():
        sha, cdate, subject = line.split("|", 2)
        blob = subprocess.run(
            ["git", "show", f"{sha}:dashboard_v2_version.json"],
            cwd=WS, capture_output=True, text=True,
        ).stdout
        try:
            v = json.loads(blob)
        except Exception:
            continue
        ver = v.get("version", "")
        if not ver or ver in seen:
            continue
        seen.add(ver)
        assert ver in NOTES, f"版本 {ver} 缺人工核校文案，禁止编造（提交 {sha[:7]}：{subject[:60]}）"
        rows.append((ver, v.get("date") or cdate, NOTES[ver]))
    return rows


def main():
    ver = json.load(open(VERFILE, encoding="utf-8"))
    hist = ver.get("history", [])
    if any(str(h.get("version", "")).lstrip("v") == "2.0.14" for h in hist):
        print("[SKIP] 更新日志历史已回填，退出以防重复")
        return 0

    rows = milestones()
    assert rows, "未从 git 历史解析出任何版本里程碑"
    cur = ver["version"]
    assert cur in NOTES, f"当前版本 {cur} 无核校文案"
    assert rows[-1][0] == cur, f"git 最新版本 {rows[-1][0]} 与版本文件 {cur} 不一致"

    ver["note"] = NOTES[cur]
    # 不含当前版本：由 build_dashboard_v2.py --bump 自动追加
    ver["history"] = [
        {"version": v, "date": d, "note": n}
        for v, d, n in rows[:-1][::-1]
    ]
    ver["prev"] = rows[-2][0] if len(rows) >= 2 else "v2.0.13"

    with open(VERFILE, "w", encoding="utf-8") as f:
        json.dump(ver, f, ensure_ascii=False, indent=2)

    print(f"[OK] 回填 {len(ver['history'])} 条历史（{ver['history'][-1]['version']} → "
          f"{ver['history'][0]['version']}），当前 {cur} 待 bump 追加")
    print(f"[OK] 当前版本说明：{ver['note']}")
    print(f"[OK] prev = {ver['prev']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
