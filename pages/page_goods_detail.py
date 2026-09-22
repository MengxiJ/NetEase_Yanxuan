from appium.webdriver.common.appiumby import By

from base.page_base import PageBase


class GoodsDetailPage(PageBase):
    """商品详情页面：仅承载元素定位，Step/Check 实现见 tblocks/step_impl 与 tblocks/check_impl"""

    # ===== 元素定位 =====
    # 商品信息（详情页标题真实 ID 为 tv_commodity_name，搜索结果页才是 tv_goods_name）
    _goods_name = (By.ID, 'com.netease.yanxuan:id/tv_commodity_name')
    # 商品主图（真实 dump：详情页无 img_goods——那是列表卡片图；主图为 sdv_img）
    _goods_image = (By.ID, 'com.netease.yanxuan:id/sdv_img')
    # 底部操作按钮（注意：网易严选 ID 命名与按钮文本相反）
    # btn_buy_commodity_now 实际显示"加入购物车"，btn_add_commodity_to_cart 实际显示"立即购买"
    _add_cart_btn = (By.ID, 'com.netease.yanxuan:id/btn_buy_commodity_now')
    _buy_now_btn = (By.ID, 'com.netease.yanxuan:id/btn_add_commodity_to_cart')
    # 底部栏购物车图标（详情页特征元素，用于判断是否已进入详情页）
    _cart_icon = (By.ID, 'com.netease.yanxuan:id/ib_shopping_cart')
    # 规格选择入口（v3 dump 证实不同商品详情页结构有差异：多规格商品有
    # tv_commodity_amount 数量角标，单规格商品可能无；底部操作栏容器
    # view_goods_detail_cart 为所有详情页共有，包含规格/数量/加购/购买）
    _sku_selector = (By.ID, 'com.netease.yanxuan:id/view_goods_detail_cart')