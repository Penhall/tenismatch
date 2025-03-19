import psycopg2
import sys
import locale

# Configurar locale e encoding
locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')
sys.stdout.reconfigure(encoding='utf-8')

try:
    # Conectar ao banco de dados com encoding explícito
    conn = psycopg2.connect(
        dbname="tenismatch",
        user="postgres",
        password="abc123",
        host="localhost",
        port="5432",
        options="-c client_encoding=LATIN1"
    )
    conn.set_client_encoding('LATIN1')
except psycopg2.OperationalError as e:
    print(f"Erro de conexão: {e}")
    sys.exit(1)
except Exception as e:
    print(f"Erro inesperado: {e}")
    sys.exit(1)

# Criar cursor
cur = conn.cursor()

# Criar tabela users se não existir
cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id SERIAL PRIMARY KEY,
        username VARCHAR(50) UNIQUE NOT NULL,
        email VARCHAR(100) UNIQUE NOT NULL,
        password VARCHAR(100) NOT NULL,
        profile VARCHAR(50) NOT NULL
    )
""")

# Criar usuários
users = [
    ("tester", "tester@grupo4.com", "abc123", "Comum"),
    ("Analyst", "analista@grupo4.com", "abc123", "Analista"),
    ("Manager", "gerente@grupo4.com", "abc123", "Gerente")
]

for username, email, password, profile in users:
    cur.execute("""
        INSERT INTO users (username, email, password, profile)
        VALUES (%s, %s, %s, %s)
        ON CONFLICT (username) DO NOTHING
    """, (username, email, password, profile))

# Commit e fechar conexão
conn.commit()
cur.close()
conn.close()

print("Usuários criados com sucesso!")
