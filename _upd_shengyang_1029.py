# -*- coding: utf-8 -*-
"""#129 盛阳食品城 10-29 卡整块替换（10-28 -> 10-29，依据 640.png 截图核验）。"""
import io

P = "鳜鱼鲈鱼价格看板.html"
s = io.open(P, encoding="utf-8").read()

old_legend_tail = "红鱼、鲳鱼、鲻鱼、海银鱼、斑节虾、黑虎虾等列名未报价</div>"

h3_pos = s.index("🛒 2026.10.28 · 无锡盛阳食品城水产批发价")
card_open = s.rfind('<div class="card"', 0, h3_pos)
leg_end = s.index(old_legend_tail) + len(old_legend_tail)
card_close = s.index('</div>', leg_end) + len('</div>')

new_block = '''        <div class="card" style="margin-top:14px">
      <h3>🛒 2026.10.29 · 无锡盛阳食品城水产批发价（元/斤）</h3>
      <div class="csub">本地渠道当日均价，离看板项目最近的一手批发参考。<b>鳜鱼（桂鱼）25~30 元/斤、鲈鱼 10~14 元/斤</b>，较 10.28 <b style="color:#6b7280">均持平</b>（鳜鱼与塘口标鳜全线持稳互证，鲈鱼连续多期 10~14 横盘）。普水鱼小幅波动：<b style="color:#dc2626">鳊鱼 7.5~8.5 → 8.5~9（上限 +0.5）</b>；白鲢 3.5~4、草鱼 7.5~9、花鲢 7.5~8.5、鲫鱼 8~13、青鱼 8.5~10、非洲鲫鱼 8.5~9、鲤鱼 5~6 基本持平。<b style="color:#dc2626">河虾高位档继续上探：100头 125→128（+3）、180头 58→60（+2）</b>；<b style="color:#12a150">150头 85→84（-1）小幅回落</b>，130头 103、160头 72 持平——大规格缺货、小规格走量，价格梯度延续拉大。白虾 42/35/30（低位 +1）、罗氏虾 40/36/25（大规格 -2、中规格 +1）、基围虾 20/19/16（大规格 -1）。蟹类公蟹持平；<b style="color:#dc2626">母蟹 3.5~3.9两 55~75 → 60~75（下限 +5）</b>、母蟹 1.5两 28~33 → 28~32（上限 -1）。<b style="color:#dc2626">牛蛙 11.4~12 → 11.7~12.2（微涨）、黄鳝 35~54 → 35~56（上限 +2）</b>；螺蛳 3~6、鲶鱼 6、昂刺鱼 10~15、黑鱼 8~13、清江鱼 12.5、银鱼 27~31、河鳗 24~35、甲鱼 20~58、泥鳅 10~12 持平。</div>
      <div class="grid2"><div><table><thead><tr><th>编号</th><th>品名</th><th>价格（元/斤）</th></tr></thead><tbody><tr><td>1</td><td>白鱼</td><td class="price">10~16</td></tr><tr><td>2</td><td><b>鳜鱼（桂鱼）</b></td><td class="price"><b>25~30</b></td></tr><tr><td>3</td><td><b>鲈鱼</b></td><td class="price"><b>10~14</b></td></tr><tr><td>4</td><td>鲤鱼</td><td class="price">5~6</td></tr><tr><td>5</td><td>非洲鲫鱼</td><td class="price">8.5~9</td></tr><tr><td>6</td><td>红鱼</td><td class="price">—</td></tr><tr><td>7</td><td>鳡鱼</td><td class="price">—</td></tr></tbody></table></div><div><table><thead><tr><th>编号</th><th>品名</th><th>价格（元/斤）</th></tr></thead><tbody><tr><td>1</td><td>鲫鱼</td><td class="price">8~13</td></tr><tr><td>2</td><td>白鲢</td><td class="price">3.5~4</td></tr><tr><td>3</td><td>草鱼</td><td class="price">7.5~9</td></tr><tr><td>4</td><td>花鲢</td><td class="price">7.5~8.5</td></tr><tr><td>5</td><td>鳊鱼</td><td class="price">8.5~9</td></tr><tr><td>6</td><td>青鱼</td><td class="price">8.5~10</td></tr><tr><td>7</td><td>鲳鱼</td><td class="price">—</td></tr></tbody></table></div></div>
      <div class="legend">来源：微信公众号「无锡盛阳食品城有限公司」2026.10.29《盛阳食品城水产类批发价（当日均价、仅供参考）》（截图核校录入）· 同文杂货/虾蟹类：牛蛙(养殖) 11.7~12.2、泥鳅(养殖) 10~12、黑鱼 8~13、清江鱼 12.5、黄鳝(养殖) 35~56、甲鱼(养殖) 20~58、银鱼 27~31、河鳗(养殖) 24~35、螺蛳(养殖) 3~6、鲶鱼 6、昂刺鱼 10~15；河虾 100头 128 / 130头 103 / 150头 84 / 160头 72 / 180头 60；基围虾大中小 20/19/16、白虾大中小 42/35/30、罗氏虾大中小 40/36/25；公蟹 2两 20~25 至 5两 62~80、母蟹 1.5两 28~32 至 3.5~3.9两 60~75 · 红鱼、鲳鱼、鳙鱼、海银鱼、斑节虾、黑虎虾、梭子蟹等列名未报价</div>
    </div>'''

s = s[:card_open] + new_block + s[card_close:]
io.open(P, "w", encoding="utf-8").write(s)
print("OK 盛阳 10-29 卡替换完成")
