# Nexus Agent ⚡

**The self-improving AI agent — runs everywhere, built in Python.**

A complete clone of Hermes Agent with enhanced features, under 3k lines of core code.

## Features

- ✅ Multi-provider LLM support (OpenAI, Anthropic, OpenRouter, Ollama, Gemini, etc.)
- ✅ Tool calling with 40+ built-in tools
- ✅ CLI with rich TUI interface
- ✅ Messaging gateway (Telegram, Discord, Slack, WhatsApp)
- ✅ Skills system (self-improving, procedural memory)
- ✅ Memory management (persistent across sessions)
- ✅ Session persistence with SQLite + FTS5 search
- ✅ Cron scheduler for automated tasks
- ✅ Subagent delegation
- ✅ MCP server support
- ✅ Browser automation
- ✅ Terminal backends (local, Docker, SSH)

## Cross-Platform Packaging

| Platform | Package | Command |
|----------|---------|---------|
| Windows | `.exe` | `nexus.exe` |
| Android | `.apk` | `NexusAgent.apk` |
| Linux | Binary/AppImage | `nexus` |
| macOS | `.app` | `NexusAgent.app` |

## Quick Install

### Linux/macOS/Termux
```bash
curl -fsSL https://raw.githubusercontent.com/yourusername/nexus-agent/main/install.sh | bash
```

### Windows (PowerShell)
```powershell
irm https://raw.githubusercontent.com/yourusername/nexus-agent/main/install.ps1 | iex
```

### Android (Termux)
```bash
pkg install python
pip install nexus-agent
nexus
```

## Usage

```bash
nexus              # Interactive CLI
nexus gateway      # Start messaging gateway
nexus model        # Change LLM provider/model
nexus tools        # Configure tools
nexus skills       # Browse/install skills
nexus cron         # Manage scheduled tasks
```

## License

MIT — Built for the community.
