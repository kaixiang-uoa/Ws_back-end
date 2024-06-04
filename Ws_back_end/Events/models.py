from django.db import models
from Users.models import Ws_User

class Event(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    location = models.CharField(max_length=255)
    organizer = models.ForeignKey(Ws_User, on_delete=models.CASCADE)
    is_approved = models.BooleanField(default=False)
    image = models.ForeignKey('EventImage', null=True, blank=True, on_delete=models.SET_NULL, related_name='event_image')
    status = models.CharField(max_length=20, choices=[('pending', 'Pending'), ('approved', 'Approved'), ('rejected', 'Rejected')], default='pending')
    def __str__(self):
        return self.title

class EventImage(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='images', null=True, blank=True)
    image_path = models.ImageField(upload_to='event_images/')

    def __str__(self):
        return f"{self.event.title if self.event else 'Unassigned'} Image"
    

class UserEvent(models.Model):
    user = models.ForeignKey(Ws_User, on_delete=models.CASCADE, related_name='events')
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='participants')
    registered_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'event')

    def __str__(self):
        return f"{self.user.username} registered for {self.event.title}"