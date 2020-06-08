from django.contrib.auth.models import User

from .models import Ride


def user_to_json(user: User):
    return {'id': user.id,
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name
            }


def rides_to_json(rides: [Ride]):
    js = []
    for ride in rides:
        js.append({'id': ride.id,
                   'ride_from': ride.ride_from,
                   'ride_to': ride.ride_to,
                   'seats': ride.seats,
                   'occupied_seats': ride.occupied_seats(),
                   'date': ride.date,
                   'price': ride.price
                   })
    return js


def ride_details_to_json(ride: Ride):
    return {'id': ride.id,
            'ride_from': ride.ride_from,
            'ride_to': ride.ride_to,
            'seats': ride.seats,
            'occupied_seats': ride.occupied_seats(),
            'date': ride.date,
            'price': ride.price,
            'is_passenger': ride.is_passenger
            }


def my_ride_details_to_json(ride: Ride, passengers: [User]):
    js = []
    for passenger in passengers:
        js.append({'id': passenger.id,
                   'username': passenger.username,
                   'email': passenger.email,
                   'first_name': passenger.first_name,
                   'last_name': passenger.last_name
                   })

    return {'id': ride.id,
            'ride_from': ride.ride_from,
            'ride_to': ride.ride_to,
            'seats': ride.seats,
            'occupied_seats': ride.occupied_seats(),
            'date': ride.date,
            'price': ride.price,
            'is_passenger': ride.is_passenger,
            'passengers': js
            }
