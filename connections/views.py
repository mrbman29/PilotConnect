#connections/views.py

from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.http import HttpResponseForbidden
from django.db.models import Q
from django.db import models
from django.views.generic.base import View  # Corrected import statement
from django.views.generic.edit import CreateView
from django.views.generic.list import ListView
from django.urls import reverse_lazy
from .forms import PilotProfileForm, MessageForm, MessageReplyForm, PilotEventForm
from .models import PilotProfile, AirportData, Message, PilotEvent

def welcome(request):
    return render(request, 'connections/welcome.html')

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}!')
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'connections/registration/register.html', {'form': form})

def user_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user:
                login(request, user)
                return redirect('home')
    else:
        form = AuthenticationForm()
    return render(request, 'connections/registration/login.html', {'form': form})

@login_required
def user_logout(request):
    logout(request)
    return redirect('welcome')

@login_required
def home(request):
    return render(request, 'connections/home.html', {'user': request.user})

@login_required
def update_pilot_profile(request):
    # Get the current user's pilot profile or create one if it doesn't exist
    pilot_profile, created = PilotProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = PilotProfileForm(request.POST, instance=pilot_profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Pilot profile updated successfully.')
            return redirect('home')  # Replace with the desired redirect URL
    else:
        form = PilotProfileForm(instance=pilot_profile)

    return render(request, 'connections/update_pilot_profile.html', {'form': form})





@login_required
def airport_list(request):
    airports = AirportData.get_airports_ordered_by_icao()
    return render(request, 'connections/airport_list.html', {'airports': airports})

@login_required
def airport_list_by_state(request):
    user_home_state = request.user.pilotprofile.home_airport.state if hasattr(request.user, 'pilotprofile') else None

    if user_home_state:
        airports = AirportData.objects.filter(state=user_home_state).order_by('icao')
        return render(
            request,
            'connections/airport_list_by_state.html',
            {'airports': airports, 'user_home_state': user_home_state}
        )
    else:
        messages.warning(request, 'Please set your home airport and try again.')
        return redirect('update_pilot_profile')

@login_required
def user_list(request):
    users = User.objects.all().order_by('username')  # Order users alphabetically by username
    return render(
        request,
        'connections/user_list.html',
        {'users': users}
    )

@login_required
def user_list_by_state(request):
    # Get the current user's home airport state
    user_state = request.user.pilotprofile.home_airport.state

    # Filter users based on the home airport state
    users = User.objects.filter(pilotprofile__home_airport__state=user_state)

    return render(request, 'connections/user_list_by_state.html', {'users': users})

@login_required
def users_same_airport(request):
    current_user = request.user
    users_same_airport = User.objects.filter(
        pilotprofile__home_airport=current_user.pilotprofile.home_airport
    ).exclude(id=current_user.id).order_by('username')

    return render(request, 'connections/users_same_airport.html', {'users': users_same_airport})

@login_required
def view_pilot_profile(request, user_id):
    user = get_object_or_404(User, id=user_id)
    # You can customize this function to retrieve additional information about the user if needed
    return render(request, 'connections/view_pilot_profile.html', {'user': user})

@login_required
def send_message(request, recipient_id):
    recipient = get_object_or_404(User, id=recipient_id)

    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            subject = form.cleaned_data['subject']
            content = form.cleaned_data['content']

            Message.objects.create(
                sender=request.user,
                recipient=recipient,
                subject=subject,
                content=content
            )

            messages.success(request, 'Message sent successfully.')
            return redirect('view_messages')
    else:
        # Pre-fill the recipient field and make it read-only
        form = MessageForm(initial={'recipient': recipient}, recipient_readonly=True)

    return render(request, 'connections/send_message.html', {'form': form, 'recipient': recipient})

@login_required
def view_messages(request):
    received_messages = Message.objects.filter(recipient=request.user).order_by('-timestamp')
    sent_messages = Message.objects.filter(sender=request.user).order_by('-timestamp')

    return render(request, 'connections/view_messages.html', {'received_messages': received_messages, 'sent_messages': sent_messages})



@login_required
def send_reply(request, message_id):
    original_message = get_object_or_404(Message, id=message_id)

    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            subject = form.cleaned_data['subject']
            content = form.cleaned_data['content']

            Message.objects.create(
                sender=request.user,
                recipient=original_message.sender,
                subject=subject,
                content=content
            )

            messages.success(request, 'Reply sent successfully.')
            return redirect('view_messages')
    else:
        # Pre-fill the subject and recipient fields in the reply form
        form = MessageForm(initial={'subject': f"Re: {original_message.subject}", 'recipient': original_message.sender}, recipient_readonly=True)

    return render(request, 'connections/send_message.html', {'form': form, 'recipient': original_message.sender})


@login_required
def create_pilot_event(request):
    if request.method == 'POST':
        form = PilotEventForm(request.POST)
        if form.is_valid():
            pilot_event = form.save(commit=False)
            pilot_event.host_name = request.user  # Assign the User instance directly
            pilot_event.save()
            return redirect('event_list')
    else:
        form = PilotEventForm()

    return render(request, 'connections/create_pilot_event.html', {'form': form})



def event_list(request):
    # Retrieve the list of events from the database
    current_time = timezone.now()
    events = PilotEvent.objects.filter(event_finish_date__gte=current_time).order_by('event_start_date')

    # Render the event list template with the events
    return render(request, 'connections/event_list.html', {'events': events})


def view_pilot_event(request, event_name):
    pilot_event = get_object_or_404(PilotEvent, event_name=event_name)
    return render(request, 'connections/view_pilot_event.html', {'pilot_event': pilot_event})


@login_required
def user_hosted_events(request):
    user = request.user
    hosted_events = PilotEvent.objects.filter(host_name=user, event_finish_date__gte='2024-01-15')
    return render(request, 'connections/user_hosted_events.html', {'user': user, 'hosted_events': hosted_events})


@login_required
def edit_pilot_event(request, event_id):
    # Retrieve the pilot event object
    pilot_event = get_object_or_404(PilotEvent, id=event_id)

    # Check if the current user is the host of the event
    if request.user != pilot_event.host_name:
        # You may want to handle this case, e.g., redirect to a different page
        return render(request, 'connections/access_denied.html')

    if request.method == 'POST':
        # Process the form data and update the pilot event
        form = PilotEventForm(request.POST, instance=pilot_event)
        if form.is_valid():
            form.save()
            return redirect('user_hosted_events')
    else:
        # Display the form with the current pilot event data
        form = PilotEventForm(instance=pilot_event)

    return render(request, 'connections/edit_pilot_event.html', {'form': form, 'event': pilot_event})



@login_required
def delete_pilot_event(request, event_id):
    # Retrieve the pilot event object
    pilot_event = get_object_or_404(PilotEvent, id=event_id)

    # Check if the current user is the host of the event
    if request.user != pilot_event.host_name:
        # You may want to handle this case, e.g., redirect to a different page
        return render(request, 'connections/access_denied.html')

    # Delete the pilot event
    pilot_event.delete()

    # Redirect to the user-hosted events page
    return redirect('user_hosted_events')


class EventListByStateView(ListView):
    model = PilotEvent
    template_name = 'connections/event_list_by_state.html'
    context_object_name = 'events'
    ordering = ['event_start_date']

    def get_queryset(self):
        user_state = self.request.user.pilotprofile.home_airport.state
        return PilotEvent.objects.filter(
            models.Q(host_airport__state=user_state) |
            models.Q(second_airport__state=user_state) |
            models.Q(third_airport__state=user_state)
        ).order_by('event_start_date')



class SafetyPilotListView(ListView):
    model = PilotProfile
    template_name = 'connections/safety_pilot_list.html'

    def get_queryset(self):
        # Corrected field name for safety_pilot_need_vfr_multi_engine
        return PilotProfile.objects.filter(
            Q(safety_pilot_need_vfr_single_engine=True) |
            Q(safety_pilot_need_ifr_single_engine=True) |
            Q(safety_pilot_need_ifr_multi_engine=True)
        )



class SafetyPilotListViewByState(ListView):
    model = PilotProfile
    template_name = 'connections/safety_pilot_list_by_state.html'  # Create this template

    def get_queryset(self):
        user_state = self.request.user.pilotprofile.home_airport.state  # Assuming the state is stored in the 'state' field

        # Filter profiles based on the user's state
        return PilotProfile.objects.filter(
            Q(safety_pilot_need_vfr_single_engine=True, user__pilotprofile__home_airport__state=user_state) |
            Q(safety_pilot_need_ifr_single_engine=True, user__pilotprofile__home_airport__state=user_state) |
            Q(safety_pilot_need_ifr_multi_engine=True, user__pilotprofile__home_airport__state=user_state)
        )


class SafetyPilotListByHomeAirportView(ListView):
    model = PilotProfile
    template_name = 'connections/safety_pilot_list_by_home_airport.html'

    def get_queryset(self):
        user_home_airport = self.request.user.pilotprofile.home_airport
        return PilotProfile.objects.filter(
            Q(safety_pilot_need_vfr_single_engine=True, home_airport=user_home_airport) |
            Q(safety_pilot_need_ifr_single_engine=True, home_airport=user_home_airport) |
            Q(safety_pilot_need_ifr_multi_engine=True, home_airport=user_home_airport)
        )


class SafetyPilotListOfferingView(ListView):
    model = PilotProfile
    template_name = 'connections/safety_pilot_list_offering.html'

    def get_queryset(self):
        return PilotProfile.objects.filter(
            Q(safety_pilot_offer_vfr_single_engine=True) |
            Q(safety_pilot_offer_ifr_single_engine=True) |
            Q(safety_pilot_offer_ifr_multi_engine=True)
        )


class SafetyPilotListOfferingByStateView(ListView):
    model = PilotProfile
    template_name = 'connections/safety_pilot_list_offering_by_state.html'  # You can create a new template if needed

    def get_queryset(self):
        # Filter Safety Pilots offering by the user's home state
        user_state = self.request.user.pilotprofile.home_airport.state
        return PilotProfile.objects.filter(
            Q(safety_pilot_offer_vfr_single_engine=True, user__pilotprofile__home_airport__state=user_state) |
            Q(safety_pilot_offer_ifr_single_engine=True, user__pilotprofile__home_airport__state=user_state) |
            Q(safety_pilot_offer_ifr_multi_engine=True, user__pilotprofile__home_airport__state=user_state)
        )


class SafetyPilotListOfferingByAirportView(ListView):
    model = PilotProfile
    template_name = 'connections/safety_pilot_list_offering_by_airport.html'  # Adjust this to your template path


    def get_queryset(self):
        # Retrieve safety pilots offering by airport (customize this based on your model and logic)
        user_home_airport = self.request.user.pilotprofile.home_airport
        return PilotProfile.objects.filter(
            Q(safety_pilot_offer_vfr_single_engine=True, home_airport=user_home_airport) |
            Q(safety_pilot_offer_ifr_single_engine=True, home_airport=user_home_airport) |
            Q(safety_pilot_offer_ifr_multi_engine=True, home_airport=user_home_airport)
        )


class InstructorListView(ListView):
    model = PilotProfile
    template_name = 'connections/instructor_list.html'
    context_object_name = 'instructors'

    def get_queryset(self):
        return PilotProfile.objects.filter(
            Q(instructor_need_cfi=True) |
            Q(instructor_need_instrument_cfii=True) |
            Q(instructor_need_commercial_single_engine=True) |
            Q(instructor_need_commercial_multi_engine_mei=True) |
            Q(instructor_offer_cfi=True) |
            Q(instructor_offer_instrument_cfii=True) |
            Q(instructor_offer_commercial_single_engine=True) |
            Q(instructor_offer_commercial_multi_engine_mei=True)
        )




class InstructorListViewByState(ListView):
    model = PilotProfile
    template_name = 'connections/instructor_list_by_state.html'


    def get_queryset(self):
        user_state = self.request.user.pilotprofile.home_airport.state
        return PilotProfile.objects.filter(
            Q(instructor_need_cfi=True, user__pilotprofile__home_airport__state=user_state) |
            Q(instructor_need_instrument_cfii=True, user__pilotprofile__home_airport__state=user_state) |
            Q(instructor_need_commercial_single_engine=True, user__pilotprofile__home_airport__state=user_state) |
            Q(instructor_need_commercial_multi_engine_mei=True, user__pilotprofile__home_airport__state=user_state) |
            Q(instructor_offer_cfi=True, user__pilotprofile__home_airport__state=user_state) |
            Q(instructor_offer_instrument_cfii=True, user__pilotprofile__home_airport__state=user_state) |
            Q(instructor_offer_commercial_single_engine=True, user__pilotprofile__home_airport__state=user_state) |
            Q(instructor_offer_commercial_multi_engine_mei=True, user__pilotprofile__home_airport__state=user_state)
        )

class InstructorListByHomeAirportView(ListView):
    model = PilotProfile
    template_name = 'connections/instructor_list_by_home_airport.html'

    def get_queryset(self):
        user_home_airport = self.request.user.pilotprofile.home_airport
        return PilotProfile.objects.filter(

            Q(instructor_need_cfi=True, home_airport=user_home_airport) |
            Q(instructor_need_instrument_cfii=True, home_airport=user_home_airport) |
            Q(instructor_need_commercial_single_engine=True, home_airport=user_home_airport) |
            Q(instructor_need_commercial_multi_engine_mei=True, home_airport=user_home_airport) |
            Q(instructor_offer_cfi=True, home_airport=user_home_airport) |
            Q(instructor_offer_instrument_cfii=True, home_airport=user_home_airport) |
            Q(instructor_offer_commercial_single_engine=True, home_airport=user_home_airport) |
            Q(instructor_offer_commercial_multi_engine_mei=True, home_airport=user_home_airport)

        )


class InstructorListOfferingView(ListView):
    model = PilotProfile
    template_name = 'connections/instructor_list_offering.html'
    context_object_name = 'instructors'

    def get_queryset(self):
        return PilotProfile.objects.filter(
            Q(instructor_offer_cfi=True) |
            Q(instructor_offer_instrument_cfii=True) |
            Q(instructor_offer_commercial_single_engine=True) |
            Q(instructor_offer_commercial_multi_engine_mei=True)
        )


class InstructorListOfferingByStateView(ListView):
    model = PilotProfile
    template_name = 'connections/instructor_list_offering_by_state.html'
    context_object_name = 'instructors'

    def get_queryset(self):
        user_state = self.request.user.pilotprofile.home_airport.state
        return PilotProfile.objects.filter(
            Q(instructor_offer_cfi=True, user__pilotprofile__home_airport__state=user_state) |
            Q(instructor_offer_instrument_cfii=True, user__pilotprofile__home_airport__state=user_state) |
            Q(instructor_offer_commercial_single_engine=True, user__pilotprofile__home_airport__state=user_state) |
            Q(instructor_offer_commercial_multi_engine_mei=True, user__pilotprofile__home_airport__state=user_state)
        )

class InstructorListOfferingByHomeAirportView(ListView):
    model = PilotProfile
    template_name = 'connections/instructor_list_offering_by_home_airport.html'
    context_object_name = 'instructors'

    def get_queryset(self):
        user_home_airport = self.request.user.pilotprofile.home_airport
        return PilotProfile.objects.filter(
            Q(instructor_offer_cfi=True, home_airport=user_home_airport) |
            Q(instructor_offer_instrument_cfii=True, home_airport=user_home_airport) |
            Q(instructor_offer_commercial_single_engine=True, home_airport=user_home_airport) |
            Q(instructor_offer_commercial_multi_engine_mei=True, home_airport=user_home_airport)
        )