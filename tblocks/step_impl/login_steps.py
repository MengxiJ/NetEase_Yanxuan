"""
登录模块步骤实现（step 逻辑从 pages 迁出）
"""
import time

from base import logger
from base.page_base import step_result
from config import APP_CONFIG
from tblocks.registry import step
from pages.page_01_login import LoginPage


class LoginSteps(LoginPage):
    """登录模块 Step 实现（复用 LoginPage 元素定位与 PageBase 底层操作）"""

    def click_agreed(self):
        """点击同意协议"""
        logger.info("[Step] 点击同意协议")
        return self.base_click(self._agree)

    def click_mine(self):
        """点击个人中心（含清数据首启闪退恢复）"""
        logger.info("[Step] 点击个人中心")
        self._ensure_home_after_launch()
        return self.base_click(self._mine)

    def _ensure_home_after_launch(self):
        """清数据首启后 App 会在 SplashActivity 闪退到桌面，检测到后二次拉起并等待首页"""
        recovered = False
        for _ in range(12):
            try:
                act = self.driver.current_activity or ''
                src = self.driver.page_source or ''
            except Exception:
                time.sleep(2)
                continue
            if 'MainPageActivity' in act or 'tv_home_search' in src:
                return True
            if '.yanxuan' not in src and not recovered:
                logger.info("[登录] 检测到首启闪退到桌面，二次拉起 App")
                try:
                    self.driver.activate_app(APP_CONFIG["appPackage"])
                except Exception as e:
                    logger.warning(f"[登录] 二次拉起失败: {e}")
                recovered = True
                time.sleep(3)
                continue
            time.sleep(2)
        return False

    def switch_login_type(self):
        """切换到密码登录模式（手机号+密码），并勾选同意协议"""
        logger.info("[Step] 切换登录方式为密码登录")
        self.base_click(self._change_mode)
        self.base_click(self._agree_checkbox)
        return step_result("switch_login_type", True, "已切换到密码登录模式")

    def input_username(self, username):
        """输入用户名"""
        logger.info(f"[Step] 输入用户名: {username}")
        return self.base_input_text(self._username, username)

    def input_password(self, password):
        """输入密码"""
        logger.info("[Step] 输入密码")
        return self.base_input_text(self._password, password)

    def click_login(self):
        """点击登录按钮"""
        logger.info("[Step] 点击登录按钮")
        return self.base_click(self._login_btn)


step("click_agreed", LoginSteps, "click_agreed")
step("click_mine", LoginSteps, "click_mine")
step("switch_login_type", LoginSteps, "switch_login_type")
step("input_username", LoginSteps, "input_username")
step("input_password", LoginSteps, "input_password")
step("click_login", LoginSteps, "click_login")
