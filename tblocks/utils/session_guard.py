"""
会话状态保障（app_driver 专用）

背景：logout 等用例以未登录态收尾，pytest 按用例 id 字母序执行时，
中段运行的登出用例会污染其后所有依赖登录态的用例（底部 tab 被登录
引导浮层遮挡、个人中心无昵称、订单列表要求重新登录等）。

app_driver fixture 建立会话后调用 ensure_logged_in：
归位首页 -> 关闭遮挡浮层 -> 进入个人中心检测登录态 -> 必要时自动
密码登录 -> 回到首页。异常不向上抛出，不阻塞用例启动。
"""
import time

from appium.webdriver.common.appiumby import By

from base import logger
from config import APP_CONFIG, ACCOUNT
from tblocks.step_impl.home_steps import HomeSteps
from tblocks.step_impl.login_steps import LoginSteps


def ensure_logged_in(driver):
    """确保 App 已登录并回到首页（对外入口，吞异常）"""
    try:
        _ensure(driver)
    except Exception as e:
        logger.error(f"[SessionGuard] 登录态保障异常（不阻塞用例）: {e}")


def _ensure(driver):
    home = HomeSteps(driver)
    login = LoginSteps(driver)

    # 1. 归位首页（处理开屏广告/落地页延续，必要时重启 App）
    home.close_popup()

    # 2. 未登录态首页可能出现登录引导浮层遮挡底部 tab（与开屏广告同 id），先关闭
    if home.is_element_exist(home._splash_cancel, timeout=2):
        try:
            driver.find_element(*home._splash_cancel).click()
            time.sleep(1)
        except Exception:
            pass

    # 3. 进入个人中心检测登录态
    tab_res = home.click_tab("个人")
    if not tab_res["status"]:
        logger.warning("[SessionGuard] 无法进入个人中心，跳过登录态检测")
        return
    time.sleep(2)
    if login.is_element_exist(login._nickname, timeout=5):
        logger.info("[SessionGuard] 已登录，回到首页")
        home.click_tab("首页")
        return

    # 4. 未登录：在登录页执行密码登录（短信验证码模式则先切换为密码模式）
    logger.info("[SessionGuard] 检测到未登录，执行自动登录")
    sms_mode = (By.ID, f'{APP_CONFIG["appPackage"]}:id/btn_get_sms')
    if login.is_element_exist(sms_mode, timeout=3):
        login.base_click(login._change_mode)
        time.sleep(1)
    login.base_click(login._agree_checkbox)
    login.base_input_text(login._username, ACCOUNT["username"])
    login.base_input_text(login._password, ACCOUNT["password"])
    login.base_click(login._login_btn)
    time.sleep(6)
    home.close_popup()
    logger.info("[SessionGuard] 自动登录完成")
