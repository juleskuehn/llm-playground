# Generated by Django 4.2.4 on 2023-08-18 17:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("chat", "0015_documentchunk_text"),
    ]

    operations = [
        migrations.AddField(
            model_name="document",
            name="text",
            field=models.TextField(blank=True, default=""),
        ),
    ]
