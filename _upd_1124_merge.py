#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""11-24 早批：腾氏 11-23「一周鱼价行情播报」与已入库通威 11-20 卡逐项同值，
按同源合并规则并入同一卡双出处留痕：不新增卡、不更新日期、不重复计数、
不作两期比较。2S68t…（11-24 早报）上一批已录，跳过。
"""
from pathlib import Path
import re
import sys

from _upd_1123_late import balance

P = Path("鳜鱼鲈鱼价格看板.html")
s = P.read_text(encoding="utf-8")

TENG_LINK = "https://mp.weixin.qq.com/s/t8JqPplj8Tg1Y3Jvozqowg"
GUARD = "同源合并（腾氏转载）"

OLD_CALLOUT_TAIL = (
    "与塘口价（鳜康泰 11-22 江苏标鳜 24、腾氏㊻ 24.5）、"
    "分市场批发（淡水渔业 11-20 元/公斤、科学养鱼 OCR）、白沙洲批发、"
    "盛阳 25~30、视频号全国参考区间、渔无忧次日预测"
    "<b>多口径并存、禁止互减</b>。</div>"
)
NEW_CALLOUT_TAIL = (
    "与塘口价（鳜康泰 11-22 江苏标鳜 24、腾氏㊻ 24.5）、"
    "分市场批发（淡水渔业 11-20 元/公斤、科学养鱼 OCR）、白沙洲批发、"
    "盛阳 25~30、视频号全国参考区间、渔无忧次日预测"
    "<b>多口径并存、禁止互减</b>。 "
    "④ <b>同源合并（腾氏转载）：</b>"
    "腾氏水产商务网 2026-11-23 19:34"
    "《“涨”声一片！鲫鱼、叉尾鮰、对虾、牛蛙、螃蟹集体上涨！"
    "最高暴涨2元/斤！｜一周鱼价行情播报》"
    "原文自述「数据来源：通威农发市场一线行情报价组」；"
    "其鳜鱼 23.0（上周 25.3 / 周跌 -2.3 / 同比 -4% / 环比 -9.2%）、"
    "加州鲈 9.5（上周 10.3 / 周跌 -0.9 / 同比 -9% / 环比 -8.3%）"
    "及分省 4 行、肇庆鳜鱼 23~24 与本卡<b>逐项同值</b>，"
    "判为<b>同一份报价的两个发布渠道</b>，合并一卡双出处留痕（链接见下方 legend），"
    "<b>保留原 h3、不更新日期、不重复计数、不作两期比较</b>。</div>"
)

OLD_LEGEND = (
    "来源：微信公众号「通威农牧」2026-11-20 19:15"
    "《草鱼跌至3.9元/斤，后市这些水产品行情或将继续走低!｜一周鱼价行情》"
    "· <a class=\"plink\" href=\"https://mp.weixin.qq.com/s/rCpArgbbahT2jsDLoDuNfw\" "
    "target=\"_blank\" rel=\"noopener\">📄 阅读原文</a> "
    "· 元/斤 · 全国塘口均价 · 正文文字 + 附图核校录入"
)
NEW_LEGEND = OLD_LEGEND + (
    " · <a class=\"plink\" href=\"" + TENG_LINK + "\" "
    "target=\"_blank\" rel=\"noopener\">📄 腾氏转载原文（11-23 同源）</a>"
)


def main():
    if GUARD in s:
        print("[SKIP] 11-24 同源合并已完成")
        return
    if TENG_LINK in s:
        print("[FATAL] 腾氏链接已存在但合并说明缺失，需人工核查")
        sys.exit(1)

    for label, old in [("callout tail", OLD_CALLOUT_TAIL), ("legend", OLD_LEGEND)]:
        n = s.count(old)
        print(f"  [{label}] count={n}")
        if n != 1:
            print("[FATAL] 替换串不唯一")
            sys.exit(1)

    before = balance(s)
    out = s.replace(OLD_CALLOUT_TAIL, NEW_CALLOUT_TAIL, 1)
    out = out.replace(OLD_LEGEND, NEW_LEGEND, 1)
    after = balance(out)

    bad = [(t, before[t], after[t]) for t in before if before[t][0] != before[t][1] or after[t][0] != after[t][1]]
    if bad:
        print("[FATAL] 标签不配平:", bad)
        sys.exit(1)

    P.write_text(out, encoding="utf-8")
    print(f"[ok] 同源合并完成：+{len(out.encode('utf-8')) - len(s.encode('utf-8'))} B")
    print(f"[ok] 腾氏链接 count={out.count(TENG_LINK)} | 合并说明 count={out.count(GUARD)}")
    print("[ok] 14 类标签前后均配平")


if __name__ == "__main__":
    main()
