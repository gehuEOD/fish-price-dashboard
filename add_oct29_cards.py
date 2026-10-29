# -*- coding: utf-8 -*-
"""Insert 4 new source cards (Oct-28/29 batch) into the dashboard, at safe anchors.
Cards: 鳜康泰全国鳜鱼报价10-28 / 强渔周报10-28 / 渔飞鱼预报10-29 / 渔飞鱼日报10-29
强渔 is inserted BEFORE <!-- VIDEOCHANNEL_LIVE_START --> to avoid being wiped by inject_videochannel_block.py.
"""
import re, sys

P = "鳜鱼鲈鱼价格看板.html"
s = open(P, encoding="utf-8").read()

def check(anchor, name):
    n = s.count(anchor)
    if n != 1:
        print(f"[ABORT] anchor for {name} found {n} times (need 1)")
        sys.exit(1)
    print(f"[ok] anchor {name}: 1 match")

# ---- Card [6] 鳜康泰特约·全国鳜鱼报价 10-28 ----
C_GUIKANGTAI = '''
    <div class="card" style="margin-top:14px">
      <h3>🐟 鳜康泰特约 · 全国鳜鱼报价（2026-10-28 · 元/斤 · 8 产区 · 日/周涨跌）</h3>
      <div class="csub">产区塘口/批发参考价，与 <b>渔有福 10-28</b>（标鳜 24-26、广东中鳜 24.5→24 再跌 0.5）方向一致：广东标鳜 24.5 周涨 1（较 10-22 的 23.5）、中鳜 24 周跌 0.5；江苏/江西标鳜 26 领涨全国，安徽/湖南 25；全国标鳜 24.5~26 区间，探底未止、局部阴跌。</div>
      <table><thead><tr><th>地区</th><th>规格</th><th>10-27</th><th>10-28</th><th>10-22</th><th>日涨跌</th><th>周涨跌</th></tr></thead><tbody>
        <tr><td rowspan="3"><span class="tag tag-gui">广东</span></td><td><span class="spec spec-s">小鳜（0.8斤以下）</span></td><td class="price">18.5</td><td class="price">18.5</td><td class="price">18.5</td><td style="color:#6b7280;font-size:12px">—</td><td style="color:#6b7280;font-size:12px">—</td></tr>
        <tr><td><span class="spec spec-s">标鳜（0.8-1.5斤）</span></td><td class="price">24.5</td><td class="price"><b>24.5</b></td><td class="price">23.5</td><td style="color:#6b7280;font-size:12px">—</td><td style="color:#dc2626;font-size:12px">↑1</td></tr>
        <tr><td><span class="spec spec-m">中鳜（1.5斤以上）</span></td><td class="price">24</td><td class="price"><b>24</b></td><td class="price">24.5</td><td style="color:#6b7280;font-size:12px">—</td><td style="color:#12a150;font-size:12px">↓0.5</td></tr>
        <tr><td><span class="tag tag-gui">湖北</span></td><td><span class="spec spec-s">标鳜</span></td><td class="price">24.5</td><td class="price"><b>24.5</b></td><td class="price">24</td><td style="color:#6b7280;font-size:12px">—</td><td style="color:#dc2626;font-size:12px">↑0.5</td></tr>
        <tr><td><span class="tag tag-gui">安徽</span></td><td><span class="spec spec-s">标鳜</span></td><td class="price">25</td><td class="price"><b>25</b></td><td class="price">25</td><td style="color:#6b7280;font-size:12px">—</td><td style="color:#6b7280;font-size:12px">—</td></tr>
        <tr><td><span class="tag tag-gui">江西</span></td><td><span class="spec spec-s">标鳜</span></td><td class="price">26</td><td class="price"><b>26</b></td><td class="price">26</td><td style="color:#6b7280;font-size:12px">—</td><td style="color:#6b7280;font-size:12px">—</td></tr>
        <tr><td><span class="tag tag-gui">湖南</span></td><td><span class="spec spec-s">标鳜</span></td><td class="price">25</td><td class="price"><b>25</b></td><td class="price">25</td><td style="color:#6b7280;font-size:12px">—</td><td style="color:#6b7280;font-size:12px">—</td></tr>
        <tr><td><span class="tag tag-gui">江苏</span></td><td><span class="spec spec-s">标鳜</span></td><td class="price">26</td><td class="price"><b>26</b></td><td class="price">26</td><td style="color:#6b7280;font-size:12px">—</td><td style="color:#6b7280;font-size:12px">—</td></tr>
      </tbody></table>
      <div class="legend">来源：微信公众号「鳜康泰特约·全国鳜鱼报价」2026-10-28《10月28日鳜鱼价格行情丨鳜康泰特约·全国鳜鱼报价》· <a class="plink" href="https://mp.weixin.qq.com/s/VMslhPHLXELqu4o7xq-CRQ" target="_blank" rel="noopener">📄 阅读原文（鳜鱼全国报价 10-28）</a> · 元/斤 · 产区塘口/批发参考价，因规格、地区、品质不同存在差异</div>
    </div>'''

