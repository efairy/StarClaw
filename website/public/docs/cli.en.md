# CLI

`starclaw` is the command-line tool for StarClaw. This page is organized from
"get-up-and-running" to "advanced management" — read from top to bottom if
you're new, or jump to the section you need.

> Not sure what "channels", "heartbeat", or "cron" mean? See
> [Introduction](./intro) first.

---

## Getting started

These are the commands you'll use on day one.

### starclaw init

First-time setup. Walks you through configuration interactively.

```bash
starclaw init              # Interactive setup (recommended for first time)
starclaw init --defaults   # Non-interactive, use all defaults (good for scripts)
starclaw init --force      # Overwrite existing config files
```

**What the interactive flow covers (in order):**

1. **Heartbeat** — interval (e.g. `30m`), target (`main` / `last`), optional
   active hours.
2. **Show tool details** — whether tool call details appear in channel messages.
3. **Language** — `zh` / `en` / `ru` for agent persona files (SOUL.md, etc.).
4. **Channels** — optionally configure iMessage / Discord / DingTalk / Feishu /
   QQ / Console.
5. **LLM provider** — select provider, enter API key, choose model (**required**).
6. **Skills** — enable all / none / custom selection.
7. **Environment variables** — optionally add key-value pairs for tools.
8. **HEARTBEAT.md** — edit the heartbeat checklist in your default editor.

### starclaw app

Start the StarClaw server. Everything else — channels, cron jobs, the Console
UI — depends on this.

```bash
starclaw app                             # Start on 127.0.0.1:8088
starclaw app --host 0.0.0.0 --port 9090 # Custom address
starclaw app --reload                    # Auto-reload on code change (dev)
starclaw app --log-level debug           # Verbose logging
```

| Option        | Default     | Description                                                   |
| ------------- | ----------- | ------------------------------------------------------------- |
| `--host`      | `127.0.0.1` | Bind host                                                     |
| `--port`      | `8088`      | Bind port                                                     |
| `--reload`    | off         | Auto-reload on file changes (dev only)                        |
| `--log-level` | `info`      | `critical` / `error` / `warning` / `info` / `debug` / `trace` |
| `--workers`   | —           | **[DEPRECATED]** Ignored. StarClaw always uses 1 worker          |

> **Note:** The `--workers` option is deprecated for stability reasons. StarClaw is designed to run with a single worker process. Multi-worker mode can cause issues with in-memory state management and WebSocket connections. This option will be removed in a future version.

### Console

Once `starclaw app` is running, open `http://127.0.0.1:8088/` in your browser to
access the **Console** — a web UI for chat, channels, cron, skills, models,
and more. See [Console](./console) for a full walkthrough.

If the frontend was not built, the root URL returns a JSON message like `{"message": "StarClaw Web Console is not available."}` but the API still works.

**To build the frontend:** in the project's `console/` directory run
`npm ci && npm run build`, then copy the output to the package directory:
`mkdir -p src/starclaw/console && cp -R console/dist/. src/starclaw/console/`.
Docker images and pip packages already include the Console.

### starclaw daemon

Inspect status, version, and recent logs without starting a conversation. Same
behavior as sending `/daemon status` etc. in chat (CLI can show local info when
the app is not running).

| Command                      | Description                                                                               |
| ---------------------------- | ----------------------------------------------------------------------------------------- |
| `starclaw daemon status`        | Status (config, working dir, memory manager)                                              |
| `starclaw daemon restart`       | Print instructions (in-chat /daemon restart does in-process reload)                       |
| `starclaw daemon reload-config` | Re-read and validate config (channel/MCP changes need /daemon restart or process restart) |
| `starclaw daemon version`       | Version and paths                                                                         |
| `starclaw daemon logs [-n N]`   | Last N lines of log (default 100; from `starclaw.log` in working dir)                        |

**Multi-Agent Support:** All commands support the `--agent-id` parameter (defaults to `default`).

```bash
starclaw daemon status                     # Default agent status
starclaw daemon status --agent-id abc123   # Specific agent status
starclaw daemon version
starclaw daemon logs -n 50
```

---

## Models & environment variables

