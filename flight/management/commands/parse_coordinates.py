from django.core.management import BaseCommand

from flight.models import AirportsData


class Command(BaseCommand):
    help = 'Parse coordinates from text field to latitude and longitude fields'

    def handle(self, *args, **options):
        self.stdout.write('Начинаем парсинг координат...')

        airports = AirportsData.objects.all()
        success_count = 0
        error_count = 0

        for airport in airports:
            try:
                coords_text = airport.coordinates.strip()  # Bo'sh joylarni olib tashlash

                # Koordinatalarni qavs va vergulni olib tashlab olish
                coords_text = coords_text.replace("(", "").replace(")", "")
                lon, lat = map(float, coords_text.split(","))  # Vergul bilan ajratib olish

                # Ma'lumotlarni saqlash
                airport.longitude = lon
                airport.latitude = lat
                airport.save(update_fields=['longitude', 'latitude'])
                success_count += 1
                self.stdout.write(f"Обработан аэропорт {airport.airport_code}: lon={lon}, lat={lat}")

            except Exception as e:
                error_count += 1
                self.stdout.write(self.style.ERROR(
                    f"Ошибка при обработке аэропорта {airport.airport_code}: {e}"
                ))

        self.stdout.write(self.style.SUCCESS(
            f'Парсинг завершен! Успешно: {success_count}, с ошибками: {error_count}'
        ))
