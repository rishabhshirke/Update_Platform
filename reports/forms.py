from django import forms
from django.utils import timezone
from .models import EODReport, ReportReview


class EODReportForm(forms.ModelForm):
    """Form for employees to submit EOD reports"""

    class Meta:
        model = EODReport
        fields = ['report_date', 'project_name', 'tasks_completed', 'hours_worked', 'blockers_issues', 'next_day_plan']
        widgets = {
            'report_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control',
                'max': timezone.now().date().isoformat()
            }),
            'project_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Mobile App Development, Website Redesign...'
            }),
            'tasks_completed': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'List the tasks and activities you completed today...'
            }),
            'hours_worked': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.5',
                'min': '0',
                'max': '24',
                'placeholder': 'e.g., 8.5'
            }),
            'blockers_issues': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Describe any blockers or issues you faced (optional)...'
            }),
            'next_day_plan': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'What do you plan to work on tomorrow?...'
            }),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        # Set default date to today
        if not self.instance.pk:
            self.fields['report_date'].initial = timezone.now().date()

    def clean_report_date(self):
        report_date = self.cleaned_data['report_date']

        # Prevent future dates
        if report_date > timezone.now().date():
            raise forms.ValidationError("Cannot submit reports for future dates.")

        # Check if date is a weekend (Saturday=5, Sunday=6)
        if report_date.weekday() >= 5:
            raise forms.ValidationError(
                "Reports can only be submitted for weekdays (Monday to Friday). "
                "Weekend submissions are not allowed."
            )

        # Check for duplicate reports (only when creating new report)
        if not self.instance.pk and self.user:
            if EODReport.objects.filter(employee=self.user, report_date=report_date).exists():
                raise forms.ValidationError(
                    f"You have already submitted a report for {report_date}. "
                    "Please edit your existing report instead."
                )

        return report_date


class ReportReviewForm(forms.ModelForm):
    """Form for managers to review EOD reports"""

    DECISION_CHOICES = [
        ('APPROVED', 'Approve'),
        ('REJECTED', 'Reject'),
    ]

    decision = forms.ChoiceField(
        choices=DECISION_CHOICES,
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
        label='Review Decision'
    )

    class Meta:
        model = ReportReview
        fields = ['comments']
        widgets = {
            'comments': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Add your feedback and comments...'
            }),
        }

    def __init__(self, *args, **kwargs):
        self.report = kwargs.pop('report', None)
        super().__init__(*args, **kwargs)
        if self.report:
            self.fields['decision'].initial = self.report.status


class EODReportFilterForm(forms.Form):
    """Filter form for EOD reports"""

    date_from = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control'
        }),
        label='From Date'
    )
    date_to = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control'
        }),
        label='To Date'
    )
    status = forms.ChoiceField(
        required=False,
        choices=[('', 'All Status')] + list(EODReport.STATUS_CHOICES),
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='Status'
    )
    employee = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search by employee name...'
        }),
        label='Employee'
    )
