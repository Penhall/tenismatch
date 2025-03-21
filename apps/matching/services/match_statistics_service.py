# /tenismatch/apps/matching/services/match_statistics_service.py
import logging
from django.db.models import Avg, Count, Sum, Case, When, IntegerField, F
from ..models import Match, SneakerProfile

logger = logging.getLogger(__name__)

class MatchStatisticsService:
    """
    Serviço para obtenção e processamento de estatísticas relacionadas a matches e perfis.
    Fornece métodos para análise de dados de compatibilidade, histórico de matches e tendências.
    """
    
    @staticmethod
    def get_user_match_statistics(user):
        """
        Obtém estatísticas de matches para um usuário específico.
        
        Args:
            user: O usuário para o qual obter estatísticas
            
        Returns:
            dict: Dicionário com estatísticas de matches
        """
        try:
            # Estatísticas gerais
            stats = Match.objects.filter(user_a=user).aggregate(
                avg_score=Avg('compatibility_score'),
                total_matches=Count('id'),
                mutual_matches=Count('id', filter={'is_mutual': True}),
                liked_matches=Count('id', filter={'status': 'liked'}),
                rejected_matches=Count('id', filter={'status': 'rejected'})
            )
            
            # Calcular taxa de match mútuo
            if stats['total_matches'] > 0:
                stats['mutual_rate'] = round((stats['mutual_matches'] / stats['total_matches']) * 100, 1)
            else:
                stats['mutual_rate'] = 0
                
            # Estatísticas adicionais
            # Média de score dos matches mútuos vs rejeitados
            mutual_avg = Match.objects.filter(
                user_a=user, is_mutual=True
            ).aggregate(avg=Avg('compatibility_score'))['avg'] or 0
            
            rejected_avg = Match.objects.filter(
                user_a=user, status='rejected'
            ).aggregate(avg=Avg('compatibility_score'))['avg'] or 0
            
            stats['mutual_avg_score'] = round(mutual_avg, 1)
            stats['rejected_avg_score'] = round(rejected_avg, 1)
            
            return stats
        except Exception as e:
            logger.error(f"Erro ao obter estatísticas de match para usuário {user.id}: {str(e)}")
            return {
                'avg_score': 0,
                'total_matches': 0,
                'mutual_matches': 0,
                'mutual_rate': 0
            }

    @staticmethod
    def get_style_distribution():
        """
        Obtém a distribuição de estilos de tênis entre todos os perfis.
        
        Returns:
            list: Lista de dicionários com estilo e contagem, ordenados por popularidade
        """
        try:
            style_counts = SneakerProfile.objects.values('style').annotate(
                count=Count('id')
            ).order_by('-count')
            
            # Calcular percentuais
            total = SneakerProfile.objects.count()
            if total > 0:
                for style in style_counts:
                    style['percentage'] = round((style['count'] / total) * 100, 1)
                    
                    # Adicionar o nome legível do estilo
                    for code, name in SneakerProfile.STYLE_CHOICES:
                        if code == style['style']:
                            style['style_name'] = name
                            break
            
            return list(style_counts)
        except Exception as e:
            logger.error(f"Erro ao obter distribuição de estilos: {str(e)}")
            return []

    @staticmethod
    def get_user_matching_history(user, limit=10):
        """
        Obtém o histórico de matches de um usuário.
        
        Args:
            user: O usuário para o qual obter o histórico
            limit: Número máximo de matches a retornar
            
        Returns:
            QuerySet: Lista de matches ordenados por data
        """
        try:
            return Match.objects.filter(user_a=user).order_by(
                '-matched_at'
            ).select_related('user_b')[:limit]
        except Exception as e:
            logger.error(f"Erro ao obter histórico de matches para usuário {user.id}: {str(e)}")
            return Match.objects.none()

    @staticmethod
    def process_sneaker_data(sneaker_profile):
        """
        Processa os dados de um perfil de tênis para uso em algoritmos.
        
        Args:
            sneaker_profile: Perfil de tênis a ser processado
            
        Returns:
            dict: Dicionário com vetores processados
        """
        try:
            # Vectorização para uso em algoritmos
            style_count = len(SneakerProfile.STYLE_CHOICES)
            color_count = len(SneakerProfile.COLOR_CHOICES)
            
            data = {
                'style_vector': [0] * style_count,
                'color_vector': [0] * color_count,
                'price_normalized': sneaker_profile.price_range / 5.0,  # Normalizar para 0-1
                'brand_id': 0
            }
            
            # One-hot encoding para estilo
            for i, (code, _) in enumerate(SneakerProfile.STYLE_CHOICES):
                if code == sneaker_profile.style:
                    data['style_vector'][i] = 1
                    break
            
            # One-hot encoding para cor
            for i, (code, _) in enumerate(SneakerProfile.COLOR_CHOICES):
                if code == sneaker_profile.color:
                    data['color_vector'][i] = 1
                    break
            
            # Codificação para marca (se disponível)
            if hasattr(SneakerProfile, 'BRAND_CHOICES'):
                for i, (code, _) in enumerate(SneakerProfile.BRAND_CHOICES):
                    if code == sneaker_profile.brand:
                        data['brand_id'] = i
                        break
            
            return data
        except Exception as e:
            logger.error(f"Erro ao processar dados de tênis: {str(e)}")
            # Valores padrão em caso de erro
            return {
                'style_vector': [0] * 5,
                'color_vector': [0] * 5,
                'price_normalized': 0.5,
                'brand_id': 0
            }
    
    @staticmethod
    def get_brand_compatibility_matrix():
        """
        Gera uma matriz de compatibilidade entre marcas baseada em matches existentes.
        
        Returns:
            dict: Matriz de compatibilidade entre marcas
        """
        try:
            # Obter todos os matches mútuos
            mutual_matches = Match.objects.filter(is_mutual=True).select_related(
                'user_a__sneakerprofile', 'user_b__sneakerprofile'
            )
            
            # Inicializar matriz de compatibilidade
            compatibility_matrix = {}
            match_counts = {}
            
            # Preencher a matriz com dados de matches
            for match in mutual_matches:
                brand_a = match.user_a.sneakerprofile.brand
                brand_b = match.user_b.sneakerprofile.brand
                
                # Inicializar chaves se necessário
                if brand_a not in compatibility_matrix:
                    compatibility_matrix[brand_a] = {}
                    match_counts[brand_a] = {}
                
                if brand_b not in compatibility_matrix[brand_a]:
                    compatibility_matrix[brand_a][brand_b] = 0
                    match_counts[brand_a][brand_b] = 0
                
                # Somar score de compatibilidade
                compatibility_matrix[brand_a][brand_b] += match.compatibility_score
                match_counts[brand_a][brand_b] += 1
            
            # Calcular médias
            for brand_a in compatibility_matrix:
                for brand_b in compatibility_matrix[brand_a]:
                    count = match_counts[brand_a][brand_b]
                    if count > 0:
                        compatibility_matrix[brand_a][brand_b] /= count
            
            return compatibility_matrix
        except Exception as e:
            logger.error(f"Erro ao gerar matriz de compatibilidade entre marcas: {str(e)}")
            return {}