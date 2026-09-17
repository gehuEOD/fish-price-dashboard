#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
公众号「截图 → OCR → 结构化 → 并入看板」流水线
================================================
把「用户手动发截图」升级为可定时运行的自动化链路：

  ① RPA 截图（wechat_rpa.py，可选）：sogou 搜号 → 打开最新文章 → 整页截图到 ./screenshots/
  ② OCR 结构化（本脚本）：对截图做视觉 OCR，抽取价格表行
        - 优先 vision-LLM 适配器（OpenAI 兼容 / SiliconFlow，中文表格最准）
        - 兜底 tesseract 本地 OCR
  ③ 结构化落库：写入 wechat_ocr_current.json（按来源聚合）+ wechat_ocr_prices_<YYYYMMDD>.json（历史快照）
  ④ 并入看板：用稳定锚点注释替换「鳜鱼鲈鱼价格看板.html」中「科学养鱼 / a渔业行情」板块

用法
----
  # 1) 用截图直接跑（指定来源，自动 OCR）
  python wechat_ocr_pipeline.py --images 截图1.png 截图2.png --source 科学养鱼

  # 2) 已有结构化 JSON（跳过 OCR，仅合并）—— 用于无 API 环境或人工校正后回填
  python wechat_ocr_pipeline.py --json wechat_ocr_prices_20260828.json

  # 3) 仅用现有 current.json 重建看板板块（不改数据）
  python wechat_ocr_pipeline.py --rebuild

  # 环境变量（vision 适配器）
  OCR_API_BASE  默认 https://api.siliconflow.cn/v1
  OCR_API_KEY   必填（SiliconFlow / OpenAI 兼容密钥）
  OCR_MODEL     默认 Qwen/Qwen2.5-VL-72B-Instruct

