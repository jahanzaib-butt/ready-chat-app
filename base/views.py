from django.shortcuts import render, redirect, get_object_or_404
from .models import Room, Message
from django.db.models import Max, Prefetch
# from django.contrib.auth.decorators import login_required
from .forms import RoomForm
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from django.views.decorators.http import require_POST
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.contrib.auth.models import User
from django.contrib.auth import logout

def home(request):
    rooms = Room.objects.annotate(
        last_message_time=Max('messages__created')
    ).prefetch_related(
        Prefetch('messages', 
                 queryset=Message.objects.order_by('-created'),
                 to_attr='recent_messages')
    ).order_by('-last_message_time')

    for room in rooms:
        room.latest_message = room.recent_messages[0] if room.recent_messages else None

    context = {'rooms': rooms}
    return render(request, 'base/home.html', context)


# @login_required(login_url='login')  # Specify the login URL
def create_room(request):
    if request.method == 'POST':
        form = RoomForm(request.POST)
        if form.is_valid():
            room = form.save(commit=False)
            if not room.host:
                room.host = request.user  # Set the host to the current user if not specified
            room.save()
            return redirect('home')  # or wherever you want to redirect after creation
    else:
        form = RoomForm(initial={'host': request.user})  # Pre-fill with current user
    hosts = User.objects.all()  # Get all users for the host dropdown
    return render(request, 'base/room_form.html', {'form': form, 'hosts': hosts})


def room(request, pk):
    room = get_object_or_404(Room, id=pk)
    room_messages = room.messages.all().order_by('-created')
    
    if request.method == 'POST':
        body = request.POST.get('body')
        if body:
            Message.objects.create(
                user=request.user if request.user.is_authenticated else None,
                room=room,
                body=body
            )
            room.last_activity = timezone.now()
            room.save()
            return redirect('room', pk=room.id)
        # else:
        #     messages.error(request, 'Message cannot be empty.')
    
    context = {'room': room, 'room_messages': room_messages}
    return render(request, 'base/room.html', context)

def get_messages(request, room_id):
    try:
        messages = Message.objects.filter(room_id=room_id).order_by('created')
        messages_data = [
            {
                'id': message.id,
                'user': message.user.username,
                'body': message.body,
                'created': message.created.isoformat()  # Convert to ISO format string
            } for message in messages
        ]
        return JsonResponse({'messages': messages_data})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


@csrf_exempt
@login_required
def send_message(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            room_id = data.get('room_id')
            message_text = data.get('message')
            
            room = Room.objects.get(id=room_id)
            message = Message.objects.create(
                room=room,
                user=request.user,
                body=message_text
            )
            
            return JsonResponse({'status': 'success', 'message': 'Message sent successfully'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=400)


def get_room_details(request, room_id):
    try:
        room = Room.objects.get(id=room_id)
        data = {
            'name': room.name,
            'host': room.host.username if room.host else 'Anonymous',
            'description': room.description or 'No description available'
        }
        return JsonResponse(data)
    except Room.DoesNotExist:
        return JsonResponse({'error': 'Room not found'}, status=404)


def get_rooms(request):
    rooms = Room.objects.annotate(
        last_message_time=Max('messages__created')
    ).prefetch_related(
        Prefetch('messages', 
                 queryset=Message.objects.order_by('-created'),
                 to_attr='recent_messages')
    ).order_by('-last_message_time')

    rooms_data = []
    for room in rooms:
        latest_message = room.recent_messages[0] if room.recent_messages else None
        rooms_data.append({
            'id': room.id,
            'name': room.name,
            'host': room.host.username if room.host else 'Anonymous',
            'description': room.description,
            'latest_message': {
                'user': latest_message.user.username if latest_message and latest_message.user else 'Anonymous',
                'body': latest_message.body if latest_message else '',
                'created': latest_message.created.isoformat() if latest_message else None
            } if latest_message else None
        })

    return JsonResponse({'rooms': rooms_data})


@require_POST
def delete_room(request, room_id):
    room = get_object_or_404(Room, id=room_id)
    
    # Check if the user has permission to delete the room
    if request.user == room.host or request.user.is_staff:
        room.delete()
        return JsonResponse({'status': 'success', 'message': 'Room deleted successfully'})
    else:
        return JsonResponse({'status': 'error', 'message': 'You do not have permission to delete this room'}, status=403)

def room_list(request):
    rooms = Room.objects.all()  # This will use the ordering from the model
    return render(request, 'room_list.html', {'rooms': rooms})

@login_required
def room_message(request, room_id):
    if not request.user.is_authenticated:
        return HttpResponseForbidden("You must be logged in to send messages.")
    
    # ... existing code for handling room messages ...

@login_required
def createRoom(request):
    form = RoomForm()
    if request.method == 'POST':
        form = RoomForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('home')
    
    context = {'form': form}
    return render(request, 'base/room_form.html', context)

def logout_user(request):
    logout(request)
    return redirect('home')  # Redirect to your home page or login page