Before using StarClaw you need at least one LLM provider configured. Environment
variables power many built-in tools (e.g. web search).

### starclaw models

Manage LLM providers and the active model.

| Command                                | What it does                                         |
| -------------------------------------- | ---------------------------------------------------- |
| `starclaw models list`                    | Show all providers, API key status, and active model |
| `starclaw models config`                  | Full interactive setup: API keys → active model      |
| `starclaw models config-key [provider]`   | Configure a single provider's API key                |
| `starclaw models set-llm`                 | Switch the active model (API keys unchanged)         |
| `starclaw models download <repo_id>`      | Download a local model (llama.cpp / MLX)             |
| `starclaw models local`                   | List downloaded local models                         |
| `starclaw models remove-local <model_id>` | Delete a downloaded local model                      |
| `starclaw models ollama-pull <model>`     | Download an Ollama model                             |
| `starclaw models ollama-list`             | List Ollama models                                   |
| `starclaw models ollama-remove <model>`   | Delete an Ollama model                               |

```bash
starclaw models list                    # See what's configured
starclaw models config                  # Full interactive setup
starclaw models config-key modelscope   # Just set ModelScope's API key
starclaw models config-key dashscope    # Just set DashScope's API key
starclaw models config-key custom       # Set custom provider (Base URL + key)
starclaw models set-llm                 # Change active model only
```

#### Local models

StarClaw can also run models locally via llama.cpp or MLX — no API key needed.
Install the backend first: `pip install 'starclaw[llamacpp]'` or
`pip install 'starclaw[mlx]'`.

```bash
# Download a model (auto-selects Q4_K_M GGUF)
starclaw models download Qwen/Qwen3-4B-GGUF

# Download an MLX model
starclaw models download Qwen/Qwen3-4B --backend mlx

# Download from ModelScope
starclaw models download Qwen/Qwen2-0.5B-Instruct-GGUF --source modelscope

# List downloaded models
starclaw models local
starclaw models local --backend mlx

# Delete a downloaded model
starclaw models remove-local <model_id>
starclaw models remove-local <model_id> --yes   # skip confirmation
```

| Option      | Short | Default       | Description                                                           |
| ----------- | ----- | ------------- | --------------------------------------------------------------------- |
| `--backend` | `-b`  | `llamacpp`    | Target backend (`llamacpp` or `mlx`)                                  |
| `--source`  | `-s`  | `huggingface` | Download source (`huggingface` or `modelscope`)                       |
| `--file`    | `-f`  | _(auto)_      | Specific filename. If omitted, auto-selects (prefers Q4_K_M for GGUF) |

#### Ollama models

