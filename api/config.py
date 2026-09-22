# 接口测试配置（无接口文档场景：Charles 抓包回放 + 本地 Mock 契约）
import os

from config import BASE_DIR

# ============ HTTP 客户端配置 ============
API_CLIENT_CONFIG = {
    "timeout": 10,      # 单请求超时（秒）
    "max_retries": 2,   # 连接失败自动重试次数
}

# ============ Mock 服务配置 ============
MOCK_CONFIG = {
    "host": "127.0.0.1",
    "port": 0,          # 0 = 随机可用端口（避免端口冲突，随测试会话启停）
}

# ============ HAR 抓包回放配置（配合 Charles 使用） ============
# 使用流程：Charles 抓包 → File → Export Session → HAR → 存入 captured 目录
HAR_CONFIG = {
    # Charles 导出 HAR 的存放目录（支持多个 HAR 文件并存回放）
    "dir": os.path.join(BASE_DIR, "api", "data", "captured"),
    # 仅回放这些域名（空 = 全部回放）
    "include_hosts": [],
    # 排除域名（统计/埋点/推送等非被测系统流量）
    "exclude_hosts": [],
    # 排除静态资源后缀（JS/图片/字体等，非接口请求）
    "exclude_extensions": [
        ".js", ".css", ".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg",
        ".ico", ".woff", ".woff2", ".ttf", ".mp4",
    ],
    # 单次回放的最大请求数（防止 HAR 过大拖垮流水线）
    "max_entries": 50,
    # True = 状态码按 2xx/4xx/5xx 类别比对（容忍 token 过期等导致的 401↔403 漂移）
    # False = 精确比对抓包时的状态码
    "status_class_match": True,
    # 单请求响应时间阈值（毫秒）
    "response_time_ms": 5000,
    # 回放时域名重写：抓包域名 → 回放目标环境
    # "${mock_base}" 占位符 = 运行时本地 Mock 服务地址
    # 真实抓包回放示例："you.163.com": "https://test.you.163.com"
    "url_rewrite": {
        "mock.yanxuan.local": "${mock_base}",
    },
    # 回放时剔除的请求头（hop-by-hop 头 + 内容编码头，交由客户端重新生成）
    "drop_headers": [
        "host", "connection", "keep-alive", "proxy-authorization",
        "proxy-connection", "te", "trailer", "transfer-encoding",
        "upgrade", "content-length", "accept-encoding",
    ],
    # 回放时统一覆盖的请求头（例：注入有效 token 替换抓包时已过期的凭据）
    # 示例 HAR 的订单接口需登录态（mock-token-*），回放时统一注入有效凭据
    "headers_override": {"Authorization": "mock-token-replay"},
}
