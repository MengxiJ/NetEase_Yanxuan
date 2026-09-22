"""
Mock 契约测试（无接口文档场景的接口测试层）

校验本地 Mock 服务的接口契约，覆盖：
- 业务码与 HTTP 状态分离（严选风格：HTTP 200 + code 字段）
- 登录：成功 / 密码错误 / 参数缺失
- 搜索：命中（参数化）/ 空结果
- 购物车：添加后查询一致性（有状态）/ 参数校验
- 订单：列表结构 / 状态筛选
- 容错与性能：故障注入 500 / 未知路由 404 / 延迟注入（响应时间阈值）
"""
import time

import allure
import pytest

from api.config import HAR_CONFIG

# 与 App 自动化层、Mock 服务保持一致的账号与关键词
ACCOUNT = {"username": "17658097530", "password": "Aa123456"}
HIT_KEYWORDS = ["毛巾", "牛奶", "饼干"]


@allure.feature("接口测试")
@allure.story("Mock 契约")
@pytest.mark.api
@pytest.mark.mock
@pytest.mark.regression
class TestMockService:
    """Mock 服务契约测试"""

    @staticmethod
    def _auth_headers(api_client):
        """登录获取 token，返回受保护接口（订单）所需的鉴权头"""
        resp = api_client.post("/api/user/login.do", json=ACCOUNT)
        token = resp.json()["result"]["token"]
        return {"Authorization": token}

    def test_service_health(self, api_client):
        """健康检查：/status 返回服务名与版本"""
        resp = api_client.get("/status")
        assert resp.status_code == 200
        body = resp.json()
        assert body["code"] == 200
        assert body["result"]["service"] == "yanxuan-mock"
        assert body["result"]["version"]
        assert resp.headers["X-Mock-Server"].startswith("yanxuan-mock")

    def test_login_success(self, api_client):
        """登录成功：返回昵称与 token"""
        resp = api_client.post("/api/user/login.do", json=ACCOUNT)
        assert resp.status_code == 200
        body = resp.json()
        assert body["code"] == 200
        assert body["result"]["nickname"] == "严选测试用户"
        assert body["result"]["token"].startswith("mock-token-")

    def test_login_wrong_password(self, api_client):
        """登录失败：密码错误返回业务码 401（HTTP 状态仍为 200）"""
        resp = api_client.post("/api/user/login.do", json={
            "username": ACCOUNT["username"], "password": "wrong-password",
        })
        assert resp.status_code == 200
        body = resp.json()
        assert body["code"] == 401
        assert "密码" in body["message"]

    def test_login_missing_params(self, api_client):
        """登录参数校验：缺少密码返回业务码 400"""
        resp = api_client.post("/api/user/login.do", json={"username": ACCOUNT["username"]})
        assert resp.status_code == 200
        assert resp.json()["code"] == 400

    @pytest.mark.parametrize("keyword", HIT_KEYWORDS)
    def test_search_hit(self, api_client, keyword):
        """搜索命中：关键词返回商品列表，字段结构完整"""
        allure.dynamic.title("搜索命中: {}".format(keyword))
        resp = api_client.get("/api/goods/search.do", params={"keyword": keyword})
        body = resp.json()
        assert body["code"] == 200
        result = body["result"]
        assert result["totalCount"] > 0
        assert len(result["list"]) == result["totalCount"]
        for goods in result["list"]:
            assert set(goods.keys()) == {"id", "name", "price"}
            assert goods["price"] > 0
            assert keyword in goods["name"]

    def test_search_no_result(self, api_client):
        """搜索空结果：不存在的关键词返回空列表"""
        resp = api_client.get("/api/goods/search.do", params={"keyword": "不存在的商品xyz123"})
        body = resp.json()
        assert body["code"] == 200
        assert body["result"]["list"] == []
        assert body["result"]["totalCount"] == 0

    def test_cart_add_then_list(self, api_client):
        """购物车：添加商品后查询，数量与明细一致（有状态接口）"""
        add = api_client.post("/api/cart/add.do", json={"goodsId": 1001, "quantity": 2})
        assert add.json()["code"] == 200
        cart_count = add.json()["result"]["cartCount"]
        assert cart_count >= 2

        listing = api_client.get("/api/cart/list.do")
        body = listing.json()
        assert body["code"] == 200
        assert body["result"]["cartCount"] == cart_count
        assert any(item["goodsId"] == 1001 for item in body["result"]["list"])

    def test_cart_add_missing_goods(self, api_client):
        """购物车参数校验：缺少 goodsId 返回业务码 400"""
        resp = api_client.post("/api/cart/add.do", json={})
        assert resp.json()["code"] == 400

    def test_order_list_structure(self, api_client):
        """订单列表：结构与字段完整性（登录态访问）"""
        resp = api_client.get("/api/order/list.do", headers=self._auth_headers(api_client))
        body = resp.json()
        assert body["code"] == 200
        orders = body["result"]["list"]
        assert body["result"]["total"] == len(orders)
        for order in orders:
            assert {"orderNo", "status", "statusText", "amount"} <= set(order.keys())
            assert order["amount"] > 0

    def test_order_list_filter_by_status(self, api_client):
        """订单列表筛选：status=1 只返回待付款订单（登录态访问）"""
        resp = api_client.get(
            "/api/order/list.do",
            params={"status": 1},
            headers=self._auth_headers(api_client),
        )
        orders = resp.json()["result"]["list"]
        assert orders
        assert all(order["status"] == 1 for order in orders)

    def test_error_injection_500(self, api_client):
        """故障注入：HTTP 500 响应可被客户端正常接收与断言"""
        resp = api_client.get("/api/error/500.do")
        assert resp.status_code == 500
        assert resp.json()["code"] == 500

    def test_unknown_route_404(self, api_client):
        """未知路由：返回 HTTP 404 且响应体为业务 JSON"""
        resp = api_client.get("/api/not/exist.do")
        assert resp.status_code == 404
        assert resp.json()["code"] == 404

    def test_response_time_threshold(self, api_client):
        """响应时间：延迟注入 300ms 应低于配置阈值"""
        start = time.time()
        resp = api_client.get("/api/delay.do", params={"ms": 300})
        elapsed_ms = (time.time() - start) * 1000
        assert resp.status_code == 200
        assert elapsed_ms < HAR_CONFIG["response_time_ms"]

    def test_content_type_is_json(self, api_client):
        """响应头规范：Content-Type 必须为 application/json"""
        resp = api_client.get("/status")
        assert "application/json" in resp.headers["Content-Type"]

    @pytest.mark.parametrize("goods_id", [1, 2, 3])
    def test_goods_detail_exists(self, api_client, goods_id):
        """商品详情：存在的 goodsId 返回完整字段结构"""
        resp = api_client.get("/api/goods/detail.do", params={"goodsId": goods_id})
        body = resp.json()
        assert body["code"] == 200
        result = body["result"]
        assert result["id"] == goods_id
        assert {"name", "price", "stock", "sales", "images"} <= set(result.keys())
        assert result["price"] > 0
        assert len(result["images"]) >= 1

    def test_goods_detail_not_found(self, api_client):
        """商品详情：不存在的 goodsId 返回业务码 404"""
        resp = api_client.get("/api/goods/detail.do", params={"goodsId": 9999})
        assert resp.json()["code"] == 404

    def test_goods_detail_missing_param(self, api_client):
        """商品详情：缺少 goodsId 返回业务码 400"""
        resp = api_client.get("/api/goods/detail.do")
        assert resp.json()["code"] == 400

    def test_user_profile_authorized(self, api_client):
        """用户信息：登录态访问返回昵称与会员信息"""
        resp = api_client.get("/api/user/profile.do", headers=self._auth_headers(api_client))
        body = resp.json()
        assert body["code"] == 200
        assert body["result"]["nickname"] == "严选测试用户"
        assert body["result"]["vip"] is True
        assert body["result"]["points"] > 0

    def test_user_profile_unauthorized(self, api_client):
        """用户信息：无 token 返回业务码 401"""
        resp = api_client.get("/api/user/profile.do")
        assert resp.json()["code"] == 401

    def test_user_profile_invalid_token(self, api_client):
        """用户信息：非法 token 前缀返回业务码 401"""
        resp = api_client.get("/api/user/profile.do", headers={"Authorization": "Bearer bad"})
        assert resp.json()["code"] == 401

    def test_coupon_receive_success(self, api_client):
        """优惠券领取：首次领取成功并返回剩余库存"""
        resp = api_client.post("/api/coupon/receive.do", json={"userId": 10086, "couponId": 100})
        body = resp.json()
        assert body["code"] == 200
        assert body["result"]["couponId"] == 100
        assert body["result"]["stockLeft"] >= 0

    def test_coupon_receive_duplicate(self, api_client):
        """优惠券领取：同一用户重复领取返回业务码 409"""
        payload = {"userId": 10086, "couponId": 200}
        api_client.post("/api/coupon/receive.do", json=payload)
        resp = api_client.post("/api/coupon/receive.do", json=payload)
        assert resp.json()["code"] == 409

    def test_cart_update_success(self, api_client):
        """购物车更新：正整数 delta 累加并返回累计数量"""
        resp = api_client.post("/api/cart/update.do", json={"goodsId": 1001, "delta": 3})
        body = resp.json()
        assert body["code"] == 200
        assert body["result"]["cartCount"] >= 3

    def test_cart_update_reject_non_positive(self, api_client):
        """购物车更新：非正整数 delta 返回业务码 422"""
        for delta in (0, -1):
            resp = api_client.post("/api/cart/update.do", json={"goodsId": 1001, "delta": delta})
            assert resp.json()["code"] == 422
