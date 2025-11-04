"""
Utility functions for reports app
"""
from datetime import timedelta
from django.utils import timezone


def get_week_date_range():
    """
    Get the start and end date of the current work week (Monday to Friday)
    Weekend (Saturday/Sunday) resets to next week's Monday
    """
    today = timezone.now().date()
    weekday = today.weekday()  # Monday=0, Sunday=6

    # If it's weekend (Saturday=5, Sunday=6), get next Monday
    if weekday >= 5:  # Saturday or Sunday
        # Calculate days until next Monday
        days_until_monday = 7 - weekday
        week_start = today + timedelta(days=days_until_monday)
        week_end = week_start + timedelta(days=4)  # Friday
    else:
        # Current week: Monday to Friday
        days_since_monday = weekday
        week_start = today - timedelta(days=days_since_monday)
        week_end = week_start + timedelta(days=4)  # Friday

    return week_start, week_end


def is_weekend():
    """Check if today is weekend (Saturday or Sunday)"""
    today = timezone.now().date()
    return today.weekday() >= 5  # Saturday=5, Sunday=6


def get_current_week_number():
    """Get the current week number of the year"""
    today = timezone.now().date()
    return today.isocalendar()[1]  # Returns week number


def get_week_display():
    """Get a display string for the current week"""
    week_start, week_end = get_week_date_range()
    return f"{week_start.strftime('%b %d')} - {week_end.strftime('%b %d, %Y')}"