# ---- Card [5] 强渔周报 10-28 (published 10-28 19:08) ----
C_QIANGYU = '''
    <div class="card" style="margin-top:14px">
      <h3>📰 水产养殖网（强渔）·《一周行情大变脸：黑鱼掉价 1.5 元，鲈鱼冲上 12 元》（2026-10-28 · 10月最后一周）</h3>
      <div class="csub">行情换位：此前连涨四周的黑鱼本周回吐，温吞的加州鲈反超硬涨、逼近 12 元；鳜鱼继续探底（佛山中鳜落 22-23 元）；黄颡跟涨。核心逻辑：深秋集中出塘 + 终端消费疲软，谁能撑价全看缺不缺大鱼。</div>
      <ul style="margin:8px 0 0;padding-left:20px;line-height:1.9">
        <li><b>黑鱼：</b>5.5-7 斤头老鱼两周涨 4 元、最高冲 13.3 元/斤，3.5 斤头新鱼冲到 10.7 元；本周新老鱼全线回落 1-1.5 元。但中鱼及加工厂收购价仍涨 0.2-0.4 元——跌的是冲太高的部分，存塘大降基本面未变，属涨多修正而非崩盘。</li>
        <li><b style="color:#dc2626">加州鲈：</b>广东老鱼存塘见底、秋鱼偏小，1 斤以上大鱼稀缺；佛山 1 斤上塘口价两周从 9.5-10 涨到 10.5-11、本周再涨 1.5 元逼近 12 元。网上流传"涨到 13 元"流通商不认，塘口真实成交 12 元一带。</li>
        <li><b style="color:#12a150">鳜鱼：</b>新鱼集中上市 + 外省同步放量 + 终端疲软，供过于求未扭转；佛山中鳜塘口落 22-23 元，各地标鳜普遍跌 1-2 元，继续探底。病鱼减少说明问题在需求与供应，不在鱼体。</li>
        <li><b>黄颡鱼：</b>广东出鱼减少、大规格缺货，单周涨 1.5 元。</li>
      </ul>
      <div class="legend">来源：水产养殖网（强渔） 2026-10-28《一周行情大变脸：黑鱼掉价 1.5 元，鲈鱼冲上 12 元，塘口别再死扛等价》· <a class="plink" href="https://mp.weixin.qq.com/s/m1HJHr87C4p3t34Pt32icA" target="_blank" rel="noopener">📄 阅读原文</a> · 价格受规格、卖相等因素影响较大，仅供参考</div>
    </div>'''

