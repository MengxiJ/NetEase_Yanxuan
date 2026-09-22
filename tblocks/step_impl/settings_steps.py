"""
设置模块步骤实现（step 逻辑从 pages 迁出）
"""
from base import logger
from base.page_base import step_result
from tblocks.registry import step
from pages.page_settings import SettingsPage


class SettingsSteps(SettingsPage):
    """设置模块 Step 实现（复用 SettingsPage 元素定位与 PageBase 底层操作）"""

    def step_go_settings(self):
        """进入设置页（子步骤失败即时中断，不再吞错）"""
        logger.info("[Step] 进入设置页")
        mine_res = self.base_click(self._mine_tab)
        if not mine_res["status"]:
            return step_result("step_go_settings", False, f"点击个人中心失败: {mine_res['message']}")
        if self.is_element_exist(self._overlay_cancel, timeout=2):
            self.base_click(self._overlay_cancel)
        setting_res = self.base_click(self._setting_entry)
        if not setting_res["status"]:
            return step_result("step_go_settings", False, f"点击设置入口失败: {setting_res['message']}")
        return step_result("step_go_settings", True, "已进入设置页")

    def click_logout(self):
        """点击退出登录"""
        logger.info("[Step] 点击退出登录")
        self.base_swipe(720, 1900, 720, 700)
        return self.base_click(self._logout_btn)

    def click_logout_confirm(self):
        """确认退出登录"""
        logger.info("[Step] 确认退出登录")
        return self.base_click(self._logout_confirm)


step("step_go_settings", SettingsSteps, "step_go_settings")
step("click_logout", SettingsSteps, "click_logout")
step("click_logout_confirm", SettingsSteps, "click_logout_confirm")