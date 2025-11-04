#!/bin/bash
# Setup script for automated EOD email notifications
# This script configures cron jobs to send daily reminders at 6 PM IST

# Get the absolute path to the project directory
PROJECT_DIR="/home/my/Desktop/Update_Platform"
VENV_PYTHON="$PROJECT_DIR/venv/bin/python"
MANAGE_PY="$PROJECT_DIR/manage.py"

echo "=================================================="
echo "EOD Report System - Email Notification Setup"
echo "=================================================="
echo ""
echo "This will set up automated email notifications:"
echo "  - Daily EOD reminders to employees at 6:00 PM IST"
echo "  - Manager notifications at 6:30 PM IST"
echo ""
echo "Project Directory: $PROJECT_DIR"
echo ""

# Check if running on Linux
if [[ "$OSTYPE" != "linux-gnu"* ]]; then
    echo "⚠️  Warning: This script is designed for Linux systems."
    echo "For other systems, please set up task scheduling manually."
    echo ""
fi

# Create a temporary cron file
CRON_FILE=$(mktemp)

# Get existing crontab (if any)
crontab -l > "$CRON_FILE" 2>/dev/null || true

# Check if cron jobs already exist
if grep -q "send_eod_reminders" "$CRON_FILE"; then
    echo "⚠️  EOD reminder cron job already exists."
    echo "Please remove existing jobs before running this script."
    echo ""
    echo "To view existing cron jobs: crontab -l"
    echo "To edit cron jobs: crontab -e"
    rm "$CRON_FILE"
    exit 1
fi

echo "Adding cron jobs..."
echo ""

# Add header comment
echo "" >> "$CRON_FILE"
echo "# EOD Report System - Automated Email Notifications" >> "$CRON_FILE"
echo "# Generated on $(date)" >> "$CRON_FILE"

# Add cron job for employee reminders at 6:00 PM IST (daily)
echo "10 16 * * 1-5 cd $PROJECT_DIR && $VENV_PYTHON $MANAGE_PY send_eod_reminders >> $PROJECT_DIR/logs/eod_reminders.log 2>&1" >> "$CRON_FILE"

# Add cron job for manager notifications at 6:30 PM IST (daily)
echo "30 18 * * 1-5 cd $PROJECT_DIR && $VENV_PYTHON $MANAGE_PY send_manager_notifications >> $PROJECT_DIR/logs/manager_notifications.log 2>&1" >> "$CRON_FILE"

echo "" >> "$CRON_FILE"

# Install the new crontab
crontab "$CRON_FILE"

# Clean up
rm "$CRON_FILE"

# Create logs directory if it doesn't exist
mkdir -p "$PROJECT_DIR/logs"

echo "✅ Cron jobs installed successfully!"
echo ""
echo "Scheduled jobs:"
echo "  📧 Employee EOD Reminders: 6:00 PM IST (Mon-Fri)"
echo "  📧 Manager Notifications:  6:30 PM IST (Mon-Fri)"
echo ""
echo "Logs will be saved to: $PROJECT_DIR/logs/"
echo ""
echo "To view your cron jobs:"
echo "  crontab -l"
echo ""
echo "To remove cron jobs:"
echo "  crontab -e  (then delete the EOD Report System lines)"
echo ""
echo "To test manually:"
echo "  python manage.py send_eod_reminders --dry-run"
echo "  python manage.py send_manager_notifications --dry-run"
echo ""
echo "=================================================="
