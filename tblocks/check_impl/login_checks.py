"""
登录模块检查实现（check 逻辑从 pages 迁出）
"""
import time

from base import logger
from base.page_base import check_result
from tblocks.registry import check
from pages.page_01_login import LoginPage


class LoginChecks(LoginPage):
    """登录模块 Check 实现（复用 LoginPage 元素定位与 PageBase 底层能力）"""

    def check_login_success(self, expected_text=None):
        """登录成功判定：离开登录页（账号输入框消失）"""
        logger.info("[Check] 验证登录成功")
        for _ in range(10):
            if not self.is_element_exist(self._username, timeout=2):
                return check_result("check_login_success", True, "登录成功")
            time.sleep(1)
        return check_result("check_login_success", False, "登录失败：账号输入框仍存在")

    def get_failed_text(self):
        """获取登录失败 Toast 提示"""
        return self.base_get_toast(self._fail_text)

    def check_login_failed(self, expected_text=None):
        """登录失败判定：错误密码登录后仍停留在登录页（账号输入框仍可见）。

        真机 dump 证实错误密码登录后页面无 Toast 元素（瞬时提示不可靠），
        改用"未离开登录页"作为失败信号；expected_text 仅作为用例意图记录。
        """
        logger.info("[Check] 验证登录失败（仍停留在登录页）")
        time.sleep(2)  # 等待可能的页面跳转
        still_on_login = self.is_element_exist(self._username, timeout=5)
        toast = ""
        if not still_on_login:
            # 兜底：若恰好捕获到 Toast 也认可
            toast = self.base_get_toast(self._fail_text, timeout=2)
        result = still_on_login or bool(toast)
        return check_result(
            "check_login_failed",
            result,
            f"登录失败检查{'通过' if result else '失败'}",
            expected=expected_text or "停留在登录页",
            actual="仍停留在登录页" if still_on_login else (f"Toast: {toast}" if toast else "已离开登录页（疑似登录成功）"),
        )


    def check_login_page_loaded(self):
        """登录页加载判定：登录视图关键元素（切换登录方式入口 + 登录按钮）可见"""
        logger.info("[Check] 验证登录页加载")
        mode_visible = self.is_element_exist(self._change_mode, timeout=5)
        btn_visible = self.is_element_exist(self._login_btn, timeout=5)
        result = mode_visible and btn_visible
        return check_result(
            "check_login_page_loaded",
            result,
            f"登录页加载检查{'通过' if result else '失败'}",
            expected="切换入口与登录按钮均可见",
            actual=f"切换入口={mode_visible}, 登录按钮={btn_visible}",
        )

    def check_login_input_visible(self):
        """账号密码输入框可见判定（切换到邮箱登录模式后）"""
        logger.info("[Check] 验证账号密码输入框可见")
        user_visible = self.is_element_exist(self._username, timeout=5)
        pwd_visible = self.is_element_exist(self._password, timeout=5)
        result = user_visible and pwd_visible
        return check_result(
            "check_login_input_visible",
            result,
            f"账号密码输入框检查{'通过' if result else '失败'}",
            expected="账号与密码输入框均可见",
            actual=f"账号框={user_visible}, 密码框={pwd_visible}",
        )


    def check_login_agreement_visible(self):
        """协议勾选框可见判定（登录页底部）"""
        logger.info("[Check] 验证协议勾选框可见")
        return self.check_element_visible(self._agree_checkbox)


check("check_login_success", LoginChecks, "check_login_success")
check("check_login_failed", LoginChecks, "check_login_failed")
check("check_login_page_loaded", LoginChecks, "check_login_page_loaded")
check("check_login_input_visible", LoginChecks, "check_login_input_visible")
check("check_login_agreement_visible", LoginChecks, "check_login_agreement_visible")