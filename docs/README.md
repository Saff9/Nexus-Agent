# ⚡ Nexus Agent - Complete Documentation

## Table of Contents

1. [Introduction](#introduction)
2. [Installation](#installation)
3. [Quick Start](#quick-start)
4. [Configuration](#configuration)
5. [CLI Usage](#cli-usage)
6. [Gateway (Messaging)](#gateway-messaging)
7. [Tools](#tools)
8. [Skills System](#skills-system)
9. [Memory System](#memory-system)
10. [Cron Scheduler](#cron-scheduler)
11. [MCP Integration](#mcp-integration)
12. [Building & Packaging](#building--packaging)
13. [API Reference](#api-reference)
14. [Troubleshooting](#troubleshooting)

---

## Introduction

**Nexus Agent** is a self-improving AI agent that runs everywhere - Linux, Windows, macOS, Android, and Termux. Built in Python with under 3,000 lines of core code.

### Features

- 🤖 **Multi-Provider LLM** - OpenAI, Anthropic, Ollama, OpenRouter (200+ models)
- 🛠️ **40+ Tools** - File ops, browser automation, web search, MCP, terminal
- 💬 **Messaging Gateway** - Telegram, Discord, Slack, WhatsApp bots
- 🧠 **Memory System** - Persistent knowledge across sessions
- 📚 **Skills** - Procedural memory, self-improving capabilities
- ⏰ **Cron Scheduler** - Automated tasks with natural language
- 📱 **Cross-Platform** - .exe (Windows), .apk (Android), native (Linux)
- 🔌 **MCP Support** - Connect to external tool servers

### Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Entry Points                          │
│  CLI (cli.py) │ Gateway │ Mobile App │ Python Library   │
└─────────┬─────────────┬──────────────┬──────────────────┘
          │             │              │
          ▼             ▼              ▼
┌─────────────────────────────────────────────────────────┐
│                  NexusAgent Core                         │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐   │
│  │ Provider │ │  Tools   │ │  Memory  │ │ Sessions │   │
│  │ Registry │ │ Registry │ │ Manager  │ │  Store   │   │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘   │
└─────────────────────────────────────────────────────────┘
          │             │              │
          ▼             ▼              ▼
┌─────────────────────────────────────────────────────────┐
│                  External Services                       │
│  LLM APIs │ MCP Servers │ Browser │ Terminal │ Files   │
└─────────────────────────────────────────────────────────┘
```

---

## Installation

### Linux/macOS/Termux

```bash
curl -fsSL https://raw.githubusercontent.com/yourusername/nexus-agent/main/install.sh | bash
```

### Windows (PowerShell)

```powershell
irm https://raw.githubusercontent.com/yourusername/nexus-agent/main/install.ps1 | iex
```

### From Source

```bash
git clone https://github.com/yourusername/nexus-agent.git
cd nexus-agent
pip install -e ".[cli,gateway]"
```

### Android (Termux)

```bash
pkg install python rust
pip install nexus-agent
nexus
```

---

## Quick Start

### 1. Set API Key

```bash
export OPENROUTER_API_KEY='sk-or-...'  # Recommended: 200+ models
# OR
export OPENAI_API_KEY='sk-...'
export ANTHROPIC_API_KEY='sk-ant-...'
```

### 2. Start CLI

```bash
nexus
```

### 3. Chat

```
❯ Hello! What can you do?

⚡ I'm Nexus Agent, your self-improving AI assistant. I can:
- Help with coding and debugging
- Search the web for information
- Automate files and terminal tasks
- Browse websites
- And much more!

What would you like to work on?
```

---

## Configuration

### Config File

Location: `~/.nexus/config.json`

```json
{
  "provider": "openrouter",
  "model": "google/gemini-2.0-flash-001",
  "max_iterations": 50,
  "temperature": 0.7,
  "max_tokens": 4096,
  "workspace": "~/nexus-workspace",
  "data_dir": "~/.nexus",
  "log_level": "INFO"
}
```

### Environment Variables

| Variable | Description |
|----------|-------------|
| `OPENAI_API_KEY` | OpenAI API key |
| `ANTHROPIC_API_KEY` | Anthropic API key |
| `OPENROUTER_API_KEY` | OpenRouter API key (recommended) |
| `NEXUS_INSTALL_DIR` | Custom install directory |
| `HERMES_HOME` | Legacy compatibility |

---

## CLI Usage

### Commands

| Command | Description |
|---------|-------------|
| `/help` | Show all commands |
| `/status` | Agent status |
| `/model <name>` | Change model |
| `/new` | New session |
| `/clear` | Clear screen |
| `/config` | Show config |
| `/tools` | List tools |
| `/skills` | List skills |
| `/memory` | Memory summary |
| `/quit` | Exit |

### Examples

```bash
# Change model
/model anthropic:claude-sonnet-4-20250514

# View status
/status

# New conversation
/new
```

---

## Gateway (Messaging)

### Telegram

```bash
# Get token from @BotFather
nexus gateway telegram --token YOUR_BOT_TOKEN
```

### Discord

```bash
# Create bot at https://discord.com/developers
nexus gateway discord --token YOUR_BOT_TOKEN
```

### Slack

```bash
# Create app at https://api.slack.com
nexus gateway slack --token YOUR_BOT_TOKEN
```

### Configuration

```yaml
# ~/.nexus/gateway.yaml
telegram:
  token: "BOT_TOKEN"
  allowed_users:
    - 123456789

discord:
  token: "BOT_TOKEN"
  allowed_channels:
    - 987654321
```

---

## Tools

### File Operations

- `read_file(path)` - Read file
- `write_file(path, content)` - Write file
- `search_files(pattern, path)` - Find files
- `list_directory(path)` - List folder

### Terminal

- `run_command(command, timeout)` - Execute shell command

### Web

- `web_search(query)` - Search web
- `web_fetch(url)` - Fetch URL content

### Browser (Playwright)

- `browser_navigate(url)` - Go to URL
- `browser_screenshot(path)` - Take screenshot
- `browser_click(selector)` - Click element
- `browser_fill(selector, value)` - Fill input
- `browser_content()` - Get page text
- `browser_evaluate(javascript)` - Run JS

### MCP

- `mcp_connect_server(name, command, args)` - Connect MCP server
- `mcp_call_tool(tool_name, arguments)` - Call MCP tool
- `mcp_list_tools()` - List MCP tools

### System

- `get_env(name)` - Get environment variable

---

## Skills System

### What are Skills?

Skills are procedural memory modules that teach the agent specific capabilities.

### Structure

```
skills/my-skill/
├── SKILL.md          # Metadata
├── handler.py        # Logic (optional)
└── examples/         # Examples (optional)
```

### SKILL.md Format

```markdown
# Skill Name

<description>
What this skill does.
</description>

Triggers on: "keyword1", "keyword2"

## Capabilities

- What it can do
- More capabilities

## Usage

Examples of how to use.
```

### Built-in Skills

- `github-helper` - GitHub operations
- `code-review` - Code analysis
- `web-research` - Deep web research
- `file-organizer` - File management

### Creating Skills

1. Create directory: `skills/my-skill/`
2. Add `SKILL.md` with metadata
3. (Optional) Add `handler.py` with logic
4. Skill auto-loads on restart

---

## Memory System

### Components

1. **MEMORY.md** - Long-term learnings
2. **USER.md** - User profile
3. **observations.json** - Recent interactions

### API

```python
from core import MemoryManager

memory = MemoryManager(Path("~/.nexus"))

# Add observation
memory.add_observation({
    "input": "User asked about Python",
    "response_summary": "Explained list comprehensions"
})

# Add learning
memory.add_learning("User prefers TypeScript over Python")

# Build context for prompts
context = memory.build_context()
```

### Search

```python
# Search observations
results = memory.search_observations("Python", limit=10)
```

---

## Cron Scheduler

### Create Scheduled Job

```python
from cron import CronScheduler

scheduler = CronScheduler(
    data_dir=Path("~/.nexus"),
    agent_factory=lambda: NexusAgent(config),
    delivery_callback=lambda target, msg: print(msg)
)

# Add daily job
scheduler.add_job(
    name="Daily Summary",
    schedule="@daily",
    prompt="Summarize today's news and stock prices",
    skills=["web-research"],
    output_target="telegram"
)

scheduler.start()
```

### Schedules

- `@hourly` - Every hour
- `@daily` - Every day at midnight
- `@weekly` - Every week
- `@monthly` - Every month
- `0 9 * * *` - Cron format (9 AM daily)

### Management

```bash
nexus cron list
nexus cron add --name "Backup" --schedule "@daily" --prompt "Backup my files"
nexus cron remove job_1
nexus cron disable job_2
```

---

## MCP Integration

### What is MCP?

Model Context Protocol (MCP) allows connecting to external tool servers.

### Connect Server

```python
from tools.mcp import get_mcp_client

client = get_mcp_client()
await client.connect_server("filesystem", "npx", ["-y", "@modelcontextprotocol/server-filesystem"])
```

### Call Tool

```python
result = await client.call_tool("read_file", {"path": "/etc/hosts"})
```

### Available Servers

- `filesystem` - File operations
- `git` - Git operations
- `postgres` - Database queries
- `slack` - Slack integration
- Custom servers via stdio

---

## Building & Packaging

### Build All

```bash
python build.py
```

### Build Specific Platform

```bash
python build.py --platform windows   # .exe
python build.py --platform linux     # binary
python build.py --platform macos     # .app
python build.py --platform android   # .apk
python build.py --pip               # pip package
```

### Requirements

- **Windows**: PyInstaller
- **Android**: Buildozer, JDK 11, Android SDK
- **pip**: build, twine

### Distribution

```bash
# Windows .exe
dist/nexus.exe

# Linux binary
dist/nexus

# Android APK
bin/NexusAgent-0.1.0-debug.apk

# pip package
pip install dist/nexus_agent-0.1.0-py3-none-any.whl
```

---

## API Reference

### NexusAgent

```python
from core import NexusAgent, Config

config = Config.load()
agent = NexusAgent(config)

# Run conversation
response = agent.run_conversation("Hello!")

# Get status
status = agent.get_status()

# Interrupt
agent.interrupt()
agent.reset_interrupt()
```

### Config

```python
from core import Config

config = Config.load()
config.get("model")
config.set("model", "openai:gpt-4o")
config.save()
```

### Session

```python
from core import Session, SessionStore

store = SessionStore(Path("~/.nexus/sessions.db"))
session = store.get_or_create()
session.add_message("user", "Hello")
session.add_message("assistant", "Hi!")
store.save(session)
```

---

## Troubleshooting

### "Module not found"

```bash
pip install -e ".[cli,gateway]"
```

### "API key not set"

```bash
export OPENROUTER_API_KEY='your-key'
```

### Android build fails

```bash
# Install dependencies
sudo apt install python3-pip python3-venv libffi-dev libssl-dev openjdk-11-jdk
pip install buildozer
buildozer android debug
```

### Browser tools not working

```bash
pip install playwright
playwright install chromium
```

### MCP not connecting

```bash
pip install mcp
# Ensure server command is in PATH
```

---

## Support

- **Docs**: https://nexus-agent.io/docs
- **GitHub**: https://github.com/yourusername/nexus-agent
- **Discord**: https://discord.gg/nexus-agent
- **Issues**: https://github.com/yourusername/nexus-agent/issues

---

**Built with ⚡ by the Nexus Team** | MIT License