# ---- Card [3] 渔飞鱼 预报 10-29 ----
C_YUFYYB = '''
    <div class="card" style="margin-top:14px">
      <h3>🐟 渔飞鱼 ·《明日水产行情预报 2026-10-29》（周四周末备货前 · 河蟹母蟹暴跌 20%、公蟹逆势涨）</h3>
      <div class="csub">覆盖 28 品种。明日节点：周四（周末备货前一天）。<b style="color:#12a150">河蟹母蟹领跌</b>：5.0 母 135→115、4.0 母 100→78（跌 20%+），兴化/宿豫普货母蟹普遍跌 2-8 元；<b style="color:#dc2626">中小公蟹逆势大涨</b>。加州鲈批发均价 14.22 元/斤平稳。其余品种多数持稳。鳜鱼 / 普通鲈鱼未在预报表单列（与日报口径一致：鳜鱼持续探底、鲈鱼低位）。</div>
      <div class="grid2"><div><h3 style="font-size:14px;margin:6px 0 8px"><span class="tag tag-lu">加州鲈 / 海鲈</span> 明日预测（元/斤）</h3><table><thead><tr><th>品种</th><th>基准价</th><th>明日预测</th><th>方向</th></tr></thead><tbody>
        <tr><td>加州鲈鱼</td><td class="price">14.22</td><td class="price">14.2-14.3</td><td style="color:#6b7280;font-size:12px">→ 平稳</td></tr>
        <tr><td>海鲈鱼</td><td class="price">17.0-23.0</td><td class="price">17.0-23.0</td><td style="color:#6b7280;font-size:12px">→ 平稳</td></tr>
      </tbody></table></div><div><h3 style="font-size:14px;margin:6px 0 8px"><span class="tag tag">河蟹（大闸蟹）</span> 明日预测（元/斤）</h3><table><thead><tr><th>规格</th><th>基准价</th><th>明日预测</th><th>方向</th></tr></thead><tbody>
        <tr><td>5.0 母统货</td><td class="price">115</td><td class="price">113-117</td><td style="color:#12a150;font-size:12px">↓ 继续跌</td></tr>
        <tr><td>4.0 母统货</td><td class="price">78</td><td class="price">76-80</td><td style="color:#12a150;font-size:12px">↓ 继续跌</td></tr>
        <tr><td>中小公蟹统货</td><td class="price">上涨中</td><td class="price">继续走强</td><td style="color:#dc2626;font-size:12px">↑ 逆势涨</td></tr>
      </tbody></table></div></div>
      <div class="legend">来源：微信公众号「渔飞鱼水产」2026-10-29 05:00《明日水产行情预报 | 2026年10月29日》· <a class="plink" href="https://mp.weixin.qq.com/s/OszgKA6ff9pfAzCk7ODKxw" target="_blank" rel="noopener">📄 阅读原文（渔飞鱼预报 10-29）</a> · 基准 10-27/28 塘口/产地/批发参考价，预测不构成交易决策依据</div>
    </div>'''

