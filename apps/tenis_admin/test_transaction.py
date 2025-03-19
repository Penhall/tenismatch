"""
Teste usando TransactionTestCase para verificar a conexão com o PostgreSQL.
Este teste usa TransactionTestCase, mas não depende de modelos do Django ou de migrações.
"""

from django.test import TransactionTestCase
import psycopg2

class PostgreSQLTransactionTestCase(TransactionTestCase):
    """Teste usando TransactionTestCase para verificar a conexão com o PostgreSQL."""
    
    databases = '__all__'  # Usa todos os bancos de dados configurados
    
    def setUp(self):
        """Configuração do teste."""
        # Conectar ao PostgreSQL
        self.conn = psycopg2.connect(
            dbname='tenismatch',
            user='postgres',
            password='abc123',
            host='localhost',
            port='5432'
        )
        
        # Criar um cursor
        self.cursor = self.conn.cursor()
        
        # Criar uma tabela temporária para o teste
        self.cursor.execute("""
            CREATE TEMPORARY TABLE test_table (
                id SERIAL PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                value INTEGER
            );
        """)
        
        # Confirmar a transação
        self.conn.commit()
    
    def tearDown(self):
        """Limpeza após o teste."""
        # Fechar cursor e conexão
        if hasattr(self, 'cursor') and self.cursor:
            self.cursor.close()
        
        if hasattr(self, 'conn') and self.conn:
            self.conn.close()
    
    def test_insert_and_select(self):
        """Testa a inserção e seleção de dados."""
        # Inserir dados
        self.cursor.execute("""
            INSERT INTO test_table (name, value) VALUES
            ('Item 1', 100),
            ('Item 2', 200),
            ('Item 3', 300);
        """)
        
        # Confirmar a transação
        self.conn.commit()
        
        # Selecionar dados
        self.cursor.execute("SELECT COUNT(*) FROM test_table;")
        count = self.cursor.fetchone()[0]
        
        # Verificar se os dados foram inseridos
        self.assertEqual(count, 3)
        
        # Selecionar um item específico
        self.cursor.execute("SELECT name, value FROM test_table WHERE name = 'Item 2';")
        item = self.cursor.fetchone()
        
        # Verificar se o item foi encontrado
        self.assertIsNotNone(item)
        self.assertEqual(item[0], 'Item 2')
        self.assertEqual(item[1], 200)
