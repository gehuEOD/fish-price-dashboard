#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
2026-10-28 数据更新：渔有福 10-28 鳜鱼塘口 + 全国渔业价格 10-28 早报 + 渔飞鱼(渔知识指导) 10-28 日报
===============================================================================================
来源（用户提供的公众号链接）：
  A https://mp.weixin.qq.com/s/1iFkF6nUCpzBRXh-YIUTug  渔有福水产 10-28 09:34 鳜鱼塘口行情
  B https://mp.weixin.qq.com/s/q-qVBDQBduemizdiMImBMA  全国渔业价格 10-27 18:00 10-28 行情早报
  C https://mp.weixin.qq.com/s/r2EQTGBk2Ep2Nn1WetN93A  渔知识指导(渔飞鱼·董小月) 10-28 05:05 日报
  D https://mp.weixin.qq.com/s/NQWBeByVoxePNH947Fs4iw  渔飞鱼水产 10-27 09:59 10-28 明日预报（看板已有）
  E https://mp.weixin.qq.com/s/PYAhLUwKJAjRBbiQgDOj2A  淡水渔业 10-27 批发价（看板已有）
"""
import re
import sys

P = "鳜鱼鲈鱼价格看板.html"
s = open(P, encoding="utf-8").read()
orig_len = len(s)

RED, GREEN, GRAY = "#dc2626", "#12a150", "#6b7280"

def colorize(t: str) -> str:
    return t.replace("@@R@@", RED).replace("@@G@@", GREEN).replace("@@K@@", GRAY)



# ---------------------------------------------------------------- 卡片 1：渔有福 10-28
CARD_GUI = """    <div class="card" style="margin-top:14px">
      <h3>🐟 10月28日 · 鳜鱼塘口价一览（广东中鳜再跌 0.5 · 外省标鳜全线稳）</h3>
      <div class="csub"><b style="color:@@G@@">广东中鳜（1.5~2 斤）24.5 → 24 元/斤，跌 0.5</b>，为全表唯一变动；小鳜 18.5、标鳜 24.5 转稳。外省标鳜<b>全线持平</b>：湖北 24.5、安徽 25、湖南 25、<b style="color:@@R@@">江西 26 / 江苏 26 继续领跑</b>。全表价差 8 元/斤（广东小鳜 18.5 最低 vs 江苏/江西 26 最高）。<b>成因：</b>成鱼持续上市、流通走货速度一般，广东大规格中鳜承压先行下调，属结构性下调而非全线下行。</div>
      <table style="width:100%;border-collapse:collapse;font-size:13px"><thead><tr><th>产区</th><th>规格</th><th>塘口价（元/斤）</th><th>较 10-27</th></tr></thead><tbody>
        <tr><td>广东</td><td><span class="spec spec-s">小鳜（0.8斤以下）</span></td><td class="price"><b>18.5</b></td><td style="color:@@K@@;font-size:12px">→ 平</td></tr>
        <tr><td>广东</td><td><span class="spec spec-s">标鳜（0.8~1.5斤）</span></td><td class="price"><b>24.5</b></td><td style="color:@@K@@;font-size:12px">→ 平</td></tr>
        <tr><td>广东</td><td><span class="spec spec-s">中鳜（1.5~2斤）</span></td><td class="price"><b>24</b></td><td style="color:@@G@@;font-size:12px">▼ 跌 0.5</td></tr>
        <tr><td>湖北</td><td><span class="spec spec-s">标鳜</span></td><td class="price"><b>24.5</b></td><td style="color:@@K@@;font-size:12px">→ 平</td></tr>
        <tr><td>安徽</td><td><span class="spec spec-s">标鳜</span></td><td class="price">25</td><td style="color:@@K@@;font-size:12px">→ 平</td></tr>
        <tr><td>江西</td><td><span class="spec spec-s">标鳜</span></td><td class="price">26</td><td style="color:@@K@@;font-size:12px">→ 平</td></tr>
        <tr><td>湖南</td><td><span class="spec spec-s">标鳜</span></td><td class="price"><b>25</b></td><td style="color:@@K@@;font-size:12px">→ 平</td></tr>
        <tr><td>江苏</td><td><span class="spec spec-s">标鳜</span></td><td class="price">26</td><td style="color:@@K@@;font-size:12px">→ 平</td></tr>
      </tbody></table>
      <div class="callout" style="margin-top:10px"><b>操作建议（原文）：</b>不建议盲目跟风恐慌出鱼，<b>优先挑规格整齐、品相好的鱼出塘</b>；存塘鱼未达上市规格的重点稳水质、控病害，做好<b>越冬前体质养护</b>——「减少损耗就是保住利润」。<br><b>口径提醒（重要）：</b>本卡为<b>塘口报价</b>（元/斤），与 MOA / 淡水渔业<b>批发价</b>（元/公斤）不同口径——江苏标鳜塘口 26 元/斤 vs 同日 MOA 凌家塘批发 57 元/公斤（28.5 元/斤），批发端溢价约 10%；<b>批发价不可直接当收购上限</b>，须先倒扣鳜鱼流通成本（约 3 元/斤）再按规格折算。</div>
      <div class="legend">来源：微信公众号「渔有福水产」2026-10-28 09:34《10 月 28 日鳜鱼塘口行情｜广东中鳜再跌 0.5 元斤，各地价差一览》· <a class="plink" href="https://mp.weixin.qq.com/s/1iFkF6nUCpzBRXh-YIUTug" target="_blank" rel="noopener">📄 阅读原文（鳜鱼塘口 10-28）</a> · 元/斤 · 塘口报价随行就市</div>
    </div>

