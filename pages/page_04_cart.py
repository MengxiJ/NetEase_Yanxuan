from appium.webdriver.common.appiumby import By

from base.page_base import PageBase


class CartPage(PageBase):
    """购物车页面：仅承载元素定位，Step/Check 实现见 tblocks/step_impl 与 tblocks/check_impl"""

    # ===== 元素定位 =====
    _goods_name = (By.ID, 'com.netease.yanxuan:id/tv_goods_name')
    _add = (By.XPATH, '//android.widget.TextView[@text="加入购物车"]')
    _success_res = (By.XPATH, '//android.widget.Toast')
    # ===== 购物车页元素（基于真实 UI dump） =====
    _cart_title = (By.XPATH, '//android.widget.TextView[@text="购物车"]')
    _coupon_entry = (By.ID, 'com.netease.yanxuan:id/tv_get_coupon_highlight')
    # 空态提示：多版本文案兜底
    _empty_hint = (By.XPATH, '//*[contains(@text,"去添加点什么吧") or contains(@text,"购物车还是空的") or contains(@text,"购物车空空如也")]')
    # 有商品判定：商品项容器 / 商品名 / 商品价 / 结算按钮带数量 四者任一即可
    _goods_item = (By.ID, 'com.netease.yanxuan:id/rl_goods')
    _goods_price = (By.ID, 'com.netease.yanxuan:id/tv_price')
    _settle_btn = (By.XPATH, '//android.widget.TextView[contains(@text,"结算")]')
    # 加购成功后详情页底部栏购物车图标角标数量（v3_05 dump：text='1'）
    _cart_badge = (By.ID, 'com.netease.yanxuan:id/tv_commodity_amount')
    # 空态购物车没有"猜你喜欢"推荐流，推荐/促销元素实际为 Pro 会员横幅
    _recommend = (By.ID, 'com.netease.yanxuan:id/shopping_banner_desc')