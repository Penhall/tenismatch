# /tenismatch/apps/profiles/migrations/XXXX_historical_profiles.py
# Substitua XXXX pelo próximo número de migração

from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0002_initial'),  # Substitua pelo nome da sua última migração
    ]

    operations = [
        # 1. Criar a nova tabela para histórico de perfis
        migrations.CreateModel(
            name='ProfileHistory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('data', models.JSONField()),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('profile', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='history', to='profiles.userprofile')),
            ],
            options={
                'verbose_name': 'Histórico de Perfil',
                'verbose_name_plural': 'Históricos de Perfil',
                'ordering': ['-timestamp'],
            },
        ),
        
        # 2. Adicionar índice ao campo user no UserProfile
        migrations.AlterField(
            model_name='userprofile',
            name='user',
            field=models.OneToOneField(db_index=True, on_delete=django.db.models.deletion.CASCADE, to='users.user'),
        ),
    ]