"""
原子节点注册表
参照 AutoTestRes 原子化框架的 step_registry / check_registry 设计：
step_impl / check_impl 各模块在被导入时调用 step() / check() 完成注册，
工作流 JSON 中的 step_id / check_id 通过本注册表解析到页面对象方法。
"""
# ===== 注册表 =====
# key: step_id / check_id（workflow JSON 中引用），value: (页面类, 方法名)
STEP_REGISTRY = {}
CHECK_REGISTRY = {}

def step(step_id, page_cls, method_name):
    """注册步骤节点: step_id -> (页面类, 方法名)"""
    STEP_REGISTRY[step_id] = (page_cls, method_name)


def check(check_id, page_cls, method_name):
    """注册检查节点: check_id -> (页面类, 方法名)"""
    CHECK_REGISTRY[check_id] = (page_cls, method_name)


# ===== Hook 注册表（setup/teardown） =====
# driver 生命周期由 conftest fixture 管理，此处仅作声明映射
HOOK_REGISTRY = {
    "step_launch_app": "launch_app",
    "step_quit_app": "quit_app",
}
