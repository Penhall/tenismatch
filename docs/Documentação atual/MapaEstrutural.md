# Mapa Estrutural do Projeto TenisMatch

## 1. Hierarquia de Diretórios e Arquivos

```
tenismatch/
├── apps/
│   ├── matching/               # Módulo de matching e recomendações
│   │   ├── ml/                 # Machine learning e datasets
│   │   ├── services/           # Lógica de processamento de dados
│   │   ├── migrations/         # Migrações do banco de dados
│   │   ├── models.py           # Modelos de dados
│   │   ├── views.py            # Views e endpoints
│   │   └── ...
│   ├── profiles/               # Gerenciamento de perfis
│   ├── tenis_admin/            # Administração e treinamento de modelos
│   │   ├── services/           # Serviços de IA e processamento
│   │   ├── migrations/         # Migrações do banco de dados
│   │   ├── models.py           # Modelos de dados
│   │   ├── views.py            # Views e endpoints
│   │   └── ...
│   └── users/                  # Autenticação e gerenciamento de usuários
├── core/                       # Configurações principais
│   ├── settings.py             # Configurações do Django
│   ├── urls.py                 # Rotas principais
│   └── ...
├── docs/                       # Documentação do projeto
│   ├── Documentação atual/     # Documentação técnica atualizada
│   └── ...
├── media/                      # Arquivos de mídia e uploads
│   ├── avatars/                # Fotos de perfil
│   └── datasets/               # Datasets carregados
├── memory-bank/                # Documentação de contexto
├── resources/                  # Recursos visuais e assets
├── scripts/                    # Scripts de automação
├── static/                     # Arquivos estáticos
│   ├── css/                    # Folhas de estilo
│   ├── img/                    # Imagens do sistema
│   └── ...
├── templates/                  # Templates HTML
│   ├── manager/                # Templates de gerenciamento
│   ├── matching/               # Templates de matching
│   ├── profiles/               # Templates de perfis
│   └── ...
└── ...
```

## 2. Funções, Classes e Constantes Exportadas

### Módulo: matching/
- **Funções:**
  - `calculate_compatibility_score()`: Calcula a compatibilidade entre usuários
  - `generate_recommendations()`: Gera lista de recomendações personalizadas

- **Classes:**
  - `Match`: Modelo de dados para matches
  - `RecommendationEngine`: Motor de recomendações principal

### Módulo: tenis_admin/
- **Funções:**
  - `train_model()`: Inicia o treinamento de um modelo de IA
  - `evaluate_model()`: Avalia o desempenho de um modelo

- **Classes:**
  - `AIModel`: Modelo de dados para modelos de IA
  - `Dataset`: Modelo de dados para datasets
  - `ModelTrainer`: Serviço de treinamento de modelos

### Módulo: users/
- **Funções:**
  - `create_user()`: Cria um novo usuário
  - `authenticate_user()`: Autentica um usuário

- **Classes:**
  - `User`: Modelo de dados principal de usuário
  - `UserProfile`: Informações detalhadas do perfil

## 3. Visão Geral dos Módulos Principais

### Módulo de Matching
- Responsável por: Recomendações e compatibilidade
- Dependências: tenis_admin (para modelos treinados)
- Relacionamentos: 
  - Consome modelos de IA do tenis_admin
  - Utiliza dados de perfis do módulo profiles

### Módulo Tenis Admin
- Responsável por: Treinamento e gerenciamento de modelos
- Dependências: matching (para dados de treinamento)
- Relacionamentos:
  - Fornece modelos para o módulo matching
  - Gerencia datasets e modelos de IA

### Módulo de Usuários
- Responsável por: Autenticação e gerenciamento de contas
- Dependências: Nenhuma
- Relacionamentos:
  - Fornece dados de usuários para todos os módulos
  - Gerencia permissões e autenticação

## 4. Utilitários e Componentes Compartilhados

### Utilitários Principais
- **data_processor.py**: Processamento e limpeza de dados
- **recommender.py**: Lógica de recomendação central
- **metrics_service.py**: Cálculo de métricas de desempenho

### Bibliotecas Principais
- Django Rest Framework: API RESTful
- Scikit-learn: Machine learning
- Pandas: Manipulação de dados
- NumPy: Computação numérica

## 5. Atualizações Recentes (docs/)
- Adicionada documentação de endpoints da API
- Atualizada visão geral do projeto
- Adicionada estrutura de diretórios completa
- Documentado fluxo de treinamento de modelos
