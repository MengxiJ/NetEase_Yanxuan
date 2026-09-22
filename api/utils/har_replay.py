"""
HAR 抓包回放引擎（配合 Charles 抓包使用）

使用流程（无接口文档场景的接口测试路径）：
1. Charles 抓取 App 真实流量（手机代理指向 Charles；HTTPS 需信任 Charles 根证书后方可解密）
2. Charles: File → Export Session… → HAR File，导出到 api/data/captured/
3. pytest -m har 回放：框架重发每个请求并校验契约
   - 状态码比对（默认按 2xx/4xx/5xx 类别，容忍 token 过期导致的 401↔403 漂移）
   - JSON 可解析性
   - 响应顶层结构键比对（抓包存有响应正文时，检测接口结构变更）
   - 响应时间阈值
4. 生产抓包回放到测试环境：在 HAR_CONFIG.url_rewrite 配置域名重写
"""
import json
import os
from urllib.parse import urlparse

from base import logger
from api.config import HAR_CONFIG


def discover_har_files():
    """发现 captured 目录下的全部 HAR 文件（按文件名排序）"""
    har_dir = HAR_CONFIG["dir"]
    if not os.path.isdir(har_dir):
        return []
    return sorted(
        os.path.join(har_dir, name)
        for name in os.listdir(har_dir)
        if name.lower().endswith(".har")
    )


def _load_har(path):
    """读取单个 HAR 文件，返回 entries 列表"""
    with open(path, "r", encoding="utf-8-sig") as f:
        data = json.load(f)
    return data.get("log", {}).get("entries", [])


def _host_allowed(url):
    """按 include_hosts / exclude_hosts 过滤域名"""
    host = urlparse(url).netloc.lower()
    excludes = [h.lower() for h in HAR_CONFIG["exclude_hosts"]]
    includes = [h.lower() for h in HAR_CONFIG["include_hosts"]]
    if excludes and any(host == h or host.endswith("." + h) for h in excludes):
        return False
    if includes:
        return any(host == h or host.endswith("." + h) for h in includes)
    return True


def _is_static_resource(url):
    """判断是否静态资源（按 URL 路径后缀）"""
    path = urlparse(url).path.lower()
    return any(path.endswith(ext) for ext in HAR_CONFIG["exclude_extensions"])


def _expected_keys(entry):
    """提取抓包响应正文的顶层键集合（用于结构比对；未存正文时返回 None）"""
    try:
        text = entry.get("response", {}).get("content", {}).get("text") or ""
        if not text:
            return None
        data = json.loads(text)
        return set(data.keys()) if isinstance(data, dict) else None
    except (ValueError, TypeError):
        return None


def load_replay_entries():
    """加载全部 HAR 文件并过滤，生成待回放条目列表"""
    entries = []
    for path in discover_har_files():
        for raw in _load_har(path):
            request = raw.get("request", {})
            method = (request.get("method") or "").upper()
            url = request.get("url") or ""
            # 仅回放标准 HTTP(S) 请求
            if method not in ("GET", "POST", "PUT", "DELETE", "PATCH"):
                continue
            if not url.lower().startswith(("http://", "https://")):
                continue
            if not _host_allowed(url) or _is_static_resource(url):
                continue

            headers = {
                h.get("name", ""): h.get("value", "")
                for h in request.get("headers", [])
            }
            body = (request.get("postData") or {}).get("text")
            path_part = urlparse(url).path or "/"
            entries.append({
                "id": "{:03d}-{}-{}".format(len(entries) + 1, method, path_part),
                "har_file": os.path.basename(path),
                "method": method,
                "url": url,
                "headers": headers,
                "body": body,
                "expected_status": int(raw.get("response", {}).get("status") or 0),
                "expected_keys": _expected_keys(raw),
            })
            if len(entries) >= HAR_CONFIG["max_entries"]:
                logger.warning("[HAR] 条目数达到上限 {}，超出部分截断".format(HAR_CONFIG["max_entries"]))
                return entries
    logger.info("[HAR] 待回放请求 {} 条（文件数 {}）".format(
        len(entries), len(discover_har_files())))
    return entries


def rewrite_url(url, mock_base=None):
    """按 HAR_CONFIG.url_rewrite 重写域名（支持 ${mock_base} 占位符）"""
    parsed = urlparse(url)
    host = parsed.netloc.lower()
    for src, dst in HAR_CONFIG["url_rewrite"].items():
        if host == src.lower():
            dst = dst.replace("${mock_base}", mock_base or "")
            query = ("?" + parsed.query) if parsed.query else ""
            return dst.rstrip("/") + parsed.path + query
    return url


def build_request_kwargs(entry, mock_base=None):
    """将 HAR 条目转换为 ApiClient.request 可用的参数（剔除 hop-by-hop 头）"""
    drop = {h.lower() for h in HAR_CONFIG["drop_headers"]}
    headers = {k: v for k, v in entry["headers"].items() if k.lower() not in drop}
    headers.update(HAR_CONFIG["headers_override"])
    kwargs = {
        "method": entry["method"],
        "url": rewrite_url(entry["url"], mock_base),
        "headers": headers,
    }
    if entry["body"]:
        kwargs["data"] = entry["body"].encode("utf-8")
    return kwargs


def status_class(status):
    """状态码类别（2/4/5），用于类别比对"""
    return str(status)[0] if status else "0"