"""

# ---------------------------------------------------------------- 卡片 2：全国渔业价格 10-28 早报
CARD_MINJIAN = """    <div class="card" style="margin-top:14px">
      <h3>📰 全国渔业价格 ·《全国水产品行情早报 2026-10-28》（发布 10-27 18:00 · 加州鲈生鱼周涨 1 元、黄鳝领涨 11.83%、金鲳再跌）</h3>
      <div class="csub">21 品种「普水稳、特水分化」：<b style="color:@@R@@">▲加州鲈佛山 9 两上 9.2~9.5 元/斤周涨 1 元 · ▲生鱼大规格 10.7 周涨 0.7 · ▲黄鳝全国批发 32.5 周涨 11.83%</b>；<b style="color:@@G@@">▼金鲳湛江 15.5 周跌 0.5</b>；河蟹兴化 38.39 止跌企稳、<b>存塘创五年新低</b>（同比 -11.2%）；普水草鱼/花鲢/白鲢批发走稳。<b>卖鱼思路：</b>加州鲈、生鱼大鱼爽市趁涨分批出；黄鳝货源偏紧可锁价；金鲳消费疲软顺价走、勿压塘；河蟹优质母蟹惜售等双 11；普水大规格够标趁稳出。</div>
      <div class="grid2"><div><h3 style="font-size:14px;margin:6px 0 8px">🐟 特水/虾蟹 · 塘口产地价（元/斤）</h3><table><thead><tr><th>品种</th><th>地区/规格</th><th>价格</th><th>周环比</th></tr></thead><tbody>
        <tr><td><span class="tag tag-lu">加州鲈</span></td><td><span class="spec spec-m">广东佛山 9两上</span></td><td class="price"><b>9.2~9.5</b></td><td style="color:@@R@@;font-size:12px">▲ 周涨 1 元</td></tr>
        <tr><td><span class="tag">生鱼</span></td><td><span class="spec spec-m">广东佛山 大规格3.5斤上</span></td><td class="price"><b>10.7</b></td><td style="color:@@R@@;font-size:12px">▲ 周涨 0.7</td></tr>
        <tr><td><span class="tag">黄鳝</span></td><td><span class="spec spec-m">全国批发 ≥100g</span></td><td class="price"><b>32.5</b></td><td style="color:@@R@@;font-size:12px">▲ 周涨 11.83%</td></tr>
        <tr><td><span class="tag">黄颡鱼</span></td><td><span class="spec spec-m">广东南海 平6两</span></td><td class="price">9.5</td><td style="color:@@R@@;font-size:12px">▲ 缺鱼涨 0.6</td></tr>
        <tr><td><span class="tag">鮰鱼</span></td><td><span class="spec spec-m">江苏 产地批发通货</span></td><td class="price">6.80</td><td style="color:@@K@@;font-size:12px">→ 平稳</td></tr>
        <tr><td><span class="tag">金鲳鱼</span></td><td><span class="spec spec-m">广东湛江 码头1-1.2斤新鱼</span></td><td class="price">15.5</td><td style="color:@@G@@;font-size:12px">▼ 周跌 0.5</td></tr>
        <tr><td><span class="tag">大黄鱼</span></td><td><span class="spec spec-m">福建霞浦 产地通货</span></td><td class="price"><b>26.15</b></td><td style="color:@@K@@;font-size:12px">产地稳·批发 19.06（-0.73%）</td></tr>
        <tr><td><span class="tag">河蟹</span></td><td><span class="spec spec-m">江苏兴化 产地均价</span></td><td class="price"><b>38.39</b></td><td style="color:@@K@@;font-size:12px">→ 止跌企稳·存塘五年新低</td></tr>
        <tr><td><span class="tag">南美白对虾</span></td><td><span class="spec spec-m">山东滨州 通货</span></td><td class="price">22.3</td><td style="color:@@K@@;font-size:12px">→ 平</td></tr>
        <tr><td><span class="tag">罗氏沼虾</span></td><td><span class="spec spec-m">江苏连云港 通货</span></td><td class="price">20.0</td><td style="color:@@K@@;font-size:12px">→ 平</td></tr>
        <tr><td><span class="tag">小龙虾</span></td><td><span class="spec spec-m">湖北潜江 通货</span></td><td class="price">11.0</td><td style="color:@@K@@;font-size:12px">→ 平</td></tr>
        <tr><td><span class="tag">梭子蟹</span></td><td><span class="spec spec-m">浙江桐乡 4-6两</span></td><td class="price">18.8</td><td style="color:@@K@@;font-size:12px">→ 平</td></tr>
        <tr><td><span class="tag">海参</span></td><td><span class="spec spec-m">山东威海 批发统货</span></td><td class="price">38.25</td><td style="color:@@K@@;font-size:12px">→ 平</td></tr>
      </tbody></table></div><div><h3 style="font-size:14px;margin:6px 0 8px">🐟 普水鱼 · 批发价（元/斤）</h3><table><thead><tr><th>品种</th><th>地区/规格</th><th>价格</th><th>备注</th></tr></thead><tbody>
        <tr><td>草鱼</td><td><span class="spec spec-m">武汉白沙洲 ≥1500g</span></td><td class="price">6.25</td><td style="color:@@K@@;font-size:12px">走稳</td></tr>
        <tr><td>鲫鱼</td><td><span class="spec spec-m">河南郑州 活500克上</span></td><td class="price">8.0</td><td style="color:@@K@@;font-size:12px">发改委监测</td></tr>
        <tr><td>鲤鱼</td><td><span class="spec spec-m">武汉白沙洲 ≥1500g</span></td><td class="price">5.1</td><td style="color:@@K@@;font-size:12px">走稳</td></tr>
        <tr><td>花鲢</td><td><span class="spec spec-m">武汉白沙洲 ≥1500g</span></td><td class="price">6.0</td><td style="color:@@K@@;font-size:12px">大规格走俏</td></tr>
        <tr><td>白鲢</td><td><span class="spec spec-m">武汉白沙洲 ≥1500g</span></td><td class="price">3.15</td><td style="color:@@K@@;font-size:12px">走稳</td></tr>
        <tr><td colspan="4" style="font-size:12px;color:@@K@@">泥鳅 山东济宁 22.0（平）· 青虾 / 金刚虾：当日暂无采集</td></tr>
      </tbody></table></div></div>
      <div class="callout" style="margin-top:10px"><b>口径提示（本卡三处易误读）：</b>① <b>加州鲈 9 两上 9.2~9.5 出自《特水鱼周报》第 38 期（10-26 塘头价）</b>，与《加州鲈周报》第 41 期（10-21）「佛山 1 斤上 10.5~11」是<b>规格 + 时间双重差异</b>、也与本期早报昨日「四川大邑基地 14.5」渠道不同——三者<b>不可直接相比</b>，同口径只能看方向（周涨 1 元一致）；② 黄鳝「全国批发 32.5」与 10-27 早报「武汉白沙洲 33.5」为不同市场口径（全国均价 vs 单市场），跌幅不代表武汉本地；③ 河蟹兴化 38.39 为<b>产地均价</b>（一亩田 10-26），与「38 规格普挑 22」分级口径不同，勿混用。<b>天气：</b>冷空气明日到货（广州降 1~2℃），福州昼夜温差拉大至 10℃+、夜晨 16℃；台风「烟花」超强级但原地少动、对我国海区无影响；霞浦沿海 28 日阵风 9~10 级，海上作业防风。</div>
      <div class="legend">来源：微信公众号「全国渔业价格」2026-10-27 18:00《生鱼加州鲈周涨 1 元！黄鳝批发周涨近 12%——金鲳再跌、河蟹存塘五年新低，双 11 前卖鱼抓窗口》· <a class="plink" href="https://mp.weixin.qq.com/s/q-qVBDQBduemizdiMImBMA" target="_blank" rel="noopener">📄 阅读原文（行情早报 10-28）</a> · 加州鲈/生鱼/黄颡鱼/金鲳为特水鱼周报第38期（10-26）、黄鳝为食品商务网全国批发均价（10-27）、梭子蟹/罗氏沼虾/泥鳅为惠农网（10-26/27）、河蟹为一亩田兴化产地均价（10-26）、鲫鱼为郑州市发改委（10-27）、草鲤花白鲢为白沙洲批发价（10-25）</div>
    </div>

