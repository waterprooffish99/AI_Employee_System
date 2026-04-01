#!/usr/bin/env node
/**
 * Facebook MCP Server
 * Allows Claude Code to post on Facebook and get analytics
 */

import { McpServer } from '@modelcontextprotocol/sdk/server/mcp.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import axios from 'axios';
import dotenv from 'dotenv';

// Load environment variables
dotenv.config();

const FB_API_BASE = 'https://graph.facebook.com/v18.0';
const ACCESS_TOKEN = process.env.FACEBOOK_ACCESS_TOKEN;
const PAGE_ID = process.env.FACEBOOK_PAGE_ID;

// Create MCP server
const server = new McpServer({
  name: 'facebook-mcp',
  version: '1.0.0',
  description: 'Facebook integration for AI Employee'
});

// Tool 1: Post to Facebook Page
server.tool('post_to_facebook', {
  description: 'Post a message to your Facebook Page',
  inputSchema: {
    type: 'object',
    properties: {
      message: {
        type: 'string',
        description: 'The post message/text',
        maxLength: 5000
      },
      link: {
        type: 'string',
        description: 'Optional link to share',
        format: 'uri'
      }
    },
    required: ['message']
  }
}, async ({ message, link }) => {
  try {
    console.error(`📝 Posting to Facebook: "${message.substring(0, 50)}..."`);
    
    const params = {
      message: message,
      access_token: ACCESS_TOKEN
    };
    
    if (link) {
      params.link = link;
    }
    
    const response = await axios.post(
      `${FB_API_BASE}/${PAGE_ID}/feed`,
      params,
      {
        headers: { 'Content-Type': 'application/json' }
      }
    );
    
    const postId = response.data.id;
    const postUrl = `https://facebook.com/${postId}`;
    
    return {
      content: [{
        type: 'text',
        text: `✅ Facebook post created successfully!\n\n📍 Post URL: ${postUrl}\n📊 Post ID: ${postId}`
      }]
    };
  } catch (error) {
    console.error('Facebook API Error:', error.response?.data || error.message);
    return {
      content: [{
        type: 'text',
        text: `❌ Error posting to Facebook: ${error.response?.data?.error?.message || error.message}\n\nMake sure your Page Access Token is valid and has pages_manage_posts permission.`
      }]
    };
  }
});

// Tool 2: Post Photo to Facebook
server.tool('post_photo_to_facebook', {
  description: 'Post a photo to your Facebook Page',
  inputSchema: {
    type: 'object',
    properties: {
      photoUrl: {
        type: 'string',
        description: 'URL of the photo to post',
        format: 'uri'
      },
      message: {
        type: 'string',
        description: 'Caption for the photo',
        maxLength: 5000
      }
    },
    required: ['photoUrl', 'message']
  }
}, async ({ photoUrl, message }) => {
  try {
    console.error(`📷 Posting photo to Facebook: ${photoUrl}`);
    
    const response = await axios.post(
      `${FB_API_BASE}/${PAGE_ID}/photos`,
      {
        url: photoUrl,
        message: message,
        access_token: ACCESS_TOKEN
      },
      {
        headers: { 'Content-Type': 'application/json' }
      }
    );
    
    const photoId = response.data.id;
    const photoUrl = `https://facebook.com/photo.php?fbid=${photoId}`;
    
    return {
      content: [{
        type: 'text',
        text: `✅ Photo posted successfully!\n\n📍 Photo URL: ${photoUrl}\n📊 Photo ID: ${photoId}`
      }]
    };
  } catch (error) {
    console.error('Facebook API Error:', error.response?.data || error.message);
    return {
      content: [{
        type: 'text',
        text: `❌ Error posting photo: ${error.response?.data?.error?.message || error.message}`
      }]
    };
  }
});

// Tool 3: Get Page Posts
server.tool('get_facebook_posts', {
  description: 'Get recent posts from your Facebook Page',
  inputSchema: {
    type: 'object',
    properties: {
      count: {
        type: 'number',
        description: 'Number of posts to fetch (default: 5)',
        default: 5,
        minimum: 1,
        maximum: 50
      }
    }
  }
}, async ({ count = 5 }) => {
  try {
    console.error(`📖 Fetching ${count} recent Facebook posts`);
    
    const response = await axios.get(
      `${FB_API_BASE}/${PAGE_ID}/posts`,
      {
        params: {
          limit: count,
          fields: 'message,created_time,permalink_url,likes.summary(true),comments.summary(true),shares',
          access_token: ACCESS_TOKEN
        }
      }
    );
    
    const posts = response.data.data || [];
    
    if (posts.length === 0) {
      return {
        content: [{
          type: 'text',
          text: '📭 No recent posts on your Facebook Page.'
        }]
      };
    }
    
    const formattedPosts = posts.map((post, index) => {
      const message = post.message || post.story || 'No text';
      const likes = post.likes?.summary?.total_count || 0;
      const comments = post.comments?.summary?.total_count || 0;
      const shares = post.shares?.count || 0;
      
      return `${index + 1}. ${message.substring(0, 100)}${message.length > 100 ? '...' : ''}\n` +
             `   📅 ${new Date(post.created_time).toLocaleDateString()}\n` +
             `   ❤️ ${likes} | 💬 ${comments} | 🔄 ${shares}\n` +
             `   🔗 ${post.permalink_url}`;
    }).join('\n\n');
    
    return {
      content: [{
        type: 'text',
        text: `📱 Recent Facebook Posts (${posts.length}):\n\n${formattedPosts}`
      }]
    };
  } catch (error) {
    console.error('Facebook API Error:', error.response?.data || error.message);
    return {
      content: [{
        type: 'text',
        text: `❌ Error fetching posts: ${error.response?.data?.error?.message || error.message}`
      }]
    };
  }
});

