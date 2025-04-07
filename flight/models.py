from django.db import models
from django.utils.translation import get_language
from django.contrib.gis.db import models as gis_models


class AircraftsData(models.Model):
    aircraft_code = models.CharField(primary_key=True, max_length=3, db_comment='Aircraft code, IATA')
    model = models.JSONField(db_comment='Aircraft model')
    range = models.IntegerField(db_comment='Maximal flying distance, km')

    class Meta:
        managed = False
        db_table = 'aircrafts_data'
        db_table_comment = 'Aircrafts (internal data)'


class AirportsData(models.Model):
    airport_code = models.CharField(primary_key=True, max_length=3, db_comment='Airport code')
    airport_name = models.JSONField(db_comment='Airport name')
    city = models.JSONField(db_comment='City')

    coordinates = models.TextField(db_comment='Airport coordinates (longitude and latitude)')

    latitude = models.FloatField(null=True, db_comment='Airport latitude')
    longitude = models.FloatField(null=True, db_comment='Airport longitude')
    timezone = models.TextField(db_comment='Airport time zone')

    class Meta:
        managed = False
        db_table = 'airports_data'
        db_table_comment = 'Airports (internal data)'

    def to_dict(self):
        lang = get_language()
        return self.airport_name[lang]


class BoardingPasses(models.Model):
    ticket_no = models.OneToOneField('TicketFlights', models.DO_NOTHING, db_column='ticket_no', primary_key=True,
                                     db_comment='Ticket number')  # The composite primary key (ticket_no, flight_id) found, that is not supported. The first column is selected.
    flight_id = models.IntegerField(db_comment='Flight ID')
    boarding_no = models.IntegerField(db_comment='Boarding pass number')
    seat_no = models.CharField(max_length=4, db_comment='Seat number')

    class Meta:
        managed = False
        db_table = 'boarding_passes'
        unique_together = (('flight_id', 'boarding_no'), ('flight_id', 'seat_no'), ('ticket_no', 'flight_id'),)
        db_table_comment = 'Boarding passes'


class Bookings(models.Model):
    book_ref = models.CharField(primary_key=True, max_length=6, db_comment='Booking number')
    book_date = models.DateTimeField(db_comment='Booking date')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, db_comment='Total booking cost')

    class Meta:
        managed = False
        db_table = 'bookings'
        db_table_comment = 'Bookings'


class Flights(models.Model):
    flight_id = models.AutoField(primary_key=True, db_comment='Flight ID')
    flight_no = models.CharField(max_length=6, db_comment='Flight number')
    scheduled_departure = models.DateTimeField(db_comment='Scheduled departure time')
    scheduled_arrival = models.DateTimeField(db_comment='Scheduled arrival time')
    departure_airport = models.ForeignKey(AirportsData, models.DO_NOTHING, db_column='departure_airport',
                                          db_comment='Airport of departure')
    arrival_airport = models.ForeignKey(AirportsData, models.DO_NOTHING, db_column='arrival_airport',
                                        related_name='flights_arrival_airport_set', db_comment='Airport of arrival')
    status = models.CharField(max_length=20, db_comment='Flight status')
    aircraft_code = models.ForeignKey(AircraftsData, models.DO_NOTHING, db_column='aircraft_code',
                                      db_comment='Aircraft code, IATA')
    actual_departure = models.DateTimeField(blank=True, null=True, db_comment='Actual departure time')
    actual_arrival = models.DateTimeField(blank=True, null=True, db_comment='Actual arrival time')

    class Meta:
        managed = False
        db_table = 'flights'
        unique_together = (('flight_no', 'scheduled_departure'),)
        db_table_comment = 'Flights'


class Seats(models.Model):
    aircraft_code = models.OneToOneField(AircraftsData, models.DO_NOTHING, db_column='aircraft_code', primary_key=True,
                                         db_comment='Aircraft code, IATA')  # The composite primary key (aircraft_code, seat_no) found, that is not supported. The first column is selected.
    seat_no = models.CharField(max_length=4, db_comment='Seat number')
    fare_conditions = models.CharField(max_length=10, db_comment='Travel class')

    class Meta:
        managed = False
        db_table = 'seats'
        unique_together = (('aircraft_code', 'seat_no'),)
        db_table_comment = 'Seats'


class TicketFlights(models.Model):
    ticket_no = models.OneToOneField('Tickets', models.DO_NOTHING, db_column='ticket_no', primary_key=True,
                                     db_comment='Ticket number')  # The composite primary key (ticket_no, flight_id) found, that is not supported. The first column is selected.
    flight = models.ForeignKey(Flights, models.DO_NOTHING, db_comment='Flight ID')
    fare_conditions = models.CharField(max_length=10, db_comment='Travel class')
    amount = models.DecimalField(max_digits=10, decimal_places=2, db_comment='Travel cost')

    class Meta:
        managed = False
        db_table = 'ticket_flights'
        unique_together = (('ticket_no', 'flight'),)
        db_table_comment = 'Flight segment'


class Tickets(models.Model):
    ticket_no = models.CharField(primary_key=True, max_length=13, db_comment='Ticket number')
    book_ref = models.ForeignKey(Bookings, models.DO_NOTHING, db_column='book_ref', db_comment='Booking number')
    passenger_id = models.CharField(max_length=20, db_comment='Passenger ID')
    passenger_name = models.TextField(db_comment='Passenger name')
    contact_data = models.JSONField(blank=True, null=True, db_comment='Passenger contact information')

    class Meta:
        managed = False
        db_table = 'tickets'
        db_table_comment = 'Tickets'
