

# connections/admin.py

from django.contrib import admin
from .models import AirportData, PilotProfile, Message, PilotEvent

class AirportDataAdmin(admin.ModelAdmin):
    list_display = ('icao', 'airport', 'state', 'city')
    search_fields = ('icao', 'airport', 'state', 'city')

admin.site.register(AirportData, AirportDataAdmin)

class PilotProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'home_airport', 'flight_hours', 'last_activity_date')
    search_fields = ('user__username', 'home_airport__airport', 'flight_hours')
    list_filter = ('last_activity_date', 'private_pilot', 'instrument_rating', 'commercial_pilot_single_engine')

admin.site.register(PilotProfile, PilotProfileAdmin)

class MessageAdmin(admin.ModelAdmin):
    list_display = ('sender', 'recipient', 'subject', 'timestamp')
    search_fields = ('sender__username', 'recipient__username', 'subject')
    list_filter = ('timestamp',)

admin.site.register(Message, MessageAdmin)

class PilotEventAdmin(admin.ModelAdmin):
    list_display = ('event_name', 'event_start_date', 'host_airport', 'host_name')
    search_fields = ('event_name', 'host_airport__airport', 'host_name__username')
    list_filter = ('event_start_date', 'host_airport', 'host_name')

admin.site.register(PilotEvent, PilotEventAdmin)
