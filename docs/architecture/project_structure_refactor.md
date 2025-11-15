# Hyrule Football 项目结构重构方案

## 📁 推荐的目录结构

```
hyrule_football/
├── src/
│   └── hyrule_football/
│       ├── __init__.py
│       │
│       ├── models/                      # 数据模型 ✅ 保持不变
│       │   ├── __init__.py
│       │   ├── odds.py                  # 赔率模型（合并 hyrule_odds, standard_odds）
│       │   ├── match.py                 # 比赛模型
│       │   └── betting.py               # 投注模型
│       │
│       ├── clients/                     # HTTP 客户端 ✅ 保持不变
│       │   ├── __init__.py
│       │   ├── http_client.py           # 基础 HTTP 客户端
│       │   ├── async_http_client.py     # 异步 HTTP 客户端
│       │   └── exceptions.py            # 客户端异常
│       │
│       ├── integrations/                # 第三方平台集成 ⭐ 新增
│       │   ├── __init__.py
│       │   ├── ouhe/                    # 欧赔网集成
│       │   │   ├── __init__.py
│       │   │   ├── client.py            # OuHe API 客户端
│       │   │   ├── models.py            # OuHe 数据模型
│       │   │   └── parser.py            # OuHe 数据解析
│       │   ├── bet365/                  # Bet365 集成（示例）
│       │   │   ├── __init__.py
│       │   │   └── client.py
│       │   └── william_hill/            # 威廉希尔集成（示例）
│       │       ├── __init__.py
│       │       └── client.py
│       │
│       ├── api/                         # 对外提供的 API ⭐ 重构
│       │   ├── __init__.py
│       │   ├── v1/                      # API v1 版本
│       │   │   ├── __init__.py
│       │   │   ├── routes/              # 路由定义
│       │   │   │   ├── __init__.py
│       │   │   │   ├── odds.py          # 赔率相关 API
│       │   │   │   ├── matches.py       # 比赛相关 API
│       │   │   │   └── analysis.py      # 分析相关 API
│       │   │   ├── schemas/             # API 请求/响应模型
│       │   │   │   ├── __init__.py
│       │   │   │   ├── odds.py
│       │   │   │   └── matches.py
│       │   │   └── dependencies.py      # API 依赖注入
│       │   └── app.py                   # FastAPI/Flask 应用入口
│       │
│       ├── services/                    # 业务逻辑层 ⭐ 新增
│       │   ├── __init__.py
│       │   ├── odds_service.py          # 赔率服务
│       │   ├── match_service.py         # 比赛服务
│       │   ├── analysis_service.py      # 分析服务
│       │   └── prediction_service.py    # 预测服务
│       │
│       ├── cache/                       # 缓存层 ⭐ 新增
│       │   ├── __init__.py
│       │   ├── base.py                  # 缓存基类
│       │   ├── redis_cache.py           # Redis 缓存
│       │   ├── vector/                  # 向量数据库
│       │   │   ├── __init__.py
│       │   │   ├── base.py              # 向量数据库基类
│       │   │   ├── chroma.py            # Chroma 实现
│       │   │   ├── faiss.py             # FAISS 实现
│       │   │   └── manager.py           # 向量数据库管理器
│       │   └── config.py                # 缓存配置
│       │
│       ├── agents/                      # AI Agent 工具链 ⭐ 新增
│       │   ├── __init__.py
│       │   ├── tools/                   # LangChain Tools
│       │   │   ├── __init__.py
│       │   │   ├── odds_analyzer.py     # 赔率分析工具
│       │   │   ├── match_predictor.py   # 比赛预测工具
│       │   │   └── data_retriever.py    # 数据检索工具
│       │   ├── chains/                  # LangChain Chains
│       │   │   ├── __init__.py
│       │   │   ├── analysis_chain.py    # 分析链
│       │   │   └── prediction_chain.py  # 预测链
│       │   └── prompts/                 # Prompt 模板
│       │       ├── __init__.py
│       │       └── templates.py
│       │
│       ├── utils/                       # 通用工具函数 ⭐ 重构
│       │   ├── __init__.py
│       │   ├── parsers/                 # 解析器
│       │   │   ├── __init__.py
│       │   │   ├── handicap.py          # 盘口解析（aisa_handicap_parser）
│       │   │   ├── markdown.py          # Markdown 解析
│       │   │   └── html.py              # HTML 解析
│       │   ├── converters/              # 转换器
│       │   │   ├── __init__.py
│       │   │   ├── odds.py              # 赔率转换
│       │   │   └── chinese_num.py       # 中文数字转换
│       │   ├── validators/              # 验证器
│       │   │   ├── __init__.py
│       │   │   └── odds.py              # 赔率验证
│       │   └── helpers.py               # 其他辅助函数
│       │
│       ├── core/                        # 核心引擎 ⭐ 新增
│       │   ├── __init__.py
│       │   ├── odds_engine.py           # 赔率引擎（重构现有 odds_engine）
│       │   ├── analysis_engine.py       # 分析引擎
│       │   └── config.py                # 核心配置
│       │
│       └── main.py                      # 主程序入口
│
├── config/                              # 配置文件 ⭐ 新增
│   ├── __init__.py
│   ├── settings.py                      # 全局配置
│   ├── api_config.py                    # API 配置
│   ├── cache_config.py                  # 缓存配置
│   └── logging_config.py                # 日志配置
│
├── data/                                # 数据目录 ✅ 保持不变
│   ├── raw/                             # 原始数据
│   ├── processed/                       # 处理后的数据
│   └── vectordb/                        # 向量数据库持久化
│       ├── chroma/                      # Chroma 数据
│       ├── faiss/                       # FAISS 索引
│       └── metadata/                    # 元数据
│
├── docs/                                # 文档 ✅ 保持不变
│   ├── odds/                            # 赔率文档
│   ├── api/                             # API 文档
│   └── architecture/                    # 架构文档
│
├── tests/                               # 测试 ✅ 保持不变
│   ├── __init__.py
│   ├── unit/                            # 单元测试
│   │   ├── test_models/
│   │   ├── test_services/
│   │   └── test_utils/
│   ├── integration/                     # 集成测试
│   │   ├── test_api/
│   │   └── test_integrations/
│   └── fixtures/                        # 测试数据
│
├── notebooks/                           # Jupyter 笔记本 ✅ 保持不变
│   ├── odds.ipynb
│   └── ouhe.ipynb
│
├── examples/                            # 示例代码 ✅ 保持不变
│   ├── http_client_usage.py
│   └── agent_usage.py
│
├── logs/                                # 日志目录 ✅ 保持不变
│
├── .env                                 # 环境变量
├── .gitignore
├── pyproject.toml
└── README.md
```

