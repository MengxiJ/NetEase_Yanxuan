"""
设置模块检查实现（check 逻辑从 pages 迁出）
"""
from tblocks.registry import check
from pages.page_settings import SettingsPage


class SettingsChecks(SettingsPage):
    """设置模块 Check 实现（复用 SettingsPage 元素定位与 PageBase 底层能力）"""

    def check_settings_loaded(self):
        """设置页加载判定"""
        return self.check_page_loaded(self._account_manager)

    def check_address_entry_visible(self):
        """地址管理入口可见判定"""
        return self.check_element_visible(self._address_manage)

    def check_account_entry_visible(self):
        """账号与安全入口可见判定"""
        return self.check_element_visible(self._account_manager)

    def check_clear_cache_visible(self):
        """清除缓存入口可见判定"""
        return self.check_element_visible(self._clear_cache)

    def check_logout_btn_visible(self):
        """退出登录按钮可见判定：设置页退出登录入口在底部，先上滑露出"""
        for _ in range(3):
            if self.is_element_exist(self._logout_btn, timeout=2):
                break
            self.base_swipe(720, 1900, 720, 700)
        return self.check_element_visible(self._logout_btn)

    def check_logout_success(self):
        """退出登录成功判定：回到登录页"""
        return self.check_element_visible(self._login_view)


check("check_settings_loaded", SettingsChecks, "check_settings_loaded")
check("check_address_entry_visible", SettingsChecks, "check_address_entry_visible")
check("check_account_entry_visible", SettingsChecks, "check_account_entry_visible")
check("check_clear_cache_visible", SettingsChecks, "check_clear_cache_visible")
check("check_logout_btn_visible", SettingsChecks, "check_logout_btn_visible")
check("check_logout_success", SettingsChecks, "check_logout_success")