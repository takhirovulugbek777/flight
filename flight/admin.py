from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register([AircraftsData, BoardingPasses, AirportsData,
                     Bookings, Flights, Seats, TicketFlights,
                     Tickets])
