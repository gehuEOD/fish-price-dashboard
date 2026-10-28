# 鳜鱼 · 鲈鱼 价格看板（农业农村部批发价爬虫）

自动抓取**农业农村部「重点农产品市场信息平台」**（ncpscxx.moa.gov.cn）全国批发市场中
**活鳜鱼 / 淡水鲈鱼 / 海水鲈鱼** 的当日批发价，并配套一份江浙沪皖价格数据看板。

## 两版看板（并存发布，互不覆盖）

| 版本 | 线上地址 | 定位 | 更新机制 |
|------|---------|------|---------|
| **v1 · 数据总览版** | `https://fishmarket.gehueod.cn/` | 全量行情明细、多源溯源、数据新鲜度 | 气象 09:00 + 价格 09:30 双工作流 |
| **v2 · 决策版** | `https://fishmarket.gehueod.cn/v2/` | 三角色视图（老板/技术员/采购员），每角色独立「今日行动清单」 | 每日 **09:15** 单一工作流重算并重渲染 |

两版共用同一套数据源；v2 由 `build_dashboard_v2.py` 从数据文件 + 模板生成，**不要手改生成物**：
- 模板：`dashboard_v2_template.html`
- 人工核校源（塘口价 / 病害 / 本地渠道）：`v2_manual_prices.json`
- 版本：`dashboard_v2_version.json`
- 产出：`dashboard-v2/index.html`

```bash
python3 build_dashboard_v2.py              # 重新生成 v2
python3 build_dashboard_v2.py --bump patch # 生成并升版本号
```

## 数据来源

| 维度 | 来源 | 说明 |
|------|------|------|
| 批发价 | `moa_fish_crawler.py` 直连农业农村部批发价接口 | 逆向异步接口 + AES-256-CBC 解密，抓取当日各市场报价 |
| 塘头价（出塘价） | 水产前沿《特水鱼周报》、腾氏水产播报 | 分产区分规格，行业权威周报 |
| 看板 | `鳜鱼鲈鱼价格看板.html` | 本地静态 HTML，浏览器直接打开 |

## 目录结构

```
moa_fish_crawler.py                 # 农业农村部批发价爬虫（AES 解密、三品种抓取、历史累积）
inject_moa_block.py                 # 把当日 MOA 快照注入 v1 看板（KPI/明细表/口径说明，幂等）
fish_prices.csv / fish_prices.json # 当日快照（覆盖写）
fish_prices_history.csv/.json/.js  # 历史累积（追加写，.js 供看板读取）
.github/workflows/daily-crawl.yml  # GitHub Actions 每日定时抓取并提交
鳜鱼鲈鱼价格看板.html              # 价格数据看板（爬虫当日批发价 + 周报塘头价 + 历史序列图，已内联 Chart.js 与历史数据，离线可用）
inline_assets.py                   # 把 Chart.js 与历史数据内联进看板 HTML（离线渲染）
chart.umd.min.js                   # 本地 Chart.js v4.4.1（inline_assets.py 的内联源）
```

## 使用方法

```bash
# 抓取全部市场，写出当日快照 + 追加到历史
python moa_fish_crawler.py

# 仅输出江苏及周边（江浙沪皖）市场
python moa_fish_crawler.py --region
```

依赖：`pycryptodome`（`urllib`/`ssl` 为标准库）。脚本会自动安装缺失依赖。

### 注入 v1 看板的 MOA 区块（口径自动推导，勿手改）

v1 的「鲈鱼批发 KPI + 活鳜明细表 + 数据说明」不再手工维护，由爬虫结果推导：

```bash
python inject_moa_block.py            # 注入并写回 鳜鱼鲈鱼价格看板.html（幂等）
python inject_moa_block.py --check    # 只体检：打印数据日/中位数、HTML 是否需更新
python inject_moa_block.py --dry-run  # 打印将生成的四段内容，不落盘
```

四个锚点（成对出现，缺一即报错）：`MOA_KPI_LU`（鲈鱼批发 KPI）、`MOA_GUI_FRAG`（鳜鱼 KPI 趋势内片段）、
`MOA_ROWS`（明细表行）、`MOA_CALLOUT`（数据说明自动段）。手工叙述（历史对比、销地新闻）留在锚点外，不受影响。

口径三条（与 v2 决策版一致）：**全国中枢取中位数**（算术平均会被远距离销区单侧拉高约 50%，仅在说明里作反面参照）；
**远距离销区（乌鲁木齐/甘肃/宁夏/青海/拉萨等）只作销地参考，不构成跨区套利**；
**批发价不可直接当收购上限，须倒扣流通成本**（鳜鱼 3 元/斤、鲈鱼 1 元/斤）。

某品种当日 `data=null` 时脚本**跳过该品种替换**、保留看板原值，不会把 KPI 写成空。

## 产出文件

| 文件 | 作用 |
|------|------|
| `fish_prices.csv` / `fish_prices.json` | 当日快照（覆盖写），看板「批发价」板块数据源 |
| `fish_prices_history.csv` / `.json` / `.js` | **历史累积**（追加写，按日期去重）。看板已通过 `inline_assets.py` 把历史数据**内联**进 HTML，不再依赖此外部文件，单文件离线打开图表也能显示 |

## 历史 30 天序列怎么来

农业农村部该接口**只返当日快照、无历史日期参数**；而能查历史的 `FarmDaily`/`common-price-avg` 接口只覆盖「重点监测 46 品种」，**不含鳜鱼、鲈鱼**。
因此**唯一稳妥路径是逐日累积**：每天定时跑一次爬虫，把当日快照追加到 `fish_prices_history.*`，约 30 天后即得完整 30 天逐日序列。看板「六、历史价格序列」板块会自动读取并绘图。

## 离线渲染（图表内联）

看板里的「价格可视化对比」与「历史价格序列」两张图由 Chart.js 绘制。为避免 `file://` 直接打开时因 CDN / 网络被拦截而图不显示，已将 Chart.js 源码与 `fish_prices_history.js` 的历史数据**内联**进 `鳜鱼鲈鱼价格看板.html`，使其成为完全自包含的单文件。

每次更新完数据后，重跑一次即可重新内联：

```bash
python inline_assets.py
```

前置：`chart.umd.min.js`（本地 Chart.js v4.4.1）与 `fish_prices_history.js` 与本脚本同目录。（需升级 Chart.js 时，重新下载对应 UMD 覆盖 `chart.umd.min.js` 后重跑。）

## 定时更新（GitHub Actions 已就绪）

仓库已包含 `.github/workflows/daily-crawl.yml`：

- 触发：`cron` 每天 UTC 09:00（≈北京时间 17:00）+ 手动 `workflow_dispatch`
- 流程：检出 → 装 `pycryptodome` → 跑爬虫 → 有变化则提交 `fish_prices_*` 回仓库
- 推送用内置 `GITHUB_TOKEN`，**无需你额外提供令牌**（仅首次把本仓库 push 上去后 Actions 才会运行）

如需本地定时，也可 `crontab -e` 加一行每日执行 `python /path/moa_fish_crawler.py`。

## 重要说明（数据边界）

1. 接口报价为**统货价、不分 500g 内/外规格**；分规格需求以水产前沿周报塘头价为准。
2. 品种编码：活鳜鱼 `AM01013003`、淡水鲈鱼 `AM01009`、海水鲈鱼 `AM02005`。
3. 价格随行就市，仅供参考。

