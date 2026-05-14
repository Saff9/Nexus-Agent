#!/bin/bash
# Nexus Agent Installer for Linux/macOS/Termux

set -e

echo "╔═══════════════════════════════════════════════════════╗"
echo "║                                                       ║"
echo "║   ⚡  N E X U S   A G E N T   I N S T A L L E R       ║"
echo "║                                                       ║"
echo "╚═══════════════════════════════════════════════════════╝"
echo

# Detect platform
PLATFORM=$(uname -s | tr '[:upper:]' '[:lower:]')
ARCH=$(uname -m)

echo "📱 Platform: $PLATFORM ($ARCH)"

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3.10+ is required"
    echo "   Install: sudo apt install python3 python3-pip (Ubuntu/Debian)"
    echo "   Install: brew install python (macOS)"
    exit 1
fi

PYTHON_VERSION=$(python3 --version 2>&1 | cut -d' ' -f2)
echo "✓ Python: $PYTHON_VERSION"

# Create directories
INSTALL_DIR="${NEXUS_INSTALL_DIR:-$HOME/.nexus}"
BIN_DIR="$HOME/.local/bin"

mkdir -p "$INSTALL_DIR"
mkdir -p "$BIN_DIR"

echo "📁 Install directory: $INSTALL_DIR"

# Clone or copy repository
if [ -d "nexus-agent" ]; then
    echo "📦 Installing from local directory..."
    cp -r nexus-agent/* "$INSTALL_DIR/"
else
    echo "📦 Downloading latest release..."
    # Would download from GitHub releases
    git clone https://github.com/yourusername/nexus-agent.git "$INSTALL_DIR/src" 2>/dev/null || {
        echo "⚠️  Git clone failed, using local files"
        mkdir -p "$INSTALL_DIR/src"
        cp -r . "$INSTALL_DIR/src/" 2>/dev/null || true
    }
fi

# Create virtual environment
echo "🔧 Creating virtual environment..."
python3 -m venv "$INSTALL_DIR/venv"
source "$INSTALL_DIR/venv/bin/activate"

# Install dependencies
echo "📦 Installing dependencies..."
pip install --upgrade pip
pip install httpx pyyaml prompt-toolkit rich

# Install nexus-agent
cd "$INSTALL_DIR/src"
pip install -e .

# Create launcher script
cat > "$BIN_DIR/nexus" << 'EOF'
#!/bin/bash
INSTALL_DIR="${NEXUS_INSTALL_DIR:-$HOME/.nexus}"
source "$INSTALL_DIR/venv/bin/activate"
python "$INSTALL_DIR/src/cli.py" "$@"
EOF

chmod +x "$BIN_DIR/nexus"

# Add to PATH if not already
if [[ ":$PATH:" != *":$HOME/.local/bin:"* ]]; then
    echo ""
    echo "⚠️  Adding $HOME/.local/bin to PATH..."
    if [[ -f "$HOME/.bashrc" ]]; then
        echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$HOME/.bashrc"
    fi
    if [[ -f "$HOME/.zshrc" ]]; then
        echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$HOME/.zshrc"
    fi
    echo "   Please restart your shell or run: export PATH=\"\$HOME/.local/bin:\$PATH\""
fi

# Setup complete
echo ""
echo "╔═══════════════════════════════════════════════════════╗"
echo "║                                                       ║"
echo "║   ⚡  I N S T A L L A T I O N   C O M P L E T E       ║"
echo "║                                                       ║"
echo "╚═══════════════════════════════════════════════════════╝"
echo ""
echo "🚀 Quick Start:"
echo "   nexus              # Start interactive CLI"
echo "   nexus --help       # Show all commands"
echo ""
echo "⚙️  Configure API keys:"
echo "   export OPENAI_API_KEY='your-key'"
echo "   export ANTHROPIC_API_KEY='your-key'"
echo "   export OPENROUTER_API_KEY='your-key'"
echo ""
echo "📚 Documentation: https://nexus-agent.io/docs"
echo ""
