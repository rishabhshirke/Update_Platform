from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone


class EODReport(models.Model):
    """
    End-of-Day Report Model
    Tracks daily employee reports with tasks, hours, blockers, and plans
    """
    STATUS_CHOICES = (
        ('PENDING', 'Pending Review'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
    )

    employee = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='eod_reports',
        limit_choices_to={'role': 'EMPLOYEE'}
    )
    report_date = models.DateField(
        default=timezone.now,
        help_text='Date for which this report is submitted'
    )
    project_name = models.CharField(
        max_length=200,
        default='Trainee',
        help_text='Project or task name you worked on'
    )

    # Report Fields
    tasks_completed = models.TextField(
        help_text='List of tasks/activities completed today'
    )
    hours_worked = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(24)],
        help_text='Total hours worked today'
    )
    blockers_issues = models.TextField(
        blank=True,
        null=True,
        help_text='Any blockers or issues encountered'
    )
    next_day_plan = models.TextField(
        help_text='Plan for tomorrow'
    )

    # Status and metadata
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='PENDING'
    )
    submitted_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-report_date', '-submitted_at']
        unique_together = ['employee', 'report_date']
        verbose_name = 'EOD Report'
        verbose_name_plural = 'EOD Reports'
        indexes = [
            models.Index(fields=['-report_date']),
            models.Index(fields=['employee', '-report_date']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return f"{self.employee.get_full_name()} - {self.report_date}"

    def can_edit(self):
        """Check if report can still be edited (same day submission and not approved/rejected)"""
        return self.report_date == timezone.now().date() and self.status == 'PENDING'

    def is_pending(self):
        return self.status == 'PENDING'

    def is_approved(self):
        return self.status == 'APPROVED'

    def is_rejected(self):
        return self.status == 'REJECTED'


class ReportReview(models.Model):
    """
    Manager's review and comments on EOD reports
    """
    report = models.OneToOneField(
        EODReport,
        on_delete=models.CASCADE,
        related_name='review'
    )
    reviewer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='reviews_given',
        limit_choices_to={'role__in': ['MANAGER', 'ADMIN']}
    )
    comments = models.TextField(
        blank=True,
        null=True,
        help_text='Manager feedback and comments'
    )
    reviewed_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-reviewed_at']
        verbose_name = 'Report Review'
        verbose_name_plural = 'Report Reviews'

    def __str__(self):
        return f"Review by {self.reviewer.get_full_name()} for {self.report}"
