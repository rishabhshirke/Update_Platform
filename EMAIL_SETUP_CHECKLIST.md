# Email Notification Setup Checklist

## ✅ Current Status

**What's Working:**
- ✅ Email commands created and tested
- ✅ Timezone set to IST (Asia/Kolkata)
- ✅ Automation script ready
- ✅ Settings configured with environment variables
- ✅ Test users have valid email addresses

**Test Results:**
```bash
$ python manage.py send_eod_reminders --dry-run
[DRY RUN] Would send email to: emp1@gammaedge.io
[DRY RUN] Would send email to: rishabh.shirke@gammaedge.io
Would send 2 reminder(s)
```

---

## 🚀 Setup Options

### Option A: Development Mode (Current - Emails in Console)

**Status:** Already configured ✅

**How to use:**
1. Emails will appear in your terminal/console
2. No actual emails sent
3. Perfect for testing

**Test now:**
```bash
source venv/bin/activate
python manage.py send_eod_reminders
```

You'll see the email content in your console output.

---

### Option B: Production Mode (Real Emails via Gmail)

**Setup Steps:**

#### Step 1: Get Gmail App Password

1. Go to: https://myaccount.google.com/
2. Click "Security" in left menu
3. Enable "2-Step Verification" (if not already)
4. Go back to Security
5. Click "App passwords"
6. Create new app password:
   - App: Mail
   - Device: Other (Custom name)
   - Name it: "EOD Report System"
7. Copy the 16-character password (e.g., `abcd efgh ijkl mnop`)

#### Step 2: Update .env File

Edit `/home/my/Desktop/Update_Platform/.env`:

```env
# Email Configuration for Production
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-actual-email@gmail.com
EMAIL_HOST_PASSWORD=abcdefghijklmnop
DEFAULT_FROM_EMAIL=EOD Reports <your-actual-email@gmail.com>
```

**Replace:**
- `your-actual-email@gmail.com` with your Gmail address
- `abcdefghijklmnop` with your 16-char app password (remove spaces)

#### Step 3: Test Production Emails

```bash
source venv/bin/activate

# Test with dry run first
python manage.py send_eod_reminders --dry-run

# Send actual test email
python manage.py send_eod_reminders
```

Check the recipient inboxes!

---

## ⏰ Setup Automated Scheduling

### Automatic Setup (Linux)

```bash
cd /home/my/Desktop/Update_Platform
./setup_cron.sh
```

This schedules:
- **6:00 PM IST (Mon-Fri)** - Employee reminders
- **6:30 PM IST (Mon-Fri)** - Manager notifications

### Verify Cron Jobs

```bash
# View scheduled jobs
crontab -l

# You should see:
# 0 18 * * 1-5 cd /home/my/Desktop/Update_Platform && ...
# 30 18 * * 1-5 cd /home/my/Desktop/Update_Platform && ...
```

### Manual Cron Setup

If automated setup doesn't work:

```bash
# Edit crontab
crontab -e

# Add these lines:
0 18 * * 1-5 cd /home/my/Desktop/Update_Platform && /home/my/Desktop/Update_Platform/venv/bin/python manage.py send_eod_reminders >> /home/my/Desktop/Update_Platform/logs/eod_reminders.log 2>&1

30 18 * * 1-5 cd /home/my/Desktop/Update_Platform && /home/my/Desktop/Update_Platform/venv/bin/python manage.py send_manager_notifications >> /home/my/Desktop/Update_Platform/logs/manager_notifications.log 2>&1

# Save and exit
```

---

## 📊 Monitoring Emails

### View Logs

```bash
# Real-time monitoring
tail -f logs/eod_reminders.log
tail -f logs/manager_notifications.log

# View last 50 lines
tail -n 50 logs/eod_reminders.log
```

### Check if Cron is Running

```bash
# Check cron service
sudo systemctl status cron

# View cron execution logs
grep CRON /var/log/syslog | tail -20
```

---

## 🧪 Testing Scenarios

### Test 1: Employee Without Report

1. Create a new employee (or use existing one)
2. Make sure they don't submit today's report
3. Run: `python manage.py send_eod_reminders`
4. Check console (dev) or email inbox (production)

### Test 2: Manager with Pending Reports

1. Login as employee, submit a report
2. Run: `python manage.py send_manager_notifications`
3. Manager should receive notification with report count

### Test 3: No Reminders Needed

1. All employees submit reports
2. Run: `python manage.py send_eod_reminders`
3. Should see: "All employees have submitted their reports!"

---

## 📧 Email Templates Preview

### Employee Reminder Email

```
From: EOD Reports <your-email@gmail.com>
To: emp1@gammaedge.io
Subject: Reminder: Submit Your EOD Report

Hello John Doe,

This is a friendly reminder to submit your End-of-Day (EOD)
report for October 26, 2025.

Please log in to the EOD Reporting System to submit your report.

If you have already submitted your report, please disregard
this email.

Thank you!

---
EOD Reporting System
```

### Manager Notification Email

```
From: EOD Reports <your-email@gmail.com>
To: m@gammaedge.io
Subject: Pending EOD Reports to Review (2)

Hello Manager1,

You have 2 pending EOD report(s) awaiting your review:

- John Doe (October 26, 2025)
- Jane Smith (October 25, 2025)

Please log in to the EOD Reporting System to review these reports.

Thank you!

---
EOD Reporting System
```

---

## 🎯 Quick Commands Reference

```bash
# Test employee reminders (dry run)
python manage.py send_eod_reminders --dry-run

# Test manager notifications (dry run)
python manage.py send_manager_notifications --dry-run

# Send employee reminders (actual)
python manage.py send_eod_reminders

# Send manager notifications (actual)
python manage.py send_manager_notifications

# Setup automated scheduling
./setup_cron.sh

# View scheduled cron jobs
crontab -l

# View email logs
tail -f logs/eod_reminders.log
tail -f logs/manager_notifications.log
```

---

## 🔐 Security Notes

**Never commit .env file to version control!**
- ✅ Already added to `.gitignore`
- ✅ Use `.env.example` as template
- ⚠️ Keep email passwords secure

**Gmail App Passwords:**
- Use app-specific passwords, not your regular password
- Can be revoked anytime from Google account settings
- More secure than using your main password

---

## ⚙️ Configuration Files

```
.env                    ← Your actual email credentials (NOT in git)
.env.example            ← Template file (safe to commit)
setup_cron.sh           ← Automated scheduling script
logs/
├── eod_reminders.log          ← Employee reminder logs
└── manager_notifications.log  ← Manager notification logs
```

---

## 🎬 Recommended Workflow

### For Development/Testing:
1. ✅ Keep console backend (current setup)
2. ✅ Test commands manually
3. ✅ Verify email content in console
4. ✅ DON'T set up cron yet

### For Production:
1. Configure `.env` with real email credentials
2. Test with `--dry-run` first
3. Send test emails to verify delivery
4. Run `./setup_cron.sh` to automate
5. Monitor logs for first few days
6. Adjust timing if needed

---

## 📞 Support

**Questions?**
- Review: `EMAIL_AUTOMATION_GUIDE.md` (detailed guide)
- Quick ref: `QUICK_REFERENCE.md` (commands)
- Main docs: `README.md` (complete documentation)

---

**Ready to go!** Your email notification system is fully configured and ready for both development and production use. 🎉
