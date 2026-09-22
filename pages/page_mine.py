from appium.webdriver.common.appiumby import By

from base.page_base import PageBase


class MinePage(PageBase):
    """个人中心页面：仅承载元素定位，Check 实现见 tblocks/check_impl"""

    # ===== 元素定位（基于截图 + text 定位） =====
    # 用户信息
    _user_nickname = (By.ID, 'com.netease.yanxuan:id/user_name')
    # 资产入口
    _balance = (By.XPATH, '//*[@text="余额"]')
    _coupon = (By.XPATH, '//*[@text="优惠券"]')
    _red_packet = (By.XPATH, '//*[@text="红包"]')
    _points = (By.XPATH, '//*[@text="积分"]')
    _gift_card = (By.XPATH, '//*[@text="礼品卡"]')
    # 订单入口
    _all_orders = (By.XPATH, '//*[@text="全部订单"]')
    _wait_pay = (By.XPATH, '//*[@text="待付款"]')
    _wait_comment = (By.XPATH, '//*[@text="待评价"]')
    # 我的服务
    _favorite = (By.XPATH, '//*[@text="收藏"]')
    _footprint = (By.XPATH, '//*[@text="足迹"]')
    _refund = (By.XPATH, '//*[@text="退换/售后"]')
    _customer_service = (By.XPATH, '//*[@text="客服服务"]')
    # 设置
    _setting = (By.ID, 'com.netease.yanxuan:id/ivSetting')
