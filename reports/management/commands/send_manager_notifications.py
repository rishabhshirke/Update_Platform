from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.conf import settings
from accounts.models import User
from reports.models import EODReport


class Command(BaseCommand):
    help = 'Send notifications to managers about pending reports to review'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show who would receive emails without actually sending them',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']

        # Get all managers
        managers = User.objects.filter(
            role='MANAGER',
            is_active=True
        )

        sent_count = 0
        failed_count = 0

        for manager in managers:
            # Get pending reports for this manager's team
            pending_reports = EODReport.objects.filter(
                employee__manager=manager,
                status='PENDING'
            ).select_related('employee')

            if not pending_reports.exists():
                self.stdout.write(
                    self.style.SUCCESS(f'No pending reports for manager: {manager.username}')
                )
                continue

            if not manager.email:
                self.stdout.write(
                    self.style.WARNING(f'Skipping {manager.username} - no email address')
                )
                continue

            # Prepare email
            subject = f'Pending EOD Reports to Review ({pending_reports.count()})'

            report_list = '\n'.join([
                f'- {report.employee.get_full_name()} ({report.report_date.strftime("%B %d, %Y")})'
                for report in pending_reports
            ])

            message = f"""
Hello {manager.get_full_name()},

You have {pending_reports.count()} pending EOD report(s) awaiting your review:

{report_list}

Please log in to the EOD Reporting System to review these reports:
{settings.DEFAULT_FROM_EMAIL}

Thank you!

---
EOD Reporting System
            """.strip()

            if dry_run:
                self.stdout.write(
                    self.style.WARNING(
                        f'[DRY RUN] Would send email to: {manager.email} '
                        f'({pending_reports.count()} pending reports)'
                    )
                )
                sent_count += 1
            else:
                try:
                    send_mail(
                        subject=subject,
                        message=message,
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[manager.email],
                        fail_silently=False,
                    )
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'Sent notification to: {manager.email} '
                            f'({pending_reports.count()} pending reports)'
                        )
                    )
                    sent_count += 1
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(f'Failed to send to {manager.email}: {str(e)}')
                    )
                    failed_count += 1

        # Summary
        self.stdout.write('\n' + '='*50)
        if dry_run:
            self.stdout.write(
                self.style.SUCCESS(f'[DRY RUN] Would send {sent_count} notification(s)')
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(f'Successfully sent {sent_count} notification(s)')
            )
            if failed_count > 0:
                self.stdout.write(
                    self.style.ERROR(f'Failed to send {failed_count} email(s)')
                )
