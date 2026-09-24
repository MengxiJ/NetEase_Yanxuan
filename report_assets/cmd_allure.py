"""
一键生成 Allure 测试报告并在浏览器中打开

用法：
    python report_assets/cmd_allure.py            # 生成报告并自动打开浏览器
    python report_assets/cmd_allure.py --no-open  # 仅生成报告，不打开浏览器

前置条件：
    1. 已运行 pytest 生成 allure 原始数据（report/ 目录）
    2. 已安装 allure-pytest 与 allure CLI
"""
import os
import sys
import shutil
import webbrowser

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(SCRIPT_DIR)  # 项目根目录
RESULT_DIR = os.path.join(BASE_DIR, "report")
CATEGORIES_SRC = os.path.join(SCRIPT_DIR, "categories.json")
CATEGORIES_DST = os.path.join(RESULT_DIR, "categories.json")
REPORT_DIR = os.path.join(BASE_DIR, "new_report")


def copy_categories():
    """将失败分类模板复制到 allure 结果目录"""
    if os.path.exists(CATEGORIES_SRC):
        shutil.copy2(CATEGORIES_SRC, CATEGORIES_DST)
        print(f"[报告] 已复制失败分类: {CATEGORIES_DST}")
    else:
        print(f"[警告] 未找到 categories.json: {CATEGORIES_SRC}")


def generate_report():
    """生成 allure HTML 报告"""
    if not os.path.exists(RESULT_DIR) or not os.listdir(RESULT_DIR):
        print(f"[错误] allure 结果目录为空: {RESULT_DIR}")
        print("       请先运行 pytest 生成测试结果")
        return False
    cmd = f'allure generate "{RESULT_DIR}" -o "{REPORT_DIR}" --clean'
    print(f"[报告] 执行: {cmd}")
    ret = os.system(cmd)
    if ret == 0:
        print(f"[报告] 生成成功: {REPORT_DIR}")
        return True
    print(f"[错误] 报告生成失败，返回码: {ret}")
    return False


def open_report():
    """在浏览器中打开生成的报告"""
    index = os.path.join(REPORT_DIR, "index.html")
    if os.path.exists(index):
        webbrowser.open(f"file:///{index}")
        print(f"[报告] 已在浏览器打开: {index}")
    else:
        print(f"[警告] 未找到报告入口: {index}")


def main():
    no_open = "--no-open" in sys.argv
    copy_categories()
    if generate_report():
        if not no_open:
            open_report()


if __name__ == "__main__":
    main()
