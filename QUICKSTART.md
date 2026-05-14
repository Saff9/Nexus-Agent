# ⚡ Nexus Agent - Quick Start Guide

## Installation

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

### From Source
```bash
git clone https://github.com/yourusername/nexus-agent.git
cd nexus-agent
pip install -e ".[cli]"
nexus
```

## Configuration

### Set API Keys (Required)

**Linux/macOS:**
```bash
export OPENAI_API_KEY='sk-...'
export ANTHROPIC_API_KEY='sk-ant-...'
export OPENROUTER_API_KEY='sk-or-...'
```

**Windows (PowerShell):**
```powershell
$env:OPENAI_API_KEY="sk-..."
[Environment]::SetEnvironmentVariable("OPENAI_API_KEY", "sk-...", "User")
```

**Permanent (add to ~/.bashrc or ~/.zshrc):**
```bash
export OPENROUTER_API_KEY='sk-or-...'  # Recommended: 200+ models
```

## Usage

### Interactive CLI
```bash
nexus              # Start chat
nexus /help        # Show commands
nexus /model openai:gpt-4o-mini  # Change model
nexus /new         # New session
```

### As Python Library
```python
from core import NexusAgent, Config

config = Config.load()
agent = NexusAgent(config)

response = agent.run_conversation("Hello!")
print(response)
```

### Gateway (Messaging Platforms)
```bash
# Telegram
nexus gateway telegram --token YOUR_BOT_TOKEN

# Discord
nexus gateway discord --token YOUR_BOT_TOKEN
```

## Building

### Build for Current Platform
```bash
python build.py
```

### Build for Specific Platform
```bash
python build.py --platform windows   # .exe
python build.py --platform linux     # binary
python build.py --platform macos     # .app
python build.py --platform android   # .apk
python build.py --pip               # pip package
```

## Features

### Tools (Built-in)
- `read_file` / `write_file` - File operations
- `search_files` - Find files by pattern
- `run_command` - Execute shell commands
- `web_search` - Search the web
- `web_fetch` - Fetch URL content
- `list_directory` - List folder contents
- `get_env` - Get environment variables

### Commands
| Command | Description |
|---------|-------------|
| `/help` | Show all commands |
| `/status` | Agent status |
| `/model <name>` | Change AI model |
| `/new` | New conversation |
| `/clear` | Clear screen |
| `/config` | Show config |
| `/tools` | List tools |
| `/skills` | List skills |
| `/memory` | Show memory |
| `/quit` | Exit |

### Supported Providers
- **OpenRouter** (Recommended) - 200+ models
- **OpenAI** - GPT-4, GPT-4o, o1
- **Anthropic** - Claude Sonnet, Opus
- **Ollama** - Local models (llama3.1, mistral, etc.)
- **Gemini** - Via OpenRouter

## Project Structure

```
nexus-agent/
├── core/           # Agent engine
│   ├── agent.py    # Main agent loop
│   ├── config.py   # Configuration
│   ├── session.py  # Session management
│   ├── memory.py   # Memory system
│   └── provider.py # LLM providers
├── tools/          # Built-in tools
├── skills/         # Skills (procedural memory)
├── cli.py          # Command-line interface
├── app.py          # Kivy mobile app
├── build.py        # Build script
├── install.sh      # Linux/macOS installer
├── install.ps1     # Windows installer
└── buildozer.spec  # Android build config
```

## Troubleshooting

### "Module not found"
```bash
pip install -e .
```

### "API key not set"
```bash
export OPENROUTER_API_KEY='your-key'
```

### "Permission denied" (Linux)
```bash
chmod +x ~/.local/bin/nexus
```

### Android APK build fails
```bash
# Install dependencies
sudo apt install python3-pip python3-venv libffi-dev libssl-dev
pip install buildozer
buildozer android debug
```

## Resources

- Documentation: https://nexus-agent.io/docs
- GitHub: https://github.com/yourusername/nexus-agent
- Discord: https://discord.gg/nexus-agent

---

**Built with ⚡ by the Nexus Team** | MIT License
