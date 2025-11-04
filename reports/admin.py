from django.contrib import admin
from .models import EODReport, ReportReview


class ReportReviewInline(admin.StackedInline):
    """Inline admin for report reviews"""
    model = ReportReview
    extra = 0
    can_delete = False
    fields = ['reviewer', 'comments', 'reviewed_at']
    readonly_fields = ['reviewed_at']


@admin.register(EODReport)
class EODReportAdmin(admin.ModelAdmin):
    """Admin for EOD Reports"""

    list_display = ['employee', 'report_date', 'project_name', 'hours_worked', 'status', 'submitted_at']
    list_filter = ['status', 'report_date', 'employee__department', 'project_name']
    search_fields = ['employee__username', 'employee__first_name', 'employee__last_name', 'project_name', 'tasks_completed']
    date_hierarchy = 'report_date'
    ordering = ['-report_date', '-submitted_at']
    readonly_fields = ['submitted_at', 'updated_at']

    fieldsets = (
        ('Employee Information', {
            'fields': ('employee', 'report_date', 'status')
        }),
        ('Report Details', {
            'fields': ('project_name', 'tasks_completed', 'hours_worked', 'blockers_issues', 'next_day_plan')
        }),
        ('Timestamps', {
            'fields': ('submitted_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    inlines = [ReportReviewInline]

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('employee', 'employee__manager')

    actions = ['approve_reports', 'reject_reports']

    def approve_reports(self, request, queryset):
        updated = queryset.update(status='APPROVED')
        self.message_user(request, f'{updated} report(s) approved successfully.')
    approve_reports.short_description = 'Approve selected reports'

    def reject_reports(self, request, queryset):
        updated = queryset.update(status='REJECTED')
        self.message_user(request, f'{updated} report(s) rejected.')
    reject_reports.short_description = 'Reject selected reports'


@admin.register(ReportReview)
class ReportReviewAdmin(admin.ModelAdmin):
    """Admin for Report Reviews"""

    list_display = ['report', 'reviewer', 'reviewed_at']
    list_filter = ['reviewed_at', 'reviewer']
    search_fields = ['report__employee__username', 'reviewer__username', 'comments']
    date_hierarchy = 'reviewed_at'
    readonly_fields = ['reviewed_at']

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('report', 'report__employee', 'reviewer')
