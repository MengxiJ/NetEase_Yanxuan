# 网易严选 App 自动化测试框架

面向网易严选 App（Appium + UiAutomator2 + 模拟器）的企业级自动化测试框架，覆盖功能、UI 界面、接口、性能、并发与安全测试，共 **101 条自动化用例，全部通过**。采用自研的「Step/Check 原子化 + JSON 工作流编排」架构，新增测试场景仅需声明式 JSON 并注册原子方法，无需编写测试代码。

> 📄 **最新全量回归测试报告（2026-09-25，101条：101 通过 / 0 失败，通过率 100.0%）：**
> [PDF 测试报告](report_assets/test_report.pdf)

## 核心亮点

- **声明式工作流引擎**：测试场景以 JSON（nodes + edges 节点图）描述，由 Step/Check 原子方法注册表驱动，新增场景零测试代码
- **无接口文档的接口测试方案**：Charles 抓包回放 + 自建本地 Mock 契约，无接口文档、无外网也能验证接口行为
- **企业级非功能覆盖**：性能（延迟分位数/吞吐/持续负载）、并发（一致性/无丢失更新/故障稳定性）、安全（注入/越权/信息泄露）、回归（冒烟 ⊂ 回归 ⊂ 全量）
- **登录态自动保障**：`session_guard` 自动检测并恢复登录态，消除登出用例对后续用例的跨用例状态污染
- **可视化测试报告**：Allure 报告含环境信息、失败分类、失败截图，一键生成并自动打开浏览器
- **分层解耦架构**：PO（纯 locator）→ 原子实现层（Step/Check）→ 工作流编排层，职责清晰、易维护扩展
- **标准化治理**：统一 step/check 返回值结构、元素定位自动重试、失败自动截图、Allure 报告

## 技术栈
Python + Appium + PO（Page Object）+ Pytest + Allure + JSON 工作流驱动 + Requests（接口层）

## 框架设计理念
- **Step/Check 分离**：步骤节点（step）与检查节点（check）独立注册、独立目录管理
- **统一返回值规范**：所有操作返回标准化结构，便于日志与断言
- **JSON 工作流驱动**：测试场景以 `tblocks/workflows/**/*.json` 声明（nodes + edges 节点图），
  按类别分组（function/ 功能测试、ui/ 界面测试），新增场景只需新增 JSON 文件并注册原子方法
- **分层架构**：
  - `base/` → 公共能力
  - `pages/` → 纯元素定位层（locator，受保护前缀）
  - `tblocks/step_impl/ + check_impl/` → 原子方法实现与注册层（实现类继承 page 复用 locator）
  - `tblocks/utils/composer.py` → 工作流编排器
  - `tblocks/workflow_runner.py` → 执行主入口
  - `scripts/` → pytest 统一执行入口
  - `api/` → 接口测试层（无接口文档方案：Charles 抓包回放 + 本地 Mock 契约）
- **异常处理与重试**：元素定位内置重试机制；接口层连接失败自动重试
- **实例管理**：页面实例/驱动统一管理，测试隔离；Mock 服务随测试会话启停（随机端口）

