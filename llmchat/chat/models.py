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


def user_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    return "user_{0}/{1}".format(instance.user.username.split('@')[0], filename)


class Document(models.Model):
    """
    Metadata for a document uploaded to GCP storage
    """

    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    file = models.FileField(null=True, upload_to=user_directory_path)
    uploaded_at = models.DateTimeField(blank=True, null=True)
    indexed_at = models.DateTimeField(blank=True, null=True)
    title = models.CharField(max_length=255, blank=True, default="")
    original_filename = models.CharField(max_length=255, blank=True, default="")
    summary = models.TextField(blank=True, default="")
    summary_embedding = VectorField(dimensions=768, null=True)  # PaLM embedding
    mean_embedding = VectorField(dimensions=768, null=True)  # PaLM embedding
    tags = models.ManyToManyField("DocumentTag", related_name="documents")
    chunk_overlap = models.IntegerField(
        default=200
    )  # Number of characters to overlap between chunks
    chunk_size = models.IntegerField(default=2000)  # Number of characters per chunk
    text = models.TextField(blank=True, default="")

    def __str__(self):
        return f"Document {self.id}: {self.original_filename}"
    
    @property
    def name(self):
        return self.file.name.split('/')[-1]


class DocumentChunk(models.Model):
    """
    A text chunk of a document, for similarity search
    """

    document = models.ForeignKey(
        Document, on_delete=models.CASCADE, related_name="chunks"
    )
    chunk_number = models.IntegerField()
    page_number = models.IntegerField(null=True)  # Some document loaders support this
    embedding = VectorField(dimensions=768, null=True)  # PaLM embedding
    text = models.TextField(blank=True, default="")

    def __str__(self):
        return f"DocumentChunk {self.id}: {self.document.file.name} Chunk {self.chunk_number}"

class DocumentTag(models.Model):
    tag = models.CharField(max_length=255)
    user_generated = models.BooleanField(default=True)

    def __str__(self):
        return f"DocumentTag {self.id}: {self.tag}"


class UserSettings(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="settings")
    model_name = models.CharField(
        max_length=255,
        default="chat-bison",
        choices=[
            ("chat-bison", "Google PaLM chat-bison"),
            ("codechat-bison", "Google PaLM codechat-bison"),
            ("text-bison", "Google PaLM text-bison"),
            ("code-bison", "Google PaLM code-bison"),
        ],
    )
    system_prompt = models.TextField(null=True, blank=True)
    max_output_tokens = models.IntegerField(default=1024)
    temperature = models.FloatField(default=0)
