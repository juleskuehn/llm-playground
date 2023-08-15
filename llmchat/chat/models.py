"""
Models for the LLM chat application
"""

from django.db import models
from django.contrib.auth.models import User

from pgvector.django import VectorField

from llmchat.settings import GS_BUCKET_NAME


class Message(models.Model):
    """
    A message sent by a user or bot.
    """
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_bot = models.BooleanField(default=False)
    chat = models.ForeignKey("Chat", on_delete=models.CASCADE)

    def __str__(self):
        return self.message


class Chat(models.Model):
    """
    A sequence of Messages
    """
    timestamp = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=255, blank=True, default="")
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=False)

    def __str__(self):
        return f"Chat {self.id}: {self.title}"


class Document(models.Model):
    """
    Metadata for a document uploaded to GCP storage
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    file = models.FileField(null=True)
    upload_finished_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"Document {self.id}: {self.file}"
    

class DocumentChunk(models.Model):
    """
    A text chunk of a document, 1-1 with chunks in GCP matching engine
    """
    document = models.ForeignKey(Document, on_delete=models.CASCADE)
    text = models.TextField()
    chunk_number = models.IntegerField()
    page_number = models.IntegerField(null=True)  # Some document loaders support this
    embedding = VectorField(dimensions=768)  # PaLM embedding

    def __str__(self):
        return f"DocumentChunk {self.id}: {self.document.name} Chunk {self.chunk_number}"
