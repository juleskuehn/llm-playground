# Generated by Django 4.2.4 on 2023-08-15 23:45

from django.db import migrations
import pgvector.django


class Migration(migrations.Migration):

    dependencies = [
        ("chat", "0007_documenttag_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="documentchunk",
            name="embedding",
            field=pgvector.django.VectorField(dimensions=768, null=True),
        ),
    ]
