from django.db import models
from django.contrib.auth.models import User

CHECK_IN = 'IN'
CHECK_OUT = 'OUT'
CHECK_CHOICES = [
    (CHECK_IN, 'IN'),
    (CHECK_OUT, 'OUT')
]


class Check(models.Model):
    check_choice = models.CharField(max_length=3, choices=CHECK_CHOICES)
    check_time = models.DateTimeField(auto_now_add=True)
    checked_by = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return "User with ID {0} Checked {1} at {2}" \
            .format(self.checked_by.id, self.check_choice, self.check_time)


class Vacation(models.Model):
    start_date = models.DateField()
    end_date = models.DateField()
    taken_by = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return "User with ID {0} took a vacation of length {1} days from date {2} to date {3}" \
            .format(self.taken_by.id, (self.end_date - self.start_date).days + 1, self.start_date, self.end_date)
