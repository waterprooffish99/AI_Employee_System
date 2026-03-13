#!/usr/bin/env bash
# Ralph Wiggum Loop Runner for Gold Tier AI Employee System
# Usage: bash .specify/scripts/bash/run_ralph_loop.sh --task "process_all_files"

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$(dirname "$SCRIPT_DIR")")"

cd "$PROJECT_ROOT"

# Default values
TASK=""
MAX_ITERATIONS=10
MODEL="claude"
DRY_RUN=false
VERBOSE=false

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --task)
            TASK="$2"
            shift 2
            ;;
        --max-iterations)
            MAX_ITERATIONS="$2"
            shift 2
            ;;
        --model)
            MODEL="$2"
            shift 2
            ;;
        --dry-run)
            DRY_RUN=true
            shift
            ;;
        --verbose)
            VERBOSE=true
            shift
            ;;
        --help)
            echo "Ralph Wiggum Loop Runner"
            echo ""
            echo "Usage: bash .specify/scripts/bash/run_ralph_loop.sh --task <task_id> [options]"
            echo ""
            echo "Options:"
            echo "  --task <id>           Task ID (filename without .md)"
            echo "  --max-iterations <n>  Maximum iterations (default: 10)"
            echo "  --model <name>        LLM model: claude or gemini (default: claude)"
            echo "  --dry-run             Test without calling LLM API"
            echo "  --verbose             Enable verbose logging"
            echo "  --help                Show this help"
            echo ""
            echo "Examples:"
            echo "  bash .specify/scripts/bash/run_ralph_loop.sh --task process_all_files"
            echo "  bash .specify/scripts/bash/run_ralph_loop.sh --task process_all_files --max-iterations 5"
            echo "  bash .specify/scripts/bash/run_ralph_loop.sh --task process_all_files --dry-run"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# Validate task
if [[ -z "$TASK" ]]; then
    echo "❌ Error: --task is required"
    echo "Use --help for usage information"
    exit 1
fi

# Build command
CMD="uv run python -m src.utils.ralph_wiggum_cli --task=\"$TASK\" --max-iterations=$MAX_ITERATIONS --model=$MODEL"

if [[ "$DRY_RUN" == true ]]; then
    CMD="$CMD --dry-run"
fi

if [[ "$VERBOSE" == true ]]; then
    CMD="$CMD --verbose"
fi

# Run the command
echo "🚀 Starting Ralph Wiggum Loop..."
echo "Task: $TASK"
echo "Max Iterations: $MAX_ITERATIONS"
echo "Model: $MODEL"
echo "Dry Run: $DRY_RUN"
echo ""

eval "$CMD"
