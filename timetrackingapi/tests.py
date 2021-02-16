from rest_framework.test import APITestCase
from django.contrib.auth.models import User
from django.test import Client
from .models import Vacation, Check
from datetime import datetime, timedelta
import pytz
from unittest import mock

client = Client()
'''
List of checks, containing 9 working hours in week 13 (04/04/2021) and 2 leaving hours
and also 21 working hours in 4th quarter with 4 leaving hours
whole year contains 30 working hours, with 6 leaving hours
'''
check_list = [datetime(2021, 4, 4, 8, 00, 00, tzinfo=pytz.utc),
              datetime(2021, 4, 4, 13, 00, 00, 00, tzinfo=pytz.utc),
              datetime(2021, 4, 4, 15, 00, 00, 00, tzinfo=pytz.utc),
              datetime(2021, 4, 4, 19, 00, 00, 00, tzinfo=pytz.utc),
              datetime(2021, 12, 1, 8, 00, 00, 00, tzinfo=pytz.utc),
              datetime(2021, 12, 1, 12, 00, 00, 00, tzinfo=pytz.utc),
              datetime(2021, 12, 2, 9, 00, 00, 00, tzinfo=pytz.utc),
              datetime(2021, 12, 2, 19, 00, 00, 00, tzinfo=pytz.utc),
              datetime(2021, 12, 4, 8, 00, 00, 00, tzinfo=pytz.utc),
              datetime(2021, 12, 4, 11, 00, 00, 00, tzinfo=pytz.utc),
              datetime(2021, 12, 4, 15, 00, 00, 00, tzinfo=pytz.utc),
              datetime(2021, 12, 4, 19, 00, 00, 00, tzinfo=pytz.utc)
              ]

'''
List of checks for a second user, used to find statistics for the whole team in unit tests
'''
check_list2 = [datetime(2021, 5, 1, 6, 00, 00, tzinfo=pytz.utc),
               datetime(2021, 5, 1, 13, 00, 00, 00, tzinfo=pytz.utc),
               datetime(2021, 5, 1, 15, 00, 00, 00, tzinfo=pytz.utc),
               datetime(2021, 5, 1, 21, 00, 00, 00, tzinfo=pytz.utc),
               datetime(2021, 10, 1, 11, 00, 00, 00, tzinfo=pytz.utc),
               datetime(2021, 10, 1, 12, 00, 00, 00, tzinfo=pytz.utc),
               datetime(2021, 10, 2, 9, 30, 00, 00, tzinfo=pytz.utc),
               datetime(2021, 10, 2, 19, 00, 00, 00, tzinfo=pytz.utc),
               datetime(2021, 10, 4, 8, 45, 00, 00, tzinfo=pytz.utc),
               datetime(2021, 10, 4, 11, 00, 00, 00, tzinfo=pytz.utc),
               datetime(2021, 10, 4, 15, 00, 00, 00, tzinfo=pytz.utc),
               datetime(2021, 10, 4, 17, 30, 00, 00, tzinfo=pytz.utc)
               ]


class ObtainAuthTokenTests(APITestCase):

    def setUp(self):
        user = User.objects.create_user(username="test_user", password="test_password")

    def test_registered_user_should_obtain_auth_token(self):
        credentials = {
            "username": "test_user",
            "password": "test_password"
        }
        response = self.client.post('/api/obtain-auth-token/', credentials)
        self.assertEqual(response.status_code, 200)

    def test_unregistered_user_should_not_obtain_auth_token(self):
        credentials = {
            "username": "unregistered_user",
            "password": "password"
        }
        response = self.client.post('/api/obtain-auth-token/', credentials)
        self.assertEqual(response.status_code, 400)


