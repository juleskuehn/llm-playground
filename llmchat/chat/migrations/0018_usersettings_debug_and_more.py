# Generated by Django 4.2.5 on 2023-09-22 15:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("chat", "0017_document_original_filename"),
    ]

    operations = [
        migrations.AddField(
            model_name="usersettings",
            name="debug",
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name="usersettings",
            name="max_output_tokens",
            field=models.IntegerField(default=2048),
        ),
        migrations.AlterField(
            model_name="usersettings",
            name="model_name",
            field=models.CharField(
                choices=[
                    ("chat-bison", "Google PaLM chat-bison"),
                    ("codechat-bison", "Google PaLM codechat-bison"),
                    ("text-bison", "Google PaLM text-bison"),
                    ("code-bison", "Google PaLM code-bison"),
                    ("chat-bison-32k", "Google PaLM chat-bison 32k"),
                    ("codechat-bison-32k", "Google PaLM codechat-bison 32k"),
                    ("text-bison-32k", "Google PaLM text-bison 32k"),
                    ("code-bison-32k", "Google PaLM code-bison 32k"),
                ],
                default="chat-bison",
                max_length=255,
            ),
        ),
        migrations.AlterField(
            model_name="usersettings",
            name="temperature",
            field=models.FloatField(default=0.1),
        ),
    ]
