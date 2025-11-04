# EOD Report System

A comprehensive web-based End-of-Day (EOD) reporting system built with Django. This application allows employees to submit daily reports and managers to review and approve them.

## Features

- **User Authentication & Role-Based Access**
  - Employee, Manager, and Admin roles
  - Secure login/logout functionality
  - User profile management

- **Employee Features**
  - Submit daily EOD reports
  - Track tasks completed, hours worked, blockers, and next-day plans
  - Edit same-day reports
  - View report history with filtering
  - Visual dashboard with statistics

- **Manager Features**
  - Review team members' reports
  - Approve or reject reports with comments
  - Filter and search reports by date, status, and employee
  - Dashboard with pending reports count

- **Email Notifications**
  - Daily reminders for employees who haven't submitted reports
  - Notifications to managers about pending reviews
  - Configurable email settings

- **Admin Panel**
  - Comprehensive Django admin interface
  - User management with role assignment
  - Bulk operations on reports
  - Advanced filtering and search

## Technology Stack

- **Backend**: Django 4.2.11
- **Frontend**: Bootstrap 5, HTML5, CSS3
- **Database**: SQLite (development) / PostgreSQL (production-ready)
- **Forms**: Django Crispy Forms with Bootstrap 4
- **Email**: Django email backend (console for dev, SMTP for production)

## Installation

### Prerequisites

- Python 3.8+
- pip
- virtualenv (recommended)

### Setup Instructions

1. **Clone or navigate to the project directory**
   ```bash
   cd /home/my/Desktop/Update_Platform
   ```

2. **Create and activate virtual environment** (already done)
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies** (already done)
   ```bash
   pip install -r requirements.txt
   ```

4. **Run migrations** (already done)
   ```bash
   python manage.py migrate
   ```

5. **Create a superuser**
   ```bash
   python manage.py createsuperuser
   ```
   Follow the prompts to create an admin account.

6. **Run the development server**
   ```bash
   python manage.py runserver
   ```

7. **Access the application**
   - Main application: http://127.0.0.1:8000/
   - Admin panel: http://127.0.0.1:8000/admin/

## Usage

### Initial Setup

1. **Create a Superuser** (if not already done)
   ```bash
   python manage.py createsuperuser
   ```

2. **Access Admin Panel**
   - Log in at http://127.0.0.1:8000/admin/
   - Use your superuser credentials

3. **Create Users**
   - In the admin panel, create users with appropriate roles:
     - **Admin**: Full system access
     - **Manager**: Can review team reports
     - **Employee**: Can submit reports

4. **Assign Managers to Employees**
   - Edit employee users and assign them to a manager
   - This is required for the reporting workflow

### User Registration (Self-Registration)

1. **New users can register** at http://127.0.0.1:8000/accounts/register/
2. **Fill in registration details**
   - Username, email, password
   - First/last name, department (optional)
3. **Account pending approval**
   - New accounts are created as **inactive** by default
   - Users cannot login until activated by an administrator

### Activating New Users (Admin)

When a new user registers:
1. **Login to admin panel** at http://127.0.0.1:8000/admin/
2. **Go to Users** and find the new user (filter by "Active" = No)
3. **Edit the user** and:
   - Assign a **Manager** (required for employees)
   - Check **Active** status
   - Set **Role** if needed (defaults to Employee)
   - Save the user
4. **Notify the user** that their account is now active

### For Employees

1. **Login** at http://127.0.0.1:8000/accounts/login/
   - Use your activated account credentials
2. **Submit EOD Report**
   - **⚠️ Weekday Dates Only**: Reports can only be for weekday dates (Monday-Friday)
   - You CAN access the system on weekends to submit reports for past weekdays
   - You CANNOT submit reports for Saturday/Sunday dates
   - Click "Submit Report" in the navigation
   - Fill in:
     - Report Date (must be a Monday-Friday date)
     - Project Name (defaults to "Trainee")
     - Tasks completed
     - Hours worked
     - Blockers/issues (optional)
     - Next day plan
   - Submit the report
3. **Edit Reports**
   - Reports can only be edited on the same day they were submitted
   - **Important**: Once a report is approved or rejected by a manager, it cannot be edited
   - Pending reports can be edited until end of day
   - Report dates must be weekdays (Monday-Friday)
4. **View Reports**
   - Dashboard shows recent reports with status
   - "My Reports" shows complete history with filters

### For Managers

1. **Login** at http://127.0.0.1:8000/accounts/login/
2. **Review Reports**
   - Manager Dashboard shows all team reports
   - Filter by date, status, or employee
   - Click "Review" on **pending** reports only
3. **Approve/Reject Reports**
   - View report details
   - Add comments (optional)
   - Select "Approve" or "Reject"
   - Submit review
   - **⚠️ Important**: Once submitted, reviews are **FINAL** and cannot be edited
4. **View Reviewed Reports**
   - Approved/rejected reports show "Final" badge
   - Review button is disabled
   - Can only view details, cannot modify decision

### Email Notifications (Automated)

#### ⚡ Quick Setup (Automated - Recommended)

Set up automated daily emails at **6:00 PM IST**:

```bash
# Run the automated setup script
./setup_cron.sh
```

This will configure:
- ✅ **6:00 PM IST** - Employee EOD reminders (Mon-Fri)
- ✅ **6:30 PM IST** - Manager notifications (Mon-Fri)
- ✅ Log files in `logs/` directory

