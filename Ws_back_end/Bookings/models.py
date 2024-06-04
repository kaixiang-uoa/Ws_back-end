from django.db import models
from Users.models import Ws_User

class Booking(models.Model):
    user = models.ForeignKey(Ws_User, on_delete=models.CASCADE, related_name='bookings')
    professor = models.ForeignKey(Ws_User, on_delete=models.CASCADE, related_name='professor_bookings')
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=[('pending', 'Pending'), ('approved', 'Approved')], default='pending')
    additional_email = models.EmailField(blank=True, null=True)

    def __str__(self):
        return f"{self.user.username} booked {self.professor.username} from {self.start_time} to {self.end_time}"
