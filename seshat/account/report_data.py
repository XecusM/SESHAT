from collections import OrderedDict
from datetime import date

from dateutil.relativedelta import relativedelta

from django.db.models import Count
from django.utils import timezone
from django.db.models.functions import TruncMonth
from django.utils.translation import gettext_lazy as _

from x_django_app.models import XActivity


ACTIVITY_LABELS = dict(XActivity.activity_choices)


def parse_date_range(request):
    '''
    Get the report's date range from the request, defaulting to the
    12 months ending this month
    '''
    to_date = timezone.localdate()
    try:
        if request.GET.get('to_date'):
            to_date = date.fromisoformat(request.GET.get('to_date'))
    except ValueError:
        pass

    from_date = to_date.replace(day=1) - relativedelta(months=11)
    try:
        if request.GET.get('from_date'):
            from_date = date.fromisoformat(request.GET.get('from_date'))
    except ValueError:
        pass

    if from_date > to_date:
        from_date, to_date = to_date, from_date

    return from_date, to_date


def month_range(from_date, to_date):
    '''
    Get every first-of-month date between from_date and to_date, inclusive
    '''
    months = []
    current = from_date.replace(day=1)
    end = to_date.replace(day=1)
    while current <= end:
        months.append(current)
        current += relativedelta(months=1)

    return months


def monthly_counts(queryset, months, date_field):
    '''
    Count queryset rows per month for the given date field, aligned to months
    '''
    month_keys = [month.strftime('%Y-%m') for month in months]
    counts = OrderedDict((key, 0) for key in month_keys)

    rows = queryset.annotate(month=TruncMonth(date_field)).values(
                                'month').annotate(
                                total=Count('id')).order_by('month')

    for row in rows:
        month_key = row['month'].strftime('%Y-%m')
        if month_key in counts:
            counts[month_key] = row['total']

    return [counts[key] for key in month_keys]


def monthly_counts_by_group(queryset, months, date_field, group_field):
    '''
    Count queryset rows per month, split by group_field, aligned to months
    '''
    month_keys = [month.strftime('%Y-%m') for month in months]
    breakdown = OrderedDict()

    rows = queryset.annotate(month=TruncMonth(date_field)).values(
                                'month', group_field).annotate(
                                total=Count('id')).order_by('month')

    for row in rows:
        month_key = row['month'].strftime('%Y-%m')
        group_name = row[group_field]
        breakdown.setdefault(
                        group_name,
                        OrderedDict((key, 0) for key in month_keys))
        if month_key in breakdown[group_name]:
            breakdown[group_name][month_key] = row['total']

    return OrderedDict(
        (name, [values[key] for key in month_keys])
        for name, values in breakdown.items()
    )


def group_totals(queryset, group_field, top_n=None):
    '''
    Count queryset rows by group_field. When top_n is given, keep only
    the top groups and fold the rest into "Others"
    '''
    rows = list(queryset.values(group_field).annotate(
                                total=Count('id')).order_by('-total'))

    if top_n is None:
        return OrderedDict((row[group_field], row['total']) for row in rows)

    result = OrderedDict((row[group_field], row['total']) for row in rows[:top_n])

    rest = rows[top_n:]
    if rest:
        result['Others'] = sum(row['total'] for row in rest)

    return result


def relabel_activity(dict_by_code):
    '''
    Replace activity codes with their display labels
    '''
    return OrderedDict(
        (str(ACTIVITY_LABELS.get(code, code)), value)
        for code, value in dict_by_code.items()
    )


def relabel_area(dict_by_app_label):
    '''
    Replace missing app labels (activities recorded without a content
    type) with "Other", keeping the "Others" top_n bucket as-is
    '''
    return OrderedDict(
        (app_label if app_label else str(_('Other')), value)
        for app_label, value in dict_by_app_label.items()
    )


def build_user_report(user, request):
    '''
    Personal activity report data for a single user: activities per
    month, the same trend split by activity type, and the activity
    breakdown by area (app), for the requested date range
    '''
    from_date, to_date = parse_date_range(request)
    months = month_range(from_date, to_date)

    queryset = XActivity.objects.filter(
                                user=user,
                                created_at__date__gte=from_date,
                                created_at__date__lte=to_date)

    return {
        'months': [month.strftime('%Y-%m') for month in months],
        'total': monthly_counts(queryset, months, 'created_at'),
        'by_type': relabel_activity(monthly_counts_by_group(
                                queryset, months, 'created_at', 'activity')),
        'by_area': relabel_area(group_totals(queryset, 'activity_type__app_label')),
    }


def build_all_users_report(request, top_n=8):
    '''
    Org-wide activity report data, scoped to active users only:
    activities per month, the same trend split by activity type, the
    activity breakdown by area, and the top active users by activity
    count, for the requested date range
    '''
    from_date, to_date = parse_date_range(request)
    months = month_range(from_date, to_date)

    queryset = XActivity.objects.filter(
                                user__is_active=True,
                                created_at__date__gte=from_date,
                                created_at__date__lte=to_date)

    return {
        'months': [month.strftime('%Y-%m') for month in months],
        'total': monthly_counts(queryset, months, 'created_at'),
        'by_type': relabel_activity(monthly_counts_by_group(
                                queryset, months, 'created_at', 'activity')),
        'by_area': relabel_area(group_totals(queryset, 'activity_type__app_label')),
        'top_users': group_totals(queryset, 'user__username', top_n=top_n),
    }
