"""
首页模块步骤实现（step 逻辑从 pages 迁出）
"""
import time

from appium.webdriver.common.appiumby import By

from base import logger
from base.page_base import step_result
from config import APP_CONFIG
from tblocks.registry import step
from pages.page_home import HomePage


class HomeSteps(HomePage):
    """首页模块 Step 实现（复用 HomePage 元素定位与 PageBase 底层操作）"""

    def close_popup(self):
        """
        关闭启动弹窗并确保回到首页（基于真实 UI dump）
        策略：
        1. 已在首页（搜索框可见）则直接返回
        2. 开屏广告页：点击 trans_cancel 跳过
        3. 强行终止并重启 App，回到主 Activity（首页），解决落地页延续问题
        4. 重启后轮询等待首页加载，期间持续处理开屏广告
        5. 兜底点击底部首页 tab 归位
        """
        logger.info("[Step] 尝试关闭启动弹窗并回到首页")
        # 1. 已在首页则无需处理
        if self.is_element_exist(self._search_box, timeout=3):
            logger.info("[Step] 已在首页，无需关闭弹窗")
            return step_result("close_popup", True, "已在首页")
        # 2. 开屏广告：点击跳过按钮
        if self.is_element_exist(self._splash_cancel, timeout=3):
            try:
                self.driver.find_element(*self._splash_cancel).click()
                time.sleep(2)
                logger.info("[Step] 已跳过开屏广告")
            except Exception:
                pass
        # 3. 强行终止并重启 App，回到主 Activity（首页）
        try:
            self.driver.terminate_app(APP_CONFIG["appPackage"])
            time.sleep(1)
            self.driver.activate_app(APP_CONFIG["appPackage"])
            logger.info("[Step] 已重启 App，等待首页加载")
        except Exception as e:
            logger.warning(f"[Step] 重启 App 失败: {e}")
        # 4. 轮询等待首页加载（冷启动可能较慢），期间持续处理开屏广告
        for _ in range(8):
            if self.is_element_exist(self._search_box, timeout=2):
                logger.info("[Step] 已回到首页")
                return step_result("close_popup", True, "已回到首页")
            if self.is_element_exist(self._splash_cancel, timeout=2):
                try:
                    self.driver.find_element(*self._splash_cancel).click()
                    time.sleep(2)
                except Exception:
                    pass
            time.sleep(2)
        # 5. 兜底点击首页 tab 归位
        try:
            self.driver.find_element(*self._tab_home).click()
            time.sleep(1)
        except Exception:
            pass
        return step_result("close_popup", True, "弹窗关闭与归位操作已执行")

    def _dismiss_overlay(self):
        """关闭可能遮挡底部 tab 的开屏广告/登录引导浮层（同为 trans_cancel）"""
        if self.is_element_exist(self._splash_cancel, timeout=1):
            try:
                self.driver.find_element(*self._splash_cancel).click()
                time.sleep(1)
                logger.info("[Step] 已关闭遮挡浮层")
            except Exception:
                pass

    def click_tab(self, tab_name):
        """点击底部导航：文本定位优先；角标计数（如购物车显示数量）时回退 tab 图标索引"""
        logger.info(f"[Step] 点击底部导航: {tab_name}")
        self._dismiss_overlay()
        text_loc = (By.XPATH, f'//android.widget.TextView[@text="{tab_name}"]')
        if self.is_element_exist(text_loc, timeout=3):
            return self.base_click(text_loc)
        # 5 tab 结构：首页[1] 分类[2] 视频[3] 购物车[4] 个人[5]
        icon_index = {"首页": 1, "分类": 2, "视频": 3, "购物车": 4, "个人": 5}.get(tab_name)
        if icon_index:
            icon_loc = (By.XPATH,
                        f'(//android.widget.ImageView[@resource-id="com.netease.yanxuan:id/img_mainpage_tab_icon"])[{icon_index}]')
            if self.is_element_exist(icon_loc, timeout=3):
                return self.base_click(icon_loc)
        return self.base_click(text_loc)

    def step_go_category(self):
        """进入分类页"""
        return self.click_tab("分类")

    def step_go_cart(self):
        """进入购物车页：加购后常停留在详情页（无底部 tab），先回首页再点购物车"""
        from appium.webdriver.common.appiumby import By
        home_mark = (By.ID, f"{APP_CONFIG['appPackage']}:id/tv_home_search")
        if not self.is_element_exist(home_mark, timeout=2):
            self.close_popup()  # 非首页时重启 App 归位首页
        return self.click_tab("购物车")

    def step_go_mine(self):
        """进入个人中心页"""
        return self.click_tab("个人")

    def step_go_home(self):
        """回到首页"""
        return self.click_tab("首页")


step("close_popup", HomeSteps, "close_popup")
step("step_go_category", HomeSteps, "step_go_category")
step("step_go_cart", HomeSteps, "step_go_cart")
step("step_go_mine", HomeSteps, "step_go_mine")
step("step_go_home", HomeSteps, "step_go_home")