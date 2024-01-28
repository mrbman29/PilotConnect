# connections/models.py

from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone
from django import forms


class AirportData(models.Model):
    country_code = models.CharField(max_length=2, default='US')
    iata = models.CharField(max_length=3)
    icao = models.CharField(max_length=4)
    airport = models.CharField(max_length=255)
    latitude = models.FloatField(default=0.0)
    longitude = models.FloatField(default=0.0)
    city = models.CharField(max_length=255)
    state = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.icao} - {self.airport} - {self.state}"

    @classmethod
    def get_airports_ordered_by_icao(cls):
        return cls.objects.order_by('icao')


class PilotProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    home_airport = models.ForeignKey(AirportData, on_delete=models.SET_NULL, null=True, blank=True)
    flight_hours = models.PositiveIntegerField(default=0)

    last_activity_date = models.DateTimeField(null=True, blank=True)

    # group as Certifications
    private_pilot = models.BooleanField(default=False)
    instrument_rating = models.BooleanField(default=False)
    commercial_pilot_single_engine = models.BooleanField(default=False)
    flight_instructor_cfi = models.BooleanField(default=False)
    flight_instructor_cfii = models.BooleanField(default=False)
    commercial_pilot_multi_engine = models.BooleanField(default=False)
    flight_instructor_multi_engine_mei = models.BooleanField(default=False)

    # group as Safety Pilot
    safety_pilot_need_vfr_single_engine = models.BooleanField(default=False)
    safety_pilot_need_ifr_single_engine = models.BooleanField(default=False)
    safety_pilot_need_ifr_multi_engine = models.BooleanField(default=False)
    safety_pilot_offer_vfr_single_engine = models.BooleanField(default=False)
    safety_pilot_offer_ifr_single_engine = models.BooleanField(default=False)
    safety_pilot_offer_ifr_multi_engine = models.BooleanField(default=False)

    # group as Instructor
    instructor_need_cfi = models.BooleanField(default=False)
    instructor_need_instrument_cfii = models.BooleanField(default=False)
    instructor_need_commercial_single_engine = models.BooleanField(default=False)
    instructor_need_commercial_multi_engine_mei = models.BooleanField(default=False)
    instructor_offer_cfi = models.BooleanField(default=False)
    instructor_offer_instrument_cfii = models.BooleanField(default=False)
    instructor_offer_commercial_single_engine = models.BooleanField(default=False)
    instructor_offer_commercial_multi_engine_mei = models.BooleanField(default=False)

    # group as Plane Rental
    rent_need_single_engine = models.BooleanField(default=False)
    rent_need_multi_engine = models.BooleanField(default=False)
    rent_offer_single_engine = models.BooleanField(default=False)
    rent_offer_multi_engine = models.BooleanField(default=False)

    # group as Comment
    comments = models.TextField(null=True, blank=True)

    def update_last_activity(self):
        self.last_activity_date = timezone.now()
        self.save()

    def __str__(self):
        return f"{self.user.username}'s Pilot Profile"


class Message(models.Model):
    sender = models.ForeignKey(User, related_name='sent_messages', on_delete=models.CASCADE)
    recipient = models.ForeignKey(User, related_name='received_messages', on_delete=models.CASCADE)
    subject = models.CharField(max_length=255)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    deleted_for_user = models.ManyToManyField(User, related_name='deleted_messages', blank=True)

    def __str__(self):
        return f"{self.sender} to {self.recipient} - {self.subject}"


class PilotEvent(models.Model):
    event_name = models.CharField(max_length=500)
    event_start_date = models.DateField()
    event_finish_date = models.DateField()
    host_airport = models.ForeignKey(AirportData, on_delete=models.CASCADE, blank=True, null=True, related_name='host_airport_events')
    second_airport = models.ForeignKey(AirportData, on_delete=models.CASCADE, blank=True, null=True, related_name='second_airport_events')
    third_airport = models.ForeignKey(AirportData, on_delete=models.CASCADE, blank=True, null=True, related_name='third_airport_events')
    host_name = models.ForeignKey(User, on_delete=models.CASCADE)  # ForeignKey to User
    event_description = models.TextField()

    def __str__(self):

        return f"{self.event_name} - {self.event_start_date} - {self.host_name}"

class PilotEventForm(forms.ModelForm):
    class Meta:
        model = PilotEvent
        fields = ['event_name', 'event_start_date', 'host_airport', 'host_name', 'event_description']