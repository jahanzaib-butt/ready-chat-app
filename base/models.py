from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Room(models.Model):
    name = models.CharField(max_length=100)
    host = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='hosted_rooms')
    description = models.TextField(null=True, blank=True)
    participants = models.ManyToManyField(User, related_name='rooms', blank=True)
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)
    last_activity = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-last_activity']  # This will order rooms by last activity

    def __str__(self):
        return self.name

class Message(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='messages')
    room = models.ForeignKey(Room, on_delete=models.CASCADE, null=False, blank=False, related_name='messages', default=1)
    body = models.TextField()
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created']

    def __str__(self):
        return f"{self.user.username if self.user else 'Anonymous'}: {self.body[:50]}"