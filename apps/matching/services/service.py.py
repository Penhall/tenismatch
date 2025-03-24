# /tenismatch/apps/matching/services.py
import logging
import random
from django.db.models import Avg, Count
from django.utils import timezone
from datetime import timedelta

from .models import SneakerProfile, Match, MatchFeedback

logger = logging.getLogger(__name__)

class RecommenderService:
    """
    Serviço responsável por gerar recomendações de matches com base em perfis de tênis.
    """
    
    def __init__(self):
        self.style_compatibility = {
            'ESP': ['ESP', 'CAS'],
            'CAS': ['CAS', 'ESP', 'VIN'],
            'VIN': ['VIN', 'CAS'],
            'SOC': ['SOC', 'FAS'],
            'FAS': ['FAS', 'SOC', 'VIN']
        }
        
        self.color_compatibility = {
            'BLK': ['BLK', 'WHT', 'NEU'],
            'WHT': ['WHT', 'BLK', 'NEU'],
            'COL': ['COL', 'NEU'],
            'NEU': ['NEU', 'BLK', 'WHT', 'COL']
        }
    
    def get_matches(self, user_profile, limit=10):
        """
        Retorna matches recomendados para o perfil do usuário.
        """
        try:
            # Excluir perfil do próprio usuário
            other_profiles = SneakerProfile.objects.exclude(user=user_profile.user)
            
            # Perfis já avaliados (liked, rejected, blocked)
            evaluated_users = Match.objects.filter(user_a=user_profile.user).values_list('user_b_id', flat=True)
            
            # Filtrar perfis que não foram avaliados
            other_profiles = other_profiles.exclude(user__id__in=evaluated_users)
            
            matches = []
            for profile in other_profiles:
                compatibility = self._calculate_compatibility(user_profile, profile)
                reasons = self._generate_compatibility_reasons(user_profile, profile, compatibility)
                
                matches.append({
                    'profile': profile,
                    'compatibility': compatibility,
                    'reasons': reasons
                })
            
            # Ordenar por compatibilidade (do maior para o menor)
            matches.sort(key=lambda x: x['compatibility'], reverse=True)
            
            # Limitar quantidade de resultados
            return matches[:limit]
        
        except Exception as e:
            logger.error(f"Erro ao obter matches: {str(e)}")
            return []
    
    def get_single_match(self, user_profile, other_profile):
        """
        Calcula compatibilidade entre dois perfis específicos.
        """
        try:
            compatibility = self._calculate_compatibility(user_profile, other_profile)
            reasons = self._generate_compatibility_reasons(user_profile, other_profile, compatibility)
            
            return {
                'compatibility': compatibility,
                'reasons': reasons
            }
        except Exception as e:
            logger.error(f"Erro ao calcular compatibilidade: {str(e)}")
            return {
                'compatibility': 0,
                'reasons': []
            }
    
    def get_match_suggestions(self, user_profile, limit=3):
        """
        Retorna sugestões diárias de matches.
        """
        matches = self.get_matches(user_profile, limit=limit)
        return matches
    
    def update_match_status(self, user_profile, other_user_id, status):
        """
        Atualiza o status de um match.
        """
        try:
            # Verificar se já existe um match
            existing_match = Match.objects.filter(
                user_a=user_profile.user,
                user_b_id=other_user_id
            ).first()
            
            is_mutual = False
            
            if existing_match:
                # Atualizar match existente
                existing_match.status = status
                existing_match.save()
                
                if status == 'liked':
                    # Verificar se existe um match reverso (para detectar match mútuo)
                    reverse_match = Match.objects.filter(
                        user_a_id=other_user_id,
                        user_b=user_profile.user,
                        status='liked'
                    ).first()
                    
                    if reverse_match:
                        existing_match.is_mutual = True
                        existing_match.save()
                        
                        reverse_match.is_mutual = True
                        reverse_match.save()
                        
                        is_mutual = True
                
                return True, f"Status atualizado para {status}.", is_mutual
            else:
                # Criar novo match
                other_profile = SneakerProfile.objects.get(user_id=other_user_id)
                compatibility = self._calculate_compatibility(user_profile, other_profile)
                
                match = Match.objects.create(
                    user_a=user_profile.user,
                    user_b_id=other_user_id,
                    compatibility_score=compatibility,
                    status=status
                )
                
                if status == 'liked':
                    # Verificar se existe um match reverso (para detectar match mútuo)
                    reverse_match = Match.objects.filter(
                        user_a_id=other_user_id,
                        user_b=user_profile.user,
                        status='liked'
                    ).first()
                    
                    if reverse_match:
                        match.is_mutual = True
                        match.save()
                        
                        reverse_match.is_mutual = True
                        reverse_match.save()
                        
                        is_mutual = True
                
                return True, f"Match criado com status {status}.", is_mutual
        
        except Exception as e:
            logger.error(f"Erro ao atualizar status do match: {str(e)}")
            return False, f"Erro ao atualizar status: {str(e)}", False
    
    def _calculate_compatibility(self, user_profile, other_profile):
        """
        Calcula pontuação de compatibilidade entre dois perfis.
        """
        score = 0
        
        # Compatibilidade de estilo (30%)
        if other_profile.style in self.style_compatibility.get(user_profile.style, []):
            score += 30
        
        # Compatibilidade de cor (20%)
        if other_profile.color in self.color_compatibility.get(user_profile.color, []):
            score += 20
        
        # Compatibilidade de marca (15%)
        if user_profile.brand.lower() == other_profile.brand.lower():
            score += 15
        
        # Compatibilidade de faixa de preço (15%)
        price_diff = abs(user_profile.price_range - other_profile.price_range)
        if price_diff < 100:
            score += 15
        elif price_diff < 300:
            score += 10
        elif price_diff < 500:
            score += 5
        
        # Compatibilidade de ocasião (20%)
        if user_profile.occasion.lower() == other_profile.occasion.lower():
            score += 20
        
        return score / 100  # Normalizar para 0-1
    
    def _generate_compatibility_reasons(self, user_profile, other_profile, score):
        """
        Gera explicações para a compatibilidade entre dois perfis.
        """
        reasons = []
        
        # Estilo
        if other_profile.style in self.style_compatibility.get(user_profile.style, []):
            reasons.append(f"Vocês possuem estilos compatíveis: {user_profile.get_style_display()} e {other_profile.get_style_display()}")
        
        # Cor
        if other_profile.color in self.color_compatibility.get(user_profile.color, []):
            reasons.append(f"Vocês preferem cores complementares: {user_profile.get_color_display()} e {other_profile.get_color_display()}")
        
        # Marca
        if user_profile.brand.lower() == other_profile.brand.lower():
            reasons.append(f"Vocês têm a mesma marca favorita: {user_profile.brand}")
        
        # Faixa de preço
        price_diff = abs(user_profile.price_range - other_profile.price_range)
        if price_diff < 100:
            reasons.append("Vocês valorizam tênis em faixas de preço similares")
        
        # Ocasião
        if user_profile.occasion.lower() == other_profile.occasion.lower():
            reasons.append(f"Vocês usam tênis em ocasiões semelhantes: {user_profile.occasion}")
        
        return reasons


