#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build_dashboard_v2.py — 宜兴官林鳜鱼鲈鱼「决策看板 v2」生成器

设计原则（与 v1 数据总览版互补、互不覆盖）：
  v1（/）     ：全量行情明细、多源溯源、Vue 单页
  v2（/v2/）  ：三角色决策视图，每角色独立「今日行动清单」，每日 09:15 由 Actions 重算

数据流：
  farm_weather_latest.json / Open-Meteo API  → 气象 + N 日预报
  fish_prices.json + fish_prices_history.csv → 农业农村部批发价（当日 + 历史序列）
  v2_manual_prices.json                      → 塘口价 / 病害 / 本地渠道（人工核校源）
  douyin_live_*.json                         → 社媒行情线索
  dashboard_v2_template.html                 → 版式模板
        ↓
  dashboard-v2/index.html

用法：
  python3 build_dashboard_v2.py                # 常规生成
  python3 build_dashboard_v2.py --bump patch   # 生成并升版本号
"""

import csv
import glob
import json
import os
import re
import sys
import urllib.request
from datetime import datetime, timedelta, timezone

WS = os.path.dirname(os.path.abspath(__file__))
TPL = os.path.join(WS, "dashboard_v2_template.html")
OUT_DIR = os.path.join(WS, "dashboard-v2")
OUT = os.path.join(OUT_DIR, "index.html")
MANUAL = os.path.join(WS, "v2_manual_prices.json")
WEATHER = os.path.join(WS, "farm_weather_latest.json")
VERFILE = os.path.join(WS, "dashboard_v2_version.json")
CST = timezone(timedelta(hours=8))

FORECAST_DAYS = 15

# 塘口 → 批发的流通成本（运输 + 损耗 + 档口毛利），用于收购价倒推。
# 鳜鱼货值高、流通环节加价空间大；鲈鱼加价空间小，扣除值用错会算出低于塘口价的荒谬上限。
GUI_MARGIN = 3.0
LU_MARGIN = 1.0

# 跨区调货不可行的远距离市场（运费吃掉价差，出现在价差推荐里会误导）
FAR_MARKETS = ("乌鲁木齐", "甘肃", "新疆", "拉萨", "西宁", "银川", "呼和浩特", "哈尔滨", "长春", "沈阳", "南宁", "海口", "昆明", "贵阳")

# WMO 天气码 → 中文 / emoji
WMO = {
    0: ("晴", "☀️"), 1: ("晴间多云", "🌤️"), 2: ("多云", "⛅"), 3: ("阴", "☁️"),
    45: ("雾", "🌫️"), 48: ("冻雾", "🌫️"),
    51: ("毛毛雨(弱)", "🌦️"), 53: ("毛毛雨", "🌦️"), 55: ("毛毛雨(强)", "🌦️"),
    56: ("冻雨(弱)", "🌧️"), 57: ("冻雨", "🌧️"),
    61: ("小雨", "🌧️"), 63: ("中雨", "🌧️"), 65: ("大雨", "🌧️"),
    66: ("冻雨(弱)", "🌧️"), 67: ("冻雨(强)", "🌧️"),
    71: ("小雪", "🌨️"), 73: ("中雪", "🌨️"), 75: ("大雪", "❄️"), 77: ("米雪", "🌨️"),
    80: ("阵雨(弱)", "🌦️"), 81: ("阵雨", "🌦️"), 82: ("强阵雨", "⛈️"),
    85: ("阵雪(弱)", "🌨️"), 86: ("阵雪(强)", "🌨️"),
    95: ("雷阵雨", "⛈️"), 96: ("雷阵雨伴冰雹", "⛈️"), 99: ("强雷阵雨伴冰雹", "⛈️"),
}


def wmo(code):
    return WMO.get(int(code or 0), ("—", "•"))


def weekday_cn(d):
    return "周" + "一二三四五六日"[d.weekday()]


def mmdd(d):
    return d.strftime("%m-%d")


# ----------------------------------------------------------------------------
# 数据加载
# ----------------------------------------------------------------------------
def load_json(path, default=None):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"[warn] 读取失败 {os.path.basename(path)}: {e}")
        return default if default is not None else {}


def fetch_weather(site):
    """优先实时抓取 Open-Meteo（15 日），失败则降级到本地 farm_weather_latest.json"""
    lat, lon = site.get("lat"), site.get("lon")
    url = (
        "https://api.open-meteo.com/v1/forecast"
        f"?latitude={lat}&longitude={lon}"
        "&current=temperature_2m,relative_humidity_2m,apparent_temperature,precipitation,"
        "weather_code,wind_speed_10m,wind_direction_10m,surface_pressure,visibility"
        "&daily=weather_code,temperature_2m_max,temperature_2m_min,precipitation_sum,"
        "precipitation_probability_max,wind_speed_10m_max,relative_humidity_2m_mean,sunrise,sunset"
        f"&timezone=Asia/Shanghai&forecast_days={FORECAST_DAYS}"
    )
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "fish-dashboard-v2/1.0"})
        with urllib.request.urlopen(req, timeout=20) as r:
            raw = json.loads(r.read().decode("utf-8"))
        cur = raw.get("current", {})
        dly = raw.get("daily", {})
        daily = []
        for i, d in enumerate(dly.get("time", [])):
            code = dly["weather_code"][i]
            daily.append({
                "date": d,
                "weather_code": code,
                "weather_text": wmo(code)[0],
                "weather_icon": wmo(code)[1],
                "temp_max_c": dly["temperature_2m_max"][i],
                "temp_min_c": dly["temperature_2m_min"][i],
                "precip_mm": dly["precipitation_sum"][i] or 0.0,
                "precip_prob_pct": dly["precipitation_probability_max"][i] or 0,
                "wind_max_kmh": dly["wind_speed_10m_max"][i] or 0.0,
                "humidity_pct": (dly.get("relative_humidity_2m_mean") or [None] * 99)[i],
                "sunrise": (dly.get("sunrise") or [None] * 99)[i],
                "sunset": (dly.get("sunset") or [None] * 99)[i],
            })
        cur_txt, cur_icon = wmo(cur.get("weather_code"))
        current = {
            "temperature_c": cur.get("temperature_2m"),
            "apparent_c": cur.get("apparent_temperature"),
            "humidity_pct": cur.get("relative_humidity_2m"),
            "visibility_km": round((cur.get("visibility") or 0) / 1000.0, 1),
            "wind_speed_kmh": cur.get("wind_speed_10m"),
            "wind_dir_deg": cur.get("wind_direction_10m"),
            "pressure_hpa": cur.get("surface_pressure"),
            "precipitation_mm": cur.get("precipitation") or 0.0,
            "weather_code": cur.get("weather_code"),
            "weather_text": cur_txt,
            "weather_icon": cur_icon,
            "time": cur.get("time"),
        }
        print(f"[ok] Open-Meteo 实时抓取成功，预报 {len(daily)} 天")
        return current, daily, raw.get("timezone", "Asia/Shanghai")
    except Exception as e:
        print(f"[warn] Open-Meteo 抓取失败（{e}），降级到本地 farm_weather_latest.json")
        w = load_json(WEATHER, {})
        return w.get("current", {}), w.get("daily", [])[:FORECAST_DAYS], "Asia/Shanghai"


def load_history():
    """返回 {品种组: {date: (全国均价元/斤, 江苏周边均价元/斤)}}"""
    path = os.path.join(WS, "fish_prices_history.csv")
    acc = {"鳜": {}, "鲈": {}}
    if not os.path.exists(path):
        return acc
    with open(path, encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            name = (row.get("品种") or "").strip()
            date = (row.get("日期") or "").strip()
            try:
                p = float(row.get("批发价_元公斤"))
            except Exception:
                continue
            if p <= 0:
                continue
            grp = "鳜" if "鳜" in name else ("鲈" if "鲈" in name else None)
            if not grp or not date:
                continue
            jin = p / 2.0
            slot = acc[grp].setdefault(date, {"all": [], "js": []})
            slot["all"].append(jin)
            if str(row.get("是否江苏周边")).strip().lower() == "true":
                slot["js"].append(jin)
    out = {}
    for grp, dates in acc.items():
        out[grp] = {}
        for d, v in sorted(dates.items()):
            # 全国均价改用「中位数」：MOA 覆盖全国含西北/东北销区市场，
            # 算术平均会被乌鲁木齐 145 元/公斤等极端高价严重拉高（实测可虚高 50%），
            # 中位数才能代表主销区真实水平；江苏及周边样本少且同质，用均值。
            nat = _median(v["all"]) if v["all"] else None
            js = sum(v["js"]) / len(v["js"]) if v["js"] else None
            out[grp][d] = (round(nat, 2) if nat else None, round(js, 2) if js else nat)
    return out


def load_today_prices():
    """当日各市场批发价 → {市场: {'鳜': val, '鲈': val}}（元/斤）"""
    mk = {}
    for row in load_json(os.path.join(WS, "fish_prices.json"), []) or []:
        name = (row.get("品种") or "").strip()
        try:
            jin = float(row.get("批发价_元公斤")) / 2.0
        except Exception:
            continue
        mkt = (row.get("市场") or "").strip()
        if not mkt:
            continue
        slot = mk.setdefault(mkt, {})
        if "鳜" in name:
            slot["鳜"] = round(jin, 2)
        elif "鲈" in name:
            prev = slot.get("鲈")
            slot["鲈"] = round(jin, 2) if prev is None else round((prev + jin) / 2, 2)
    return mk


def latest_douyin():
    files = sorted(glob.glob(os.path.join(WS, "douyin_live_*.json")))
    if not files:
        return None, []
    path = files[-1]
    data = load_json(path, [])
    date = os.path.basename(path).replace("douyin_live_", "").replace(".json", "")
    try:
        date = f"{date[:4]}-{date[4:6]}-{date[6:8]}"
    except Exception:
        pass
    items = sorted(data, key=lambda r: int(r.get("digg") or 0), reverse=True)[:3] if data else []
    return date, items


# ----------------------------------------------------------------------------
# 行情计算
# ----------------------------------------------------------------------------
def series_from_hist(hist, grp, n=30):
    data = hist.get(grp, {})
    dates = sorted(data.keys())[-n:]
    nat, js = [], []
    for d in dates:
        v = data[d]
        nat.append(v[0])
        js.append(v[1])
    return dates, nat, js


def pct_change(hist, grp):
    data = hist.get(grp, {})
    ds = [d for d in sorted(data.keys()) if data[d][0]]
    if len(ds) < 2:
        return None, None, None
    cur, prev = ds[-1], ds[-2]
    c, p = data[cur][0], data[prev][0]
    if not p:
        return None, None, None
    return round((c - p) / p * 100, 2), round(c, 2), round(p, 2)


def window_days(daily):
    """从今日起，连续满足 降水<1mm 且 最低温>=10℃ 的天数"""
    cnt = 0
    for d in daily[:7]:
        if (d.get("precip_mm") or 0) < 1.0 and (d.get("temp_min_c") or 0) >= 10:
            cnt += 1
        else:
            break
    return cnt


def pick_pond(manual, fish, region_kw=None, local=False):
    rows = manual.get("pond", {}).get(fish, {}).get("rows", [])
    if local:
        cands = [r for r in rows if r.get("local")]
    elif region_kw:
        cands = [r for r in rows if region_kw in r.get("region", "")]
    else:
        cands = rows
    return cands


# ----------------------------------------------------------------------------
# 行动清单规则引擎
# ----------------------------------------------------------------------------
def build_actions(ctx):
    """返回 {'boss':[...], 'tech':[...], 'buyer':[...]}，元素为 (level, text, why)"""
    daily = ctx["daily"]
    today = daily[0] if daily else {}
    cur = ctx["current"]
    manual = ctx["manual"]

    boss, tech, buyer = [], [], []

    # ---------- 通用量 ----------
    w = window_days(daily)
    window_txt = "、".join(mmdd(datetime.strptime(d["date"], "%Y-%m-%d")) for d in daily[:max(w, 1)]) or "—"
    rain_today = today.get("precip_mm") or 0
    tmax, tmin = today.get("temp_max_c"), today.get("temp_min_c")
    dif_t = (tmax - tmin) if (tmax is not None and tmin is not None) else 0
    next7_min = min((d.get("temp_min_c") or 99) for d in daily[:7]) if daily[:7] else None
    next7_min_day = None
    for d in daily[:7]:
        if (d.get("temp_min_c") or 99) == next7_min:
            next7_min_day = d["date"]
            break
    max_wind = max((d.get("wind_max_kmh") or 0) for d in daily[:3]) if daily[:3] else 0

    # 未来首个雨天
    first_rain = next((d for d in daily[1:6] if (d.get("precip_mm") or 0) >= 1.0), None)

    gui_chg = ctx["gui_chg"]
    lu_chg = ctx["lu_chg"]

    # ---------- 老板视图 ----------
    if w >= 3:
        boss.append(("danger",
                     f"出塘窗口开启：未来 <b>{w} 天</b>（{window_txt}）无有效降水、最低温不低于 10℃，<b>建议按批次出鱼</b>，先达标规格、后小鱼。",
                     f"依据：{FORECAST_DAYS} 日预报降水均 &lt;1mm，最低温 {min((d.get('temp_min_c') or 0) for d in daily[:w]):.0f}℃"))
    elif w == 1 or w == 2:
        boss.append(("warn",
                     f"出塘窗口偏短：仅今天起 <b>{w} 天</b> 适宜作业，建议集中在 {window_txt} 完成当日拉网计划，勿摊排到下周。",
                     f"依据：{FORECAST_DAYS} 日预报，第 {w+1} 天起出现降水或低温"))
    else:
        boss.append(("info",
                     "今日不宜拉网：当日有降水或低温，建议改为塘头巡检与出鱼前的停食、体检准备。",
                     f"依据：今日降水 {rain_today}mm、最低温 {tmin}℃"))

    if gui_chg and gui_chg[0] is not None:
        pct, c, p = gui_chg
        if pct <= -2:
            boss.append(("danger",
                         f"鳜鱼批发价环比 <b style=\"color:#dc2626\">跌 {abs(pct):.1f}%</b>（{p} → {c} 元/斤），跌势未止，<b>达标鱼不要压塘等价</b>，建议本周晴好期顺势走量。",
                         "依据：农业农村部统货批发价日度环比"))
        elif pct >= 2:
            boss.append(("ok",
                         f"鳜鱼批发价环比 <b>涨 {pct:.1f}%</b>（{p} → {c} 元/斤），可分批走鱼、留一部分搏下周行情。",
                         "依据：农业农村部统货批发价日度环比"))
        else:
            boss.append(("ok",
                         f"鳜鱼批发价环比基本持平（{pct:+.1f}%，{c} 元/斤），行情进入盘整，按批次节奏正常出鱼即可。",
                         "依据：农业农村部统货批发价日度环比"))

    if lu_chg and lu_chg[0] is not None:
        pct, c, p = lu_chg
        arrow = "涨" if pct > 0 else ("跌" if pct < 0 else "持平")
        level = "ok" if pct >= 2 else ("danger" if pct <= -2 else "info")
        boss.append((level,
                     f"鲈鱼批发价环比 <b>{arrow} {abs(pct):.1f}%</b>（{c} 元/斤）。大鱼紧缺是当前涨价主因，<b>建议优先出 1 斤以上规格</b>，小鱼择机并塘继续养。",
                     f"依据：农业农村部统货批发价 + 水产前沿周报「大鱼爽市」"))

    if next7_min is not None and next7_min < 10:
        boss.append(("warn",
                     f"冷空气预警：{mmdd(datetime.strptime(next7_min_day, '%Y-%m-%d'))} 最低温降至 <b>{next7_min:.0f}℃</b>，<b>把出塘与拉网排在寒潮之前</b>，避免低温期操作造成机械损伤与水霉感染。",
                     f"依据：{FORECAST_DAYS} 日预报最低温序列"))

    dis = manual.get("disease", {})
    if dis.get("level") == "high":
        names = "、".join(d["name"] for d in dis.get("items", []) if d.get("level") == "high")
        boss.append(("danger",
                     f"病害高发期（{dis.get('period','')}）：{names} <b>无特效药、死亡率高</b>。当前策略应是<b>保成活率优先于赌价格</b>，减少一次不必要的大量换水与转塘。",
                     "依据：公众号行情源病害提示 + 季节性流行规律"))

    boss.append(("info",
                 f"本周排产口径：鳜鱼出塘参考 <b>{ctx['gui_pond_txt']}</b>、鲈鱼 <b>{ctx['lu_pond_txt']}</b>；盈亏试算在下方计算器按本场实际成本重算后，再决定出鱼批次顺序。",
                 "依据：塘口价快照 + 农业农村部批发价"))

    # ---------- 技术员视图 ----------
    mean_t = ((tmax + tmin) / 2) if (tmax is not None and tmin is not None) else None
    if mean_t is not None:
        if mean_t >= 20:
            feed = "按常规量投喂（日投饵率约 2.5%~3%），早晚两餐"
        elif mean_t >= 15:
            feed = "日投饵率降至 2% 左右，中午前后集中投喂"
        elif mean_t >= 10:
            feed = "日投饵率 1%~1.5%，每日 1 餐、中午晴暖时进行"
        else:
            feed = "水温过低，停料或隔日少量投喂"
        tech.append(("info",
                     f"今日投喂：气温 {tmin:.0f}~{tmax:.0f}℃（{today.get('weather_text','')}），<b>{feed}</b>。",
                     f"依据：日均温 {mean_t:.1f}℃ 对应投饵率区间"))

    if rain_today >= 1.0 or (today.get("precip_prob_pct") or 0) >= 60:
        tech.append(("warn",
                     f"今日有降水（{rain_today}mm / 概率 {today.get('precip_prob_pct')}%）：<b>减料 50%</b>，雨停后泼 EM 菌 + 底改，夜间提前开增氧机防缺氧。",
                     "依据：当日降水量与降水概率"))
    elif first_rain:
        tech.append(("info",
                     f"未来降水：{mmdd(datetime.strptime(first_rain['date'], '%Y-%m-%d'))} 有 {first_rain.get('precip_mm')}mm 降雨，<b>提前一天备好底改与增氧片</b>，雨前适当减料。",
                     f"依据：{FORECAST_DAYS} 日预报"))
    else:
        tech.append(("ok",
                     "未来 5 日无明显降水，藻相相对稳定，按常规调水即可，注意补充磷肥维持藻种多样性。",
                     f"依据：{FORECAST_DAYS} 日预报"))

    tech.append(("info",
                 f"今日溶氧管理：{'阴雨/多云，光合作用弱，建议中午开机 2 小时破分层，并备好化学增氧剂' if today.get('weather_code', 0) in (3, 2) or (today.get('precip_prob_pct') or 0) > 40 else '天气晴好、藻类产氧充足，常规夜间增氧即可，凌晨巡塘一次'}。",
                 f"依据：今日天气 {today.get('weather_text','')} · 湿度 {cur.get('humidity_pct','—')}%"))

    if dif_t >= 9:
        tech.append(("warn",
                     f"昼夜温差达 <b>{dif_t:.0f}℃</b>（{tmin:.0f}~{tmax:.0f}℃），鱼体应激加大、易泛塘：<b>保持高水位、减少换水量</b>，拌料加 VC + 免疫多糖。",
                     "依据：当日最高/最低温差"))

    if next7_min is not None and next7_min < 12:
        tech.append(("warn",
                     f"越冬准备启动：{mmdd(datetime.strptime(next7_min_day, '%Y-%m-%d'))} 起最低温 {next7_min:.0f}℃。本周<b>逐步加深水位至 2.5 m 以上保温</b>，水温 15℃ 以上完成抽样体检，排查寄生虫与溃疡。",
                     f"依据：{FORECAST_DAYS} 日最低温序列 + 越冬前防控规范"))

    if dis.get("actions"):
        tech.append(("info",
                     f"本周病害巡塘清单：{dis['actions'][0]}、{dis['actions'][1]}、{dis['actions'][2]}。发现离群独游、吃料下滑个体立即隔离镜检。",
                     f"依据：{dis.get('period','')}病害防控要点"))

    if max_wind >= 25:
        tech.append(("warn",
                     f"未来 3 日最大风速达 <b>{max_wind:.0f} km/h</b>：大风搅动底泥、易引起泛塘，<b>提前加固增氧设施、检查电路</b>，风力最大时段暂停投喂。",
                     f"依据：{FORECAST_DAYS} 日最大风速"))

    tech.append(("ok",
                 "数据边界提醒：本页水质提示为<b>气象推导值、非实测探头数据</b>。pH / 氨氮 / 亚硝酸盐务必以本场试剂盒或在线探头读数为准。",
                 "依据：数据源口径说明"))

    # ---------- 采购员视图 ----------
    gui_ws = ctx["gui_ws_js"] or ctx["gui_ws_nat"]
    lu_ws = ctx["lu_ws_js"] or ctx["lu_ws_nat"]
    if gui_ws:
        cap = gui_ws - GUI_MARGIN
        buyer.append(("danger" if (gui_chg and gui_chg[0] is not None and gui_chg[0] <= -2) else "info",
                      f"鳜鱼收购上限：周边市场批发均价 <b>{gui_ws:.1f}</b> 元/斤，扣除流通成本 {GUI_MARGIN:g} 元/斤后，<b>建议收购价不高于 {cap:.1f} 元/斤</b>，超过则该批次无利可图。",
                      "依据：农业农村部周边市场批发均价倒推（运输 + 损耗 + 档口毛利）"))
    if lu_ws:
        cap = lu_ws - LU_MARGIN
        buyer.append(("info",
                      f"鲈鱼收购上限：周边批发均价 <b>{lu_ws:.1f}</b> 元/斤，扣除流通成本 {LU_MARGIN:g} 元/斤后，<b>建议控制在 {cap:.1f} 元/斤以内</b>；当前 1 斤以上大规格偏紧，可在上限内适度让价抢货。",
                      "依据：农业农村部周边市场批发均价 + 大鱼紧缺行情"))
    else:
        buyer.append(("info",
                      "鲈鱼周边批发数据今日缺位，收购前请以当日实际询价为准，勿沿用隔日价。",
                      "依据：数据源新鲜度检查"))

    if ctx.get("arb"):
        nm, hi, lo, spread = ctx["arb"]
        buyer.append(("warn",
                      f"跨区价差：今日最高价市场为 <b>{nm}</b>（鳜鱼 {hi:.1f} 元/斤），与最低价市场价差 <b>{spread:.1f} 元/斤</b>。若能承担运费，<b>优先向高价市场调货</b>，单趟毛利空间明显。",
                      "依据：农业农村部当日分市场批发价对比"))

    buyer.append(("info",
                  "收鱼规格建议：优先收 <b>标鳜以上（0.8~1.5 斤）与 9 两以上加州鲈</b>。小鳜（0.8 斤以下）与 3 成中鳜当前走货慢、常在产区打死包，压库风险高。",
                  "依据：水产前沿周报第38期「偏小规格难走」+ 塘口分规格报价"))

    if rain_today >= 1.0 or (today.get("precip_prob_pct") or 0) >= 60:
        buyer.append(("warn",
                      f"今日装车注意：{today.get('weather_text','')} / 降水 {rain_today}mm。<b>运输车做好防雨、加盖篷布</b>，到货后缓水 15 分钟再卸，降低应激掉秤。",
                      "依据：当日降水预报"))
    else:
        buyer.append(("ok",
                      f"今日天气 {today.get('weather_text','')}、湿度 {cur.get('humidity_pct','—')}%，运输条件良好，可按常规时段装车；仍建议避开正午高温，选择早晚运输降低死亡率。",
                      "依据：实时气象"))

    if dis.get("level") == "high":
        buyer.append(("danger",
                      "收鱼体检红线：当前 ISKNV / 蛙虹彩病毒高发。<b>拒收体色发黑、鳍基红肿、离群独游个体</b>，可疑批次要镜检并单独暂养观察 24 小时再混塘。",
                      "依据：病害快照 + 防控要点"))

    return {"boss": boss[:6], "tech": tech[:6], "buyer": buyer[:6]}


# ----------------------------------------------------------------------------
# 渲染
# ----------------------------------------------------------------------------
def esc(s):
    return (str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;"))


def render_actions(items, title, hint):
    lis = []
    for level, text, why in items:
        badge = {"danger": "必办", "warn": "关注", "ok": "正常", "info": "提示"}[level]
        cls = {"danger": "badge-danger", "warn": "badge-warn", "ok": "badge-ok", "info": "badge-info"}[level]
        lis.append(f'<li><span class="badge {cls}">{badge}</span>{text}<span class="why">↳ {why}</span></li>')
    return (f'<div class="action-list">\n<h3>📋 {title}</h3>\n'
            f'<div class="alist-sub">{hint}</div>\n<ol>\n' + "\n".join(lis) + "\n</ol>\n</div>")


def block_replace(html, start, end, body):
    pattern = re.compile(re.escape(start) + r".*?" + re.escape(end), re.S)
    return pattern.sub(start + "\n" + body + "\n" + end, html, count=1)


def main():
    # 版本
    ver = load_json(VERFILE, {"version": "v2.0.14", "date": "2026-10-27", "history": []})
    if "--bump" in sys.argv:
        i = sys.argv.index("--bump")
        level = sys.argv[i + 1] if len(sys.argv) > i + 1 else "patch"
        nums = [int(x) for x in re.findall(r"\d+", ver["version"])]
        if level == "minor":
            nums = [nums[0], nums[1] + 1, 0]
        elif level == "major":
            nums = [nums[0] + 1, 0, 0]
        else:
            nums = [nums[0], nums[1], nums[2] + 1]
        ver["version"] = ".".join(str(x) for x in nums)

    manual = load_json(MANUAL, {})
    base = load_json(WEATHER, {})
    site = base.get("site", {})
    current, daily, tz = fetch_weather(site)
    if not daily:
        print("[error] 无任何气象数据，终止生成")
        sys.exit(1)
    daily = daily[:FORECAST_DAYS]

    hist = load_history()
    markets = load_today_prices()
    dy_date, dy_items = latest_douyin()

    now = datetime.now(CST)
    updated_human = now.strftime("%Y-%m-%d %H:%M")
    updated_iso = now.isoformat()

    gui_dates, gui_nat, gui_js = series_from_hist(hist, "鳜")
    lu_dates, lu_nat, lu_js = series_from_hist(hist, "鲈")
    gui_chg = pct_change(hist, "鳜")
    lu_chg = pct_change(hist, "鲈")
    all_d = sorted(set(list(hist.get("鳜", {}).keys()) + list(hist.get("鲈", {}).keys())))
    today_date = all_d[-1] if all_d else now.strftime("%Y-%m-%d")

    gui_ws_nat = gui_nat[-1] if gui_nat else None
    gui_ws_js = gui_js[-1] if gui_js and gui_js[-1] else gui_ws_nat
    lu_ws_nat = lu_nat[-1] if lu_nat else None
    lu_ws_js = lu_js[-1] if lu_js and lu_js[-1] else lu_ws_nat

    # 跨市场价差
    arb = None
    gmap = [(m, v["鳜"]) for m, v in markets.items()
            if v.get("鳜") and not any(k in m for k in FAR_MARKETS)]
    if len(gmap) >= 2:
        gmap.sort(key=lambda x: -x[1])
        hi_m, hi = gmap[0]
        lo = gmap[-1][1]
        if hi - lo >= 5:
            arb = (_short_m(hi_m), hi, lo, hi - lo)

    # 塘口价
    js_gui = pick_pond(manual, "鳜鱼", region_kw="江苏")
    gui_pond_val = js_gui[0]["price"] if js_gui else None
    gui_pond_date = manual.get("pond", {}).get("鳜鱼", {}).get("date", "—")
    lu_local = pick_pond(manual, "加州鲈", local=True)
    if lu_local:
        vals = [r["price"] for r in lu_local]
        lu_lo, lu_hi = min(vals), max(vals)
        lu_pond_val = (lu_lo + lu_hi) / 2
        lu_pond_txt = f"{lu_lo:g}~{lu_hi:g}"
    else:
        lu_pond_val, lu_pond_txt = None, "—"
    lu_pond_date = manual.get("pond", {}).get("加州鲈", {}).get("date", "—")

    def tag_cls(pct):
        if pct is None:
            return "tag-flat", "数据缺失"
        if pct >= 2:
            return "tag-up", f"环比 +{pct:.1f}%"
        if pct <= -2:
            return "tag-down", f"环比 {pct:.1f}%"
        return "tag-flat", f"环比 {pct:+.1f}%"

    gui_ws_cls, gui_ws_txt = tag_cls(gui_chg[0] if gui_chg else None)
    lu_ws_cls, lu_ws_txt = tag_cls(lu_chg[0] if lu_chg else None)
    gp = manual.get("pond", {}).get("鳜鱼", {})
    lp = manual.get("pond", {}).get("加州鲈", {})

    ctx = dict(daily=daily, current=current, manual=manual,
               gui_chg=gui_chg, lu_chg=lu_chg,
               gui_ws_nat=gui_ws_nat, gui_ws_js=gui_ws_js, lu_ws_nat=lu_ws_nat, lu_ws_js=lu_ws_js,
               gui_pond_txt=f"{gui_pond_val:g} 元/斤" if gui_pond_val else "—",
               lu_pond_txt=f"{lu_pond_txt} 元/斤" if lu_pond_val else "—",
               arb=arb)
    acts = build_actions(ctx)

    # ---------------- 各区块 HTML ----------------
    today = daily[0]
    cur = current
    vis = cur.get("visibility_km")
    wind_dir = cur.get("wind_dir_text") or _dir_text(cur.get("wind_dir_deg"))
    weather_cards = "".join([
        _wcard("🌡️", "当前气温", f"{cur.get('temperature_c', '—')}℃",
               f"体感 {cur.get('apparent_c', '—')}℃ · 今日 {today.get('temp_min_c')}~{today.get('temp_max_c')}℃"),
        _wcard("💨", "风速/风向", f"{wind_dir}{_beaufort(cur.get('wind_speed_kmh'))}级",
               f"约 {cur.get('wind_speed_kmh', '—')} km/h"),
        _wcard("👁️", "能见度", f"{vis} km" if vis else "—",
               "低于 5km 建议延迟装车出发" if (vis or 99) < 5 else "运输视线良好"),
        _wcard("💧", "相对湿度", f"{cur.get('humidity_pct', '—')}%",
               "高湿，注意水体溶氧与病害" if (cur.get("humidity_pct") or 0) >= 85 else "湿度正常"),
        _wcard("🌧️", "降水量", f"{cur.get('precipitation_mm', 0)} mm",
               f"今日累计预报 {today.get('precip_mm')}mm / 概率 {today.get('precip_prob_pct')}%"),
        _wcard("🔵", "气压", f"{cur.get('pressure_hpa', '—')} hPa",
               "气压平稳" if cur.get("pressure_hpa") else "—"),
        _wcard(f"{today.get('weather_icon','•')}", "今日天气", f"{today.get('weather_text','—')}",
               f"日落前后温差 {(today.get('temp_max_c') or 0) - (today.get('temp_min_c') or 0):.0f}℃"),
        _wcard("🌾", "24h 低温预警", f"{min((d.get('temp_min_c') or 99) for d in daily[:3]):.0f}℃",
               f"未来 3 日最低温，低于 10℃ 需保温"),
    ])

    water_cards = []
    first_rain = next((d for d in daily[1:8] if (d.get("precip_mm") or 0) >= 1.0), None)
    if first_rain:
        water_cards.append(_water(
            f"🌧️ {mmdd(datetime.strptime(first_rain['date'], '%Y-%m-%d'))} 降水 {first_rain.get('precip_mm')}mm",
            "<strong>风险：</strong>pH 骤降、亚硝酸盐升高、底泥有害物质释放<br>"
            "<strong>应对：</strong>雨前减料 50%；雨后泼 EM 菌 + 底改；中午开增氧机搅动水层"))
    n7min = min((d.get("temp_min_c") or 99) for d in daily[:7])
    n7day = next(d["date"] for d in daily[:7] if (d.get("temp_min_c") or 99) == n7min)
    water_cards.append(_water(
        f"❄️ {mmdd(datetime.strptime(n7day, '%Y-%m-%d'))} 最低 {n7min:.0f}℃",
        "<strong>风险：</strong>水温骤降、强应激、诱发水霉病与越冬综合征<br>"
        "<strong>应对：</strong>提前加深水位保温；寒潮期停喂；避免拉网操作"))
    sunny = sum(1 for d in daily[:7] if (d.get("precip_mm") or 0) < 1)
    water_cards.append(_water(
        f"☀️ 未来 7 日 {sunny} 天无有效降水",
        "<strong>风险：</strong>氨氮易累积、水体分层、溶氧昼夜波动大<br>"
        "<strong>应对：</strong>中午曝气 2 小时破分层；控制投喂防残饵；择晴好日出塘"))
    water_html = "".join(water_cards)

    dis = manual.get("disease", {})
    dis_items = dis.get("items", [])
    high = [d for d in dis_items if d.get("level") == "high"]
    mid = [d for d in dis_items if d.get("level") == "mid"]
    upcoming = [d for d in dis_items if d.get("level") == "upcoming"]
    disease_cards = ""
    if high:
        disease_cards += _alert("danger", "🦠 当前高危（重点盯防）",
                                "".join(f"• {d['name']}（{d['species']}）<br>" for d in high[:3]),
                                f"防控：{dis.get('actions', ['—'])[0]}")
    if mid:
        disease_cards += _alert("warn", "🐟 常规流行病害",
                                "".join(f"• {d['name']}<br>" for d in mid[:3]),
                                "按月流行规律：10-11 月为发病高峰")
    if upcoming:
        disease_cards += _alert("info", "❄️ 即将进入（提前部署）",
                                "".join(f"• {d['name']}<br>" for d in upcoming[:2]),
                                "低温 + 拉网操作是主要诱因")
    if dis.get("actions"):
        disease_cards += _alert("info", "📋 本周执行清单",
                                "".join(f"{i+1}. {a}<br>" for i, a in enumerate(dis["actions"][:4])),
                                "工具网具务必消毒，防交叉感染")

    rows = []
    today_str = today["date"]
    for d in daily:
        dt = datetime.strptime(d["date"], "%Y-%m-%d")
        tmin, tmax = d.get("temp_min_c"), d.get("temp_max_c")
        precip = d.get("precip_mm") or 0
        prob = d.get("precip_prob_pct") or 0
        wind = d.get("wind_max_kmh") or 0
        hum = d.get("humidity_pct")
        # 塘头提示
        if precip >= 8:
            tip, cls = f"<strong>中到大雨 {precip}mm：全天减料 50%、增氧不停</strong>", "warn-row"
        elif precip >= 1:
            tip, cls = "有降雨：减料、雨后必做底改与解毒", "warn-row"
        elif tmin is not None and tmin < 10:
            tip, cls = f"<strong>最低 {tmin:.0f}℃：防寒应激、停拉网</strong>", "danger-row"
        elif precip < 1 and (tmin or 0) >= 10:
            tip, cls = "晴好：适宜拉网出塘 / 正常投喂", ""
        else:
            tip, cls = "常规管理，注意夜间增氧", ""
        if d["date"] == today_str:
            cls = (cls + " today").strip()
        rows.append(
            f'<tr class="{cls}"><td>{mmdd(dt)} {weekday_cn(dt)}{"（今天）" if d["date"] == today_str else ""}</td>'
            f'<td>{d.get("weather_icon","")} {d.get("weather_text","")}</td>'
            f'<td>{_fmt_t(tmin)}~{_fmt_t(tmax)}</td>'
            f'<td>{wind:.0f} km/h</td><td>{hum if hum is not None else "—"}</td>'
            f'<td>{prob}%</td><td>{precip:g}</td><td>{tip}</td></tr>')
    forecast_rows = "\n".join(rows)

    # 采购：出塘 vs 批发
    prows = []
    guirows = gp.get("rows", [])
    if guirows:
        small = next((r for r in guirows if "小鳜" in r.get("spec", "")), None)
        std = next((r for r in guirows if r.get("region") == "江苏"), None)
        ws_gui = gui_ws_js or gui_ws_nat or 0
        if small:
            prows.append(_prow("🐟 鳜鱼", esc(small["spec"]), f"{small['price']:g}", "—", "",
                               gp.get("date", "—"), esc(gp.get("source", ""))))
        if std:
            prows.append(_prow("🐟 鳜鱼", f"标鳜（江苏·本地参考）", f"{std['price']:g}", f"{ws_gui:.1f}",
                               f"{ws_gui - std['price']:+.1f}（{(ws_gui / std['price'] - 1) * 100:.0f}%）",
                               gp.get("date", "—"), esc(gp.get("source", ""))))
    wk = gp.get("weekly", {})
    if wk.get("rows"):
        r0 = wk["rows"][0]
        prows.append(_prow("🐟 鳜鱼", f"{r0['region']} {esc(r0['spec'])}（周报）", r0["curr"], "—",
                           f"较上周 {r0['prev']}", wk.get("date", "—"), esc(wk.get("source", ""))))
    lurows = lp.get("rows", [])
    if lurows:
        local_rows = [r for r in lurows if r.get("local")]
        for r in (local_rows or lurows)[:2]:
            ws_lu = lu_ws_js or lu_ws_nat or 0
            try:
                pv = float(r["price"])
                gap = f"{ws_lu - pv:+.1f}（{(ws_lu / pv - 1) * 100:.0f}%）" if pv else ""
            except Exception:
                gap = ""
            prows.append(_prow("🐟 加州鲈", f"{esc(r['region'])} · {esc(r['spec'])}", f"{r['price']:g}",
                               f"{ws_lu:.1f}" if ws_lu else "—", gap, lp.get("date", "—"), esc(lp.get("source", ""))))
    lw = manual.get("local_wholesale", {})
    for r in lw.get("rows", [])[:2]:
        prows.append(_prow("🏪 本地渠道", esc(r["name"]), "—", esc(r["price"]), esc(r.get("note", "")),
                           lw.get("date", "—"), esc(lw.get("source", ""))))
    purchase_rows = "\n".join(prows) or '<tr><td colspan="7">今日无可用报价</td></tr>'

    # 采购：今日收鱼建议卡
    recv = []
    if gui_pond_val and gui_ws_js:
        recv.append(_recv("🐟 鳜鱼（江苏标鳜）",
                          f"塘口收货价参考 {gui_pond_val:g} 元/斤；江苏及周边批发 {gui_ws_js:.1f} 元/斤，扣除流通成本后收购上限约 {gui_ws_js - GUI_MARGIN:.1f} 元/斤。当前环比 {'跌势未止，宜快进快出' if (gui_chg and gui_chg[0] is not None and gui_chg[0] <= -2) else '平稳/上行，可正常收货'}。",
                          f"{gui_pond_val:g} 元/斤"))
    if lu_pond_val and lu_ws_js:
        recv.append(_recv("🐟 加州鲈（环太湖）",
                          f"9 两以上规格优先，参考 {lu_pond_txt} 元/斤；批发端 {lu_ws_js:.1f} 元/斤，收购上限约 {lu_ws_js - LU_MARGIN:.1f} 元/斤。大鱼紧缺，可在上限内适度让价抢货。",
                          f"{lu_pond_txt} 元/斤"))
    recv.append(_recv("🚫 谨慎收货规格",
                      "小鳜（0.8 斤以下）与产区偏小规格当前走货慢、易打死包贱卖；新鱼集中上市期也不宜大量压货。收鱼前务必体检：体色发黑、鳍基红肿、离群独游个体拒收。",
                      "低优先级"))
    recv_cards = "".join(recv)

    # 行情线索表
    posts = []
    if wk.get("summary"):
        posts.append(_post(esc(wk.get("source", "")), wk.get("date", "—"), esc(wk["summary"]),
                           f'<a class="plink" href="{esc(wk.get("source_url",""))}" target="_blank" rel="noopener">水产前沿周报38期</a>'))
    if gp.get("headline"):
        posts.append(_post(esc(gp.get("source", "")), gp.get("date", "—"), esc(gp["headline"]),
                           f'<a class="plink" href="{esc(gp.get("source_url",""))}" target="_blank" rel="noopener">渔有福10-27</a>'))
    if lp.get("headline"):
        posts.append(_post(esc(lp.get("source", ""))[:28], lp.get("date", "—"), esc(lp["headline"]),
                           f'<a class="plink" href="{esc(lp.get("source_url",""))}" target="_blank" rel="noopener">腾氏㊷</a>'))
    if dis.get("items"):
        posts.append(_post("病害动态", dis.get("period", "—"),
                           esc("、".join(d["name"] for d in high[:2]) + " 高发"), "公众号行情源核校"))
    if dy_items:
        for it in dy_items:
            posts.append(_post(f'抖音 · {esc((it.get("author") or "")[:10])}', dy_date,
                               esc((it.get("title") or "")[:40]), f'点赞 {it.get("digg", 0)}'))
    post_rows = "\n".join(posts[:8])

    # 老板今日关注卡
    focus = []
    if gui_chg and gui_chg[0] is not None:
        pct, c, p = gui_chg
        focus.append(_alert("danger" if pct <= -2 else "ok", "📉 鳜鱼批发价",
                            f"今日全国中位数 <strong>{c} 元/斤</strong>（较上一交易日 {p} 元/斤，<b>{pct:+.1f}%</b>）",
                            "跌势中建议达标鱼顺势出塘，勿压塘等价"))
    if lu_chg and lu_chg[0] is not None:
        pct, c, p = lu_chg
        focus.append(_alert("ok" if pct >= 0 else "danger", "📈 鲈鱼批发价",
                            f"今日全国中位数 <strong>{c} 元/斤</strong>（{pct:+.1f}%），大规格紧缺是当前涨价主因",
                            "优先出 1 斤以上规格"))
    w = window_days(daily)
    focus.append(_alert("ok" if w >= 3 else "warn", "🪟 出塘窗口",
                        f"今日起连续适宜作业 <strong>{w} 天</strong>，{'窗口充裕，可分批安排' if w >= 3 else '窗口偏紧，建议集中作业'}",
                        f"未来 7 日最低温 {n7min:.0f}℃，{'需防寒' if n7min < 10 else '温度适宜'}"))
    focus.append(_alert("danger" if dis.get("level") == "high" else "info", "🦠 病害风险",
                        f"{dis.get('period','—')}：<strong>{'、'.join(d['name'] for d in high[:2]) or '常规防控'}</strong> 高发",
                        "保成活率优先于赌价格"))
    focus_cards = "".join(focus)

    # 变更日志
    hist_rows = [f'<div class="changelog-item"><span class="ver">{esc(ver["version"])} · {esc(now.strftime("%Y-%m-%d"))}</span> · 决策版看板：三角色视图 + 每日行动清单规则引擎 + {FORECAST_DAYS} 日预报重算</div>']
    for h in ver.get("history", [])[:6]:
        hist_rows.append(f'<div class="changelog-item"><span class="ver">{esc(h.get("version",""))} · {esc(h.get("date",""))}</span> · {esc(h.get("note",""))}</div>')
    changelog = "\n".join(hist_rows)

    # ---------------- 模板替换 ----------------
    html = open(TPL, encoding="utf-8").read()
    repl = {
        "{{VERSION}}": ver["version"],
        "{{UPDATED_DATE}}": now.strftime("%Y-%m-%d"),
        "{{UPDATED_HUMAN}}": updated_human,
        "{{UPDATED_ISO}}": updated_iso,
        "{{SITE_NAME}}": esc(site.get("name", "宜兴官林养殖基地")),
        "{{SITE_ADDR}}": esc(site.get("address", "")),
        "{{LAT}}": str(site.get("lat", 31.557387)),
        "{{LON}}": str(site.get("lon", 119.723966)),
        "{{COORD_SOURCE}}": esc(site.get("coord_source", "高德地理编码")),
        "{{FORECAST_DAYS}}": str(FORECAST_DAYS),
        "{{FORECAST_ROWS}}": forecast_rows,
        "{{WEATHER_CARDS}}": weather_cards,
        "{{WATER_CARDS}}": water_html,
        "{{DISEASE_CARDS}}": disease_cards,
        "{{DISEASE_PERIOD}}": esc(dis.get("period", "当月")),
        "{{BOSS_FOCUS_CARDS}}": focus_cards,
        "{{PURCHASE_ROWS}}": purchase_rows,
        "{{RECV_CARDS}}": recv_cards,
        "{{POST_ROWS}}": post_rows,
        "{{GUI_POND_PRICE}}": f"{gui_pond_val:g}" if gui_pond_val else "—",
        "{{GUI_POND_SUB}}": esc(f"江苏标鳜 · {gui_pond_date} · {gp.get('source','')}").replace("amp;", ""),
        "{{GUI_POND_TAG_CLASS}}": "tag-flat",
        "{{GUI_POND_TAG_TEXT}}": esc((gp.get("headline") or "")[:26]),
        "{{GUI_WS_PRICE}}": f"{gui_ws_nat:.1f}" if gui_ws_nat else "—",
        "{{GUI_WS_SUB}}": f"江苏及周边 {gui_ws_js:.1f} 元/斤 · 数据日 {today_date}" if gui_ws_js else f"数据日 {today_date}",
        "{{GUI_WS_TAG_CLASS}}": gui_ws_cls,
        "{{GUI_WS_TAG_TEXT}}": gui_ws_txt,
        "{{LU_POND_PRICE}}": lu_pond_txt,
        "{{LU_POND_SUB}}": esc(f"环太湖 9两/1.1斤 · {lu_pond_date}").replace("amp;", ""),
        "{{LU_POND_TAG_CLASS}}": "tag-up",
        "{{LU_POND_TAG_TEXT}}": esc((lp.get("headline") or "")[:26]),
        "{{LU_WS_PRICE}}": f"{lu_ws_nat:.1f}" if lu_ws_nat else "—",
        "{{LU_WS_SUB}}": f"江苏及周边 {lu_ws_js:.1f} 元/斤 · 数据日 {today_date}" if lu_ws_js else f"数据日 {today_date}",
        "{{LU_WS_TAG_CLASS}}": lu_ws_cls,
        "{{LU_WS_TAG_TEXT}}": lu_ws_txt,
        "{{GUI_CUR_PRICE}}": f"{gui_pond_val:.1f}" if gui_pond_val else (f"{gui_ws_js:.1f}" if gui_ws_js else "0"),
        "{{LU_CUR_PRICE}}": f"{lu_pond_val:.1f}" if lu_pond_val else (f"{lu_ws_js:.1f}" if lu_ws_js else "0"),
        "{{GUI_DATES}}": json.dumps([d[5:] for d in gui_dates], ensure_ascii=False),
        "{{GUI_NAT}}": json.dumps(gui_nat, ensure_ascii=False),
        "{{GUI_JS}}": json.dumps(gui_js, ensure_ascii=False),
        "{{LU_DATES}}": json.dumps([d[5:] for d in lu_dates], ensure_ascii=False),
        "{{LU_NAT}}": json.dumps(lu_nat, ensure_ascii=False),
        "{{LU_JS}}": json.dumps(lu_js, ensure_ascii=False),
        "{{MK_NAMES}}": json.dumps([_short_m(m) for m in _pick_markets(markets)], ensure_ascii=False),
        "{{MK_GUI}}": json.dumps([round(markets[m].get("鳜", 0), 1) for m in _pick_markets(markets)], ensure_ascii=False),
        "{{MK_LU}}": json.dumps([round(markets[m].get("鲈", 0), 1) for m in _pick_markets(markets)], ensure_ascii=False),
        "{{CHANGELOG_ITEMS}}": changelog,
        "{{VERSION_HISTORY_NOTE}}": esc(f"前序版本 {ver.get('prev', 'v2.0.13')}（设计参考稿）"),
    }
    for k, v in repl.items():
        html = html.replace(k, v)

    html = block_replace(html, "<!-- BOS_ACTIONS_START -->", "<!-- BOS_ACTIONS_END -->",
                         render_actions(acts["boss"], "老板 · 今日行动清单",
                                        f"{now.strftime('%Y-%m-%d')} 自动生成 · 依据：{FORECAST_DAYS}日预报 + 农业农村部批发价环比 + 塘口价快照"))
    html = block_replace(html, "<!-- TECH_ACTIONS_START -->", "<!-- TECH_ACTIONS_END -->",
                         render_actions(acts["tech"], "技术员 · 今日行动清单",
                                        f"{now.strftime('%Y-%m-%d')} 自动生成 · 依据：实时气象 + 水温投饵模型 + 病害周期"))
    html = block_replace(html, "<!-- BUYER_ACTIONS_START -->", "<!-- BUYER_ACTIONS_END -->",
                         render_actions(acts["buyer"], "采购员 · 今日行动清单",
                                        f"{now.strftime('%Y-%m-%d')} 自动生成 · 依据：周边批发均价倒推 + 跨区价差 + 收鱼体检红线"))

    os.makedirs(OUT_DIR, exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(html)

    # 版本落盘
    ver.setdefault("history", [])
    ver["date"] = now.strftime("%Y-%m-%d")
    ver["prev"] = ver.get("prev", "v2.0.13")
    with open(VERFILE, "w", encoding="utf-8") as f:
        json.dump(ver, f, ensure_ascii=False, indent=2)

    print(f"[ok] 生成完成 → dashboard-v2/index.html（{len(html)} 字符，版本 {ver['version']}）")
    print(f"     气象 {len(daily)} 天 / 历史序列 鳜 {len(gui_dates)} 点、鲈 {len(lu_dates)} 点 / 市场对比 {len(_pick_markets(markets))} 个")
    for role, items in acts.items():
        print(f"     行动清单 {role}: {len(items)} 条")


# ----------------------------------------------------------------------------
# 小工具
# ----------------------------------------------------------------------------
def _median(vals):
    if not vals:
        return None
    s = sorted(vals)
    n = len(s)
    return s[n // 2] if n % 2 else (s[n // 2 - 1] + s[n // 2]) / 2


def _fmt_t(v):
    return f"{v:.0f}" if isinstance(v, (int, float)) else "—"


def _dir_text(deg):
    if deg is None:
        return ""
    names = ["北", "东北", "东", "东南", "南", "西南", "西", "西北"]
    return names[int((deg % 360) / 45 + 0.5) % 8]


def _beaufort(kmh):
    if kmh is None:
        return "—"
    for b, thr in enumerate([1, 5, 11, 19, 28, 38, 49, 61, 74, 88, 102, 117], start=0):
        if kmh < thr:
            return str(b)
    return "12"


def _wcard(icon, label, value, sub):
    return (f'<div class="weather-card"><div class="icon">{icon}</div><div class="label">{label}</div>'
            f'<div class="value">{value}</div><div class="sub">{sub}</div></div>')


def _water(title, body):
    return f'<div class="water-card"><h4>{title}</h4><p>{body}</p></div>'


def _alert(cls, title, body, tip):
    return (f'<div class="alert-card {cls}"><h4>{title}</h4><p>{body}</p><div class="tip">{tip}</div></div>')


def _recv(title, body, price):
    return (f'<div class="recv-card"><h4>{title}</h4><p>{body}</p>'
            f'<div class="price-line">{price}</div></div>')


def _prow(a, b, c, d, e, f, g):
    return (f"<tr><td>{a}</td><td>{b}</td><td>{c}</td><td>{d}</td><td>{e}</td>"
            f"<td>{f}</td><td>{g}</td></tr>")


def _post(title, date, core, src):
    return f"<tr><td>{title}</td><td>{date}</td><td>{core}</td><td>{src}</td></tr>"


def _short_m(m):
    s = m
    for suf in ("有限责任公司", "股份有限公司", "有限公司", "农副产品批发市场",
                "农产品市场", "批发市场", "经营管理", "股份", "实业"):
        s = s.replace(suf, "")
    s = re.sub(r"(市场|管理|发展|股份|有限|责任|公司)+$", "", s).strip()
    return (s or m)[:9]


def _pick_markets(markets):
    key_names = ["凌家塘", "南环桥", "新发地", "白沙洲", "华潮", "大红门", "江杨", "北园春", "周谷堆", "农产品"]
    picked = []
    for k in key_names:
        for m in markets:
            if k in m and m not in picked:
                picked.append(m)
                break
    rest = [m for m in markets if m not in picked]
    rest.sort(key=lambda x: -(markets[x].get("鳜", 0)))
    return (picked + rest)[:10]


if __name__ == "__main__":
    main()
