from django.urls import path
from .views import CheckView, VacationView, UserHourInformationView, UserAverageTimesView, TeamLeavingToWorkingHours
from rest_framework.authtoken import views as auth_view

urlpatterns = [
    path('check/', CheckView.as_view()),
    path('vacation/', VacationView.as_view()),
    path('obtain-auth-token/', auth_view.obtain_auth_token),
    path('users/<int:user_id>/hours', UserHourInformationView.as_view()),
    path('users/<int:user_id>/average-times', UserAverageTimesView.as_view()),
    path('team-stats/working-to-leaving', TeamLeavingToWorkingHours.as_view())
]

handler400 = 'rest_framework.exceptions.bad_request'
handler500 = 'rest_framework.exceptions.server_error'
