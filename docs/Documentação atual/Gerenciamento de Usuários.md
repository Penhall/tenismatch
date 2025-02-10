# Gerenciamento de Usuários e Controle de Acesso Baseado em Funções (RBAC)

## **Visão Geral**
O **TenisMatch** utiliza um sistema de gerenciamento de usuários baseado no modelo **RBAC (Role-Based Access Control)**, garantindo que cada usuário tenha permissões apropriadas de acordo com seu perfil.

## **Perfis de Usuário**
Os usuários são classificados em diferentes perfis, cada um com permissões específicas:

| Perfil        | Descrição | Permissões Principais |
|--------------|-----------|----------------------|
| **Usuário Free**  | Usuário gratuito com funcionalidades limitadas | Acesso a recomendações básicas, visualização de perfis restrita |
| **Usuário Pago**  | Usuário premium com acesso completo | Visualização completa de perfis, matches ilimitados |
| **Analista**  | Responsável por gerenciar e analisar datasets de IA | Upload de datasets, monitoramento de modelos |
| **Gerente**  | Acompanha e aprova modelos de IA | Aprovação/rejeição de modelos, gestão de usuários |
| **Suporte**  | Responsável por manutenção do sistema | Reset de senhas, visualização de logs, modificação de tabelas |

## **Sistema de Autenticação**
A autenticação no sistema é feita através de **Django Auth** com suporte a **JWT (JSON Web Token)** para APIs. O fluxo de autenticação segue os seguintes passos:

1. O usuário insere e-mail e senha na página de login.
2. As credenciais são verificadas no banco de dados.
3. Se corretas, um **token JWT** é gerado e enviado para o cliente.
4. O usuário pode acessar recursos protegidos utilizando esse token.

Para segurança, o sistema implementa:
- **Senhas criptografadas com PBKDF2**
- **Tokens de expiração curta para evitar uso indevido**
- **Requisições protegidas contra CSRF, XSS e SQL Injection**

## **Estrutura do Banco de Dados**
O controle de acesso é armazenado utilizando tabelas relacionadas no banco de dados:

- **users**: Contém as informações básicas de cada usuário
- **profiles**: Relaciona cada usuário ao seu perfil
- **permissions**: Lista de permissões específicas do sistema
- **user_roles**: Relação entre usuários e seus respectivos perfis
- **role_permissions**: Associa permissões específicas a cada perfil

## **Exemplo de Implementação RBAC**
A implementação no Django pode ser feita utilizando o **Django Groups and Permissions**:

```python
from django.contrib.auth.models import Group, Permission

def setup_roles():
    # Criando perfis de usuário
    roles = ['Usuário Free', 'Usuário Pago', 'Analista', 'Gerente', 'Suporte']
    for role in roles:
        Group.objects.get_or_create(name=role)

    # Atribuindo permissões
    user_group = Group.objects.get(name='Usuário Pago')
    permission = Permission.objects.get(codename='view_full_profiles')
    user_group.permissions.add(permission)
```

## **Gerenciamento de Sessões e Segurança**
- **Registro de tentativas de login**
- **Bloqueio de conta após múltiplas tentativas falhas**
- **Autenticação em dois fatores (2FA) para usuários administrativos**
- **Logout automático após período de inatividade**

## **Próximos Passos**
- Refinamento da experiência do usuário na gestão de permissões
- Implementação de logs detalhados para auditoria de acessos
- Criação de um painel administrativo para gerenciamento de usuários e papéis

---
Esse documento será atualizado conforme novas melhorias forem implementadas no sistema.

