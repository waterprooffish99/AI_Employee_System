#!/bin/bash
# AI Employee System - Cron Job Setup Script
# Silver Tier Requirement: Basic scheduling via cron or Task Scheduler

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$(dirname "$SCRIPT_DIR")")"
VAULT_PATH="$PROJECT_ROOT/AI_Employee_Vault"

echo "=== AI Employee System - Cron Setup ==="
echo ""
echo "Project Root: $PROJECT_ROOT"
echo "Vault Path: $VAULT_PATH"
echo ""

# Detect OS
if [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]]; then
    echo "Windows detected - creating Task Scheduler tasks..."
    create_windows_tasks
else
    echo "Linux/Mac detected - creating cron jobs..."
    create_cron_jobs
fi

create_cron_jobs() {
    # Create cron jobs for watchers and orchestrator
    
    CRON_JOBS=$(cat << EOF
# AI Employee System - Scheduled Tasks
# Generated: $(date)

# Gmail Watcher - Check every 2 minutes
*/2 * * * * cd $PROJECT_ROOT && uv run python -m src.watchers.gmail_watcher >> $VAULT_PATH/Logs/cron_gmail.log 2>&1

# WhatsApp Watcher - Check every minute
* * * * * cd $PROJECT_ROOT && uv run python -m src.watchers.whatsapp_watcher >> $VAULT_PATH/Logs/cron_whatsapp.log 2>&1

# Orchestrator - Run continuously (managed by supervisor/systemd)
# Note: For production, use systemd or supervisorctl

# Daily Briefing - Generate at 8:00 AM every day
0 8 * * * cd $PROJECT_ROOT && uv run python -m src.orchestrator.daily_briefing >> $VAULT_PATH/Logs/cron_briefing.log 2>&1

# Weekly Cleanup - Archive old logs at 2:00 AM every Sunday
0 2 * * 0 cd $PROJECT_ROOT && uv run python -m src.utils.archive_logs >> $VAULT_PATH/Logs/cron_cleanup.log 2>&1
EOF
)

    # Check if crontab already has our jobs
    if crontab -l 2>/dev/null | grep -q "AI Employee System"; then
        echo "Cron jobs already exist. Updating..."
        # Remove old jobs and add new ones
        (crontab -l 2>/dev/null | grep -v "AI Employee System"; echo "$CRON_JOBS") | crontab -
    else
        echo "Adding new cron jobs..."
        (crontab -l 2>/dev/null; echo "$CRON_JOBS") | crontab -
    fi
    
    echo ""
    echo "✓ Cron jobs installed!"
    echo ""
    echo "Current cron jobs:"
    crontab -l | grep "AI Employee"
    echo ""
    echo "To view cron logs:"
    echo "  tail -f $VAULT_PATH/Logs/cron_*.log"
    echo ""
    echo "To remove cron jobs:"
    echo "  crontab -e  # Remove AI Employee System section"
}

create_windows_tasks() {
    echo "Windows Task Scheduler setup:"
    echo ""
    echo "Run these commands in PowerShell (as Administrator):"
    echo ""
    
    cat << EOF
# Gmail Watcher - Every 2 minutes
\$action = New-ScheduledTaskAction -Execute "uv" -Argument "run python -m src.watchers.gmail_watcher" -WorkingDirectory "$PROJECT_ROOT"
\$trigger = New-ScheduledTaskTrigger -Once -At (Get-Date) -RepetitionInterval (New-TimeSpan -Minutes 2)
Register-ScheduledTask -TaskName "AI_Employee_Gmail_Watcher" -Action \$action -Trigger \$trigger -Force

# WhatsApp Watcher - Every minute
\$action = New-ScheduledTaskAction -Execute "uv" -Argument "run python -m src.watchers.whatsapp_watcher" -WorkingDirectory "$PROJECT_ROOT"
\$trigger = New-ScheduledTaskTrigger -Once -At (Get-Date) -RepetitionInterval (New-TimeSpan -Minutes 1)
Register-ScheduledTask -TaskName "AI_Employee_WhatsApp_Watcher" -Action \$action -Trigger \$trigger -Force

# Daily Briefing - 8:00 AM daily
\$action = New-ScheduledTaskAction -Execute "uv" -Argument "run python -m src.orchestrator.daily_briefing" -WorkingDirectory "$PROJECT_ROOT"
\$trigger = New-ScheduledTaskTrigger -Daily -At 8:00AM
Register-ScheduledTask -TaskName "AI_Employee_Daily_Briefing" -Action \$action -Trigger \$trigger -Force
EOF

    echo ""
    echo ""
    echo "To view tasks:"
    echo "  Get-ScheduledTask | Where-Object {\$_.TaskName -like 'AI_Employee*'}"
    echo ""
    echo "To remove tasks:"
    echo "  Unregister-ScheduledTask -TaskName 'AI_Employee_*' -Confirm"
}

echo ""
echo "=== Setup Complete ==="
