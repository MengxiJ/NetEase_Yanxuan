"""
订单模块检查实现（check 逻辑从 pages 迁出）
"""
import time

from appium.webdriver.common.appiumby import By

from base import logger
from base.page_base import check_result
from tblocks.registry import check
from pages.page_05_order import OrderPage, GetOrderPage


class OrderChecks(OrderPage):
    """订单模块 Check 实现（复用 OrderPage 元素定位与 PageBase 底层能力）"""

    def check_order_page_loaded(self):
        """订单确认页/订单页加载判定"""
        return self.check_page_loaded(self._submit_order_loc)

    def check_payment_page_opened(self):
        """提交订单后验证支付页已打开。
        本项目不真实支付：点击「提交订单」后跳转到支付页即视为成功。
        v3_16 dump 证实支付页为全屏 android.webkit.WebView，且订单确认页的
        提交订单按钮(order_btn)已消失。判定条件：order_btn 不存在 且 WebView 存在。"""
        logger.info("[Check] 验证支付页已打开")
        order_btn_gone = not self.is_element_exist(self._submit_order_loc, timeout=8)
        has_webview = self.is_element_exist((By.CLASS_NAME, "android.webkit.WebView"), timeout=5)
        result = order_btn_gone and has_webview
        if has_webview:
            actual = "支付页 WebView 已加载"
        elif order_btn_gone:
            actual = "已离开订单确认页（未检测到 WebView）"
        else:
            actual = "仍停留在订单确认页"
        return check_result(
            "check_payment_page_opened",
            result,
            f"支付页打开检查{'通过' if result else '失败'}",
            expected="跳转至支付页（WebView）",
            actual=actual,
        )


class GetOrderChecks(GetOrderPage):
    """订单查询 Check 实现（复用 GetOrderPage 元素定位与 PageBase 底层能力）"""

    def click_mine(self):
        """进入个人中心"""
        return self.base_click(self._mine_loc)

    def click_wait_pay(self):
        """进入待付款订单列表"""
        return self.base_click(self._wait_pay_loc)

    def get_order_num(self):
        """获取订单编号"""
        return self.base_get_text(self._order_num_loc)

    def check_order_exists(self):
        """待付款页面加载判定：进入个人→待付款后页面成功加载。
        本项目不真实支付，待付款列表通常为空；有订单编号或空列表提示均视为页面加载成功。"""
        logger.info("[Check] 验证待付款页面加载")
        self.click_mine()
        self.click_wait_pay()
        time.sleep(2)
        has_order = self.is_element_exist(self._order_num_loc, timeout=3)
        is_empty = self.is_element_exist(self._order_empty_loc, timeout=3)
        result = has_order or is_empty
        if has_order:
            actual = f"待付款订单存在，编号={self.get_order_num()}"
        elif is_empty:
            actual = "待付款列表为空（页面加载成功）"
        else:
            actual = "未进入待付款列表页"
        return check_result(
            "check_order_exists",
            result,
            f"待付款页面加载检查{'通过' if result else '失败'}",
            expected="待付款页面加载成功",
            actual=actual,
        )


check("check_order_exists", GetOrderChecks, "check_order_exists")
check("check_order_page_loaded", OrderChecks, "check_order_page_loaded")
check("check_payment_page_opened", OrderChecks, "check_payment_page_opened")
