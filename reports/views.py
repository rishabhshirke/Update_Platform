from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q, Count, Avg
from datetime import timedelta
from .models import EODReport, ReportReview
from .forms import EODReportForm, ReportReviewForm, EODReportFilterForm
from .utils import get_week_date_range, is_weekend, get_week_display


@login_required
def dashboard_view(request):
    """Main dashboard - redirects based on user role"""
    if request.user.is_manager() or request.user.is_admin_user():
        return redirect('reports:manager_dashboard')
    else:
        return redirect('reports:employee_dashboard')


@login_required
def employee_dashboard_view(request):
    """Employee dashboard showing their reports"""
    # Get employee's reports
    reports = EODReport.objects.filter(employee=request.user).order_by('-report_date')[:10]

    # Check if today's report exists
    today = timezone.now().date()
    try:
        today_report = EODReport.objects.get(employee=request.user, report_date=today)
        today_report_exists = True
        can_edit_today_report = today_report.can_edit()
    except EODReport.DoesNotExist:
        today_report = None
        today_report_exists = False
        can_edit_today_report = False

    # Get current week date range
    week_start, week_end = get_week_date_range()

    # Get overall statistics
    total_reports = EODReport.objects.filter(employee=request.user).count()
    pending_reports = EODReport.objects.filter(employee=request.user, status='PENDING').count()
    approved_reports = EODReport.objects.filter(employee=request.user, status='APPROVED').count()

    # Get weekly statistics
    week_reports = EODReport.objects.filter(
        employee=request.user,
        report_date__gte=week_start,
        report_date__lte=week_end
    )
    week_total = week_reports.count()
    week_pending = week_reports.filter(status='PENDING').count()
    week_approved = week_reports.filter(status='APPROVED').count()
    week_rejected = week_reports.filter(status='REJECTED').count()

    context = {
        'reports': reports,
        'today_report': today_report,
        'today_report_exists': today_report_exists,
        'can_edit_today_report': can_edit_today_report,
        'today': today,
        'is_weekend': is_weekend(),
        'week_display': get_week_display(),
        'week_start': week_start,
        'week_end': week_end,
        # Overall stats
        'total_reports': total_reports,
        'pending_reports': pending_reports,
        'approved_reports': approved_reports,
        # Weekly stats
        'week_total': week_total,
        'week_pending': week_pending,
        'week_approved': week_approved,
        'week_rejected': week_rejected,
    }
    return render(request, 'reports/employee_dashboard.html', context)


@login_required
def submit_report_view(request):
    """Submit or edit EOD report"""
    today = timezone.now().date()

    # Check if report for today already exists (only check weekday reports)
    try:
        # Try to find today's report only if today is a weekday
        if today.weekday() < 5:  # Monday-Friday
            report = EODReport.objects.get(employee=request.user, report_date=today)
            is_edit = True

            # Check if report can be edited (not approved/rejected)
            if not report.can_edit():
                messages.error(
                    request,
                    f'Cannot edit this report. It has been {report.get_status_display().lower()} by your manager.'
                )
                return redirect('reports:employee_dashboard')
        else:
            # Weekend: Allow creating new reports for past weekdays
            report = None
            is_edit = False
    except EODReport.DoesNotExist:
        report = None
        is_edit = False

    if request.method == 'POST':
        form = EODReportForm(request.POST, instance=report, user=request.user)
        if form.is_valid():
            eod_report = form.save(commit=False)
            eod_report.employee = request.user
            eod_report.save()
            if is_edit:
                messages.success(request, 'EOD report updated successfully!')
            else:
                messages.success(request, 'EOD report submitted successfully!')
            return redirect('reports:employee_dashboard')
    else:
        form = EODReportForm(instance=report, user=request.user)

    context = {
        'form': form,
        'is_edit': is_edit,
        'report': report,
    }
    return render(request, 'reports/submit_report.html', context)


@login_required
def report_detail_view(request, pk):
    """View individual report details"""
    report = get_object_or_404(EODReport, pk=pk)

    # Check permissions
    if request.user.is_employee():
        if report.employee != request.user:
            messages.error(request, 'You do not have permission to view this report.')
            return redirect('reports:employee_dashboard')
    elif request.user.is_manager():
        # Manager can only view their team members' reports
        if report.employee.manager != request.user:
            messages.error(request, 'You do not have permission to view this report.')
            return redirect('reports:manager_dashboard')

    context = {'report': report}
    return render(request, 'reports/report_detail.html', context)


