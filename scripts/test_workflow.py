"""
工作流驱动测试入口（统一入口）

自动发现 tblocks/workflows/**/*.json 并参数化生成测试用例：
- 按 category 分组目录组织（function/ 功能测试、ui/ 界面测试），用例 id 为相对路径
- 根据 JSON metadata.driver 选择测试驱动 fixture
  （app_driver 免登录 / first_app_driver 清数据首启）
- 根据 JSON suites 字段动态挂载 pytest marker（smoke / regression / ui）
- 根据 JSON category / module / priority 动态生成 Allure 元数据
- 搜索类工作流通过 WORKFLOW_PARAMS 注入多组关键词参数

新增工作流 JSON 后无需修改本文件即可自动纳入测试。
"""
import json
import os

import pytest
import allure

from base import logger
from config import BASE_DIR
from tblocks import WorkflowExecutor
from tblocks.registry import STEP_REGISTRY, CHECK_REGISTRY

WORKFLOW_DIR = os.path.join(BASE_DIR, "tblocks", "workflows")

# 需要参数化的工作流：文件名 -> custom_params 组列表（每组生成一条用例）
WORKFLOW_PARAMS = {
    "search_goods.json": [
        {"keyword": "毛巾"},
        {"keyword": "牛奶"},
        {"keyword": "饼干"},
    ],
}

# 工作流资产完整性校验清单（模块全覆盖：功能 + UI界面，相对路径）
REQUIRED_WORKFLOWS = [
    "function/login_success.json",       # 功能-登录成功
    "function/login_failed.json",        # 功能-登录失败
    "function/search_goods.json",        # 功能-商品搜索
    "function/add_to_cart.json",         # 功能-加入购物车
    "function/add_address.json",         # 功能-添加收货地址
    "function/order_flow.json",          # 功能-下单端到端
    "function/order_status_check.json",  # 功能-待付款订单查询
    "function/home_navigation.json",     # 功能-底部导航切换
    "function/logout.json",              # 功能-退出登录
    "function/search_no_result.json",    # 功能-搜索无结果
    "function/search_to_detail.json",    # 功能-搜索进入商品详情
    "function/buy_now.json",             # 功能-立即购买
    "function/cart_after_add.json",      # 功能-加购后购物车联动
    "function/search_back_home.json",    # 功能-搜索页返回键回首页
    "function/goods_detail_back.json",   # 功能-详情页返回键回搜索结果
    "function/sku_add_cart.json",        # 功能-规格选择加购
    "function/settings_back.json",       # 功能-设置页返回键回个人中心
    "ui/home_ui_check.json",             # UI-首页界面检查
    "ui/goods_detail_check.json",        # UI-商品详情界面检查
    "ui/mine_page_check.json",           # UI-个人中心界面检查
    "ui/category_check.json",            # UI-分类页界面检查
    "ui/cart_page_check.json",           # UI-购物车界面检查
    "ui/search_page_check.json",         # UI-搜索页界面检查
    "ui/settings_check.json",            # UI-设置页界面检查
    "ui/login_page_ui_check.json",       # UI-登录页界面检查
    "ui/home_deep_ui_check.json",        # UI-首页深度界面检查
    "ui/goods_detail_full_ui_check.json",# UI-详情页完整界面检查
    "ui/mine_service_ui_check.json",     # UI-个人中心服务区界面检查
    "ui/mine_asset_ui_check.json",       # UI-个人中心资产区界面检查
    "ui/mine_order_service_ui_check.json",  # UI-个人中心订单与服务入口检查
    "ui/search_result_ui_check.json",    # UI-搜索结果页界面检查
    "ui/tab_switch_ui_check.json",       # UI-底部Tab轮巡界面检查
    "ui/search_flow_ui_check.json",      # UI-搜索页到结果页联动检查
]


def _load_workflow(path):
    with open(path, mode="r", encoding="utf-8-sig") as f:
        return json.load(f)


