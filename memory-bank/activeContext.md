# Funcionalidades por Ator

## 1. Usuários Comuns (Jogadores)
- **Perfil do Jogador** (apps/profiles/models.py)
  - Cadastro de dados pessoais
  - Upload de avatar (media/avatars)
  - Histórico de partidas
- **Preferências** (templates/profiles/preferences.html)
  - Configuração de nível de jogo
  - Preferências de locais/tipos de quadra
- **Matchmaking** (apps/matching/services/recommender.py)
  - Sistema de recomendações de parceiros
  - Visualização de matches (templates/matching/match_list.html)
- **Dashboard** (templates/profiles/dashboard.html)
  - Estatísticas de desempenho
  - Agenda de partidas

## 2. Analistas
- **Gestão de Datasets** (apps/tenis_admin/services/dataset_service.py)
  - Upload de datasets (media/datasets)
  - Validação de dados
- **Análise de Métricas** (templates/manager/metrics_dashboard.html)
  - Monitoramento de performance de modelos
  - Visualização de KPIs
- **Modelos de IA** (apps/tenis_admin/services/model_catalog.py)
  - Comparação de modelos
  - Avaliação de métricas

## 3. Administradores
- **Treinamento de Modelos** (apps/tenis_admin/model_training_service.py)
  - Pipeline de treinamento automatizado
  - Configuração de hiperparâmetros
- **Deploy de Modelos** (apps/tenis_admin/services/model_deployment_service.py)
  - Versionamento de modelos
  - Testes A/B
- **Monitoramento** (apps/tenis_admin/services/metrics_service.py)
  - Logs de execução
  - Alertas de desempenho

## 4. Sistema (Processos Automatizados)
- **Processamento de Dados** (apps/matching/services/data_processor.py)
  - Limpeza de datasets
  - Feature engineering
- **Recomendações** (apps/matching/ml/training.py)
  - Geração de embeddings
  - Cálculo de similaridade
- **Matchmaking** (apps/matching/views.py)
  - Algoritmo de pairing
  - Notificações automáticas
