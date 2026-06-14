# KoMiX — Lightweight Comic Book Manager

KoMiX 是一个轻量级本地漫画库管理工具，面向 ACGN 爱好者。它提供 Web UI 浏览本地漫画目录，并通过**插件系统**从网络数据源自动获取漫画元数据和封面图。

## 特性

- **目录即漫画** — 将一个目录下的每个子目录视为一本漫画，自动发现并展示为海报墙
- **元数据刮削** — 通过插件自动搜索并下载漫画信息（标题、作者、简介、标签）和封面图
- **ComicInfo.xml** — 元数据以标准 `ComicInfo.xml` 格式写入漫画目录，兼容其他漫画管理工具
- **插件驱动** — 基于 `pluggy` 的插件系统，数据源完全由外部插件提供，可任意扩展
- **单文件 Web UI** — 纯 HTML/JS 前端，无框架依赖，内置封面海报网格、全选/批量刮削等交互
- **快速启动** — Typer CLI + FastAPI 后端，一条命令启动服务

## 快速开始

### 安装

```bash
pip install komix
```

### 启动服务

```bash
komix serve # 默认 http://127.0.0.1:7788
komix serve --host 0.0.0.0 --port 8080
```

### 使用

1. 浏览器打开 `http://127.0.0.1:7788`
2. 输入漫画库根目录路径（例如 `/mnt/comics`）
3. 选择需要刮削的漫画目录
4. 点击「刮削所选项目」按钮，等待插件获取元数据和封面

> 首次使用需要安装至少一个数据源插件，否则刮削不会产生任何效果。参见下方插件开发指南。

---

## 技术架构

| 模块 | 文件 | 职责 |
|------|------|------|
| 数据模型 | `comicinfo.py` | `ComicInfo` Pydantic 数据类 |
| 插件契约 | `hookspecs.py` | 定义 3 个插件 Hook 接口 |
| 插件管理 | `api.py` | 插件加载、元数据读写、封面下载 |
| Web API | `routes.py` | FastAPI 路由：目录列表、元数据查询、刮削触发 |
| 命令行 | `main.py` | Typer CLI，封装 FastAPI 应用并通过 uvicorn 启动 |
| Web UI | `index.html` | 单页应用，原生 JS 实现海报网格 |

### 技术栈

- **Python 3.12+**
- **FastAPI** — Web 框架
- **Typer** — 命令行接口
- **pluggy** — 插件系统
- **Pydantic** — 数据校验与序列化
- **aiohttp / aiofiles** — 异步 HTTP 和文件 I/O
- **uvicorn** — ASGI 服务器
- **hatchling** — 构建系统

### API 端点

| 方法 | 路径 | 说明 |
|------|------|------|
| `GET` | `/` | 返回 Web UI 页面 |
| `GET` | `/api/comics?rootdir=<path>` | 列出根目录下所有子目录 |
| `GET` | `/api/comicinfo?dirpath=<path>` | 读取目录中的 `ComicInfo.xml` |
| `GET` | `/api/cover?dirpath=<path>` | 返回目录中的 `cover.jpg` |
| `PUT` | `/api/scrape?dirpath=<path>` | 对指定目录触发插件刮削流程 |

---

## 插件开发指南

KoMiX 使用 `pluggy` 作为插件框架，插件以 Python 包形式发布，通过 setuptools entry point 注册。

### 1. 插件接口说明

插件需要实现以下 3 个 Hook 函数：

```python
def search(query: str) -> list[ComicInfo]:
    """根据搜索关键词（通常是目录名）搜索漫画，返回匹配列表。"""

def fetch_comicinfo(comic_id: str) -> ComicInfo:
    """根据漫画 ID 获取完整元数据。"""

def fetch_cover_url(comic_id: str) -> str:
    """根据漫画 ID 获取封面图片 URL。"""
```

其中 `ComicInfo` 的数据结构为：

```python
@dataclass
class ComicInfo:
    title: str = ""
    id: str = ""
    author: str = ""
    summary: str = ""
    tags: list[str] = field(default_factory=list)
```

