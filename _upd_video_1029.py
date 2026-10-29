#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""#119 向 video_channel_snapshots_20261028.json 追加于老师 2026-10-29 快照。"""
import json

F = "video_channel_snapshots_20261028.json"
d = json.load(open(F, encoding="utf-8"))

new = {
  "source_account": "水产养殖服务于老师",
  "platform": "微信视频号",
  "price_date": "2026-10-29",
  "title": "2026.10.29全国鱼价 涨跌一目了然",
  "note": "全国塘口价，行情仅做参考，具体以塘口现场议价为准",
  "comment": "13 个品种 10 平 2 跌 1 涨：生鱼（3.5斤上）11.0-13.0 小幅上涨，鲤鱼（2-3斤）3.3-4.5 持续低迷、白鲢（2斤上）2.1-2.7 持续低迷；鳜鱼（1斤上）21-24、加州鲈（1斤上）10.0-11.0 基本持平。较 10-27：生鱼 9.0-12.8 → 11.0-13.0（下限上移 2 元、整体回升）、鳜鱼 23-26 → 21-24（中值下移约 2 元）、加州鲈 10.2-11.3 → 10.0-11.0（微落基本持平）、花鲢 4.8-5.7 → 4.6-5.5（微落）、草鱼 5.2-6.8 → 5.4-7.0（基本持平）。",
  "rows": [
    {"species":"生鱼","spec":"3.5斤上","price":"11.0-13.0","vs":"↑ 小幅上涨"},
    {"species":"加州鲈","spec":"1斤上","price":"10.0-11.0","vs":"→ 基本持平"},
    {"species":"鳜鱼（桂花鱼）","spec":"1斤上","price":"21-24","vs":"→ 基本持平"},
    {"species":"鮰鱼","spec":"1.5斤上","price":"7.8-8.5","vs":"→ 基本持平"},
    {"species":"黄颡鱼","spec":"3两上","price":"8.5-12","vs":"→ 基本持平"},
    {"species":"青鱼","spec":"6-10斤","price":"7.4-8.8","vs":"→ 基本持平"},
    {"species":"花鲢","spec":"3斤上","price":"4.6-5.5","vs":"→ 基本持平"},
    {"species":"罗非鱼","spec":"1斤上","price":"4.3-5.2","vs":"→ 基本持平"},
    {"species":"草鱼","spec":"3-5斤","price":"5.4-7.0","vs":"→ 基本持平"},
    {"species":"鲫鱼","spec":"6-8两","price":"5.0-7.8","vs":"→ 基本持平"},
    {"species":"鳊鱼","spec":"1.2斤上","price":"4.6-6.0","vs":"→ 基本持平"},
    {"species":"鲤鱼","spec":"2-3斤","price":"3.3-4.5","vs":"↓ 持续低迷"},
    {"species":"白鲢","spec":"2斤上","price":"2.1-2.7","vs":"↓ 持续低迷"},
  ],
}

# 防止重复追加
for it in d["snapshots"]:
    if it.get("source_account")==new["source_account"] and it.get("price_date")==new["price_date"]:
        print("[SKIP] 已存在 于老师 10-29")
        raise SystemExit(0)

d["snapshots"].append(new)
json.dump(d, open(F,"w",encoding="utf-8"), ensure_ascii=False, indent=2)
print("[OK] 已追加 于老师 10-29，snapshots 现共 {} 条".format(len(d["snapshots"])))