## 🔑 关键变更说明

### 1️⃣ **`integrations/` - 第三方平台集成**
- **用途**：存放所有调用第三方平台的 API 客户端
- **原因**：与 `api/`（对外提供的 API）明确区分
- **迁移**：
  - `src/hyrule_football/api/ouhe_api.py` → `src/hyrule_football/integrations/ouhe/client.py`

### 2️⃣ **`api/` - 对外提供的 API**
- **用途**：提供给客户端/Web 的 RESTful API
- **结构**：采用版本化设计（v1, v2...）
- **技术栈**：推荐 FastAPI

### 3️⃣ **`agents/` - AI Agent 工具链**
- **用途**：存放 LangChain 相关的 Tools、Chains、Prompts
- **与 `utils/` 区分**：
  - `agents/tools/` - LangChain 工具（用于 Agent）
  - `utils/` - 通用开发工具函数

### 4️⃣ **`cache/` - 缓存层**
- **用途**：统一管理所有缓存（Redis、Chroma、FAISS）
- **结构**：
  - `cache/redis_cache.py` - Redis 缓存
  - `cache/vector/` - 向量数据库（Chroma、FAISS）

### 5️⃣ **`services/` - 业务逻辑层**
- **用途**：封装业务逻辑，供 API 和 Agent 调用
- **好处**：解耦业务逻辑和接口层

### 6️⃣ **`utils/` - 通用工具函数**
- **重构**：按功能分类（parsers、converters、validators）
- **迁移**：
  - `odds/aisa_handicap_parser.py` → `utils/parsers/handicap.py`

### 7️⃣ **`core/` - 核心引擎**
- **用途**：核心业务引擎（赔率引擎、分析引擎）
- **迁移**：
  - `odds/odds_engine.py` → `core/odds_engine.py`

