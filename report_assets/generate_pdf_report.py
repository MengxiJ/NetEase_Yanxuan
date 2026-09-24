"""
生成 PDF 测试报告
用法：python generate_pdf_report.py
依赖：reportlab
"""
import os
import json
import glob
from datetime import datetime

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak,
)

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(SCRIPT_DIR)  # 项目根目录
REPORT_DIR = os.path.join(BASE_DIR, "report")
OUTPUT_PDF = os.path.join(SCRIPT_DIR, "test_report.pdf")

pdfmetrics.registerFont(TTFont("SimHei", r"C:\Windows\Fonts\simhei.ttf"))

STYLES = getSampleStyleSheet()
STYLES.add(ParagraphStyle(name="ChineseTitle", fontName="SimHei", fontSize=20, leading=28,
                          alignment=1, spaceAfter=20, textColor=colors.HexColor("#1a1a1a")))
STYLES.add(ParagraphStyle(name="ChineseH1", fontName="SimHei", fontSize=14, leading=20,
                          spaceBefore=12, spaceAfter=8, textColor=colors.HexColor("#2c5282")))
STYLES.add(ParagraphStyle(name="ChineseSmall", fontName="SimHei", fontSize=8, leading=12,
                          textColor=colors.HexColor("#718096")))


def parse_results():
    cases = []
    for f in glob.glob(os.path.join(REPORT_DIR, "*-result.json")):
        try:
            with open(f, "r", encoding="utf-8") as fp:
                data = json.load(fp)
            cases.append({
                "name": data.get("name", ""),
                "status": data.get("status", "unknown"),
                "description": data.get("description", ""),
                "fullName": data.get("fullName", ""),
                "start": data.get("start", 0),
                "stop": data.get("stop", 0),
                "duration_ms": data.get("stop", 0) - data.get("start", 0),
                "feature": next((l["value"] for l in data.get("labels", []) if l["name"] == "feature"), "未分类"),
            })
        except Exception:
            continue
    return cases