"""

# ---------------------------------------------------------------- 卡片 3：渔飞鱼（渔知识指导）10-28 日报
CARD_YUFEIYU = """    <div class="card" style="margin-top:14px">
      <h3>🐟 渔飞鱼 ·《全国最新水产行情日报 2026-10-28》（加州鲈佛山全线回 10 元大关 · 罗非鱼工厂价直逼 4.5 · 黄颡鱼高位回调 6%）</h3>
      <div class="csub">今日整体平稳、局部回暖：<b style="color:@@R@@">加州鲈佛山 1 斤上 10.5~11 元/斤（周涨 1~1.3）全线回 10 元大关</b>；<b>罗非鱼加工厂抬价抢鱼</b>，北海 1-1.6 斤 4.45~4.5（三地最高、直逼 4.5 大关）；<b style="color:@@G@@">黄颡鱼全国批发 9.75 元/斤（较昨日 -6.02%）高位回调</b>；河蟹兴化 38.39 止跌企稳（存塘同比 -11.2%、五年新低、江苏销地需求指数回升至 194）；罗氏沼虾广西 33.35 领涨、南北价差近 10 元；草鲫塘口回暖（荆州草鱼 4-6 斤 5.8~6、射阳鲫鱼 1 斤 7、周内均涨 0.5）。</div>
      <div class="grid2"><div><h3 style="font-size:14px;margin:6px 0 8px"><span class="tag tag-lu">加州鲈</span> 四产区塘口价（元/斤）</h3><table><thead><tr><th>产区</th><th>规格</th><th>塘口价</th><th>周环比</th></tr></thead><tbody>
        <tr><td>广东佛山</td><td><span class="spec spec-s">1斤上</span></td><td class="price"><b>10.5~11</b></td><td style="color:@@R@@;font-size:12px">▲ 涨 1~1.3</td></tr>
        <tr><td>江苏吴江</td><td><span class="spec spec-s">9两上</span></td><td class="price"><b>10.5~11.5</b></td><td style="color:@@R@@;font-size:12px">▲ 涨</td></tr>
        <tr><td>四川成都</td><td><span class="spec spec-s">1斤上</span></td><td class="price">11~12</td><td style="color:@@K@@;font-size:12px">→ 平</td></tr>
        <tr><td>湖南华容</td><td><span class="spec spec-s">9两上</span></td><td class="price">10.5</td><td style="color:@@K@@;font-size:12px">→ 平</td></tr>
      </tbody></table>
      <div style="font-size:12px;color:@@K@@;margin-top:6px">四产区区间 10.5~12 元/斤，川粤价差 1 元+（西南需求支撑）；广东大鱼稀缺、外省低存塘见底，部分养户惜售。</div></div><div><h3 style="font-size:14px;margin:6px 0 8px">重点品种 · 塘口/批发价</h3><table><thead><tr><th>品种</th><th>地区/规格</th><th>价格</th><th>信号</th></tr></thead><tbody>
        <tr><td>黄颡鱼</td><td><span class="spec spec-s">全国批发 ≥150g</span></td><td class="price"><b>9.75</b></td><td style="color:@@G@@;font-size:12px">▼ -6.02% 高位回调</td></tr>
        <tr><td>罗非鱼</td><td><span class="spec spec-s">广西北海 1-1.6斤</span></td><td class="price"><b>4.45~4.5</b></td><td style="color:@@R@@;font-size:12px">▲ 加工厂抢鱼</td></tr>
        <tr><td>罗氏沼虾</td><td><span class="spec spec-s">江苏连云港 通货</span></td><td class="price">23.38</td><td style="color:@@R@@;font-size:12px">广西 33.35 领涨</td></tr>
        <tr><td>河蟹</td><td><span class="spec spec-s">江苏泰州 均价</span></td><td class="price"><b>38.39</b></td><td style="color:@@K@@;font-size:12px">→ 止跌企稳</td></tr>
        <tr><td>南美白对虾</td><td><span class="spec spec-s">江苏如东 20头</span></td><td class="price">18~19</td><td style="color:@@K@@;font-size:12px">产地均价 16.60</td></tr>
        <tr><td>草鱼</td><td><span class="spec spec-s">湖北荆州 4-6斤</span></td><td class="price">5.8~6.0</td><td style="color:@@R@@;font-size:12px">▲ 周内涨 0.2</td></tr>
      </tbody></table></div></div>
      <div class="callout" style="margin-top:10px"><b>政策（新增）：</b>湖南 10-20 发布「十五五」渔业发展支持政策（湘农联〔2026〕75 号），重点支持池塘升级改造与尾水综合治理、稻渔综合种养、工厂化循环水，<b>聚焦鳜鱼、鲈鱼、龟鳖、虾蟹打造优势产业集群</b>；2026 年度渔业油价补贴统筹——池塘改造每亩补助不超过 1500 元、单个项目最高 100 万元（湖北武汉按 2500 元/亩：中央 1500 + 市级 1000）。<br><b style="color:@@R@@">⚠️ 病害（本轮最需警惕）：</b>鳜鱼<b>传染性脾肾坏死病（ISKNV）</b>广东病原检测阳性率高、<b>10 天内死亡率可达 90%</b>；叠加罗非鱼链球菌病、草鱼出血病（水温 20~30℃）、淡水鱼细菌性败血症、鲫造血器官坏死病，降温降雨期水霉病/车轮虫/锚头鳋增多。<b>对宜兴官林基地：</b>价格窗口与病害高风险期叠加，优先保成活率，勿赌价。</div>
      <div class="legend">来源：微信公众号「渔知识指导」（渔飞鱼 · 董小月）2026-10-28 05:05《全国最新水产行情日报》· <a class="plink" href="https://mp.weixin.qq.com/s/r2EQTGBk2Ep2Nn1WetN93A" target="_blank" rel="noopener">📄 阅读原文（渔飞鱼日报 10-28）</a> · 塘口/产地参考价，因规格、地区、品质不同存在差异</div>
    </div>

