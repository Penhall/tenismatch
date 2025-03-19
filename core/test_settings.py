"""
Configurações específicas para testes com PostgreSQL.
Este arquivo estende as configurações padrão do projeto e adiciona configurações específicas para testes.

Para usar estas configurações, execute:
    python manage.py test --settings=core.test_settings
"""

from .settings import *

# Configuração do banco de dados de teste
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'test_tenismatch',  # Banco de dados específico para testes
        'USER': 'postgres',
        'PASSWORD': 'abc123',
        'HOST': 'localhost',
        'PORT': '5432',
        'TEST': {
            'NAME': 'test_tenismatch',  # Nome fixo para o banco de dados de teste
            'SERIALIZE': False,  # Desativa a serialização para testes mais rápidos
        },
    }
}

# Configurações para testes mais rápidos
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',  # Mais rápido para testes
]

# Desativa o cache para testes
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}

# Configurações de logging para testes
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'WARNING',
        },
        'apps': {
            'handlers': ['console'],
            'level': 'WARNING',
        },
    },
}

# Configurações para testes de integração
TEST_RUNNER = 'django.test.runner.DiscoverRunner'

# Configurações para arquivos de mídia em testes
import tempfile
MEDIA_ROOT = tempfile.mkdtemp()  # Diretório temporário para arquivos de mídia em testes

# Configurações para testes de email
EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'

# Desativa a proteção CSRF para testes
MIDDLEWARE = [m for m in MIDDLEWARE if m != 'django.middleware.csrf.CsrfViewMiddleware']

# Configurações para testes mais rápidos
DEBUG = False
