# Generated by Django 4.2.4 on 2023-08-16 13:01

from django.db import migrations
import pgvector.django


class Migration(migrations.Migration):

    dependencies = [
        ("chat", "0008_alter_documentchunk_embedding"),
    ]

    operations = [
        migrations.AddField(
            model_name="document",
            name="mean_embedding",
            field=pgvector.django.VectorField(dimensions=768, null=True),
        ),
    ]
