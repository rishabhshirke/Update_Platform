# Email Automation Guide - EOD Report System

This guide explains how to set up automated daily email notifications at **6:00 PM IST**.

## Overview

The system sends two types of automated emails:
1. **Employee Reminders** (6:00 PM IST) - To employees who haven't submitted EOD reports
2. **Manager Notifications** (6:30 PM IST) - To managers with pending reports to review

---

## Quick Setup (Linux/Mac)

### Automatic Setup

Run the provided setup script:

```bash
cd /home/my/Desktop/Update_Platform
./setup_cron.sh
```

This will automatically:
- ✅ Configure cron jobs for 6:00 PM and 6:30 PM IST
- ✅ Set up log files
- ✅ Schedule Monday-Friday execution only

### Manual Setup

If you prefer manual setup:

```bash
# Open crontab editor
crontab -e

# Add these lines (adjust paths as needed):
# Employee reminders at 6:00 PM IST (Mon-Fri)
0 18 * * 1-5 cd /home/my/Desktop/Update_Platform && /home/my/Desktop/Update_Platform/venv/bin/python manage.py send_eod_reminders >> /home/my/Desktop/Update_Platform/logs/eod_reminders.log 2>&1

# Manager notifications at 6:30 PM IST (Mon-Fri)
30 18 * * 1-5 cd /home/my/Desktop/Update_Platform && /home/my/Desktop/Update_Platform/venv/bin/python manage.py send_manager_notifications >> /home/my/Desktop/Update_Platform/logs/manager_notifications.log 2>&1
```

---

## Understanding Cron Schedule

```
0 18 * * 1-5
│  │  │ │ │
│  │  │ │ └─── Day of week (1-5 = Mon-Fri)
│  │  │ └───── Month (1-12)
│  │  └─────── Day of month (1-31)
│  └────────── Hour (18 = 6 PM)
└───────────── Minute (0 = :00)
```

- `0 18 * * 1-5` = 6:00 PM, Monday through Friday
- `30 18 * * 1-5` = 6:30 PM, Monday through Friday

---

## Testing Email Notifications

### Test Without Sending (Dry Run)

```bash
# Activate virtual environment
source venv/bin/activate

# Test employee reminders
python manage.py send_eod_reminders --dry-run

# Test manager notifications
python manage.py send_manager_notifications --dry-run
```

### Send Actual Emails (Development Mode)

```bash
# Send employee reminders
python manage.py send_eod_reminders

# Send manager notifications
python manage.py send_manager_notifications
```

**Note**: In development mode (current setup), emails appear in the console/terminal, not actual inboxes.

---

## Production Email Configuration

### Step 1: Configure SMTP Settings

Edit `eod_project/settings.py`:

```python
# Replace console backend with SMTP
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

# Gmail Example (recommended: use App Password)
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your-company-email@gmail.com'
EMAIL_HOST_PASSWORD = 'your-app-password'  # Use App Password, not regular password
DEFAULT_FROM_EMAIL = 'EOD Reports <your-company-email@gmail.com>'

# Or use your company's SMTP server
# EMAIL_HOST = 'smtp.yourcompany.com'
# EMAIL_PORT = 587
# EMAIL_USE_TLS = True
# EMAIL_HOST_USER = 'noreply@yourcompany.com'
# EMAIL_HOST_PASSWORD = 'secure-password'
```

### Step 2: Set Up Gmail App Password (if using Gmail)

1. Go to Google Account Settings
2. Enable 2-Factor Authentication
3. Go to Security → App Passwords
4. Generate a new app password for "Mail"
5. Use this 16-character password in `EMAIL_HOST_PASSWORD`

### Step 3: Security Best Practices

**Use Environment Variables** (Recommended):

1. Install python-decouple (already in requirements.txt)

2. Create `.env` file in project root:
   ```bash
   # Email Configuration
   EMAIL_HOST=smtp.gmail.com
   EMAIL_PORT=587
   EMAIL_HOST_USER=your-email@gmail.com
   EMAIL_HOST_PASSWORD=your-app-password
   DEFAULT_FROM_EMAIL=EOD Reports <your-email@gmail.com>
   ```

3. Update `settings.py`:
   ```python
   from decouple import config

   EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
   EMAIL_HOST = config('EMAIL_HOST', default='smtp.gmail.com')
   EMAIL_PORT = config('EMAIL_PORT', default=587, cast=int)
   EMAIL_USE_TLS = True
   EMAIL_HOST_USER = config('EMAIL_HOST_USER')
   EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD')
   DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL')
   ```

4. Add `.env` to `.gitignore` (already done)

---

## Viewing Logs

### Check Email Logs

```bash
# View employee reminder logs
tail -f logs/eod_reminders.log

# View manager notification logs
tail -f logs/manager_notifications.log

# View last 50 lines
tail -n 50 logs/eod_reminders.log
```

### Log Location

