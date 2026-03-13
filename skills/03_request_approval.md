# Skill: Request Approval

**Purpose**: Create approval request files for actions requiring human intervention.

## Trigger
When an action requires human approval before execution.

## Approval Thresholds (from Company_Handbook.md)

| Action Category | Auto-Approve | Always Require Approval |
|-----------------|--------------|------------------------|
| Email replies | To known contacts | New contacts, bulk sends |
| Payments | < $50 recurring | All new payees, > $100 |
| Social media | Scheduled posts | Replies, DMs |
| File operations | Create, read | Delete, move outside vault |

## Instructions

1. **Determine** if action requires approval based on thresholds above

2. **Create** approval request file in `/Pending_Approval/`:
   ```markdown
   ---
   type: approval_request
   action: <action_type>
   <action-specific fields>
   created: YYYY-MM-DDTHH:MM:SS
   expires: YYYY-MM-DDTHH:MM:SS (24 hours from creation)
   status: pending
   ---

   ## Action Details
   <Full description of what will be done>

   ## Parameters
   - Field 1: value
   - Field 2: value

   ## Impact
   <What will happen when this is executed>

   ## To Approve
   Move this file to /Approved folder.

   ## To Reject
   Move this file to /Rejected folder or delete.
   ```

3. **Log** the approval request

4. **Update Dashboard** to show pending approval

## Rules
- Always include expiration time
- Be specific about what will be done
- Never execute without approval for sensitive actions
