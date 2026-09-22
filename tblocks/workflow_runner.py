"""
工作流执行主入口
参照 AutoTestRes 原子化框架的 workflow_runner.py 设计
"""
from tblocks.utils.composer import WorkflowExecutor


def run_workflow(driver, workflow_json_path, custom_params=None):
    """
    便捷运行单个工作流

    Args:
        driver: Appium driver 实例
        workflow_json_path: 工作流 JSON 文件路径
        custom_params: 自定义参数（支持 ${custom_params.xxx} 引用）

    Returns:
        dict: {success, workflow_id, executed_nodes, failed_node, results}
    """
    executor = WorkflowExecutor(driver, custom_params=custom_params)
    return executor.execute(workflow_json_path)


__all__ = ["WorkflowExecutor", "run_workflow"]
