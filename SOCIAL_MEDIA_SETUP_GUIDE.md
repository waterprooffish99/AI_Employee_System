# 📱 Social Media Integration - Complete Beginner's Guide

## 🎯 What You're Building

You're creating an AI Employee that can:
- ✅ **Post automatically** to Twitter, Facebook, and Instagram
- ✅ **Generate summaries** of your social media performance
- ✅ **Read analytics** and report engagement metrics
- ✅ **Respond to messages** (WhatsApp integration already exists)

## 📁 Project Structure

```
mcp-servers/
├── twitter-mcp/       # Twitter/X integration
├── facebook-mcp/      # Facebook integration
└── instagram-mcp/     # Instagram integration
```

---

## 🐦 PART 1: Twitter/X Setup

### Step 1: Get Twitter API Credentials (15 minutes)

1. **Go to**: https://developer.twitter.com/
2. **Sign in** with your Twitter account
3. **Create Project**:
   - Click "Create a project" → "Create"
   - Project name: `AI Employee`
   - Use case: "Automated social media posting for my business"
   - Click "Next"
4. **Create App**:
   - App name: `ai-employee-bot`
   - Click "Next"
   - Click "Create"
5. **Get Credentials**:
   - Go to your App → **Keys and tokens**
   - **Copy these 5 values** (you'll need them later):
     - API Key (Consumer Key)
     - API Secret (Consumer Secret)
     - Bearer Token
     - Access Token
     - Access Token Secret

### Step 2: Install Twitter MCP Server

```bash
# Navigate to Twitter MCP directory
cd /home/waterprooffish99/projects/AI_Employee_System/mcp-servers/twitter-mcp

# Install dependencies
./install.sh
# OR manually:
npm install
```

### Step 3: Configure Credentials

```bash
# Edit the .env file
nano .env
```

Replace the placeholder values:
```env
TWITTER_API_KEY=your_actual_api_key
TWITTER_API_SECRET=your_actual_api_secret
TWITTER_ACCESS_TOKEN=your_actual_access_token
TWITTER_ACCESS_TOKEN_SECRET=your_actual_access_token_secret
TWITTER_BEARER_TOKEN=your_actual_bearer_token
```

Save and exit (Ctrl+X, Y, Enter)

### Step 4: Test Twitter MCP

```bash
# Test the server
node index.js
```

If it starts without errors, press `Ctrl+C` to stop.

---

## 📘 PART 2: Facebook Setup

### Step 1: Create Facebook App (20 minutes)

1. **Go to**: https://developers.facebook.com/apps/
2. **Click "Create App"**
3. **Select Use Case**: "Other" → "Next"
4. **App Type**: "Business" → "Next"
5. **App Details**:
   - App name: `AI Employee`
   - App contact email: your email
   - Click "Create App"
6. **Add Products**:
   - Scroll down and find "Marketing API" → Click "Set Up"
   - Find "Pages API" → Click "Set Up"
7. **Get Credentials**:
   - Go to App Dashboard → **Settings → Basic**
   - Copy:
     - App ID
     - App Secret (click "Show")

### Step 2: Get Page Access Token

1. **Go to**: https://developers.facebook.com/tools/explorer/
2. **Select your app** from dropdown
3. **Click "Get Token" → "Get Page Access Token"**
4. **Select your Facebook Page** (create one if you don't have)
5. **Copy the Access Token**

**Important**: This token expires in 1 hour. For production, you need a long-lived token (valid 60 days). See: https://developers.facebook.com/docs/pages/access-tokens

### Step 3: Get Your Page ID

1. **Go to your Facebook Page**
2. **Click "About"**
3. **Find "Facebook Page ID"** (it's a number)
4. **Copy it**

### Step 4: Install Facebook MCP Server

```bash
cd /home/waterprooffish99/projects/AI_Employee_System/mcp-servers/facebook-mcp
npm install
```

### Step 5: Configure Credentials

```bash
nano .env
```

```env
FACEBOOK_APP_ID=your_app_id
FACEBOOK_APP_SECRET=your_app_secret
FACEBOOK_ACCESS_TOKEN=your_page_access_token
FACEBOOK_PAGE_ID=your_page_id
```

---

## 📸 PART 3: Instagram Setup

### Prerequisites

⚠️ **IMPORTANT**: You MUST have:
1. Instagram **Business** or **Creator** account (free to convert)
2. Instagram connected to a Facebook Page

### Step 1: Convert to Business Account (5 minutes)

1. **Open Instagram app** → Go to your profile
2. **Menu (☰)** → Settings and privacy
3. **Account type and tools** → "Switch to professional account"
4. **Choose category** (e.g., "Business")
5. **Confirm**

### Step 2: Connect Instagram to Facebook Page

1. **Instagram app** → Profile → Menu (☰)
2. **Settings** → Account → Linked Accounts
3. **Facebook** → Connect
4. **Select your Facebook Page**

### Step 3: Get Instagram Business Account ID

1. **Go to**: https://graph.facebook.com/v18.0/me/accounts?access_token=YOUR_ACCESS_TOKEN
2. **Replace YOUR_ACCESS_TOKEN** with your Facebook access token
3. **Look for** `instagram_business_account` → `id`
4. **Copy this ID**

### Step 4: Install Instagram MCP Server

```bash
cd /home/waterprooffish99/projects/AI_Employee_System/mcp-servers/instagram-mcp
npm install
```

### Step 5: Configure Credentials

```bash
nano .env
```

```env
INSTAGRAM_BUSINESS_ACCOUNT_ID=your_ig_business_account_id
FACEBOOK_PAGE_ID=your_connected_fb_page_id
FACEBOOK_ACCESS_TOKEN=your_long_lived_access_token
```

---

## 🔧 PART 4: Configure Claude Code

### Step 1: Edit Claude Code MCP Config

```bash
nano ~/.config/claude-code/mcp.json
```

### Step 2: Add All Three Servers

```json
{
  "mcpServers": {
    "twitter": {
      "command": "node",
      "args": ["/home/waterprooffish99/projects/AI_Employee_System/mcp-servers/twitter-mcp/index.js"],
      "env": {
        "TWITTER_API_KEY": "your_api_key",
        "TWITTER_API_SECRET": "your_api_secret",
        "TWITTER_ACCESS_TOKEN": "your_access_token",
        "TWITTER_ACCESS_TOKEN_SECRET": "your_access_token_secret",
        "TWITTER_BEARER_TOKEN": "your_bearer_token"
      }
    },
    "facebook": {
      "command": "node",
      "args": ["/home/waterprooffish99/projects/AI_Employee_System/mcp-servers/facebook-mcp/index.js"],
      "env": {
        "FACEBOOK_APP_ID": "your_app_id",
        "FACEBOOK_APP_SECRET": "your_app_secret",
        "FACEBOOK_ACCESS_TOKEN": "your_access_token",
        "FACEBOOK_PAGE_ID": "your_page_id"
      }
    },
    "instagram": {
      "command": "node",
      "args": ["/home/waterprooffish99/projects/AI_Employee_System/mcp-servers/instagram-mcp/index.js"],
      "env": {
        "INSTAGRAM_BUSINESS_ACCOUNT_ID": "your_ig_id",
        "FACEBOOK_PAGE_ID": "your_page_id",
        "FACEBOOK_ACCESS_TOKEN": "your_access_token"
      }
    }
  }
}
```

Save and exit (Ctrl+X, Y, Enter)

---

## 🎯 PART 5: Test Your Integration

### Test Twitter

```bash
claude
```

Then ask:
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

### Test Facebook

Ask Claude:
```
Post to Facebook: "Excited to share our latest updates! Check out our new AI Employee system. #AI #Innovation"
```

Or:
```
Show me my recent Facebook posts
```

Or:
```
Get my Facebook page insights for the last 7 days
```

### Test Instagram

Ask Claude:
```
Post to Instagram this photo: https://example.com/image.jpg with caption "Building amazing things with AI! 🚀 #AI #Technology"
```

Or:
```
Show me my recent Instagram posts
```

Or:
```
Generate my Instagram weekly summary
```

---

## 📊 Available Commands Summary

### Twitter Commands
| Command | What it does |
|---------|-------------|
| `post_tweet` | Post a single tweet |
| `post_thread` | Post multiple tweets as a thread |
| `get_timeline` | Read your Twitter timeline |
| `get_tweet_analytics` | Get stats for a specific tweet |
| `generate_weekly_summary` | Weekly activity report |

### Facebook Commands
| Command | What it does |
|---------|-------------|
| `post_to_facebook` | Post text (with optional link) |
| `post_photo_to_facebook` | Post a photo with caption |
| `get_facebook_posts` | Get recent page posts |
| `get_facebook_insights` | Get page analytics |
| `generate_facebook_weekly_summary` | Weekly summary |

### Instagram Commands
| Command | What it does |
|---------|-------------|
| `post_photo_to_instagram` | Post a single photo |
| `post_carousel_to_instagram` | Post 3-10 photos as carousel |
| `get_instagram_media` | Get recent posts |
| `get_instagram_insights` | Get analytics |
| `generate_instagram_weekly_summary` | Weekly summary |

---

## 🚨 Troubleshooting

### Twitter Issues

**"Invalid credentials"**
- Double-check all 5 credentials in `.env`
- No extra spaces or quotes
- Restart the MCP server after changes

**"Rate limit exceeded"**
- Twitter limits: 300 tweets per 3 hours (for most tiers)
- Wait 15 minutes and try again

**"Tweet failed"**
- Max 280 characters per tweet
- Check for prohibited content

### Facebook Issues

**"Invalid access token"**
- Page tokens expire in 1 hour
- Get a new token from Graph API Explorer
- For production, generate a long-lived token (60 days)

**"Permissions error"**
- Your app needs review for certain permissions
- Go to App Review in Facebook Developer dashboard

### Instagram Issues

**"Business account required"**
- Convert to Business/Creator account in Instagram settings
- Free upgrade, takes 2 minutes

**"No media found"**
- Insights take 24-48 hours to populate for new accounts
- Make sure Instagram is linked to Facebook Page

---

## 🔒 Security Best Practices

1. **Never commit `.env` files** to Git
   - They're already in `.gitignore` - don't remove!

2. **Rotate credentials monthly**
   - Generate new tokens from each platform

3. **Use environment variables**
   - Never hardcode credentials in code

4. **Monitor API usage**
   - Check your developer dashboards regularly

5. **Limit permissions**
   - Only request permissions you actually need

---

## 📝 Testing Checklist

Before marking this complete, verify:

- [ ] Twitter MCP server starts without errors
- [ ] Can post a tweet via Claude
- [ ] Can read Twitter timeline
- [ ] Facebook MCP server starts without errors
- [ ] Can post to Facebook page
- [ ] Can get Facebook insights
- [ ] Instagram MCP server starts without errors
- [ ] Can post photo to Instagram
- [ ] Can get Instagram media list
- [ ] All three servers configured in Claude Code
- [ ] `.env` files NOT committed to Git

---

## 🎓 Example Use Cases

### 1. Automated Daily Post
```
Claude, every day at 9 AM, post an motivational quote to Twitter, Facebook, and Instagram
```

### 2. Product Launch Campaign
```
Claude, create a 5-tweet thread about our new product launch, then post it to all platforms
```

### 3. Weekly Performance Report
```
Claude, generate a summary of all social media performance this week
```

### 4. Cross-Platform Announcement
```
Claude, post this announcement to all three platforms with platform-appropriate formatting
```

---

## 📚 Additional Resources

- **Twitter API Docs**: https://developer.twitter.com/en/docs
- **Facebook Graph API**: https://developers.facebook.com/docs/graph-api
- **Instagram Graph API**: https://developers.facebook.com/docs/instagram-api
- **MCP SDK**: https://modelcontextprotocol.io/docs

---

## ✅ Next Steps

After completing social media integrations:

1. ✅ **WhatsApp Integration** (already in your project as Watcher)
2. ✅ **Weekly CEO Briefing** (aggregate all social media data)
3. ✅ **Scheduling System** (cron jobs for automated posts)
4. ✅ **Human-in-the-Loop Approval** (require approval before posting)

---

**🎉 Congratulations!** You now have a fully functional social media management AI Employee!
