#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
moa_index_crawler.py —— 农业农村部「农产品批发价格200指数」每日抓取 + 看板注入

数据链路（已溯源核验 2026-11-06）：
  采集：全国 286 家产销地批发市场 每日 14:00 采价
  计算：农业农村部信息中心
  发布：农业农村部市场与信息化司 → 中国农业农村信息网「最新发布」栏目
        https://www.agri.cn/zx/zxfb/

能拿到：200 总指数、菜篮子指数、28 种蔬菜、6 种水果、以及
        鲫鱼 / 鲤鱼 / 白鲢鱼 / 大带鱼 四种水产的元/公斤 + 日环比。

拿不到：**水产品价格指数**（只在 pfsc.agri.cn 门户 SPA 显示，/api 需 token）。
        该值保存在 moa_index_latest.json 的 water_index 字段，需人工按门户核对更新；
        脚本发现其日期落后于指数日期时会在 csub 内标注实际取数日期，不冒充当日值。

用法：
  python3 moa_index_crawler.py            # 抓取 → 写 json → 注入看板 → 回写 manifest 日期
  python3 moa_index_crawler.py --dry-run  # 只抓取并打印，不写文件
  python3 moa_index_crawler.py --check    # 只校验线上最新文章标题与日期
"""
import argparse
import json
import os
import re
import sys
import urllib.request
from datetime import datetime

HERE = os.path.dirname(os.path.abspath(__file__))
HTML = os.path.join(HERE, "鳜鱼鲈鱼价格看板.html")
JSON_OUT = os.path.join(HERE, "moa_index_latest.json")
MANIFEST = os.path.join(HERE, "data_sources_manifest.json")

LIST_URL = "https://www.agri.cn/zx/zxfb/"
UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/120.0 Safari/537.36")

START = "<!-- MOA_INDEX_START -->"
END = "<!-- MOA_INDEX_END -->"
H3_MARK = "<h3>📊 水产市场风向标"

SPECIES = ["鲫鱼", "鲤鱼", "白鲢鱼", "大带鱼"]
# 看板浅色主题：涨=红、跌=绿（国内习惯）
RED, GREEN, GRAY = "#dc2626", "#12a150", "#6b7280"


def fetch(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    return urllib.request.urlopen(req, timeout=25).read().decode("utf-8", "ignore")


def strip_tags(h: str) -> str:
    h = re.sub(r"<script.*?</script>", "", h, flags=re.S | re.I)
    h = re.sub(r"<style.*?</style>", "", h, flags=re.S | re.I)
    t = re.sub(r"<[^>]+>", "", h)
    t = t.replace("&nbsp;", " ").replace("&quot;", '"').replace("&amp;", "&")
    return re.sub(r"\s+", " ", t)


def latest_article() -> tuple:
    """返回 (title, url, date_str, year_int)。优先栏目首页，回退当月目录。"""
    html = fetch(LIST_URL)
    cands = []
    for href, title in re.findall(r'<a[^>]+href="([^"]+)"[^>]*>\s*([^<]*?农产品批发价格200指数[^<]*)</a>', html):
        title = re.sub(r"\s+", " ", title).strip()
        url = href if href.startswith("http") else "https://www.agri.cn/zx/zxfb/" + href.lstrip("./")
        cands.append((title, url))
    if not cands:
        raise RuntimeError("栏目页未找到「农产品批发价格200指数」文章，站点结构可能变更")
    title, url = cands[0]
    m = re.search(r"t(\d{4})(\d{2})(\d{2})_", url)
    if not m:
        raise RuntimeError(f"无法从 URL 解析日期: {url}")
    y, mo, d = m.group(1), m.group(2), m.group(3)
    return title, url, f"{y}-{mo}-{d}", int(y)


def parse_body(text: str) -> dict:
    def idx(pattern):
        m = re.search(pattern, text)
        if not m:
            return None
        groups = m.groups()
        return groups

    out = {}
    m = re.search(r'农产品批发价格200指数[”"」]?\s*为\s*([\d.]+)\s*[，,]\s*比\s*(昨天|上周五|上周)\s*(下降|上升|持平)\s*([\d.]+)\s*个点', text)
    if m:
        out["index200"] = {"value": float(m.group(1)), "base": m.group(2),
                           "dir": m.group(3), "delta": float(m.group(4))}
    m = re.search(r'菜篮子[”"」]?\s*产品批发价格指数为\s*([\d.]+)\s*[，,]\s*比\s*(昨天|上周五|上周)\s*(下降|上升|持平)\s*([\d.]+)\s*个点', text)
    if m:
        out["cailanzi"] = {"value": float(m.group(1)), "base": m.group(2),
                           "dir": m.group(3), "delta": float(m.group(4))}
    fishes = {}
    for name in SPECIES:
        m = re.search(name + r'\s*([\d.]+)\s*元/公斤\s*[，,]\s*比\s*(昨天|上周五|上周)\s*(下降|上升|持平)\s*([\d.]+)\s*%', text)
        if m:
            fishes[name] = {"value": float(m.group(1)), "base": m.group(2),
                            "dir": m.group(3), "delta": float(m.group(4))}
    out["fish"] = fishes
    return out


def arrow(direction: str, delta: float, unit: str = "") -> str:
    if direction == "持平" or delta == 0:
        return "持平"
    sign = "↓" if direction == "下降" else "↑"
    return f"{sign}{delta:g}{unit}"


def color_of(direction: str) -> str:
    if direction == "持平":
        return GRAY
    return GREEN if direction == "下降" else RED   # 跌绿、涨红（国内习惯）


def commentary(fish: dict) -> str:
    if not fish:
        return ""
    ranked = sorted(fish.items(), key=lambda kv: -abs(kv[1]["delta"]))
    top_name, top = ranked[0]
    downs = [n for n, v in fish.items() if v["dir"] == "下降" and n != top_name]
    ups = [n for n, v in fish.items() if v["dir"] == "上升" and n != top_name]
    if top["dir"] == "下降" and abs(top["delta"]) >= 3:
        lead = f"{top_name}单日跌 {top['delta']:g}%（四品种跌幅榜首）"
    elif top["dir"] == "上升" and abs(top["delta"]) >= 3:
        lead = f"{top_name}单日涨 {top['delta']:g}%（四品种涨幅榜首）"
    else:
        lead = f"四品种波动均在 {max(abs(v['delta']) for v in fish.values()):g}% 以内"
    tail = []
    if downs:
        tail.append("、".join(downs) + " 下跌")
    if ups:
        tail.append("、".join(ups) + " 上涨")
    flat = [n for n, v in fish.items() if v["dir"] == "持平"]
    if flat:
        tail.append("、".join(flat) + " 持平")
    return lead + ("，" + "，".join(tail) if tail else "") + "，普水鱼整体" + ("偏弱" if len(downs) > len(ups) else "偏强" if len(ups) > len(downs) else "弱稳") + "。"


def build_card(data: dict, prev_water: dict | None) -> str:
    date = data["date"]
    y_, m_, d_ = date.split("-")
    d_cn = f"{int(m_)}-{d_}"          # 11-05 形式，月前导零去掉、日保留两位
    i2, cl = data.get("index200"), data.get("cailanzi")
    fish = data.get("fish", {})
    title_idx = ""
    if i2:
        title_idx = f'（"200指数"{i2["value"]:.2f} {arrow(i2["dir"], i2["delta"], "点")}）'

    # 水产品指数：门户口径、人工核对，日期不同则显式标注
    water_txt = ""
    if prev_water and prev_water.get("value"):
        wd = prev_water.get("date", "")
        wd_short = wd[5:] if len(wd) >= 10 else wd
        same_day = wd == date
        d_arrow = arrow(prev_water.get("dir", "持平"), prev_water.get("delta", 0), "点")
        water_txt = (f'水产品价格指数 {prev_water["value"]:.2f}'
                     f'（{wd_short} 门户值{d_arrow}{"" if same_day else "，非本日同步"}）。')

    fish_bits = []
    for n in SPECIES:
        if n in fish:
            v = fish[n]
            fish_bits.append(f'{n.replace("鱼", "") if n == "白鲢鱼" else n} {v["value"]:g} 元/kg（{arrow(v["dir"], v["delta"], "%")}）')
    fish_txt = "、".join(fish_bits)

    sub = (f'据农业农村部监测，{d_cn} 「农产品批发价格200指数」'
           f'{i2["value"]:.2f}（{arrow(i2["dir"], i2["delta"], "点")}）'
           + (f'，「菜篮子」产品批发价格指数 {cl["value"]:.2f}（{arrow(cl["dir"], cl["delta"], "点")}）' if cl else "")
           + "，" + water_txt
           + f'截至 14:00 全国批发：<b>{fish_txt}</b>。'
           + commentary(fish)
           + '注：原「水产市场风向标」公众号 10-16 后停更 200 指数（改发海水鱼日报），'
             '本卡自 10-29 起改引农业农村部市场与信息化司每日指数，现由 '
             '<code>moa_index_crawler.py</code> 每日自动抓取。')

    rows = []
    for n in SPECIES:
        if n not in fish:
            continue
        v = fish[n]
        c = color_of(v["dir"])
        rows.append(f'          <tr><td>{n}</td><td class="price"><b>{v["value"]:g}</b></td>'
                    f'<td style="color:{c};font-size:12px">{arrow(v["dir"], v["delta"], "%")}</td></tr>')
    if i2:
        rows.append(f'          <tr><td>农产品批发价格200指数</td><td class="price">{i2["value"]:.2f}</td>'
                    f'<td style="color:{color_of(i2["dir"])};font-size:12px">{arrow(i2["dir"], i2["delta"], "点")}</td></tr>')
    if cl:
        rows.append(f'          <tr><td>菜篮子产品批发价格指数</td><td class="price">{cl["value"]:.2f}</td>'
                    f'<td style="color:{color_of(cl["dir"])};font-size:12px">{arrow(cl["dir"], cl["delta"], "点")}</td></tr>')

    jc = ""
    if "鲫鱼" in fish:
        jc = (f'（如鲫鱼 {fish["鲫鱼"]["value"]:g} 元/kg≈{fish["鲫鱼"]["value"]/2:.2f} 元/斤、'
              f'可与白沙洲塘口价对照）')

    block = f'''{START}
    <div class="card" style="margin-top:14px">
      <h3>📊 水产市场风向标 · 农业农村部批发价格指数 {date}{title_idx}</h3>
      <div class="csub">{sub}</div>
      <table>
        <thead><tr><th>品种</th><th>农业农村部批发价（元/kg）</th><th>日环比</th></tr></thead>
        <tbody>
{os.linesep.join(rows)}
        </tbody>
      </table>
      <div class="callout" style="margin-top:10px"><b>口径说明：</b>农业农村部全国批发均价为官方口径（元/kg），与看板 KPI 批发价（元/斤）换算一致{jc}；本表四品种为农业农村部每日公布的普水代表品种，<b>不含鳜鱼/加州鲈</b>（特水鱼官方无日更口径，见上方各源塘口/批发卡）。原「水产市场风向标」账号 10-16 后停更 200 指数，本卡数据自 10-29 起改引农业农村部官方每日指数，保证口径一致、可逐日刷新；指数与四鱼价由脚本自动更新，<b>水产品价格指数一项仍需按 pfsc.agri.cn 门户人工核对</b>。</div>
      <div class="legend">来源：农业农村部市场与信息化司 {date}《农产品批发价格200指数》· <a class="plink" href="https://www.agri.cn/zx/zxfb/" target="_blank" rel="noopener">📄 官方栏目（每日更新·永久入口）</a> · <a class="plink" href="{data["url"]}" target="_blank" rel="noopener">📄 本篇原文（{date}）</a> · 指数看板（含水产品指数）：<a class="plink" href="https://pfsc.agri.cn/portal-app/#/indexpage" target="_blank" rel="noopener">pfsc.agri.cn</a></div>
    </div>
{END}'''
    return block


def find_card_span(html: str) -> tuple:
    i = html.find(H3_MARK)
    if i < 0:
        raise RuntimeError("看板内未找到「📊 水产市场风向标」卡片")
    start = html.rfind('<div class="card"', 0, i)
    depth, j = 0, start
    while True:
        nxt_open = html.find("<div", j)
        nxt_close = html.find("</div>", j)
        if nxt_close < 0:
            raise RuntimeError("卡片 div 未闭合")
        if nxt_open != -1 and nxt_open < nxt_close:
            depth += 1
            j = nxt_open + 4
        else:
            depth -= 1
            j = nxt_close + 6
            if depth == 0:
                return start, j


def inject(html: str, block: str) -> str:
    if START in html and END in html:
        s = html.index(START)
        e = html.index(END, s) + len(END)
        return html[:s] + block + html[e:]
    s, e = find_card_span(html)
    return html[:s] + block + html[e:]


def update_manifest(date: str):
    with open(MANIFEST, encoding="utf-8") as f:
        m = json.load(f)
    m.setdefault("manual_dates", {})["fengxiang"] = date
    for s in m.get("sources", []):
        if s.get("key") == "fengxiang":
            s["note"] = ("农业农村部「农产品批发价格200指数」每日发布（agri.cn/zx/zxfb/），"
                         "由 moa_index_crawler.py 自动抓取指数与鲫/鲤/白鲢/大带鱼四品种价；"
                         "水产品价格指数仅 pfsc.agri.cn 门户可见，需人工核对")
    with open(MANIFEST, "w", encoding="utf-8") as f:
        json.dump(m, f, ensure_ascii=False, indent=2)
    return m["manual_dates"]["fengxiang"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true", help="只抓取并打印，不写文件")
    ap.add_argument("--check", action="store_true", help="只校验最新文章标题/日期")
    args = ap.parse_args()

    title, url, date, year = latest_article()
    print(f"[1/4] 最新文章：{title}\n      URL：{url}\n      日期：{date}")
    if args.check:
        return

    body = strip_tags(fetch(url))
    parsed = parse_body(body)
    if not parsed.get("index200"):
        print("[ERROR] 未解析到 200 指数，站点文案可能变更；保留看板原值不覆盖", file=sys.stderr)
        sys.exit(2)
    print(f"[2/4] 200指数 {parsed['index200']['value']:g}，菜篮子 "
          f"{parsed.get('cailanzi', {}).get('value', 'N/A')}，鱼价 "
          + "、".join(f"{k}{v['value']:g}({v['dir']}{v['delta']:g}%)" for k, v in parsed["fish"].items()))

    prev = {}
    if os.path.exists(JSON_OUT):
        with open(JSON_OUT, encoding="utf-8") as f:
            prev = json.load(f)
    water = prev.get("water_index") or {"value": 116.00, "date": "2026-11-05",
                                        "dir": "下降", "delta": 0.52,
                                        "note": "pfsc.agri.cn 门户口径，人工核对"}

    data = {"title": title, "url": url, "date": date, "year": year,
            "fetched_at": datetime.now().astimezone().isoformat(timespec="seconds"),
            **parsed, "water_index": water}

    block = build_card(data, water)
    if args.dry_run:
        print("[dry-run] 卡片预览：\n" + block)
        return

    # 数据未变（当日文章尚未发布/内容相同）时不重写 JSON，避免每日空提交
    sig = ("title", "url", "date", "index200", "cailanzi", "fish")
    unchanged = all(prev.get(k) == data.get(k) for k in sig)
    if unchanged:
        print(f"[3/4] 数据与 {os.path.basename(JSON_OUT)} 一致，跳过写入")
    else:
        with open(JSON_OUT, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"[3/4] 已写 {os.path.basename(JSON_OUT)}")

    with open(HTML, encoding="utf-8") as f:
        html = f.read()
    new = inject(html, block)
    if new == html:
        print("[4/4] 看板内容无变化，跳过写入")
    else:
        with open(HTML, "w", encoding="utf-8") as f:
            f.write(new)
        print("[4/4] 看板已注入（幂等，重复运行不叠加）")

    d = update_manifest(date)
    print(f"      manifest manual_dates.fengxiang -> {d}")


if __name__ == "__main__":
    main()
