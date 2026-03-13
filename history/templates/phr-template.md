# Prompt History Record (PHR)

**ID**: PHR-{{YYYYMMDD}}-{{NNN}}  
**Timestamp**: {{timestamp}}  
**Skill Used**: {{skill_name}}  
**Status**: {{completed|failed|pending}}

---

## Context

**Trigger**: {{what_triggered_this_prompt}}  
**Task File**: {{task_file_path}}  
**Actor**: {{claude_code|watcher|orchestrator}}

---

## Prompt

```
{{full_prompt_sent_to_claude}}
```

---

## Response Summary

{{summary_of_claude_response}}

### Actions Taken
- {{action_1}}
- {{action_2}}
- {{action_3}}

### Files Created/Modified
- {{file_1}}
- {{file_2}}

---

## Outcome

**Result**: {{success|failure|partial}}

**Lessons Learned**:
{{what_did_we_learn}}

**Follow-up Required**: {{yes/no}}

---

## Audit Trail

| Timestamp | Event | Actor |
|-----------|-------|-------|
| {{time}} | {{event}} | {{actor}} |

---

*PHR for audit, learning, and future reference*
