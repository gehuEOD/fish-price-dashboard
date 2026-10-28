# -*- coding: utf-8 -*-
"""Rebuild the 通威农牧 card 鳜鱼/加州鲈 tables from the 2026-10-28 screenshots.
Rule: only 鳜鱼 + 加州鲈 are tracked (黄颡鱼/斑点叉尾鮰 excluded).
Faithful to screenshots: 上海江杨 has two rows (33.5 + 30); 南京众彩/北京岳各庄
dropped from 鳜鱼 (absent in 10-28); 加拿大鲈 南京众彩 12.25->12.75, 重庆涪陵 14->14.1.
"""
import io, sys

p = "鳜鱼鲈鱼价格看板.html"
with io.open(p, encoding="utf-8") as f:
    s = f.read()

def rep(old, new, s, label):
    if old not in s:
        print("!! MISS:", label); sys.exit(1)
    return s.replace(old, new, 1)

# 1) title date
s = rep('<h3>🐟 通威农牧 · 特水鱼类批发均价（2026-10-27 · 元/斤 · 分规格）</h3>',
        '<h3>🐟 通威农牧 · 特水鱼类批发均价（2026-10-28 · 元/斤 · 分规格）</h3>', s, "title")

# 2) csub count + 江阳->江杨 name fix
s = rep('鳜鱼 34 条 / 加州鲈 17 条', '鳜鱼 32 条 / 加州鲈 17 条', s, "csub count")
s = rep('上海江阳 33.5=67÷2', '上海江杨 33.5=67÷2', s, "csub 江杨")

# 3) 鳜鱼 LEFT tbody
old_gl = '''        <tr><td>乌鲁木齐北园春</td><td><span class="spec spec-s">1.0-1.5斤</span></td><td class="price"><b style="color:#dc2626">60</b></td></tr>
        <tr><td>上海江杨</td><td><span class="spec spec-s">1.0-1.5斤</span></td><td class="price"><b>50</b></td></tr>
        <tr><td>福建兴业华洲</td><td><span class="spec spec-s">1.0-1.5斤</span></td><td class="price">48</td></tr>
        <tr><td>云南华潮</td><td><span class="spec spec-s">≥1.5斤</span></td><td class="price"><b>47.5</b></td></tr>
        <tr><td>福州名成</td><td><span class="spec spec-s">≥1.5斤</span></td><td class="price">46.5</td></tr>
        <tr><td>湖北黄冈硕源</td><td><span class="spec spec-s">≥1.5斤</span></td><td class="price">43</td></tr>
        <tr><td>福建莆田闽中</td><td><span class="spec spec-s">5两-1.0斤</span></td><td class="price">39.5</td></tr>
        <tr><td>湖北黄冈硕源</td><td><span class="spec spec-s">1.0-1.5斤</span></td><td class="price">38.5</td></tr>
        <tr><td>江西萍乡城南</td><td><span class="spec spec-s">5两-1.0斤</span></td><td class="price">38</td></tr>
        <tr><td>甘肃兰州绿色食品</td><td><span class="spec spec-s">≥1.5斤</span></td><td class="price">37</td></tr>
        <tr><td>湖北仙桃江汉平原</td><td><span class="spec spec-s">1.0-1.5斤</span></td><td class="price">36.5</td></tr>
        <tr><td>北京大红门京深</td><td><span class="spec spec-s">≥1.5斤</span></td><td class="price">36</td></tr>
        <tr><td>湖北黄冈硕源</td><td><span class="spec spec-s">5两-1.0斤</span></td><td class="price">35.5</td></tr>
        <tr><td>山东临沂华东淡水鱼</td><td><span class="spec spec-s">≥1.5斤</span></td><td class="price">35</td></tr>
        <tr><td>安徽合肥周谷堆</td><td><span class="spec spec-s">5两-1.0斤</span></td><td class="price">35</td></tr>
        <tr><td>上海江阳</td><td><span class="spec spec-s">1.0-1.5斤</span></td><td class="price">33.5</td></tr>
        <tr><td>重庆龙门西三街</td><td><span class="spec spec-s">1.0-1.5斤</span></td><td class="price">33</td></tr>'''
