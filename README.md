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
| 数据模型 | `kominfo` | `ComicInfo` Pydantic 数据类（独立库） |
| 插件契约 | `hookspecs.py` | 定义 1 个插件 Hook 接口：`scrape` |
| 插件管理 | `api.py` | 插件加载、元数据读写、封面下载 |
| Web API | `routes.py` | FastAPI 路由：目录列表、元数据查询、刮削触发 |
| 命令行 | `main.py` | Typer CLI，封装 FastAPI 应用并通过 uvicorn 启动 |
| Web UI | `index.html` | 单页应用，原生 JS 实现海报网格 |

### 技术栈

- **Python 3.12+**
- **FastAPI** — Web 框架
- **Typer** — 命令行接口
- **kominfo** — ComicInfo 数据模型与 XML 序列化
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

插件只需实现一个 Hook 函数：

```python
def scrape(title: str) -> tuple[ComicInfo, str]:
    """根据标题刮削漫画信息。

    Args:
        title: 漫画标题（通常取目录名）。

    Returns:
        (ComicInfo, cover_url) 元组。
    """
```

其中 `ComicInfo` 由 [`kominfo`](https://pypi.org/project/kominfo/) 库提供，遵循标准的 ComicInfo.xml Schema，包含 `title`、`series`、`writer`、`summary`、`tags`、`genre` 等完整字段。详情请参考 kominfo 文档。

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
from komix import hookimpl
from kominfo import ComicInfo


class MySource:
    @hookimpl
    def scrape(self, title: str):
        # 实现刮削逻辑，返回 (ComicInfo, cover_url)
        info = ComicInfo()
        info.title = title
        info.writer = "作者名"
        info.summary = "简介文本"
        return info, f"https://example.com/covers/12345.jpg"
```

### 3. 安装插件

```bash
pip install komix-mysource
```

安装后启动 `komix serve`，插件即被自动发现并生效。

### 4. 插件执行流程

当用户点击「刮削所选项目」时，KoMiX 对每个选中的目录执行如下流程：

1. 以目录名作为 `title` 调用所有插件的 `scrape()`，汇总结果
2. 取第一个有效结果，解包得到 `(ComicInfo, cover_url)`
3. 将元数据写入 `ComicInfo.xml`，将封面下载为 `cover.jpg`，均存放于该目录下

### 5. 开发调试

插件开发期间推荐使用 `uv` 管理环境并安装本地插件：

```bash
cd komix-mysource
uv sync                    # 安装依赖
uv pip install -e .        # 可编辑安装
komix serve                # 启动服务，插件自动被加载
```

### 6. 更复杂的例子：异步 HTTP 调用

```python
import asyncio
import aiohttp
from komix import hookimpl
from kominfo import ComicInfo

class MySource:
    API_BASE = "https://api.example.com/v1"

    @hookimpl
    def scrape(self, title: str):
        return asyncio.run(self._async_scrape(title))

    async def _async_scrape(self, title: str):
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{self.API_BASE}/comic", params={"title": title}
            ) as resp:
                item = await resp.json()
                info = ComicInfo()
                info.title = item["title"]
                info.writer = item.get("writer", "")
                info.summary = item.get("description", "")
                info.tags = item.get("genres", "")
                cover_url = item.get("cover_url", "")
                return info, cover_url
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
