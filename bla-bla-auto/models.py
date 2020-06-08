from __future__ import unicode_literals

from django.contrib.auth.models import User
from django.db import models


class Ride(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    ride_from = models.CharField(max_length=50)
    ride_to = models.CharField(max_length=50)
    seats = models.PositiveSmallIntegerField()
    date = models.DateTimeField()
    price = models.FloatField()

    def __str__(self):
        return str(self.id)

    def can_add_passenger(self):
        return self.seats - Passenger.objects.filter(ride=self).count() > 0

    def am_I_passenger(self, user):
        return self.owner == user or Passenger.objects.filter(user=user, ride=self).count() > 0

    def occupied_seats(self):
        return Passenger.objects.filter(ride=self).count()


class Passenger(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    ride = models.ForeignKey(Ride, on_delete=models.CASCADE)
