# /tenismatch/apps/profiles/management/commands/migrate_profile_history.py
from django.core.management.base import BaseCommand
from django.db import transaction
from apps.profiles.models import UserProfile, ProfileHistory
import json
from datetime import datetime
import pytz
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Migra os dados históricos de perfis do campo JSONField para a nova tabela ProfileHistory'

    def handle(self, *args, **options):
        # Configuração inicial
        profiles_processed = 0
        histories_created = 0
        errors = 0

        self.stdout.write('Iniciando migração de histórico de perfis...')
        
        # Verificar se já existem registros históricos
        if ProfileHistory.objects.exists():
            self.stdout.write(self.style.WARNING(
                'Já existem registros na tabela ProfileHistory. Isso pode causar duplicidade. Deseja continuar? (s/n)'
            ))
            answer = input()
            if answer.lower() != 's':
                self.stdout.write(self.style.WARNING('Operação cancelada pelo usuário.'))
                return
        
        # Processar cada perfil
        profiles = UserProfile.objects.all()
        total_profiles = profiles.count()
        
        self.stdout.write(f'Encontrados {total_profiles} perfis para processar.')
        
        for profile in profiles:
            try:
                with transaction.atomic():
                    # Salvar o histórico atual como estado inicial se ainda não houver histórico
                    if not ProfileHistory.objects.filter(profile=profile).exists():
                        # Dados para o primeiro registro histórico
                        profile_data = {
                            'id': profile.id,
                            'user': profile.user_id,
                            'user_type': profile.user_type,
                            'bio': profile.bio,
                            'location': profile.location,
                            'shoe_size': profile.shoe_size,
                            'preferred_brands': profile.preferred_brands,
                            'style_preferences': profile.style_preferences,
                            'compatibility_scores': profile.compatibility_scores,
                            'fashion_specialization': profile.fashion_specialization,
                            'experience_years': profile.experience_years,
                            'profile_version': profile.profile_version,
                        }
                        
                        # Criar o primeiro registro histórico
                        ProfileHistory.objects.create(
                            profile=profile,
                            data=profile_data,
                            timestamp=profile.last_updated
                        )
                        histories_created += 1
                    
                    # Se houver dados históricos no campo JSON antigo, migrar
                    historical_data = getattr(profile, 'historical_data', None)
                    if historical_data and isinstance(historical_data, list) and len(historical_data) > 0:
                        # Processar cada entrada histórica, do mais antigo para o mais recente
                        for entry in historical_data:
                            if isinstance(entry, dict) and 'data' in entry and 'timestamp' in entry:
                                try:
                                    # Extrair dados
                                    data = entry['data']
                                    timestamp_str = entry['timestamp']
                                    
                                    # Converter string de timestamp para objeto datetime
                                    try:
                                        timestamp = datetime.fromisoformat(timestamp_str)
                                    except (ValueError, TypeError):
                                        # Fallback para o datetime atual
                                        timestamp = datetime.now(pytz.UTC)
                                    
                                    # Criar registro histórico
                                    ProfileHistory.objects.create(
                                        profile=profile,
                                        data=data,
                                        timestamp=timestamp
                                    )
                                    histories_created += 1
                                except Exception as e:
                                    logger.error(f"Erro ao processar entrada histórica: {str(e)}")
                                    errors += 1
                        
                        # Limpar o campo de histórico antigo
                        profile.historical_data = []
                        profile.save(update_fields=['historical_data'])
                
                profiles_processed += 1
                if profiles_processed % 10 == 0:
                    self.stdout.write(f'Processados {profiles_processed}/{total_profiles} perfis...')
                    
            except Exception as e:
                errors += 1
                logger.error(f"Erro ao processar perfil {profile.id}: {str(e)}")
                self.stdout.write(self.style.ERROR(f'Erro ao processar perfil {profile.id}: {str(e)}'))
        
        # Relatório final
        self.stdout.write(self.style.SUCCESS(
            f'Migração concluída. '
            f'Perfis processados: {profiles_processed}/{total_profiles}. '
            f'Históricos criados: {histories_created}. '
            f'Erros: {errors}'
        ))