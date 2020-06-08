from datetime import datetime

from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from rest_framework.parsers import JSONParser
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import *
from rest_framework.views import APIView

from . import parse_utils
from .models import Ride, Passenger


class Authentication(APIView):

    permission_classes = (AllowAny,)

    def post(self, request):

        try:
            json_body = request.data
            username, password = json_body['username'], json_body['password']
            assert username is not None and password is not None
        except (TypeError, AssertionError, KeyError):
            return Response("Incorrect request body", status=HTTP_400_BAD_REQUEST)
        user = authenticate(username=username, password=password)
        if user is not None:
            token = Token.objects.get_or_create(user=user)[0]
            return Response(data=token.key)
        else:
            return Response(data="Login failed", status=HTTP_404_NOT_FOUND)


class Registration(APIView):
    permission_classes = (AllowAny,)
    parser_classes = [JSONParser]

    def post(self, request):
        try:
            json_body = request.data
            username, password = json_body['username'], json_body['password']
            assert username is not None and password is not None
        except (TypeError, AssertionError, KeyError):
            return Response("Incorrect request body", status=HTTP_400_BAD_REQUEST)
        user = User(username=username, first_name=json_body.get('first_name'),
                    last_name=json_body.get('last_name'), email=json_body.get('email'))

        user.set_password(password)

        try:
            user.save()
            print(parse_utils.user_to_json(user))
            return Response(data=user.__str__(), status=HTTP_201_CREATED)
        except Exception as exc:
            return Response(data=exc.__str__(), status=HTTP_400_BAD_REQUEST)


class Profile(APIView):
    permission_classes = (IsAuthenticated,)
    parser_classes = [JSONParser]

    def get(self, request):
        return Response(data=parse_utils.user_to_json(request.user))

    def patch(self, request):
        try:
            json_body = request.data
            password = json_body.get('password')
            first_name = json_body.get('first_name')
            last_name = json_body.get('last_name')
            email = json_body.get('email')
            user: User = request.user

            if password is not None:
                user.__setattr__('password', password)
            if first_name is not None:
                user.__setattr__('first_name', first_name)
            if last_name is not None:
                user.__setattr__('last_name', last_name)
            if email is not None:
                user.__setattr__('email', email)

            user.save()

            return Response(data=user.__str__(), status=HTTP_200_OK)
        except Exception as exc:
            return Response(data=exc.__str__(), status=HTTP_400_BAD_REQUEST)


class Rides(APIView):
    parser_classes = (JSONParser,)

    permission_classes = (AllowAny,)

    def get(self, request):
        params = request.query_params
        try:
            ride_from = params.get('ride_from')
            ride_to = params.get('ride_to')
            start_date = params.get('start_date')
            assert ride_from is not None and ride_to is not None and start_date is not None
        except (TypeError, AssertionError, KeyError):
            return Response("Wrong parameters", status=HTTP_400_BAD_REQUEST)
        if params.get('first_result') is not None:
            first_result = int(params.get('first_result'))
        else:
            first_result = 0
        if params.get('max_result') is not None:
            max_result = min(int(params.get('max_result')), 10)
        else:
            max_result = 10

        rides = Ride.objects.order_by('date').filter(ride_from=ride_from, ride_to=ride_to,
                                                     date__gt=start_date)[first_result:max_result]

        return Response(data=parse_utils.rides_to_json(rides), status=HTTP_200_OK)

    def post(self, request):

        try:
            res = request.data

            ride_from = res['ride_from']
            ride_to = res['ride_to']
            seats = res['seats']
            format_data_time = '%Y-%m-%dT%H:%M'
            date = datetime.strptime(res['start_date'], format_data_time)
            price = res['price']
            ride = Ride(owner=request.user, ride_from=ride_from, ride_to=ride_to, seats=seats, date=date, price=price)
            ride.save()

        except Exception as exp:
            return Response(exp.__str__(), status=HTTP_400_BAD_REQUEST)
        return Response(data=parse_utils.ride_details_to_json(ride), status=HTTP_201_CREATED)


class HistoricRides(APIView):
    parser_classes = (JSONParser,)

    permission_classes = (IsAuthenticated,)

    def get(self, request):
        params = request.query_params

        if params.get('first_result') is not None:
            first_result = int(params.get('first_result'))
        else:
            first_result = 0
        if params.get('max_result') is not None:
            max_result = min(int(params.get('max_result')), 5)
        else:
            max_result = 5

        rides = Ride.objects.order_by('-date').filter(owner=request.user)[first_result:max_result]

        return Response(data=parse_utils.rides_to_json(rides), status=HTTP_200_OK)


class ParticipantRides(APIView):
    parser_classes = (JSONParser,)

    permission_classes = (IsAuthenticated,)

    def get(self, request):
        params = request.query_params

        if params.get('first_result') is not None:
            first_result = int(params.get('first_result'))
        else:
            first_result = 0
        if params.get('max_result') is not None:
            max_result = min(int(params.get('max_result')), 5)
        else:
            max_result = 5

        rides = Ride.objects.order_by('-date').filter(passenger__user=request.user)[first_result:max_result]

        return Response(data=parse_utils.rides_to_json(rides), status=HTTP_200_OK)


class RideDetails(APIView):
    parser_classes = (JSONParser,)

    permission_classes = (AllowAny,)

    def get(self, request, id):
        ride = Ride.objects.get(id=id)
        ride.is_passenger = ride.am_I_passenger(request.user)
        if ride is not None and ride.owner == request.user:
            passengers = User.objects.filter(passenger__ride=ride.id)
            return Response(data=parse_utils.my_ride_details_to_json(ride, passengers), status=HTTP_200_OK)

        return Response(data=parse_utils.ride_details_to_json(ride), status=HTTP_200_OK)


class AddPassenger(APIView):
    parser_classes = (JSONParser,)

    permission_classes = (IsAuthenticated,)

    def put(self, request, id):
        try:
            ride = Ride.objects.get(id=id)
            if ride is not None and ride.can_add_passenger():
                passenger = Passenger(user=request.user, ride=ride)
                passenger.save()
                ride.is_passenger = True
            else:
                return Response(data='Can not add passenger', status=HTTP_400_BAD_REQUEST)

        except Exception as exp:
            return Response(exp.__str__(), status=HTTP_400_BAD_REQUEST)
        return Response(data=parse_utils.ride_details_to_json(ride), status=HTTP_201_CREATED)
