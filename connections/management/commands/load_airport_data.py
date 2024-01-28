# pilotconnect/connections/management/commands/load_airport_data.py
import pandas as pd
from django.core.management.base import BaseCommand
from connections.models import AirportData

class Command(BaseCommand):
    help = 'Load data from Excel file to AirportData model'

    def handle(self, *args, **kwargs):
        excel_path = "C:\\Users\\b.conley\\PycharmProjects\\PilotConnect\\airport codes.xlsx"

        try:
            df = pd.read_excel(excel_path)
            for _, row in df.iterrows():
                AirportData.objects.create(
                    country_code=row['country_code'],
                    iata=row['iata'],
                    icao=row['icao'],
                    airport=row['airport'],
                    latitude=row['latitude'],
                    longitude=row['longitude'],
                    city=row['city'],
                    state=row['state']
                )
            self.stdout.write(self.style.SUCCESS('Data loaded successfully.'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error loading data: {e}'))
