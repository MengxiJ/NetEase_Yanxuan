"""
购物车模块检查实现（check 逻辑从 pages 迁出）
"""
import time

from base import logger
from base.page_base import check_result
from tblocks.registry import check
from pages.page_04_cart import CartPage


class CartChecks(CartPage):
    """购物车模块 Check 实现（复用 CartPage 元素定位与 PageBase 底层能力）"""

    def get_add_res(self):
        """获取加入购物车 Toast 提示"""
        return self.base_get_toast(self._success_res)

    def check_add_cart_success(self, expected_text=None):
        """加入购物车成功判定：Toast 瞬时不可靠（base_get_toast 常抓取失败），
        改用详情页底部栏购物车角标数量 > 0 判定（v3_05 dump 证实角标 ID
        为 tv_commodity_amount，加购成功后显示数字）"""
        logger.info("[Check] 验证加入购物车成功")
        badge_text = ""
        try:
            if self.is_element_exist(self._cart_badge, timeout=5):
                badge_text = self.base_get_text(self._cart_badge)
        except Exception:
            pass
        try:
            count = int(badge_text)
        except (ValueError, TypeError):
            count = 0
        result = count > 0
        actual = f"购物车角标数量={count}" if badge_text else "未检测到购物车角标"
        return check_result(
            "check_add_cart_success",
            result,
            f"加入购物车检查{'通过' if result else '失败'}",
            expected="购物车角标数量>0",
            actual=actual,
        )

    def check_cart_page_loaded(self):
        """购物车页加载判定"""
        return self.check_page_loaded(self._cart_title)

    def check_cart_coupon_entry_visible(self):
        """领券入口可见判定"""
        return self.check_element_visible(self._coupon_entry)

    def check_cart_state_valid(self):
        """购物车状态判定：存在商品 或 空态提示，二者满足其一即可"""
        time.sleep(1)  # 等待购物车页内容渲染完成
        # 有商品判定：多组兜底定位器（商品项容器 / 商品名 / 商品价 / 结算按钮）
        goods_locators = [
            self._goods_item,
            self._goods_name,
            self._goods_price,
            self._settle_btn,
        ]
        has_goods = False
        for loc in goods_locators:
            if self.is_element_exist(loc, timeout=3):
                has_goods = True
                break
        # 空态提示判定
        empty = self.is_element_exist(self._empty_hint, timeout=3)
        result = has_goods or empty
        actual = "商品" if has_goods else ("空态" if empty else "无内容")
        return check_result(
            "check_cart_state_valid",
            result,
            f"购物车状态检查{'通过' if result else '失败'}",
            expected="商品列表或空态提示",
            actual=actual,
        )

    def check_cart_recommend_visible(self):
        """推荐区（空态 Pro 会员横幅）可见判定：先上滑露出首屏下方区域"""
        self.base_swipe(720, 1900, 720, 700)
        return self.check_element_visible(self._recommend)


check("check_add_cart_success", CartChecks, "check_add_cart_success")
check("check_cart_page_loaded", CartChecks, "check_cart_page_loaded")
check("check_cart_coupon_entry_visible", CartChecks, "check_cart_coupon_entry_visible")
check("check_cart_state_valid", CartChecks, "check_cart_state_valid")
check("check_cart_recommend_visible", CartChecks, "check_cart_recommend_visible")
