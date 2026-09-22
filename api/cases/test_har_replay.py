"""
HAR 抓包回放测试（配合 Charles 抓包，无接口文档场景）

- 自动发现 api/data/captured/*.har（Charles: File → Export Session → HAR）
- 逐条回放请求并校验：状态码类别 / JSON 可解析 / 顶层结构键 / 响应时间阈值
- 支持 HAR_CONFIG.url_rewrite 域名重写（生产抓包 → Mock/测试环境回放）
- 目录内置 sample.har 示例（域名 mock.yanxuan.local 重写至本地 Mock 服务），
  真实 Charles 导出文件放入同目录即可并存回放
"""
import json
import os

import allure
import pytest

from api.client import ApiClient
from api.config import HAR_CONFIG
from api.utils.har_replay import (
    build_request_kwargs,
    discover_har_files,
    load_replay_entries,
    status_class,
)

# 收集阶段解析 HAR（纯文件解析，不依赖任何服务）
HAR_FILES = discover_har_files()
REPLAY_ENTRIES = load_replay_entries()


@pytest.mark.skipif(not HAR_FILES, reason="未发现 Charles 导出的 HAR 文件（api/data/captured/）")
@allure.feature("接口测试")
@allure.story("抓包回放")
@pytest.mark.api
@pytest.mark.har
@pytest.mark.regression
class TestHarReplay:
    """HAR 抓包回放测试"""

    @pytest.mark.parametrize(
        "har_file", HAR_FILES, ids=[os.path.basename(f) for f in HAR_FILES]
    )
    def test_har_file_valid(self, har_file):
        """HAR 文件结构合法：log.entries 存在且非空"""
        with open(har_file, "r", encoding="utf-8-sig") as f:
            data = json.load(f)
        entries = data.get("log", {}).get("entries")
        assert isinstance(entries, list) and entries, "{}: log.entries 为空".format(har_file)

    @pytest.mark.skipif(not REPLAY_ENTRIES, reason="过滤后无待回放请求")
    @pytest.mark.parametrize("entry", REPLAY_ENTRIES, ids=[e["id"] for e in REPLAY_ENTRIES])
    def test_replay_request(self, entry, mock_server):
        """回放单条抓包请求并比对契约"""
        allure.dynamic.title("回放 {}".format(entry["id"]))
        client = ApiClient()
        resp = client.request(**build_request_kwargs(entry, mock_base=mock_server))

        # 1. 状态码比对（默认按 2xx/4xx/5xx 类别，容忍环境差异导致的漂移）
        if HAR_CONFIG["status_class_match"]:
            assert status_class(resp.status_code) == status_class(entry["expected_status"]), (
                "{} 状态码类别不符: 抓包 {} 实际 {}".format(
                    entry["id"], entry["expected_status"], resp.status_code
                )
            )
        else:
            assert resp.status_code == entry["expected_status"], (
                "{} 状态码不符: 抓包 {} 实际 {}".format(
                    entry["id"], entry["expected_status"], resp.status_code
                )
            )

        # 2. 响应时间阈值
        elapsed_ms = resp.elapsed.total_seconds() * 1000
        assert elapsed_ms < HAR_CONFIG["response_time_ms"], (
            "{} 响应超时: {}ms >= {}ms".format(entry["id"], elapsed_ms, HAR_CONFIG["response_time_ms"])
        )

        # 3. JSON 可解析 + 顶层结构键比对（抓包存有响应正文时，检测接口结构变更）
        content_type = resp.headers.get("Content-Type", "")
        if "json" in content_type.lower():
            actual = resp.json()
            assert isinstance(actual, dict), "{} 响应应为 JSON 对象".format(entry["id"])
            if entry["expected_keys"] is not None:
                assert set(actual.keys()) == entry["expected_keys"], (
                    "{} 响应顶层结构变更: 抓包 {} 实际 {}".format(
                        entry["id"], sorted(entry["expected_keys"]), sorted(actual.keys())
                    )
                )
