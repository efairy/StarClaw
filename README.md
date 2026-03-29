<div align="center">

# StarClaw

[![GitHub Repo](https://img.shields.io/badge/GitHub-Repo-black.svg?logo=github)](https://github.com/efairy/StarClaw)
[![Python Version](https://img.shields.io/badge/python-3.10%20~%20%3C3.14-blue.svg?logo=python&label=Python)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-Apache%202.0-red.svg?logo=apache&label=License)](LICENSE)
[![Code Style](https://img.shields.io/badge/code%20style-black-black.svg?logo=python&label=CodeStyle)](https://github.com/psf/black)

[[中文](README_zh.md)] 

<p align="center"><b>Works for you, grows with you.</b></p>

</div>

Your Personal AI Assistant — deploy on your own machine, chat via multiple apps, extend with Skills.

> **Core capabilities:**
>
> **Every channel** — DingTalk, Feishu, QQ, Discord, iMessage, Telegram, WeChat, Matrix, MQTT, and more.
>
> **Under your control** — Memory, personalization, and data stay on your machine. Scheduled reminders to any channel.
>
> **Multi-Agent** — Create multiple independent agents with collaboration skills for inter-agent communication.
>
> **Skills** — Built-in cron; custom skills auto-loaded from your workspace. No lock-in.

---

## Quick Start

### Build from source

```bash
git clone https://github.com/efairy/StarClaw.git
cd StarClaw

# Build console frontend (required for web UI)
cd console && npm ci && npm run build && cd ..

# Copy console build output to package directory
mkdir -p src/starclaw/console
cp -R console/dist/. src/starclaw/console/

# Install Python package
pip install -e .

# Initialize and run
starclaw init --defaults
starclaw app
```

Then open **http://127.0.0.1:8088/** in your browser for the Console.

For development (tests, linting):

```bash
pip install -e ".[dev,full]"
pre-commit install
```

> **Note for updates:** After `git pull`, rebuild the frontend, reinstall the package (`pip install -e .`), restart `starclaw app`, and clear browser cache with `Ctrl+Shift+R` (or `Cmd+Shift+R` on macOS).

### Desktop Application (Beta)

Download the desktop app from [GitHub Releases](https://github.com/efairy/StarClaw/releases):
- **Windows**: `StarClaw-Setup-<version>.exe`
- **macOS**: `StarClaw-<version>-macOS.zip` (Apple Silicon recommended)

### Using Docker

```bash
docker compose up
```

Or manually:

```bash
docker build -t StarClaw:latest -f deploy/Dockerfile .
docker run -p 127.0.0.1:8088:8088 \
  -v starclaw-data:/app/working \
  -v starclaw-secrets:/app/working.secret \
  StarClaw:latest
```

---

## API Key

Cloud LLM providers require an API key. Configure via:

1. **Console** — Open **http://127.0.0.1:8088/** → **Settings** → **Models**. Choose a provider, enter the API Key.
2. **CLI** — Run `starclaw init` and follow the prompts.
3. **Environment variable** — Set provider keys (e.g. `DASHSCOPE_API_KEY`) in your shell or `.env` file.

> Using [local models](#local-models) only? No API key needed.

---

## Local Models

StarClaw can run LLMs entirely on your machine.

| Backend       | Best for                                 | Install extra                   |
| ------------- | ---------------------------------------- | ------------------------------- |
| **llama.cpp** | Cross-platform (macOS / Linux / Windows) | `pip install -e ".[llamacpp]"`  |
| **MLX**       | Apple Silicon Macs (M1/M2/M3/M4)        | `pip install -e ".[mlx]"`      |
| **Ollama**    | Cross-platform (requires Ollama service) | `pip install -e ".[ollama]"`   |

```bash
starclaw models download Qwen/Qwen3-4B-GGUF
starclaw models     # select the downloaded model
starclaw app        # start the server
```

---

## Documentation

Documentation is available in `website/public/docs/`. Key topics:

- **Channels** — DingTalk, Feishu, QQ, Discord, iMessage, Telegram, and more
- **Skills** — Extend and customize capabilities
- **MCP** — Model Context Protocol clients
- **Memory** — Long-term memory system
- **CLI** — Init, cron jobs, skills, clean
- **Multi-Agent** — Create multiple agents with collaboration
- **Config** — Working directory and config file

---

## Contributing

Contributions are welcome! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

```bash
# Development setup
pip install -e ".[dev,full]"
pre-commit install

# Run tests
pytest tests/unit -v
pytest tests/ -v --cov=src/starclaw
```

---

## License

StarClaw is released under the [Apache License 2.0](LICENSE).

StarClaw is a fork of [CoPaw](https://github.com/agentscope-ai/CoPaw) by the AgentScope team, independently maintained.
