"""
HTTP 接口客户端封装（企业级规范：超时 / 重试 / 日志统一治理）

所有接口用例统一通过 ApiClient 发送请求（用例中禁止直接 import requests），
便于统一控制超时、重试与请求日志，后续可无缝扩展签名、鉴权注入。
"""
import time

import requests

from base import logger
from api.config import API_CLIENT_CONFIG


class ApiClient:
    """轻量 HTTP 客户端（基于 requests.Session，连接失败自动重试）"""

    def __init__(self, base_url=None, timeout=None, max_retries=None):
        self.base_url = (base_url or "").rstrip("/")
        self.timeout = timeout if timeout is not None else API_CLIENT_CONFIG["timeout"]
        self.max_retries = (
            max_retries if max_retries is not None else API_CLIENT_CONFIG["max_retries"]
        )
        self.session = requests.Session()

    def request(self, method, url, params=None, json=None, data=None, headers=None):
        """发送 HTTP 请求：相对路径自动拼接 base_url，连接异常自动重试"""
        if self.base_url and not url.lower().startswith(("http://", "https://")):
            url = "{}/{}".format(self.base_url, url.lstrip("/"))

        last_exc = None
        for attempt in range(1, self.max_retries + 2):
            start = time.time()
            try:
                resp = self.session.request(
                    method=method, url=url, params=params,
                    json=json, data=data, headers=headers, timeout=self.timeout,
                )
                elapsed = int((time.time() - start) * 1000)
                logger.info("[API] {} {} -> {} ({}ms)".format(method, url, resp.status_code, elapsed))
                return resp
            except (requests.ConnectionError, requests.Timeout) as exc:
                last_exc = exc
                logger.warning("[API] {} {} 第{}次请求失败: {}".format(method, url, attempt, exc))

        logger.error("[API] {} {} 重试{}次后仍失败".format(method, url, self.max_retries))
        raise last_exc

    def get(self, url, params=None, **kwargs):
        """GET 请求"""
        return self.request("GET", url, params=params, **kwargs)

    def post(self, url, json=None, **kwargs):
        """POST 请求"""
        return self.request("POST", url, json=json, **kwargs)
