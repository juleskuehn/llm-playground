"""
Models for the LLM chat application
"""

from django.db import models
from django.contrib.auth.models import User


class Message(models.Model):
    """
    A message sent by a user or bot.
    """
    author = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    chat = models.ForeignKey("Chat", on_delete=models.CASCADE)

    def __str__(self):
        return self.message
    
    @property
    def is_bot(self):
        return self.user is None
    
    @property
    def is_user(self):
        return self.user is not None


class Chat(models.Model):
    """
    A sequence of Messages
    """
    timestamp = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=255, blank=True, default="")

    def __str__(self):
        return f"Chat {self.id}: {self.title}"