def build_pdf(cases):
    doc = SimpleDocTemplate(OUTPUT_PDF, pagesize=A4,
                            leftMargin=20 * mm, rightMargin=20 * mm,
                            topMargin=20 * mm, bottomMargin=20 * mm)
    story = []

    total = len(cases)
    passed = sum(1 for c in cases if c["status"] == "passed")
    failed = sum(1 for c in cases if c["status"] in ("failed", "broken"))
    skipped = sum(1 for c in cases if c["status"] == "skipped")
    pass_rate = (passed / total * 100) if total > 0 else 0

    if cases:
        total_sec = (max(c["stop"] for c in cases) - min(c["start"] for c in cases)) / 1000.0
    else:
        total_sec = 0
    total_dur = sum(c["duration_ms"] for c in cases) / 1000.0

    story.append(Paragraph("网易严选 App 自动化测试报告", STYLES["ChineseTitle"]))
    story.append(Paragraph("生成时间：" + datetime.now().strftime("%Y-%m-%d %H:%M:%S"), STYLES["ChineseSmall"]))
    story.append(Spacer(1, 10 * mm))

    story.append(Paragraph("一、测试概览", STYLES["ChineseH1"]))
    overview = [
        ["指标", "数值"],
        ["总用例数", str(total)],
        ["通过", str(passed)],
        ["失败", str(failed)],
        ["跳过", str(skipped)],
        ["通过率", f"{pass_rate:.2f}%"],
        ["总耗时（墙钟）", f"{total_sec:.2f} 秒"],
        ["用例执行总耗时", f"{total_dur:.2f} 秒"],
    ]
    t = Table(overview, colWidths=[60 * mm, 100 * mm])
    t.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (-1, -1), "SimHei"),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2c5282")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e0")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f7fafc")]),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(t)
    story.append(Spacer(1, 8 * mm))

    story.append(Paragraph("二、测试环境", STYLES["ChineseH1"]))
    env_data = [["环境项", "值"]]
    env_path = os.path.join(REPORT_DIR, "environment.properties")
    if os.path.exists(env_path):
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if "=" in line:
                    k, v = line.split("=", 1)
                    env_data.append([k, v])
    env_data.extend([
        ["测试框架", "pytest + Appium"],
        ["被测应用", "网易严选 (com.netease.yanxuan)"],
        ["设备", "MuMu 模拟器 (127.0.0.1:7555)"],
    ])
    t2 = Table(env_data, colWidths=[55 * mm, 105 * mm])
    t2.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (-1, -1), "SimHei"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2c5282")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e0")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f7fafc")]),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    story.append(t2)
    story.append(Spacer(1, 8 * mm))

    story.append(Paragraph("三、分组统计", STYLES["ChineseH1"]))
    groups = {}
    for c in cases:
        f = c["feature"]
        groups.setdefault(f, {"total": 0, "passed": 0, "failed": 0, "skipped": 0})
        groups[f]["total"] += 1
        if c["status"] == "passed":
            groups[f]["passed"] += 1
        elif c["status"] in ("failed", "broken"):
            groups[f]["failed"] += 1
        else:
            groups[f]["skipped"] += 1
    group_data = [["分组", "总数", "通过", "失败", "跳过", "通过率"]]
    for f, g in sorted(groups.items()):
        rate = f"{g['passed'] / g['total'] * 100:.1f}%" if g["total"] > 0 else "-"
        group_data.append([f, str(g["total"]), str(g["passed"]), str(g["failed"]), str(g["skipped"]), rate])
    t3 = Table(group_data, colWidths=[35 * mm, 18 * mm, 18 * mm, 18 * mm, 18 * mm, 25 * mm])
    t3.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (-1, -1), "SimHei"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2c5282")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e0")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f7fafc")]),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    story.append(t3)
    story.append(Spacer(1, 8 * mm))

    story.append(Paragraph("四、用例执行明细", STYLES["ChineseH1"]))
    cases_sorted = sorted(cases, key=lambda x: (x["feature"], x["name"]))
    detail_data = [["序号", "用例名称", "分组", "状态", "耗时(ms)"]]
    for i, c in enumerate(cases_sorted, 1):
        st = "通过" if c["status"] == "passed" else ("跳过" if c["status"] == "skipped" else "失败")
        detail_data.append([str(i), c["name"], c["feature"], st, str(c["duration_ms"])])

    page_size = 30
    for i in range(0, len(detail_data), page_size):
        chunk = [detail_data[0]] + detail_data[i + 1:i + 1 + page_size]
        if len(chunk) <= 1:
            break
        t4 = Table(chunk, colWidths=[12 * mm, 55 * mm, 30 * mm, 18 * mm, 20 * mm], repeatRows=1)
        cmds = [
            ("FONTNAME", (0, 0), (-1, -1), "SimHei"),
            ("FONTSIZE", (0, 0), (-1, -1), 8),
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2c5282")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("ALIGN", (1, 1), (1, -1), "LEFT"),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e0")),
            ("TOPPADDING", (0, 0), (-1, -1), 3),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ]
        for row_idx, row in enumerate(chunk[1:], 1):
            if row[3] == "失败":
                cmds.append(("TEXTCOLOR", (3, row_idx), (3, row_idx), colors.red))
            elif row[3] == "通过":
                cmds.append(("TEXTCOLOR", (3, row_idx), (3, row_idx), colors.HexColor("#38a169")))
        for row_idx in range(2, len(chunk), 2):
            cmds.append(("BACKGROUND", (0, row_idx), (-1, row_idx), colors.HexColor("#f7fafc")))
        t4.setStyle(TableStyle(cmds))
        story.append(t4)
        if i + page_size < len(detail_data):
            story.append(PageBreak())
            story.append(Paragraph("四、用例执行明细（续）", STYLES["ChineseH1"]))

    doc.build(story)
    print(f"[PDF] 报告已生成: {OUTPUT_PDF}")
    print(f"[PDF] 用例总数: {total}, 通过: {passed}, 失败: {failed}, 跳过: {skipped}, 通过率: {pass_rate:.2f}%")


if __name__ == "__main__":
    cases = parse_results()
    if not cases:
        print("[错误] 未找到 allure 结果文件，请先运行 pytest")
        exit(1)
    build_pdf(cases)
