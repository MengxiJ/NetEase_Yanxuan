from appium.webdriver.common.appiumby import By

from base.page_base import PageBase


class SearchPage(PageBase):
    """搜索页面：仅承载元素定位，Step/Check 实现见 tblocks/step_impl 与 tblocks/check_impl"""

    # ===== 元素定位 =====
    _search_box = (By.ID, 'com.netease.yanxuan:id/tv_home_search')
    _search_input = (By.ID, 'com.netease.yanxuan:id/search_input')
    _search_btn = (By.ID, 'com.netease.yanxuan:id/tv_search_button')
    _search_res = (By.ID, 'com.netease.yanxuan:id/tv_goods_name')
    # ===== 搜索页元素（基于真实 UI dump） =====
    _hot_keywords = (By.ID, 'com.netease.yanxuan:id/hot_keyword_flow')
    _history_head = (By.ID, 'com.netease.yanxuan:id/history_record_head')
    _empty_result = (By.ID, 'com.netease.yanxuan:id/tv_empty_search_result')