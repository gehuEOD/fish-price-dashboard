#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""高德天气 v3 直连（云端替代 WorkBuddy amap MCP）

原 automation 用 mcp__amap-maps__maps_weather 写 amap_weather_latest.json，
仅本机 WorkBuddy 在线时可用 → 这是「气象刷新依赖电脑」的根因。
本脚本改调高德开放平台 v3 weatherInfo Web API，使刷新可在 GitHub Actions 云端运行。

高德 v3 接口：https://restapi.amap.com/v3/weather/weatherInfo
  - city=320282（宜兴市 adcode）
  - extensions=all（含多日预报 casts，字段与 MCP 透传完全一致）
  - key 从环境变量 AMAP_KEY 读取（由 GitHub Actions secrets 注入）

输出 amap_weather_latest.json 与历史 MCP 生成格式【逐字段一致】：
直接透传高德原始 casts（date/week/dayweather/nightweather/daytemp/daytemp_float/...），
确保 weather_fetcher.cross_check() 与 inject_weather_block.py 无需任何改动即可复用。

失败处理：未配 AMAP_KEY / 网络异常 / 限流 / status!=1 → 不写文件，
weather_fetcher.load_amap() 回退到历史旧文件（与 MCP 失败时「保留旧文件」语义一致）。
"""
import json
import os
import sys
import time
import urllib.parse
import urllib.request
from datetime import datetime, timezone, timedelta

WS = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(WS, "amap_weather_latest.json")
AMAP_KEY = os.environ.get("AMAP_KEY", "")
CITY = "320282"  # 宜兴市 adcode
ENDPOINT = "https://restapi.amap.com/v3/weather/weatherInfo"


def fetch():
    if not AMAP_KEY:
        print("[warn] 未设置 AMAP_KEY 环境变量，跳过双源校验（云端降级 Open-Meteo 单源）",
              file=sys.stderr)
        return False
    params = urllib.parse.urlencode({"city": CITY, "extensions": "all", "key": AMAP_KEY})
    url = f"{ENDPOINT}?{params}"
    for attempt in range(1, 4):
        try:
            req = urllib.request.Request(
                url, headers={"User-Agent": "Mozilla/5.0 WorkBuddy-WeatherCI"})
            with urllib.request.urlopen(req, timeout=20) as resp:
                data = json.loads(resp.read().decode("utf-8"))
            if data.get("status") != "1":
                print(f"[warn] 高德 API 返回 status={data.get('status')} "
                      f"info={data.get('info')} infocode={data.get('infocode')}",
                      file=sys.stderr)
                return False
            forecasts = data.get("forecasts") or []
            casts = (forecasts[0].get("casts") if forecasts else None) or []
            if not casts:
                print("[warn] 高德返回空 forecasts/casts", file=sys.stderr)
                return False
            f0 = forecasts[0]
            # 透传高德原始 casts，逐字段对齐历史 MCP 生成格式
            out = {
                "city": f0.get("city", "宜兴市"),
                "adcode": f0.get("adcode", CITY),
                "source": "高德天气 API（中国气象局数据，v3 weatherInfo 直连）",
                "fetched_at_cst": datetime.now(timezone(timedelta(hours=8)))
                .strftime("%Y-%m-%d %H:%M:%S"),
                "forecasts": casts,
            }
            with open(OUT, "w", encoding="utf-8") as fp:
                json.dump(out, fp, ensure_ascii=False, indent=2)
            print(f"[OK] 高德天气已写入 {OUT}，{len(casts)} 天预报")
            return True
        except Exception as e:  # HTTPError / URLError / timeout / JSON 解析
            print(f"[warn] 高德第 {attempt} 次请求失败：{e}", file=sys.stderr)
            if attempt < 3:
                time.sleep(3 * attempt)
    print("[error] 高德连续失败，保留旧文件（降级为 Open-Meteo 单源）", file=sys.stderr)
    return False


if __name__ == "__main__":
    sys.exit(0 if fetch() else 1)