## 目录结构
```
pythonProject11/
├── base/                       # 基础层：公共操作封装（元素定位、操作、检查、截图、统一返回值）
│   ├── __init__.py             # 日志器初始化
│   └── page_base.py            # 页面对象基类（元素定位、操作、检查、截图、统一返回值）
├── pages/                      # 页面对象层：纯元素定位（locator，受保护前缀 `_`）
│   ├── page_01_login.py        # 登录页
│   ├── page_02_address.py      # 地址管理页
│   ├── page_03_search.py       # 搜索页
│   ├── page_04_cart.py         # 购物车页
│   ├── page_05_order.py        # 订单页（下单 OrderPage + 订单查询 GetOrderPage）
│   ├── page_home.py            # 首页（弹窗处理、底部导航）
│   ├── page_goods_detail.py    # 商品详情页
│   ├── page_mine.py            # 个人中心页
│   └── page_category.py        # 分类页
├── tblocks/                     # ★ 原子化测试框架（Step/Check 注册 + 工作流编排）
│   ├── __init__.py             # 导入顺序：step_impl → check_impl → 执行器
│   ├── workflow_runner.py      # 工作流执行主入口（run_workflow 便捷函数）
│   ├── registry.py             # Step/Check 注册表 + step()/check() 注册函数
│   ├── step_impl/              # ★ 步骤节点注册（按业务域分组，导入即注册）
│   │   ├── login_steps.py      #   登录步骤（协议/邮箱切换/输入/提交）
│   │   ├── search_steps.py     #   搜索步骤
│   │   ├── cart_steps.py       #   购物车步骤
│   │   ├── order_steps.py      #   订单步骤（结算/提交）
│   │   ├── home_steps.py       #   首页步骤（弹窗关闭/Tab切换）
│   │   ├── goods_steps.py      #   商品详情步骤（进详情/加购/立即购买）
│   │   ├── address_steps.py    #   地址步骤
│   │   └── settings_steps.py   #   设置步骤（进设置/退出登录）
│   ├── check_impl/             # ★ 检查节点注册（按业务域分组，导入即注册）
│   │   ├── login_checks.py     #   登录检查（成功/失败提示）
│   │   ├── search_checks.py    #   搜索结果检查
│   │   ├── cart_checks.py      #   加购成功检查
│   │   ├── order_checks.py     #   订单存在/订单页加载检查
│   │   ├── home_checks.py      #   首页核心元素检查
│   │   ├── goods_checks.py     #   商品详情元素检查
│   │   ├── address_checks.py   #   地址添加成功检查
│   │   ├── category_checks.py  #   分类页商品列表/价格检查
│   │   ├── mine_checks.py      #   个人中心核心元素检查
│   │   └── settings_checks.py  #   设置页元素/退出登录检查
│   ├── utils/
│   │   ├── composer.py         # ★ 工作流编排器（节点执行、路由、变量解析）
│   │   └── session_guard.py    # ★ 登录态自动保障（检测+恢复登录，消除跨用例污染）
│   └── workflows/              # ★ JSON 工作流用例（按类别分组）
│       ├── function/           #   功能测试
│       │   ├── login_success.json       # P0 登录成功
│       │   ├── login_failed.json        # P1 登录失败（错误密码）
│       │   ├── search_goods.json        # P0 商品搜索（3组关键词参数化）
│       │   ├── add_to_cart.json         # P0 加入购物车
│       │   ├── add_address.json         # P1 添加收货地址
│       │   ├── order_flow.json          # P0 下单到支付页打开验证
│       │   ├── order_status_check.json  # P1 待付款列表页面加载验证
│       │   ├── home_navigation.json     # P0 底部导航切换
│       │   ├── logout.json              # P0 退出登录
│       │   ├── search_no_result.json    # P1 搜索无结果
│       │   ├── search_to_detail.json    # P1 搜索进入商品详情
│       │   ├── buy_now.json             # P0 立即购买
│       │   ├── cart_after_add.json      # P1 加购后购物车联动
│       │   ├── search_back_home.json    # P1 返回键回首页
│       │   ├── goods_detail_back.json   # P1 返回键回搜索结果
│       │   ├── sku_add_cart.json        # P1 规格选择加购
│       │   └── settings_back.json       # P1 返回键回个人中心
│       └── ui/                 #   UI界面测试
│           ├── home_ui_check.json       # P1 首页界面检查
│           ├── goods_detail_check.json  # P1 商品详情界面检查
│           ├── mine_page_check.json     # P1 个人中心界面检查
│           ├── category_check.json      # P1 分类页界面检查
│           ├── cart_page_check.json     # P1 购物车界面检查
│           ├── search_page_check.json   # P1 搜索页界面检查
│           └── settings_check.json      # P1 设置页界面检查
├── scripts/                    # 测试用例层（统一入口）
│   ├── test_workflow.py        # 自动发现工作流并参数化执行 + 资产门禁
│   └── test_smoke.py           # 冒烟测试（环境健康 + 资产门禁 + 接口健康）
├── api/                        # ★ 接口测试层（无接口文档方案）
│   ├── config.py               #   接口配置（客户端超时重试 / Mock / HAR 回放规则）
│   ├── client.py               #   HTTP 客户端封装（超时/重试/日志统一治理）
│   ├── mock_server.py          #   本地 Mock 服务（标准库实现：严选风格契约 + 鉴权/限流注入
│   │                           #   + 故障/延迟注入 + 安全契约：413 请求体上限/405 方法白名单/nosniff 头）
│   ├── conftest.py             #   Mock 服务 fixture（会话级启停，随机端口）
│   ├── utils/
│   │   └── har_replay.py       #   HAR 解析 / 过滤 / 域名重写 / 回放参数构建
│   ├── cases/
│   │   ├── test_mock_api.py    #   Mock 契约用例（登录/搜索/购物车/订单/商品详情/用户信息/优惠券/容错/性能）
│   │   ├── test_har_replay.py  #   HAR 抓包回放用例（状态码类别/JSON结构/响应时间比对）
│   │   ├── test_performance.py #   性能测试（延迟分位数/吞吐QPS/持续负载/稳定性，指标附Allure）
│   │   ├── test_concurrency.py #   并发测试（并发登录/读/写无丢失更新/读写混合/故障稳定性）
│   │   └── test_security.py    #   安全测试（SQL注入/XSS/越权/信息泄露/413/405/安全头）
│   └── data/captured/          #   Charles 导出的 HAR 存放目录（内置 sample.har 示例）
├── img/                        # 截图存储（失败自动截图）
├── log/                        # 日志存储（按天滚动）
├── report/                     # Allure 原始结果（pytest 运行时生成）
├── report_assets/              # ★ 报告相关资产（脚本 + 分类模板 + PDF 报告）
│   ├── generate_pdf_report.py  #   PDF 测试报告生成脚本
│   ├── cmd_allure.py           #   Allure HTML 报告一键生成（复制分类+生成HTML+打开浏览器）
│   ├── categories.json         #   Allure 失败分类模板
│   └── test_report.pdf         #   生成的 PDF 测试报告
├── config.py                   # 项目配置（设备、应用、账号）
├── conftest.py                 # Pytest fixture + 失败截图钩子 + 环境信息生成
├── tools.py                    # 工具层（驱动管理、日志）
└── pytest.ini                  # Pytest 配置（markers: smoke/regression/ui/workflow）
```

