from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from accounts.models import User
from reports.models import EODReport


class Command(BaseCommand):
    help = 'Send email reminders to employees who have not submitted EOD reports'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show who would receive emails without actually sending them',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        today = timezone.now().date()

        # Get all active employees
        employees = User.objects.filter(
            role='EMPLOYEE',
            is_active=True
        )

        # Filter employees who haven't submitted reports today
        employees_without_report = []
        for employee in employees:
            if not EODReport.objects.filter(
                employee=employee,
                report_date=today
            ).exists():
                employees_without_report.append(employee)

        if not employees_without_report:
            self.stdout.write(self.style.SUCCESS('All employees have submitted their reports!'))
            return

        # Send reminders
        sent_count = 0
        failed_count = 0

        for employee in employees_without_report:
            if not employee.email:
                self.stdout.write(
                    self.style.WARNING(f'Skipping {employee.username} - no email address')
                )
                continue

            subject = 'Reminder: Submit Your EOD Report'
            message = f"""
Hello {employee.get_full_name()},

This is a friendly reminder to submit your End-of-Day (EOD) report for {today.strftime('%B %d, %Y')}.

Please log in to the EOD Reporting System to submit your report:
{settings.DEFAULT_FROM_EMAIL}

If you have already submitted your report, please disregard this email.

Thank you!

---
EOD Reporting System
            """.strip()

            if dry_run:
                self.stdout.write(
                    self.style.WARNING(f'[DRY RUN] Would send email to: {employee.email}')
                )
                sent_count += 1
            else:
                try:
                    send_mail(
                        subject=subject,
                        message=message,
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[employee.email],
                        fail_silently=False,
                    )
                    self.stdout.write(
                        self.style.SUCCESS(f'Sent reminder to: {employee.email}')
                    )
                    sent_count += 1
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(f'Failed to send to {employee.email}: {str(e)}')
                    )
                    failed_count += 1

        # Summary
        self.stdout.write('\n' + '='*50)
        if dry_run:
            self.stdout.write(
                self.style.SUCCESS(f'[DRY RUN] Would send {sent_count} reminder(s)')
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(f'Successfully sent {sent_count} reminder(s)')
            )
            if failed_count > 0:
                self.stdout.write(
                    self.style.ERROR(f'Failed to send {failed_count} email(s)')
                )