### 2. 快速开始：编写一个插件

创建项目结构：

```
komix-mysource/
├── pyproject.toml
└── src/
    └── komix_mysource/
        ├── __init__.py
        └── plugin.py
```

**pyproject.toml**：

```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "komix-mysource"
version = "0.1.0"
requires-python = ">=3.12"
dependencies = [
    "komix",
    "aiohttp",
]

[project.entry-points.komix]
mysource = "komix_mysource.plugin:MySource"

[tool.hatch.build.targets.wheel]
packages = ["src/komix_mysource"]
```

**src/komix_mysource/plugin.py**：

```python
import aiohttp
from komix import hookimpl
from komix.comicinfo import ComicInfo


class MySource:
    @hookimpl
    def search(self, query: str):
        # 实现搜索逻辑，返回 ComicInfo 列表
        return [ComicInfo(
            title=query,
            id="12345",
            author="作者名",
            summary="简介文本",
            tags=["标签1", "标签2"],
        )]

    @hookimpl
    def fetch_comicinfo(self, comic_id: str):
        # 根据 ID 获取完整元数据
        return ComicInfo(
            title="漫画标题",
            id=comic_id,
            author="作者名",
            summary="详细简介...",
            tags=["标签1", "标签2"],
        )

    @hookimpl
    def fetch_cover_url(self, comic_id: str):
        # 返回封面图片的 URL
        return f"https://example.com/covers/{comic_id}.jpg"
```

### 3. 安装插件

```bash
pip install komix-mysource
```

安装后启动 `komix serve`，插件即被自动发现并生效。

### 4. 插件执行流程

当用户点击「刮削所选项目」时，KoMiX 对每个选中的目录执行如下流程：

1. 以目录名作为 `query` 调用所有插件的 `search()`，汇总搜索结果
2. 取第一个搜索结果，以 `comic_id` 调用 `fetch_comicinfo()` 获取元数据
3. 以 `comic_id` 调用 `fetch_cover_url()` 获取封面 URL
4. 将元数据写入 `ComicInfo.xml`，将封面下载为 `cover.jpg`，均存放于该目录下

### 5. 开发调试

插件开发期间推荐使用 `uv` 管理环境并安装本地插件：

```bash
cd komix-mysource
uv sync                    # 安装依赖
uv pip install -e .        # 可编辑安装
komix serve                # 启动服务，插件自动被加载
```

### 6. 更复杂的例子：异步 HTTP 调用

如果你的插件需要调用远程 API，推荐使用 `aiohttp` 保持异步（但请注意：`pluggy` 的 hook 调用是同步的，如果你的实现本身是同步的，可以直接用 `requests` 等同步库）：

```python
import aiohttp
from komix import hookimpl
from komix.comicinfo import ComicInfo

class MySource:
    API_BASE = "https://api.example.com/v1"

    @hookimpl
    def search(self, query: str):
        # 注意：hook 是同步调用的，但你可以内部使用 asyncio
        import asyncio
        return asyncio.run(self._async_search(query))

    async def _async_search(self, query: str):
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.API_BASE}/search", params={"q": query}) as resp:
                data = await resp.json()
                return [
                    ComicInfo(
                        id=item["id"],
                        title=item["title"],
                        author=item.get("author", ""),
                        summary=item.get("description", ""),
                        tags=item.get("genres", []),
                    )
                    for item in data["results"]
                ]
```

### 7. 发布插件到 PyPI

1. 在 `pyproject.toml` 中完善项目元信息
2. 使用 `hatch build` 构建发行版
3. 使用 `twine upload dist/*` 发布到 PyPI

发布后用户通过 `pip install komix-mysource` 即可使用。

---

## 开发

```bash
git clone https://github.com/kongolou/komix.git
cd komix
uv sync                    # 安装依赖（含开发依赖）
uv run komix serve         # 启动开发服务器
ruff check                 # 代码检查
ruff format                # 代码格式化
```

## License

MIT