new_gl = '''        <tr><td>乌鲁木齐北园春</td><td><span class="spec spec-s">1.0-1.5斤</span></td><td class="price"><b style="color:#dc2626">60</b></td></tr>
        <tr><td>福建兴业华洲</td><td><span class="spec spec-s">1.0-1.5斤</span></td><td class="price"><b>48</b></td></tr>
        <tr><td>云南华潮</td><td><span class="spec spec-s">≥1.5斤</span></td><td class="price"><b>47.5</b></td></tr>
        <tr><td>福州名成</td><td><span class="spec spec-s">≥1.5斤</span></td><td class="price">46.5</td></tr>
        <tr><td>湖北黄冈硕源</td><td><span class="spec spec-s">≥1.5斤</span></td><td class="price">43</td></tr>
        <tr><td>福建莆田闽中</td><td><span class="spec spec-s">5两-1.0斤</span></td><td class="price">39.3</td></tr>
        <tr><td>湖北黄冈硕源</td><td><span class="spec spec-s">1.0-1.5斤</span></td><td class="price">38.5</td></tr>
        <tr><td>江西萍乡城南</td><td><span class="spec spec-s">5两-1.0斤</span></td><td class="price">37.5</td></tr>
        <tr><td>甘肃兰州绿色食品</td><td><span class="spec spec-s">≥1.5斤</span></td><td class="price">37</td></tr>
        <tr><td>湖北仙桃江汉平原</td><td><span class="spec spec-s">1.0-1.5斤</span></td><td class="price">36.5</td></tr>
        <tr><td>北京大红门京深</td><td><span class="spec spec-s">≥1.5斤</span></td><td class="price">36</td></tr>
        <tr><td>湖北黄冈硕源</td><td><span class="spec spec-s">5两-1.0斤</span></td><td class="price">35.5</td></tr>
        <tr><td>山东临沂华东淡水鱼</td><td><span class="spec spec-s">≥1.5斤</span></td><td class="price">35</td></tr>
        <tr><td>安徽合肥周谷堆</td><td><span class="spec spec-s">5两-1.0斤</span></td><td class="price">35</td></tr>
        <tr><td>上海江杨</td><td><span class="spec spec-s">1.0-1.5斤</span></td><td class="price">33.5</td></tr>
        <tr><td>重庆龙门西三街</td><td><span class="spec spec-s">1.0-1.5斤</span></td><td class="price">33</td></tr>'''
s = rep(old_gl, new_gl, s, "gui-left")

# 4) 鳜鱼 RIGHT tbody
old_gr = '''        <tr><td>山西太原五龙口</td><td><span class="spec spec-s">1.0-1.5斤</span></td><td class="price">32.5</td></tr>
        <tr><td>湖北宜昌三峡物流园</td><td><span class="spec spec-s">1.0-1.5斤</span></td><td class="price">32</td></tr>
        <tr><td>江西九江鲜活</td><td><span class="spec spec-s">1.0-1.5斤</span></td><td class="price">31.5</td></tr>
        <tr><td>中国供销上饶</td><td><span class="spec spec-s">1.0-1.5斤</span></td><td class="price">31</td></tr>
        <tr><td>福建三明鲜活</td><td><span class="spec spec-s">1.0-1.5斤</span></td><td class="price">31</td></tr>
        <tr><td>江西南昌</td><td><span class="spec spec-s">1.0-1.5斤</span></td><td class="price">29</td></tr>
        <tr><td>江苏凌家塘</td><td><span class="spec spec-s">1.0-1.5斤</span></td><td class="price"><b>28.5</b></td></tr>
        <tr><td>长沙马王堆</td><td><span class="spec spec-s">1.0-1.5斤</span></td><td class="price">28.5</td></tr>
        <tr><td>南京众彩</td><td><span class="spec spec-s">1.0-1.5斤</span></td><td class="price">28.5</td></tr>
        <tr><td>北京岳各庄</td><td><span class="spec spec-s">1.0-1.5斤</span></td><td class="price">28.5</td></tr>
        <tr><td>苏州南环桥</td><td><span class="spec spec-s">1.0-1.5斤</span></td><td class="price">27.75</td></tr>
        <tr><td>武汉白沙洲</td><td><span class="spec spec-s">≥1.5斤</span></td><td class="price">27.25</td></tr>
        <tr><td>武汉白沙洲</td><td><span class="spec spec-s">1.0-1.5斤</span></td><td class="price">26.5</td></tr>
        <tr><td>苏州南环桥</td><td><span class="spec spec-s">5两-1.0斤</span></td><td class="price">25.25</td></tr>
        <tr><td>湖北宜昌三峡物流园</td><td><span class="spec spec-s">5两-1.0斤</span></td><td class="price">25</td></tr>
        <tr><td>武汉白沙洲</td><td><span class="spec spec-s">5两-1.0斤</span></td><td class="price">23.5</td></tr>
        <tr><td>四川攀枝花通威</td><td><span class="spec spec-s">1.0-1.5斤</span></td><td class="price"><b>20</b></td></tr>'''
