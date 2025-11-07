from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from datetime import timedelta


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
    resubmission_count = models.IntegerField(
        default=0,
        help_text='Number of times this report has been resubmitted after rejection (max 3)'
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
        """
        Check if report can still be edited:
        - PENDING reports: can be edited anytime until reviewed
        - REJECTED reports: within 7 days of last review and under 3 resubmissions
        - APPROVED reports: cannot be edited
        """
        if self.status == 'PENDING':
            # Pending reports can be edited anytime until manager reviews them
            return True
        elif self.status == 'REJECTED':
            # Rejected reports can be edited within 7 days and under 3 attempts
            if self.resubmission_count >= 3:
                return False
            # Check if within 7 days of last review
            try:
                last_review = self.reviews.latest('reviewed_at')
                days_since_review = (timezone.now() - last_review.reviewed_at).days
                return days_since_review <= 7
            except ReportReview.DoesNotExist:
                return False
        return False

    def is_pending(self):
        return self.status == 'PENDING'

    def is_approved(self):
        return self.status == 'APPROVED'

    def is_rejected(self):
        return self.status == 'REJECTED'

    def remaining_resubmissions(self):
        """Returns the number of resubmissions remaining (max 3 total)"""
        return max(0, 3 - self.resubmission_count)


class ReportReview(models.Model):
    """
    Manager's review and comments on EOD reports
    Supports multiple reviews per report for resubmissions
    """
    report = models.ForeignKey(
        EODReport,
        on_delete=models.CASCADE,
        related_name='reviews'
    )
    reviewer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='reviews_given',
        limit_choices_to={'role__in': ['MANAGER', 'ADMIN']}
    )
    review_number = models.IntegerField(
        default=1,
        help_text='Review iteration number (1st review, 2nd review, etc.)'
    )
    comments = models.TextField(
        blank=True,
        null=True,
        help_text='Manager feedback and comments'
    )
    reviewed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-reviewed_at']
        verbose_name = 'Report Review'
        verbose_name_plural = 'Report Reviews'
        unique_together = ['report', 'review_number']

    def __str__(self):
        return f"Review by {self.reviewer.get_full_name()} for {self.report}"
