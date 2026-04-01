#!/usr/bin/env node
/**
 * Twitter/X MCP Server
 * Allows Claude Code to post tweets and read timeline
 */

import { McpServer } from '@modelcontextprotocol/sdk/server/mcp.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import { TwitterApi } from 'twitter-api-v2';
import dotenv from 'dotenv';

// Load environment variables
dotenv.config();

// Initialize Twitter client
const twitterClient = new TwitterApi({
  appKey: process.env.TWITTER_API_KEY,
  appSecret: process.env.TWITTER_API_SECRET,
  accessToken: process.env.TWITTER_ACCESS_TOKEN,
  accessSecret: process.env.TWITTER_ACCESS_TOKEN_SECRET,
});

// Create MCP server
const server = new McpServer({
  name: 'twitter-mcp',
  version: '1.0.0',
  description: 'Twitter/X integration for AI Employee'
});

// Tool 1: Post a Tweet
server.tool('post_tweet', {
  description: 'Post a new tweet on Twitter/X',
  inputSchema: {
    type: 'object',
    properties: {
      text: {
        type: 'string',
        description: 'The tweet text (max 280 characters)',
        maxLength: 280
      }
    },
    required: ['text']
  }
}, async ({ text }) => {
  try {
    console.error(`📝 Posting tweet: "${text}"`);
    
    const tweet = await twitterClient.v2.tweet(text);
    
    const tweetUrl = `https://twitter.com/i/web/status/${tweet.data.id}`;
    
    return {
      content: [{
        type: 'text',
        text: `✅ Tweet posted successfully!\n\n📍 Tweet URL: ${tweetUrl}\n📊 Tweet ID: ${tweet.data.id}`
      }]
    };
  } catch (error) {
    console.error('Twitter API Error:', error);
    return {
      content: [{
        type: 'text',
        text: `❌ Error posting tweet: ${error.message}\n\nMake sure your Twitter API credentials are valid.`
      }]
    };
  }
});

// Tool 2: Post a Thread (multiple connected tweets)
server.tool('post_thread', {
  description: 'Post a thread of multiple tweets on Twitter/X',
  inputSchema: {
    type: 'object',
    properties: {
      tweets: {
        type: 'array',
        items: {
          type: 'string',
          maxLength: 280
        },
        description: 'Array of tweet texts for the thread',
        minItems: 1,
        maxItems: 10
      }
    },
    required: ['tweets']
  }
}, async ({ tweets }) => {
  try {
    console.error(`📝 Posting thread with ${tweets.length} tweets`);
    
    const tweetIds = [];
    let replyTo = null;
    
    for (let i = 0; i < tweets.length; i++) {
      const tweetText = tweets[i];
      const tweetData = replyTo 
        ? await twitterClient.v2.tweet({ text: tweetText, reply: { in_reply_to_tweet_id: replyTo } })
        : await twitterClient.v2.tweet(tweetText);
      
      tweetIds.push(tweetData.data.id);
      replyTo = tweetData.data.id;
      
      console.error(`  ✓ Tweet ${i + 1}/${tweets.length} posted`);
    }
    
    const firstTweetUrl = `https://twitter.com/i/web/status/${tweetIds[0]}`;
    
    return {
      content: [{
        type: 'text',
        text: `✅ Thread posted successfully! (${tweets.length} tweets)\n\n📍 First tweet URL: ${firstTweetUrl}\n📊 Tweet IDs: ${tweetIds.join(', ')}`
      }]
    };
  } catch (error) {
    console.error('Twitter API Error:', error);
    return {
      content: [{
        type: 'text',
        text: `❌ Error posting thread: ${error.message}`
      }]
    };
  }
});

// Tool 3: Get Recent Tweets from Timeline
server.tool('get_timeline', {
  description: 'Get recent tweets from your Twitter timeline',
  inputSchema: {
    type: 'object',
    properties: {
      count: {
        type: 'number',
        description: 'Number of tweets to fetch (default: 5)',
        default: 5,
        minimum: 1,
        maximum: 20
      }
    }
  }
}, async ({ count = 5 }) => {
  try {
    console.error(`📖 Fetching ${count} recent tweets from timeline`);
    
    const timeline = await twitterClient.v2.homeTimeline({
      'tweet.fields': ['created_at', 'author_id', 'text', 'public_metrics'],
      'user.fields': ['name', 'username'],
      max_results: count
    });
    
    const tweets = timeline.data.data || [];
    
    if (tweets.length === 0) {
      return {
        content: [{
          type: 'text',
          text: '📭 No recent tweets in your timeline.'
        }]
      };
    }
    
    const formattedTweets = tweets.map(tweet => {
      const metrics = tweet.public_metrics;
      return `• @${timeline.data.includes.users.find(u => u.id === tweet.author_id)?.username || 'Unknown'}: ${tweet.text}\n  ❤️ ${metrics.like_count} | 🔄 ${metrics.retweet_count} | 💬 ${metrics.reply_count}`;
    }).join('\n\n');
    
    return {
      content: [{
        type: 'text',
        text: `📱 Recent Tweets (${tweets.length}):\n\n${formattedTweets}`
      }]
    };
  } catch (error) {
    console.error('Twitter API Error:', error);
    return {
      content: [{
        type: 'text',
        text: `❌ Error fetching timeline: ${error.message}`
      }]
    };
  }
});

