#!/bin/bash
# view-logs.sh - View logs in real-time
echo "📋 Viewing logs (Ctrl+C to exit)..."
tail -f logs/*.log 2>/dev/null || echo "No logs found. Start a service first."