class MatchStatisticsService:
    """
    Serviço responsável por gerar estatísticas sobre matches.
    """
    
    @staticmethod
    def get_user_match_statistics(user):
        """
        Retorna estatísticas de matches para um usuário.
        """
        try:
            # Total de matches
            total_matches = Match.objects.filter(user_a=user).count()
            
            # Matches mútuos
            mutual_matches = Match.objects.filter(user_a=user, is_mutual=True).count()
            
            # Média de compatibilidade
            avg_compatibility = Match.objects.filter(user_a=user).aggregate(
                avg=Avg('compatibility_score')
            )['avg'] or 0
            
            # Matches por status
            liked = Match.objects.filter(user_a=user, status='liked').count()
            rejected = Match.objects.filter(user_a=user, status='rejected').count()
            pending = Match.objects.filter(user_a=user, status='pending').count()
            
            return {
                'total_matches': total_matches,
                'mutual_matches': mutual_matches,
                'avg_compatibility': avg_compatibility * 100,  # Converter para porcentagem
                'liked': liked,
                'rejected': rejected,
                'pending': pending
            }
        
        except Exception as e:
            logger.error(f"Erro ao obter estatísticas de matches: {str(e)}")
            return {
                'total_matches': 0,
                'mutual_matches': 0,
                'avg_compatibility': 0,
                'liked': 0,
                'rejected': 0,
                'pending': 0
            }
    
    @staticmethod
    def get_style_distribution():
        """
        Retorna distribuição de estilos entre todos os usuários.
        """
        try:
            styles = SneakerProfile.objects.values('style').annotate(
                count=Count('style')
            ).order_by('-count')
            
            # Converter códigos para nomes de estilo
            for style in styles:
                style_obj = SneakerProfile(style=style['style'])
                style['name'] = style_obj.get_style_display()
            
            return styles
        
        except Exception as e:
            logger.error(f"Erro ao obter distribuição de estilos: {str(e)}")
            return []
    
    @staticmethod
    def get_user_matching_history(user, limit=5):
        """
        Retorna histórico recente de matches do usuário.
        """
        try:
            return Match.objects.filter(user_a=user).order_by('-matched_at')[:limit]
        
        except Exception as e:
            logger.error(f"Erro ao obter histórico de matches: {str(e)}")
            return []