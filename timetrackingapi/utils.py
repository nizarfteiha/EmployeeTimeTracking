from .models import Check
import datetime


def get_team_ratio(team):
    """
    :param team: group containing all users
    :return: float: the calculated ratio.

    responsible for calculating leaving to working hours ratio
    """
    team_working_hours = 0
    team_leaving_hours = 0
    for member in team:
        checks = Check.objects.filter(checked_by=member)
        if checks.count() == 0:
            continue
        member_working_hours, member_leaving_hours = calculate_hours(checks)
        team_working_hours += member_working_hours
        team_leaving_hours += member_leaving_hours

    ratio = (team_leaving_hours / team_working_hours) * 100
    return ratio


def get_time_type_and_value(query_params):
    """
    :param query_params: request query parameters
    :return: tuple: containing time_type, time_value
    """
    possible_types = ['week', 'quarter', 'year']
    for param_type in possible_types:
        param_value = query_params.get(param_type)
        if param_value is not None:
            return param_type, param_value


def get_hours(time_type, time_value, checks_queryset):
    """
    :param time_type: type of time interval (week,quarter,year)
    :param time_value: week,quarter,year number
    :param checks_queryset: queryset containing user checks
    :return: float,float: number of worked hours, number of left hours

    filters the queryset based on time period, and passes the filtered queryset
    to another method responsible for hour calculation
    """
    if time_type == 'week':
        checks = checks_queryset.filter(check_time__week=time_value)
    elif time_type == 'quarter':
        checks = checks_queryset.filter(check_time__quarter=time_value)
    elif time_type == 'year':
        checks = checks_queryset.filter(check_time__year=time_value)

    hours_worked, hours_left = calculate_hours(checks)

    return hours_worked, hours_left


def get_average_times(checks_queryset):
    """
    :param checks_queryset: queryset containing user related checks
    :return: float,float: average arrival time, average leave time

    Calculates average arrival time, average leaving time
    """
    arrival_times = []
    leave_times = []
    days_worked = checks_queryset.dates('check_time', 'day')
    for day in days_worked:
        checks_in_day = checks_queryset.filter(check_time__date=day)
        first_check = checks_in_day[0].check_time.time()
        last_check = checks_in_day[checks_in_day.count() - 1].check_time.time()
        arrival_times.append(first_check.hour * 60 + first_check.minute)
        leave_times.append(last_check.hour * 60 + last_check.minute)

    average_arrival = '{:02d}:{:02d}'.format(*divmod(int(sum(arrival_times) / len(arrival_times)), 60))
    average_leave = '{:02d}:{:02d}'.format(*divmod(int(sum(leave_times) / len(leave_times)), 60))
    return average_arrival, average_leave


def calculate_hours(checks):
    """
    :param checks: queryset containing checks in period
    :return: float,float : hours_worked, hours_left

    calculates working hours & leaving hours from a given checks queryset
    """
    working_minutes = 0
    leaving_minutes = 0
    hours_worked = 0
    hours_left = 0
    for i in range(len(checks) - 1):
        # Two different days,skip
        if checks[i].check_time.date() != checks[i + 1].check_time.date():
            continue
        # IN,OUT combo (working hours)
        minutes = (checks[i + 1].check_time - checks[i].check_time).total_seconds() / 60
        if (i + 1) % 2:
            working_minutes += minutes
        # OUT,IN combo (leaving hours,or next day)
        else:
            leaving_minutes += minutes
        hours_worked = working_minutes / 60
        hours_left = leaving_minutes / 60
    return hours_worked, hours_left


def get_vacations_number(vacations):
    """
    :param vacations: vacation queryset
    :return: int: number of taken vacations

    iterates on each taken vacation and calls another method responsible for calculating number of
    weekdays taken, returns total number of taken vacations
    """
    number_of_vacations = 0
    for vacation in vacations:
        number_of_vacations += calculate_workdays_between_dates(vacation.start_date, vacation.end_date)
    return number_of_vacations


def calculate_workdays_between_dates(start_date, end_date):
    """
    :param start_date: vacation start date (YYYY-MM-DD)
    :param end_date: vacation end date (YYYY-MM-DD)
    :return: number of working days (all days except for friday and saturday) for the given period

    responsible for calculating workdays taken as vacation
    """
    day_delta = datetime.timedelta(days=1)
    work_days = 0
    current_day = start_date
    while current_day <= end_date:
        if current_day.weekday() != 4 and current_day.weekday() != 5:
            work_days += 1
        current_day += day_delta
    return work_days
