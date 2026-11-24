#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""11-24 午批：新增渔有福水产 11-24 鳜鱼塘口卡（小鳜 19.5→20 原文上调 0.5）。
科学养鱼 11-23 正文图（o1taa…）与用户截图均已在 11-23 晚间批录入，跳过。
"""
from pathlib import Path
import sys

from _upd_1123_late import balance

P = Path("鳜鱼鲈鱼价格看板.html")
s = P.read_text(encoding="utf-8")

LINK = "https://mp.weixin.qq.com/s/mnxTNhSIkRRf99-jR2PQlA"
GUARD = "🐟 11月24日 · 渔有福水产 鳜鱼塘口报价"
ANCHOR = (
    '<div class="card" style="margin-top:14px">\n'
    '  <h3>🐟 11月23日 · 渔有福水产 鳜鱼塘口报价'
)
CARD = '''<div class="card" style="margin-top:14px">
  <h3>🐟 11月24日 · 渔有福水产 鳜鱼塘口报价（小鳜上调 0.5 · 8 项 · 元/斤）</h3>
  <div class="csub">「渔有福水产」2026-11-24 09:25 发布 11 月 24 日全国主产区鳜鱼塘口价（河南）。广东产区规格价：<b>小鳜（0.8 斤以下）20、标鳜（0.8~1.5 斤）22.5、中鳜（1.5~2 斤）19</b> 元/斤左右；分省标鳜：湖北 24.5、安徽 23.5、江西 25.5、湖南 24.5、江苏 24 元/斤左右。原文为塘口主流参考价，实际成交看品相、体质、存塘规格与鱼中议价。本期逐项变动说明见下方 callout，本卡按原文照录绝对值。</div>
  <table><thead><tr><th>产区</th><th>规格</th><th>塘口价（元/斤）</th></tr></thead><tbody>
  <tr><td>广东</td><td>小鳜（0.8 斤以下）</td><td class="price"><b>20</b></td></tr>
  <tr><td>广东</td><td>标鳜（0.8~1.5 斤）</td><td class="price"><b>22.5</b></td></tr>
  <tr><td>广东</td><td>中鳜（1.5~2 斤）</td><td class="price"><b>19</b></td></tr>
  <tr><td>湖北</td><td>标鳜</td><td class="price"><b>24.5</b></td></tr>
  <tr><td>安徽</td><td>标鳜</td><td class="price"><b>23.5</b></td></tr>
  <tr><td>江西</td><td>标鳜</td><td class="price"><b>25.5</b></td></tr>
  <tr><td>湖南</td><td>标鳜</td><td class="price"><b>24.5</b></td></tr>
  <tr><td><span class="tag tag-gui">江苏</span></td><td>标鳜</td><td class="price"><b>24</b></td></tr>
  </tbody></table>
  <div class="callout" style="margin-top:10px"><b>逐项变动 / 同值并列 / 口径说明：</b>① 本期原文明确「<b>小鳜价格上调 0.5 元 / 斤</b>」，本卡广东小鳜 <b>20</b>（该号上一期 11-23 为 19.5），<b>仅此一项按原文标注变动</b>；其余 7 项（标鳜 22.5 / 中鳜 19、鄂 24.5 / 皖 23.5 / 赣 25.5 / 湘 24.5 / 苏 24）与渔有福 11-23 期逐项同值，<b>原文未标「沿用」，如实并列、不重复计数、不推断逐项涨跌、不作两期比较</b>。② 与「鳜康泰特约 11-23」卡 8 项逐项同值（该卡小鳜亦为 20、原文标涨 0.5），但<b>发布号不同（渔有福水产 vs 兴渔派-鳜鱼通）、期次不同（11-24 vs 11-23）</b>，按既有先例（渔有福 11-23 vs 鳜康泰 11-22）<b>独立成卡、不合并双出处、不重复计数、不推断统一涨跌</b>。③ 原文「左右 / 约」口径保留，<b>不取中值冒充实测价</b>；广东规格价（小鳜 / 标鳜 / 中鳜）与分省标鳜为<b>不同规格口径，不可直接比较、不互减</b>。④ 本卡为<b>塘口参考价（元/斤）</b>，与通威 11-20 全国塘口均价 23.0、腾氏 11-23 同源播报、分市场批发（元/公斤）、白沙洲批发、盛阳本地批发、视频号全国参考区间、渔无忧次日预测<b>规格·时间·渠道三重不同，多口径并存、禁止互减</b>。⑤ 同篇降温季水霉 / 寄生虫 / 细菌性烂鳃 / 病毒风险提示与稳水管护要点属病害防控建议，<b>不作为价格数据录入</b>；本期<b>未给加州鲈报价，如实留空</b>。</div>
  <div class="legend">来源：微信公众号「渔有福水产」2026-11-24 09:25《11 月 24 日鳜鱼行情｜小鳜上涨 0.5 元 / 斤！各地塘口报价更新，降温季病害防控务必盯紧》· <a class="plink" href="''' + LINK + '''" target="_blank" rel="noopener">📄 阅读原文</a> · 元/斤 · 塘口参考价（实际成交随品相 / 体质 / 存塘规格 / 鱼中议价浮动，仅供参考）· 正文文字核校录入</div>
</div>
'''

CHIP_OLD = "渔有福水产（10-26~28塘口/11-05/11-06塘口/11-09同源报价/11-13塘口/11-16塘口/11-23塘口）"
CHIP_NEW = "渔有福水产（10-26~28塘口/11-05/11-06塘口/11-09同源报价/11-13塘口/11-16塘口/11-23塘口/11-24塘口）"


def main():
    if GUARD in s:
        print("[SKIP] 11-24 午批渔有福卡已插入")
        return
    if LINK in s:
        print("[FATAL] 链接已存在但卡片守卫缺失，需人工核查")
        sys.exit(1)

    checks = [("anchor", ANCHOR, 1), ("chip", CHIP_OLD, 1), ("guard", GUARD, 0)]
    for label, k, want in checks:
        n = s.count(k)
        print(f"  [{label}] count={n} (want {want})")
        if n != want:
            sys.exit(1)

    before = balance(s)
    out = s.replace(ANCHOR, CARD + ANCHOR, 1)
    out = out.replace(CHIP_OLD, CHIP_NEW, 1)
    after = balance(out)
    bad = [(t, before[t], after[t]) for t in before
           if before[t][0] != before[t][1] or after[t][0] != after[t][1]]
    if bad:
        print("[FATAL] 标签不配平:", bad)
        sys.exit(1)

    P.write_text(out, encoding="utf-8")
    print(f"[ok] 插卡完成：+{len(out.encode('utf-8')) - len(s.encode('utf-8'))} B")
    print(f"[ok] 守卫 count={out.count(GUARD)} | chip count={out.count(CHIP_NEW)} | 链接 count={out.count(LINK)}")
    print("[ok] 14 类标签前后均配平")


if __name__ == "__main__":
    main()