def _collect_cases():
    """递归扫描工作流目录，生成参数化用例（按相对路径排序保证依赖顺序）"""
    cases = []
    for root, _, files in os.walk(WORKFLOW_DIR):
        for file_name in sorted(files):
            if not file_name.endswith(".json"):
                continue
            path = os.path.join(root, file_name)
            rel_path = os.path.relpath(path, WORKFLOW_DIR).replace("\\", "/")
            wf = _load_workflow(path)
            suite = wf.get("suites", "regression")
            marks = [getattr(pytest.mark, suite)]
            # 回归集为全量：冒烟/UI 工作流同时挂 regression 标记（冒烟 ⊂ 回归 ⊂ 全量）
            if suite != "regression":
                marks.append(pytest.mark.regression)
            param_groups = WORKFLOW_PARAMS.get(file_name, [{}])
            for params in param_groups:
                if params:
                    case_id = "{}[{}]".format(rel_path[:-5], list(params.values())[0])
                else:
                    case_id = rel_path[:-5]
                cases.append(pytest.param(path, params, case_id, marks=marks, id=case_id))
    return sorted(cases, key=lambda c: c.id)


CASES = _collect_cases()


@pytest.mark.workflow
class TestWorkflow:
    """基于 JSON 工作流的功能与UI界面测试"""

    @pytest.mark.parametrize("workflow_path,custom_params,case_id", CASES)
    def test_execute_workflow(self, workflow_path, custom_params, case_id, request):
        """执行单条工作流：加载JSON -> 动态打标签 -> 调度节点图 -> 断言结果"""
        wf = _load_workflow(workflow_path)

        # 动态生成 Allure 元数据（报告按 category / module / priority 分层展示）
        allure.dynamic.feature(wf.get("category", "workflow"))
        allure.dynamic.story(wf.get("module", "workflow"))
        allure.dynamic.title(wf.get("display_name", case_id))
        allure.dynamic.description(
            "{}\n\n前置条件:\n{}\n\n预期结果:\n{}".format(
                wf.get("description", ""),
                wf.get("precondition", ""),
                wf.get("expected", ""),
            )
        )
        allure.dynamic.tag(wf.get("priority", "P1"))

        # 根据工作流声明选择测试驱动（免登录 / 清数据首启）
        driver_name = wf.get("metadata", {}).get("driver", "app_driver")
        driver = request.getfixturevalue(driver_name)
        # 注册到 funcargs，保证 conftest 失败截图钩子可获取 driver
        request.node.funcargs[driver_name] = driver

        logger.info("========== 工作流用例: {} (driver={}) ==========".format(case_id, driver_name))
        executor = WorkflowExecutor(driver, custom_params=custom_params)
        result = executor.execute(workflow_path)

        logger.info(
            "工作流结果: success={}, executed={}, failed_node={}".format(
                result["success"], result["executed_nodes"], result["failed_node"]
            )
        )
        assert result["success"], (
            "工作流 {} 执行失败，失败节点: {}".format(case_id, result["failed_node"])
        )

    @pytest.mark.regression
    def test_list_workflows(self):
        """工作流资产门禁（无设备依赖）：
        1. 模块全覆盖（功能 + UI界面）
        2. 每个工作流的节点引用均已注册（step_id / check_id）
        3. 边的 source / target 均存在于节点列表
        """
        workflows = WorkflowExecutor.list_workflows()
        logger.info("可用工作流({}): {}".format(len(workflows), workflows))

        missing = [wf for wf in REQUIRED_WORKFLOWS if wf not in workflows]
        assert not missing, "缺少工作流: {}".format(missing)

        for rel_path in workflows:
            wf = _load_workflow(os.path.join(WORKFLOW_DIR, rel_path))
            nodes = wf.get("nodes", [])
            edges = wf.get("edges", [])
            node_ids = {n["id"] for n in nodes}

            assert nodes, "{}: nodes 为空".format(rel_path)
            for node in nodes:
                if node["type"] == "step":
                    assert node.get("step_id") in STEP_REGISTRY, (
                        "{}: 未注册的 step_id: {}".format(rel_path, node.get("step_id"))
                    )
                elif node["type"] == "check":
                    assert node.get("check_id") in CHECK_REGISTRY, (
                        "{}: 未注册的 check_id: {}".format(rel_path, node.get("check_id"))
                    )
                else:
                    raise AssertionError(
                        "{}: 未知节点类型 {}".format(rel_path, node["type"])
                    )
            for edge in edges:
                assert edge["source"] in node_ids, (
                    "{}: 边 source 不存在: {}".format(rel_path, edge)
                )
                assert edge["target"] in node_ids, (
                    "{}: 边 target 不存在: {}".format(rel_path, edge)
                )
