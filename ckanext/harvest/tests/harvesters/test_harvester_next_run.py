import unittest
from datetime import datetime

from ckanext.harvest.logic.action.update import _calculate_next_run
from numpy.ma.testutils import assert_equal

DAYS_OF_WEEK = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']


class TestNextRunCalculation(unittest.TestCase):

    def test_monday_sunday_weekly(self):
        start_date = datetime.strptime('2020-08-10T06:30:00', '%Y-%m-%dT%H:%M:%S')
        expected_result = datetime.strptime('2020-08-16T06:30:00', '%Y-%m-%dT%H:%M:%S')
        actual_date = _calculate_next_run(
            start_date=start_date,
            frequency="WEEKLY",
            day_of_week="Sunday",
            time=None
        )
        assert_equal(actual_date, expected_result)

    def test_monday_saturday_weekly(self):
        start_date = datetime.strptime('2020-08-10T06:30:00', '%Y-%m-%dT%H:%M:%S')
        expected_result = datetime.strptime('2020-08-15T06:30:00', '%Y-%m-%dT%H:%M:%S')
        actual_date = _calculate_next_run(
            start_date=start_date,
            frequency="WEEKLY",
            day_of_week="Saturday",
            time=None
        )
        assert_equal(actual_date, expected_result)

    def test_monday_tuesday_weekly(self):
        start_date = datetime.strptime('2020-08-10T06:30:00', '%Y-%m-%dT%H:%M:%S')
        expected_result = datetime.strptime('2020-08-18T06:30:00', '%Y-%m-%dT%H:%M:%S')
        actual_date = _calculate_next_run(
            start_date=start_date,
            frequency="WEEKLY",
            day_of_week="Tuesday",
            time=None
        )
        assert_equal(actual_date, expected_result)

    def test_wednesday_monday_monthly(self):
        start_date = datetime.strptime('2020-08-12T06:30:00', '%Y-%m-%dT%H:%M:%S')
        expected_result = datetime.strptime('2020-09-14T06:30:00', '%Y-%m-%dT%H:%M:%S')
        actual_date = _calculate_next_run(
            start_date=start_date,
            frequency="MONTHLY",
            day_of_week="Monday",
            time=None
        )
        assert_equal(actual_date, expected_result)

    def test_tuesday_sunday_biweekly(self):
        start_date = datetime.strptime('2020-08-13T06:30:00', '%Y-%m-%dT%H:%M:%S')
        expected_result = datetime.strptime('2020-08-30T06:30:00', '%Y-%m-%dT%H:%M:%S')
        actual_date = _calculate_next_run(
            start_date=start_date,
            frequency="BIWEEKLY",
            day_of_week="Sunday",
            time=None
        )
        assert_equal(actual_date, expected_result)

    def test_tuesday_sunday_daily(self):
        start_date = datetime.strptime('2020-08-13T06:30:00', '%Y-%m-%dT%H:%M:%S')
        expected_result = datetime.strptime('2020-08-14T06:30:00', '%Y-%m-%dT%H:%M:%S')
        actual_date = _calculate_next_run(
            start_date=start_date,
            frequency="DAILY",
            day_of_week="Sunday",
            time=None
        )
        assert_equal(actual_date, expected_result)

    def test_tuesday_sunday_always(self):
        start_date = datetime.strptime('2020-08-13T06:30:00', '%Y-%m-%dT%H:%M:%S')
        expected_result = datetime.strptime('2020-08-13T06:30:00', '%Y-%m-%dT%H:%M:%S')
        actual_date = _calculate_next_run(
            start_date=start_date,
            frequency="ALWAYS",
            day_of_week="Sunday",
            time=None
        )
        assert_equal(actual_date, expected_result)
