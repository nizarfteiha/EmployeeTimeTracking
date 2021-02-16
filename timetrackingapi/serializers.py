from rest_framework import serializers
from .models import Check, Vacation
from django.contrib.auth.models import User
from . import utils


class UserSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    username = serializers.CharField(max_length=255)

    class Meta:
        model = User
        fields = ['id', 'username']


class CheckSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    check_choice = serializers.CharField(read_only=True)
    check_time = serializers.DateTimeField(read_only=True)
    checked_by = UserSerializer(read_only=True)

    class Meta:
        model = Check
        fields = "__all__"


class VacationSerializer(serializers.ModelSerializer):
    start_date = serializers.DateField()
    end_date = serializers.DateField()
    taken_by = UserSerializer(read_only=True)

    def validate(self, data):
        user_vacations = Vacation.objects.filter(taken_by=self.context['request'].user)
        taken_vacations_length = utils.get_vacations_number(user_vacations)
        requested_vacation_length = utils.calculate_workdays_between_dates(data['start_date'], data['end_date'])
        if data['start_date'] > data['end_date']:
            raise serializers.ValidationError({
                "start_date": "start_date must be before end_date",
            })
        elif requested_vacation_length > 14:
            raise serializers.ValidationError(
                "The number of requested days is higher than the vacation limit (14 days)")
        elif taken_vacations_length + requested_vacation_length > 14:
            raise serializers.ValidationError(
                "You have exceeded the number of vacations, you can only take {0} more vacations".format(
                    14 - taken_vacations_length))
        else:
            return data

    class Meta:
        model = Vacation
        fields = "__all__"
