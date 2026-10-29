import io

path = "鳜鱼鲈鱼价格看板.html"
html = open(path, encoding="utf-8").read()

start_marker = '<div class="card" style="margin-top:14px">\n      <h3>🐟 渔飞鱼 ·《全国水产品行情早报 2026-10-29》'
end_marker = '\n    </div>\n\n    <div class="card" style="margin-top:14px">\n      <h3>📊 水产市场风向标'

s = html.find(start_marker)
e = html.find(end_marker)
assert s != -1, "start_marker not found"
assert e != -1, "end_marker not found"

new_card = '''<div class="card" style="margin-top:14px">
      <h3>🐟 渔飞鱼 ·《全国水产品行情早报 2026-10-30》（特水领涨、河蟹止跌、普水低位持稳 · 黄鳝 +10.04% / 河蟹兴化 38.87 止跌 / 加拿大鲈川渝 18-19 vs 广东 9.2-9.5）</h3>
      <div class="csub">21 品种「特水领涨、河蟹止跌、普水低位持稳」：<b style="color:#dc2626">▲ 黄鳝全国批发 31.5 元/斤（周涨 10.04%）</b>、<b style="color:#dc2626">▲ 兴化河蟹 38.87 元/斤（止跌、结束 12 日连跌，4 两+ 公蟹 42~46）</b>；<b style="color:#12a150">▼ 白鲢批发 4.95（跌 3.7%）、▼ 花鲢白沙洲 4.75（较前回落）</b>；草鱼 5.5 / 鲫鱼 6.0 / 鲤鱼 5.5 低位持稳。<b style="color:#dc2626">加拿大鲈福建武平 18、重庆 19 vs 广东佛山 9.2~9.5（川渝闽比粤高 8~10 元，跨区调货利润厚）</b>。鳜鱼本轮未在日报表内单列（持续探底，与强渔周报 / 鳜康泰报价互证）。</div>
      <table><thead><tr><th>品种</th><th>地区</th><th>规格</th><th>塘口价(元/斤)</th><th>周环比</th></tr></thead><tbody>
        <tr><td><span class="tag tag-lu">加州鲈</span></td><td>福建武平</td><td><span class="spec spec-s">统货供货</span></td><td class="price"><b>18.0</b></td><td style="color:#dc2626;font-size:12px">▲ 川渝闽高价（10/29）</td></tr>
        <tr><td><span class="tag tag">黄颡鱼</span></td><td>浙江湖州</td><td><span class="spec spec-s">0.05公斤起</span></td><td class="price">16.0</td><td style="color:#6b7280;font-size:12px">→ 货源紧俏（10/28）</td></tr>
        <tr><td><span class="tag tag">鮰鱼</span></td><td>广东佛山顺德</td><td><span class="spec spec-s">统货</span></td><td class="price">10.5</td><td style="color:#6b7280;font-size:12px">→ 平稳（10/28）</td></tr>
        <tr><td><span class="tag tag">生鱼</span></td><td>广东佛山</td><td><span class="spec spec-l">大规格3.5斤上</span></td><td class="price">10.7</td><td style="color:#6b7280;font-size:12px">→ 平稳（10/28）</td></tr>
        <tr><td><span class="tag tag" style="background:#dc2626;color:#fff">▲黄鳝</span></td><td>全国批发</td><td><span class="spec spec-m">条重≥100</span></td><td class="price"><b>31.5</b></td><td style="color:#dc2626;font-size:12px">▲ 周涨10.04%</td></tr>
        <tr><td><span class="tag tag">泥鳅</span></td><td>山东鱼台</td><td><span class="spec spec-s">10-15cm成鳅</span></td><td class="price">46.0</td><td style="color:#6b7280;font-size:12px">→ 货紧（10/29）</td></tr>
        <tr><td><span class="tag tag">金鲳鱼</span></td><td>广西钦州</td><td><span class="spec spec-s">现货供货</span></td><td class="price">12.0</td><td style="color:#6b7280;font-size:12px">→ 平稳（10/28）</td></tr>
        <tr><td><span class="tag tag">大黄鱼</span></td><td>全国批发</td><td><span class="spec spec-m">批发均价</span></td><td class="price">19.05</td><td style="color:#12a150;font-size:12px">▼ 微落0.1%（10/29）</td></tr>
        <tr><td><span class="tag tag">草鱼</span></td><td>重庆</td><td><span class="spec spec-s">统货</span></td><td class="price">5.5</td><td style="color:#6b7280;font-size:12px">→ 低位（10/29）</td></tr>
        <tr><td><span class="tag tag">鲫鱼</span></td><td>重庆</td><td><span class="spec spec-s">黄金鲫</span></td><td class="price">6.0</td><td style="color:#6b7280;font-size:12px">→ 低位（10/29）</td></tr>
        <tr><td><span class="tag tag">鲤鱼</span></td><td>重庆</td><td><span class="spec spec-s">统货</span></td><td class="price">5.5</td><td style="color:#6b7280;font-size:12px">→ 低位（10/29）</td></tr>
        <tr><td><span class="tag tag" style="background:#12a150;color:#fff">▼花鲢</span></td><td>武汉白沙洲</td><td><span class="spec spec-m">条重≥1000</span></td><td class="price">4.75</td><td style="color:#12a150;font-size:12px">▼ 较前回落（10/29）</td></tr>
        <tr><td><span class="tag tag" style="background:#12a150;color:#fff">▼白鲢</span></td><td>全国批发</td><td><span class="spec spec-m">均价</span></td><td class="price">4.95</td><td style="color:#12a150;font-size:12px">▼ -3.7%（10/28）</td></tr>
        <tr><td><span class="tag tag">南美白对虾</span></td><td>山东滨州</td><td><span class="spec spec-s">通货</span></td><td class="price">22.3</td><td style="color:#6b7280;font-size:12px">→ 平稳（10/28）</td></tr>
        <tr><td><span class="tag tag">青虾</span></td><td>—</td><td><span class="spec spec-s">—</span></td><td class="price">—</td><td style="color:#6b7280;font-size:12px">当日暂无采集</td></tr>
        <tr><td><span class="tag tag">罗氏沼虾</span></td><td>江苏连云港</td><td><span class="spec spec-s">通货</span></td><td class="price">20.0</td><td style="color:#6b7280;font-size:12px">→ 平稳（10/28）</td></tr>
        <tr><td><span class="tag tag">金刚虾</span></td><td>—</td><td><span class="spec spec-s">—</span></td><td class="price">—</td><td style="color:#6b7280;font-size:12px">当日暂无采集</td></tr>
        <tr><td><span class="tag tag">小龙虾</span></td><td>湖北洪湖</td><td><span class="spec spec-s">统货</span></td><td class="price">15.0</td><td style="color:#6b7280;font-size:12px">→ 平稳（10/29）</td></tr>
        <tr><td><span class="tag tag" style="background:#dc2626;color:#fff">▲河蟹</span></td><td>江苏兴化</td><td><span class="spec spec-m">产地均价</span></td><td class="price"><b>38.87</b></td><td style="color:#dc2626;font-size:12px">▲ 止跌、结束12日连跌</td></tr>
        <tr><td><span class="tag tag">梭子蟹</span></td><td>广东湛江</td><td><span class="spec spec-s">鲜活海捕</span></td><td class="price">11.0</td><td style="color:#6b7280;font-size:12px">→ 平稳（10/28）</td></tr>
        <tr><td><span class="tag tag">海参</span></td><td>山东威海</td><td><span class="spec spec-s">批发市场统货</span></td><td class="price">45.0</td><td style="color:#6b7280;font-size:12px">—（10/28）</td></tr>
      </tbody></table>
      <div class="legend">来源：微信公众号「渔飞鱼水产·全国渔业价格」2026-10-30《全国水产品行情早报（2026年10月30日）》· <a class="plink" href="https://mp.weixin.qq.com/s/91jxdCiubkKjPOPSoac9Bg" target="_blank" rel="noopener">📄 阅读原文（渔飞鱼早报 10-30）</a> · 塘口/产地参考价，因规格、地区、品质不同存在差异</div>
    </div>'''

new_html = html[:s] + new_card + html[e:]
open(path, "w", encoding="utf-8").write(new_html)
print("replaced bytes:", len(html)-len(new_html)+len(new_card))
# quick tag balance sanity
for tag in ["<table", "</table>", "<tbody", "</tbody>", "<tr", "</tr>", "<div", "</div>"]:
    print(tag, new_html.count(tag))
