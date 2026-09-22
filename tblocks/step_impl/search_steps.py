"""
搜索模块步骤实现（step 逻辑从 pages 迁出）
"""
import time

from base import logger
from base.page_base import step_result
from tblocks.registry import step
from pages.page_03_search import SearchPage


class SearchSteps(SearchPage):
    """搜索模块 Step 实现（复用 SearchPage 元素定位与 PageBase 底层操作）"""

    def click_search_box(self):
        """点击搜索框"""
        logger.info("[Step] 点击搜索框")
        return self.base_click(self._search_box)

    def input_search_text(self, text):
        """输入搜索内容并搜索（输入/点击失败即时返回，不再吞错）"""
        logger.info(f"[Step] 输入搜索内容: {text}")
        input_res = self.base_input_text(self._search_input, text)
        if not input_res["status"]:
            return step_result("input_search_text", False, f"输入搜索内容失败: {input_res['message']}")
        # 先收起 IME 键盘，避免键盘遮挡导致搜索按钮点击被吞
        try:
            self.driver.hide_keyboard()
        except Exception:
            pass
        click_res = self.base_click(self._search_btn)
        if not click_res["status"]:
            return step_result("input_search_text", False, f"点击搜索按钮失败: {click_res['message']}")
        # 验证搜索是否生效：成功搜索后 tv_search_button 会消失
        time.sleep(2)
        if self.is_element_exist(self._search_btn, timeout=3):
            logger.info("[Step] 搜索按钮仍存在，重试点击")
            retry_res = self.base_click(self._search_btn)
            if not retry_res["status"]:
                return step_result("input_search_text", False, f"重试点击搜索按钮失败: {retry_res['message']}")
        if self.is_element_exist(self._search_btn, timeout=2):
            return step_result("input_search_text", False, "搜索按钮未消失，搜索未提交")
        return step_result("input_search_text", True, f"搜索: {text}")

    def step_search(self, text):
        """搜索业务步骤（子步骤失败即时中断，不再吞错）"""
        logger.info(f"[Step] 执行搜索: {text}")
        click_res = self.click_search_box()
        if not click_res["status"]:
            return step_result("step_search", False, f"点击搜索框失败: {click_res['message']}")
        input_res = self.input_search_text(text)
        if not input_res["status"]:
            return step_result("step_search", False, f"搜索输入失败: {input_res['message']}")
        return step_result("step_search", True, f"搜索操作完成: {text}")


step("click_search_box", SearchSteps, "click_search_box")
step("input_search_text", SearchSteps, "input_search_text")
step("step_search", SearchSteps, "step_search")