## 调用链
```
scripts/test_workflow.py        # pytest 入口：自动发现 + 参数化 + 动态标记
    │
    ▼
tblocks/workflow_runner.py       # 执行主入口
    │
    ▼
tblocks/utils/composer.py        # 编排器：加载JSON、调度节点图、解析变量
    ├── step_impl/*.py          #   step 节点 → registry 解析
    │   └── pages/*.py          #     → 页面对象方法（base/page_base.py 统一返回值）
    └── check_impl/*.py         #   check 节点 → registry 解析
        └── pages/*.py          #     → 页面对象检查方法
```

## 工作流 JSON 结构
```json
{
  "id": "yanxuan/function/login_success",
  "display_name": "网易严选登录成功",
  "category": "function",          // feature 维度（function/ui），对应分组目录
  "module": "login",               // story 维度
  "suites": "smoke",               // pytest marker（smoke/regression/ui）
  "priority": "P0",
  "precondition": "1. ...",
  "expected": "登录成功，显示用户昵称",
  "metadata": {
    "driver": "first_app_driver"   // 声明所需 fixture（app_driver=免登录 / first_app_driver=清数据）
  },
  "nodes": [
    {"id": "step_click_login", "type": "step", "step_id": "click_login", "params": {}},
    {"id": "check_login_success", "type": "check", "check_id": "check_login_success", "params": {}}
  ],
  "edges": [
    {"source": "step_click_login", "target": "check_login_success", "condition": "pass"}
  ]
}
```

