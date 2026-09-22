"""
商品详情模块步骤实现（step 逻辑从 pages 迁出）
"""
import time

from appium.webdriver.common.appiumby import By

from base import logger
from base.page_base import step_result
from tblocks.registry import step
from pages.page_goods_detail import GoodsDetailPage
from pages.page_category import CategoryPage


class CategorySteps(CategoryPage):
    """分类页 Step 实现（内置第一个商品点击进入详情页）"""

    def click_first_goods(self):
        """
        点击第一个商品（基于真实dump优化）
        搜索结果页商品元素因限时购倒计时频繁重绘，element.click() 点击瞬间
        易抛 NoSuchElementError，改为获取元素中心坐标后 tap 坐标点击；
        点击后自动处理系统权限弹窗，并探测详情页特征元素验证是否进入，
        未进入则重新获取坐标再 tap（最多 5 次）。
        商品名 tv_goods_name 重绘时回退用商品图片 img_goods 定位。
        """
        logger.info("[Step] 点击第一个商品")
        detail_mark = (By.ID, 'com.netease.yanxuan:id/ib_shopping_cart')
        fallback_locs = [
            self._goods_name,
            (By.ID, 'com.netease.yanxuan:id/img_goods'),
        ]
        for attempt in range(1, 6):
            el = None
            for loc in fallback_locs:
                try:
                    if self.is_element_exist(loc, timeout=3):
                        el = self.fd_element(loc, timeout=5)
                        break
                except Exception:
                    continue
            if el is None:
                logger.warning(f"[Step] 第{attempt}次未找到商品元素，刷新重试")
                self.base_swipe(500, 1200, 500, 1400)  # 轻微下拉刷新
                time.sleep(2)
                continue
            try:
                rect = el.rect
                cx = rect["x"] + rect["width"] // 2
                cy = rect["y"] + rect["height"] // 2
                self.driver.tap([(cx, cy)], 50)
                time.sleep(3)
                logger.info(f"[Step] 第{attempt}次已点击商品坐标: ({cx}, {cy})")
            except Exception as e:
                logger.error(f"[Step] 点击第一个商品失败(第{attempt}次): {e}")
                continue
            if self.is_element_exist(self._alert_allow, timeout=2):
                try:
                    self.driver.find_element(*self._alert_allow).click()
                    time.sleep(1)
                    logger.info("[Step] 已处理系统权限弹窗（允许）")
                except Exception:
                    pass
            if self.is_element_exist(detail_mark, timeout=5):
                logger.info(f"[Step] 已进入商品详情页(第{attempt}次点击)")
                return step_result("click_first_goods", True, "已点击第一个商品并进入详情页")
        return step_result("click_first_goods", False, "多次点击仍未进入详情页")


class GoodsSteps(GoodsDetailPage):
    """商品详情 Step 实现（复用 GoodsDetailPage 元素定位与 PageBase 底层操作）"""

    def click_add_cart(self):
        """点击加入购物车"""
        logger.info("[Step] 点击加入购物车")
        return self.base_click(self._add_cart_btn)

    def click_buy_now(self):
        """点击立即购买"""
        logger.info("[Step] 点击立即购买")
        return self.base_click(self._buy_now_btn)

    def step_select_sku(self):
        """选择商品规格"""
        logger.info("[Step] 选择商品规格")
        if self.is_element_exist(self._sku_selector, timeout=3):
            self.base_click(self._sku_selector)
        return step_result("step_select_sku", True, "规格选择完成")

    def step_add_to_cart(self):
        """加入购物车业务步骤（多规格商品需两段点击，点击失败即时中断）
        v3 dump 证实：点详情页「加入购物车」(btn_buy_commodity_now)后弹出
        SKU 规格弹窗（默认已选中规格），须再点弹窗内「加入购物车」确认——
        弹窗确认按钮与详情页按钮复用同一 resource-id。"""
        logger.info("[Step] 执行加入购物车")
        click_res = self.click_add_cart()
        if not click_res["status"]:
            return step_result("step_add_to_cart", False, f"点击加入购物车失败: {click_res['message']}")
        time.sleep(2)
        confirm_res = self.base_click(self._add_cart_btn)
        if not confirm_res["status"]:
            return step_result("step_add_to_cart", False, f"弹窗确认加入购物车失败: {confirm_res['message']}")
        return step_result("step_add_to_cart", True, "加入购物车操作完成")

    def step_buy_now(self):
        """
        立即购买业务步骤

        多规格商品点击"立即购买"后会先弹出 SKU 选择弹窗（默认已选中规格），
        需再次点击弹窗内的"立即购买"（复用同一 btn_buy_commodity_now ID）确认后才进入订单页。
        """
        logger.info("[Step] 执行立即购买")
        self.click_buy_now()          # 第1次：详情页点立即购买 → 弹出 SKU 弹窗
        time.sleep(2)
        self.click_buy_now()          # 第2次：弹窗内点立即购买 → 确认规格进订单页
        return step_result("step_buy_now", True, "立即购买操作完成")


step("click_first_goods", CategorySteps, "click_first_goods")
step("step_add_to_cart", GoodsSteps, "step_add_to_cart")
step("step_buy_now", GoodsSteps, "step_buy_now")