#!/usr/bin/env node
/**
 * Instagram MCP Server
 * Allows Claude Code to post on Instagram and get analytics
 * Uses Instagram Graph API (requires Business/Creator account)
 */

import { McpServer } from '@modelcontextprotocol/sdk/server/mcp.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import axios from 'axios';
import dotenv from 'dotenv';

// Load environment variables
dotenv.config();

const IG_API_BASE = 'https://graph.facebook.com/v18.0';
const ACCESS_TOKEN = process.env.FACEBOOK_ACCESS_TOKEN;
const IG_BUSINESS_ACCOUNT_ID = process.env.INSTAGRAM_BUSINESS_ACCOUNT_ID;

// Create MCP server
const server = new McpServer({
  name: 'instagram-mcp',
  version: '1.0.0',
  description: 'Instagram integration for AI Employee'
});

// Tool 1: Post Photo to Instagram
server.tool('post_photo_to_instagram', {
  description: 'Post a photo to Instagram (single image)',
  inputSchema: {
    type: 'object',
    properties: {
      imageUrl: {
        type: 'string',
        description: 'URL of the photo to post (must be publicly accessible)',
        format: 'uri'
      },
      caption: {
        type: 'string',
        description: 'Caption for the post',
        maxLength: 2200
      }
    },
    required: ['imageUrl', 'caption']
  }
}, async ({ imageUrl, caption }) => {
  try {
    console.error(`📷 Posting photo to Instagram: ${imageUrl}`);
    
    // Step 1: Create media container
    const createResponse = await axios.post(
      `${IG_API_BASE}/${IG_BUSINESS_ACCOUNT_ID}/media`,
      {
        image_url: imageUrl,
        caption: caption,
        access_token: ACCESS_TOKEN
      },
      {
        headers: { 'Content-Type': 'application/json' }
      }
    );
    
    const creationId = createResponse.data.id;
    console.error(`📝 Media container created: ${creationId}`);
    
    // Wait a moment for Instagram to process
    await new Promise(resolve => setTimeout(resolve, 3000));
    
    // Step 2: Publish the media
    const publishResponse = await axios.post(
      `${IG_API_BASE}/${IG_BUSINESS_ACCOUNT_ID}/media_publish`,
      {
        creation_id: creationId,
        access_token: ACCESS_TOKEN
      },
      {
        headers: { 'Content-Type': 'application/json' }
      }
    );
    
    const publishedMediaId = publishResponse.data.id;
    const permalink = `https://instagram.com/p/${publishedMediaId}`;
    
    return {
      content: [{
        type: 'text',
        text: `✅ Photo posted to Instagram successfully!\n\n📍 Media ID: ${publishedMediaId}\n\nNote: Check your Instagram app to view the post`
      }]
    };
  } catch (error) {
    console.error('Instagram API Error:', error.response?.data || error.message);
    return {
      content: [{
        type: 'text',
        text: `❌ Error posting to Instagram: ${error.response?.data?.error?.message || error.message}\n\nMake sure:\n- You have a Business/Creator Instagram account\n- Instagram is connected to a Facebook Page\n- Your access token is valid\n- Image URL is publicly accessible`
      }]
    };
  }
});

// Tool 2: Post Carousel (Multiple Photos) to Instagram
server.tool('post_carousel_to_instagram', {
  description: 'Post multiple photos as a carousel to Instagram',
  inputSchema: {
    type: 'object',
    properties: {
      imageUrls: {
        type: 'array',
        items: {
          type: 'string',
          format: 'uri'
        },
        description: 'Array of image URLs (3-10 images)',
        minItems: 3,
        maxItems: 10
      },
      caption: {
        type: 'string',
        description: 'Caption for the carousel',
        maxLength: 2200
      }
    },
    required: ['imageUrls', 'caption']
  }
}, async ({ imageUrls, caption }) => {
  try {
    console.error(`📷 Posting carousel to Instagram (${imageUrls.length} images)`);
    
    // Step 1: Create media containers for each image
    const creationIds = [];
    
    for (const imageUrl of imageUrls) {
      const createResponse = await axios.post(
        `${IG_API_BASE}/${IG_BUSINESS_ACCOUNT_ID}/media`,
        {
          image_url: imageUrl,
          is_carousel_item: true,
          access_token: ACCESS_TOKEN
        },
        {
          headers: { 'Content-Type': 'application/json' }
        }
      );
      
      creationIds.push(createResponse.data.id);
      console.error(`  ✓ Created container: ${createResponse.data.id}`);
    }
    
    // Wait for processing
    await new Promise(resolve => setTimeout(resolve, 5000));
    
    // Step 2: Create carousel container
    const carouselResponse = await axios.post(
      `${IG_API_BASE}/${IG_BUSINESS_ACCOUNT_ID}/media`,
      {
        media_type: 'CAROUSEL',
        children: creationIds.join(','),
        caption: caption,
        access_token: ACCESS_TOKEN
      },
      {
        headers: { 'Content-Type': 'application/json' }
      }
    );
    
    const carouselId = carouselResponse.data.id;
    
    // Wait for processing
    await new Promise(resolve => setTimeout(resolve, 3000));
    
    // Step 3: Publish the carousel
    const publishResponse = await axios.post(
      `${IG_API_BASE}/${IG_BUSINESS_ACCOUNT_ID}/media_publish`,
      {
        creation_id: carouselId,
        access_token: ACCESS_TOKEN
      },
      {
        headers: { 'Content-Type': 'application/json' }
      }
    );
    
    const publishedMediaId = publishResponse.data.id;
    
    return {
      content: [{
        type: 'text',
        text: `✅ Carousel posted to Instagram successfully! (${imageUrls.length} images)\n\n📍 Media ID: ${publishedMediaId}\n\nNote: Check your Instagram app to view the post`
      }]
    };
  } catch (error) {
    console.error('Instagram API Error:', error.response?.data || error.message);
    return {
      content: [{
        type: 'text',
        text: `❌ Error posting carousel: ${error.response?.data?.error?.message || error.message}`
      }]
    };
  }
});

