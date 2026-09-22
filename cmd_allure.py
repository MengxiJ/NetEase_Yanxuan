# 1.导包
import os

# 2.配置cmd下执行命令（生成allure执行命令）
run_cmd = "allure generate ./report -o ./new_report --clean"
# 通过os.system(命令)方法运行终端命令（相当于在终端运行上述命令）
os.system(run_cmd)
# allure generate ：生成allure测试报告的命令
# ./report :allure ：运行生成的临时报告文件路径
# -o ./new_report ：输出HTML的报告到report路径下
# --clean ：清除报告目录下原有的历史数据
