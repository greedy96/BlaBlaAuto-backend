from django.contrib import admin

from .models import Passenger, Ride


@admin.register(Ride)
class RideAdmin(admin.ModelAdmin):
    list_display = ('id', 'ride_from', 'ride_to', 'date', 'owner')
    ordering = ('date',)


@admin.register(Passenger)
class PassengerAdmin(admin.ModelAdmin):
    list_display = ('user', 'ride')
