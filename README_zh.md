<div align="center">

# StarClaw

[![GitHub Repo](https://img.shields.io/badge/GitHub-Repo-black.svg?logo=github)](https://github.com/efairy/StarClaw)
[![Python Version](https://img.shields.io/badge/python-3.10%20~%20%3C3.14-blue.svg?logo=python&label=Python)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-Apache%202.0-red.svg?logo=apache&label=License)](LICENSE)
[![Code Style](https://img.shields.io/badge/code%20style-black-black.svg?logo=python&label=CodeStyle)](https://github.com/psf/black)

[[English](README.md)] 

<p align="center"><b>懂你所需，伴你左右。</b></p>

</div>

你的 AI 个人助理 — 部署在自己的机器上，通过多种聊天应用对话，通过 Skills 扩展能力。

> **核心能力：**
>
> **全域触达** — 钉钉、飞书、QQ、Discord、iMessage、Telegram、微信、Matrix、MQTT 等频道。
>
> **由你掌控** — 记忆、个性化和数据留在你的机器上。定时提醒可发往任意频道。
>
> **多智能体** — 创建多个独立智能体，启用协作技能实现智能体间通信。
>
> **Skills 扩展** — 内置定时任务；自定义技能自动加载，无绑定。

---

## 快速开始

### 从源码构建

```bash
git clone https://github.com/efairy/StarClaw.git
cd StarClaw

# 构建控制台前端（Web UI 必需）
cd console && npm ci && npm run build && cd ..

# 复制构建产物到包目录
mkdir -p src/starclaw/console
cp -R console/dist/. src/starclaw/console/

# 安装 Python 包
pip install -e .

# 初始化并运行
starclaw init --defaults
starclaw app
```

浏览器打开 **http://127.0.0.1:8088/** 即可使用控制台。

开发环境（测试、代码检查）：

```bash
pip install -e ".[dev,full]"
pre-commit install
```

> **更新提示：** `git pull` 后需重新构建前端、重装包 (`pip install -e .`)、重启 `starclaw app`，并清除浏览器缓存。

### 桌面应用（Beta）

从 [GitHub Releases](https://github.com/efairy/StarClaw/releases) 下载：
- **Windows**: `StarClaw-Setup-<version>.exe`
- **macOS**: `StarClaw-<version>-macOS.zip`（推荐 Apple Silicon）

### 使用 Docker

```bash
docker compose up
```

或手动构建：

```bash
docker build -t StarClaw:latest -f deploy/Dockerfile .
docker run -p 127.0.0.1:8088:8088 \
  -v starclaw-data:/app/working \
  -v starclaw-secrets:/app/working.secret \
  StarClaw:latest
```

---

## API Key

使用云端 LLM 需要配置 API Key：

1. **控制台** — 打开 **http://127.0.0.1:8088/** → **设置** → **模型**，选择供应商并输入 API Key。
2. **CLI** — 运行 `starclaw init`，按提示配置。
3. **环境变量** — 在 shell 或 `.env` 文件中设置供应商密钥（如 `DASHSCOPE_API_KEY`）。

> 仅使用[本地模型](#本地模型)？无需 API Key。

---

## 本地模型

StarClaw 支持完全本地运行 LLM。

| 后端          | 适用场景                                 | 安装方式                        |
| ------------- | ---------------------------------------- | ------------------------------- |
| **llama.cpp** | 跨平台（macOS / Linux / Windows）        | `pip install -e ".[llamacpp]"`  |
| **MLX**       | Apple Silicon Mac（M1/M2/M3/M4）         | `pip install -e ".[mlx]"`      |
| **Ollama**    | 跨平台（需 Ollama 服务）                 | `pip install -e ".[ollama]"`   |

```bash
starclaw models download Qwen/Qwen3-4B-GGUF
starclaw models     # 选择已下载的模型
starclaw app        # 启动服务
```

---

## 文档

文档位于 `website/public/docs/`。主要内容：

- **频道** — 钉钉、飞书、QQ、Discord、iMessage、Telegram 等
- **Skills** — 扩展和自定义能力
- **MCP** — Model Context Protocol 客户端
- **记忆** — 长期记忆系统
- **CLI** — 初始化、定时任务、技能、清理
- **多智能体** — 创建多个智能体并启用协作
- **配置** — 工作目录和配置文件

---

## 参与贡献

欢迎贡献！请阅读 [CONTRIBUTING_zh.md](CONTRIBUTING_zh.md) 了解指南。

```bash
# 开发环境
pip install -e ".[dev,full]"
pre-commit install

# 运行测试
pytest tests/unit -v
pytest tests/ -v --cov=src/starclaw
```

---

## 许可证

StarClaw 基于 [Apache License 2.0](LICENSE) 发布。

StarClaw 是 [CoPaw](https://github.com/agentscope-ai/CoPaw)（AgentScope 团队）的 fork，独立维护。
