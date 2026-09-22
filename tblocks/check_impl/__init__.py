"""
检查节点注册入口（导入即注册）
参照 AutoTestRes 的 tblocks/check_impl/ 按业务域分组组织
"""
from tblocks.check_impl import (
    login_checks,
    search_checks,
    cart_checks,
    order_checks,
    home_checks,
    goods_checks,
    address_checks,
    category_checks,
    mine_checks,
    settings_checks,
)