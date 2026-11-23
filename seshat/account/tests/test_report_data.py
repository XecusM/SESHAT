from datetime import date

from django.test import TestCase, RequestFactory

from x_django_app.models import XActivity

from account import report_data
from seshat.testing import create_user


class ReportHelpersTest(TestCase):
    '''
    Test the report helper functions
    '''

    def test_parse_date_range(self):
        request = RequestFactory().get(
                        '/', {'from_date': '2026-01-01', 'to_date': '2026-03-31'})
        self.assertEqual(
                    report_data.parse_date_range(request),
                    (date(2026, 1, 1), date(2026, 3, 31)))

    def test_parse_date_range_defaults_and_bad_values(self):
        request = RequestFactory().get('/', {'from_date': 'bad', 'to_date': 'bad'})
        from_date, to_date = report_data.parse_date_range(request)
        self.assertLessEqual(from_date, to_date)
        self.assertEqual(from_date.day, 1)

    def test_parse_date_range_swapped(self):
        request = RequestFactory().get(
                        '/', {'from_date': '2026-05-01', 'to_date': '2026-01-01'})
        from_date, to_date = report_data.parse_date_range(request)
        self.assertLess(from_date, to_date)

    def test_month_range(self):
        months = report_data.month_range(date(2025, 11, 15), date(2026, 2, 1))
        self.assertEqual(
                    [month.strftime('%Y-%m') for month in months],
                    ['2025-11', '2025-12', '2026-01', '2026-02'])

    def test_relabel_area(self):
        self.assertEqual(
                    list(report_data.relabel_area({None: 2, 'stock': 1})),
                    ['Other', 'stock'])


class BuildReportsTest(TestCase):
    '''
    Test the report data builders
    '''

    def setUp(self):
        self.user = create_user('reporter')
        self.other = create_user('other', is_active=False)
        for _ in range(3):
            XActivity.objects.create_activity(
                activity_object=self.user, activity=XActivity.EDIT,
                user=self.user, message='edit')
        XActivity.objects.create_activity(
                activity_object=self.other, activity=XActivity.CREATE,
                user=self.other, message='create')
        self.request = RequestFactory().get('/')

    def test_user_report(self):
        data = report_data.build_user_report(self.user, self.request)
        self.assertEqual(len(data['months']), 12)
        self.assertEqual(sum(data['total']), 3)
        self.assertEqual(sum(data['by_type']['Edit']), 3)
        self.assertEqual(sum(data['by_area'].values()), 3)

    def test_all_users_report_only_active_users(self):
        data = report_data.build_all_users_report(self.request)
        self.assertEqual(sum(data['total']), 3)
        self.assertEqual(data['top_users'], {'reporter': 3})

    def test_top_users_folds_others(self):
        totals = report_data.group_totals(
                    XActivity.objects.all(), 'user__username', top_n=1)
        self.assertEqual(totals, {'reporter': 3, 'Others': 1})
