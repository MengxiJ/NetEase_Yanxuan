"""
地址管理模块检查实现（check 逻辑从 pages 迁出）
"""
from base import logger
from base.page_base import check_result
from tblocks.registry import check
from pages.page_02_address import AddressPage


class AddressChecks(AddressPage):
    """地址管理 Check 实现（复用 AddressPage 元素定位与 PageBase 底层能力）"""

    def get_success_text(self):
        """获取地址列表新增收货人文本"""
        return self.base_get_text(self._success_text)

    def check_add_address_success(self, expected_name=None):
        """地址添加成功判定：列表展示新增收货人姓名"""
        logger.info("[Check] 验证地址添加成功")
        actual = self.get_success_text()
        result = expected_name in actual if expected_name else bool(actual)
        return check_result(
            "check_add_address_success",
            result,
            f"地址添加检查{'通过' if result else '失败'}",
            expected=expected_name,
            actual=actual,
        )


check("check_add_address_success", AddressChecks, "check_add_address_success")