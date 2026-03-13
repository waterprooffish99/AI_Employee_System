# Social Media Manager - Agent Skill for Cross-Platform Posting

## Overview

Unified social media management across Facebook, Instagram, and Twitter/X.

## Capabilities

- Post to all platforms simultaneously
- Platform-specific optimizations
- Generate engagement summaries
- Monitor responses and mentions
- Schedule posts

## Usage

### Post to All Platforms

```
Post this business update to all social media:
"We're excited to announce our Q1 results - 25% growth!"
Image: https://example.com/image.jpg

Platforms: facebook, instagram, twitter
```

### Generate Summary

```
Generate social media engagement summary for the last 7 days.
Include:
- Total impressions
- Engagement rates by platform
- Top performing posts
- Recommendations
```

### Platform-Specific Post

```
Post to Twitter only:
"Quick update: New feature launching tomorrow! 🚀"
```

## Response Format

```json
{
  "success": true,
  "results": {
    "facebook": {"success": true, "post_id": "12345"},
    "instagram": {"success": true, "media_id": "67890"},
    "twitter": {"success": true, "tweet_id": "11111"}
  }
}
```

## Engagement Summary Template

```markdown
# Social Media Summary - Last 7 Days

## Overall Performance
- Total Impressions: X
- Total Engagements: Y
- Overall Engagement Rate: Z%

## By Platform
| Platform | Impressions | Engagements | Rate |
|----------|-------------|-------------|------|
| Facebook | X | Y | Z% |
| Instagram | X | Y | Z% |
| Twitter | X | Y | Z% |

## Recommendations
1. [Specific action item]
```

## Best Practices

1. **Twitter**: Keep under 280 chars, use threads for longer content
2. **Instagram**: Always include images, use relevant hashtags
3. **Facebook**: Longer posts perform well, include links
4. **Timing**: Post during business hours for B2B
5. **Approval**: Always get HITL approval before posting

## Error Handling

- If platform API fails: Log error, continue with other platforms
- If rate limited: Queue post, retry later
- If authentication fails: Alert user immediately

## Integration

Works with:
- CEO Briefing generator (for metrics)
- Dashboard updater (for display)
- Audit logger (for compliance)

---

*Skill Version: 1.0.0 | Gold Tier*
