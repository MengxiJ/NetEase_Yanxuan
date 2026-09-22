"""
首页模块检查实现（check 逻辑从 pages 迁出）
"""
from base.page_base import check_result
from tblocks.registry import check
from pages.page_home import HomePage


class HomeChecks(HomePage):
    """首页模块 Check 实现（复用 HomePage 元素定位与 PageBase 底层能力）"""

    def check_home_loaded(self):
        """首页加载判定"""
        return self.check_page_loaded(self._search_box)

    def check_search_box_visible(self):
        """搜索框可见判定"""
        return self.check_element_visible(self._search_box)

    def check_search_btn_visible(self):
        """搜索按钮可见判定"""
        return self.check_element_visible(self._search_btn)

    def check_message_entrance_visible(self):
        """消息入口可见判定"""
        return self.check_element_visible(self._message_entrance)

    def check_banner_visible(self):
        """轮播图可见判定"""
        return self.check_element_visible(self._banner)

    def check_kingkong_visible(self):
        """金刚区（分类入口）可见判定"""
        return self.check_element_visible(self._kingkong)

    def check_recommend_list_visible(self):
        """推荐商品列表可见判定"""
        return self.check_element_visible(self._recommend_list)

    def check_bottom_tabs_visible(self):
        """底部导航可见判定"""
        return self.check_element_visible(self._tab_titles)

    def check_category_entry_exists(self):
        """分类入口存在判定"""
        return self.check_element_visible(self._kingkong)

    def check_all_core_elements(self):
        """首页核心元素汇总判定"""
        locators = [
            self._search_box,
            self._banner,
            self._kingkong,
            self._recommend_list,
            self._tab_titles,
        ]
        all_visible = all(self.is_element_exist(loc, timeout=5) for loc in locators)
        return check_result(
            "check_all_core_elements",
            all_visible,
            f"首页核心元素检查{'通过' if all_visible else '失败'}",
            expected="全部核心元素可见",
            actual="全部可见" if all_visible else "存在不可见元素",
        )


check("check_home_loaded", HomeChecks, "check_home_loaded")
check("check_search_box_visible", HomeChecks, "check_search_box_visible")
check("check_search_btn_visible", HomeChecks, "check_search_btn_visible")
check("check_message_entrance_visible", HomeChecks, "check_message_entrance_visible")
check("check_banner_visible", HomeChecks, "check_banner_visible")
check("check_kingkong_visible", HomeChecks, "check_kingkong_visible")
check("check_recommend_list_visible", HomeChecks, "check_recommend_list_visible")
check("check_bottom_tabs_visible", HomeChecks, "check_bottom_tabs_visible")
check("check_category_entry_exists", HomeChecks, "check_category_entry_exists")
check("check_all_core_elements", HomeChecks, "check_all_core_elements")