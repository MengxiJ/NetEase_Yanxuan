"""
个人中心模块检查实现（check 逻辑从 pages 迁出）
"""
from base.page_base import check_result
from tblocks.registry import check
from pages.page_mine import MinePage


class MineChecks(MinePage):
    """个人中心模块 Check 实现（复用 MinePage 元素定位与 PageBase 底层能力）"""

    def check_mine_loaded(self):
        """个人中心加载判定"""
        return self.check_page_loaded(self._user_nickname)

    def check_user_nickname_visible(self):
        """用户昵称可见判定"""
        return self.check_element_visible(self._user_nickname)

    def check_asset_entries_visible(self):
        """资产入口可见判定（余额）"""
        return self.check_element_visible(self._balance)

    def check_order_entries_visible(self):
        """订单入口可见判定（全部订单）"""
        return self.check_element_visible(self._all_orders)

    def check_service_entries_visible(self):
        """服务入口可见判定（收藏）"""
        return self.check_element_visible(self._favorite)

    def check_wait_pay_entry_visible(self):
        """待付款订单入口可见判定"""
        return self.check_element_visible(self._wait_pay)

    def check_setting_visible(self):
        """设置入口可见判定"""
        return self.check_element_visible(self._setting)

    def check_full_asset_entries(self):
        """资产入口全覆盖判定：余额/优惠券/红包/积分/礼品卡"""
        locators = [self._balance, self._coupon, self._red_packet, self._points, self._gift_card]
        all_visible = all(self.is_element_exist(loc, timeout=5) for loc in locators)
        return check_result(
            "check_full_asset_entries",
            all_visible,
            f"资产入口检查{'通过' if all_visible else '失败'}",
            expected="余额/优惠券/红包/积分/礼品卡均可见",
            actual="全部可见" if all_visible else "存在不可见入口",
        )

    def check_full_order_entries(self):
        """订单入口全覆盖判定：全部订单/待付款/待评价"""
        locators = [self._all_orders, self._wait_pay, self._wait_comment]
        all_visible = all(self.is_element_exist(loc, timeout=5) for loc in locators)
        return check_result(
            "check_full_order_entries",
            all_visible,
            f"订单入口检查{'通过' if all_visible else '失败'}",
            expected="全部订单/待付款/待评价均可见",
            actual="全部可见" if all_visible else "存在不可见入口",
        )

    def check_full_service_entries(self):
        """服务入口全覆盖判定：收藏/足迹/退换售后/客服服务"""
        locators = [self._favorite, self._footprint, self._refund, self._customer_service]
        all_visible = all(self.is_element_exist(loc, timeout=5) for loc in locators)
        return check_result(
            "check_full_service_entries",
            all_visible,
            f"服务入口检查{'通过' if all_visible else '失败'}",
            expected="收藏/足迹/退换售后/客服服务均可见",
            actual="全部可见" if all_visible else "存在不可见入口",
        )


check("check_mine_loaded", MineChecks, "check_mine_loaded")
check("check_user_nickname_visible", MineChecks, "check_user_nickname_visible")
check("check_asset_entries_visible", MineChecks, "check_asset_entries_visible")
check("check_order_entries_visible", MineChecks, "check_order_entries_visible")
check("check_service_entries_visible", MineChecks, "check_service_entries_visible")
check("check_wait_pay_entry_visible", MineChecks, "check_wait_pay_entry_visible")
check("check_setting_visible", MineChecks, "check_setting_visible")
check("check_full_asset_entries", MineChecks, "check_full_asset_entries")
check("check_full_order_entries", MineChecks, "check_full_order_entries")
check("check_full_service_entries", MineChecks, "check_full_service_entries")