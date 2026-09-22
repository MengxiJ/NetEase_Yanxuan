import os
import time

import pytest
import allure
from appium import webdriver
from appium.options.android import UiAutomator2Options

from base import logger
from config import *
from tools import get_timestamp_str
from tblocks.utils.session_guard import ensure_logged_in


def _create_driver(reset_app=False):
    """创建 Appium 驱动"""
    app_cfg = dict(APP_CONFIG)
    if reset_app:
        app_cfg.pop("noReset", None)
    des_caps = {**DEVICE_CONFIG, **app_cfg}
    option = UiAutomator2Options().load_capabilities(des_caps)
    return webdriver.Remote(APPIUM_SERVER, options=option)


@pytest.fixture
def app_driver():
    """免登录 fixture（保留登录状态；自动保障登录态，消除登出用例的跨用例状态污染）"""
    logger.info("[Fixture] 创建 APP 驱动（免登录模式）")
    driver = _create_driver(reset_app=False)
    ensure_logged_in(driver)
    yield driver
    logger.info("[Fixture] 关闭 APP 驱动")
    time.sleep(3)
    driver.quit()


@pytest.fixture
def first_app_driver():
    """首次启动 fixture（清除数据）"""
    logger.info("[Fixture] 创建 APP 驱动（首次启动模式）")
    driver = _create_driver(reset_app=True)
    yield driver
    logger.info("[Fixture] 关闭 APP 驱动")
    time.sleep(3)
    driver.quit()


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """测试失败时自动截图并附加到 Allure 报告"""
    outcome = yield
    report = outcome.get_result()

    if report.when == "call" and report.failed:
        # 获取 driver 对象（从 fixture 中）
        driver = None
        for fixture_name in ["app_driver", "first_app_driver"]:
            if fixture_name in item.funcargs:
                driver = item.funcargs[fixture_name]
                break

        if driver:
            try:
                img_dir = os.path.join(BASE_DIR, "img")
                os.makedirs(img_dir, exist_ok=True)
                # 用例名可能包含 "/"（如 function/buy_now），需替换为合法文件名字符
                safe_name = item.name.replace("/", "_").replace("\\", "_").replace(":", "_")
                img_name = f"failure_{safe_name}_{get_timestamp_str()}.png"
                img_path = os.path.join(img_dir, img_name)
                driver.get_screenshot_as_file(img_path)
                logger.error(f"[失败截图] 已保存: {img_path}")

                # 附加到 Allure 报告
                with open(img_path, "rb") as f:
                    allure.attach(
                        f.read(),
                        name=img_name,
                        attachment_type=allure.attachment_type.PNG,
                    )
            except Exception as e:
                logger.error(f"[失败截图] 截图失败: {e}")


def pytest_sessionfinish(session, exitstatus):
    """测试会话结束时生成 Allure 环境信息文件（environment.properties）"""
    import platform
    try:
        alluredir = session.config.getoption("--alluredir")
        if not alluredir:
            return
        os.makedirs(alluredir, exist_ok=True)
        env_path = os.path.join(alluredir, "environment.properties")
        from importlib.metadata import version as pkg_version
        try:
            appium_ver = pkg_version("Appium-Python-Client")
        except Exception:
            appium_ver = "unknown"
        try:
            allure_ver = pkg_version("allure-pytest")
        except Exception:
            allure_ver = "unknown"
        lines = [
            f"Python.Version={platform.python_version()}",
            f"Platform.System={platform.system()}",
            f"Platform.Release={platform.release()}",
            f"Appium.Version={appium_ver}",
            f"Allure.Version={allure_ver}",
            f"App.Package={APP_CONFIG.get('appPackage', '')}",
            f"App.Activity={APP_CONFIG.get('appActivity', '')}",
            f"Device.UDID={DEVICE_CONFIG.get('udid', '')}",
            f"Appium.Server={APPIUM_SERVER}",
        ]
        with open(env_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
        logger.info(f"[Allure] 环境信息已写入: {env_path}")
    except Exception as e:
        logger.error(f"[Allure] 生成环境信息失败: {e}")
