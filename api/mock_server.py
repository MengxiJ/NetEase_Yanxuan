"""
本地 Mock 服务（无接口文档场景的契约测试后端）

- 基于标准库 http.server 实现，零额外依赖，随测试会话启停（随机端口）
- 模拟网易严选风格接口契约：业务码与 HTTP 状态分离（HTTP 200 + code 字段）
- 覆盖核心业务域：登录 / 搜索 / 购物车 / 订单 / 健康检查
- 支持故障注入（500）与延迟注入（性能阈值演练），用于验证客户端容错
"""
import json
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs

from base import logger

SERVICE_VERSION = "yanxuan-mock/1.0.0"
# 请求体大小上限（安全规范：拒绝超大报文，1MB）
MAX_BODY_BYTES = 1024 * 1024
# 有效 token 前缀（登录颁发；HAR 回放通过 headers_override 注入 replay token）
TOKEN_PREFIX = "mock-token-"

# 模拟严选账号（与 App 自动化层 config.ACCOUNT 保持一致）
DEFAULT_ACCOUNT = {"username": "17658097530", "password": "Aa123456"}
# 可命中的搜索关键词（与 App 搜索工作流的参数化关键词一致）
HIT_KEYWORDS = ["毛巾", "牛奶", "饼干"]

# 购物车状态（线程安全，随服务生命周期存在）
_lock = threading.Lock()
_cart_state = {"count": 0, "items": []}

# 优惠券状态（线程安全，限量库存 + 已领取集合）
_coupon_state = {"stock": 5, "received": set()}


def _ok(result=None, message="ok"):
    """成功响应体（业务码 200）"""
    payload = {"code": 200, "message": message}
    if result is not None:
        payload["result"] = result
    return payload


def _err(code, message):
    """失败响应体（HTTP 状态可为 200，业务码表达失败）"""
    return {"code": code, "message": message}


def _handle_status(params, body, headers):
    """健康检查"""
    return 200, _ok({"service": "yanxuan-mock", "version": SERVICE_VERSION})


def _handle_login(params, body, headers):
    """登录：校验账号密码，返回昵称与 token"""
    body = body or {}
    username = body.get("username")
    password = body.get("password")
    if not username or not password:
        return 200, _err(400, "参数缺失: username/password")
    if username == DEFAULT_ACCOUNT["username"] and password == DEFAULT_ACCOUNT["password"]:
        return 200, _ok({
            "userId": 10086,
            "nickname": "严选测试用户",
            "token": "mock-token-" + username[-4:],
        })
    return 200, _err(401, "用户名或密码错误")


def _handle_search(params, body, headers):
    """商品搜索：命中关键词返回商品列表，否则返回空列表"""
    keyword = (params.get("keyword") or [""])[0]
    if keyword in HIT_KEYWORDS:
        goods = [
            {"id": i + 1, "name": "{} 第{}款".format(keyword, i + 1), "price": 19.9 + i}
            for i in range(3)
        ]
    else:
        goods = []
    return 200, _ok({"keyword": keyword, "totalCount": len(goods), "list": goods})


def _handle_cart_add(params, body, headers):
    """加入购物车：累计数量与明细（有状态接口）"""
    body = body or {}
    goods_id = body.get("goodsId")
    quantity = body.get("quantity", 1)
    if not goods_id:
        return 200, _err(400, "参数缺失: goodsId")
    with _lock:
        _cart_state["count"] += quantity
        _cart_state["items"].append({"goodsId": goods_id, "quantity": quantity})
        count = _cart_state["count"]
    return 200, _ok({"cartCount": count})


def _handle_cart_list(params, body, headers):
    """购物车列表查询"""
    with _lock:
        return 200, _ok({"cartCount": _cart_state["count"], "list": list(_cart_state["items"])})


