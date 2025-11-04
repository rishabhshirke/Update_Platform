# Quick Start Guide - EOD Report System

## Getting Started in 5 Minutes

### 1. Create a Superuser
```bash
source venv/bin/activate  # Activate virtual environment
python manage.py createsuperuser
```
Enter username, email, and password when prompted.

### 2. Start the Server
```bash
python manage.py runserver
```

### 3. Access the Admin Panel
Open browser: http://127.0.0.1:8000/admin/
Login with your superuser credentials.

### 4. Create Test Users

**Create a Manager:**
1. Go to Users → Add User
2. Username: `manager1`
3. Password: (set password)
4. Save and continue editing
5. Set:
   - First name: John
   - Last name: Manager
   - Email: manager@example.com
   - Role: **Manager**
   - Department: Engineering
   - Staff status: ✓ (checked)
6. Save

**Create an Employee:**

*Option 1: Via Admin Panel*
1. Go to Users → Add User
2. Username: `employee1`
3. Password: (set password)
4. Save and continue editing
5. Set:
   - First name: Jane
   - Last name: Employee
   - Email: employee@example.com
   - Role: **Employee**
   - Department: Engineering
   - Manager: **Select manager1**
   - Active: ✓ (checked)
6. Save

*Option 2: Via Self-Registration*
1. Logout from admin
2. Go to: http://127.0.0.1:8000/accounts/register/
3. Fill in registration form
4. After registration, login to admin panel
5. Go to Users → find the new user
6. Edit and set:
   - Manager: **Select manager1**
   - Active: ✓ (checked)
7. Save

### 5. Test the Application

**As Employee:**
1. Logout from admin
2. Go to: http://127.0.0.1:8000/
3. Login as `employee1`
4. Click "Submit Report"
5. Fill in the EOD report form:
   - Tasks: "Completed feature X, Fixed bug Y"
   - Hours: 8
   - Blockers: "None"
   - Next Day: "Will work on feature Z"
6. Submit

**As Manager:**
1. Logout
2. Login as `manager1`
3. You'll see the Manager Dashboard
4. Click "Review" on the pending report
5. Add comments and Approve/Reject

## Email Notifications (Development)

Emails will appear in your console/terminal where the server is running.

### Send Test Reminder
```bash
python manage.py send_eod_reminders --dry-run
```

### Send Test Manager Notification
```bash
python manage.py send_manager_notifications --dry-run
```

Remove `--dry-run` to actually send (they'll appear in console in development).

## Common Tasks

### Reset Database (Start Fresh)
```bash
rm db.sqlite3
python manage.py migrate
python manage.py createsuperuser
```

### View All URLs
```bash
python manage.py show_urls
```

### Run Development Server on Different Port
```bash
python manage.py runserver 8080
```

### Access from Other Devices (same network)
```bash
python manage.py runserver 0.0.0.0:8000
```

## Troubleshooting

**Issue: Can't login after self-registration**
- New accounts are **inactive by default**
- Login to admin panel and activate the user:
  1. Users → find your account
  2. Assign a manager
  3. Check "Active" box
  4. Save

**Issue: Can't login as employee**
- Make sure you assigned a manager to the employee in admin panel
- Check that the user is marked as "Active"

**Issue: Server won't start**
- Check if port 8000 is already in use
- Try: `python manage.py runserver 8080`

**Issue: Templates not loading**
- Run: `python manage.py collectstatic` (if needed)
- Check TEMPLATES setting in settings.py

## Next Steps

1. Customize the application
2. Add more users
3. Configure email for production (see README.md)
4. Set up scheduled tasks for email notifications
5. Deploy to production server

For detailed information, see [README.md](README.md)