@login_required
def manager_dashboard_view(request):
    """Manager dashboard for reviewing team reports"""
    if not (request.user.is_manager() or request.user.is_admin_user()):
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('reports:employee_dashboard')

    # Get team members' reports
    if request.user.is_admin_user():
        reports = EODReport.objects.all()
        team_members = None
    else:
        team_members = request.user.get_team_members()
        reports = EODReport.objects.filter(employee__in=team_members)

    # Apply filters
    filter_form = EODReportFilterForm(request.GET)
    if filter_form.is_valid():
        date_from = filter_form.cleaned_data.get('date_from')
        date_to = filter_form.cleaned_data.get('date_to')
        status = filter_form.cleaned_data.get('status')
        employee = filter_form.cleaned_data.get('employee')

        if date_from:
            reports = reports.filter(report_date__gte=date_from)
        if date_to:
            reports = reports.filter(report_date__lte=date_to)
        if status:
            reports = reports.filter(status=status)
        if employee:
            reports = reports.filter(
                Q(employee__first_name__icontains=employee) |
                Q(employee__last_name__icontains=employee) |
                Q(employee__username__icontains=employee)
            )

    reports = reports.select_related('employee').order_by('-report_date', '-submitted_at')[:50]

    # Get current week date range
    week_start, week_end = get_week_date_range()

    # Get base queryset for statistics
    if request.user.is_admin_user():
        base_reports = EODReport.objects.all()
    else:
        base_reports = EODReport.objects.filter(employee__manager=request.user)

    # Get overall statistics
    pending_count = base_reports.filter(status='PENDING').count()
    total_count = base_reports.count()
    approved_count = base_reports.filter(status='APPROVED').count()

    # Get weekly statistics
    week_reports = base_reports.filter(
        report_date__gte=week_start,
        report_date__lte=week_end
    )
    week_total = week_reports.count()
    week_pending = week_reports.filter(status='PENDING').count()
    week_approved = week_reports.filter(status='APPROVED').count()
    week_rejected = week_reports.filter(status='REJECTED').count()

    context = {
        'reports': reports,
        'filter_form': filter_form,
        'is_weekend': is_weekend(),
        'week_display': get_week_display(),
        'week_start': week_start,
        'week_end': week_end,
        # Overall stats
        'pending_count': pending_count,
        'total_count': total_count,
        'approved_count': approved_count,
        # Weekly stats
        'week_total': week_total,
        'week_pending': week_pending,
        'week_approved': week_approved,
        'week_rejected': week_rejected,
        'team_members': team_members,
    }
    return render(request, 'reports/manager_dashboard.html', context)


@login_required
def review_report_view(request, pk):
    """Manager review and approve/reject report"""
    if not (request.user.is_manager() or request.user.is_admin_user()):
        messages.error(request, 'You do not have permission to review reports.')
        return redirect('reports:employee_dashboard')

    report = get_object_or_404(EODReport, pk=pk)

    # Check if manager has permission to review this report
    if request.user.is_manager() and report.employee.manager != request.user:
        messages.error(request, 'You can only review reports from your team members.')
        return redirect('reports:manager_dashboard')

    # Check if report is already approved/rejected (cannot be edited)
    if report.status != 'PENDING':
        messages.info(
            request,
            f'This report has already been {report.get_status_display().lower()}. '
            'Reviews cannot be modified once finalized.'
        )
        # Redirect to report detail instead of review page
        return redirect('reports:report_detail', pk=report.pk)

    # Get or create review
    try:
        review = ReportReview.objects.get(report=report)
        is_new_review = False
    except ReportReview.DoesNotExist:
        review = None
        is_new_review = True

    if request.method == 'POST':
        # Double-check status hasn't changed since page load
        if report.status != 'PENDING':
            messages.error(request, 'This report has already been reviewed and cannot be modified.')
            return redirect('reports:manager_dashboard')

        form = ReportReviewForm(request.POST, instance=review, report=report)
        if form.is_valid():
            report_review = form.save(commit=False)
            report_review.report = report
            report_review.reviewer = request.user
            report_review.save()

            # Update report status
            decision = form.cleaned_data.get('decision')
            report.status = decision
            report.save()

            action = 'approved' if decision == 'APPROVED' else 'rejected'
            messages.success(request, f'Report {action} successfully! This decision is final and cannot be changed.')
            return redirect('reports:manager_dashboard')
    else:
        form = ReportReviewForm(instance=review, report=report)

    context = {
        'form': form,
        'report': report,
        'is_new_review': is_new_review,
    }
    return render(request, 'reports/review_report.html', context)


@login_required
def my_reports_view(request):
    """View all reports for the current user"""
    reports = EODReport.objects.filter(employee=request.user).order_by('-report_date')

    # Apply date filters
    filter_form = EODReportFilterForm(request.GET)
    if filter_form.is_valid():
        date_from = filter_form.cleaned_data.get('date_from')
        date_to = filter_form.cleaned_data.get('date_to')
        status = filter_form.cleaned_data.get('status')

        if date_from:
            reports = reports.filter(report_date__gte=date_from)
        if date_to:
            reports = reports.filter(report_date__lte=date_to)
        if status:
            reports = reports.filter(status=status)

    context = {
        'reports': reports,
        'filter_form': filter_form,
    }
    return render(request, 'reports/my_reports.html', context)
