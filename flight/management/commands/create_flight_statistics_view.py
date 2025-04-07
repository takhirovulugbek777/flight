from django.core.management.base import BaseCommand
from django.db import connection


class Command(BaseCommand):
    help = 'Create materialized view flight_statistics'

    def handle(self, *args, **options):
        with connection.cursor() as cursor:
            cursor.execute("""
                CREATE MATERIALIZED VIEW IF NOT EXISTS flight_statistics AS
                SELECT
                    f.flight_id,
                    f.flight_no,
                    f.scheduled_departure,
                    f.scheduled_arrival,
                    f.departure_airport,
                    f.arrival_airport,
                    f.status,
                    f.aircraft_code,
                    f.actual_departure,
                    f.actual_arrival,
                    COUNT(tf.ticket_no) AS passengers_count
                FROM flights f
                LEFT JOIN ticket_flights tf ON f.flight_id = tf.flight_id
                GROUP BY
                    f.flight_id, f.flight_no, f.scheduled_departure, f.scheduled_arrival,
                    f.departure_airport, f.arrival_airport, f.status, f.aircraft_code,
                    f.actual_departure, f.actual_arrival;

                CREATE INDEX IF NOT EXISTS idx_flight_statistics_departure_airport 
                ON flight_statistics (departure_airport);

                CREATE INDEX IF NOT EXISTS idx_flight_statistics_arrival_airport 
                ON flight_statistics (arrival_airport);
            """)
            self.stdout.write(self.style.SUCCESS('Materialized view created successfully.'))