要点：
- `step_id` / `check_id` 必须已在 `tblocks/step_impl/` 或 `tblocks/check_impl/` 中注册
- `params` 支持 `${custom_params.xxx}` 变量引用（由编排器解析，账号自动注入）
- 节点失败且配置了 `fail` 边时走恢复分支，否则终止工作流
- 新增 JSON 文件（放至 function/ 或 ui/ 分组）后自动纳入测试，无需改代码

## 新增原子方法流程
1. 在 `pages/` 对应页面类中实现方法（step 返回 `step_result()`，check 返回 `check_result()`）
2. 在 `tblocks/step_impl/` 或 `tblocks/check_impl/` 对应业务域模块中调用 `step()` / `check()` 注册
3. 新建工作流 JSON 引用该 step_id / check_id

## 统一返回值规范

### Step 返回值
```python
{
    "step": "step_name",
    "status": True/False,
    "message": "描述",
    "data": {...},
    "timestamp": "YYYY-mm-dd HH:MM:SS"
}
```

### Check 返回值
```python
{
    "check": "check_name",
    "result": True/False,
    "status": True/False,
    "message": "描述",
    "expected": "期望值",
    "actual": "实际值",
    "data": {...},
    "timestamp": "YYYY-mm-dd HH:MM:SS"
}
```

## 环境准备

| 依赖 | 说明 |
|------|------|
| Python | 3.10（Anaconda 环境） |
| Appium Server | 2.x（`/wd/hub`）/ 3.x（根路径），默认 `127.0.0.1:4723` |
| Android 设备 | MuMu 模拟器（Android 12，udid `127.0.0.1:7555`） |
| 被测应用 | 网易严选 `com.netease.yanxuan` |

核心 Python 依赖：`appium-python-client`、`selenium`、`pytest`、`allure-pytest`、`requests`。

运行前需启动 Appium Server 并保持模拟器在线（`adb devices` 可发现设备）；账号信息通过 `config.py` 的 `ACCOUNT` 注入，不随代码仓库提交。

## 运行方式
```bash
# 运行全部测试（App 工作流 + 接口 + 冒烟，101 条用例）
pytest

# 运行冒烟测试（P0 核心链路 + 环境健康检查）
pytest -m smoke

# 运行 UI 界面测试
pytest -m ui

# 运行全部接口测试（Mock 契约 + HAR 抓包回放）
pytest -m api

# 仅运行 Mock 契约测试
pytest -m mock

# 仅运行 Charles 抓包回放测试
pytest -m har

# 性能测试（延迟分位数 / 吞吐 / 持续负载 / 稳定性）
pytest -m perf

# 并发测试（并发一致性 / 无丢失更新 / 故障稳定性）
pytest -m concurrent

# 安全测试（注入 / 越权 / 信息泄露 / 报文规范 / 安全头）
pytest -m security

# 回归测试（全量用例集：功能 + UI + 接口 + 性能/并发/安全 + 冒烟，冒烟 ⊂ 回归）
pytest -m regression

# 运行单个工作流（按用例 id 过滤，id 为相对路径）
pytest -k "login_success"
pytest -k "function/order_flow"

# 仅运行功能测试分组
pytest -k "function"

# 仅校验工作流资产完整性（无设备依赖）
pytest scripts/test_workflow.py::TestWorkflow::test_list_workflows

# 冒烟严格模式（CI 卡点：环境不就绪直接失败而非跳过）
SMOKE_STRICT=1 pytest scripts/test_smoke.py

# 生成 Allure 报告并自动打开浏览器
python report_assets/cmd_allure.py

# 仅生成报告不打开浏览器
python report_assets/cmd_allure.py --no-open

# 或直接启动 Allure 在线服务
allure serve report
```

## 测试报告（Allure）

框架集成 Allure 可视化报告，运行 pytest 后自动生成原始数据，一键生成 HTML 报告。

