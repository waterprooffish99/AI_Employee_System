# Twitter MCP Server Setup Guide

## 🎯 What This Does

This MCP server allows your AI Employee to:
- ✅ Post tweets on Twitter/X
- ✅ Post tweet threads (multiple connected tweets)
- ✅ Read your Twitter timeline
- ✅ Get tweet analytics (likes, retweets, impressions)
- ✅ Generate weekly activity summaries

## 📋 Prerequisites

- Node.js v18+ installed
- Twitter Developer Account
- Twitter App created with API credentials

## 🚀 Step-by-Step Setup

### Step 1: Get Twitter API Credentials

1. **Go to Twitter Developer Portal**: https://developer.twitter.com/
2. **Sign in** with your Twitter account
3. **Create a Project**:
   - Click "Create a project"
   - Project name: `AI Employee`
   - Use case: "Automated posting for business"
   - Description: "Automated social media management for my business"
4. **Create an App**:
   - App name: `ai-employee-bot`
   - Click "Create"
5. **Get Your Credentials**:
   - Go to your App → **Keys and tokens**
   - Copy these 5 values:
     - API Key (Consumer Key)
     - API Secret (Consumer Secret)
     - Bearer Token
     - Access Token
     - Access Token Secret

### Step 2: Install Dependencies

```bash
cd /home/waterprooffish99/projects/AI_Employee_System/mcp-servers/twitter-mcp
npm install
```

### Step 3: Configure Credentials

Edit the `.env` file with your Twitter credentials:

```bash
TWITTER_API_KEY=your_actual_api_key
TWITTER_API_SECRET=your_actual_api_secret
TWITTER_ACCESS_TOKEN=your_actual_access_token
TWITTER_ACCESS_TOKEN_SECRET=your_actual_access_token_secret
TWITTER_BEARER_TOKEN=your_actual_bearer_token
```

### Step 4: Test the MCP Server

```bash
# Test installation
npm test

# Or run directly
node index.js
```

### Step 5: Add to Claude Code Configuration

Add this to your Claude Code MCP config (`~/.config/claude-code/mcp.json`):

```json
{
  "servers": [
    {
      "name": "twitter",
      "command": "node",
      "args": ["/home/waterprooffish99/projects/AI_Employee_System/mcp-servers/twitter-mcp/index.js"],
      "env": {
        "TWITTER_API_KEY": "your_api_key",
        "TWITTER_API_SECRET": "your_api_secret",
        "TWITTER_ACCESS_TOKEN": "your_access_token",
        "TWITTER_ACCESS_TOKEN_SECRET": "your_access_token_secret",
        "TWITTER_BEARER_TOKEN": "your_bearer_token"
      }
    }
  ]
}
```

### Step 6: Test with Claude Code

```bash
claude
```

Then ask Claude:
```
Post a tweet saying "Hello from my AI Employee! #AI #Automation"
```

Or:
```
Show me my recent Twitter timeline
```

Or:
```
Generate a summary of my Twitter activity this week
```

## 🛠️ Available Commands (Tools)

| Tool | Description | Example |
|------|-------------|---------|
| `post_tweet` | Post a single tweet | "Tweet: Just launched our new product!" |
| `post_thread` | Post multiple tweets as thread | "Post a 3-tweet thread about AI benefits" |
| `get_timeline` | Read recent tweets from timeline | "Show me 10 recent tweets" |
| `get_tweet_analytics` | Get stats for a tweet | "Analytics for tweet ID: 123456" |
| `generate_weekly_summary` | Weekly activity report | "Generate my Twitter summary" |

## 🔒 Security Notes

- **NEVER** commit your `.env` file to Git
- Keep your API credentials private
- Rotate credentials monthly
- Monitor your Twitter app usage

## 🐛 Troubleshooting

### "Invalid credentials" error
- Double-check all 5 credentials in `.env`
- Make sure there are no extra spaces
- Verify your Twitter app has proper permissions

### "Rate limit exceeded" error
- Twitter has API rate limits
- Wait 15 minutes and try again
- Consider upgrading your Twitter API tier

### "Tweet failed to post" error
- Check tweet length (max 280 characters)
- Verify your account isn't suspended
- Check Twitter API status: https://api.twitterstat.us/

## 📚 Next Steps

After Twitter is working:
1. ✅ Set up Facebook MCP server
2. ✅ Set up Instagram MCP server
3. ✅ Integrate with your AI Employee workflow
4. ✅ Schedule automated posts

## 📞 Support

If you get stuck:
1. Check the logs: `node index.js` shows error messages
2. Test credentials: Use Twitter's API console
3. Review docs: https://developer.twitter.com/en/docs