Logs are saved to:
- `logs/eod_reminders.log` - Employee reminder logs
- `logs/manager_notifications.log` - Manager notification logs

---

## Managing Cron Jobs

### View Scheduled Jobs

```bash
crontab -l
```

### Edit Cron Jobs

```bash
crontab -e
```

### Remove All Cron Jobs

```bash
crontab -r
```

### Temporarily Disable

Comment out the line in crontab (add `#` at the beginning):
```bash
# 0 18 * * 1-5 cd /home/my/Desktop/Update_Platform && ...
```

---

## How It Works

### Employee Reminder Flow

1. **6:00 PM IST** - Cron triggers `send_eod_reminders` command
2. System checks all active employees
3. Identifies employees without today's report
4. Sends reminder email to each employee
5. Logs results to `logs/eod_reminders.log`

### Manager Notification Flow

1. **6:30 PM IST** - Cron triggers `send_manager_notifications` command
2. System checks all active managers
3. Counts pending reports for each manager's team
4. Sends summary email to managers with pending reports
5. Logs results to `logs/manager_notifications.log`

---

## Email Templates

### Employee Reminder Email

```
Subject: Reminder: Submit Your EOD Report

Hello [Employee Name],

This is a friendly reminder to submit your End-of-Day (EOD) report
for October 25, 2025.

Please log in to the EOD Reporting System to submit your report.

If you have already submitted your report, please disregard this email.

Thank you!

---
EOD Reporting System
```

### Manager Notification Email

```
Subject: Pending EOD Reports to Review (3)

Hello [Manager Name],

You have 3 pending EOD report(s) awaiting your review:

- John Doe (October 25, 2025)
- Jane Smith (October 25, 2025)
- Bob Johnson (October 24, 2025)

Please log in to the EOD Reporting System to review these reports.

Thank you!

---
EOD Reporting System
```

---

## Troubleshooting

### Cron Jobs Not Running

**Check if cron service is running:**
```bash
sudo systemctl status cron
```

**Start cron service:**
```bash
sudo systemctl start cron
```

**View cron logs:**
```bash
grep CRON /var/log/syslog
```

### Emails Not Sending

1. **Check SMTP settings** in `settings.py`
2. **Verify credentials** are correct
3. **Check firewall** allows outbound port 587
4. **Review error logs** in `logs/` directory
5. **Test manually**:
   ```bash
   python manage.py send_eod_reminders
   ```

### Permission Denied

```bash
chmod +x setup_cron.sh
chmod +x manage.py
```

### Python Path Issues

Make sure to use absolute paths in cron:
```bash
/home/my/Desktop/Update_Platform/venv/bin/python manage.py send_eod_reminders
```

---

## Advanced Configuration

### Change Email Time

Edit cron schedule:
```bash
# Change to 5:30 PM IST
30 17 * * 1-5 cd /home/my/Desktop/Update_Platform && ...

# Change to 7:00 PM IST
0 19 * * 1-5 cd /home/my/Desktop/Update_Platform && ...
```

### Send on Specific Days Only

```bash
# Monday, Wednesday, Friday only
0 18 * * 1,3,5 cd /home/my/Desktop/Update_Platform && ...

# Every day including weekends
0 18 * * * cd /home/my/Desktop/Update_Platform && ...
```

### Multiple Reminders Per Day

```bash
# Morning reminder at 10 AM
0 10 * * 1-5 cd /home/my/Desktop/Update_Platform && ...

# Afternoon reminder at 3 PM
0 15 * * 1-5 cd /home/my/Desktop/Update_Platform && ...

# Evening reminder at 6 PM
0 18 * * 1-5 cd /home/my/Desktop/Update_Platform && ...
```

---

## Windows Setup (Alternative)

### Using Windows Task Scheduler

1. Open Task Scheduler
2. Create New Task
3. **Trigger**: Daily at 6:00 PM
4. **Action**: Start a program
   - Program: `C:\path\to\Update_Platform\venv\Scripts\python.exe`
   - Arguments: `manage.py send_eod_reminders`
   - Start in: `C:\path\to\Update_Platform`
5. **Conditions**: Run only if computer is on
6. Save and test

---

## Production Deployment Checklist

- [ ] Update timezone to IST in `settings.py`
- [ ] Configure SMTP email settings
- [ ] Use environment variables for email credentials
- [ ] Set up cron jobs using `setup_cron.sh`
- [ ] Create `logs/` directory with proper permissions
- [ ] Test emails with `--dry-run` flag
- [ ] Send test emails to verify delivery
- [ ] Monitor logs for first few days
- [ ] Set up log rotation for large log files
- [ ] Document company-specific SMTP settings
- [ ] Train admins on managing cron jobs

---

## Support

For issues or questions:
- Check logs in `logs/` directory
- Review cron jobs with `crontab -l`
- Test manually with management commands
- Verify email settings in `settings.py`

---

**Generated**: 2025-10-26
**Timezone**: Asia/Kolkata (IST)
**Version**: 1.0