### 报告内容
- **环境信息**（`environment.properties`）：Python 版本、操作系统、Appium 版本、Allure 版本、App 包名/Activity、设备 UDID、Appium 服务地址
- **失败分类**（`categories.json`）：断言失败、元素定位失败、Appium 服务异常、接口请求失败、测试框架异常、其他失败
- **失败截图**：用例失败时自动截图并附加到报告
- **步骤记录**：每个工作流节点的执行日志

### 生成方式
```bash
# 1. 运行测试（pytest.ini 已配置 --alluredir report，自动生成原始数据）
pytest

# 2. 生成 HTML 报告并自动打开浏览器
python report_assets/cmd_allure.py

# 仅生成不打开
python report_assets/cmd_allure.py --no-open
```

## 登录态自动保障

`conftest.py` 的 `app_driver` fixture 在创建驱动后调用 `tblocks/utils/session_guard.py` 的 `ensure_logged_in(driver)`，自动检测并恢复登录态：
1. 归位首页，关闭遮挡浮层
2. 进入「个人」tab 检测 `user_name` 元素
3. 已登录则返回首页；未登录则条件切换密码模式后自动登录

该机制消除了 `logout` 用例（以未登录态收尾）对后续依赖登录态用例的跨用例状态污染。

## 订单流程说明

本项目**不执行真实支付**，订单相关用例设计如下：
- **`order_flow`**：购物车 → 结算 → 提交订单 → **验证支付页已打开**（检测订单确认页提交按钮消失 + 支付页 WebView 出现）
- **`order_status_check`**：进入「个人 → 待付款」列表，验证页面加载成功（有订单编号或空列表提示均通过）

## 接口测试（无接口文档方案）

项目没有接口文档的情况下，接口测试通过两条路径实现：

### 路径一：Charles 抓包回放（-m har）
1. **抓包**：手机代理指向 Charles，HTTPS 需信任 Charles 根证书后解密
2. **导出**：Charles `File → Export Session… → HAR File`，导出到 `api/data/captured/`
3. **回放**：`pytest -m har` 框架自动逐条重发请求并校验：
   - 状态码类别比对（2xx/4xx/5xx，容忍 token 过期导致的 401↔403 漂移）
   - JSON 可解析性
   - 响应顶层结构键比对（抓包存有响应正文时，检测接口结构变更）
   - 响应时间阈值（默认 5s）
4. **环境切换**：`api/config.py` 的 `HAR_CONFIG.url_rewrite` 支持域名重写
   （生产抓包 → 测试环境回放；内置 sample.har 演示重写至本地 Mock）
5. **过滤治理**：`include_hosts` / `exclude_hosts`（剔除埋点统计流量）、
   `exclude_extensions`（剔除静态资源）、`max_entries`（防 HAR 过大）、
   `headers_override`（回放时注入有效凭据）

### 路径二：本地 Mock 契约测试（-m mock）
`api/mock_server.py` 基于标准库 http.server 自建 Mock 后端（随机端口、随会话启停），
定义严选风格契约（HTTP 200 + 业务码 code 分离），覆盖登录/搜索/购物车/订单，
支持故障注入（500）与延迟注入（性能阈值演练），验证客户端与服务端契约一致。

### 接口层规范
- 用例统一通过 `api/client.py` 的 ApiClient 发请求（禁止直接 import requests），
  超时/重试/日志集中治理
- Mock 服务 fixture 会话级启停，与 App 自动化层完全解耦，无设备/外网依赖

## 冒烟测试（-m smoke）
`scripts/test_smoke.py` 最小集合快速验证环境与框架就绪：
- 框架资产门禁（注册表 / 工作流 JSON 完整性，必须通过）
- P0 冒烟链路资产（≥7 条 P0 工作流已注册）
- Appium 服务健康（GET /status，ready 校验）
- 设备在线（adb devices）与 APP 安装（pm list packages）
- 接口层健康（本地 Mock 服务 /status）

