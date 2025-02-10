# Resolução de Problemas Comuns (Troubleshooting)

## **Visão Geral**
Este documento lista os problemas mais comuns encontrados durante o desenvolvimento e implantação do **TenisMatch**, além de fornecer soluções e sugestões para depuração.

---
## **1. Problemas com o Banco de Dados**

### **Erro:** `django.db.utils.OperationalError: could not connect to server`
**Causa:** O banco de dados PostgreSQL pode não estar rodando ou a configuração está incorreta.

**Solução:**
```bash
sudo systemctl start postgresql
sudo systemctl enable postgresql
```
Verifique a configuração no `.env`:
```env
DATABASE_URL=postgres://usuario:senha@localhost:5432/tenismatch
```
Teste a conexão manualmente:
```bash
psql -h localhost -U usuario -d tenismatch
```

### **Erro:** `relation "auth_user" does not exist`
**Causa:** As migrações do banco de dados não foram executadas.

**Solução:**
```bash
python manage.py migrate
```
Se necessário, recrie o banco de dados:
```bash
python manage.py flush
python manage.py migrate
python manage.py createsuperuser
```

---
## **2. Problemas na API**

### **Erro:** `401 Unauthorized`
**Causa:** O token JWT pode estar expirado ou ausente.

**Solução:**
- Gere um novo token:
```bash
curl -X POST http://127.0.0.1:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email": "usuario@email.com", "password": "senha123"}'
```
- Adicione o token nas requisições:
```bash
curl -X GET http://127.0.0.1:8000/api/recommendations/ \
  -H "Authorization: Bearer <TOKEN>"
```

### **Erro:** `403 Forbidden`
**Causa:** O usuário não tem permissão para acessar o recurso.

**Solução:**
- Verifique as permissões do usuário:
```bash
python manage.py shell
from django.contrib.auth.models import User
user = User.objects.get(email="usuario@email.com")
print(user.groups.all())
```
- Atribua permissões manualmente:
```bash
user.groups.add(Group.objects.get(name="Usuário Pago"))
```

---
## **3. Problemas com Servidor Web**

### **Erro:** `502 Bad Gateway` no Nginx
**Causa:** O Gunicorn pode não estar rodando corretamente.

**Solução:**
```bash
sudo systemctl restart tenismatch
sudo systemctl status tenismatch
```
Se o erro persistir, verifique os logs:
```bash
sudo journalctl -u tenismatch --no-pager
```

### **Erro:** `403 Forbidden` ao acessar arquivos estáticos
**Causa:** O Nginx pode não estar servindo corretamente os arquivos.

**Solução:**
```bash
sudo chown -R www-data:www-data /caminho/para/tenismatch/static
sudo chmod -R 755 /caminho/para/tenismatch/static
sudo systemctl restart nginx
```

---
## **4. Problemas com Deploy**

### **Erro:** `ModuleNotFoundError: No module named 'core'`
**Causa:** O ambiente virtual pode não estar ativado.

**Solução:**
```bash
source venv/bin/activate
python manage.py runserver
```
Se estiver rodando com Gunicorn:
```bash
/caminho/para/venv/bin/gunicorn --bind 0.0.0.0:8000 core.wsgi:application
```

### **Erro:** `SECRET_KEY setting must not be empty`
**Causa:** A variável de ambiente `SECRET_KEY` não foi definida corretamente.

**Solução:**
Verifique o arquivo `.env` e adicione:
```env
SECRET_KEY=sua-chave-secreta
```

---
## **5. Logs e Debugging**

Para identificar problemas mais rapidamente, utilize os seguintes comandos:
- Ver logs do Django:
```bash
tail -f /caminho/para/tenismatch/logs/django.log
```
- Ver logs do Gunicorn:
```bash
sudo journalctl -u tenismatch --no-pager
```
- Ver logs do Nginx:
```bash
sudo journalctl -u nginx --no-pager
```
- Testar se o servidor responde corretamente:
```bash
curl -X GET http://127.0.0.1:8000/
```

---
## **Próximos Passos**
- Implementação de monitoramento com **Prometheus e Grafana**.
- Melhoria na observabilidade com **Sentry** para capturar erros automaticamente.
- Otimização da performance com **caching** (Redis, Memcached).

---
Este documento será atualizado conforme novos problemas e soluções forem identificados no sistema.

