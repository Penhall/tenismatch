# Generated by Django 5.0 on 2025-01-28 23:46

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("tenis_admin", "0001_initial"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="aimodel",
            name="model_file",
        ),
        migrations.AddField(
            model_name="dataset",
            name="file_type",
            field=models.CharField(
                choices=[
                    ("csv", "CSV"),
                    ("xls", "XLS"),
                    ("xlsx", "XLSX"),
                    ("xml", "XML"),
                ],
                default="csv",
                max_length=4,
            ),
            preserve_default=False,
        ),
    ]
