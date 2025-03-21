"""
Teste simples para verificar a conexão com o PostgreSQL.
Este teste não depende de modelos do Django ou de migrações.
"""

from django.test import TestCase
import psycopg2

class SimpleTestCase(TestCase):
    """Teste simples para verificar a conexão com o PostgreSQL."""
    
    def test_postgresql_connection(self):
        """Testa a conexão com o PostgreSQL."""
        # Conectar ao PostgreSQL
        conn = psycopg2.connect(
            dbname='tenismatch',
            user='postgres',
            password='abc123',
            host='localhost',
            port='5432'
        )
        
        # Criar um cursor
        cursor = conn.cursor()
        
        # Executar uma consulta simples
        cursor.execute("SELECT version();")
        
        # Obter o resultado
        version = cursor.fetchone()
        
        # Fechar cursor e conexão
        cursor.close()
        conn.close()
        
        # Verificar se a versão foi obtida
        self.assertIsNotNone(version)
        self.assertIn('PostgreSQL', version[0])
