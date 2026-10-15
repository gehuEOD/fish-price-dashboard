#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""宜兴官林镇数字低碳生态养殖项目 · 实时气象抓取脚本
主数据源：Open-Meteo API（免费、无需 Key、WMO 标准、15min 更新）— 提供全部 8 项指标
校验源：高德天气 API（中国气象局数据）— 提供官方中文预报，用于交叉校验
坐标：(119.723966, 31.557387)  江苏省无锡市宜兴市官林镇生产路（高德地理编码权威值）
输出：farm_weather_latest.json（含 current + 7d daily + hourly shortwave_radiation
      + amap 官方预报 + 异常告警列表）
"""
import json, urllib.request, urllib.parse, os, sys, time
from datetime import datetime, timezone, timedelta

WS = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(WS, "farm_weather_latest.json")
AMAP_FILE = os.path.join(WS, "amap_weather_latest.json")

LAT = 31.557387
LON = 119.723966
LOCATION_NAME = "江苏环荟·宜兴官林镇数字低碳生态养殖项目"
ADDRESS = "江苏省无锡市宜兴市官林镇生产路"
ADCODE = "320282"  # 宜兴市
COORD_SOURCE = "高德地理编码 API（level=道路·生产路，2026-09-01 校准）"
OPERATOR = "江苏环荟"


def deg_to_compass(deg):
    """角度 → 16 方位中文标签"""
    if deg is None:
        return "—"
    n360 = deg % 360
    labels = ["北", "北东北", "东北", "东北东", "东", "东南东", "东南", "南东南",
              "南", "南西南", "西南", "西南西", "西", "西北西", "西北", "北西北"]
    idx = int((n360 + 11.25) // 22.5) % 16
    return labels[idx]


def wmo_to_text(code):
    """WMO weather code → (图标, 描述)"""
    table = {
        0: ("☀️", "晴"),
        1: ("🌤️", "局部多云"),
        2: ("⛅", "多云"),
        3: ("☁️", "阴"),
        45: ("🌫️", "雾"),
        48: ("🌫️", "雾凇"),
        51: ("🌦️", "毛毛雨(弱)"),
        53: ("🌦️", "毛毛雨(中)"),
        55: ("🌦️", "毛毛雨(强)"),
        56: ("🌧️", "冻毛毛雨"),
        57: ("🌧️", "冻毛毛雨"),
        61: ("🌧️", "小雨"),
        63: ("🌧️", "中雨"),
        65: ("🌧️", "大雨"),
        66: ("🌧️", "冻雨"),
        67: ("🌧️", "冻雨"),
        71: ("🌨️", "小雪"),
        73: ("🌨️", "中雪"),
        75: ("🌨️", "大雪"),
        77: ("🌨️", "米雪"),
        80: ("🌦️", "阵雨(弱)"),
        81: ("🌧️", "阵雨(中)"),
        82: ("⛈️", "阵雨(强)"),
        85: ("🌨️", "阵雪"),
        86: ("🌨️", "强阵雪"),
        95: ("⛈️", "雷暴"),
        96: ("⛈️", "雷暴+冰雹"),
        99: ("⛈️", "强雷暴+冰雹"),
    }
    return table.get(code, ("❓", f"代码{code}"))


def derive_alerts(c, daily):
    """基于养殖阈值判断告警"""
    alerts = []
    if c.get("weather_code", 0) >= 95:
        alerts.append({"level": "high", "icon": "⛈️",
                       "msg": f"当前雷暴(代码 {c['weather_code']})：检查增氧机/光伏板/排水/用电安全"})
    t = c.get("temperature_2m", 0)
    if t >= 33:
        alerts.append({"level": "high", "icon": "🔥",
                       "msg": f"高温 {t:.1f}°C（鳜鱼警戒线 33°C）：启用增氧/加深水位"})
    elif t >= 30:
        alerts.append({"level": "warn", "icon": "🌡️",
                       "msg": f"气温偏高 {t:.1f}°C（鳜鱼舒适上限 30°C）：关注午后溶氧"})
    w = c.get("wind_speed_10m", 0)
    if w >= 38:
        alerts.append({"level": "high", "icon": "💨",
                       "msg": f"大风 {w:.1f} km/h（≥6 级）：薄膜/光伏板/围网检查"})
    elif w >= 25:
        alerts.append({"level": "warn", "icon": "🌬️",
                       "msg": f"风速偏高 {w:.1f} km/h"})
    p = c.get("surface_pressure", 1013)
    if p < 1005:
        alerts.append({"level": "warn", "icon": "📉",
                       "msg": f"气压偏低 {p:.1f} hPa（<1005）：可能风暴前兆"})
    if daily and len(daily) > 0:
        r0 = daily[0].get("precip_mm", 0)
        if r0 >= 50:
            alerts.append({"level": "high", "icon": "🌊",
                           "msg": f"24h 累计降水 {r0:.1f}mm（≥50 暴雨）：检查排水系统"})
        elif r0 >= 25:
            alerts.append({"level": "warn", "icon": "🌧️",
                           "msg": f"24h 累计降水 {r0:.1f}mm（≥25 大雨）"})
    # 下一日大风预警
    if daily and len(daily) > 1:
        w_next = daily[1].get("wind_max_kmh", 0)
        if w_next >= 38:
            alerts.append({"level": "warn", "icon": "💨",
                           "msg": f"明日{daily[1]['date']} 阵风可达 {w_next:.1f} km/h"})
    return alerts


def load_amap():
    """读取高德官方天气（中国气象局数据），用于交叉校验。
    该文件由 MCP amap-maps / maps_weather 工具（city=320282 宜兴市）每日更新。
    文件不存在时返回 None，看板自动降级为纯 Open-Meteo 单源。"""
    if not os.path.exists(AMAP_FILE):
        return None
    try:
        return json.load(open(AMAP_FILE, encoding="utf-8"))
    except Exception:
        return None


def cross_check(days, amap):
    """Open-Meteo（WMO 模型）vs 高德（中国气象局）最高温交叉校验。
    偏差 ≥2°C 标记 mismatch，提示人工复核。"""
    if not amap or not amap.get("forecasts"):
        return []
    rows = []
    for f in amap["forecasts"]:
        date = f["date"]
        om = next((d for d in days if d["date"] == date), None)
        if not om:
            continue
        amap_max = float(f["daytemp_float"])
        om_max = float(om["temp_max_c"])
        delta = round(amap_max - om_max, 1)
        rows.append({
            "date": date,
            "amap_day": f["dayweather"],
            "amap_night": f["nightweather"],
            "amap_max": amap_max,
            "amap_min": float(f["nighttemp_float"]),
            "amap_wind": f["daywind"],
            "amap_power": f["daypower"],
            "openmeteo_max": om_max,
            "openmeteo_min": float(om["temp_min_c"]),
            "delta_max": delta,
            "status": "mismatch" if abs(delta) >= 2.0 else "ok",
        })
    return rows


def fetch():
    params = {
        "latitude": LAT, "longitude": LON,
        "current": "temperature_2m,wind_speed_10m,wind_direction_10m,relative_humidity_2m,precipitation,surface_pressure,weather_code",
        "hourly": "shortwave_radiation",
        "daily": "weather_code,temperature_2m_max,temperature_2m_min,precipitation_sum,precipitation_probability_max,wind_speed_10m_max,wind_direction_10m_dominant,shortwave_radiation_sum",
        "forecast_days": 7,
        "timezone": "Asia/Shanghai",
        "wind_speed_unit": "kmh",
    }
    url = "https://api.open-meteo.com/v1/forecast?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 WorkBuddy"})
    # Open-Meteo 免费版偶发 503 "service is overloaded"，重试即可成功（2026-10-15 首次遇到）
    data = None
    last_err = None
    for attempt in range(1, 6):
        try:
            with urllib.request.urlopen(req, timeout=20) as resp:
                data = json.loads(resp.read().decode("utf-8"))
            break
        except Exception as e:  # HTTPError / URLError / timeout 均重试
            last_err = e
            print(f"[warn] Open-Meteo 第 {attempt} 次请求失败：{e}", file=sys.stderr)
            if attempt < 5:
                time.sleep(5 * attempt)
    if data is None:
        print(f"[error] Open-Meteo 连续 5 次请求失败，放弃：{last_err}", file=sys.stderr)
        return False

    cur = data["current"]
    cur_iso = cur["time"]
    hourly = data.get("hourly", {})
    rad_val = None
    if "shortwave_radiation" in hourly and "time" in hourly:
        cur_dt = datetime.fromisoformat(cur_iso)
        best_diff = 1e9
        for i, t_iso in enumerate(hourly["time"]):
            t_dt = datetime.fromisoformat(t_iso)
            diff = abs((cur_dt - t_dt).total_seconds())
            if diff < best_diff:
                best_diff = diff
                rad_val = hourly["shortwave_radiation"][i]

    current = {
        "time": cur_iso,
        "temperature_c": cur["temperature_2m"],
        "wind_speed_kmh": cur["wind_speed_10m"],
        "wind_dir_deg": cur["wind_direction_10m"],
        "wind_dir_text": deg_to_compass(cur["wind_direction_10m"]),
        "humidity_pct": cur["relative_humidity_2m"],
        "precipitation_mm": cur["precipitation"],
        "pressure_hpa": cur["surface_pressure"],
        "weather_code": cur["weather_code"],
        "weather_icon": wmo_to_text(cur["weather_code"])[0],
        "weather_text": wmo_to_text(cur["weather_code"])[1],
        "solar_radiation_wm2": rad_val,
        "elevation_m": data.get("elevation", None),
        "timezone": data.get("timezone", "Asia/Shanghai"),
    }

    d = data.get("daily", {})
    days = []
    for i, date in enumerate(d.get("time", [])):
        wc = d["weather_code"][i]
        wd = d.get("wind_direction_10m_dominant", [None]*7)[i]
        days.append({
            "date": date,
            "weather_code": wc,
            "weather_icon": wmo_to_text(wc)[0],
            "weather_text": wmo_to_text(wc)[1],
            "temp_max_c": d["temperature_2m_max"][i],
            "temp_min_c": d["temperature_2m_min"][i],
            "precip_mm": d["precipitation_sum"][i],
            "precip_prob_pct": d.get("precipitation_probability_max", [None]*7)[i],
            "wind_max_kmh": d["wind_speed_10m_max"][i],
            "wind_dir_deg": wd,
            "wind_dir_text": deg_to_compass(wd) if wd is not None else "—",
            "solar_mjm2": d.get("shortwave_radiation_sum", [None]*7)[i],
        })

    amap = load_amap()
    xcheck = cross_check(days, amap)

    out = {
        "site": {
            "name": LOCATION_NAME,
            "address": ADDRESS,
            "adcode": ADCODE,
            "lat": LAT, "lon": LON,
            "coord_source": COORD_SOURCE,
            "operator": OPERATOR,
            "total_area_mu": 1200,
            "phase1_village": "丰义村", "phase1_area_mu": 500,
            "phase2_village": "白茫村", "phase2_area_mu": 700,
            "product": "鳜鱼 / 鲈鱼（蜂窝池养殖）",
        },
        "current": current,
        "daily": days,
        "amap": amap,
        "cross_check": xcheck,
        "alerts": derive_alerts(cur, days),
        "meta": {
            "fetched_at_cst": datetime.now(timezone(timedelta(hours=8))).strftime("%Y-%m-%d %H:%M:%S"),
            "source": "Open-Meteo API (https://api.open-meteo.com)",
            "license": "Open-Meteo CC BY 4.0; data from national weather services",
            "secondary_source": "高德天气 API（中国气象局）" if amap else None,
        },
    }
    json.dump(out, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print(f"[OK] {OUT}")
    print(f"  站点：{LOCATION_NAME} ({LAT}, {LON})")
    print(f"  当前：{current['weather_text']} {current['temperature_c']}°C, 风 {current['wind_speed_kmh']} km/h {current['wind_dir_text']}")
    print(f"  气压 {current['pressure_hpa']} hPa · 湿度 {current['humidity_pct']}% · 辐射 {current['solar_radiation_wm2']} W/m²")
    print(f"  告警 {len(out['alerts'])} 条")
    for a in out["alerts"]:
        print(f"   [{a['level'].upper()}] {a['icon']} {a['msg']}")
    return out


if __name__ == "__main__":
    sys.exit(0 if fetch() else 1)