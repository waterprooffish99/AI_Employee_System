#!/bin/bash

echo "🚀 Installing Twitter MCP Server..."
echo ""

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed!"
    echo "   Install it: curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -"
    echo "   Then: sudo apt-get install -y nodejs"
    exit 1
fi

echo "✅ Node.js found: $(node --version)"

# Navigate to Twitter MCP directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

echo ""
echo "📦 Installing npm dependencies..."
npm install

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Twitter MCP Server installed successfully!"
    echo ""
    echo "📝 NEXT STEPS:"
    echo "   1. Edit .env file with your Twitter API credentials"
    echo "   2. Get credentials from: https://developer.twitter.com/en/portal/dashboard"
    echo "   3. Test with: node index.js"
    echo "   4. Add to Claude Code MCP config (see README.md)"
    echo ""
    echo "📖 Full setup guide: cat README.md"
    echo ""
else
    echo ""
    echo "❌ Installation failed! Check error messages above."
    exit 1
fi
