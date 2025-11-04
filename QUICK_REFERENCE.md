# Quick Reference - EOD Report System

## 🚀 Setup Automated Emails at 6 PM IST

### One-Command Setup
```bash
./setup_cron.sh
```

That's it! Emails will be sent automatically:
- **6:00 PM IST** - Employee reminders (Mon-Fri)
- **6:30 PM IST** - Manager notifications (Mon-Fri)

---

## 📧 Email Configuration for Production

### Step 1: Configure Email Settings

```bash
# Copy the example file
cp .env.example .env

# Edit with your email credentials
nano .env
```

### Step 2: Add Your Email Credentials

In `.env` file:
```env
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-company@gmail.com
EMAIL_HOST_PASSWORD=your-gmail-app-password
DEFAULT_FROM_EMAIL=EOD Reports <your-company@gmail.com>
```

### Step 3: Update settings.py

Edit `eod_project/settings.py`:

```python
from decouple import config

# Change from console to SMTP
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = config('EMAIL_HOST')
EMAIL_PORT = config('EMAIL_PORT', cast=int)
EMAIL_USE_TLS = True
EMAIL_HOST_USER = config('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD')
DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL')
```

---

## 🧪 Testing Emails

### Test Without Sending (Dry Run)
```bash
python manage.py send_eod_reminders --dry-run
python manage.py send_manager_notifications --dry-run
```

### Send Test Emails
```bash
# Development (appears in console)
python manage.py send_eod_reminders

# Production (sends real emails)
python manage.py send_eod_reminders
```

---

## 📊 View Scheduled Jobs

### Check Cron Jobs
```bash
crontab -l
```

### View Email Logs
```bash
# Live monitoring
tail -f logs/eod_reminders.log
tail -f logs/manager_notifications.log

# View last 50 lines
tail -n 50 logs/eod_reminders.log
```

---

## 🔧 Manage Cron Jobs

### Edit Schedule
```bash
crontab -e
```

### Remove All Jobs
```bash
crontab -r
```

### Change Email Time

Edit crontab and change the hour:
```bash
# 5:00 PM IST
0 17 * * 1-5 cd /home/my/Desktop/Update_Platform && ...

# 6:00 PM IST (current)
0 18 * * 1-5 cd /home/my/Desktop/Update_Platform && ...

# 7:00 PM IST
0 19 * * 1-5 cd /home/my/Desktop/Update_Platform && ...
```

---

## 🎯 Who Gets Emails?

### Employee Reminders
- **Recipients**: Active employees who haven't submitted today's report
- **Time**: 6:00 PM IST (Mon-Fri)
- **Content**: Reminder to submit EOD report

### Manager Notifications
- **Recipients**: Active managers with pending reports to review
- **Time**: 6:30 PM IST (Mon-Fri)
- **Content**: List of pending reports from their team

---

## 📝 Gmail App Password Setup

1. Go to https://myaccount.google.com/
2. Security → 2-Step Verification → Enable it
3. Security → App Passwords
4. Select "Mail" and "Other (Custom name)"
5. Enter "EOD Report System"
6. Copy the 16-character password
7. Use this in `.env` file as `EMAIL_HOST_PASSWORD`

---

## 🎓 User Credentials Reference

### Manager Login
```
Username: Manager1
Password: Manager@123
URL: http://127.0.0.1:8000/accounts/login/
```

### Employee Login
```
Username: EMP1
Password: Emp@1234
URL: http://127.0.0.1:8000/accounts/login/
```

### Admin Panel
```
Username: Rishabh
URL: http://127.0.0.1:8000/admin/
```

---

## 📚 Documentation Files

- **README.md** - Complete documentation
- **QUICKSTART.md** - 5-minute quick start
- **EMAIL_AUTOMATION_GUIDE.md** - Detailed email setup
- **QUICK_REFERENCE.md** - This file (quick commands)

---

## 🆘 Common Commands

```bash
# Start server
python manage.py runserver

# Create superuser
python manage.py createsuperuser

# Run migrations
python manage.py migrate

# Test email notifications
python manage.py send_eod_reminders --dry-run

# Setup automated emails
./setup_cron.sh

# View cron jobs
crontab -l

# View email logs
tail -f logs/eod_reminders.log
```

---

**Last Updated**: October 2025
**Timezone**: Asia/Kolkata (IST)
