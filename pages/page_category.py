from appium.webdriver.common.appiumby import By

from base.page_base import PageBase


class CategoryPage(PageBase):
    """分类页面：仅承载元素定位，Step/Check 实现见 tblocks/step_impl 与 tblocks/check_impl"""

    # ===== 元素定位 =====
    # 搜索框（分类页顶部）
    _search_box = (By.ID, 'com.netease.yanxuan:id/tv_home_search')
    # 商品列表（真实 dump：分类页商品瀑布流容器，rv_recommend 是首页推荐流、分类页不存在）
    _goods_list = (By.ID, 'com.netease.yanxuan:id/srv_category_detail')
    _goods_name = (By.ID, 'com.netease.yanxuan:id/tv_goods_name')
    _goods_price = (By.ID, 'com.netease.yanxuan:id/final_price')
    # 底部导航
    _tab_home = (By.XPATH, '//*[@text="首页"]')
    # 系统权限弹窗"允许"按钮（进详情页时可能触发）
    _alert_allow = (By.ID, 'com.netease.yanxuan:id/btn_alert_positive')