环境依赖离线时跳过（skip）而非失败；`SMOKE_STRICT=1` 切换为严格模式用于 CI 卡点。
`pytest -m smoke` 同时命中 P0 工作流用例（suites=smoke），组成完整冒烟集。

## 性能测试（-m perf）
`api/cases/test_performance.py` 基于本地 Mock 服务的轻量性能基线（零外部依赖）：
- **延迟分位数**：/status 采样 40 次，P50/P90/P95/P99 统计并断言 P95 阈值
- **延迟注入有效性**：验证服务端延迟真实生效（均值 ≥ 注入值 80%）
- **吞吐量**：QPS 下限断言（接入真实系统后按 SLA 收紧）
- **持续负载**：4 线程压测 2.5s，零错误率 + 完成量下限
- **稳定性**：混合请求（健康/搜索/订单）最大延迟阈值

指标经 logger 输出并以 JSON attachment 附加到 Allure 报告。
接入真实被测系统仅需切换 base_url；大规模压测可平滑迁移 Locust/JMeter（本层保留为基线校验）。

## 并发测试（-m concurrent）
`api/cases/test_concurrency.py` 验证服务端线程安全与数据一致性：
- **并发登录**（20 线程）：全部成功且 token/昵称一致
- **并发读**（30 线程，命中+未命中混合）：结构完整、零失败
- **并发写**（20 线程加购）：无丢失更新（最终数量 == 基线 + 20）
- **读写混合**（10 写 + 10 读）：读者始终读到自洽快照（count == 明细数量总和）
- **故障并发**（15 线程 500 注入）：错误码准确、服务不崩溃且故障后恢复

## 安全测试（-m security）
`api/cases/test_security.py` 覆盖 OWASP 常见风险的接口层基线（15 条）：
| 风险类别 | 用例 |
|---|---|
| 注入防护 | SQL 注入载荷（搜索/登录，3 组参数化）不崩溃、不绕过鉴权、不泄露数据 |
| XSS 防护 | 载荷以惰性数据返回（JSON 上下文，无 HTML 执行环境） |
| 越权防护 | 受保护接口（订单）无 token / 无效 token 一律 401，有效 token 放行 |
| 信息泄露 | 密码不回显；错误响应不含堆栈/文件路径等内部细节 |
| 报文规范 | 超大请求体 413 拒绝；畸形 JSON 优雅处理（400 非 500）；PUT/DELETE/PATCH/OPTIONS 统一 405 |
| 安全响应头 | X-Content-Type-Options: nosniff |

配套的 Mock 服务安全契约（`api/mock_server.py`）：
订单接口登录态校验（Authorization: mock-token-*）、请求体 1MB 上限（超限先排空再 413）、
方法白名单（非 GET/POST 统一 405 业务 JSON）、nosniff 安全响应头。

## 回归测试（-m regression）
回归集 = **全量 101 条用例**（功能 17 + UI 16 工作流（36 条含参数化与门禁）+ 接口 59 含性能/并发/安全 + 冒烟 6），
标记治理遵循企业惯例 **冒烟 ⊂ 回归 ⊂ 全量**：
- 工作流用例：P0 冒烟（suites=smoke）与 UI 用例同时挂 regression 标记
- 接口/性能/并发/安全/冒烟用例：全部挂 regression 标记
- 资产门禁（test_list_workflows）纳入回归集

日常推荐节奏：`pytest -m smoke`（提交前）→ `pytest -m api`（接口变更）→ `pytest -m regression`（发版前全量）。