### 8️⃣ **`config/` - 配置管理**
- **用途**：集中管理所有配置
- **好处**：环境变量、API 配置、缓存配置统一管理

---

## 📊 文件迁移对照表

| 当前位置 | 新位置 | 说明 |
|---------|--------|------|
| `src/hyrule_football/api/ouhe_api.py` | `src/hyrule_football/integrations/ouhe/client.py` | 第三方 API 客户端 |
| `src/hyrule_football/odds/aisa_handicap_parser.py` | `src/hyrule_football/utils/parsers/handicap.py` | 盘口解析工具 |
| `src/hyrule_football/odds/odds_engine.py` | `src/hyrule_football/core/odds_engine.py` | 赔率引擎 |
| `src/hyrule_football/odds/standard_odds.py` | `src/hyrule_football/models/odds.py` | 赔率模型（合并） |
| `src/hyrule_football/odds/hyrule_odds.py` | `src/hyrule_football/models/odds.py` | 赔率模型（合并） |
| `src/hyrule_football/odds/ouhe_odds.py` | `src/hyrule_football/integrations/ouhe/models.py` | OuHe 数据模型 |
| `src/hyrule_football/clients/` | `src/hyrule_football/clients/` | ✅ 保持不变 |
| `src/hyrule_football/tools/` | `src/hyrule_football/utils/` 或 `agents/tools/` | 根据用途分类 |

---

## 🔄 详细迁移步骤

### 步骤 1：创建新目录结构

```bash
# 创建新目录
mkdir -p src/hyrule_football/integrations/ouhe
mkdir -p src/hyrule_football/api/v1/{routes,schemas}
mkdir -p src/hyrule_football/services
mkdir -p src/hyrule_football/cache/vector
mkdir -p src/hyrule_football/agents/{tools,chains,prompts}
mkdir -p src/hyrule_football/utils/{parsers,converters,validators}
mkdir -p src/hyrule_football/core
mkdir -p config
mkdir -p tests/{unit,integration,fixtures}
```

### 步骤 2：迁移第三方集成

**迁移 `ouhe_api.py`：**

```bash
# 移动文件
mv src/hyrule_football/api/ouhe_api.py \
   src/hyrule_football/integrations/ouhe/client.py
```

**重构为标准客户端：**
- 继承 `HTTPClient`
- 封装为 `OuHeClient` 类
- 添加类型注解和文档

### 步骤 3：重构 `odds/` 目录

**合并赔率模型：**
```bash
# 将 standard_odds.py 和 hyrule_odds.py 合并到 models/odds.py
# 保留核心模型，移除重复代码
```

**迁移工具函数：**
```bash
# 盘口解析器
mv src/hyrule_football/odds/aisa_handicap_parser.py \
   src/hyrule_football/utils/parsers/handicap.py

# 赔率引擎
mv src/hyrule_football/odds/odds_engine.py \
   src/hyrule_football/core/odds_engine.py
```

### 步骤 4：创建缓存层

**创建缓存基类和实现：**
- `cache/base.py` - 缓存接口
- `cache/redis_cache.py` - Redis 实现
- `cache/vector/chroma.py` - Chroma 实现
- `cache/vector/faiss.py` - FAISS 实现

### 步骤 5：创建 API 层（未来）

**使用 FastAPI 创建 RESTful API：**
- `api/v1/routes/odds.py` - 赔率 API
- `api/v1/routes/matches.py` - 比赛 API
- `api/app.py` - FastAPI 应用

### 步骤 6：创建 Agent 工具链

**迁移 LangChain 相关代码：**
- 从 notebooks 提取 RAG 相关代码
- 创建 LangChain Tools
- 创建 Chains 和 Prompts

### 步骤 7：创建配置管理

**集中管理配置：**
- `config/settings.py` - 全局配置
- `config/cache_config.py` - 缓存配置
- `.env` - 环境变量

---

## 🎯 优先级建议

### 🔴 **高优先级（立即执行）**

1. ✅ **创建 `integrations/ouhe/`**
   - 迁移 `ouhe_api.py`
   - 重构为标准客户端

2. ✅ **创建 `utils/parsers/`**
   - 迁移 `aisa_handicap_parser.py`
   - 添加其他解析器

