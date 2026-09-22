from appium.webdriver.common.appiumby import By

from base.page_base import PageBase


class LoginPage(PageBase):
    """登录页面：仅承载元素定位，Step/Check 实现见 tblocks/step_impl 与 tblocks/check_impl"""

    # ===== 元素定位 =====
    _agree = (By.XPATH, '//*[@text="同意"]')
    _mine = (By.XPATH, '//android.widget.TextView[@text="个人"]')
    _change_mode = (By.ID, 'com.netease.yanxuan:id/btn_change_mode')   # "使用密码登录"
    _agree_checkbox = (By.XPATH, '//android.widget.CheckBox[@resource-id="com.netease.yanxuan:id/check_box"]')
    _username = (By.ID, 'com.netease.yanxuan:id/account_edit')
    _password = (By.ID, 'com.netease.yanxuan:id/password_edit')
    _login_btn = (By.ID, 'com.netease.yanxuan:id/btn_login_content')
    _nickname = (By.ID, 'com.netease.yanxuan:id/user_name')
    _fail_text = (By.XPATH, '//android.widget.Toast')