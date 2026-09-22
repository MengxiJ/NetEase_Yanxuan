"""
冒烟测试（Smoke）：环境健康 + 框架资产门禁 + 接口服务健康

设计原则（企业级）：
- 最小集合、快速执行，用于版本包 / 环境就绪判断（发布前卡点）
- 环境类检查（Appium / 设备 / APP 安装）在依赖离线时 skip 而非失败，
  设置环境变量 SMOKE_STRICT=1 可切换为强校验模式（CI 卡点用）
- 框架资产门禁不依赖设备，任何时候都必须通过
- pytest -m smoke 同时会命中 P0 工作流用例（suites=smoke），组成完整冒烟集
"""
import os
import shutil
import subprocess

import allure
import pytest

from api.client import ApiClient
from api.config import MOCK_CONFIG
from api.mock_server import start_mock_server, stop_mock_server
from base import logger
from config import APPIUM_SERVER, APP_CONFIG, DEVICE_CONFIG

SMOKE_STRICT = os.environ.get("SMOKE_STRICT", "") == "1"
DEVICE_UDID = DEVICE_CONFIG["udid"]
APP_PACKAGE = APP_CONFIG["appPackage"]


def _require(condition, reason):
    """冒烟环境检查统一出口：严格模式失败，宽松模式跳过"""
    if not condition:
        if SMOKE_STRICT:
            pytest.fail("[冒烟-严格模式] {}".format(reason))
        pytest.skip("[冒烟-环境不就绪] {}".format(reason))


@allure.feature("冒烟测试")
@pytest.mark.smoke
@pytest.mark.regression
class TestSmoke:
    """冒烟测试集合（发布/环境就绪判断）"""

    def test_framework_assets(self):
        """框架资产门禁：注册表与工作流 JSON 完整（无需设备，必须通过）"""
        from tblocks import WorkflowExecutor
        from tblocks.registry import CHECK_REGISTRY, STEP_REGISTRY
        from scripts.test_workflow import REQUIRED_WORKFLOWS

        assert len(STEP_REGISTRY) >= 20, "step 注册数异常: {}".format(len(STEP_REGISTRY))
        assert len(CHECK_REGISTRY) >= 30, "check 注册数异常: {}".format(len(CHECK_REGISTRY))
        workflows = WorkflowExecutor.list_workflows()
        missing = [wf for wf in REQUIRED_WORKFLOWS if wf not in workflows]
        assert not missing, "缺少工作流: {}".format(missing)

    def test_p0_workflows_registered(self):
        """P0 冒烟链路资产就绪：核心优先级工作流数量达标"""
        import json

        from config import BASE_DIR

        workflow_dir = os.path.join(BASE_DIR, "tblocks", "workflows")
        p0_workflows = []
        for root, _, files in os.walk(workflow_dir):
            for name in files:
                if not name.endswith(".json"):
                    continue
                with open(os.path.join(root, name), encoding="utf-8-sig") as f:
                    wf = json.load(f)
                if wf.get("priority") == "P0":
                    p0_workflows.append(wf.get("id", name))
        logger.info("[Smoke] P0 工作流: {}".format(p0_workflows))
        assert len(p0_workflows) >= 7, "P0 工作流数量不足: {}".format(p0_workflows)

    def test_appium_server_health(self):
        """Appium 服务健康检查（GET /status）"""
        client = ApiClient(timeout=5, max_retries=0)
        try:
            resp = client.get("{}/status".format(APPIUM_SERVER))
        except Exception as exc:
            _require(False, "Appium 服务不可达: {}".format(exc))
            return
        assert resp.status_code == 200, "Appium /status 返回 {}".format(resp.status_code)
        # Appium 2.x/3.x 响应结构: {"value": {"ready": true, ...}}
        assert resp.json()["value"]["ready"] is True, "Appium 未就绪: {}".format(resp.text)

    def test_device_online(self):
        """设备在线检查（adb devices）"""
        adb = shutil.which("adb")
        _require(bool(adb), "未找到 adb 命令")
        output = subprocess.run(
            [adb, "devices"], capture_output=True, text=True, timeout=15
        ).stdout
        _require(
            "{}\tdevice".format(DEVICE_UDID) in output,
            "设备不在线: {}\n{}".format(DEVICE_UDID, output.strip()),
        )

    def test_app_installed(self):
        """被测 APP 已安装检查"""
        adb = shutil.which("adb")
        _require(bool(adb), "未找到 adb 命令")
        result = subprocess.run(
            [adb, "-s", DEVICE_UDID, "shell", "pm", "list", "packages"],
            capture_output=True, text=True, timeout=30,
        )
        _require(result.returncode == 0, "adb 查询包列表失败: {}".format(result.stderr.strip()))
        _require(APP_PACKAGE in result.stdout, "APP 未安装: {}".format(APP_PACKAGE))

    def test_api_mock_service(self):
        """接口层冒烟：本地 Mock 服务健康（无需外部网络与设备）"""
        server, base_url = start_mock_server(MOCK_CONFIG["host"], MOCK_CONFIG["port"])
        try:
            client = ApiClient(base_url=base_url)
            resp = client.get("/status")
            assert resp.status_code == 200
            assert resp.json()["code"] == 200
        finally:
            stop_mock_server(server)
