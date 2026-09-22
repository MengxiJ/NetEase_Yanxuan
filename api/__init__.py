"""
接口测试层（无接口文档场景的两条可行路径）：

1. HAR 抓包回放（api/utils/har_replay.py + api/cases/test_har_replay.py）
   Charles 抓取 App 真实流量 → 导出 HAR → 框架自动回放并比对契约
2. 本地 Mock 契约测试（api/mock_server.py + api/cases/test_mock_api.py）
   自建 Mock 后端定义接口契约，验证客户端与服务端约定一致

分层结构（与 App 自动化层解耦，共用 base 日志与 config 配置）：
├── config.py            # 接口测试配置（客户端/Mock/HAR 回放）
├── client.py            # HTTP 客户端封装（超时/重试/日志统一治理）
├── mock_server.py       # 本地 Mock 服务（标准库实现，随测试启停）
├── conftest.py          # Mock 服务 fixture（会话级）
├── utils/
│   └── har_replay.py    # HAR 解析/过滤/域名重写/回放参数构建
├── cases/               # 接口用例（pytest 入口）
└── data/captured/       # Charles 导出的 HAR 存放目录
"""
