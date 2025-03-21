# /tenismatch/apps/matching/services/ml_recommender.py
import logging
import os
import joblib
import numpy as np
from django.db.models import Avg, F
from django.conf import settings
from .base_recommender import BaseRecommender
from .match_statistics_service import MatchStatisticsService
from apps.tenis_admin.models import AIModel
from apps.tenis_admin.services.training_service import SneakerMatchTraining

logger = logging.getLogger(__name__)

class MLRecommender(BaseRecommender):
    """
    Implementação de recomendação baseada em modelo de Machine Learning.
    Utiliza o modelo treinado mais recente para predizer compatibilidade entre perfis.
    """
    
    def __init__(self):
        self.model = self._load_latest_model()
        self.trainer = SneakerMatchTraining()
        self.feedback_weight = 0.3  # Peso do feedback no score final
    
    def _load_latest_model(self):
        """
        Carrega o modelo de ML mais recente aprovado.
        
        Returns:
            object: Modelo carregado ou None se não houver modelo disponível
        """
        try:
            # Tenta carregar modelo de produção primeiro
            prod_model_path = os.path.join(settings.MEDIA_ROOT, 'production', 'active_model.joblib')
            if os.path.exists(prod_model_path):
                logger.info(f"Carregando modelo de produção: {prod_model_path}")
                return joblib.load(prod_model_path)
            
            # Caso não exista, busca o modelo mais recente aprovado
            latest_model = AIModel.objects.filter(
                status__in=['approved', 'deployed']
            ).order_by('-created_at').first()
            
            if latest_model and latest_model.model_file:
                model_path = os.path.join(settings.MEDIA_ROOT, latest_model.model_file.name)
                if os.path.exists(model_path):
                    logger.info(f"Carregando modelo aprovado: {model_path}")
                    return joblib.load(model_path)
            
            logger.warning("Nenhum modelo encontrado, usando SneakerMatchTraining como fallback")
            return None
            
        except Exception as e:
            logger.error(f"Erro ao carregar modelo: {str(e)}")
            return None
    
    def get_recommendations(self, user_profile, limit=5):
        """
        Gera recomendações baseadas no modelo de ML.
        
        Args:
            user_profile: Perfil do usuário
            limit: Número máximo de recomendações
            
        Returns:
            list: Lista de recomendações ordenadas por compatibilidade
        """
        try:
            # Filtrar candidatos
            candidates = self.filter_candidates(user_profile)
            
            # Obter recomendações base
            base_recommendations = []
            for candidate in candidates:
                try:
                    # Calcular score de compatibilidade
                    compatibility = self.calculate_compatibility(
                        user_profile, 
                        candidate
                    )
                    
                    # Razões para compatibilidade
                    reasons = self.get_compatibility_reasons(
                        user_profile,
                        candidate
                    )
                    
                    base_recommendations.append({
                        'profile': candidate,
                        'base_score': compatibility,
                        'reasons': reasons
                    })
                except Exception as inner_e:
                    logger.error(f"Erro ao processar candidato {candidate.user.id}: {str(inner_e)}")
                    continue
            
            # Ajustar com feedback do usuário
            adjusted_recommendations = self._adjust_with_feedback(base_recommendations, user_profile)
            
            # Ordenar por score ajustado
            adjusted_recommendations.sort(key=lambda x: x['adjusted_score'], reverse=True)
            return adjusted_recommendations[:limit]
            
        except Exception as e:
            logger.error(f"Erro ao gerar recomendações ML: {str(e)}")
            from .basic_recommender import BasicRecommender
            # Fallback para recomendador básico em caso de erro
            logger.info("Usando BasicRecommender como fallback devido a erro")
            basic = BasicRecommender()
            return basic.get_recommendations(user_profile, limit)
    
    def calculate_compatibility(self, user_profile, other_profile):
        """
        Calcula compatibilidade entre dois perfis usando o modelo de ML.
        
        Args:
            user_profile: Perfil do usuário
            other_profile: Perfil do outro usuário
            
        Returns:
            float: Score de compatibilidade entre 0 e 1
        """
        try:
            # Se não tiver modelo ML carregado, usar o trainer diretamente
            if not self.model:
                user_features = self.trainer.extract_features(user_profile.sneaker_data)
                other_features = self.trainer.extract_features(other_profile.sneaker_data)
                return self.trainer.predict_match(user_features, other_features)
            
            # Extrair características
            user_features = self._extract_features(user_profile)
            other_features = self._extract_features(other_profile)
            
            # Combinar características
            combined_features = self._combine_features(user_features, other_features)
            
            # Usar modelo para predizer
            if hasattr(self.model, 'predict_proba'):
                # Modelo de classificação com probabilidades
                probs = self.model.predict_proba([combined_features])
                # Retorna probabilidade da classe positiva (index 1)
                return float(probs[0][1] if probs.shape[1] > 1 else probs[0][0])
            elif hasattr(self.model, 'predict'):
                # Modelo de regressão ou classificação sem probabilidades
                prediction = self.model.predict([combined_features])[0]
                if isinstance(prediction, (int, bool)):
                    # Classificação binária
                    return float(prediction)
                else:
                    # Regressão
                    return float(min(1.0, max(0.0, prediction)))
            else:
                # Fallback para método básico
                return self._calculate_basic_compatibility(user_profile, other_profile)
                
        except Exception as e:
            logger.error(f"Erro ao calcular compatibilidade ML: {str(e)}")
            return self._calculate_basic_compatibility(user_profile, other_profile)
    
    def get_compatibility_reasons(self, user_profile, other_profile):
        """
        Gera razões para a compatibilidade entre dois perfis.
        
        Args:
            user_profile: Perfil do usuário
            other_profile: Perfil do outro usuário
            
        Returns:
            list: Lista de razões textuais
        """
        try:
            reasons = []
            
            # Extrai dados dos perfis
            user_data = self._get_sneaker_data(user_profile)
            other_data = self._get_sneaker_data(other_profile)
            
            # Verificar marca
            if user_data.get('tenis_marca') == other_data.get('tenis_marca'):
                reasons.append(f"Vocês têm preferência pela mesma marca: {user_data.get('tenis_marca')}")
            
            # Verificar estilo
            if user_data.get('tenis_estilo') == other_data.get('tenis_estilo'):
                style_name = self._get_style_name(user_data.get('tenis_estilo'))
                reasons.append(f"Vocês compartilham do mesmo estilo: {style_name}")
            
            # Verificar preço
            user_price = float(user_data.get('tenis_preco', 0))
            other_price = float(other_data.get('tenis_preco', 0))
            if abs(user_price - other_price) < 100:
                reasons.append("Vocês têm gostos semelhantes em termos de valor de tênis")
            
            # Verificar cores
            if user_data.get('tenis_cores') == other_data.get('tenis_cores'):
                reasons.append(f"Vocês preferem cores similares: {user_data.get('tenis_cores')}")
            
            # Se não encontrou razões específicas
            if not reasons:
                reasons.append("Vocês têm estilos complementares que podem combinar bem")
                
            return reasons
            
        except Exception as e:
            logger.error(f"Erro ao gerar razões de compatibilidade: {str(e)}")
            return ["Vocês possuem compatibilidade baseada em seus estilos de tênis"]
    
    def _adjust_with_feedback(self, recommendations, user_profile):
        """
        Ajusta scores baseado em feedback histórico
        
        Args:
            recommendations: Lista de recomendações base
            user_profile: Perfil do usuário
            
        Returns:
            list: Lista de recomendações com scores ajustados
        """
        try:
            from ..models import Match, MatchFeedback
            
            for rec in recommendations:
                profile = rec['profile']
                
                # Busca feedback histórico similar
                similar_feedback = MatchFeedback.objects.filter(
                    user=user_profile.user,
                    match__other_sneaker__style=self._get_sneaker_data(profile).get('tenis_estilo')
                ).aggregate(Avg('rating'))['rating__avg']
                
                if similar_feedback:
                    feedback_score = similar_feedback / 5.0  # Normaliza para 0-1
                    rec['adjusted_score'] = (
                        rec['base_score'] * (1 - self.feedback_weight) +
                        feedback_score * self.feedback_weight
                    )
                else:
                    rec['adjusted_score'] = rec['base_score']
                
        except Exception as e:
            logger.error(f"Erro ao ajustar com feedback: {str(e)}")
            # Em caso de erro, usar score base
            for rec in recommendations:
                rec['adjusted_score'] = rec['base_score']
                
        return recommendations
    
    def _extract_features(self, profile):
        """
        Extrai características de um perfil para uso no modelo ML.
        
        Args:
            profile: Perfil de usuário
            
        Returns:
            dict: Dicionário com características extraídas
        """
        try:
            # Obter dados do tênis
            sneaker_data = self._get_sneaker_data(profile)
            
            # Usar extrator de características do treinador
            return self.trainer.extract_features(sneaker_data)
            
        except Exception as e:
            logger.error(f"Erro ao extrair características: {str(e)}")
            # Valores padrão em caso de erro
            return {
                'marca_score': 0.5,
                'estilo_score': 0.5,
                'cores_score': 0.5,
                'preco_score': 0.5
            }
    
    def _combine_features(self, user_features, other_features):
        """
        Combina características de dois perfis para entrada no modelo ML.
        
        Args:
            user_features: Características do usuário
            other_features: Características do outro usuário
            
        Returns:
            list: Lista de características combinadas
        """
        try:
            # Combinar os dicionários de características em um vetor
            combined_features = [
                user_features['marca_score'],
                user_features['estilo_score'],
                user_features['cores_score'],
                user_features['preco_score'],
                other_features['marca_score'],
                other_features['estilo_score'],
                other_features['cores_score'],
                other_features['preco_score'],
                # Diferenças absolutas
                abs(user_features['marca_score'] - other_features['marca_score']),
                abs(user_features['estilo_score'] - other_features['estilo_score']),
                abs(user_features['cores_score'] - other_features['cores_score']),
                abs(user_features['preco_score'] - other_features['preco_score'])
            ]
            
            return combined_features
            
        except Exception as e:
            logger.error(f"Erro ao combinar características: {str(e)}")
            # Vetor padrão em caso de erro (12 dimensões)
            return [0.5] * 12
    
    def _calculate_basic_compatibility(self, user_profile, other_profile):
        """
        Método de fallback para calcular compatibilidade quando o modelo falha.
        
        Args:
            user_profile: Perfil do usuário
            other_profile: Perfil do outro usuário
            
        Returns:
            float: Score de compatibilidade entre 0 e 1
        """
        try:
            # Extrair dados dos tênis
            user_data = self._get_sneaker_data(user_profile)
            other_data = self._get_sneaker_data(other_profile)
            
            # Componentes do score
            brand_score = 1.0 if user_data.get('tenis_marca') == other_data.get('tenis_marca') else 0.3
            style_score = 1.0 if user_data.get('tenis_estilo') == other_data.get('tenis_estilo') else 0.3
            color_score = 1.0 if user_data.get('tenis_cores') == other_data.get('tenis_cores') else 0.5
            
            # Preço (normalizado)
            price_diff = abs(float(user_data.get('tenis_preco', 0)) - float(other_data.get('tenis_preco', 0)))
            price_score = 1.0 - min(1.0, price_diff / 1000.0)
            
            # Média ponderada
            final_score = (
                brand_score * 0.3 +
                style_score * 0.4 +
                color_score * 0.1 + 
                price_score * 0.2
            )
            
            return final_score
            
        except Exception as e:
            logger.error(f"Erro ao calcular compatibilidade básica: {str(e)}")
            return 0.5  # Score neutro em caso de erro
    
    def _get_sneaker_data(self, profile):
        """
        Obtém dados do tênis a partir do perfil.
        
        Args:
            profile: Perfil do usuário
            
        Returns:
            dict: Dicionário com dados do tênis
        """
        # Se tiver o atributo sneaker_data, usar diretamente
        if hasattr(profile, 'sneaker_data'):
            return profile.sneaker_data
        
        # Se tiver o atributo sneaker_profile, extrair dados
        if hasattr(profile, 'sneaker_profile'):
            sneaker = profile.sneaker_profile
            return {
                'tenis_marca': getattr(sneaker, 'brand', ''),
                'tenis_estilo': getattr(sneaker, 'style', ''),
                'tenis_cores': getattr(sneaker, 'color', ''),
                'tenis_preco': getattr(sneaker, 'price_range', 0)
            }
        
        # Caso contrário, retornar dicionário vazio
        return {}
    
    def _get_style_name(self, style_code):
        """
        Obtém o nome legível do estilo a partir do código.
        
        Args:
            style_code: Código do estilo
            
        Returns:
            str: Nome legível do estilo
        """
        style_names = {
            'ESP': 'Esportivo',
            'CAS': 'Casual',
            'VIN': 'Vintage',
            'SOC': 'Social',
            'FAS': 'Fashion'
        }
        
        return style_names.get(style_code, style_code)