依赖：pip install requests pillow   （tesseract 兜底需系统装 tesseract + pip install pytesseract）
"""
import os, sys, re, json, glob, argparse, base64, datetime, subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
DASHBOARD = os.path.join(HERE, "鳜鱼鲈鱼价格看板.html")
CURRENT_JSON = os.path.join(HERE, "wechat_ocr_current.json")

# ---- 看板锚点（与 HTML 中成对注释一致） ----
SCI_START = "<!-- 科学养鱼公众号 OCR 数据 -->"
SCI_END   = "<!-- /科学养鱼公众号 OCR 数据 -->"
A_START   = "<!-- a渔业行情公众号 OCR 数据 -->"
A_END     = "<!-- /a渔业行情公众号 OCR 数据 -->"

SOURCE_VARIANTS = {"科学养鱼": "科学养鱼", "a渔业行情": "a渔业行情",
                   "sci": "科学养鱼", "a": "a渔业行情"}


def species_tag(species: str) -> str:
    if "鳜" in species:
        return "tag-gui"
    if "鲈" in species or "加州" in species:
        return "tag-lu"
    return "tag"


def fmt_price(p):
    if p is None:
        return "—"
    if isinstance(p, (int, float)):
        return f"{float(p):.2f}"
    return str(p)


# ----------------------------------------------------------------------------
# OCR 适配器
# ----------------------------------------------------------------------------
def ocr_vision(image_paths, source, api_base, api_key, model):
    """调用 OpenAI 兼容视觉接口，返回结构化记录列表。"""
    import requests
    sys_prompt = (
        "你是水产价格表 OCR 助手。用户会给你一张微信公众号价格截图，"
        "请抽取其中所有「水产品批发价/塘口价」表格行，输出严格 JSON 数组，"
        "每条记录字段："
        '{"species": 品种(如 鳜鱼（桂花鱼）/加州鲈/青鱼), '
        '"market": 市场或地区名(尽量全称), '
        '"spec": 规格(如 条重≥750g / 标鳜 / 9两上), '
        '"price": 价格数字或区间字符串(如 72 或 "10.5-11"), '
        '"unit": 单位(元/千克 或 元/斤), '
        '"price_date": 报价日期(YYYY-MM-DD，若图中无则留空)}。'
        "只输出 JSON 数组，不要解释。"
    )
    records = []
    for img in image_paths:
        b64 = base64.b64encode(open(img, "rb").read()).decode()
        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": sys_prompt},
                {"role": "user", "content": [
                    {"type": "text", "text": f"来源公众号：{source}。请抽取价格表。"},
                    {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{b64}"}},
                ]},
            ],
            "temperature": 0,
        }
        r = requests.post(f"{api_base.rstrip('/')}/chat/completions",
                          headers={"Authorization": f"Bearer {api_key}",
                                   "Content-Type": "application/json"},
                          json=payload, timeout=120)
        r.raise_for_status()
        text = r.json()["choices"][0]["message"]["content"]
        # 容错：抽取首个 JSON 数组
        m = re.search(r"\[.*\]", text, re.S)
        if not m:
            print(f"[WARN] {os.path.basename(img)} 未解析到 JSON", file=sys.stderr)
            continue
        try:
            rows = json.loads(m.group(0))
        except json.JSONDecodeError:
            print(f"[WARN] {os.path.basename(img)} JSON 解析失败", file=sys.stderr)
            continue
        for row in rows:
            row["source"] = source
            row.setdefault("article_date", "")
            row.setdefault("note", "")
            records.append(row)
    return records


def ocr_tesseract(image_paths, source):
    """本地 tesseract 兜底（中文表格式 OCR，准确度低于 vision，仅应急）。"""
    try:
        from PIL import Image
        import pytesseract
    except ImportError:
        raise RuntimeError("tesseract 兜底需要 pip install pillow pytesseract 且系统安装 tesseract")
    records = []
    for img in image_paths:
        txt = pytesseract.image_to_string(Image.open(img), lang="chi_sim+eng")
        for line in txt.splitlines():
            m = re.search(r"(鳜|桂|鲈|青)\S*\s*([\d./\-]+)", line)
            if m:
                records.append({"source": source, "species": m.group(1),
                                "market": line[:10], "spec": "",
                                "price": m.group(2), "unit": "元/千克",
                                "price_date": "", "article_date": "", "note": "tesseract粗提"})
    return records


# ----------------------------------------------------------------------------
# 结构化落库
# ----------------------------------------------------------------------------
def load_current() -> dict:
    if os.path.exists(CURRENT_JSON):
        return json.load(open(CURRENT_JSON, encoding="utf-8"))
    # 从最新历史快照初始化
    files = sorted(glob.glob(os.path.join(HERE, "wechat_ocr_prices_*.json")))
    data = {}
    if files:
        for r in json.load(open(files[-1], encoding="utf-8")):
            data.setdefault(r.get("source", "?"), []).append(r)
    return data


def save_current(data: dict):
    json.dump(data, open(CURRENT_JSON, "w", encoding="utf-8"),
              ensure_ascii=False, indent=2)


def snapshot(data: dict, run_date: str):
    out = os.path.join(HERE, f"wechat_ocr_prices_{run_date}.json")
    all_rows = []
    for rows in data.values():
        all_rows.extend(rows)
    json.dump(all_rows, open(out, "w", encoding="utf-8"),
              ensure_ascii=False, indent=2)
    return out


def vs_cell(vs: str) -> str:
    """环比单元格：涨红跌绿（中式行情配色），新增蓝、持平灰。"""
    if not vs:
        return "<td></td>"
    if "新增" in vs:
        color = "#2563eb"
    elif "持平" in vs:
        color = "#6b7280"
    elif "↑" in vs:
        color = "#dc2626"
    else:
        color = "#12a150"
    return f'<td style="color:{color};font-size:12px;white-space:nowrap">{vs}</td>'


# ----------------------------------------------------------------------------
# 生成看板板块 HTML
# ----------------------------------------------------------------------------
def build_sci_section(rows):
    """科学养鱼：批发价，元/千克。"""
    art = rows[0].get("article_date") or rows[0].get("price_date") or ""
    price_date = rows[0].get("price_date") or art
    species_list = "、".join(sorted({r["species"] for r in rows}))
    has_vs = any(r.get("vs") for r in rows)
    vs_head = rows[0].get("vs_header") or "环比"
    # 按品种分组
    groups = {}
    for r in rows:
        groups.setdefault(r["species"], []).append(r)
    grids = []
    for sp, items in groups.items():
        trs = "".join(
            f'<tr><td>{r["market"]}</td>'
            f'<td><span class="spec spec-s">{r.get("spec","")}</span></td>'
            f'<td class="price">{fmt_price(r.get("price"))}</td>'
            f'{vs_cell(r.get("vs","")) if has_vs else ""}</tr>'
            for r in items)
        vs_th = f"<th>{vs_head}</th>" if has_vs else ""
        grids.append(
            f'<div><h3 style="font-size:14px;margin:6px 0 8px">'
            f'<span class="tag {species_tag(sp)}">{sp}</span> 批发价（元/千克）</h3>'
            f'<table><thead><tr><th>市场</th><th>规格</th><th>价格</th>{vs_th}</tr></thead>'
            f'<tbody>{trs}</tbody></table></div>')
    return (
        '  <section>\n'
        '    <div class="sec-head">\n'
        '      <span class="bar" style="background:#7c3aed"></span>\n'
        '      <h2>补充 · 「科学养鱼」公众号批发价（OCR 提取）</h2>\n'
        f'      <span class="note">{art} · 元/千克 · 已按图片数字录入</span>\n'
        '    </div>\n'
        '    <div class="card">\n'
        '      <h3>🌟 科学养鱼公众号 全国水产品批发价</h3>\n'
        f'      <div class="csub">来源：公众号价格截图，单位<b>元/千克</b>；由 OCR 提取，'
        f'报价日期 {price_date}。本次含 <b>{species_list}</b> 条目。</div>\n'
        '      <div class="grid2">' + "".join(grids) + '</div>\n'
        '      <div class="callout" style="margin-top:14px"><b>数据说明：</b>'
        '该公众号价格以<b>图片</b>形式发布，纯文本爬虫取不到数字；由截图 + OCR 提取录入。'
        '① 单位已确认为<b>元/千克</b>；② 属批发价，可与农业农村部统货口径互补；'
        '③ 历史截图数据保留于 <code>wechat_ocr_prices_*.json</code> 历史快照。</div>\n'
        '    </div>\n'
        '  </section>')


def build_a_section(rows):
    """a渔业行情：塘口价，元/斤。"""
    art = rows[0].get("article_date") or rows[0].get("price_date") or ""
    price_date = rows[0].get("price_date") or art
    species_list = "、".join(sorted({r["species"] for r in rows}))
    has_vs = any(r.get("vs") for r in rows)
    vs_head = rows[0].get("vs_header") or "环比"
    groups = {}
    for r in rows:
        groups.setdefault(r["species"], []).append(r)
    grids = []
    for sp, items in groups.items():
        trs = "".join(
            f'<tr><td>{r["market"]}</td>'
            f'<td><span class="spec spec-s">{r.get("spec","")}</span></td>'
            f'<td class="price">{fmt_price(r.get("price"))}</td>'
            f'{vs_cell(r.get("vs","")) if has_vs else ""}</tr>'
            for r in items)
        vs_th = f"<th>{vs_head}</th>" if has_vs else ""
        grids.append(
            f'<div><h3 style="font-size:14px;margin:6px 0 8px">'
            f'<span class="tag {species_tag(sp)}">{sp}</span> 报价（元/斤）</h3>'
            f'<table><thead><tr><th>地区</th><th>规格</th><th>塘口价</th>{vs_th}</tr></thead>'
            f'<tbody>{trs}</tbody></table></div>')
    return (
        '  <section>\n'
        '    <div class="sec-head">\n'
        '      <span class="bar" style="background:#059669"></span>\n'
        '      <h2>补充 · 「a渔业行情」公众号塘口价（OCR 提取）</h2>\n'
        f'      <span class="note">{price_date} 全国水产塘口价 · 元/斤</span>\n'
        '    </div>\n'
        '    <div class="card">\n'
        '      <h3>🎣 a渔业行情公众号 分产区塘口价</h3>\n'
        f'      <div class="csub">来源：公众号文章截图，由 OCR 提取。报价日期 <b>{price_date}</b>；'
        f'<b>单位元/斤</b>，属塘口（出塘）价，与批发价不可直接比较。含 <b>{species_list}</b>。</div>\n'
        '      <div class="grid2">' + "".join(grids) + '</div>\n'
        '      <div class="callout" style="margin-top:14px"><b>数据说明：</b>'
        '「a渔业行情」文章以<b>图片表格</b>发布，搜狗微信未索引且需登录/反爬，纯文本爬虫取不到；'
        '由截图 + OCR 提取。<b>单位为元/斤</b>（塘口价），与水产前沿周报口径一致，可与批发价交叉验证。</div>\n'
        '    </div>\n'
        '  </section>')


def merge_into_dashboard(sci_html, a_html):
    html = open(DASHBOARD, encoding="utf-8").read()
    for start, end, block in ((SCI_START, SCI_END, sci_html),
                              (A_START, A_END, a_html)):
        i = html.find(start)
        j = html.find(end)
        if i < 0 or j < 0 or j < i:
            raise RuntimeError(f"未找到锚点：{start} / {end}")
        # 保留锚点注释，替换中间内容（含缩进）
        html = html[:i + len(start)] + "\n" + block + "\n  " + html[j:]
    open(DASHBOARD, "w", encoding="utf-8").write(html)
    return True


# ----------------------------------------------------------------------------
# 主流程
# ----------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--images", nargs="+", help="截图文件路径")
    ap.add_argument("--source", choices=["科学养鱼", "a渔业行情"], help="截图所属来源")
    ap.add_argument("--json", help="直接载入已有结构化 JSON（跳过 OCR）")
    ap.add_argument("--rebuild", action="store_true", help="仅用 current.json 重建板块")
    ap.add_argument("--no-commit", action="store_true", help="不 git commit")
    args = ap.parse_args()

    data = load_current()
    run_date = datetime.date.today().strftime("%Y%m%d")
    changed = False

    if args.rebuild:
        pass
    elif args.json:
        new_rows = json.load(open(args.json, encoding="utf-8"))
        for r in new_rows:
            src = r.get("source")
            if src in data:
                data[src] = new_rows  # 整批替换该来源
                break
        # 更稳妥：按来源分别替换
        by_src = {}
        for r in new_rows:
            by_src.setdefault(r.get("source"), []).append(r)
        for src, rows in by_src.items():
            data[src] = rows
        changed = True
    elif args.images:
        if not args.source:
            print("[ERR] --images 需配合 --source", file=sys.stderr)
            sys.exit(1)
        api_base = os.environ.get("OCR_API_BASE") or "https://api.siliconflow.cn/v1"
        api_key = os.environ.get("OCR_API_KEY")
        model = os.environ.get("OCR_MODEL", "Qwen/Qwen2.5-VL-72B-Instruct")
        if api_key:
            print(f"[OCR] vision 适配器：{model}")
            rows = ocr_vision(args.images, args.source, api_base, api_key, model)
        else:
            print("[OCR] 未设置 OCR_API_KEY，尝试 tesseract 兜底")
            rows = ocr_tesseract(args.images, args.source)
        if rows:
            data[args.source] = rows
            changed = True
            print(f"[OCR] {args.source} 提取 {len(rows)} 条")
        else:
            print("[OCR] 未提取到记录，跳过", file=sys.stderr)
    else:
        ap.print_help()
        sys.exit(0)

    if changed:
        save_current(data)
        snapshot(data, run_date)

    sci_rows = data.get("科学养鱼", [])
    a_rows = data.get("a渔业行情", [])
    if not sci_rows or not a_rows:
        print("[WARN] 缺少某一来源数据，板块可能不全", file=sys.stderr)
    sci_html = build_sci_section(sci_rows) if sci_rows else ""
    a_html = build_a_section(a_rows) if a_rows else ""
    merge_into_dashboard(sci_html, a_html)
    print(f"[OK] 已并入看板：科学养鱼 {len(sci_rows)} 条 / a渔业行情 {len(a_rows)} 条")

    if not args.no_commit:
        try:
            subprocess.run(["git", "add", "-A"], check=True, cwd=HERE)
            subprocess.run(["git", "commit", "-q", "-m",
                            f"update: 公众号 OCR 流水线并入（{run_date}）"],
                           check=True, cwd=HERE)
            print("[OK] 已 git commit")
        except Exception as e:
            print(f"[WARN] git commit 失败: {e}", file=sys.stderr)


if __name__ == "__main__":
    main()