def _handle_order_list(params, body, headers):
    """订单列表：需登录态（Authorization: mock-token-xxx），支持按状态筛选"""
    auth = headers.get("Authorization") or ""
    if not auth.startswith(TOKEN_PREFIX):
        return 200, _err(401, "未授权访问：缺少或无效的 token")
    orders = [
        {"orderNo": "2026092100001", "status": 1, "statusText": "待付款", "amount": 59.70},
        {"orderNo": "2026092000002", "status": 2, "statusText": "待发货", "amount": 129.00},
    ]
    status_filter = (params.get("status") or [""])[0]
    if status_filter:
        orders = [o for o in orders if str(o["status"]) == status_filter]
    return 200, _ok({"total": len(orders), "list": orders})


def _handle_error_500(params, body, headers):
    """故障注入：始终返回 HTTP 500"""
    return 500, _err(500, "mock 注入的服务端错误")


def _handle_delay(params, body, headers):
    """延迟注入：延迟 ms 毫秒后返回（上限 3 秒）"""
    ms = min(int((params.get("ms") or ["300"])[0]), 3000)
    time.sleep(ms / 1000)
    return 200, _ok({"delayMs": ms})


def _handle_goods_detail(params, body, headers):
    """商品详情：按 goodsId 返回完整字段，id 1-3 存在，其余返回业务码 404"""
    raw_id = (params.get("goodsId") or [""])[0]
    if not raw_id:
        return 200, _err(400, "参数缺失: goodsId")
    try:
        gid = int(raw_id)
    except ValueError:
        return 200, _err(400, "参数非法: goodsId 必须为数字")
    if 1 <= gid <= 3:
        return 200, _ok({
            "id": gid,
            "name": "商品详情 {}".format(gid),
            "price": 19.9 + gid,
            "stock": 100,
            "sales": 1000,
            "images": ["https://img.mock/goods/{}/1.jpg".format(gid)],
        })
    return 200, _err(404, "商品不存在")


def _handle_user_profile(params, body, headers):
    """用户信息：需登录态（Authorization: mock-token-xxx）"""
    auth = headers.get("Authorization") or ""
    if not auth.startswith(TOKEN_PREFIX):
        return 200, _err(401, "未授权访问：缺少或无效的 token")
    return 200, _ok({"userId": 10086, "nickname": "严选测试用户", "vip": True, "points": 999})


def _handle_coupon_receive(params, body, headers):
    """优惠券领取：有状态，限量库存，同一用户不可重复领取"""
    body = body or {}
    user_id = body.get("userId")
    coupon_id = body.get("couponId")
    if user_id is None or coupon_id is None:
        return 200, _err(400, "参数缺失: userId/couponId")
    key = (str(user_id), str(coupon_id))
    with _lock:
        if key in _coupon_state["received"]:
            return 200, _err(409, "已领取过该优惠券")
        if _coupon_state["stock"] <= 0:
            return 200, _err(410, "优惠券已抢光")
        _coupon_state["stock"] -= 1
        _coupon_state["received"].add(key)
        return 200, _ok({"couponId": coupon_id, "stockLeft": _coupon_state["stock"]})


def _handle_cart_update(params, body, headers):
    """购物车更新：delta 必须为正整数，否则业务码 422"""
    body = body or {}
    goods_id = body.get("goodsId")
    delta = body.get("delta")
    if goods_id is None or delta is None:
        return 200, _err(400, "参数缺失: goodsId/delta")
    if not isinstance(delta, int) or isinstance(delta, bool) or delta <= 0:
        return 200, _err(422, "数量必须为正整数")
    with _lock:
        _cart_state["count"] += delta
        _cart_state["items"].append({"goodsId": goods_id, "quantity": delta})
        count = _cart_state["count"]
    return 200, _ok({"cartCount": count})


