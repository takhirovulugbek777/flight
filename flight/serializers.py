from django.db.models import Count, OuterRef, Subquery
from rest_framework import serializers

from flight.models import *


class AircraftsDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = AircraftsData
        fields = '__all__'


class AirportsDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = AirportsData
        fields = '__all__'


class BoardingPassesSerializer(serializers.ModelSerializer):
    class Meta:
        model = BoardingPasses
        fields = '__all__'


class BookingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bookings
        fields = '__all__'


class FlightsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Flights
        fields = '__all__'


class SeatsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Flights
        fields = '__all__'


class TicketFlightsSerializer(serializers.ModelSerializer):
    class Meta:
        model = TicketFlights
        fields = '__all__'


class TicketsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tickets
        fields = '__all__'


class FlightCountSerializer(serializers.Serializer):
    departure_airport = serializers.CharField()
    arrival_airport = serializers.CharField()
    flight_count = serializers.IntegerField()
    # passengers_count = serializers.IntegerField()
    distance_km = serializers.FloatField()


class FlightsPassengerCountSerializer(serializers.ModelSerializer):
    passengers_count = serializers.IntegerField()

    class Meta:
        model = Flights
        fields = [
            'flight_id', 'flight_no', 'scheduled_departure', 'scheduled_arrival',
            'departure_airport', 'arrival_airport', 'status', 'aircraft_code',
            'actual_departure', 'actual_arrival', 'passengers_count'
        ]

    @staticmethod
    def prefetch_queryset(queryset):
        passenger_count_subquery = TicketFlights.objects.filter(
            flight=OuterRef('pk')
        ).order_by().values('flight').annotate(count=Count('ticket_no')).values('count')

        return queryset.annotate(
            passengers_count=Subquery(passenger_count_subquery, output_field=models.IntegerField()))


class AirportFlightsDetailSerializer(serializers.ModelSerializer):
    arrival_airport = serializers.CharField(source='arrival_airport.airport_code')
    arrival_airport_name = serializers.SerializerMethodField()
    distance_km = serializers.FloatField()
    flight_time = serializers.SerializerMethodField()
    flight_count = serializers.IntegerField()
    total_passenger_count = serializers.IntegerField()
    departure_airport_name = serializers.SerializerMethodField()

    class Meta:
        model = Flights
        fields = [
            'departure_airport', 'departure_airport_name',
            'arrival_airport', 'arrival_airport_name',
            'distance_km', 'flight_time', 'flight_count', 'total_passenger_count'
        ]

    def get_arrival_airport_name(self, obj):
        from django.utils.translation import get_language
        lang = get_language()
        return obj.arrival_airport.airport_name.get(lang, obj.arrival_airport.airport_name.get('en', 'Unknown'))

    def get_departure_airport_name(self, obj):
        from django.utils.translation import get_language
        lang = get_language()
        return obj.departure_airport.airport_name.get(lang, obj.departure_airport.airport_name.get('en', 'Unknown'))

    def get_flight_time(self, obj):
        if hasattr(obj, 'flight_time'):
            total_seconds = int(obj.flight_time.total_seconds())
            hours, remainder = divmod(total_seconds, 3600)
            minutes, seconds = divmod(remainder, 60)
            return f"{hours:02}:{minutes:02}"
        return None
