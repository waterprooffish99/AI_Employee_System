# Skill: Create Plan

**Purpose**: Create detailed action plans for tasks in Needs_Action.

**Silver Tier Requirement**: Claude reasoning loop that creates Plan.md files

---

## Trigger
When new files appear in `/Needs_Action/`

---

## Instructions

### 1. Read the Task
- Open the task file from `/Needs_Action/`
- Read the full content and metadata
- Identify the task type and requirements

### 2. Analyze the Task
Determine:
- **Task Type**: email, payment, social_media, file_processing, general
- **Priority**: urgent, normal, low
- **Complexity**: simple (1-2 steps), medium (3-5 steps), complex (5+ steps)
- **Approval Required**: Yes/No (based on Company Handbook rules)

### 3. Create Plan.md
Create a plan file in `/Plans/` with this format:

```markdown
---
type: plan
created: YYYY-MM-DDTHH:MM:SS
status: pending_approval
source: <original_file_path>
action_type: <email_send|payment|social_media|general>
---

# Plan: <Brief Description>

## Objective
<Clear statement of what needs to be accomplished>

## Analysis
- **Task Type**: <type>
- **Priority**: <priority>
- **Estimated Steps**: <count>

## Steps
- [ ] Step 1: <action>
- [ ] Step 2: <action>
- [ ] Step 3: <action>

## Resources Needed
- <resource 1>
- <resource 2>

## Approval Required
<Yes/No>

<Explanation based on Company Handbook rules>

## Success Criteria
- <criterion 1>
- <criterion 2>

## Next Action
<What should happen next - usually "Move to Pending_Approval">
```

### 4. Determine Approval Requirements

Per Company Handbook:

| Action | Auto-Approve | Requires Approval |
|--------|--------------|-------------------|
| Email to known contacts | Yes | New contacts, bulk |
| Payments | < $50 recurring | New payees, > $100 |
| Social media | Scheduled posts | Replies, DMs |
| File operations | Create, read | Delete, move outside vault |

### 5. Log and Update
- Log the plan creation to `/Logs/YYYY-MM-DD.json`
- Update Dashboard.md with new plan status

---

## Examples

### Example 1: Email Task
**Input**: `Needs_Action/EMAIL_abc123.md`
```
---
type: email
from: client@example.com
subject: Invoice Request
---

Client asking for invoice for January services.
```

**Output Plan**:
```markdown
---
type: plan
created: 2026-03-09T10:30:00Z
status: pending_approval
source: Needs_Action/EMAIL_abc123.md
action_type: email_send
---

# Plan: Send Invoice to Client

## Objective
Generate and send January invoice to client@example.com

## Steps
- [ ] Step 1: Retrieve client invoice template
- [ ] Step 2: Generate invoice PDF for January
- [ ] Step 3: Create email send request
- [ ] Step 4: Submit for approval

## Approval Required
Yes - External email requires approval per Company Handbook

## Next Action
Move to /Pending_Approval/ for human review
```

### Example 2: LinkedIn Post Task
**Input**: `Needs_Action/business_update.md`
```
Post about our new product launch on LinkedIn.
```

**Output Plan**:
```markdown
---
type: plan
created: 2026-03-09T11:00:00Z
action_type: social_media_post
---

# Plan: LinkedIn Product Launch Post

## Objective
Create and post LinkedIn update about new product launch

## Steps
- [ ] Step 1: Draft post content
- [ ] Step 2: Add relevant hashtags
- [ ] Step 3: Create approval request
- [ ] Step 4: Post after approval

## Approval Required
Yes - Social media posts require approval

## Next Action
Move to /Pending_Approval/
```

---

## Rules
- Always create plans in `/Plans/` directory
- Always include timestamp in ISO format
- Always specify approval requirements
- Move plans to `/Pending_Approval/` after creation
- Log all plan creation events

---

*Skill for AI Employee System - Silver Tier*
