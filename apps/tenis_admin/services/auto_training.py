
from django.db.models import Count
from django.utils import timezone
from datetime import timedelta
from .training_service import SneakerMatchTraining
from apps.matching.models import Match, MatchFeedback
from ..models import AIModel

class AutoTrainingService:
    def __init__(self):
        self.trainer = SneakerMatchTraining()
        self.min_feedback_threshold = 100  # Mínimo de feedbacks para retreinar
        self.min_days_between_training = 7  # Mínimo de dias entre treinos
        
    def check_and_train(self):
        """Verifica se é necessário retreinar e executa se necessário"""
        if self._should_retrain():
            return self._perform_training()
        return None
        
    def _should_retrain(self):
        """Verifica se modelo deve ser retreinado"""
        # Verifica último treino
        last_model = AIModel.objects.filter(
            status='approved'
        ).order_by('-created_at').first()
        
        if last_model and (timezone.now() - last_model.created_at).days < self.min_days_between_training:
            return False
            
        # Conta novos feedbacks desde último treino
        new_feedback_count = MatchFeedback.objects.filter(
            created_at__gt=last_model.created_at if last_model else timezone.now() - timedelta(days=365)
        ).count()
        
        return new_feedback_count >= self.min_feedback_threshold
        
    def _perform_training(self):
        """Executa treinamento automático"""
        # Coleta dados de treino
        training_data = self._collect_training_data()
        
        # Treina novo modelo
        metrics = self.trainer.train_model(training_data)
        
        # Cria novo modelo
        model = AIModel.objects.create(
            name=f'AutoTrained_{timezone.now().strftime("%Y%m%d")}',
            version='auto',
            metrics=metrics,
            status='review'  # Ainda requer aprovação do gerente
        )
        
        return model
        
    def _collect_training_data(self):
        """Coleta dados para treino do modelo"""
        training_data = []
        
        # Coleta matches com feedback
        matches_with_feedback = Match.objects.filter(
            matchfeedback__isnull=False
        ).select_related(
            'user_sneaker',
            'other_sneaker',
            'matchfeedback'
        )
        
        for match in matches_with_feedback:
            # Dados do tênis do usuário
            user_data = {
                'style': match.user_sneaker.style,
                'brand': match.user_sneaker.brand,
                'color': match.user_sneaker.color,
                'price': match.user_sneaker.price_range
            }
            
            # Dados do tênis do match
            other_data = {
                'style': match.other_sneaker.style,
                'brand': match.other_sneaker.brand,
                'color': match.other_sneaker.color,
                'price': match.other_sneaker.price_range
            }
            
            # Considera match bem sucedido se feedback >= 4
            success = match.matchfeedback.rating >= 4
            
            training_data.append({
                'user_data': user_data,
                'other_data': other_data,
                'success': success
            })
            
        return training_data