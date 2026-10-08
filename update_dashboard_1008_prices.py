#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
2026-10-08 看板价格刷新（一次性脚本）
内容：
  1. 无锡盛阳食品城 09-29 → 10-08 批发价卡片整块替换
  2. 农业农村部接口爬虫 鳜鱼批发价卡片 09-21 → 10-08
  3. 农业农村部接口爬虫 鲈鱼批发价卡片 09-21 → 10-08
  4. 公开价源爬虫卡片：北京新发地 08-28 → 10-07（标桂 127→90）
  5. KPI 第 4 格：江苏凌家塘 8/18 → 江西九江琵琶湖 10-08
  6. chips 批发价源日期、版本号 v1.6.0 → v1.6.1、footer 更新时间
用法：python3 update_dashboard_1008_prices.py
"""
import sys

DASHBOARD = "鳜鱼鲈鱼价格看板.html"
NEW_VER = "v1.6.1"
NEW_VER_DATE = "2026-10-08"
FOOTER_TIME = "2026年10月8日 09:30"

LOG = []


def rep(html, old, new, label):
    if old not in html:
        print(f"[FAIL] 未命中：{label}")
        sys.exit(1)
    if html.count(old) > 1:
        print(f"[WARN] {label} 命中 {html.count(old)} 处，只替换第 1 处")
    LOG.append(label)
    return html.replace(old, new, 1)


html = open(DASHBOARD, encoding="utf-8").read()
orig_len = len(html)

# ============ 1. 盛阳食品城卡片：09-29 → 10-08 ============
old_sy_h3 = '''      <h3>🛒 9月29日 · 无锡盛阳食品城水产批发价（元/斤）</h3>'''
new_sy_h3 = '''      <h3>🛒 10月8日 · 无锡盛阳食品城水产批发价（元/斤）</h3>'''
html = rep(html, old_sy_h3, new_sy_h3, "盛阳卡片标题")

old_sy_sub = '''      <div class="csub">本地渠道当日均价，离看板项目最近的一手批发参考。<b>鳜鱼（桂鱼）32~38 元/斤、鲈鱼 10~14.5 元/斤</b>。较 9.20 数据：鳜鱼下限 35→32（-3）、上限 40→38（-2），继续回落；鲈鱼 10~14.5 持平。大宗淡水鱼稳中偏弱：草鱼 8.5~10.5→7.5~9.5、鲫鱼 8~14→8~13、青鱼 9~11→8.5~10、白鲢 3.5~4→3~3.5、鳊鱼下限 8.5→8；白鱼、鲤鱼、非洲鲫鱼、花鲢持平。</div>'''
new_sy_sub = '''      <div class="csub">本地渠道当日均价，离看板项目最近的一手批发参考。<b>鳜鱼（桂鱼）25~30 元/斤、鲈鱼 10~14.5 元/斤</b>。较 9.29 数据：<b style="color:#12a150">鳜鱼下限 32→25（-7）、上限 38→30（-8），跌破 9 月盘整区、创本轮调整新低</b>；鲈鱼 10~14.5 连续三期持平。大宗淡水鱼整体稳中偏强：鲫鱼上限 13→14、白鲢 3~3.5→3~4、鳊鱼下限 8→8.5、青鱼上限 10→10.5、花鲢上限 8→8.5；草鱼 7.5~9.5→7.5~8.5（上限 -1）；白鱼、鲤鱼、非洲鲫鱼持平。</div>'''
html = rep(html, old_sy_sub, new_sy_sub, "盛阳卡片副标题")

old_sy_tbl = '''      <div class="grid2"><div><table><thead><tr><th>编号</th><th>品名</th><th>价格（元/斤）</th></tr></thead><tbody><tr><td>1</td><td>白鱼</td><td class="price">10~16</td></tr><tr><td>2</td><td><b>鳜鱼（桂鱼）</b></td><td class="price"><b>32~38</b></td></tr><tr><td>3</td><td><b>鲈鱼</b></td><td class="price"><b>10~14.5</b></td></tr><tr><td>4</td><td>鲤鱼</td><td class="price">5~6</td></tr><tr><td>5</td><td>非洲鲫鱼</td><td class="price">8.5~9</td></tr><tr><td>6</td><td>红鱼</td><td class="price">—</td></tr><tr><td>7</td><td>鳡鱼</td><td class="price">—</td></tr></tbody></table></div><div><table><thead><tr><th>编号</th><th>品名</th><th>价格（元/斤）</th></tr></thead><tbody><tr><td>1</td><td>鲫鱼</td><td class="price">8~13</td></tr><tr><td>2</td><td>白鲢</td><td class="price">3~3.5</td></tr><tr><td>3</td><td>草鱼</td><td class="price">7.5~9.5</td></tr><tr><td>4</td><td>花鲢</td><td class="price">7.5~8</td></tr><tr><td>5</td><td>鳊鱼</td><td class="price">8~9</td></tr><tr><td>6</td><td>青鱼</td><td class="price">8.5~10</td></tr></tbody></table></div></div>'''
new_sy_tbl = '''      <div class="grid2"><div><table><thead><tr><th>编号</th><th>品名</th><th>价格（元/斤）</th></tr></thead><tbody><tr><td>1</td><td>白鱼</td><td class="price">10~16</td></tr><tr><td>2</td><td><b>鳜鱼（桂鱼）</b></td><td class="price"><b style="color:#12a150">25~30</b></td></tr><tr><td>3</td><td><b>鲈鱼</b></td><td class="price"><b>10~14.5</b></td></tr><tr><td>4</td><td>鲤鱼</td><td class="price">5~6</td></tr><tr><td>5</td><td>非洲鲫鱼</td><td class="price">8.5~9</td></tr><tr><td>6</td><td>红鱼</td><td class="price">—</td></tr><tr><td>7</td><td>鳡鱼</td><td class="price">—</td></tr></tbody></table></div><div><table><thead><tr><th>编号</th><th>品名</th><th>价格（元/斤）</th></tr></thead><tbody><tr><td>1</td><td>鲫鱼</td><td class="price">8~14</td></tr><tr><td>2</td><td>白鲢</td><td class="price">3~4</td></tr><tr><td>3</td><td>草鱼</td><td class="price">7.5~8.5</td></tr><tr><td>4</td><td>花鲢</td><td class="price">7.5~8.5</td></tr><tr><td>5</td><td>鳊鱼</td><td class="price">8.5~9</td></tr><tr><td>6</td><td>青鱼</td><td class="price">8.5~10.5</td></tr></tbody></table></div></div>'''
html = rep(html, old_sy_tbl, new_sy_tbl, "盛阳卡片表格")

old_sy_leg = '''      <div class="legend">来源：微信公众号「无锡盛阳食品城有限公司」2026-09-29《盛阳食品城水产类批发价（当日均价、仅供参考）》（截图 OCR）· 同文杂货类（黄鳝(养殖) 34~45、甲鱼(养殖) 20~56、牛蛙(养殖) 7.3~8、泥鳅(养殖) 10~12、黑鱼 8~10、清江鱼 12.5、银鱼 27~31、河鳗(养殖) 26~35、昂刺鱼 10~16、梭子蟹大/中/小 48/40/36 等）、虾类（河虾按规格 56~130、基围虾 17~22、白虾 50~60、罗氏虾 18~37、黑虎虾 35）与螃蟹（公/母分规格）报价可见，超出本项目核心品种范围未录入；鲳鱼列名但无报价，未录入</div>'''
new_sy_leg = '''      <div class="legend">来源：微信公众号「无锡盛阳食品城有限公司」2026-10-08《盛阳食品城水产类批发价（当日均价、仅供参考）》（截图 OCR）· 同文杂货类（黄鳝(养殖) 35~54、甲鱼(养殖) 20~58、牛蛙(养殖) 7.7~8.6、泥鳅(养殖) 10~12、黑鱼 8.5~11.5、清江鱼 12.5、银鱼 27~31、河鳗(养殖) 26~35、螺蛳(养殖) 3~6、鲶鱼 6、昂刺鱼 10~15；鲥鱼/海板鱼/梭子蟹列名未报价）、虾类（河虾 100头 139 / 130头 112 / 150头 87 / 160头 74 / 180头 57、基围虾大中小 23/21/17、白虾大中小 52/35、罗氏虾大中小 40/34/23、黑虎虾 40；斑节虾列名未报价）与螃蟹（公蟹 2两 20~25 至 5两 75~85；母蟹 1.5两 30~35 至 3.5~3.9两 80~100）报价可见，超出本项目核心品种范围未录入</div>'''
html = rep(html, old_sy_leg, new_sy_leg, "盛阳卡片来源说明")

# ============ 2. MOA 鳜鱼批发价卡片：09-21 → 10-08 ============
old_gui_h3 = '''        <h3 data-page-node-id="mKce4sWWy6nQry5jMAY8c7"><span class="tag tag-gui" data-page-node-id="wBt8G0owAvHHIoZGFOSisz">鳜鱼</span> 批发价（农业农村部接口爬虫 · 2026-09-21）</h3>
        <div class="csub" data-page-node-id="Vt3p8cMnkGCaDsFLXsPKC0">来源：moa_fish_crawler.py 实时抓取 农业农村部 ncpscxx.moa.gov.cn 全国批发价接口（AES 解密）+ 公开价源爬虫（北京新发地 08-28）</div>'''
new_gui_h3 = '''        <h3 data-page-node-id="mKce4sWWy6nQry5jMAY8c7"><span class="tag tag-gui" data-page-node-id="wBt8G0owAvHHIoZGFOSisz">鳜鱼</span> 批发价（农业农村部接口爬虫 · 2026-10-08）</h3>
        <div class="csub" data-page-node-id="Vt3p8cMnkGCaDsFLXsPKC0">来源：moa_fish_crawler.py 实时抓取 农业农村部 ncpscxx.moa.gov.cn 全国批发价接口（AES 解密）+ 公开价源爬虫（北京新发地 2026-10-07）</div>'''
html = rep(html, old_gui_h3, new_gui_h3, "鳜鱼批发卡片标题")

old_gui_thead = '''          <thead data-page-node-id="EKY1eythOSNF7rigdycbE5"><tr data-page-node-id="19KgzXLLNSgeYuRYpH3w4F"><th data-page-node-id="ltnQvqUSQn4Kjbq0fTNbch">市场 / 区域</th><th data-page-node-id="EXKlGR2HJiKpwLMVrOPZ1i">规格</th><th data-page-node-id="coMCxZfo3VTn2Bj2M9SbHx">批发价</th><th data-page-node-id="qfBcfGthf90OTujYiPzBlP">折合元/斤</th></tr></thead>'''
new_gui_thead = '''          <thead data-page-node-id="EKY1eythOSNF7rigdycbE5"><tr data-page-node-id="19KgzXLLNSgeYuRYpH3w4F"><th data-page-node-id="ltnQvqUSQn4Kjbq0fTNbch">市场 / 区域</th><th data-page-node-id="EXKlGR2HJiKpwLMVrOPZ1i">规格</th><th data-page-node-id="coMCxZfo3VTn2Bj2M9SbHx">批发价</th><th data-page-node-id="qfBcfGthf90OTujYiPzBlP">折合元/斤</th><th data-page-node-id="GUIDATE0001">抓取日期</th></tr></thead>'''
html = rep(html, old_gui_thead, new_gui_thead, "鳜鱼批发卡片表头")

old_gui_tbody = '''            <tr data-page-node-id="Qtimhc3T2O9n5TgMcSzmak"><td data-page-node-id="2szTmzCwhZACXPEVkPvYsn">北京 新发地市场</td><td data-page-node-id="F9loMAvrRQBvvpVr9B3zXF"><span class="spec spec-l" data-page-node-id="IYaBcl8RCUeuVb7bibWkMs">标桂</span></td><td class="price" data-page-node-id="XAUMjP3cQHwwTyV9UxPZnQ">127 <small data-page-node-id="zsvvG3wpEBeoxyDbBibqwj">元/公斤</small></td><td data-page-node-id="KlHGNsnge2WqKdgF2nq8ee">≈ 63.5</td></tr>
            <tr data-page-node-id="Xl4Apldolg6AVbeQ6hH4sH"><td data-page-node-id="8sTDjE5pYejdCudEMcIA2M">江苏 凌家塘市场</td><td data-page-node-id="idKGSyKSp2h4B3Y9GLIu73"><span class="spec spec-l" data-page-node-id="h7eSZrHckzz5TFe9ci0A0s">活鳜鱼 统货</span></td><td class="price" data-page-node-id="LFJMqBmHQ1EqKdXqAHiuFH">78 <small data-page-node-id="ORCuKlFhc6DYVTpIStJDCQ">元/公斤</small></td><td data-page-node-id="ugJHBGFyc2oPy3x9a4tHGY">≈ 39</td></tr>
            <tr data-page-node-id="8bPfZJgQoNd7Za9FVy757B"><td data-page-node-id="Wy9cnhiSzSIbEyYLgGYnVK">江西 九江琵琶湖</td><td data-page-node-id="6L8vetfy2okM8bFULArNI3"><span class="spec" data-page-node-id="2oMm8HKC6tWahjIaPwKf8H">活鳜鱼</span></td><td class="price" data-page-node-id="1sz875Q9vXxL9pUCxiEDBT">62 <small data-page-node-id="z1x74nJQtheMRwvF3EvXBt">元/公斤</small></td><td data-page-node-id="g7SjifHrAgV7ZvdczCNnaO">≈ 31</td></tr>
            <tr data-page-node-id="dO8b6SsfiIAmoNoKEFeMJd"><td data-page-node-id="qeaw5aYieRgwMHboNC76bp">乌鲁木齐 北园春</td><td data-page-node-id="SrI7ICHBL4I0kk1r0t74YD"><span class="spec" data-page-node-id="yC949XcaVIIHD57r0rBrhl">活鳜鱼</span></td><td class="price" data-page-node-id="mThSlQBb0FbLHYiE09BjQ9">120 <small data-page-node-id="NcwjIge9OalAn1w8YcqKMy">元/公斤</small></td><td data-page-node-id="pzAZyHbzQqGNZOxIb9I6mK">≈ 60</td></tr>'''
new_gui_tbody = '''            <tr data-page-node-id="8bPfZJgQoNd7Za9FVy757B"><td data-page-node-id="Wy9cnhiSzSIbEyYLgGYnVK"><b>江西 九江琵琶湖</b> <span class="badge b-new" style="font-size:11px">本次</span></td><td data-page-node-id="6L8vetfy2okM8bFULArNI3"><span class="spec" data-page-node-id="2oMm8HKC6tWahjIaPwKf8H">活鳜鱼</span></td><td class="price" data-page-node-id="1sz875Q9vXxL9pUCxiEDBT"><b>60</b> <small data-page-node-id="z1x74nJQtheMRwvF3EvXBt">元/公斤</small></td><td data-page-node-id="g7SjifHrAgV7ZvdczCNnaO">≈ 30 <small style="color:#12a150">▼2</small></td><td data-page-node-id="GUIDATE0002">2026-10-08</td></tr>
            <tr data-page-node-id="Qtimhc3T2O9n5TgMcSzmak"><td data-page-node-id="2szTmzCwhZACXPEVkPvYsn">北京 新发地市场</td><td data-page-node-id="F9loMAvrRQBvvpVr9B3zXF"><span class="spec spec-l" data-page-node-id="IYaBcl8RCUeuVb7bibWkMs">标桂</span></td><td class="price" data-page-node-id="XAUMjP3cQHwwTyV9UxPZnQ"><b>90</b> <small data-page-node-id="zsvvG3wpEBeoxyDbBibqwj">元/公斤</small></td><td data-page-node-id="KlHGNsnge2WqKdgF2nq8ee">≈ 45 <small style="color:#12a150">▼37</small></td><td data-page-node-id="GUIDATE0003">2026-10-07</td></tr>
            <tr data-page-node-id="Xl4Apldolg6AVbeQ6hH4sH"><td data-page-node-id="8sTDjE5pYejdCudEMcIA2M">江苏 凌家塘市场</td><td data-page-node-id="idKGSyKSp2h4B3Y9GLIu73"><span class="spec spec-l" data-page-node-id="h7eSZrHckzz5TFe9ci0A0s">活鳜鱼 统货</span></td><td class="price" data-page-node-id="LFJMqBmHQ1EqKdXqAHiuFH">78 <small data-page-node-id="ORCuKlFhc6DYVTpIStJDCQ">元/公斤</small></td><td data-page-node-id="ugJHBGFyc2oPy3x9a4tHGY">≈ 39</td><td data-page-node-id="GUIDATE0004">2026-08-18</td></tr>
            <tr data-page-node-id="dO8b6SsfiIAmoNoKEFeMJd"><td data-page-node-id="qeaw5aYieRgwMHboNC76bp">乌鲁木齐 北园春</td><td data-page-node-id="SrI7ICHBL4I0kk1r0t74YD"><span class="spec" data-page-node-id="yC949XcaVIIHD57r0rBrhl">活鳜鱼</span></td><td class="price" data-page-node-id="mThSlQBb0FbLHYiE09BjQ9">120 <small data-page-node-id="NcwjIge9OalAn1w8YcqKMy">元/公斤</small></td><td data-page-node-id="pzAZyHbzQqGNZOxIb9I6mK">≈ 60</td><td data-page-node-id="GUIDATE0005">2026-09-21</td></tr>'''
html = rep(html, old_gui_tbody, new_gui_tbody, "鳜鱼批发卡片数据行")

old_gui_callout = '''        <div class="callout" style="margin-top:14px" data-page-node-id="GYXOtM2fNMRgSqHXIDx0Nx"><b data-page-node-id="fPBD3S4ViW1htcCGeJPhIO">数据说明：</b>本表由爬虫直连农业农村部官方批发价接口（品种码 <b data-page-node-id="s1Q00TF0POF5yVqQud9t36">AM01013003</b>）解密所得，<b data-page-node-id="CcdYkUaKKXB89kQcLbapv8">最新抓取日期 2026-09-21</b>。2026-09-14 当日活鳜鱼接口仍返回 <b data-page-node-id="rFqB7rlTfkAp0KvBLbSpHG">data=null</b>，无新报价；上一条有效报价仍为 2026-08-18 江苏凌家塘 <b data-page-node-id="KWYxiGs58eeFylJ0KdMBCI">78 元/公斤</b>。公开价源爬虫 2026-08-28 北京新发地标桂 <b data-page-node-id="K8nt8iKdFOHTYxIK99aYET">127 元/公斤</b>，可作为销地高端批发参考。另见「补充·科学养鱼」板块 08-27 全国多市场分规格鳜鱼及「补充·公开价源爬虫」板块 武汉白沙洲/九江分规格鳜鱼可作交叉参考。</div>'''
new_gui_callout = '''        <div class="callout" style="margin-top:14px" data-page-node-id="GYXOtM2fNMRgSqHXIDx0Nx"><b data-page-node-id="fPBD3S4ViW1htcCGeJPhIO">数据说明：</b>本表由爬虫直连农业农村部官方批发价接口（品种码 <b data-page-node-id="s1Q00TF0POF5yVqQud9t36">AM01013003</b>）解密所得，<b data-page-node-id="CcdYkUaKKXB89kQcLbapv8">最新抓取日期 2026-10-08</b>。当日全国仅 <b data-page-node-id="rFqB7rlTfkAp0KvBLbSpHG">1 条</b>活鳜鱼报价——江西九江琵琶湖 <b data-page-node-id="KWYxiGs58eeFylJ0KdMBCI">60 元/公斤</b>（≈30 元/斤），较 09-21 的 62 元/公斤跌 2。江苏凌家塘当日无新报价，最后有效报价仍为 2026-08-18 的 78 元/公斤。<b>销地高端批发同步大跌</b>：公开价源爬虫 2026-10-07 北京新发地标桂 <b data-page-node-id="K8nt8iKdFOHTYxIK99aYET">90 元/公斤</b>（≈45 元/斤），较 08-28 的 127 元/公斤跌 37（-29%）。与无锡盛阳食品城 10-08 批发 25~30 元/斤、塘口价 22~31 元/斤三口径同向——<b>鳜鱼全链条下行，批零两端同步下移，现阶段尚无企稳信号</b>。另见「补充·科学养鱼」板块全国多市场分规格鳜鱼可作交叉参考。</div>'''
html = rep(html, old_gui_callout, new_gui_callout, "鳜鱼批发卡片说明")

# ============ 3. MOA 鲈鱼批发价卡片：09-21 → 10-08 ============
old_lu_h3 = '''        <h3 data-page-node-id="LVf0hGF0s0rP5ZzxKjrCUX"><span class="tag tag-lu" data-page-node-id="KcCIaxgQu9mt7vvhD3qIRS">鲈鱼</span> 批发价（农业农村部接口爬虫 · 2026-09-21）</h3>'''
new_lu_h3 = '''        <h3 data-page-node-id="LVf0hGF0s0rP5ZzxKjrCUX"><span class="tag tag-lu" data-page-node-id="KcCIaxgQu9mt7vvhD3qIRS">鲈鱼</span> 批发价（农业农村部接口爬虫 · 2026-10-08）</h3>'''
html = rep(html, old_lu_h3, new_lu_h3, "鲈鱼批发卡片标题")

old_lu_tbody = '''            <tr data-page-node-id="bF37MMSDI051rLi9J628V5"><td data-page-node-id="4Cpf0cuqix8pH5PsC1AQVU">山西长治 紫坊农贸</td><td data-page-node-id="Lo3WBSDY3RW3Cgv7lzVOwn"><span class="spec spec-s" data-page-node-id="Kl39NrYpSyS1LFsOJ3d3xv">淡水鲈鱼</span></td><td class="price" data-page-node-id="1DIOCEshtogWHSfGsgBdQm">31 <small data-page-node-id="E7EHJVXJxrtOipWyzGhKEB">元/公斤</small></td><td data-page-node-id="OExyuWYlqnW91Gq3Ysui05">≈ 15.5</td></tr>
            <tr data-page-node-id="L6w0UD1lCTNjF3Dvbt6IRp"><td data-page-node-id="YcuiTNoZbqN5BRZF5dnhfi">重庆 西三街农副</td><td data-page-node-id="zYkAX6om2iyKXSF01NoFWh"><span class="spec spec-l" data-page-node-id="RRzGirjH78RLb9DPMVs28g">海水鲈鱼</span></td><td class="price" data-page-node-id="r39Kw5EDIUWTUYJTAoDZ1m">40 <small data-page-node-id="nPMuYj5oYySn6nqeEP9Y5V">元/公斤</small></td><td data-page-node-id="XQTnWOVrUlxyzMGg6eHaDP">≈ 20</td></tr>
            <tr data-page-node-id="tdbeM7K503DdWW4tUTck0u"><td data-page-node-id="Gixv9UkLr8CY9KUvaC559a">北京 大洋路市场</td><td data-page-node-id="cHGaSk4tgCDY43YQCYDytp"><span class="spec spec-l" data-page-node-id="FOtgl8aFDvc9kkWOx3okEH">海水鲈鱼</span></td><td class="price" data-page-node-id="KzLlRWF0KNZxBRjOSKFWAt">30 <small data-page-node-id="zPxrnnrQF9PRKb3iR3ahHj">元/公斤</small></td><td data-page-node-id="GqNH2v7bRXB9g1NKTF3RHb">≈ 15</td></tr>
            <tr data-page-node-id="CnNWITtz1RFAXm5p44noao"><td data-page-node-id="1QFF3uqXsWW9qEnQLbXdT1">山东青岛 城阳水产</td><td data-page-node-id="4RDg4XERlqqqQEdFhTpeCQ"><span class="spec spec-l" data-page-node-id="b1gidbUkDxJUoFXqdnwzl2">海水鲈鱼</span></td><td class="price" data-page-node-id="eZyz9iZhgJI4BV5IMuDd5L">60 <small data-page-node-id="RhSvSsTPCgtjqTo9aaAO7R">元/公斤</small></td><td data-page-node-id="G8jiA1Xxld5MPfyos9NLQN">≈ 30</td></tr>
            <tr data-page-node-id="3z0eAH7GYSZAYHRf0YM0AM"><td data-page-node-id="XRS02wFRsKcC8uliUXICSG">山东威海 水产品市场</td><td data-page-node-id="cu0lYCHc4pGHLm4bSrkbW5"><span class="spec spec-l" data-page-node-id="WB5CO04Tv1XljsYWqaMKlv">海水鲈鱼</span></td><td class="price" data-page-node-id="UGXvnhBkBhyToH6KPBdZH2">40 <small data-page-node-id="AWfSOlk9tGQjqyEvNZ7iuR">元/公斤</small></td><td data-page-node-id="kUZeaD705DCASfRcMLybKC">≈ 20</td></tr>
            <tr data-page-node-id="1mkEQg1zU06cC5TgzVaQKE"><td data-page-node-id="2fQ6zEQJQdGOZgQWzjwxNy">河南 万邦国际</td><td data-page-node-id="aEGpQ52jnugYa9xGNIuLDU"><span class="spec spec-l" data-page-node-id="T1L92HhZx4mPgYAueFkO6F">海水鲈鱼</span></td><td class="price" data-page-node-id="Dae8VkxpPgiVCHQd26tAmU">29 <small data-page-node-id="Ks8uSCxJD73AAzWSgodGWs">元/公斤</small></td><td data-page-node-id="wPIdi4pQlmxOb028TFEa6v">≈ 14.5</td></tr>'''
new_lu_tbody = '''            <tr data-page-node-id="bF37MMSDI051rLi9J628V5"><td data-page-node-id="4Cpf0cuqix8pH5PsC1AQVU"><b>安徽 马鞍山安民</b> <span class="badge b-new" style="font-size:11px">江苏周边 · 新增</span></td><td data-page-node-id="Lo3WBSDY3RW3Cgv7lzVOwn"><span class="spec spec-s" data-page-node-id="Kl39NrYpSyS1LFsOJ3d3xv">淡水鲈鱼</span></td><td class="price" data-page-node-id="1DIOCEshtogWHSfGsgBdQm"><b>22</b> <small data-page-node-id="E7EHJVXJxrtOipWyzGhKEB">元/公斤</small></td><td data-page-node-id="OExyuWYlqnW91Gq3Ysui05">≈ 11</td></tr>
            <tr data-page-node-id="L6w0UD1lCTNjF3Dvbt6IRp"><td data-page-node-id="YcuiTNoZbqN5BRZF5dnhfi">山西长治 紫坊农贸</td><td data-page-node-id="zYkAX6om2iyKXSF01NoFWh"><span class="spec spec-s" data-page-node-id="RRzGirjH78RLb9DPMVs28g">淡水鲈鱼</span></td><td class="price" data-page-node-id="r39Kw5EDIUWTUYJTAoDZ1m">29 <small data-page-node-id="nPMuYj5oYySn6nqeEP9Y5V">元/公斤</small></td><td data-page-node-id="XQTnWOVrUlxyzMGg6eHaDP">≈ 14.5 <small style="color:#12a150">▼2</small></td></tr>
            <tr data-page-node-id="tdbeM7K503DdWW4tUTck0u"><td data-page-node-id="Gixv9UkLr8CY9KUvaC559a">山东青岛 城阳水产</td><td data-page-node-id="cHGaSk4tgCDY43YQCYDytp"><span class="spec spec-l" data-page-node-id="FOtgl8aFDvc9kkWOx3okEH">海水鲈鱼</span></td><td class="price" data-page-node-id="KzLlRWF0KNZxBRjOSKFWAt">50 <small data-page-node-id="zPxrnnrQF9PRKb3iR3ahHj">元/公斤</small></td><td data-page-node-id="GqNH2v7bRXB9g1NKTF3RHb">≈ 25 <small style="color:#12a150">▼10</small></td></tr>
            <tr data-page-node-id="CnNWITtz1RFAXm5p44noao"><td data-page-node-id="1QFF3uqXsWW9qEnQLbXdT1">山东威海 水产品市场</td><td data-page-node-id="4RDg4XERlqqqQEdFhTpeCQ"><span class="spec spec-l" data-page-node-id="b1gidbUkDxJUoFXqdnwzl2">海水鲈鱼</span></td><td class="price" data-page-node-id="eZyz9iZhgJI4BV5IMuDd5L">46 <small data-page-node-id="RhSvSsTPCgtjqTo9aaAO7R">元/公斤</small></td><td data-page-node-id="G8jiA1Xxld5MPfyos9NLQN">≈ 23 <small style="color:#dc2626">▲6</small></td></tr>
            <tr data-page-node-id="3z0eAH7GYSZAYHRf0YM0AM"><td data-page-node-id="XRS02wFRsKcC8uliUXICSG">重庆 西三街农副</td><td data-page-node-id="cu0lYCHc4pGHLm4bSrkbW5"><span class="spec spec-l" data-page-node-id="WB5CO04Tv1XljsYWqaMKlv">海水鲈鱼</span></td><td class="price" data-page-node-id="UGXvnhBkBhyToH6KPBdZH2">40 <small data-page-node-id="AWfSOlk9tGQjqyEvNZ7iuR">元/公斤</small></td><td data-page-node-id="kUZeaD705DCASfRcMLybKC">≈ 20 <small style="color:#6b7280">持平</small></td></tr>
            <tr data-page-node-id="1mkEQg1zU06cC5TgzVaQKE"><td data-page-node-id="2fQ6zEQJQdGOZgQWzjwxNy">山东滨州 鲁北蔬菜</td><td data-page-node-id="aEGpQ52jnugYa9xGNIuLDU"><span class="spec spec-l" data-page-node-id="T1L92HhZx4mPgYAueFkO6F">海水鲈鱼</span></td><td class="price" data-page-node-id="Dae8VkxpPgiVCHQd26tAmU">32 <small data-page-node-id="Ks8uSCxJD73AAzWSgodGWs">元/公斤</small></td><td data-page-node-id="wPIdi4pQlmxOb028TFEa6v">≈ 16</td></tr>
            <tr data-page-node-id="LUNEWROW0001"><td data-page-node-id="LUNEWCELL001">河南 万邦国际</td><td data-page-node-id="LUNEWCELL002"><span class="spec spec-l">海水鲈鱼</span></td><td class="price">27 <small>元/公斤</small></td><td data-page-node-id="LUNEWCELL003">≈ 13.5 <small style="color:#12a150">▼2</small></td></tr>'''
html = rep(html, old_lu_tbody, new_lu_tbody, "鲈鱼批发卡片数据行")

old_lu_sub = '''        <div class="csub" style="margin-top:14px" data-page-node-id="W11PvLzHuuPiOkfThM2gA3">※ 2026-09-21 爬虫实测：农业农村部接口返回 8 条鲈鱼样本（淡水鲈鱼 2 条、海水鲈鱼 6 条）。淡水鲈鱼长治紫坊 <b data-page-node-id="hsBoH2Zv1kT7zSKUIXFbl5">31</b> 元/公斤；海水鲈鱼北京大洋路 <b data-page-node-id="VtED6yT1nthC19roQAPfJP">30</b>（较 08-28 的 31 略跌 1）、青岛城阳 <b data-page-node-id="YxwznL9jDudNp8NlOFaGmm">60</b>（较 08-28 的 36 大涨，注意规格/到货差异）、山东威海 40、重庆西三街 40、河南万邦 29 元/公斤。江苏及周边（凌家塘/南环桥/合肥周谷堆/马鞍山）当日无新报价，参考 08-28 数据。鲈鱼整体低位运行，区域差异大。</div>'''
new_lu_sub = '''        <div class="csub" style="margin-top:14px" data-page-node-id="W11PvLzHuuPiOkfThM2gA3">※ 2026-10-08 爬虫实测：农业农村部接口返回 8 条鲈鱼样本（淡水鲈鱼 2 条、海水鲈鱼 6 条）。<b data-page-node-id="hsBoH2Zv1kT7zSKUIXFbl5">江苏周边首次出现鲈鱼报价——安徽马鞍山安民 22 元/公斤（≈11 元/斤）</b>，是离宜兴官林镇最近的一条批发参考，也是本次全表最低价。淡水鲈鱼长治紫坊 29（较 09-21 的 31 跌 2）；海水鲈鱼青岛城阳 <b data-page-node-id="VtED6yT1nthC19roQAPfJP">50</b>（较 09-21 的 60 跌 10）、山东威海 <b data-page-node-id="YxwznL9jDudNp8NlOFaGmm">46</b>（较 40 涨 6，规格/到货差异大）、滨州鲁北 32（新样本）、重庆西三街 40（持平）、河南万邦 27（较 29 跌 2）。海水鲈鱼区域价差 27~50 元/公斤，整体仍未走出低位；淡水鲈鱼马鞍山 22 / 长治 29 的双低组合，与江苏塘口 10.5 元/斤、广东佛山 8~9 元/斤方向一致。</div>'''
html = rep(html, old_lu_sub, new_lu_sub, "鲈鱼批发卡片说明")

# ============ 4. 公开价源卡片：新发地 08-28 → 10-07 ============
old_pub_sub = '''      <div class="csub" data-page-node-id="H0eLwUuGYspluwA4VC6VQ1">来源：<b data-page-node-id="W246slu02dy3bjrJHkngUS">public_price_crawler.py</b> 实时抓取 武汉白沙洲（07-03）/ 九江市农业农村局（07-24）/ 云南华潮（07-16）/ <b data-page-node-id="Kh5zcZW4M2vmlVwmQILcSA">北京新发地（08-27，每日价格行情 API）</b>公开价格表，弥补农业农村部接口「不分规格」的缺口。新发地官网单位为元/斤，已统一 ×2 换算为元/公斤。<b data-page-node-id="ZvcB2yeqgE4yZg60lqKdn0">北京新发地最新 2026-08-28</b>。青鱼/鲫鱼/鲤鱼/鲢鱼/鳊鱼/鳙鱼等完整数据见 <code data-page-node-id="6XV690bxk5MNjaNUv6oQV7">public_fish_prices.csv</code>。</div>'''
new_pub_sub = '''      <div class="csub" data-page-node-id="H0eLwUuGYspluwA4VC6VQ1">来源：<b data-page-node-id="W246slu02dy3bjrJHkngUS">public_price_crawler.py</b> 实时抓取 武汉白沙洲（2026-07-03）/ 九江市农业农村局（2026-07-24）/ 云南华潮（2026-07-16）/ <b data-page-node-id="Kh5zcZW4M2vmlVwmQILcSA">北京新发地（2026-10-07，每日价格行情 API）</b>公开价格表，弥补农业农村部接口「不分规格」的缺口。新发地官网单位为元/斤，已统一 ×2 换算为元/公斤。<b data-page-node-id="ZvcB2yeqgE4yZg60lqKdn0">本次 10-08 刷新：北京新发地 2026-10-07 鳜鱼标桂 <span style="color:#12a150">90</span> 元/公斤（较 08-28 的 127 跌 37，-29%）、淡水鲈鱼活 32、海鲈鱼鲜 33</b>；武汉白沙洲/九江/云南华潮三家源页未更新，沿用近期数据。青鱼/鲫鱼/鲤鱼/鲢鱼/鳊鱼/鳙鱼等完整数据见 <code data-page-node-id="6XV690bxk5MNjaNUv6oQV7">public_fish_prices.csv</code>。</div>'''
html = rep(html, old_pub_sub, new_pub_sub, "公开价源卡片副标题")

old_pub_tbody_start = '''          <tr data-page-node-id="mIzo4uNJyX02PxZgiqnJZR"><td data-page-node-id="7pdb8kPu5dCFVyIcDQduuR">武汉白沙洲 07-03</td>'''
new_pub_tbody_start = '''          <tr data-page-node-id="PUB1007ROW001"><td data-page-node-id="PUB1007CELL01"><b>北京新发地 10-07</b> <span class="badge b-new" style="font-size:11px">本次</span></td><td data-page-node-id="PUB1007CELL02">鳜鱼(桂鱼)</td><td data-page-node-id="PUB1007CELL03"><span class="spec spec-l">标桂</span></td><td class="price" data-page-node-id="PUB1007CELL04"><b>90</b> <small style="color:#12a150">▼37</small></td><td data-page-node-id="PUB1007CELL05">斤→公斤</td></tr>
          <tr data-page-node-id="PUB1007ROW002"><td data-page-node-id="PUB1007CELL06"><b>北京新发地 10-07</b></td><td data-page-node-id="PUB1007CELL07">鲈鱼</td><td data-page-node-id="PUB1007CELL08"><span class="spec spec-l">淡水 活</span></td><td class="price" data-page-node-id="PUB1007CELL09">32</td><td data-page-node-id="PUB1007CELL10">斤→公斤 · 较 08-28 的 33 跌 1</td></tr>
          <tr data-page-node-id="PUB1007ROW003"><td data-page-node-id="PUB1007CELL11"><b>北京新发地 10-07</b></td><td data-page-node-id="PUB1007CELL12">鲈鱼</td><td data-page-node-id="PUB1007CELL13"><span class="spec">海水 鲜</span></td><td class="price" data-page-node-id="PUB1007CELL14">33</td><td data-page-node-id="PUB1007CELL15">斤→公斤 · 较 08-28 的 31 涨 2</td></tr>
          <tr data-page-node-id="mIzo4uNJyX02PxZgiqnJZR"><td data-page-node-id="7pdb8kPu5dCFVyIcDQduuR">武汉白沙洲 07-03</td>'''
html = rep(html, old_pub_tbody_start, new_pub_tbody_start, "公开价源卡片新增新发地 10-07 行")

old_pub_note = '''      <div class="csub" style="margin-top:12px" data-page-node-id="qY5HWoF5Fvg4aZNby4hY46">※ 武汉白沙洲提供<b data-page-node-id="NtgTugxS7BP5re365q57uH">分规格</b>鳜鱼批发价（大规格溢价明显：≥750g 73 vs 250–500g 71 元/公斤）；九江（07-24）鳜鱼 400–750g 达 90、鲈鱼 500–750g 38 元/公斤，反映 7 月下旬鳜鱼走强；<b data-page-node-id="rUvJPy8a7GumHzJL41LF5z">北京新发地（08-27）</b>鳜鱼标桂 128、淡水鲈鱼活 33、海鲈鱼鲜 31 元/公斤，北上广与凌家塘/白沙洲交叉验证。四家来源与农业农村部爬虫（凌家塘活鳜鱼 96、海水鲈鱼 27）方向一致（鳜鱼高位、鲈鱼稳中偏弱），但区域与规格口径不同，绝对值不可直接比较。</div>'''
new_pub_note = '''      <div class="csub" style="margin-top:12px" data-page-node-id="qY5HWoF5Fvg4aZNby4hY46">※ <b data-page-node-id="rUvJPy8a7GumHzJL41LF5z">北京新发地本次刷新（10-07）是全场最关键的变化</b>：鳜鱼标桂 127（08-28）→ <b style="color:#12a150">90</b> 元/公斤，一个月跌 37 元（-29%），销地高端批发同步大幅补跌；淡水鲈鱼活 32（-1）、海鲈鱼鲜 33（+2）基本持稳。<b data-page-node-id="NtgTugxS7BP5re365q57uH">三家地方源未更新</b>——武汉白沙洲（07-03）提供分规格鳜鱼批发价（大规格溢价：≥750g 73 vs 250–500g 71 元/公斤）、九江（07-24）鳜鱼 400–750g 90 / 鲈鱼 500–750g 38、云南华潮（07-16）统货鳜 95 / 鲈 34，均为 7 月行情，仅作历史参照。<b>本次三源交叉结论</b>：新发地标桂 90（10-07）、盛阳食品城 25~30 元/斤（10-08）、塘口价 22~31 元/斤（10-05/07/08）——鳜鱼从产地到销地全链条下行且尚未见底。区域与规格口径不同，绝对值不可直接比较。</div>'''
html = rep(html, old_pub_note, new_pub_note, "公开价源卡片尾注")

# ============ 5. KPI 第 4 格 ============
old_kpi4 = '''      <div class="lbl" data-page-node-id="kPuPdIqNT11zI2s03ViZaC"><span class="dot" style="background:var(--gui)" data-page-node-id="dZ078T67CyzUT1ACH0KNRm"></span>江苏 鳜鱼 批发价（爬虫 8/18）</div>
      <div class="val" data-page-node-id="SREcF0PI3syyiMMknBvCyN">78 <small data-page-node-id="bH4tlbl2P2L6uEPIIlZkzP">元/公斤</small></div>
      <div class="trend t-down" data-page-node-id="yZBJJjD5hZCOkcKaxaEjDB">▼ 较8/13的86回落8</div>'''
new_kpi4 = '''      <div class="lbl" data-page-node-id="kPuPdIqNT11zI2s03ViZaC"><span class="dot" style="background:var(--gui)" data-page-node-id="dZ078T67CyzUT1ACH0KNRm"></span>江西九江 鳜鱼 批发价（爬虫 10-08）</div>
      <div class="val" data-page-node-id="SREcF0PI3syyiMMknBvCyN">60 <small data-page-node-id="bH4tlbl2P2L6uEPIIlZkzP">元/公斤</small></div>
      <div class="trend t-down" data-page-node-id="yZBJJjD5hZCOkcKaxaEjDB">▼ 较 09-21 的 62 跌 2 · 新发地标桂 10-07 报 90（较 08-28 的 127 大跌 37）</div>'''
html = rep(html, old_kpi4, new_kpi4, "KPI 第 4 格")

# ============ 6. chip / 版本号 / footer ============
old_chip = '''      <span class="chip" data-page-node-id="4HGb9s5gzmgXv3QvdK82PP">🤖 批发价：农业农村部接口爬虫 + 公开价源爬虫 + 科学养鱼OCR（09-24）+ a渔业行情OCR（9.15报价）</span>'''
new_chip = '''      <span class="chip" data-page-node-id="4HGb9s5gzmgXv3QvdK82PP">🤖 批发价：农业农村部接口爬虫（10-08）+ 公开价源爬虫（新发地 10-07）+ 科学养鱼OCR（09-24）+ a渔业行情OCR（9.15报价）</span>'''
html = rep(html, old_chip, new_chip, "批发价 chip")

html = rep(html,
           '<meta name="dashboard-version" content="v1.6.0">',
           '<meta name="dashboard-version" content="v1.6.1">',
           "meta 版本号")

old_ver_chip = '''      <span class="chip chip-version" data-page-node-id="VER01CHIP0001" title="看板版本号 · 完整历史见 VERSION.md">🏷️ 版本 v1.6.0 · 2026-10-08</span>'''
new_ver_chip = '''      <span class="chip chip-version" data-page-node-id="VER01CHIP0001" title="看板版本号 · 完整历史见 VERSION.md">🏷️ 版本 v1.6.1 · 2026-10-08</span>'''
html = rep(html, old_ver_chip, new_ver_chip, "版本 chip")

old_footer = '''    看板更新 2026年9月28日 09:35 · 统计周期 2026-07-13 ~ 2026-09-21 · 农业农村部爬虫抓取 2026-09-21（活鳜鱼仍无报价，保留凌家塘78元/公斤；鲈鱼7条样本）· 公开价源爬虫 07-03~08-28（含北京新发地）· 科学养鱼 OCR 09-24（鳜鱼 7 条 + 加州鲈 5 条，环比 09-17：南环桥续跌、云南华潮 110 领涨）· a渔业行情 OCR 9.15 报价（鳜鱼 8 条 + 加州鲈 7 条，2026-09-17 发布，环比 9.14：鳜鱼续跌 0.5~1.5 元、鲈鱼全线持平）+ 科学养鱼 09-10《冰火两重天》行业观察 · 塘口价快照 09-10/11（腾氏水产商务网 09-10 报价视频 + 兴渔派-鳜鱼通 + 视频号「互联惠农小洁」9-11「水产预报老段」9-11「水产养殖老陈9396」9-10 OCR + 无锡盛阳食品城 09-20 批发价）· 病害预警 09-28（第十部分，含总站 9 月/10 月预测预报 + 南京 10 月预报 · 全国水产技术推广总站 9 月预测预报 · 鳜鱼红彩病毒 · 示意图已去水印）· 抖音 TikHub 09-14 抓取 14 条 · 验收对照区块 09-17（行情监测功能清单 5 项全覆盖：看板/品种管理/市场管理/数据管理/数据爬取，明细自动取自 fish_prices_history.csv）· 养殖场实时气象+7天预报 每日 09:00 自动刷新（Open-Meteo × 高德双源校验 · 宜兴官林镇 119.723966,31.557387）· 价格随行就市，仅供参考'''
new_footer = '''    看板更新 2026年10月8日 09:30 · 统计周期 2026-07-13 ~ 2026-10-08 · <b>农业农村部爬虫抓取 2026-10-08</b>（活鳜鱼仅 1 条：江西九江琵琶湖 60 元/公斤；鲈鱼 8 条，含江苏周边马鞍山安民 22 元/公斤）· <b>公开价源爬虫本次刷新：北京新发地 2026-10-07</b>（鳜鱼标桂 90 元/公斤，较 08-28 的 127 跌 37；淡水鲈活 32、海鲈鲜 33；武汉白沙洲 07-03 / 九江 07-24 / 云南华潮 07-16 三家源页未更新）、<b>无锡盛阳食品城 2026-10-08 批发价</b>（鳜鱼 25~30 元/斤创本轮新低、鲈鱼 10~14.5 持平）· 塘头价快照（水产前沿第 35 期周报 09-29 + 水产养殖网 10-05 周报 + 视频号「互联惠农小洁」10-07/08「悠扬水产」10-08「水产养殖服务于老师」10-07 + 全国渔业价格日报 09-30）· 科学养鱼 OCR 09-24（鳜鱼 7 条 + 加州鲈 5 条）· a渔业行情 OCR 9.15 报价（鳜鱼 8 条 + 加州鲈 7 条）· 病害预警 09-28（第十部分，含总站 9 月/10 月预测预报 + 南京 10 月预报 · 鳜鱼红彩病毒 · 示意图已去水印）· 抖音 TikHub 09-14 抓取 14 条 · 验收对照区块 09-17（行情监测功能清单 5 项全覆盖：看板/品种管理/市场管理/数据管理/数据爬取，明细自动取自 fish_prices_history.csv）· 养殖场实时气象+7天预报 每日 09:00 自动刷新（Open-Meteo × 高德双源校验 · 宜兴官林镇 119.723966,31.557387）· 价格随行就市，仅供参考'''
html = rep(html, old_footer, new_footer, "footer 更新时间")

open(DASHBOARD, "w", encoding="utf-8").write(html)

print(f"[OK] 共 {len(LOG)} 处替换全部命中：")
for i, x in enumerate(LOG, 1):
    print(f"   {i:2d}. {x}")
print(f"[OK] 文件 {orig_len} → {len(html)} bytes（{len(html)-orig_len:+d}）")
