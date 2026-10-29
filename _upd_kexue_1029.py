#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""#118 将 wechat_ocr_current.json 的「科学养鱼」段替换为 10-29，并另存历史快照。"""
import json, shutil, datetime

STATE = "wechat_ocr_current.json"
SNAP = "wechat_ocr_prices_20261029.json"

D = "2026-10-29"
rows = []

def gui(market, spec, price):
    return {"source":"科学养鱼","article_date":D,"price_date":D,
            "species":"鳜鱼（桂花鱼）","market":market,"spec":spec,
            "price":price,"unit":"元/千克","vs":"—","note":"","vs_header":"vs 上期"}

def lu(market, spec, price):
    return {"source":"科学养鱼","article_date":D,"price_date":D,
            "species":"加州鲈鱼","market":market,"spec":spec,
            "price":price,"unit":"元/千克","vs":"—","note":"","vs_header":"vs 上期"}

# 鳜鱼（桂花鱼）8 条
rows += [
 gui("江西南昌市水产品综合交易批发市场","500≤条重＜750",58.00),
 gui("湖北宜昌三峡物流园有限公司水产市场","250≤条重＜500",50.00),
 gui("湖北宜昌三峡物流园有限公司水产市场","500≤条重＜750",64.00),
 gui("安徽省合肥市周谷堆水产品批发市场","250≤条重＜500",70.00),
 gui("北京大红门京深海鲜批发市场有限公司","条重≥750",72.00),
 gui("上海江杨水产品批发市场经营管理有限公司","500≤条重＜750",100.00),
 gui("北京京丰岳各庄农副产品批发市场中心","500≤条重＜750",53.00),
 gui("长沙马王堆农产品股份有限公司海鲜水产批发市场","500≤条重＜750",57.00),
]
# 加拿大鲈 8 条
rows += [
 lu("江西省萍乡市城南水产批发市场","条重≥500",27.00),
 lu("江西南昌市水产品综合交易批发市场","条重≥500",24.00),
 lu("上海江杨水产品批发市场经营管理有限公司","条重≥500",30.00),
 lu("北京京丰岳各庄农副产品批发市场中心","条重≥500",31.00),
 lu("山西太原五龙口海鲜市场","条重≥500",24.00),
 lu("甘肃省兰州市绿色食品市场","条重＜500",26.00),
 lu("上海江阳水产品批发交易市场经营管理有限公司","条重≥500",23.00),
 lu("广州黄沙水产交易市场有限公司","条重≥500",26.00),
]

with open(STATE, encoding="utf-8") as f:
    data = json.load(f)
data["科学养鱼"] = rows

# 另存历史快照（仅科学养鱼段）
with open(SNAP, "w", encoding="utf-8") as f:
    json.dump({"科学养鱼": rows}, f, ensure_ascii=False, indent=2)

# 写回 current（保留 a渔业行情 等其余段）
with open(STATE, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("已写回 {} 条科学养鱼（10-29）；快照 {}".format(len(rows), SNAP))