class VacationViewTests(APITestCase):

    def setUp(self):
        user = User.objects.create_user(username="test_user", password="test_password")

    def test_post_vacation_authenticated_user_should_return_200(self):
        self.client.force_login(User.objects.get(pk=1))
        request_payload = {
            "start_date": "2021-02-14",
            "end_date": "2021-02-15",
        }
        expected_response = {'start_date': '2021-02-14', 'end_date': '2021-02-15',
                             'taken_by': {'id': 1, 'username': 'test_user'}}
        response = self.client.post('/api/vacation/', request_payload)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json(), expected_response)

    def test_post_vacation_for_unauthenticated_user_should_return_401(self):
        request_payload = {
            "start_date": "2021-02-14",
            "end_date": "2021-02-15",
        }
        response = self.client.post('/api/vacation/', request_payload)
        self.assertEqual(response.status_code, 401)

    def test_post_vacation_with_empty_body(self):
        self.client.force_login(User.objects.get(pk=1))
        request_payload = {

        }
        response = self.client.post('/api/vacation/', request_payload)
        self.assertEqual(response.status_code, 400)

    def test_post_vacation_with_start_date_after_end_date_should_return_400(self):
        self.client.force_login(User.objects.get(pk=1))
        request_payload = {
            "start_date": "2021-02-16",
            "end_date": "2021-02-15"
        }
        expected_response = {'start_date': ['start_date must be before end_date']}
        response = self.client.post('/api/vacation/', request_payload)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), expected_response)

    def test_post_vacation_with_longer_than_fourteen_workdays(self):
        self.client.force_login(User.objects.get(pk=1))
        request_payload = {
            "start_date": "2021-03-01",
            "end_date": "2021-03-25"
        }
        expected_response = {'non_field_errors': ['The number of requested days is higher than the vacation limit (14 days)']}
        response = self.client.post('/api/vacation/', request_payload)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), expected_response)

    def test_post_vacation_with_sum_longer_than_fourteen_workdays(self):
        user = User.objects.get(pk=1)
        self.client.force_login(user)
        # 01/02/2021 to 15/02/2021 contains 11 workdays
        Vacation.objects.create(start_date=datetime(2021, 2, 1).date(),
                                end_date=datetime(2021, 2, 15).date(),
                                taken_by=user)
        request_payload = {
            "start_date": "2021-02-22",
            "end_date": "2021-02-26"
        }
        expected_response = {'non_field_errors': ['You have exceeded the number of vacations, you can only take 3 more vacations']}
        response = self.client.post('/api/vacation/', request_payload)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), expected_response)

    def test_get_vacation_should_not_be_allowed(self):
        user = User.objects.get(pk=1)
        self.client.force_login(user)
        response = self.client.get('/api/vacation/')
        self.assertEqual(response.status_code, 405)


class CheckViewTests(APITestCase):

    def setUp(self):
        user = User.objects.create_user(username="test_user", password="test_password")

    def test_post_check_authenticated_user_should_return_200(self):
        self.client.force_login(User.objects.get(pk=1))
        response = self.client.post('/api/check/')
        self.assertEqual(response.status_code, 201)

    def test_post_vacation_for_unauthenticated_user_should_return_401(self):
        response = self.client.post('/api/check/')
        self.assertEqual(response.status_code, 401)

    def test_get_vacation_should_not_be_allowed(self):
        self.client.force_login(User.objects.get(pk=1))
        response = self.client.get('/api/check/')
        self.assertEqual(response.status_code, 405)


class UserHourInformationViewTest(APITestCase):

    def setUp(self):
        user = User.objects.create_user(username="test_user", password="test_password", id=5)
        self.client.force_login(user)
        for check in check_list:
            with mock.patch('django.utils.timezone.now', mock.Mock(return_value=check)):
                Check.objects.create(checked_by=user)

    def test_get_user_weekly_hours(self):
        response = self.client.get('/api/users/5/hours?week=13')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['hours_worked'], 9.0)
        self.assertEqual(response.json()['hours_left'], 2.0)

    def test_get_user_quarterly_hours(self):
        response = self.client.get('/api/users/5/hours?quarter=4')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['hours_worked'], 21.0)
        self.assertEqual(response.json()['hours_left'], 4.0)

    def test_get_user_yearly_hours(self):
        response = self.client.get('/api/users/5/hours?year=2021')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['hours_worked'], 30.0)
        self.assertEqual(response.json()['hours_left'], 6.0)

    def test_get_user_hours_for_unknown_user_should_return_404(self):
        response = self.client.get('/api/users/6/hours?year=2021')
        self.assertEqual(response.status_code, 404)

    def test_post_user_hours_should_return_405(self):
        user = User.objects.get(pk=5)
        self.client.force_login(user)
        response = self.client.post('/api/users/5/hours?year=2021')
        self.assertEqual(response.status_code, 405)


class UserAverageTimesViewTest(APITestCase):

    def setUp(self):
        user = User.objects.create_user(username="test_user", password="test_password", id=5)
        self.client.force_login(user)
        for check in check_list:
            with mock.patch('django.utils.timezone.now', mock.Mock(return_value=check)):
                Check.objects.create(checked_by=user)

    def test_get_user_average_times(self):
        response = self.client.get('/api/users/5/average-times')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['average_arrival'], '08:15')
        self.assertEqual(response.json()['average_leave'], '17:15')

    def test_get_user_average_times_for_unknown_user(self):
        response = self.client.get('/api/users/6/average-times')
        self.assertEqual(response.status_code, 404)


class TeamLeavingToWorkingHoursViewTest(APITestCase):

    def setUp(self):
        user = User.objects.create_user(username="test_user", password="test_password")
        user2 = User.objects.create_user(username="test_user2", password="test_password2")
        self.client.force_login(user)
        for check in check_list:
            with mock.patch('django.utils.timezone.now', mock.Mock(return_value=check)):
                Check.objects.create(checked_by=user)
        for check in check_list2:
            with mock.patch('django.utils.timezone.now', mock.Mock(return_value=check)):
                Check.objects.create(checked_by=user2)

    def test_get_leaving_to_working_hours(self):
        response = self.client.get('/api/team-stats/working-to-leaving')
        expected_ratio = '20.600858369098713%'
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['leave_to_work_ratio'], expected_ratio)