For detailed configuration and troubleshooting, see **[EMAIL_AUTOMATION_GUIDE.md](EMAIL_AUTOMATION_GUIDE.md)**

#### 🧪 Manual Testing

Test without sending emails:
```bash
python manage.py send_eod_reminders --dry-run
python manage.py send_manager_notifications --dry-run
```

Send test emails (appears in console in dev mode):
```bash
python manage.py send_eod_reminders
python manage.py send_manager_notifications
```

#### Configure Email Settings

For production, update `eod_project/settings.py`:

```python
# Comment out the console backend
# EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Uncomment and configure SMTP settings
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'  # Your SMTP server
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your-email@example.com'
EMAIL_HOST_PASSWORD = 'your-app-password'
DEFAULT_FROM_EMAIL = 'noreply@yourcompany.com'
```

## Project Structure

```
Update_Platform/
├── accounts/                 # User authentication and management
│   ├── models.py            # Custom User model with roles
│   ├── views.py             # Login, register, profile views
│   ├── forms.py             # Authentication forms
│   └── admin.py             # User admin configuration
├── reports/                  # EOD reporting functionality
│   ├── models.py            # EODReport and ReportReview models
│   ├── views.py             # Dashboard and report views
│   ├── forms.py             # Report submission and review forms
│   ├── admin.py             # Report admin configuration
│   └── management/
│       └── commands/        # Email notification commands
├── templates/               # HTML templates
│   ├── base.html           # Base template with navigation
│   ├── accounts/           # Authentication templates
│   └── reports/            # Report-related templates
├── static/                  # Static files (CSS, JS, images)
├── eod_project/            # Main project settings
│   ├── settings.py         # Django settings
│   └── urls.py             # URL configuration
├── manage.py               # Django management script
└── requirements.txt        # Python dependencies
```

## Database Models

### User Model (accounts.User)
- Extends Django's AbstractUser
- Fields: username, email, role, department, manager, phone_number
- Roles: EMPLOYEE, MANAGER, ADMIN

### EODReport Model (reports.EODReport)
- Fields: employee, report_date, tasks_completed, hours_worked, blockers_issues, next_day_plan, status
- Status: PENDING, APPROVED, REJECTED
- Unique constraint: one report per employee per date

### ReportReview Model (reports.ReportReview)
- Fields: report, reviewer, comments, reviewed_at
- One-to-one relationship with EODReport

## Scheduling Email Notifications (Production)

### Using Cron (Linux/Mac)

Edit crontab:
```bash
crontab -e
```

Add these lines:
```cron
# Send employee reminders at 5 PM daily
0 17 * * * cd /path/to/Update_Platform && /path/to/venv/bin/python manage.py send_eod_reminders

# Send manager notifications at 6 PM daily
0 18 * * * cd /path/to/Update_Platform && /path/to/venv/bin/python manage.py send_manager_notifications
```

### Using Windows Task Scheduler

Create batch files and schedule them in Task Scheduler.

## Security Notes

⚠️ **Important for Production**:

1. **Change SECRET_KEY** in settings.py
2. **Set DEBUG = False**
3. **Configure ALLOWED_HOSTS**
4. **Use PostgreSQL** instead of SQLite
5. **Set up HTTPS**
6. **Use environment variables** for sensitive settings
7. **Configure proper email credentials**

## Troubleshooting

### Issue: "Account is pending approval" message when trying to login
**Solution**:
- This message appears when your account is **inactive** (not yet approved by admin)
- New registrations are **inactive by default** for security
- **What you see**: Warning message: "Your account is pending approval. Please contact your administrator to activate your account."
- **Action needed**: Contact your administrator to activate your account
- **Admin must**:
  1. Go to admin panel → Users
  2. Find your user account
  3. Assign a manager (for employees)
  4. Check the "Active" status box
  5. Save
- Once activated, you can login normally

### Issue: Can't login after registration
**Solution**:
- Same as above - your account needs admin approval

### Issue: "Manager must be assigned to employees" in admin
**Solution**:
- This only applies to **active** employees
- Either assign a manager before activating, or
- Keep the user inactive until a manager is assigned

### Issue: Manager cannot change review decision
**Solution**:
- **This is by design** - Reviews are final once submitted
- Prevents accidental changes to approved/rejected reports
- If you need to change a decision, contact your system administrator
- Admins can modify status through the admin panel if absolutely necessary

### Issue: Email notifications not working
**Solution**:
- For development, check console output (emails appear in terminal)
- For production, verify SMTP settings and credentials
- Test with `--dry-run` flag first

### Issue: Permission denied errors
**Solution**: Ensure proper file permissions and database access

## Development

### Running Tests
```bash
python manage.py test
```

### Creating Sample Data
Use the admin panel to create test users and reports, or create a custom management command for seed data.

### Customization
- Modify templates in `templates/` directory
- Add custom CSS in `static/css/`
- Extend models in respective `models.py` files

## Support

For issues or questions:
1. Check the troubleshooting section
2. Review Django documentation: https://docs.djangoproject.com/
3. Check application logs

## License

This project is proprietary software for internal organizational use.

## Contributors

Developed for organizational EOD reporting needs.

---

**Version**: 1.0.0
**Last Updated**: 2025
