from django.contrib.auth.models import User
from django.db import models


class FriendRequest(models.Model):
    from_user = models.CharField(max_length=150)
    to_user = models.CharField(max_length=150)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=[('pending', 'Pending'), ('accepted', 'Accepted'), ('rejected', 'Rejected')], default='pending')
