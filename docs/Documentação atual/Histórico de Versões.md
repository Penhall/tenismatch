# Changelog

## **Visão Geral**
Este documento acompanha todas as mudanças realizadas no **TenisMatch**, incluindo novas funcionalidades, correções de bugs e melhorias de performance. O formato segue o padrão **Keep a Changelog**.

---

## **[1.0.0] - Data de Lançamento**
### **Adicionado**
- Implementação inicial do sistema de recomendação com Machine Learning.
- Autenticação via Django Auth e RBAC para controle de permissões.
- Upload e processamento de datasets em CSV, JSON e XLSX.
- API RESTful com endpoints para usuários, datasets e recomendações.
- Interface responsiva baseada em Django Templates e Tailwind CSS.
- Sistema de revisão e aprovação de modelos de IA.

### **Corrigido**
- Melhorias na validação de permissões de usuários.
- Correção de problemas no pipeline de treinamento de modelos.
- Ajuste no tempo de expiração do token de autenticação para segurança.

### **Alterado**
- Otimização do banco de dados para melhor performance em grandes volumes de dados.
- Refatoração da arquitetura do backend para melhor modularização.

---

## **[0.9.0] - Versão Beta**
### **Adicionado**
- Primeira versão funcional com login, recomendação e administração de datasets.
- Implementação do pipeline de Machine Learning com Scikit-learn.
- Sistema de notificações para usuários premium.

### **Corrigido**
- Ajustes em permissões de acesso na API.
- Correção de erros na interface de upload de datasets.

### **Alterado**
- Ajuste na exibição das recomendações no painel do usuário.

---

## **[0.8.0] - Protótipo Inicial**
### **Adicionado**
- Estrutura inicial do projeto com Django e SQLite.
- Implementação do sistema de usuários e autenticação.
- Primeira versão do modelo de recomendação.

### **Corrigido**
- Correção de problemas no esquema do banco de dados.

### **Alterado**
- Ajustes no layout da interface do usuário.

---

## **Próximos Passos**
- Expansão do sistema de recomendação com modelos de deep learning.
- Implementação de testes automatizados para garantir estabilidade.
- Otimização da interface do usuário para melhor experiência.

---
Esse documento será atualizado conforme novas versões forem lançadas.

