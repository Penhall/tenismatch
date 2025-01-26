#!/bin/bash

# Criar diretórios
mkdir -p core
mkdir -p apps/users
mkdir -p apps/matching/services
mkdir -p apps/matching/ml
mkdir -p apps/profiles
mkdir -p templates

# Criar arquivos core
echo "# /tenismatch/core/__init__.py" > core/__init__.py
echo "# /tenismatch/core/settings.py" > core/settings.py
echo "# /tenismatch/core/urls.py" > core/urls.py
echo "# /tenismatch/core/wsgi.py" > core/wsgi.py

# Criar arquivos apps/users
echo "# /tenismatch/apps/users/__init__.py" > apps/users/__init__.py
echo "# /tenismatch/apps/users/models.py" > apps/users/models.py
echo "# /tenismatch/apps/users/views.py" > apps/users/views.py
echo "# /tenismatch/apps/users/serializers.py" > apps/users/serializers.py

# Criar arquivos apps/matching
echo "# /tenismatch/apps/matching/__init__.py" > apps/matching/__init__.py
echo "# /tenismatch/apps/matching/models.py" > apps/matching/models.py
echo "# /tenismatch/apps/matching/views.py" > apps/matching/views.py

# Criar arquivos apps/matching/services
echo "# /tenismatch/apps/matching/services/recommender.py" > apps/matching/services/recommender.py
echo "# /tenismatch/apps/matching/services/data_processor.py" > apps/matching/services/data_processor.py

# Criar arquivos apps/matching/ml
echo "# /tenismatch/apps/matching/ml/dataset.py" > apps/matching/ml/dataset.py
echo "# /tenismatch/apps/matching/ml/training.py" > apps/matching/ml/training.py

# Criar arquivos apps/profiles
echo "# /tenismatch/apps/profiles/__init__.py" > apps/profiles/__init__.py
echo "# /tenismatch/apps/profiles/models.py" > apps/profiles/models.py
echo "# /tenismatch/apps/profiles/views.py" > apps/profiles/views.py

# Criar arquivos templates
echo "# /tenismatch/templates/base.html" > templates/base.html
echo "# /tenismatch/templates/landing.html" > templates/landing.html

# Criar requirements.txt
echo "# /tenismatch/requirements.txt" > requirements.txt

echo "Estrutura de arquivos criada com sucesso!"