// Tool 4: Get Page Insights (Analytics)
server.tool('get_facebook_insights', {
  description: 'Get analytics/insights for your Facebook Page',
  inputSchema: {
    type: 'object',
    properties: {
      days: {
        type: 'number',
        description: 'Number of days of insights (default: 7)',
        default: 7,
        minimum: 1,
        maximum: 90
      }
    }
  }
}, async ({ days = 7 }) => {
  try {
    console.error(`📊 Fetching ${days}-day Facebook Page insights`);
    
    const response = await axios.get(
      `${FB_API_BASE}/${PAGE_ID}/insights`,
      {
        params: {
          metric: 'page_impressions_unique,page_engaged_users,page_post_engagements,page_likes,page_views',
          period: 'day',
          since: new Date(Date.now() - days * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
          until: new Date().toISOString().split('T')[0],
          access_token: ACCESS_TOKEN
        }
      }
    );
    
    const insights = response.data.data || [];
    
    let summary = `📊 Facebook Page Insights (Last ${days} Days)\n\n`;
    
    insights.forEach(insight => {
      const values = insight.values || [];
      const total = values.reduce((sum, v) => sum + v.value, 0);
      const avg = values.length > 0 ? (total / values.length).toFixed(1) : 0;
      
      summary += `${insight.title}: ${avg} (avg/day)\n`;
    });
    
    return {
      content: [{
        type: 'text',
        text: summary
      }]
    };
  } catch (error) {
    console.error('Facebook API Error:', error.response?.data || error.message);
    return {
      content: [{
        type: 'text',
        text: `❌ Error fetching insights: ${error.response?.data?.error?.message || error.message}`
      }]
    };
  }
});

// Tool 5: Generate Weekly Summary
server.tool('generate_facebook_weekly_summary', {
  description: 'Generate a summary of your Facebook activity for the week',
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
    console.error(`📊 Generating ${days}-day Facebook summary`);
    
    // Get posts count
    const postsResponse = await axios.get(
      `${FB_API_BASE}/${PAGE_ID}/posts`,
      {
        params: {
          limit: 100,
          fields: 'created_time',
          access_token: ACCESS_TOKEN
        }
      }
    );
    
    const allPosts = postsResponse.data.data || [];
    const sinceDate = Date.now() - days * 24 * 60 * 60 * 1000;
    const recentPosts = allPosts.filter(post => new Date(post.created_time).getTime() > sinceDate);
    
    // Get insights
    const insightsResponse = await axios.get(
      `${FB_API_BASE}/${PAGE_ID}/insights`,
      {
        params: {
          metric: 'page_impressions_unique,page_engaged_users,page_post_engagements,page_likes',
          period: 'day',
          since: new Date(sinceDate).toISOString().split('T')[0],
          until: new Date().toISOString().split('T')[0],
          access_token: ACCESS_TOKEN
        }
      }
    );
    
    const insights = insightsResponse.data.data || [];
    
    let summary = `📊 Facebook Activity Summary (Last ${days} Days)\n\n`;
    summary += `📝 Total Posts: ${recentPosts.length}\n\n`;
    
    insights.forEach(insight => {
      const values = insight.values || [];
      const total = values.reduce((sum, v) => sum + v.value, 0);
      summary += `${insight.title}: ${total.toLocaleString()}\n`;
    });
    
    return {
      content: [{
        type: 'text',
        text: summary
      }]
    };
  } catch (error) {
    console.error('Facebook API Error:', error.response?.data || error.message);
    return {
      content: [{
        type: 'text',
        text: `❌ Error generating summary: ${error.response?.data?.error?.message || error.message}`
      }]
    };
  }
});

// Start the MCP server
console.error('🚀 Starting Facebook MCP Server...');

const transport = new StdioServerTransport();
await server.connect(transport);

console.error('✅ Facebook MCP Server running on stdio');
