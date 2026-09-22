"""
工作流编排器
参照 AutoTestRes 原子化框架的 tblocks/utils/composer.py 设计：
加载 tblocks/workflows/**/*.json，按 nodes + edges 调度 step/check 节点图
"""
import json
import os
import re

from base import logger
from config import BASE_DIR, ACCOUNT
from tblocks.registry import STEP_REGISTRY, CHECK_REGISTRY


class WorkflowExecutor:
    """工作流编排器：节点执行、路由、变量解析"""

    def __init__(self, driver, custom_params=None):
        """
        Args:
            driver: Appium driver 实例
            custom_params: 自定义参数（如 username/password/keyword），
                           支持工作流中 ${custom_params.xxx} 引用
        """
        self.driver = driver
        self.custom_params = custom_params or {}
        # 默认注入账号配置
        self.custom_params.setdefault("username", ACCOUNT.get("username", ""))
        self.custom_params.setdefault("password", ACCOUNT.get("password", ""))
        # 页面实例缓存
        self._page_instances = {}
        # 节点执行结果缓存
        self._node_results = {}

    def _resolve_params(self, params):
        """解析参数中的 ${custom_params.xxx} 变量引用"""
        if not params:
            return {}
        resolved = {}
        for key, value in params.items():
            if isinstance(value, str):
                resolved[key] = self._resolve_var(value)
            else:
                resolved[key] = value
        return resolved

    def _resolve_var(self, text):
        """解析 ${custom_params.xxx} 形式的变量"""
        pattern = r"\$\{custom_params\.(\w+)\}"
        def replacer(m):
            return str(self.custom_params.get(m.group(1), ""))
        return re.sub(pattern, replacer, text)

    def _get_page(self, page_cls):
        """获取或创建页面实例（单例缓存）"""
        key = page_cls.__name__
        if key not in self._page_instances:
            self._page_instances[key] = page_cls(self.driver)
        return self._page_instances[key]

    def _execute_node(self, node):
        """执行单个节点（step 或 check）"""
        node_type = node.get("type")
        node_id = node.get("id")
        params = self._resolve_params(node.get("params", {}))

        if node_type == "step":
            step_id = node.get("step_id")
            registry_entry = STEP_REGISTRY.get(step_id)
            if not registry_entry:
                logger.error(f"未注册的 step: {step_id}")
                return False
            page_cls, method_name = registry_entry
            page = self._get_page(page_cls)
            method = getattr(page, method_name)
            logger.info(f"[Workflow Step] {node_id}: {step_id}({params})")
            result = method(**params)
            # step 返回统一结构 {status: True/False, ...}
            success = result.get("status", False) if isinstance(result, dict) else True
            self._node_results[node_id] = result
            return success

        elif node_type == "check":
            check_id = node.get("check_id")
            registry_entry = CHECK_REGISTRY.get(check_id)
            if not registry_entry:
                logger.error(f"未注册的 check: {check_id}")
                return False
            page_cls, method_name = registry_entry
            page = self._get_page(page_cls)
            method = getattr(page, method_name)
            logger.info(f"[Workflow Check] {node_id}: {check_id}({params})")
            result = method(**params)
            # check 返回统一结构 {result: True/False, ...}
            success = result.get("result", False) if isinstance(result, dict) else False
            self._node_results[node_id] = result
            logger.info(f"[Workflow Check] {node_id} result={success}")
            return success

        logger.error(f"未知节点类型: {node_type}")
        return False

    def _get_next_nodes(self, current_id, edges, condition):
        """根据当前节点和条件获取下一批节点"""
        return [
            e["target"] for e in edges
            if e["source"] == current_id and e.get("condition") == condition
        ]

    def execute(self, workflow_json_path):
        """
        执行工作流

        Args:
            workflow_json_path: workflow JSON 文件路径

        Returns:
            dict: 执行结果 {success, workflow_id, executed_nodes, failed_node, results}
        """
        # utf-8-sig 兼容带/不带 BOM 的文件
        with open(workflow_json_path, mode="r", encoding="utf-8-sig") as f:
            workflow = json.load(f)

        workflow_id = workflow.get("id", "unknown")
        nodes = workflow.get("nodes", [])
        edges = workflow.get("edges", [])
        metadata = workflow.get("metadata", {})

        logger.info(f"========== 开始执行工作流: {workflow_id} ==========")

        # 构建节点索引
        node_map = {n["id"]: n for n in nodes}

        # 寻找起始节点（无入边的节点）
        incoming = set(e["target"] for e in edges)
        start_nodes = [n["id"] for n in nodes if n["id"] not in incoming]
        if not start_nodes:
            start_nodes = [nodes[0]["id"]] if nodes else []

        executed = []
        failed_node = None
        overall_success = True

        try:
            # 1. setup_hooks（driver 生命周期由 conftest fixture 管理，此处记录声明）
            for hook in metadata.get("setup_hooks", []):
                logger.info(f"[Workflow Setup Hook] {hook}")

            # 2. 执行主流程节点图（按边顺序遍历）
            current_nodes = list(start_nodes)
            while current_nodes:
                next_nodes = []
                aborted = False
                for node_id in current_nodes:
                    node = node_map.get(node_id)
                    if not node:
                        continue
                    executed.append(node_id)
                    success = self._execute_node(node)
                    if success:
                        next_nodes.extend(self._get_next_nodes(node_id, edges, "pass"))
                    else:
                        failed_node = node_id
                        overall_success = False
                        # 节点失败：若配置了 fail 边则继续走恢复分支，否则终止
                        fail_next = self._get_next_nodes(node_id, edges, "fail")
                        if fail_next:
                            next_nodes.extend(fail_next)
                        else:
                            aborted = True
                            break
                if aborted:
                    break
                current_nodes = next_nodes

        finally:
            # 3. teardown_hooks（逆序）
            for hook in reversed(metadata.get("teardown_hooks", [])):
                logger.info(f"[Workflow Teardown Hook] {hook}")

        result = {
            "success": overall_success,
            "workflow_id": workflow_id,
            "executed_nodes": executed,
            "failed_node": failed_node,
            "results": self._node_results,
        }
        logger.info(f"========== 工作流 {workflow_id} 执行完成: success={overall_success} ==========")
        return result

    @staticmethod
    def list_workflows():
        """列出所有可用工作流（递归扫描 tblocks/workflows，返回相对路径）"""
        workflow_dir = os.path.join(BASE_DIR, "tblocks", "workflows")
        workflows = []
        if os.path.exists(workflow_dir):
            for root, _, files in os.walk(workflow_dir):
                for f in files:
                    if f.endswith(".json"):
                        rel = os.path.relpath(os.path.join(root, f), workflow_dir)
                        workflows.append(rel.replace("\\", "/"))
        return sorted(workflows)
