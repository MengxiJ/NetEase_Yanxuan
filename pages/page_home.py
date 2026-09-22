from appium.webdriver.common.appiumby import By

from base.page_base import PageBase


class HomePage(PageBase):
    """网易严选首页：仅承载元素定位，Step/Check 实现见 tblocks/step_impl 与 tblocks/check_impl"""

    # ===== 元素定位（基于真实 UI dump） =====
    # 搜索栏
    _search_box = (By.ID, 'com.netease.yanxuan:id/tv_home_search')
    _search_btn = (By.ID, 'com.netease.yanxuan:id/iv_home_search_button')
    # 消息入口
    _message_entrance = (By.ID, 'com.netease.yanxuan:id/rl_message_center_entrance')
    # 金刚区（分类入口）
    _kingkong = (By.ID, 'com.netease.yanxuan:id/compose_kingkong')
    # 轮播图
    _banner = (By.ID, 'com.netease.yanxuan:id/sdv_banner')
    # 推荐商品列表
    _recommend_list = (By.ID, 'com.netease.yanxuan:id/rv_recommend')
    # 底部导航
    _tab_titles = (By.ID, 'com.netease.yanxuan:id/txt_mainpage_tab_title')

    # 底部导航文本
    _tab_home = (By.XPATH, '//android.widget.TextView[@text="首页"]')
    # 开屏广告跳过按钮（冷启动出现，不点击不会自动消失）
    _splash_cancel = (By.ID, 'com.netease.yanxuan:id/trans_cancel')