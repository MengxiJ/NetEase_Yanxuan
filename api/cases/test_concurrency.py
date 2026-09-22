"""
并发测试（基于本地 Mock 服务验证服务端线程安全与数据一致性）

覆盖：
- 并发登录：结果一致性（同 token / 同昵称，全部成功）
- 并发读（搜索）：结构完整、零失败
- 并发写（加购）：无丢失更新（最终数量 == 基线 + 并发数）
- 读写混合：读者始终读到自洽快照（count == 明细数量总和）
- 故障并发：错误注入下服务稳定（不崩溃、错误码准确、故障后恢复）
"""
from concurrent.futures import ThreadPoolExecutor

import allure
import pytest

from api.client import ApiClient

ACCOUNT = {"username": "17658097530", "password": "Aa123456"}


@allure.feature("并发测试")
@pytest.mark.api
@pytest.mark.concurrent
@pytest.mark.regression
class TestConcurrency:
    """并发测试（本地 Mock 服务）"""

    def test_concurrent_login_consistency(self, mock_server):
        """并发登录 20 线程：全部成功且结果一致"""
        def login(_):
            client = ApiClient(base_url=mock_server)
            resp = client.post("/api/user/login.do", json=ACCOUNT)
            body = resp.json()
            return body["code"], body["result"]["token"], body["result"]["nickname"]

        with ThreadPoolExecutor(max_workers=20) as pool:
            results = list(pool.map(login, range(20)))
        assert all(r[0] == 200 for r in results), "存在登录失败的并发请求"
        assert len({r[1] for r in results}) == 1, "并发登录 token 不一致"
        assert len({r[2] for r in results}) == 1, "并发登录昵称不一致"

    def test_concurrent_search_reads(self, mock_server):
        """并发搜索 30 线程（命中+未命中混合）：全部成功且结构完整"""
        keywords = ["毛巾", "牛奶", "饼干", "不存在的商品xyz"]

        def search(i):
            client = ApiClient(base_url=mock_server)
            resp = client.get("/api/goods/search.do", params={"keyword": keywords[i % 4]})
            body = resp.json()
            assert body["code"] == 200
            assert len(body["result"]["list"]) == body["result"]["totalCount"]
            return resp.status_code

        with ThreadPoolExecutor(max_workers=30) as pool:
            statuses = list(pool.map(search, range(30)))
        assert all(s == 200 for s in statuses)

    def test_concurrent_cart_no_lost_update(self, mock_server):
        """并发加购 20 线程：无丢失更新（最终数量 == 基线 + 20）"""
        client = ApiClient(base_url=mock_server)
        baseline = client.get("/api/cart/list.do").json()["result"]
        base_count, base_items = baseline["cartCount"], len(baseline["list"])

        def add(i):
            c = ApiClient(base_url=mock_server)
            resp = c.post("/api/cart/add.do", json={"goodsId": 9000 + i, "quantity": 1})
            return resp.json()["code"] == 200

        with ThreadPoolExecutor(max_workers=20) as pool:
            oks = list(pool.map(add, range(20)))
        assert all(oks)

        final = client.get("/api/cart/list.do").json()["result"]
        assert final["cartCount"] == base_count + 20, "并发加购存在丢失更新"
        assert len(final["list"]) == base_items + 20
        assert final["cartCount"] == sum(i["quantity"] for i in final["list"])

    def test_concurrent_cart_read_write_consistency(self, mock_server):
        """读写混合（10 写 + 10 读并发）：读者快照自洽，最终数量精确"""
        client = ApiClient(base_url=mock_server)
        base_count = client.get("/api/cart/list.do").json()["result"]["cartCount"]

        def add(_):
            c = ApiClient(base_url=mock_server)
            resp = c.post("/api/cart/add.do", json={"goodsId": 9500, "quantity": 1})
            return resp.json()["code"] == 200

        def read(_):
            c = ApiClient(base_url=mock_server)
            body = c.get("/api/cart/list.do").json()["result"]
            assert body["cartCount"] == sum(i["quantity"] for i in body["list"]), \
                "读者读到不一致快照"
            return True

        with ThreadPoolExecutor(max_workers=20) as pool:
            futures = [pool.submit(add, i) for i in range(10)]
            futures += [pool.submit(read, i) for i in range(10)]
            assert all(f.result() for f in futures)

        final = client.get("/api/cart/list.do").json()["result"]
        assert final["cartCount"] == base_count + 10

    def test_concurrent_error_stability(self, mock_server):
        """并发故障注入 15 线程：全部准确返回 500，服务不崩溃且故障后恢复"""
        def hit_error(_):
            c = ApiClient(base_url=mock_server)
            return c.get("/api/error/500.do").status_code

        with ThreadPoolExecutor(max_workers=15) as pool:
            statuses = list(pool.map(hit_error, range(15)))
        assert statuses == [500] * 15
        # 故障注入后服务仍健康
        assert ApiClient(base_url=mock_server).get("/status").json()["code"] == 200
