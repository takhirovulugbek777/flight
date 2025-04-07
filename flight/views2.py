from django.db.models import F, FloatField, ExpressionWrapper, DurationField, Count, Subquery, OuterRef, IntegerField, \
    Min
from django.db.models.functions import Radians, Sin, Cos, ATan2, Sqrt
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.generics import ListAPIView
from rest_framework import filters

from .filters import CategoryFlightsFilter
from .models import Flights, TicketFlights
from .serializers import AirportFlightsDetailSerializer
from .views import AirportStatisticsPagination

from rest_framework import filters
from django.db.models import Count, F, FloatField, DurationField, IntegerField, Min, Subquery, OuterRef
from django.db.models.functions import Radians, Degrees, ACos, Cos, Sin, Least


class AllFlightsDetailApiView(ListAPIView):
    serializer_class = AirportFlightsDetailSerializer
    pagination_class = AirportStatisticsPagination
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['departure_airport__airport_name', 'arrival_airport__airport_name',
                       'distance_km', 'flight_time', 'flight_count', 'total_passenger_count']
    ordering = ['departure_airport__airport_name']

    def get_queryset(self):
        earth_radius_km = 6371

        base_queryset = Flights.objects.all().select_related(
            'departure_airport', 'arrival_airport', 'aircraft_code'
        )

        annotated_queryset = base_queryset.annotate(
            dep_lat_rad=Radians(F('departure_airport__latitude')),
            dep_lon_rad=Radians(F('departure_airport__longitude')),
            arr_lat_rad=Radians(F('arrival_airport__latitude')),
            arr_lon_rad=Radians(F('arrival_airport__longitude')),

            distance_km=ExpressionWrapper(
                earth_radius_km * Degrees(
                    ACos(
                        Least(
                            1.0,
                            Cos(F('dep_lat_rad')) * Cos(F('arr_lat_rad')) *
                            Cos(F('dep_lon_rad') - F('arr_lon_rad')) +
                            Sin(F('dep_lat_rad')) * Sin(F('arr_lat_rad'))
                        )
                    )
                ),
                output_field=FloatField()
            ),

            flight_time=ExpressionWrapper(
                F('scheduled_arrival') - F('scheduled_departure'),
                output_field=DurationField()
            ),
        )

        unique_routes = annotated_queryset.values('departure_airport', 'arrival_airport').annotate(
            min_flight_id=Min('flight_id'),
            flight_count=Count('flight_id')
        )

        flight_ids = [item['min_flight_id'] for item in unique_routes]

        route_passenger_counts = Flights.objects.values(
            'departure_airport', 'arrival_airport'
        ).annotate(
            total_passenger_count=Count('ticketflights__ticket_no')
        )

        total_passenger_subquery = route_passenger_counts.filter(
            departure_airport=OuterRef('departure_airport'),
            arrival_airport=OuterRef('arrival_airport')
        ).values('total_passenger_count')[:1]

        final_queryset = annotated_queryset.filter(
            flight_id__in=flight_ids
        ).annotate(
            passengers_count=Subquery(
                TicketFlights.objects.filter(flight=OuterRef('pk'))
                .values('flight')
                .annotate(count=Count('ticket_no'))
                .values('count'),
                output_field=IntegerField()
            ),
            flight_count=Subquery(
                unique_routes.filter(min_flight_id=OuterRef('flight_id')).values('flight_count'),
                output_field=IntegerField()
            ),
            total_passenger_count=Subquery(
                total_passenger_subquery,
                output_field=IntegerField()
            )
        )

        return final_queryset


class CategoryFlightsDetailApiView(ListAPIView):
    serializer_class = AirportFlightsDetailSerializer
    pagination_class = AirportStatisticsPagination

    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    ordering_fields = [
        'departure_airport__airport_name', 'arrival_airport__airport_name',
        'distance_km', 'flight_time', 'flight_count', 'total_passenger_count'
    ]
    ordering = ['arrival_airport__airport_name']

    def get_queryset(self):
        departure_airport = self.kwargs.get('departure_airport')
        earth_radius_km = 6371

        base_queryset = Flights.objects.filter(
            departure_airport=departure_airport
        ).select_related(
            'departure_airport', 'arrival_airport', 'aircraft_code'
        )

        annotated_queryset = base_queryset.annotate(
            # ❗ NOTE: joyi almashgan latitude/longitude
            dep_lat_rad=Radians(F('departure_airport__longitude')),
            dep_lon_rad=Radians(F('departure_airport__latitude')),
            arr_lat_rad=Radians(F('arrival_airport__longitude')),
            arr_lon_rad=Radians(F('arrival_airport__latitude')),

            delta_lat=Radians(F('arrival_airport__longitude') - F('departure_airport__longitude')),
            delta_lon=Radians(F('arrival_airport__latitude') - F('departure_airport__latitude')),

            a=ExpressionWrapper(
                Sin(F('delta_lat') / 2) ** 2 +
                Cos(F('dep_lat_rad')) * Cos(F('arr_lat_rad')) *
                Sin(F('delta_lon') / 2) ** 2,
                output_field=FloatField()
            ),
            c=ExpressionWrapper(
                2 * ATan2(Sqrt(F('a')), Sqrt(1 - F('a'))),
                output_field=FloatField()
            ),
            distance_km=ExpressionWrapper(
                earth_radius_km * F('c'),
                output_field=FloatField()
            ),
            flight_time=ExpressionWrapper(
                F('scheduled_arrival') - F('scheduled_departure'),
                output_field=DurationField()
            ),
        )

        unique_routes = annotated_queryset.values('departure_airport', 'arrival_airport').annotate(
            min_flight_id=Min('flight_id'),
            flight_count=Count('flight_id')
        )

        flight_ids = [item['min_flight_id'] for item in unique_routes]

        final_queryset = annotated_queryset.filter(
            flight_id__in=flight_ids
        ).annotate(
            passengers_count=Subquery(
                TicketFlights.objects.filter(flight=OuterRef('pk'))
                .values('flight')
                .annotate(count=Count('ticket_no'))
                .values('count'),
                output_field=IntegerField()
            ),
            flight_count=Subquery(
                unique_routes.filter(min_flight_id=OuterRef('flight_id')).values('flight_count'),
                output_field=IntegerField()
            ),
            total_passenger_count=Subquery(
                TicketFlights.objects.filter(
                    flight__departure_airport=OuterRef('departure_airport'),
                    flight__arrival_airport=OuterRef('arrival_airport')
                ).values('flight__departure_airport', 'flight__arrival_airport')
                .annotate(count=Count('ticket_no'))
                .values('count')[:1],
                output_field=IntegerField()
            )
        )

        return final_queryset