## 测试覆盖（共 101 条用例：工作流 36 + 接口 59 + 冒烟 6）
| 分组 | 模块 | 工作流 | 优先级 |
|------|------|--------|--------|
| function | 登录 | login_success | P0 |
| function | 登录 | login_failed | P1 |
| function | 搜索 | search_goods（毛巾/牛奶/饼干 3 组参数） | P0 |
| function | 购物车 | add_to_cart | P0 |
| function | 地址 | add_address | P1 |
| function | 订单 | order_flow | P0 |
| function | 订单 | order_status_check | P1 |
| function | 首页 | home_navigation | P0 |
| function | 登录 | logout | P0 |
| function | 搜索 | search_no_result | P1 |
| function | 搜索 | search_to_detail | P1 |
| function | 订单 | buy_now | P0 |
| function | 购物车 | cart_after_add（加购后购物车联动） | P1 |
| function | 搜索 | search_back_home（返回键回首页） | P1 |
| function | 商品 | goods_detail_back（返回键回搜索结果） | P1 |
| function | 商品 | sku_add_cart（规格选择加购） | P1 |
| function | 设置 | settings_back（返回键回个人中心） | P1 |
| ui | 首页 | home_ui_check | P1 |
| ui | 商品详情 | goods_detail_check | P1 |
| ui | 个人中心 | mine_page_check | P1 |
| ui | 分类 | category_check | P1 |
| ui | 购物车 | cart_page_check | P1 |
| ui | 搜索 | search_page_check | P1 |
| ui | 设置 | settings_check | P1 |
| ui | 登录 | login_page_ui_check（登录页元素/协议/输入框） | P1 |
| ui | 首页 | home_deep_ui_check（核心元素汇总/消息/推荐） | P1 |
| ui | 商品详情 | goods_detail_full_ui_check（名称/主图/按钮/规格） | P1 |
| ui | 个人中心 | mine_service_ui_check（昵称/待付款/收藏/设置） | P1 |
| ui | 个人中心 | mine_asset_ui_check（余额/优惠券/红包/积分/礼品卡） | P1 |
| ui | 个人中心 | mine_order_service_ui_check（订单/待评价/足迹/退换/客服） | P1 |
| ui | 搜索 | search_result_ui_check（结果命中/条目/价格） | P1 |
| ui | 首页 | tab_switch_ui_check（底部四 Tab 轮巡） | P1 |
| ui | 搜索 | search_flow_ui_check（搜索页到结果页联动） | P1 |

接口测试覆盖（api/cases，-m api，共 59 条）：
| 类型 | 用例文件 | 覆盖点 |
|------|----------|--------|
| Mock 契约 | test_mock_api.py（28 条） | 健康检查 / 登录成功·失败·参数缺失 / 搜索命中（3 组参数化）·空结果 / 购物车添加查询一致性·参数校验·更新数量校验 / 商品详情结构·不存在·参数校验 / 用户信息鉴权（登录态·越权） / 优惠券领取·重复领取 / 订单结构·状态筛选（登录态） / 故障注入 500 / 未知路由 404 / 响应时间阈值 / Content-Type 规范 |
| 抓包回放 | test_har_replay.py（6 条） | HAR 结构合法性 / 逐条回放比对（状态码类别 + JSON 顶层结构键 + 响应时间），内置 sample.har 演示域名重写回放 |
| 性能 | test_performance.py（5 条） | 延迟分位数 P50/P90/P95/P99 / 延迟注入有效性 / 吞吐 QPS / 持续负载（4 线程·零错误）/ 混合请求稳定性 |
| 并发 | test_concurrency.py（5 条） | 并发登录一致性 / 并发读结构完整 / 并发写无丢失更新 / 读写混合快照自洽 / 故障并发稳定性与恢复 |
| 安全 | test_security.py（15 条） | SQL 注入（3 组）/ 注入不绕过鉴权 / XSS 惰性数据 / 密码不回显 / 越权 401 / 方法 405（4 组）/ 超大报文 413 / 畸形 JSON / 错误无内部细节 / nosniff 安全头 |

冒烟测试覆盖（scripts/test_smoke.py，-m smoke）：
| 检查项 | 依赖 |
|--------|------|
| 框架资产门禁（注册表 + 工作流完整性） | 无 |
| P0 冒烟链路资产（≥7 条） | 无 |
| Appium 服务健康 | Appium |
| 设备在线（adb） | adb + 模拟器 |
| APP 已安装 | adb + 模拟器 |
| 接口层健康（Mock /status） | 无 |