new_gr = '''        <tr><td>山西太原五龙口</td><td><span class="spec spec-s">1.0-1.5斤</span></td><td class="price">32.5</td></tr>
        <tr><td>湖北宜昌三峡物流园</td><td><span class="spec spec-s">1.0-1.5斤</span></td><td class="price">32</td></tr>
        <tr><td>福建三明鲜活</td><td><span class="spec spec-s">1.0-1.5斤</span></td><td class="price">32</td></tr>
        <tr><td>江西九江鲜活</td><td><span class="spec spec-s">1.0-1.5斤</span></td><td class="price">31.5</td></tr>
        <tr><td>中国供销上饶</td><td><span class="spec spec-s">1.0-1.5斤</span></td><td class="price">31</td></tr>
        <tr><td>上海江杨</td><td><span class="spec spec-s">1.0-1.5斤</span></td><td class="price">30</td></tr>
        <tr><td>江西南昌</td><td><span class="spec spec-s">1.0-1.5斤</span></td><td class="price">29</td></tr>
        <tr><td>江苏凌家塘</td><td><span class="spec spec-s">1.0-1.5斤</span></td><td class="price"><b>28.5</b></td></tr>
        <tr><td>苏州南环桥</td><td><span class="spec spec-s">1.0-1.5斤</span></td><td class="price">27.75</td></tr>
        <tr><td>长沙马王堆</td><td><span class="spec spec-s">1.0-1.5斤</span></td><td class="price">26.5</td></tr>
        <tr><td>武汉白沙洲</td><td><span class="spec spec-s">≥1.5斤</span></td><td class="price">26.5</td></tr>
        <tr><td>武汉白沙洲</td><td><span class="spec spec-s">1.0-1.5斤</span></td><td class="price">25.5</td></tr>
        <tr><td>苏州南环桥</td><td><span class="spec spec-s">5两-1.0斤</span></td><td class="price">25.25</td></tr>
        <tr><td>湖北宜昌三峡物流园</td><td><span class="spec spec-s">5两-1.0斤</span></td><td class="price">25</td></tr>
        <tr><td>武汉白沙洲</td><td><span class="spec spec-s">5两-1.0斤</span></td><td class="price">22.5</td></tr>
        <tr><td>四川攀枝花通威</td><td><span class="spec spec-s">1.0-1.5斤</span></td><td class="price"><b>20</b></td></tr>'''
s = rep(old_gr, new_gr, s, "gui-right")

# 5) 加拿大鲈 LEFT tbody
old_ll = '''        <tr><td>上海江杨</td><td><span class="spec spec-s">≥1.0斤</span></td><td class="price"><b>15</b></td></tr>
        <tr><td>重庆龙门西三街</td><td><span class="spec spec-s">≥1.0斤</span></td><td class="price">14.5</td></tr>
        <tr><td>北京岳各庄</td><td><span class="spec spec-s">≥1.0斤</span></td><td class="price">14.5</td></tr>
        <tr><td>江西萍乡城南</td><td><span class="spec spec-s">≥1.0斤</span></td><td class="price">14</td></tr>
        <tr><td>重庆涪陵新大兴</td><td><span class="spec spec-s">≥1.0斤</span></td><td class="price">14</td></tr>
        <tr><td>江西九江鲜活</td><td><span class="spec spec-s">≥1.0斤</span></td><td class="price">13.5</td></tr>
        <tr><td>湖北仙桃江汉平原</td><td><span class="spec spec-s">≥1.0斤</span></td><td class="price">13</td></tr>
        <tr><td>甘肃兰州绿色食品</td><td><span class="spec spec-s">&lt;1.0斤</span></td><td class="price">13</td></tr>
        <tr><td>中国供销上饶</td><td><span class="spec spec-s">≥1.0斤</span></td><td class="price">13</td></tr>'''
