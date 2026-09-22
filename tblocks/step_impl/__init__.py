"""
步骤节点注册入口（导入即注册）
参照 AutoTestRes 的 tblocks/step_impl/ 按业务域分组组织
"""
from tblocks.step_impl import (
    login_steps,
    search_steps,
    cart_steps,
    order_steps,
    home_steps,
    goods_steps,
    address_steps,
    settings_steps,
    nav_steps,
)