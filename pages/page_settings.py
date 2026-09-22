from appium.webdriver.common.appiumby import By

from base.page_base import PageBase


class SettingsPage(PageBase):
    """设置页面：仅承载元素定位，Step/Check 实现见 tblocks/step_impl 与 tblocks/check_impl"""

    # ===== 元素定位（基于真实 UI dump） =====
    _mine_tab = (By.XPATH, '//android.widget.TextView[@text="个人"]')
    _overlay_cancel = (By.ID, 'com.netease.yanxuan:id/trans_cancel')
    _setting_entry = (By.ID, 'com.netease.yanxuan:id/ivSetting')
    _address_manage = (By.ID, 'com.netease.yanxuan:id/address_manager')
    _account_manager = (By.ID, 'com.netease.yanxuan:id/account_manager')
    _clear_cache = (By.ID, 'com.netease.yanxuan:id/clear_cache')
    _logout_btn = (By.ID, 'com.netease.yanxuan:id/item_logout')
    _logout_confirm = (By.ID, 'com.netease.yanxuan:id/btn_alert_positive')
    _login_view = (By.ID, 'com.netease.yanxuan:id/fl_loginview')