// Tool 3: Get Instagram Media (Posts)
server.tool('get_instagram_media', {
  description: 'Get recent posts from your Instagram Business account',
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
    console.error(`📖 Fetching ${count} recent Instagram posts`);
    
    const response = await axios.get(
      `${IG_API_BASE}/${IG_BUSINESS_ACCOUNT_ID}/media`,
      {
        params: {
          fields: 'caption,media_type,media_url,permalink,timestamp,like_count,comments_count',
          limit: count,
          access_token: ACCESS_TOKEN
        }
      }
    );
    
    const media = response.data.data || [];
    
    if (media.length === 0) {
      return {
        content: [{
          type: 'text',
          text: '📭 No recent posts on your Instagram account.'
        }]
      };
    }
    
    const formattedMedia = media.map((item, index) => {
      const date = new Date(item.timestamp).toLocaleDateString();
      const likes = item.like_count || 0;
      const comments = item.comments_count || 0;
      
      return `${index + 1}. ${item.media_type} - ${item.caption ? item.caption.substring(0, 50) + '...' : 'No caption'}\n` +
             `   📅 ${date}\n` +
             `   ❤️ ${likes} | 💬 ${comments}\n` +
             `   🔗 ${item.permalink}`;
    }).join('\n\n');
    
    return {
      content: [{
        type: 'text',
        text: `📱 Recent Instagram Posts (${media.length}):\n\n${formattedMedia}`
      }]
    };
  } catch (error) {
    console.error('Instagram API Error:', error.response?.data || error.message);
    return {
      content: [{
        type: 'text',
        text: `❌ Error fetching media: ${error.response?.data?.error?.message || error.message}`
      }]
    };
  }
});

// Tool 4: Get Instagram Insights (Analytics)
server.tool('get_instagram_insights', {
  description: 'Get analytics/insights for your Instagram Business account',
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
    console.error(`📊 Fetching ${days}-day Instagram insights`);
    
    const response = await axios.get(
      `${IG_API_BASE}/${IG_BUSINESS_ACCOUNT_ID}/insights`,
      {
        params: {
          metric: 'impressions,reach,profile_views,website_clicks,email_contacts,get_directions_clicks',
          period: 'day',
          access_token: ACCESS_TOKEN
        }
      }
    );
    
    const insights = response.data.data || [];
    
    let summary = `📊 Instagram Insights (Last ${days} Days)\n\n`;
    
    insights.forEach(insight => {
      const values = insight.values || [];
      const total = values.reduce((sum, v) => sum + (v.value || 0), 0);
      const avg = values.length > 0 ? (total / values.length).toFixed(1) : 0;
      
      summary += `${insight.title}: ${avg.toLocaleString()} (avg/day)\n`;
    });
    
    return {
      content: [{
        type: 'text',
        text: summary
      }]
    };
  } catch (error) {
    console.error('Instagram API Error:', error.response?.data || error.message);
    return {
      content: [{
        type: 'text',
        text: `❌ Error fetching insights: ${error.response?.data?.error?.message || error.message}\n\nNote: Insights may take 24-48 hours to populate for new Business accounts`
      }]
    };
  }
});

// Tool 5: Generate Weekly Summary
server.tool('generate_instagram_weekly_summary', {
  description: 'Generate a summary of your Instagram activity for the week',
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
    console.error(`📊 Generating ${days}-day Instagram summary`);
    
    // Get media count
    const mediaResponse = await axios.get(
      `${IG_API_BASE}/${IG_BUSINESS_ACCOUNT_ID}/media`,
      {
        params: {
          limit: 100,
          fields: 'timestamp',
          access_token: ACCESS_TOKEN
        }
      }
    );
    
    const allMedia = mediaResponse.data.data || [];
    const sinceDate = Date.now() - days * 24 * 60 * 60 * 1000;
    const recentMedia = allMedia.filter(media => new Date(media.timestamp).getTime() > sinceDate);
    
    // Get insights
    const insightsResponse = await axios.get(
      `${IG_API_BASE}/${IG_BUSINESS_ACCOUNT_ID}/insights`,
      {
        params: {
          metric: 'impressions,reach,profile_views,follower_count',
          period: 'day',
          access_token: ACCESS_TOKEN
        }
      }
    );
    
    const insights = insightsResponse.data.data || [];
    
    let summary = `📊 Instagram Activity Summary (Last ${days} Days)\n\n`;
    summary += `📝 Total Posts: ${recentMedia.length}\n\n`;
    
    insights.forEach(insight => {
      const values = insight.values || [];
      const total = values.reduce((sum, v) => sum + (v.value || 0), 0);
      summary += `${insight.title}: ${total.toLocaleString()}\n`;
    });
    
    return {
      content: [{
        type: 'text',
        text: summary
      }]
    };
  } catch (error) {
    console.error('Instagram API Error:', error.response?.data || error.message);
    return {
      content: [{
        type: 'text',
        text: `❌ Error generating summary: ${error.response?.data?.error?.message || error.message}`
      }]
    };
  }
});

// Start the MCP server
console.error('🚀 Starting Instagram MCP Server...');

const transport = new StdioServerTransport();
await server.connect(transport);

console.error('✅ Instagram MCP Server running on stdio');