3. ✅ **创建 `cache/`**
   - 实现 Redis 缓存
   - 实现向量数据库管理器

4. ✅ **创建 `config/`**
   - 集中管理配置
   - 环境变量管理

### 🟡 **中优先级（近期执行）**

5. ⚠️ **重构 `models/`**
   - 合并 `standard_odds.py` 和 `hyrule_odds.py`
   - 统一赔率模型

6. ⚠️ **创建 `services/`**
   - 封装业务逻辑
   - 解耦 API 和业务

7. ⚠️ **创建 `core/`**
   - 迁移 `odds_engine.py`
   - 创建核心引擎

### 🟢 **低优先级（未来执行）**

8. 💡 **创建 `api/v1/`**
   - 设计 RESTful API
   - 实现 FastAPI 应用

9. 💡 **创建 `agents/`**
   - 提取 LangChain 代码
   - 创建 Agent 工具链

---

## 📝 代码示例

### 示例 1：重构后的 OuHe 客户端

```python
# src/hyrule_football/integrations/ouhe/client.py
from hyrule_football.clients import HTTPClient
from .models import OuHeAsiaOdds, OuHeMatchList
from typing import List

class OuHeClient(HTTPClient):
    """欧赔网 API 客户端"""

    def __init__(self):
        super().__init__(
            base_url="http://ouhe.aiball365.com",
            timeout=10,
            max_retries=0,
        )

    def get_hot_matches(self) -> List[str]:
        """获取热门比赛列表"""
        # 实现逻辑...
        pass

    def get_asia_odds(self, match_id: str, company_id: str) -> OuHeAsiaOdds:
        """获取亚盘赔率"""
        # 实现逻辑...
        pass
```

### 示例 2：缓存管理器

```python
# src/hyrule_football/cache/vector/manager.py
from typing import Optional, List
from .chroma import ChromaVectorStore
from .faiss import FAISSVectorStore

class VectorStoreManager:
    """向量数据库管理器"""

    def __init__(self, store_type: str = "faiss"):
        self.store_type = store_type
        self._store = None

    def get_store(self):
        """获取向量存储实例"""
        if self._store is None:
            if self.store_type == "chroma":
                self._store = ChromaVectorStore()
            elif self.store_type == "faiss":
                self._store = FAISSVectorStore()
        return self._store

    def search(self, query: str, k: int = 5) -> List[dict]:
        """搜索相似文档"""
        return self.get_store().search(query, k)
```

### 示例 3：配置管理

```python
# config/settings.py
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    """全局配置"""

    # 应用配置
    APP_NAME: str = "Hyrule Football"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = False

    # API 配置
    API_V1_PREFIX: str = "/api/v1"

    # 缓存配置
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0

    # 向量数据库配置
    VECTOR_STORE_TYPE: str = "faiss"  # faiss, chroma
    VECTOR_STORE_PATH: str = "data/vectordb"

    # 第三方 API
    OUHE_BASE_URL: str = "http://ouhe.aiball365.com"

    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
```

---

## ✅ 重构后的优势

### 1. **清晰的职责分离**
- ✅ 第三方集成 (`integrations/`) vs 对外 API (`api/`)
- ✅ 开发工具 (`utils/`) vs AI 工具 (`agents/tools/`)
- ✅ 数据模型 (`models/`) vs 业务逻辑 (`services/`)

### 2. **更好的可维护性**
- ✅ 模块化设计，易于测试
- ✅ 配置集中管理
- ✅ 缓存统一管理

### 3. **更强的扩展性**
- ✅ 支持多版本 API（v1, v2...）
- ✅ 支持多种缓存后端
- ✅ 支持多个第三方平台集成

### 4. **符合最佳实践**
- ✅ 分层架构（Models → Services → API）
- ✅ 依赖注入
- ✅ 配置与代码分离

---

## 🚀 下一步行动

1. **立即执行**：创建 `integrations/ouhe/` 并迁移 `ouhe_api.py`
2. **本周完成**：创建 `cache/` 和 `config/`
3. **下周完成**：重构 `models/` 和创建 `services/`
4. **未来规划**：实现 `api/v1/` 和 `agents/`

需要我帮你开始执行重构吗？我可以：
- 创建新的目录结构
- 迁移和重构现有代码
- 创建示例代码

