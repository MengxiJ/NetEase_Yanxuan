"""
安全测试（基于本地 Mock 服务的 HTTP 层安全基线）

覆盖 OWASP 常见风险在接口层的基线校验：
- 注入防护：SQL 注入 / XSS 载荷不引发异常、不绕过鉴权、不泄露数据
- 越权防护：受保护接口（订单）无 token / 无效 token 一律拒绝
- 信息泄露：密码不回显、错误响应不含堆栈等内部细节
- 报文规范：超大请求体 413 拒绝、畸形 JSON 优雅处理、不支持的方法 405
- 响应安全头：X-Content-Type-Options: nosniff
"""
import allure
import pytest

from api.client import ApiClient

ACCOUNT = {"username": "17658097530", "password": "Aa123456"}

SQL_PAYLOADS = [
    "' OR 1=1 --",
    "1; DROP TABLE users; --",
    "' UNION SELECT username, password FROM users --",
]
XSS_PAYLOAD = "<script>alert('xss')</script>"


@allure.feature("安全测试")
@pytest.mark.api
@pytest.mark.security
@pytest.mark.regression
class TestSecurity:
    """HTTP 层安全基线测试"""

    @pytest.mark.parametrize("payload", SQL_PAYLOADS)
    def test_sql_injection_search(self, api_client, payload):
        """SQL 注入载荷作为搜索词：不崩溃、不泄露数据（返回空结果）"""
        resp = api_client.get("/api/goods/search.do", params={"keyword": payload})
        assert resp.status_code == 200
        body = resp.json()
        assert body["code"] == 200
        assert body["result"]["list"] == [], "注入载荷不应命中任何数据"
        assert body["result"]["totalCount"] == 0

    def test_sql_injection_login_no_bypass(self, api_client):
        """SQL 注入载荷作为登录凭据：无法绕过鉴权"""
        resp = api_client.post("/api/user/login.do", json={
            "username": "' OR 1=1 --", "password": "' OR '1'='1",
        })
        assert resp.json()["code"] == 401

    def test_xss_payload_inert_in_json(self, api_client):
        """XSS 载荷以惰性数据返回：JSON 上下文（非 HTML），无脚本执行环境"""
        resp = api_client.get("/api/goods/search.do", params={"keyword": XSS_PAYLOAD})
        assert "application/json" in resp.headers["Content-Type"]
        assert "text/html" not in resp.headers["Content-Type"].lower()
        body = resp.json()
        assert body["code"] == 200
        # 载荷作为纯数据回显（JSON 字符串字段），不构成 HTML 注入
        assert body["result"]["keyword"] == XSS_PAYLOAD

    def test_password_not_reflected(self, api_client):
        """敏感信息不泄露：响应正文不得包含明文密码或 password 字段"""
        resp = api_client.post("/api/user/login.do", json=ACCOUNT)
        assert ACCOUNT["password"] not in resp.text
        assert "password" not in resp.text.lower()

    def test_unauthorized_order_access(self, api_client):
        """越权防护：订单接口无 token / 无效 token 一律拒绝，有效 token 放行"""
        no_token = api_client.get("/api/order/list.do")
        assert no_token.json()["code"] == 401

        bad_token = api_client.get(
            "/api/order/list.do", headers={"Authorization": "Bearer invalid"}
        )
        assert bad_token.json()["code"] == 401

        login = api_client.post("/api/user/login.do", json=ACCOUNT)
        token = login.json()["result"]["token"]
        ok = api_client.get("/api/order/list.do", headers={"Authorization": token})
        assert ok.json()["code"] == 200

    @pytest.mark.parametrize("method", ["PUT", "DELETE", "PATCH", "OPTIONS"])
    def test_method_not_allowed(self, api_client, method):
        """不支持的请求方法统一 405（优雅拒绝，而非协议层 501/5xx）"""
        resp = api_client.request(method, "/status")
        assert resp.status_code == 405
        assert resp.json()["code"] == 405

    def test_oversized_body_rejected(self, api_client):
        """超大请求体（>1MB）拒绝：HTTP 413"""
        payload = {"username": "a" * (1024 * 1024), "password": "x"}
        resp = api_client.post("/api/user/login.do", json=payload)
        assert resp.status_code == 413
        assert resp.json()["code"] == 413

    def test_malformed_json_body(self, api_client):
        """畸形 JSON 请求体：优雅处理（参数缺失 400，而非 500）"""
        resp = api_client.request(
            "POST", "/api/user/login.do",
            data="{not-valid-json",
            headers={"Content-Type": "application/json"},
        )
        assert resp.status_code == 200
        assert resp.json()["code"] == 400

    def test_no_internal_details_in_errors(self, api_client):
        """错误响应不含内部细节（堆栈 / 文件路径 / 异常语句）"""
        resp = api_client.get("/api/error/500.do")
        for leak in ("Traceback", "File \"", ".py", "raise "):
            assert leak not in resp.text, "错误响应泄露内部细节: {}".format(leak)

    def test_security_headers(self, api_client):
        """响应安全头：X-Content-Type-Options: nosniff（防 MIME 嗅探）"""
        resp = api_client.get("/status")
        assert resp.headers.get("X-Content-Type-Options") == "nosniff"