// Tool 4: Get Tweet Analytics (likes, retweets, etc.)
server.tool('get_tweet_analytics', {
  description: 'Get analytics for a specific tweet',
  inputSchema: {
    type: 'object',
    properties: {
      tweetId: {
        type: 'string',
        description: 'The ID of the tweet to analyze'
      }
    },
    required: ['tweetId']
  }
}, async ({ tweetId }) => {
  try {
    console.error(`📊 Fetching analytics for tweet ${tweetId}`);
    
    const tweet = await twitterClient.v2.singleTweet(tweetId, {
      'tweet.fields': ['created_at', 'text', 'public_metrics', 'non_public_metrics']
    });
    
    const metrics = tweet.data.public_metrics;
    
    return {
      content: [{
        type: 'text',
        text: `📊 Tweet Analytics\n\n` +
              `📝 Text: ${tweet.data.text}\n` +
              `📅 Posted: ${tweet.data.created_at}\n\n` +
              `❤️ Likes: ${metrics.like_count}\n` +
              `🔄 Retweets: ${metrics.retweet_count}\n` +
              `💬 Replies: ${metrics.reply_count}\n` +
              `👁️ Impressions: ${metrics.impression_count || 'N/A'}`
      }]
    };
  } catch (error) {
    console.error('Twitter API Error:', error);
    return {
      content: [{
        type: 'text',
        text: `❌ Error fetching analytics: ${error.message}`
      }]
    };
  }
});

// Tool 5: Generate Weekly Summary
server.tool('generate_weekly_summary', {
  description: 'Generate a summary of your Twitter activity for the week',
  inputSchema: {
    type: 'object',
    properties: {
      days: {
        type: 'number',
        description: 'Number of days to summarize (default: 7)',
        default: 7,
        minimum: 1,
        maximum: 30
      }
    }
  }
}, async ({ days = 7 }) => {
  try {
    console.error(`📊 Generating ${days}-day Twitter summary`);
    
    // Get user's recent tweets
    const user = await twitterClient.v2.me();
    const myTweets = await twitterClient.v2.userTimeline(user.data.id, {
      'tweet.fields': ['created_at', 'public_metrics'],
      max_results: 100
    });
    
    const tweets = myTweets.data.data || [];
    const totalTweets = tweets.length;
    const totalLikes = tweets.reduce((sum, t) => sum + (t.public_metrics?.like_count || 0), 0);
    const totalRetweets = tweets.reduce((sum, t) => sum + (t.public_metrics?.retweet_count || 0), 0);
    const totalReplies = tweets.reduce((sum, t) => sum + (t.public_metrics?.reply_count || 0), 0);
    
    return {
      content: [{
        type: 'text',
        text: `📊 Twitter Activity Summary (Last ${days} Days)\n\n` +
              `📝 Total Tweets: ${totalTweets}\n` +
              `❤️ Total Likes Received: ${totalLikes}\n` +
              `🔄 Total Retweets: ${totalRetweets}\n` +
              `💬 Total Replies: ${totalReplies}\n\n` +
              `📈 Average Engagement per Tweet:\n` +
              `   - Likes: ${(totalLikes / totalTweets || 0).toFixed(1)}\n` +
              `   - Retweets: ${(totalRetweets / totalTweets || 0).toFixed(1)}\n` +
              `   - Replies: ${(totalReplies / totalTweets || 0).toFixed(1)}`
      }]
    };
  } catch (error) {
    console.error('Twitter API Error:', error);
    return {
      content: [{
        type: 'text',
        text: `❌ Error generating summary: ${error.message}`
      }]
    };
  }
});

// Start the MCP server
console.error('🚀 Starting Twitter MCP Server...');

const transport = new StdioServerTransport();
await server.connect(transport);

console.error('✅ Twitter MCP Server running on stdio');
