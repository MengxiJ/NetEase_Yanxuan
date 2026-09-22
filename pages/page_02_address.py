from appium.webdriver.common.appiumby import By

from base.page_base import PageBase


class AddressPage(PageBase):
    """地址管理页面：仅承载元素定位，Step/Check 实现见 tblocks/step_impl 与 tblocks/check_impl"""

    # ===== 元素定位 =====
    _mine = (By.XPATH, '//android.widget.TextView[@text="个人"]')
    _setting = (By.ID, 'com.netease.yanxuan:id/ivSetting')
    _address = (By.XPATH, '//android.widget.TextView[@text="我的地址"]')
    _add_address = (By.XPATH, '//android.widget.TextView[@text="新建地址"]')
    _province = (By.XPATH, '//android.widget.TextView[@text="北京市"]')
    _city = (By.XPATH, '//android.widget.TextView[@text="顺义区"]')
    _county = (By.XPATH, '//android.widget.TextView[@text="马坡地区"]')
    _confirm = (By.ID, 'com.netease.yanxuan:id/btn_confirm_address_manage')
    _detail_address = (By.ID, 'com.netease.yanxuan:id/address_detial_edit')
    _name = (By.ID, 'com.netease.yanxuan:id/address_name_edit')
    _phone = (By.ID, 'com.netease.yanxuan:id/address_phonenumber_edit')
    _save = (By.ID, 'com.netease.yanxuan:id/nav_right_text')
    _success_text = (By.XPATH, '//android.widget.TextView[@text="张三"]')
