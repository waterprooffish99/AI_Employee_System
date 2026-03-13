# Skill: Process Needs Action

**Purpose**: Process items in the Needs_Action folder and create appropriate plans.

## Trigger
When new files appear in `/Needs_Action/`

## Instructions

1. **Read** all files in `/Needs_Action/` that have `status: pending`

2. **Analyze** each item:
   - What type of request is this? (email, file, payment, task)
   - What action is required?
   - Does it require human approval?

3. **Create a Plan** in `/Plans/` with format:
   ```markdown
   ---
   type: plan
   created: YYYY-MM-DDTHH:MM:SS
   status: pending_approval
   source: <original_file>
   ---

   # Plan: <Brief Description>

   ## Objective
   <What needs to be accomplished>

   ## Steps
   - [ ] Step 1: ...
   - [ ] Step 2: ...
   - [ ] Step 3: ...

   ## Approval Required
   <Yes/No - Explain if human approval is needed>
   ```

4. **For actions requiring approval**, create file in `/Pending_Approval/`:
   ```markdown
   ---
   type: approval_request
   action: <action_type>
   created: YYYY-MM-DDTHH:MM:SS
   status: pending
   ---

   ## Action Details
   <Describe what will be done>

   ## To Approve
   Move this file to /Approved folder.

   ## To Reject
   Move this file to /Rejected folder.
   ```

5. **Update Dashboard** with current status

6. **Log** all actions to `/Logs/YYYY-MM-DD.json`

## Rules
- Always consult Company_Handbook.md before acting
- Never execute external actions without approval
- Log everything
- Be transparent about decisions
