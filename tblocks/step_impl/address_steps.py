"""
地址管理模块步骤实现（step 逻辑从 pages 迁出）

真实页面结构（v3 dump 证实）：地址列表页点「新建地址」后直接弹出
省市区联动选择弹层（ll_mask + tab_view_address_manage + rv_address_manage +
btn_confirm_address_manage），无独立表单页；列表每屏仅显示约 7 项，
目标条目常在屏幕外，须滚动查找。北京市为直辖市：选省后直接进区县级，
「顺义区」为第二级、「马坡地区」为第三级（街道/地区）。
"""
import time

from base import logger
from base.page_base import step_result
from tblocks.registry import step
from pages.page_02_address import AddressPage


class AddressSteps(AddressPage):
    """地址管理 Step 实现（复用 AddressPage 元素定位与 PageBase 底层操作）"""

    def click_mine(self):
        """点击个人中心"""
        logger.info("[Step] 点击个人中心")
        return self.base_click(self._mine)

    def click_setting(self):
        """点击设置"""
        logger.info("[Step] 点击设置")
        return self.base_click(self._setting)

    def click_my_address(self):
        """点击我的地址"""
        logger.info("[Step] 点击我的地址")
        return self.base_click(self._address)

    def _scroll_find_click(self, locator, label, x=500, max_swipes=6):
        """在地区联动列表中滚动查找并点击目标条目（每屏约 7 项，目标可能在屏幕外）"""
        for _ in range(max_swipes):
            if self.is_element_exist(locator, timeout=2):
                res = self.base_click(locator)
                if res["status"]:
                    return res
            self.base_swipe(x, 2000, x, 1200)
        return {"status": False, "message": f"滚动查找{label}失败"}

    def select_province(self):
        """选择省份（子步骤失败即时中断，不再吞错）"""
        logger.info("[Step] 选择省份")
        add_res = self.base_click(self._add_address)
        if not add_res["status"]:
            return step_result("select_province", False, f"点击新建地址失败: {add_res['message']}")
        prov_res = self.base_click(self._province)
        if not prov_res["status"]:
            return step_result("select_province", False, f"选择省份失败: {prov_res['message']}")
        return step_result("select_province", True, "省份选择完成")

    def select_city(self, x=500):
        """选择区县（直辖市无市级，第二级即区县「顺义区」；滚动查找）"""
        logger.info("[Step] 选择区县")
        city_res = self._scroll_find_click(self._city, "区县(顺义区)", x)
        if not city_res["status"]:
            return step_result("select_city", False, f"选择区县失败: {city_res['message']}")
        return step_result("select_city", True, "区县选择完成")

    def select_county(self, x=500):
        """选择第三级地区/街道（「马坡地区」），选完点确定收起联动弹层"""
        logger.info("[Step] 选择地区/街道")
        county_res = self._scroll_find_click(self._county, "地区(马坡地区)", x)
        if not county_res["status"]:
            return step_result("select_county", False, f"选择地区失败: {county_res['message']}")
        time.sleep(1)
        confirm_res = self.base_click(self._confirm)
        if not confirm_res["status"]:
            return step_result("select_county", False, f"点击确定失败: {confirm_res['message']}")
        return step_result("select_county", True, "地区选择完成")

    def input_detail_address(self, detail, name, phone):
        """输入详细地址信息（子步骤失败即时中断，不再吞错）"""
        logger.info(f"[Step] 输入详细地址: name={name}, phone={phone}")
        for label, locator, text in (("详细地址", self._detail_address, detail),
                                     ("收货人", self._name, name),
                                     ("手机号", self._phone, phone)):
            res = self.base_input_text(locator, text)
            if not res["status"]:
                return step_result("input_detail_address", False, f"输入{label}失败: {res['message']}")
        self.base_click(self._save)
        return step_result("input_detail_address", True, f"地址信息已保存: {name}")

    def step_add_default_address(self, detail, name, phone):
        """添加默认地址业务步骤（子步骤失败即时中断，不再吞错）"""
        logger.info(f"[Step] 添加默认地址: {name}, {phone}")
        mine_res = self.click_mine()
        if not mine_res["status"]:
            return step_result("step_add_default_address", False, f"点击个人中心失败: {mine_res['message']}")
        setting_res = self.click_setting()
        if not setting_res["status"]:
            return step_result("step_add_default_address", False, f"点击设置失败: {setting_res['message']}")
        address_res = self.click_my_address()
        if not address_res["status"]:
            return step_result("step_add_default_address", False, f"点击我的地址失败: {address_res['message']}")
        for name_, fn in (("省份", lambda: self.select_province()),
                          ("城市", lambda: self.select_city()),
                          ("区县", lambda: self.select_county()),
                          ("地址信息", lambda: self.input_detail_address(detail, name, phone))):
            res = fn()
            if not res["status"]:
                return step_result("step_add_default_address", False, f"{name_}步骤失败: {res['message']}")
        return step_result("step_add_default_address", True, f"地址添加操作完成: {name}")


step("step_add_default_address", AddressSteps, "step_add_default_address")