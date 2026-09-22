"""
通用导航步骤（系统级操作，不绑定具体页面）
"""
from base import logger
from base.page_base import PageBase
from tblocks.registry import step


class NavSteps(PageBase):
    """通用导航 Step 实现（复用 PageBase 底层能力，无页面元素依赖）"""

    def press_back(self):
        """按下系统返回键"""
        logger.info("[Step] 按下系统返回键")
        return self.base_back()


step("press_back", NavSteps, "press_back")
