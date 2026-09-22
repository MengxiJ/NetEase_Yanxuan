"""接口测试 fixtures：本地 Mock 服务（会话级启停）与 API 客户端"""
import pytest

from api.client import ApiClient
from api.config import MOCK_CONFIG
from api.mock_server import start_mock_server, stop_mock_server


@pytest.fixture(scope="session")
def mock_server():
    """启动本地 Mock 服务（随机端口），返回 base_url；会话结束后停止"""
    server, base_url = start_mock_server(MOCK_CONFIG["host"], MOCK_CONFIG["port"])
    yield base_url
    stop_mock_server(server)


@pytest.fixture
def api_client(mock_server):
    """指向 Mock 服务的 API 客户端"""
    return ApiClient(base_url=mock_server)
