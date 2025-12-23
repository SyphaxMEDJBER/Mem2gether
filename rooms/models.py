from django.db import models
from django.contrib.auth.models import User

class Room(models.Model):
    MODE_CHOICES = (
        ("photos", "Photos"),
        ("youtube", "YouTube"),
    )

    room_id = models.CharField(max_length=20, unique=True, primary_key=True)
    created_at = models.DateTimeField(auto_now_add=True)
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name="created_rooms")
    password = models.CharField(max_length=20, blank=True)
    mode = models.CharField(max_length=10, choices=MODE_CHOICES, default="photos")

    def __str__(self):
        return f"Room #{self.room_id} (par {self.creator.username})"


class ImageQueue(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name="image_queue")
    image_url = models.URLField()
    position = models.PositiveIntegerField()
    uploaded_at = models.DateTimeField(auto_now_add=True)
    is_displayed = models.BooleanField(default=False)
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    image_hash = models.CharField(max_length=64, blank=True, null=True)

    class Meta:
        ordering = ["position"]

    def __str__(self):
        return f"Image {self.position} dans {self.room.room_id}"


class Participant(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name="participants")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    joined_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} dans {self.room.room_id}"


# --------- NOUVEAU : MESSAGES SAUVES ---------
class Message(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name="messages")
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["timestamp"]


    def __str__(self):
        return f"{self.user} : {self.content[:20]}"