new_ll = '''        <tr><td>上海江杨</td><td><span class="spec spec-s">≥1.0斤</span></td><td class="price"><b>15</b></td></tr>
        <tr><td>重庆龙门西三街</td><td><span class="spec spec-s">≥1.0斤</span></td><td class="price">14.5</td></tr>
        <tr><td>北京岳各庄</td><td><span class="spec spec-s">≥1.0斤</span></td><td class="price">14.5</td></tr>
        <tr><td>重庆涪陵新大兴</td><td><span class="spec spec-s">≥1.0斤</span></td><td class="price">14.1</td></tr>
        <tr><td>江西九江鲜活</td><td><span class="spec spec-s">≥1.0斤</span></td><td class="price">13.5</td></tr>
        <tr><td>江西萍乡城南</td><td><span class="spec spec-s">≥1.0斤</span></td><td class="price">13.5</td></tr>
        <tr><td>湖北仙桃江汉平原</td><td><span class="spec spec-s">≥1.0斤</span></td><td class="price">13</td></tr>
        <tr><td>甘肃兰州绿色食品</td><td><span class="spec spec-s">&lt;1.0斤</span></td><td class="price">13</td></tr>
        <tr><td>中国供销上饶</td><td><span class="spec spec-s">≥1.0斤</span></td><td class="price">13</td></tr>'''
s = rep(old_ll, new_ll, s, "lu-left")

# 6) 加拿大鲈 RIGHT tbody
old_lr = '''        <tr><td>国家级荆州淡水</td><td><span class="spec spec-s">≥1.0斤</span></td><td class="price">12.3</td></tr>
        <tr><td>南京众彩</td><td><span class="spec spec-s">≥1.0斤</span></td><td class="price">12.25</td></tr>
        <tr><td>山西太原五龙口</td><td><span class="spec spec-s">≥1.0斤</span></td><td class="price">12</td></tr>
        <tr><td>湖州菱湖陈塔</td><td><span class="spec spec-s">≥1.0斤</span></td><td class="price"><b>11.3</b></td></tr>
        <tr><td>上海江阳</td><td><span class="spec spec-s">≥1.0斤</span></td><td class="price">11.25</td></tr>
        <tr><td>江西南昌</td><td><span class="spec spec-s">≥1.0斤</span></td><td class="price">11</td></tr>
        <tr><td>湖州菱湖陈塔</td><td><span class="spec spec-s">&lt;1.0斤</span></td><td class="price">10.6</td></tr>
        <tr><td>安徽蚌埠城南</td><td><span class="spec spec-s">≥1.0斤</span></td><td class="price"><b>10.5</b></td></tr>'''
new_lr = '''        <tr><td>南京众彩</td><td><span class="spec spec-s">≥1.0斤</span></td><td class="price">12.75</td></tr>
        <tr><td>国家级郑州淡水</td><td><span class="spec spec-s">≥1.0斤</span></td><td class="price">12.3</td></tr>
        <tr><td>山西太原五龙口</td><td><span class="spec spec-s">≥1.0斤</span></td><td class="price">12</td></tr>
        <tr><td>湖州菱湖陈塔</td><td><span class="spec spec-s">≥1.0斤</span></td><td class="price"><b>11.3</b></td></tr>
        <tr><td>上海江阳</td><td><span class="spec spec-s">≥1.0斤</span></td><td class="price">11.25</td></tr>
        <tr><td>江西南昌</td><td><span class="spec spec-s">≥1.0斤</span></td><td class="price">11</td></tr>
        <tr><td>湖州菱湖陈塔</td><td><span class="spec spec-s">&lt;1.0斤</span></td><td class="price">10.6</td></tr>
        <tr><td>安徽蚌埠城南</td><td><span class="spec spec-s">≥1.0斤</span></td><td class="price"><b>10.5</b></td></tr>'''
s = rep(old_lr, new_lr, s, "lu-right")

# 7) callout: update 黄颡鱼/叉尾鮰 note to 10-28 data, keep rule
old_callout = '''③ <b>黄颡鱼 / 斑点叉尾鮰表格截图截断</b>（仅黄颡鱼首行：黄冈硕源 条重≤1两 10.45），如需录入请补全两表截图；④'''
new_callout = '''③ <b>黄颡鱼 / 斑点叉尾鮰仍按约定不入表</b>（10-28 截图：黄颡鱼首行 13.5 九江鲜活、斑点叉尾鮰 9.5 重庆龙门西三街，均属非跟踪品种）；④'''
s = rep(old_callout, new_callout, s, "callout")

# 8) legend date
s = rep('微信公众号「通威农牧」2026-10-27 18:05《水产行情｜10月27日草、鲤、生鱼、加州鲈、南美白对虾等水产品各地批发价》',
        '微信公众号「通威农牧」2026-10-28《水产行情｜10月28日草、鲤、生鱼、加州鲈、南美白对虾等水产品各地批发价》', s, "legend")

with io.open(p, "w", encoding="utf-8") as f:
    f.write(s)
print("OK wrote", p)
