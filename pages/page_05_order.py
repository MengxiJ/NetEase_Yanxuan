from appium.webdriver.common.appiumby import By

from base.page_base import PageBase


class OrderPage(PageBase):
    """订单页面：仅承载元素定位，Step/Check 实现见 tblocks/step_impl 与 tblocks/check_impl"""

    # ===== 元素定位 =====
    # 底部导航已是 5 tab（首页/分类/视频/购物车/个人），购物车为第 4 个图标；
    # 有角标时 tab 文本显示为数量而非"购物车"，因此图标索引与文本双定位
    _cart_loc = (By.XPATH, '(//android.widget.ImageView[@resource-id="com.netease.yanxuan:id/img_mainpage_tab_icon"])[4]')
    _cart_tab_text = (By.XPATH, '//android.widget.TextView[@text="购物车"]')
    # 结算按钮：购物车底部为"结算(N)"（真实 dump 文本），文本定位优先；compose 结构定位兜底
    _settlement_text_loc = (By.XPATH, '//*[contains(@text,"结算") and contains(@text,"(")]')
    _settlement_loc = (By.XPATH, '//androidx.compose.ui.platform.ComposeView/android.view.View/android.view.View/android.view.View[5]')
    _submit_order_loc = (By.ID, 'com.netease.yanxuan:id/order_btn')


class GetOrderPage(PageBase):
    """获取订单页面：仅承载元素定位，Check 实现见 tblocks/check_impl"""

    # ===== 元素定位 =====
    _mine_loc = (By.XPATH, '//android.widget.TextView[@text="个人"]')
    _wait_pay_loc = (By.XPATH, '//android.widget.TextView[@text="待付款"]')
    _order_num_loc = (By.ID, 'com.netease.yanxuan:id/tv_order_form_number')
    # 空订单提示（真实 dump："还没有相关的订单呢"）
    _order_empty_loc = (By.ID, 'com.netease.yanxuan:id/tv_order_empty')
