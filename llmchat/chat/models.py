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
    uploaded_at = models.DateTimeField(blank=True, null=True)
    indexed_at = models.DateTimeField(blank=True, null=True)
    title = models.CharField(max_length=255, blank=True, default="")
    summary = models.TextField(blank=True, default="")
    summary_embedding = VectorField(dimensions=768, null=True)  # PaLM embedding
    mean_embedding = VectorField(dimensions=768, null=True)  # PaLM embedding
    tags = models.ManyToManyField("DocumentTag", related_name="documents")
    chunk_overlap = models.IntegerField(
        default=0
    )  # Number of characters to overlap between chunks

    def __str__(self):
        return f"Document {self.id}: {self.file.name}"

    @property
    def full_text(self):
        """
        Return the full text of the document
        """
        text = ""
        chunks = self.chunks.all().order_by("chunk_number")
        max_chunks = 10
        for i, chunk in enumerate(chunks[:max_chunks].values_list("text", flat=True)):
            text += chunk
            if i < len(chunks) - 1:
                text = text[: -self.chunk_overlap]

        if len(chunks) > max_chunks:
            text += f"\n\n... (truncated at {max_chunks} chunks)"
        return text


class DocumentChunk(models.Model):
    """
    A text chunk of a document, for similarity search
    """

    document = models.ForeignKey(
        Document, on_delete=models.CASCADE, related_name="chunks"
    )
    text = models.TextField()
    chunk_number = models.IntegerField()
    page_number = models.IntegerField(null=True)  # Some document loaders support this
    embedding = VectorField(dimensions=768, null=True)  # PaLM embedding

    def __str__(self):
        return f"DocumentChunk {self.id}: {self.document.file.name} Chunk {self.chunk_number}"


class DocumentTag(models.Model):
    tag = models.CharField(max_length=255)

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
