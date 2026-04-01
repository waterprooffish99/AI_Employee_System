#!/bin/bash

echo "🚀 Installing All Social Media MCP Servers..."
echo ""

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed!"
    echo "   Install it with:"
    echo "   curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -"
    echo "   sudo apt-get install -y nodejs"
    exit 1
fi

echo "✅ Node.js found: $(node --version)"
echo ""

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
MCP_DIR="$PROJECT_DIR/mcp-servers"

# Install Twitter MCP
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🐦 Installing Twitter MCP Server..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
cd "$MCP_DIR/twitter-mcp"
npm install
if [ $? -eq 0 ]; then
    echo "✅ Twitter MCP installed!"
else
    echo "❌ Twitter MCP installation failed!"
    exit 1
fi
echo ""

# Install Facebook MCP
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📘 Installing Facebook MCP Server..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
cd "$MCP_DIR/facebook-mcp"
npm install
if [ $? -eq 0 ]; then
    echo "✅ Facebook MCP installed!"
else
    echo "❌ Facebook MCP installation failed!"
    exit 1
fi
echo ""

# Install Instagram MCP
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📸 Installing Instagram MCP Server..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
cd "$MCP_DIR/instagram-mcp"
npm install
if [ $? -eq 0 ]; then
    echo "✅ Instagram MCP installed!"
else
    echo "❌ Instagram MCP installation failed!"
    exit 1
fi
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ ALL MCP SERVERS INSTALLED SUCCESSFULLY!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📝 NEXT STEPS:"
echo ""
echo "1. Configure credentials for each server:"
echo "   - Twitter:     nano $MCP_DIR/twitter-mcp/.env"
echo "   - Facebook:    nano $MCP_DIR/facebook-mcp/.env"
echo "   - Instagram:   nano $MCP_DIR/instagram-mcp/.env"
echo ""
echo "2. Get API credentials from:"
echo "   - Twitter:     https://developer.twitter.com/en/portal/dashboard"
echo "   - Facebook:    https://developers.facebook.com/apps/"
echo "   - Instagram:   Requires Facebook Page + Business Instagram account"
echo ""
echo "3. Add servers to Claude Code config:"
echo "   nano ~/.config/claude-code/mcp.json"
echo ""
echo "4. Test each server:"
echo "   cd $MCP_DIR/twitter-mcp && node index.js"
echo "   cd $MCP_DIR/facebook-mcp && node index.js"
echo "   cd $MCP_DIR/instagram-mcp && node index.js"
echo ""
echo "📖 Full setup guide: cat $PROJECT_DIR/SOCIAL_MEDIA_SETUP_GUIDE.md"
echo ""
