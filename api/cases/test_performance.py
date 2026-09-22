"""
性能测试（基于本地 Mock 服务的轻量性能基线，零外部依赖）

覆盖企业级性能基线四要素：
- 延迟分位数（P50/P90/P95/P99）与阈值断言
- 吞吐量（QPS）下限断言
- 持续负载（线程池压测，零错误率 + 完成量下限）
- 响应时间稳定性（混合请求最大延迟阈值）

指标通过 logger 输出并附加到 Allure 报告（JSON attachment）。
接入真实被测系统时仅需切换 base_url 并按 SLA 收紧阈值；
如需大规模压测可平滑迁移至 Locust/JMeter（本层用例作为基线校验保留）。
"""
import json
import math
import time
from concurrent.futures import ThreadPoolExecutor

import allure
import pytest

from api.client import ApiClient
from base import logger

# 性能基线阈值（本地 Mock，宽阈值防环境抖动；接入真实系统后按 SLA 收紧）
LATENCY_SAMPLES = 40      # 延迟采样请求数
P95_THRESHOLD_MS = 1000   # /status P95 阈值（毫秒）
DELAY_MS = 100            # 延迟注入值（验证服务端延迟真实生效）
QPS_SAMPLES = 40          # 吞吐采样请求数
QPS_FLOOR = 20            # QPS 下限
LOAD_WORKERS = 4          # 持续负载并发线程数
LOAD_DURATION_S = 2.5     # 持续负载时长（秒）
LOAD_MIN_TOTAL = 60       # 持续负载最少完成请求数
STABILITY_MAX_MS = 3000   # 混合请求最大延迟阈值（毫秒）


def _percentile(values, p):
    """计算分位数（最近邻上取整法）"""
    data = sorted(values)
    index = max(0, math.ceil(p / 100 * len(data)) - 1)
    return data[index]


def _attach_stats(name, stats):
    """性能指标输出到日志并附加到 Allure 报告"""
    logger.info("[Perf] {}: {}".format(name, stats))
    allure.attach(
        json.dumps(stats, ensure_ascii=False, indent=2),
        name=name, attachment_type=allure.attachment_type.JSON,
    )


@allure.feature("性能测试")
@pytest.mark.api
@pytest.mark.perf
@pytest.mark.regression
class TestPerformance:
    """性能基线测试（本地 Mock 服务）"""

    def test_latency_percentiles(self, mock_server):
        """/status 延迟分位数：P95 低于阈值"""
        client = ApiClient(base_url=mock_server)
        latencies = []
        for _ in range(LATENCY_SAMPLES):
            start = time.perf_counter()
            resp = client.get("/status")
            latencies.append((time.perf_counter() - start) * 1000)
            assert resp.status_code == 200
        stats = {
            "samples": LATENCY_SAMPLES,
            "p50_ms": round(_percentile(latencies, 50), 2),
            "p90_ms": round(_percentile(latencies, 90), 2),
            "p95_ms": round(_percentile(latencies, 95), 2),
            "p99_ms": round(_percentile(latencies, 99), 2),
            "max_ms": round(max(latencies), 2),
        }
        _attach_stats("status_latency_percentiles", stats)
        assert stats["p95_ms"] < P95_THRESHOLD_MS

    def test_delay_injection_effective(self, mock_server):
        """延迟注入真实生效：均值不低于注入值的 80%"""
        client = ApiClient(base_url=mock_server)
        latencies = []
        for _ in range(20):
            start = time.perf_counter()
            resp = client.get("/api/delay.do", params={"ms": DELAY_MS})
            latencies.append((time.perf_counter() - start) * 1000)
            assert resp.status_code == 200
        mean_ms = sum(latencies) / len(latencies)
        stats = {
            "delay_ms": DELAY_MS,
            "mean_ms": round(mean_ms, 2),
            "p95_ms": round(_percentile(latencies, 95), 2),
        }
        _attach_stats("delay_injection", stats)
        assert mean_ms >= DELAY_MS * 0.8
        assert stats["p95_ms"] < 2000

    def test_throughput_qps(self, mock_server):
        """吞吐量：顺序请求 QPS 不低于下限"""
        client = ApiClient(base_url=mock_server)
        start = time.perf_counter()
        for _ in range(QPS_SAMPLES):
            assert client.get("/status").status_code == 200
        elapsed = time.perf_counter() - start
        qps = QPS_SAMPLES / elapsed
        stats = {
            "requests": QPS_SAMPLES,
            "elapsed_s": round(elapsed, 3),
            "qps": round(qps, 1),
        }
        _attach_stats("throughput_qps", stats)
        assert qps > QPS_FLOOR

    def test_sustained_load(self, mock_server):
        """持续负载：4 线程压测 2.5s，零错误且完成量达标"""
        deadline = time.perf_counter() + LOAD_DURATION_S

        def worker():
            client = ApiClient(base_url=mock_server)
            count = 0
            while time.perf_counter() < deadline:
                resp = client.get("/status")
                assert resp.status_code == 200
                assert resp.json()["code"] == 200
                count += 1
            return count

        with ThreadPoolExecutor(max_workers=LOAD_WORKERS) as pool:
            counts = list(pool.map(lambda _: worker(), range(LOAD_WORKERS)))
        total = sum(counts)
        stats = {
            "workers": LOAD_WORKERS,
            "duration_s": LOAD_DURATION_S,
            "total_requests": total,
            "per_worker": counts,
            "errors": 0,
        }
        _attach_stats("sustained_load", stats)
        assert total >= LOAD_MIN_TOTAL

    def test_response_time_stability(self, mock_server):
        """稳定性：混合请求（健康检查/搜索/订单）最大延迟低于阈值"""
        client = ApiClient(base_url=mock_server)
        auth = {"Authorization": "mock-token-perf"}
        targets = [
            ("GET", "/status", None, None),
            ("GET", "/api/goods/search.do", {"keyword": "毛巾"}, None),
            ("GET", "/api/order/list.do", None, auth),
        ]
        max_ms = 0
        for i in range(30):
            _, path, params, headers = targets[i % len(targets)]
            start = time.perf_counter()
            resp = client.get(path, params=params, headers=headers)
            elapsed = (time.perf_counter() - start) * 1000
            max_ms = max(max_ms, elapsed)
            assert resp.status_code == 200
        stats = {"requests": 30, "max_ms": round(max_ms, 2)}
        _attach_stats("response_time_stability", stats)
        assert max_ms < STABILITY_MAX_MS
