from timetrackingapi.serializers import CheckSerializer, VacationSerializer
from rest_framework import generics, mixins
from rest_framework.views import APIView
from rest_framework.response import Response
from timetrackingapi.models import Check, CHECK_IN, CHECK_OUT, Vacation
from django.utils import timezone
import timetrackingapi.utils as utils
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from datetime import datetime

'''
Model related views
These two views (CheckView & VacationView) are responsible for creating new instances using HTTP POST method,
to validate the input using their corresponding serializer, and to save it into the DB.
Here, mixins were used because they offer easy usage for common behavior (here, we don't have much 
custom pre/postprocessing)
'''


class CheckView(mixins.CreateModelMixin,
                generics.GenericAPIView):
    queryset = Check.objects.all()
    serializer_class = CheckSerializer

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    def perform_create(self, serializer):
        daily_checks = self.queryset.filter(checked_by=self.request.user, check_time__day=datetime.now().day)
        check_choice = CHECK_IN if daily_checks.count() % 2 == 0 else CHECK_OUT
        serializer.save(checked_by=self.request.user, check_choice=check_choice)


class VacationView(mixins.CreateModelMixin,
                   generics.GenericAPIView):
    queryset = Vacation.objects.all()
    serializer_class = VacationSerializer

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    def perform_create(self, serializer):
        serializer.save(taken_by_id=self.request.user.id)


'''
Information related views
These views are responsible for retrieving helpful information/statistics from the data in the DB.
Here, APIView was used, because there is custom pre/processing and post/processing for the data from the request,
and there is no model/serializer to rely on for validation.
'''


class UserHourInformationView(APIView):
    def get(self, request, *args, **kwargs):
        user = get_object_or_404(get_user_model(), id=kwargs.get('user_id'))
        user_checks = Check.objects.filter(checked_by=user)
        if user_checks.count() == 0:
            return Response("User {0} has no checks".format(user.id), status=404)
        # pass query params instead of requests
        time_type, time_val = utils.get_time_type_and_value(request.query_params)
        hours_worked, hours_left = utils.get_hours(time_type, time_val, user_checks)
        res = {
            "hours_worked": hours_worked,
            "hours_left": hours_left,
        }

        return Response(res)


class UserAverageTimesView(APIView):

    def get(self, request, *args, **kwargs):
        user = get_object_or_404(get_user_model(), id=kwargs.get('user_id'))
        user_checks = Check.objects.filter(checked_by=user)
        if user_checks.count() == 0:
            return Response("User {0} has no checks".format(user.id), status=404)
        average_arrival, average_leave = utils.get_average_times(user_checks)
        res = {
            "average_arrival": average_arrival,
            "average_leave": average_leave,
        }

        return Response(res)


class TeamLeavingToWorkingHours(APIView):

    def get(self, request, *args, **kwargs):
        ratio = utils.get_team_ratio(get_user_model().objects.all())
        res = {
            "leave_to_work_ratio": str(ratio) + "%"
        }
        return Response(res)
