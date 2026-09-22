"""
原子化测试框架（参照 AutoTestRes 项目结构）

├── registry.py          # Step/Check 注册表
├── workflow_runner.py   # 工作流执行主入口
├── step_impl/           # 步骤节点注册（按业务域分组）
├── check_impl/          # 检查节点注册（按业务域分组）
├── utils/
│   └── composer.py      # 工作流编排器（节点执行、路由、变量解析）
└── workflows/           # JSON 工作流用例（按类别分组：function / ui）
"""
# 导入顺序：先触发 step/check 注册，再导出执行器
from tblocks import step_impl   # noqa: F401 触发 step 注册
from tblocks import check_impl  # noqa: F401 触发 check 注册
from tblocks.workflow_runner import WorkflowExecutor, run_workflow

__all__ = ["WorkflowExecutor", "run_workflow"]
