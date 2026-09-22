"""
订单模块步骤实现（step 逻辑从 pages 迁出）
"""
from base import logger
from base.page_base import step_result
from tblocks.registry import step
from pages.page_05_order import OrderPage


class OrderSteps(OrderPage):
    """订单模块 Step 实现（复用 OrderPage 元素定位与 PageBase 底层操作）"""

    def click_cart(self):
        """点击购物车tab：文本优先，角标计数（文本变数字）时回退第 4 个 tab 图标"""
        logger.info("[Step] 点击购物车")
        if self.is_element_exist(self._cart_tab_text, timeout=3):
            return self.base_click(self._cart_tab_text)
        return self.base_click(self._cart_loc)

    def click_settlement(self):
        """点击结算：文本"结算(N)"优先，compose 结构定位兜底"""
        logger.info("[Step] 点击结算")
        if self.is_element_exist(self._settlement_text_loc, timeout=3):
            return self.base_click(self._settlement_text_loc)
        return self.base_click(self._settlement_loc)

    def click_submit_order(self):
        """点击提交订单"""
        logger.info("[Step] 点击提交订单")
        return self.base_click(self._submit_order_loc)

    def step_order(self):
        """下单业务步骤（子步骤失败即时中断，不再吞错）"""
        logger.info("[Step] 执行下单操作")
        cart_res = self.click_cart()
        if not cart_res["status"]:
            return step_result("step_order", False, f"进入购物车失败: {cart_res['message']}")
        settle_res = self.click_settlement()
        if not settle_res["status"]:
            return step_result("step_order", False, f"点击结算失败: {settle_res['message']}")
        submit_res = self.click_submit_order()
        if not submit_res["status"]:
            return step_result("step_order", False, f"提交订单失败: {submit_res['message']}")
        return step_result("step_order", True, "下单操作完成")


step("click_cart", OrderSteps, "click_cart")
step("click_settlement", OrderSteps, "click_settlement")
step("click_submit_order", OrderSteps, "click_submit_order")
step("step_order", OrderSteps, "step_order")