"""


CARD_GUI, CARD_MINJIAN, CARD_YUFEIYU = map(colorize, (CARD_GUI, CARD_MINJIAN, CARD_YUFEIYU))


def insert_before(html: str, anchor: str, block: str, label: str) -> str:
    """在 anchor 所在的 <div class="card" 开头之前插入 block（anchor 需唯一）"""
    cnt = html.count(anchor)
    if cnt != 1:
        sys.exit(f"[ERR] 锚点「{label}」出现 {cnt} 次，需唯一：{anchor[:40]}")
    i = html.index(anchor)
    # 回退到该卡片起始行
    start = html.rindex('<div class="card"', 0, i)
    line_start = html.rindex("\n", 0, start) + 1
    return html[:line_start] + block + html[line_start:]


# 1) 渔有福 10-28 插在 10-27 鳜鱼塘口卡之前
s = insert_before(s, "<h3>🐟 10月27日 · 鳜鱼塘口价一览（全线持稳 · 病毒高发预警）</h3>",
                  CARD_GUI, "渔有福10-27卡")
# 2) 全国渔业价格 10-28 插在 10-27 早报卡之前
s = insert_before(s, "<h3>📰 全国渔业价格 ·《全国水产品行情早报 2026-10-27》",
                  CARD_MINJIAN, "全国渔业10-27早报卡")
# 3) 渔飞鱼 10-28 日报插在 10-27 日报卡之前
s = insert_before(s, "<h3>🐟 渔飞鱼 ·《全国最新水产行情日报 2026-10-27》",
                  CARD_YUFEIYU, "渔飞鱼10-27日报卡")

# ---------------------------------------------------------------- KPI 更新
# 鳜鱼·塘口价：25（10-18 腾氏全国均价）→ 26（10-28 渔有福 江苏/江西标鳜）
old_gui_sub = '<div class="sub" data-page-node-id="65b7fZVihju0pGkhkAg2XPs">全国均价 · 10-18 · 腾氏一周鱼价播报</div>'
new_gui_sub = '<div class="sub" data-page-node-id="65b7fZVihju0pGkhkAg2XPs">主产区标鳜 · 10-28 · 渔有福塘口（江苏/江西领跑）</div>'
assert old_gui_sub in s, "鳜鱼 KPI sub 未命中"
s = s.replace(old_gui_sub, new_gui_sub, 1)

old_gui_val = '<div class="val" data-page-node-id="h6Oavy5MoQgpSnSTILKX6r">25 <small data-page-node-id="cs1EaDsg0j1v2TKVm9TBFL">元/斤</small></div>'
new_gui_val = '<div class="val" data-page-node-id="h6Oavy5MoQgpSnSTILKX6r">26 <small data-page-node-id="cs1EaDsg0j1v2TKVm9TBFL">元/斤</small></div>'
assert old_gui_val in s, "鳜鱼 KPI val 未命中"
s = s.replace(old_gui_val, new_gui_val, 1)

old_gui_trend = '<div class="trend t-down" data-page-node-id="E3AKMrOidBfeXgTjKeCwDF">▼ 环比 -7.4%（27→25）· 同比 -14% · 广东 1.3斤 25（周跌 2）· 与水产前沿第36期佛山 3成中鳜 25 一致</div>'
new_gui_trend = ('<div class="trend t-flat" data-page-node-id="E3AKMrOidBfeXgTjKeCwDF">■ 江苏/江西 26 持稳（连续两日）· 湖北 24.5 / 湖南 25 / 安徽 25 持平 · '
                 f'<b style="color:{GREEN}">广东中鳜 24.5→24（跌 0.5）</b>、小鳜 18.5、标鳜 24.5 · 全表价差 8 元/斤</div>')
assert old_gui_trend in s, "鳜鱼 KPI trend 未命中"
s = s.replace(old_gui_trend, new_gui_trend, 1)

# 鲈鱼·塘口价：sub 更新到 10-28，trend 补四产区
old_lu_sub = '<div class="sub" data-page-node-id="wllgsawCjzdYKR5p4zBAY2s">江苏（吴江松陵/全省口径）· 10-18 · 腾氏一周鱼价播报</div>'
new_lu_sub = '<div class="sub" data-page-node-id="wllgsawCjzdYKR5p4zBAY2s">江苏吴江 9两上 · 10-28 · 渔飞鱼日报 + 加州鲈周报41期</div>'
assert old_lu_sub in s, "鲈鱼 KPI sub 未命中"
s = s.replace(old_lu_sub, new_lu_sub, 1)

old_lu_trend = '<div class="trend t-flat" data-page-node-id="uyUGRa8iC1GvFl0wsXnr6C">■ 江苏 10.5 持稳（老口存塘约 100 万斤、新口未集中出塘）· 佛山 1斤上 9（+0.2）· 浙江 10 / 四川新口 11.5</div>'
new_lu_trend = (f'<div class="trend t-up" data-page-node-id="uyUGRa8iC1GvFl0wsXnr6C">▲ <b>佛山 1 斤上 10.5~11（周涨 1~1.3，全线回 10 元大关）</b> · '
                '吴江 9两上 10.5~11.5 · 四川成都 11~12 · 湖南华容 10.5 · 四产区区间 10.5~12、川粤价差 1 元+</div>')
assert old_lu_trend in s, "鲈鱼 KPI trend 未命中"
s = s.replace(old_lu_trend, new_lu_trend, 1)

write = True
if len(sys.argv) > 1 and sys.argv[1] == "--check":
    write = False

if write:
    open(P, "w", encoding="utf-8").write(s)
    print(f"[OK] 已插入 3 张卡片并更新 2 张 KPI 卡 · {orig_len} → {len(s)} bytes (+{len(s) - orig_len})")
else:
    print(f"[check] 校验通过，将变化 {len(s) - orig_len} bytes")
