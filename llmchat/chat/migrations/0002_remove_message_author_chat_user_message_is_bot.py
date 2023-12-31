# Generated by Django 4.2.4 on 2023-08-13 00:01

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("chat", "0001_initial"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="message",
            name="author",
        ),
        migrations.AddField(
            model_name="chat",
            name="user",
            field=models.ForeignKey(
                default=1,
                on_delete=django.db.models.deletion.CASCADE,
                to=settings.AUTH_USER_MODEL,
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="message",
            name="is_bot",
            field=models.BooleanField(default=False),
        ),
    ]
