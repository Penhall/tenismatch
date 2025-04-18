# Generated by Django 5.0 on 2025-03-22 14:49

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("users", "0002_alter_user_is_approved_alter_user_role"),
    ]

    operations = [
        migrations.AlterField(
            model_name="user",
            name="role",
            field=models.CharField(
                choices=[
                    ("GERENTE", "Gerente"),
                    ("ANALISTA", "Analista"),
                    ("USUARIO", "Usuário Regular"),
                ],
                db_index=True,
                default="USUARIO",
                max_length=10,
            ),
        ),
    ]
