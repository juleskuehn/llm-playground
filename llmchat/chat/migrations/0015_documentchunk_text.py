# Generated by Django 4.2.4 on 2023-08-18 17:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("chat", "0014_remove_documentchunk_text_document_chunk_size_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="documentchunk",
            name="text",
            field=models.TextField(blank=True, default=""),
        ),
    ]
