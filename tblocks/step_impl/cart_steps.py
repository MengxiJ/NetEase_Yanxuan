"""
购物车模块步骤实现（step 逻辑从 pages 迁出）
"""
from base import logger
from base.page_base import step_result
from tblocks.registry import step
from pages.page_04_cart import CartPage


class CartSteps(CartPage):
    """购物车模块 Step 实现（复用 CartPage 元素定位与 PageBase 底层操作）"""

    def click_goods_name(self):
        """点击商品进入详情页"""
        logger.info("[Step] 点击商品")
        return self.base_click(self._goods_name)

    def click_add_cart(self):
        """点击加入购物车"""
        logger.info("[Step] 点击加入购物车")
        return self.base_click(self._add)

    def step_add_cart(self):
        """加入购物车业务步骤（子步骤失败即时中断，不再吞错）"""
        logger.info("[Step] 执行加入购物车")
        name_res = self.click_goods_name()
        if not name_res["status"]:
            return step_result("step_add_cart", False, f"点击商品失败: {name_res['message']}")
        add_res = self.click_add_cart()
        if not add_res["status"]:
            return step_result("step_add_cart", False, f"点击加入购物车失败: {add_res['message']}")
        add_res = self.click_add_cart()
        if not add_res["status"]:
            return step_result("step_add_cart", False, f"确认加入购物车失败: {add_res['message']}")
        return step_result("step_add_cart", True, "加入购物车操作完成")


step("click_goods_name", CartSteps, "click_goods_name")
step("click_add_cart", CartSteps, "click_add_cart")
step("step_add_cart", CartSteps, "step_add_cart")