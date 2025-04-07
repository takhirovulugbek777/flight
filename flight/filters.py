# filters.py
import django_filters
from .models import Flights


class CategoryFlightsFilter(django_filters.FilterSet):
    # Matnli fieldlar
    departure_airport__airport_name = django_filters.CharFilter(lookup_expr='icontains')
    arrival_airport__airport_name = django_filters.CharFilter(lookup_expr='icontains')

    # Raqamli fieldlar
    min_distance_km = django_filters.NumberFilter(field_name='distance_km', lookup_expr='gte')
    max_distance_km = django_filters.NumberFilter(field_name='distance_km', lookup_expr='lte')

    min_flight_count = django_filters.NumberFilter(field_name='flight_count', lookup_expr='gte')
    max_flight_count = django_filters.NumberFilter(field_name='flight_count', lookup_expr='lte')

    min_total_passenger_count = django_filters.NumberFilter(field_name='total_passenger_count', lookup_expr='gte')
    max_total_passenger_count = django_filters.NumberFilter(field_name='total_passenger_count', lookup_expr='lte')

    # flight_time ni sekundlarda filter qilamiz (eng optimal)
    min_flight_time = django_filters.DurationFilter(field_name='flight_time', lookup_expr='gte')
    max_flight_time = django_filters.DurationFilter(field_name='flight_time', lookup_expr='lte')

    class Meta:
        model = Flights
        fields = []
