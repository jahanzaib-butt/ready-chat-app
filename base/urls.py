from django.urls import path
from django.contrib.auth.decorators import login_required
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('room/<str:pk>/', views.room, name='room'),
    path('create-room/', views.createRoom, name='create-room'),
    path('api/messages/<str:room_id>/', views.get_messages, name='get_messages'),
    path('api/room/<str:room_id>/', views.get_room_details, name='get_room_details'),
    path('api/rooms/', views.get_rooms, name='get_rooms'),
    path('api/delete-room/<str:room_id>/', views.delete_room, name='delete_room'),
    path('api/send-message/', login_required(views.send_message), name='send_message'),
    path('room/<int:room_id>/message/', login_required(views.room_message), name='room_message'),
    path('logout/', views.logout_user, name='logout'),
]
