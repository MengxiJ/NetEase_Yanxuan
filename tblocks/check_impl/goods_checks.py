"""
商品详情模块检查实现（check 逻辑从 pages 迁出）
"""
from base import logger
from base.page_base import check_result
from tblocks.registry import check
from pages.page_goods_detail import GoodsDetailPage


class GoodsChecks(GoodsDetailPage):
    """商品详情模块 Check 实现（复用 GoodsDetailPage 元素定位与 PageBase 底层能力）"""

    def check_goods_detail_loaded(self):
        """详情页加载判定：以底部栏购物车图标为特征元素"""
        return self.check_page_loaded(self._cart_icon)

    def check_goods_name_visible(self):
        """商品名可见判定"""
        return self.check_element_visible(self._goods_name)

    def check_goods_image_visible(self):
        """商品主图可见判定"""
        return self.check_element_visible(self._goods_image)

    def check_add_cart_btn_visible(self):
        """加入购物车按钮可见判定"""
        return self.check_element_visible(self._add_cart_btn)

    def check_buy_now_btn_visible(self):
        """立即购买按钮可见判定"""
        return self.check_element_visible(self._buy_now_btn)

    def check_goods_sku_entry_visible(self):
        """规格选择入口（"选择"）可见判定"""
        return self.check_element_visible(self._sku_selector)

    def get_goods_name(self):
        """获取商品名文本"""
        return self.base_get_text(self._goods_name)

    def check_goods_name_not_empty(self):
        """商品名非空判定"""
        logger.info("[Check] 验证商品名非空")
        name = self.get_goods_name()
        result = bool(name and name.strip())
        return check_result(
            "check_goods_name_not_empty",
            result,
            f"商品名非空检查{'通过' if result else '失败'}",
            expected="商品名非空",
            actual=name,
        )


check("check_goods_detail_loaded", GoodsChecks, "check_goods_detail_loaded")
check("check_goods_name_visible", GoodsChecks, "check_goods_name_visible")
check("check_goods_image_visible", GoodsChecks, "check_goods_image_visible")
check("check_add_cart_btn_visible", GoodsChecks, "check_add_cart_btn_visible")
check("check_buy_now_btn_visible", GoodsChecks, "check_buy_now_btn_visible")
check("check_goods_sku_entry_visible", GoodsChecks, "check_goods_sku_entry_visible")
check("check_goods_name_not_empty", GoodsChecks, "check_goods_name_not_empty")