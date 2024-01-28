# connections/forms.py
from django import forms
from .models import PilotProfile, AirportData, Message, PilotEvent
from django.contrib.auth.models import User
from django.forms import DateInput


class PilotProfileForm(forms.ModelForm):
    class Meta:
        model = PilotProfile
        exclude = ('user',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Customize the choices for home_airport
        airports = AirportData.objects.all().order_by('icao')
        self.fields['home_airport'].queryset = airports


class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['subject', 'content', 'recipient']

        widgets = {
            'subject': forms.TextInput(attrs={'class': 'custom-subject-input'}),
            'content': forms.Textarea(attrs={'class': 'custom-content-input'}),
        }

    def __init__(self, *args, recipient_readonly=False, **kwargs):
        super().__init__(*args, **kwargs)
        if recipient_readonly:
            self.fields['recipient'].widget = forms.HiddenInput()



class MessageReplyForm(forms.Form):
    content = forms.CharField(widget=forms.Textarea)


class PilotEventForm(forms.ModelForm):
    class Meta:
        model = PilotEvent
        fields = ['event_name', 'event_start_date', 'event_finish_date', 'host_airport', 'second_airport', 'third_airport', 'event_description']

        widgets = {
            'event_start_date': forms.DateInput(attrs={'type': 'date'}),
            'event_finish_date': forms.DateInput(attrs={'type': 'date'}),
            'event_description': forms.Textarea(attrs={'class': 'custom-event-description-input', 'style': 'width: 66.666%'}),
        }

    event_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'custom-event-name-input', 'style': 'width: 66.666%'}))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Order the airport choices alphabetically
        self.fields['host_airport'].queryset = AirportData.objects.order_by('icao')
        self.fields['second_airport'].queryset = AirportData.objects.order_by('icao')
        self.fields['third_airport'].queryset = AirportData.objects.order_by('icao')