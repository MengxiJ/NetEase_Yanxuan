# 项目配置文件
import os

# 项目根目录
BASE_DIR = os.path.dirname(__file__)

# ============ Appium 服务配置 ============
# Appium 3.x 使用根路径，2.x 使用 /wd/hub
APPIUM_SERVER = "http://127.0.0.1:4723"

# ============ 设备配置信息 ============
DEVICE_CONFIG = {
    "platformName": "Android",          # 移动端系统平台
    "platformVersion": "12",            # 平台版本
    "deviceName": "mumu",               # 设备名称
    "automationName": "UiAutomator2",   # 自动化引擎
    "udid": "127.0.0.1:7555",           # 设备唯一标识（MuMu 模拟器）
    "newCommandTimeout": 60,            # 命令超时时间（秒）
    "noSign": True,                     # 不重新签名
    "unicodeKeyboard": True,            # 支持中文输入
    "resetKeyboard": True,              # 测试后重置键盘
}

# ============ 应用配置信息 ============
APP_CONFIG = {
    "appPackage": "com.netease.yanxuan",        # 包名
    "appActivity": ".module.mainpage.activity.MainPageActivity",  # 启动 Activity
    "appWaitActivity": "*",                     # 等待任意 Activity
    "noReset": True,                            # 不清除数据，保留登录状态
}

# ============ 账号配置 ============
ACCOUNT = {
    "username": "17658097530",
    "password": "Aa123456",
}
