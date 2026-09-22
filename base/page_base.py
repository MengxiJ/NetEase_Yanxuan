import os
import time
import functools
from datetime import datetime

from appium.webdriver.common.appiumby import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from base import logger
from config import BASE_DIR


def step_result(step_name, status, message, data=None):
    """统一构建 Step 返回值（参照原子化框架规范）"""
    return {
        "step": step_name,
        "status": status,
        "message": message,
        "data": data or {},
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }


def check_result(check_name, result, message, expected=None, actual=None, data=None):
    """统一构建 Check 返回值（参照原子化框架规范）"""
    return {
        "check": check_name,
        "result": result,
        "status": result,
        "message": message,
        "expected": expected,
        "actual": actual,
        "data": data or {},
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }


def with_retry(retries=3, interval=1):
    """重试装饰器（参照原子化框架异常处理规范）"""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            last_exc = None
            for attempt in range(1, retries + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exc = e
                    logger.warning(f"[{func.__name__}] 第{attempt}/{retries}次尝试失败: {e}")
                    if attempt < retries:
                        time.sleep(interval)
            raise last_exc
        return wrapper
    return decorator


class PageBase:
    """页面对象基类

    参照 AutoTestRes 原子化框架的分层思想：
    - 页面操作方法（step_xxx）返回统一结构
    - 页面检查方法（check_xxx）返回统一结构
    - 所有底层操作内置异常处理与日志
    """

    def __init__(self, driver):
        self.driver = driver

    # ============ 元素定位（底层能力） ============

    @with_retry(retries=3, interval=1)
    def fd_element(self, locator, timeout=15):
        """定位单个元素（带显式等待 + 重试）"""
        logger.info(f"定位元素: {locator}")
        element = WebDriverWait(self.driver, timeout).until(
            EC.visibility_of_element_located(locator)
        )
        return element

    @with_retry(retries=3, interval=1)
    def fd_elements(self, locator, timeout=15):
        """定位多个元素（带显式等待 + 重试）"""
        logger.info(f"定位多个元素: {locator}")
        return WebDriverWait(self.driver, timeout).until(
            EC.visibility_of_all_elements_located(locator)
        )

    def is_element_exist(self, locator, timeout=5):
        """判断元素是否存在（用于检查点）"""
        try:
            WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located(locator)
            )
            return True
        except Exception:
            return False

    # ============ 页面操作（Step 层） ============

    def base_click(self, locator):
        """点击元素"""
        try:
            logger.info(f"点击元素: {locator}")
            self.fd_element(locator).click()
            return step_result("base_click", True, f"点击成功: {locator}")
        except Exception as e:
            logger.error(f"点击失败: {locator} - {e}")
            return step_result("base_click", False, f"点击失败: {e}", {"error": str(e)})

    def base_input_text(self, locator, text):
        """输入文本"""
        try:
            logger.info(f"在元素 {locator} 输入文本: {text}")
            element = self.fd_element(locator)
            element.clear()
            element.send_keys(text)
            return step_result("base_input_text", True, f"输入成功: {text}")
        except Exception as e:
            logger.error(f"输入失败: {locator} - {e}")
            return step_result("base_input_text", False, f"输入失败: {e}", {"error": str(e)})

    def base_swipe(self, start_x, start_y, end_x, end_y, duration=1000):
        """滑动操作"""
        try:
            logger.info(f"滑动: ({start_x},{start_y}) -> ({end_x},{end_y})")
            self.driver.swipe(start_x, start_y, end_x, end_y, duration)
            return step_result("base_swipe", True, "滑动成功")
        except Exception as e:
            logger.error(f"滑动失败: {e}")
            return step_result("base_swipe", False, f"滑动失败: {e}", {"error": str(e)})

    def base_press_key(self, keycode):
        """按键操作"""
        try:
            logger.info(f"按键: {keycode}")
            self.driver.press_keycode(keycode)
            return step_result("base_press_key", True, f"按键成功: {keycode}")
        except Exception as e:
            logger.error(f"按键失败: {e}")
            return step_result("base_press_key", False, f"按键失败: {e}", {"error": str(e)})

    def base_back(self):
        """返回键"""
        try:
            self.driver.back()
            return step_result("base_back", True, "返回成功")
        except Exception as e:
            return step_result("base_back", False, f"返回失败: {e}", {"error": str(e)})

    # ============ 页面检查（Check 层） ============

    def base_get_text(self, locator):
        """获取元素文本"""
        try:
            text = self.fd_element(locator).text
            logger.info(f"获取元素文本: {locator} -> {text}")
            return text
        except Exception as e:
            logger.error(f"获取文本失败: {locator} - {e}")
            return ""

    def check_text_exists(self, locator, expected_text):
        """检查元素文本是否包含预期内容（Check 点）"""
        actual = self.base_get_text(locator)
        result = expected_text in actual
        return check_result(
            "check_text_exists",
            result,
            f"文本检查{'通过' if result else '失败'}",
            expected=f"包含 '{expected_text}'",
            actual=actual,
        )

    def base_get_toast(self, toast_loc, timeout=10):
        """获取Toast提示文本"""
        try:
            toast = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located(toast_loc)
            )
            text = toast.text
            logger.info(f"获取Toast提示: {text}")
            return text
        except Exception as e:
            logger.error(f"获取Toast失败: {e}")
            return ""

    def check_toast(self, toast_loc, expected_text, timeout=10):
        """检查Toast提示文本（Check 点）"""
        actual = self.base_get_toast(toast_loc, timeout)
        result = expected_text in actual
        return check_result(
            "check_toast",
            result,
            f"Toast检查{'通过' if result else '失败'}",
            expected=expected_text,
            actual=actual,
        )

    def check_element_visible(self, locator, timeout=10):
        """检查元素是否可见（Check 点）"""
        result = self.is_element_exist(locator, timeout)
        return check_result(
            "check_element_visible",
            result,
            f"元素可见性检查: {'可见' if result else '不可见'}",
            expected="可见",
            actual="可见" if result else "不可见",
        )

    # ============ UI 界面检查（Check 层扩展） ============

    def check_element_text_equal(self, locator, expected_text):
        """检查元素文本是否完全等于预期"""
        actual = self.base_get_text(locator)
        result = actual == expected_text
        return check_result(
            "check_element_text_equal",
            result,
            f"文本相等检查: {'通过' if result else '失败'}",
            expected=expected_text,
            actual=actual,
        )

    def check_element_enabled(self, locator):
        """检查元素是否可点击/启用"""
        try:
            element = self.fd_element(locator)
            enabled = element.is_enabled()
            return check_result(
                "check_element_enabled",
                enabled,
                f"元素启用状态: {'启用' if enabled else '禁用'}",
                expected="启用",
                actual="启用" if enabled else "禁用",
            )
        except Exception as e:
            return check_result(
                "check_element_enabled",
                False,
                f"检查失败: {e}",
                expected="启用",
                actual="元素不存在",
            )

    def check_elements_count(self, locator, expected_count):
        """检查匹配元素数量"""
        try:
            elements = self.fd_elements(locator)
            actual = len(elements)
            result = actual == expected_count
            return check_result(
                "check_elements_count",
                result,
                f"元素数量检查: {'通过' if result else '失败'}",
                expected=str(expected_count),
                actual=str(actual),
            )
        except Exception as e:
            return check_result(
                "check_elements_count",
                False,
                f"检查失败: {e}",
                expected=str(expected_count),
                actual="0",
            )

    def check_element_attribute(self, locator, attribute, expected_value):
        """检查元素属性值"""
        try:
            element = self.fd_element(locator)
            actual = element.get_attribute(attribute) or ""
            result = expected_value in actual
            return check_result(
                "check_element_attribute",
                result,
                f"属性 {attribute} 检查: {'通过' if result else '失败'}",
                expected=expected_value,
                actual=actual,
            )
        except Exception as e:
            return check_result(
                "check_element_attribute",
                False,
                f"检查失败: {e}",
                expected=expected_value,
                actual="获取失败",
            )

    def check_page_loaded(self, key_locator, timeout=15):
        """页面加载完成检查（通过关键元素是否存在判断）"""
        result = self.is_element_exist(key_locator, timeout)
        return check_result(
            "check_page_loaded",
            result,
            f"页面{'已加载' if result else '未加载'}",
            expected="关键元素可见",
            actual="可见" if result else "不可见",
        )

    def get_element_rect(self, locator):
        """获取元素位置和尺寸（用于布局校验）"""
        try:
            element = self.fd_element(locator)
            rect = element.rect
            return rect  # {'x':, 'y':, 'width':, 'height':}
        except Exception as e:
            logger.error(f"获取元素位置失败: {e}")
            return {}

    # ============ 辅助工具 ============

    def get_shot(self, file_name):
        """截图保存到 img 目录"""
        file_path = os.path.join(BASE_DIR, 'img', file_name)
        try:
            self.driver.get_screenshot_as_file(file_path)
            logger.info(f"截图保存: {file_path}")
            return step_result("get_shot", True, f"截图成功: {file_name}")
        except Exception as e:
            logger.error(f"截图失败: {e}")
            return step_result("get_shot", False, f"截图失败: {e}", {"error": str(e)})

    def get_window_size(self):
        """获取屏幕尺寸"""
        size = self.driver.get_window_size()
        return size["width"], size["height"]

    def swipe_up(self, duration=1000):
        """向上滑动"""
        w, h = self.get_window_size()
        return self.base_swipe(w // 2, int(h * 0.8), w // 2, int(h * 0.2), duration)

    def swipe_down(self, duration=1000):
        """向下滑动"""
        w, h = self.get_window_size()
        return self.base_swipe(w // 2, int(h * 0.2), w // 2, int(h * 0.8), duration)

    def swipe_left(self, duration=1000):
        """向左滑动"""
        w, h = self.get_window_size()
        return self.base_swipe(int(w * 0.8), h // 2, int(w * 0.2), h // 2, duration)

    def swipe_right(self, duration=1000):
        """向右滑动"""
        w, h = self.get_window_size()
        return self.base_swipe(int(w * 0.2), h // 2, int(w * 0.8), h // 2, duration)