# ---- Card [7] 渔飞鱼 日报 10-29 ----
C_YUFYRB = '''
    <div class="card" style="margin-top:14px">
      <h3>🐟 渔飞鱼 ·《全国水产品行情早报 2026-10-29》（特水走强、普水回调 · 加州鲈江门 14 元 / 黄鳝 +11.83% / 河蟹泰州 38.29 周跌 4.3%）</h3>
      <div class="csub">21 品种"特水走强、普水回调"：<b style="color:#dc2626">▲ 加州鲈江门统货供货 14.0 元/斤</b>（较佛山周涨 1 元、大规格爽市）；▲ 黄鳝全国批发 32.5（+11.83%）、▲ 生鱼大规格 10.7；<b style="color:#12a150">▼ 河蟹泰州 38.29（周跌 4.3%、优质蟹库存仅 18%）</b>、▼ 白鲢 -3.7%。鳜鱼本轮未在日报表内单列（持续探底，与强渔周报 / 鳜康泰报价互证）。</div>
      <table><thead><tr><th>品种</th><th>地区</th><th>规格</th><th>塘口价(元/斤)</th><th>周环比</th></tr></thead><tbody>
        <tr><td><span class="tag tag-lu">加州鲈</span></td><td>广东江门</td><td><span class="spec spec-s">统货供货</span></td><td class="price"><b>14.0</b></td><td style="color:#dc2626;font-size:12px">▲ 较佛山周涨1元</td></tr>
        <tr><td><span class="tag tag">黄颡鱼</span></td><td>广东佛山</td><td><span class="spec spec-s">平6两</span></td><td class="price">11.0</td><td style="color:#6b7280;font-size:12px">→ 缺鱼偏强</td></tr>
        <tr><td><span class="tag tag">生鱼</span></td><td>广东佛山</td><td><span class="spec spec-l">大规格3.5斤上</span></td><td class="price">10.46<span style="font-size:11px;color:#6b7280">（大规格10.7）</span></td><td style="color:#dc2626;font-size:12px">▲ 大规格周涨0.7</td></tr>
        <tr><td><span class="tag tag">黄鳝</span></td><td>全国批发</td><td><span class="spec spec-m">条重≥100</span></td><td class="price">32.5</td><td style="color:#dc2626;font-size:12px">▲ 周涨11.83%</td></tr>
        <tr><td><span class="tag tag">河蟹</span></td><td>江苏泰州/兴化</td><td><span class="spec spec-m">产地均价</span></td><td class="price">38.29</td><td style="color:#12a150;font-size:12px">▼ 周跌4.3%、优质蟹库存仅18%</td></tr>
        <tr><td><span class="tag tag">白鲢</span></td><td>全国批发</td><td><span class="spec spec-m">均价</span></td><td class="price">4.95</td><td style="color:#12a150;font-size:12px">▼ -3.7%</td></tr>
        <tr><td><span class="tag tag">鲫鱼</span></td><td>全国批发</td><td><span class="spec spec-m">均价</span></td><td class="price">9.67</td><td style="color:#12a150;font-size:12px">▼ -1.1%</td></tr>
        <tr><td><span class="tag tag">鲤鱼</span></td><td>全国批发</td><td><span class="spec spec-m">均价</span></td><td class="price">6.83</td><td style="color:#12a150;font-size:12px">▼ -1.5%</td></tr>
      </tbody></table>
      <div class="legend">来源：微信公众号「渔飞鱼水产」2026-10-29《渔飞鱼水产行情日报（2026年10月29日）》· <a class="plink" href="https://mp.weixin.qq.com/s/a_NHxrqMOvcTxDMVwJR0jA" target="_blank" rel="noopener">📄 阅读原文（渔飞鱼日报 10-29）</a> · 塘口/产地参考价，因规格、地区、品质不同存在差异</div>
    </div>'''

# ---- anchors ----
A_GUI = '📄 阅读原文（鳜鱼塘口 10-28）</a> · 元/斤 · 塘口报价随行就市</div>'
A_YFB = '📄 阅读原文（渔飞鱼预报 10-28）</a> · 基准 10-26/27 塘口/产地/批发参考价，预测不构成交易决策依据</div>'
A_VC  = '  <!-- VIDEOCHANNEL_LIVE_START -->'

check(A_GUI, "鳜康泰-after")
check(A_YFB, "渔飞鱼预报10-29-after")
check(A_VC,  "强渔-before-VIDEOCHANNEL")

# Insert: 鳜康泰 after 渔有福10-28 legend
s = s.replace(A_GUI, A_GUI + C_GUIKANGTAI, 1)
# Insert 渔飞鱼 预报10-29 + 日报10-29 after 渔飞鱼预报10-28 legend
s = s.replace(A_YFB, A_YFB + C_YUFYYB + C_YUFYRB, 1)
# Insert 强渔 card before VIDEOCHANNEL_LIVE_START (outside auto-block)
s = s.replace(A_VC, C_QIANGYU + "\n" + A_VC, 1)

open(P, "w", encoding="utf-8").write(s)
print("[done] wrote", P, "size=", len(s))
