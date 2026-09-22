"""
搜索模块检查实现（check 逻辑从 pages 迁出）
"""
from base import logger
from base.page_base import check_result
from tblocks.registry import check
from pages.page_03_search import SearchPage


class SearchChecks(SearchPage):
    """搜索模块 Check 实现（复用 SearchPage 元素定位与 PageBase 底层能力）"""

    def get_search_res(self):
        """获取搜索结果文本"""
        try:
            elements = self.fd_elements(self._search_res, timeout=8)
            return " ".join([e.text for e in elements if e.text])
        except Exception:
            return ""

    def check_search_result(self, expected_text=None):
        """搜索结果判定：结果列表文本包含关键词"""
        logger.info("[Check] 验证搜索结果")
        actual = self.get_search_res()
        result = expected_text in actual if expected_text else bool(actual)
        return check_result(
            "check_search_result",
            result,
            f"搜索结果检查{'通过' if result else '失败'}",
            expected=expected_text,
            actual=actual,
        )

    def check_search_page_loaded(self):
        """搜索页加载判定"""
        return self.check_page_loaded(self._search_input)

    def check_search_btn_visible(self):
        """搜索按钮可见判定"""
        return self.check_element_visible(self._search_btn)

    def check_hot_keywords_visible(self):
        """热门关键词区可见判定"""
        return self.check_element_visible(self._hot_keywords)

    def check_search_no_result(self, expected_text=None):
        """无结果提示判定"""
        logger.info("[Check] 验证无结果提示")
        exists = self.is_element_exist(self._empty_result, timeout=5)
        actual = self.base_get_text(self._empty_result) if exists else ""
        result = (expected_text in actual) if expected_text else exists
        return check_result(
            "check_search_no_result",
            result,
            f"无结果提示检查{'通过' if result else '失败'}",
            expected=expected_text,
            actual=actual,
        )


check("check_search_result", SearchChecks, "check_search_result")
check("check_search_page_loaded", SearchChecks, "check_search_page_loaded")
check("check_search_page_btn_visible", SearchChecks, "check_search_btn_visible")
check("check_hot_keywords_visible", SearchChecks, "check_hot_keywords_visible")
check("check_search_no_result", SearchChecks, "check_search_no_result")