StarClaw integrates with Ollama to run models locally. Models are dynamically loaded from your Ollama daemon — install Ollama first from [ollama.com](https://ollama.com).

Install the Ollama SDK: `pip install 'starclaw[ollama]'` (or re-run the installer with `--extras ollama`)

```bash
# Download an Ollama model
starclaw models ollama-pull mistral:7b
starclaw models ollama-pull qwen3:8b

# List Ollama models
starclaw models ollama-list

# Remove an Ollama model
starclaw models ollama-remove mistral:7b
starclaw models ollama-remove qwen3:8b --yes   # skip confirmation

# Use in config flow (auto-detects Ollama models)
starclaw models config           # Select Ollama → Choose from model list
starclaw models set-llm          # Switch to a different Ollama model
```

**Key differences from local models:**

- Models come from Ollama daemon (not downloaded by StarClaw)
- Use `ollama-pull` / `ollama-remove` instead of `download` / `remove-local`
- Model list updates dynamically when you add/remove via Ollama CLI or StarClaw

> **Note:** You are responsible for ensuring the API key is valid. StarClaw does
> not verify key correctness. See [Config — LLM Providers](./config#llm-providers).

### starclaw env

Manage environment variables used by tools and skills at runtime.

| Command                   | What it does                  |
| ------------------------- | ----------------------------- |
| `starclaw env list`          | List all configured variables |
| `starclaw env set KEY VALUE` | Set or update a variable      |
| `starclaw env delete KEY`    | Delete a variable             |

```bash
starclaw env list
starclaw env set TAVILY_API_KEY "tvly-xxxxxxxx"
starclaw env set GITHUB_TOKEN "ghp_xxxxxxxx"
starclaw env delete TAVILY_API_KEY
```

> **Note:** StarClaw only stores and loads these values; you are responsible for
> ensuring they are correct. See
> [Config — Environment Variables](./config#environment-variables).

---

## Channels

Connect StarClaw to messaging platforms.

### starclaw channels

Manage channel configuration (iMessage, Discord, DingTalk, Feishu, QQ,
Console, etc.) and send messages to channels. **Note:** Use `config` for interactive setup (no `configure`
subcommand); use `remove` to uninstall custom channels (no `uninstall`).

**Alias:** You can use `starclaw channel` (singular) as a shorthand for `starclaw channels`.

| Command                        | What it does                                                                                                      |
| ------------------------------ | ----------------------------------------------------------------------------------------------------------------- |
| `starclaw channels list`          | Show all channels and their status (secrets masked)                                                               |
| `starclaw channels send`          | Send a one-way message to a user/session via a channel (requires all 5 parameters)                                |
| `starclaw channels install <key>` | Install a channel into `custom_channels/`: create stub or use `--path`/`--url`                                    |
| `starclaw channels add <key>`     | Install and add to config; built-in channels only get config entry; supports `--path`/`--url`                     |
| `starclaw channels remove <key>`  | Remove a custom channel from `custom_channels/` (built-ins cannot be removed); `--keep-config` keeps config entry |
| `starclaw channels config`        | Interactively enable/disable channels and fill in credentials                                                     |

**Multi-Agent Support:** All commands support the `--agent-id` parameter (defaults to `default`).

```bash
starclaw channels list                    # See default agent's channels
starclaw channels list --agent-id abc123  # See specific agent's channels
starclaw channels install my_channel      # Create custom channel stub
starclaw channels install my_channel --path ./my_channel.py
starclaw channels add dingtalk            # Add DingTalk to config
starclaw channels remove my_channel       # Remove custom channel (and from config by default)
starclaw channels remove my_channel --keep-config   # Remove module only, keep config entry
starclaw channels config                  # Configure default agent
starclaw channels config --agent-id abc123 # Configure specific agent
```

The interactive `config` flow lets you pick a channel, enable/disable it, and enter credentials. It loops until you choose "Save and exit".

| Channel      | Fields to fill in                                                                    |
| ------------ | ------------------------------------------------------------------------------------ |
| **iMessage** | Bot prefix, database path, poll interval                                             |
| **Discord**  | Bot prefix, Bot Token, HTTP proxy, proxy auth                                        |
| **DingTalk** | Bot prefix, Client ID, Client Secret, Message Type, Card Template ID/Key, Robot Code |
| **Feishu**   | Bot prefix, App ID, App Secret                                                       |
| **QQ**       | Bot prefix, App ID, Client Secret                                                    |
| **Console**  | Bot prefix                                                                           |

> For platform-specific credential setup, see [Channels](./channels).

#### Sending messages to channels (Proactive Notifications)

> Corresponding skill: **Channel Message**

Use `starclaw channels send` to proactively push messages to users/sessions via any configured channel. This is a **one-way send** — no response expected.

When agents have the **channel_message** skill enabled, they can automatically use this command to send proactive notifications when needed.

**Typical use cases:**

- Notify user after task completion
- Scheduled reminders, alerts, status updates
- Push async processing results back to original session
- User explicitly requested "notify me when done"

```bash
# Step 1: Query available sessions
starclaw chats list --agent-id my_bot --channel feishu

# Step 2: Send message using queried parameters
starclaw channels send \
  --agent-id my_bot \
  --channel feishu \
  --target-user ou_xxxx \
  --target-session session_id_xxxx \
  --text "Task completed!"
```

**Required parameters (all 5):**

- `--agent-id`: Sending agent ID
- `--channel`: Target channel (console/dingtalk/feishu/discord/imessage/qq)
- `--target-user`: User ID (get from `starclaw chats list`)
- `--target-session`: Session ID (get from `starclaw chats list`)
- `--text`: Message content

**Important:**

- Always query sessions with `starclaw chats list` first — do NOT guess `target-user` or `target-session`
- If multiple sessions exist, prefer the most recently updated one
- This is for proactive notifications only; for agent-to-agent communication, use `starclaw agents chat` (see "Agents" section below)

**Key differences from `starclaw agents chat`:**

- `starclaw channels send`: Agent-to-user/channel, one-way, no response
- `starclaw agents chat`: Agent-to-agent, bidirectional, with response

---

## Agents

Manage agents and enable inter-agent communication.

### starclaw agents

> Corresponding skill: **Multi-Agent Collaboration**

When agents have the **multi_agent_collaboration** skill enabled, they can automatically use `starclaw agents chat` to collaborate with other agents as needed.

**Alias:** You can use `starclaw agent` (singular) as a shorthand for `starclaw agents`.

| Command             | What it does                                                                 |
| ------------------- | ---------------------------------------------------------------------------- |
| `starclaw agents list` | List all configured agents with their IDs, names, descriptions, workspaces   |
| `starclaw agents chat` | Communicate with another agent (bidirectional, supports multi-turn dialogue) |

```bash
# List all agents
starclaw agents list
starclaw agent list  # Same with singular alias

# Chat with another agent (real-time mode, one-shot)
starclaw agents chat \
  --agent-id my_bot \
  --to-agent helper_bot \
  --text "Please analyze this data"

# Multi-turn conversation (session reuse)
starclaw agents chat \
  --agent-id my_bot \
  --to-agent helper_bot \
  --session-id collab_session_001 \
  --text "Follow-up question"

# Complex task (background mode)
starclaw agents chat --background \
  --agent-id my_bot \
  --to-agent data_analyst \
  --text "Analyze /data/logs/2026-03-26.log and generate detailed report"
# Returns [TASK_ID: xxx] [SESSION: xxx]

# Check background task status (--to-agent is optional when querying)
starclaw agents chat --background \
  --task-id <task_id>
# Status flow: submitted → pending → running → finished
# When finished, result shows: completed (✅) or failed (❌)

# Stream mode (incremental response, real-time mode only)
starclaw agents chat \
  --agent-id my_bot \
  --to-agent helper_bot \
  --text "Long analysis task" \
  --mode stream
```

**Required parameters (real-time mode):**

- `--from-agent` (alias: `--agent-id`): Your agent ID (sender)
- `--to-agent`: Target agent ID (recipient)
- `--text`: Message content

**Background task parameters (new):**

- `--background`: Background task mode
- `--task-id`: Check background task status (use with `--background`)

**Optional parameters:**

- `--session-id`: Session ID for multi-turn conversations (auto-generated if omitted)
- `--mode`: Response mode — `final` (default, complete response) or `stream` (incremental)
  - **Note**: `--background` and `--mode stream` are mutually exclusive
- `--base-url`: Override API base URL
- `--timeout`: Timeout in seconds (default: 300)
- `--json-output`: Output full JSON instead of text

**Background mode explanation:**

When tasks are complex (e.g., data analysis, batch processing, report generation), use `--background` to avoid blocking the current agent. After submission, it returns a `task_id` that can be used later to query the task status and result.

**Use cases for background mode**:

- Data analysis and statistics
- Batch file processing
- Generating detailed reports
- Calling slow external APIs
- Complex tasks with uncertain execution time

**Task Status Flow**:

- `submitted`: Task accepted, waiting to start
- `pending`: Queued for execution
- `running`: Currently executing
- `finished`: Completed (result shows `completed` for success or `failed` for error)

**Note:** You can use either `--from-agent` or `--agent-id` — they are equivalent. When checking task status, only `--task-id` is required (`--to-agent` is optional).

**Key differences from `starclaw channels send`:**

- `starclaw agents chat`: Agent-to-agent, bidirectional, returns response
- `starclaw channels send`: Agent-to-user/channel, one-way, no response

---

## Cron (scheduled tasks)

Create jobs that run on a timed schedule — "every day at 9am", "every 2 hours
ask StarClaw and send the reply". **Requires `starclaw app` to be running.**

### starclaw cron

| Command                      | What it does                                  |
| ---------------------------- | --------------------------------------------- |
| `starclaw cron list`            | List all jobs                                 |
| `starclaw cron get <job_id>`    | Show a job's spec                             |
| `starclaw cron state <job_id>`  | Show runtime state (next run, last run, etc.) |
| `starclaw cron create ...`      | Create a job                                  |
| `starclaw cron delete <job_id>` | Delete a job                                  |
| `starclaw cron pause <job_id>`  | Pause a job                                   |
| `starclaw cron resume <job_id>` | Resume a paused job                           |
| `starclaw cron run <job_id>`    | Run once immediately                          |

**Multi-Agent Support:** All commands support the `--agent-id` parameter (defaults to `default`).

### Creating jobs

**Option 1 — CLI arguments (simple jobs)**

Two task types:

- **text** — send a fixed message to a channel on schedule.
- **agent** — ask StarClaw a question on schedule and deliver the reply.

```bash
# Text: send "Good morning!" to DingTalk every day at 9:00 (default agent)
starclaw cron create \
  --type text \
  --name "Daily 9am" \
  --cron "0 9 * * *" \
  --channel dingtalk \
  --target-user "your_user_id" \
  --target-session "session_id" \
  --text "Good morning!"

# Agent: create task for specific agent
starclaw cron create \
  --agent-id abc123 \
  --type agent \
  --name "Check todos" \
  --cron "0 */2 * * *" \
  --channel dingtalk \
  --target-user "your_user_id" \
  --target-session "session_id" \
  --text "What are my todo items?"
```

Required: `--type`, `--name`, `--cron`, `--channel`, `--target-user`,
`--target-session`, `--text`.

**Option 2 — JSON file (complex or batch)**

```bash
starclaw cron create -f job_spec.json
```

JSON structure matches the output of `starclaw cron get <job_id>`.

### Additional options

| Option                       | Default       | Description                                                              |
| ---------------------------- | ------------- | ------------------------------------------------------------------------ |
| `--timezone`                 | user timezone | Timezone for the cron schedule (defaults to `user_timezone` from config) |
| `--enabled` / `--no-enabled` | enabled       | Create enabled or disabled                                               |
| `--mode`                     | `final`       | `stream` (incremental) or `final` (complete response)                    |
| `--base-url`                 | auto          | Override the API base URL                                                |

### Cron expression cheat sheet

Five fields: **minute hour day month weekday** (no seconds).

| Expression     | Meaning                   |
| -------------- | ------------------------- |
| `0 9 * * *`    | Every day at 9:00         |
| `0 */2 * * *`  | Every 2 hours on the hour |
| `30 8 * * 1-5` | Weekdays at 8:30          |
| `0 0 * * 0`    | Sunday at midnight        |
| `*/15 * * * *` | Every 15 minutes          |

---

## Chats (sessions)

Manage chat sessions via the API. **Requires `starclaw app` to be running.**

### starclaw chats

**Alias:** You can use `starclaw chat` (singular) as a shorthand for `starclaw chats`.

| Command                                | What it does                                                  |
| -------------------------------------- | ------------------------------------------------------------- |
| `starclaw chats list`                     | List all sessions (supports `--user-id`, `--channel` filters) |
| `starclaw chats get <id>`                 | View a session's details and message history                  |
| `starclaw chats create ...`               | Create a new session                                          |
| `starclaw chats update <id> --name "..."` | Rename a session                                              |
| `starclaw chats delete <id>`              | Delete a session                                              |

**Multi-Agent Support:** All commands support the `--agent-id` parameter (defaults to `default`).

```bash
starclaw chats list                        # Default agent's chats
starclaw chats list --agent-id abc123      # Specific agent's chats
starclaw chats list --user-id alice --channel dingtalk
starclaw chats get 823845fe-dd13-43c2-ab8b-d05870602fd8
starclaw chats create --session-id "discord:alice" --user-id alice --name "My Chat"
starclaw chats create --agent-id abc123 -f chat.json
starclaw chats update <chat_id> --name "Renamed"
starclaw chats delete <chat_id>
```

---

## Skills

Extend StarClaw's capabilities with skills (PDF reading, web search, etc.).

### starclaw skills

| Command               | What it does                                      |
| --------------------- | ------------------------------------------------- |
| `starclaw skills list`   | Show all skills and their enabled/disabled status |
| `starclaw skills config` | Interactively enable/disable skills (checkbox UI) |

**Multi-Agent Support:** All commands support the `--agent-id` parameter (defaults to `default`).

```bash
starclaw skills list                   # See default agent's skills
starclaw skills list --agent-id abc123 # See specific agent's skills
starclaw skills config                 # Configure default agent
starclaw skills config --agent-id abc123 # Configure specific agent
```

In the interactive UI: ↑/↓ to navigate, Space to toggle, Enter to confirm.
A preview of changes is shown before applying.

> For built-in skill details and custom skill authoring, see [Skills](./skills).

---

## Maintenance

### starclaw clean

Remove everything under the working directory (default `~/.starclaw`).

```bash
starclaw clean             # Interactive confirmation
starclaw clean --yes       # No confirmation
starclaw clean --dry-run   # Only list what would be removed
```

---

## Global options

Every `starclaw` subcommand inherits:

| Option          | Default     | Description                                    |
| --------------- | ----------- | ---------------------------------------------- |
| `--host`        | `127.0.0.1` | API host (auto-detected from last `starclaw app`) |
| `--port`        | `8088`      | API port (auto-detected from last `starclaw app`) |
| `-h` / `--help` |             | Show help message                              |

If the server runs on a non-default address, pass these globally:

```bash
starclaw --host 0.0.0.0 --port 9090 cron list
```

## Working directory

All config and data live in `~/.starclaw` by default:

- **Global config**: `config.json` (providers, environment variables, agent list)
- **Agent workspaces**: `workspaces/{agent_id}/` (each agent's independent config and data)

```
~/.starclaw/
├── config.json              # Global config
└── workspaces/
    ├── default/             # Default agent workspace
    │   ├── agent.json       # Agent config
    │   ├── chats.json       # Conversation history
    │   ├── jobs.json        # Cron jobs
    │   ├── AGENTS.md        # Persona files
    │   └── memory/          # Memory files
    └── abc123/              # Other agent workspace
        └── ...
```

| Variable            | Description                         |
| ------------------- | ----------------------------------- |
| `STARCLAW_WORKING_DIR` | Override the working directory path |
| `STARCLAW_CONFIG_FILE` | Override the config file path       |

See [Config & Working Directory](./config) and [Multi-Agent](./multi-agent) for full details.

---

## Command overview

| Command          | Subcommands                                                                                                                            | Requires server? |
| ---------------- | -------------------------------------------------------------------------------------------------------------------------------------- | :--------------: |
| `starclaw init`     | —                                                                                                                                      |        No        |
| `starclaw app`      | —                                                                                                                                      |  — (starts it)   |
| `starclaw models`   | `list` · `config` · `config-key` · `set-llm` · `download` · `local` · `remove-local` · `ollama-pull` · `ollama-list` · `ollama-remove` |        No        |
| `starclaw env`      | `list` · `set` · `delete`                                                                                                              |        No        |
| `starclaw channels` | `list` · `send` · `install` · `add` · `remove` · `config`                                                                              |     **Yes**      |
| `starclaw agents`   | `list` · `chat`                                                                                                                        |     **Yes**      |
| `starclaw cron`     | `list` · `get` · `state` · `create` · `delete` · `pause` · `resume` · `run`                                                            |     **Yes**      |
| `starclaw chats`    | `list` · `get` · `create` · `update` · `delete`                                                                                        |     **Yes**      |
| `starclaw skills`   | `list` · `config`                                                                                                                      |        No        |
| `starclaw clean`    | —                                                                                                                                      |        No        |

---

## Related pages

- [Introduction](./intro) — What StarClaw can do
- [Console](./console) — Web-based management UI
- [Channels](./channels) — DingTalk, Feishu, iMessage, Discord, QQ setup
- [Heartbeat](./heartbeat) — Scheduled check-in / digest
- [Skills](./skills) — Built-in and custom skills
- [Config & Working Directory](./config) — Working directory and config.json
- [Multi-Agent](./multi-agent) — Multi-agent setup, management, and collaboration
