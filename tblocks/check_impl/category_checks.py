"""
分类模块检查实现（check 逻辑从 pages 迁出）
"""
from tblocks.registry import check
from pages.page_category import CategoryPage


class CategoryChecks(CategoryPage):
    """分类模块 Check 实现（复用 CategoryPage 元素定位与 PageBase 底层能力）"""

    def check_category_loaded(self):
        """分类页加载判定"""
        return self.check_page_loaded(self._goods_list)

    def check_goods_list_visible(self):
        """商品列表可见判定"""
        return self.check_element_visible(self._goods_list)

    def check_goods_items_displayed(self):
        """商品条目展示判定"""
        return self.check_element_visible(self._goods_name)

    def check_goods_price_displayed(self):
        """价格展示判定"""
        return self.check_element_visible(self._goods_price)


check("check_category_loaded", CategoryChecks, "check_category_loaded")
check("check_goods_list_visible", CategoryChecks, "check_goods_list_visible")
check("check_goods_items_displayed", CategoryChecks, "check_goods_items_displayed")
check("check_goods_price_displayed", CategoryChecks, "check_goods_price_displayed")