# 路由表：(HTTP 方法, 路径) -> 处理函数(params, body, headers) -> (HTTP 状态, 响应体)
ROUTES = {
    ("GET", "/status"): _handle_status,
    ("POST", "/api/user/login.do"): _handle_login,
    ("GET", "/api/goods/search.do"): _handle_search,
    ("POST", "/api/cart/add.do"): _handle_cart_add,
    ("GET", "/api/cart/list.do"): _handle_cart_list,
    ("GET", "/api/order/list.do"): _handle_order_list,
    ("GET", "/api/goods/detail.do"): _handle_goods_detail,
    ("GET", "/api/user/profile.do"): _handle_user_profile,
    ("POST", "/api/coupon/receive.do"): _handle_coupon_receive,
    ("POST", "/api/cart/update.do"): _handle_cart_update,
    ("GET", "/api/error/500.do"): _handle_error_500,
    ("GET", "/api/delay.do"): _handle_delay,
}


class _MockHandler(BaseHTTPRequestHandler):
    """Mock 请求处理器：路由分发 + JSON 编解码 + 统一异常兜底"""

    server_version = SERVICE_VERSION

    def log_message(self, fmt, *args):
        """收敛 BaseHTTPRequestHandler 默认的 stderr 输出"""
        logger.debug("[Mock] {} {}".format(self.address_string(), fmt % args))

    def do_GET(self):
        self._dispatch("GET")

    def do_POST(self):
        self._dispatch("POST")

    def do_PUT(self):
        self._reject_method()

    def do_DELETE(self):
        self._reject_method()

    def do_PATCH(self):
        self._reject_method()

    def do_OPTIONS(self):
        self._reject_method()

    def _reject_method(self):
        """不支持的请求方法统一 405（业务 JSON 响应，而非协议层 501）"""
        self._write_json(405, _err(405, "不支持的请求方法"))

    def _dispatch(self, method):
        parsed = urlparse(self.path)
        length = int(self.headers.get("Content-Length") or 0)
        if length > MAX_BODY_BYTES:
            # 安全规范：超大请求体先排空再拒绝（413），避免连接悬挂
            self._drain_body(length)
            self._write_json(413, _err(413, "请求体过大: {} bytes".format(length)))
            return
        route = ROUTES.get((method, parsed.path))
        if route is None:
            status, payload = 404, _err(404, "接口不存在: {}".format(parsed.path))
        else:
            body = self._read_json_body()
            try:
                status, payload = route(parse_qs(parsed.query), body, self.headers)
            except Exception as exc:  # mock 自身异常兜底，保证服务不崩
                status, payload = 500, _err(500, "mock 处理异常: {}".format(exc))
        self._write_json(status, payload)

    def _drain_body(self, length):
        """分块排空超大请求体，保证连接状态一致"""
        remaining = length
        while remaining > 0:
            chunk = self.rfile.read(min(65536, remaining))
            if not chunk:
                break
            remaining -= len(chunk)

    def _read_json_body(self):
        """读取并解析 JSON 请求体（非 JSON 或空体返回 None）"""
        length = int(self.headers.get("Content-Length") or 0)
        if not length:
            return None
        raw = self.rfile.read(length)
        if not raw:
            return None
        try:
            return json.loads(raw.decode("utf-8"))
        except (ValueError, UnicodeDecodeError):
            return None

    def _write_json(self, status, payload):
        """统一 JSON 响应输出"""
        data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.send_header("X-Mock-Server", SERVICE_VERSION)
        # 安全响应头（防止 MIME 嗅探）
        self.send_header("X-Content-Type-Options", "nosniff")
        self.end_headers()
        self.wfile.write(data)


def start_mock_server(host="127.0.0.1", port=0):
    """启动 Mock 服务（后台线程），返回 (server, base_url)"""
    server = ThreadingHTTPServer((host, port), _MockHandler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    base_url = "http://{}:{}".format(host, server.server_address[1])
    logger.info("[Mock] 服务已启动: {} (路由数={})".format(base_url, len(ROUTES)))
    return server, base_url


def stop_mock_server(server):
    """停止 Mock 服务"""
    server.shutdown()
    server.server_close()
    logger.info("[Mock] 服务已停止")
