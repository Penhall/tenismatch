# Diretrizes de Desenvolvimento (Dev Guidelines)

## **Visão Geral**
Este documento estabelece as diretrizes para o desenvolvimento do **TenisMatch**, garantindo consistência, boas práticas e qualidade de código em todas as fases do projeto.

## **Padrões de Código**
O projeto segue os seguintes padrões:
- **Linguagem**: Python 3.10+
- **Framework**: Django
- **Estilo de Código**: PEP 8 e PEP 257 para docstrings
- **Ferramentas de Linter**: Flake8 e Black
- **Controle de Versão**: Git (GitHub)
- **Convenção de Nomenclatura**:
  - Variáveis: `snake_case`
  - Classes: `PascalCase`
  - Métodos e Funções: `snake_case`
  - Constantes: `UPPER_SNAKE_CASE`

## **Estrutura do Projeto**
O repositório segue a seguinte organização:
```
tenismatch/
│── apps/
│   ├── users/
│   ├── matching/
│   ├── datasets/
│   ├── ai_models/
│── core/
│── static/
│── templates/
│── docs/
│── tests/
│── manage.py
│── requirements.txt
```

## **Fluxo de Desenvolvimento**
1. Criar um branch para cada nova feature ou correção:
```bash
git checkout -b feature/nome_da_feature
```
2. Implementar a funcionalidade seguindo os padrões estabelecidos.
3. Escrever testes para a nova funcionalidade.
4. Realizar commit seguindo a convenção de mensagens:
```bash
git commit -m "feat: adiciona suporte a múltiplos datasets"
```
5. Criar um Pull Request e aguardar revisão.

## **Boas Práticas**
### **1. Gerenciamento de Dependências**
- Todas as dependências devem ser declaradas no `requirements.txt`.
- Utilize `virtualenv` para isolamento do ambiente:
```bash
python -m venv venv
source venv/bin/activate
```
- Atualizar dependências com segurança:
```bash
pip install -r requirements.txt
```

### **2. Testes**
- Todos os códigos novos devem incluir testes unitários e de integração.
- Utilizamos **pytest** e **Django TestCase**:
```bash
pytest tests/
```
- Testes devem cobrir pelo menos **80%** do código-fonte.

### **3. Documentação**
- Todo novo módulo deve ter docstrings conforme PEP 257.
- Comentários devem ser claros e concisos.
- Atualizar a documentação no diretório `docs/`.

### **4. Segurança**
- Nunca faça commit de credenciais ou chaves de API.
- Use variáveis de ambiente (`.env`) para armazenar informações sensíveis.
- Ative logs para monitoramento de erros:
```bash
import logging
logger = logging.getLogger(__name__)
```

## **CI/CD e Deploy**
- Utilizamos **GitHub Actions** para CI/CD.
- O código deve passar nos testes antes de ser mesclado no branch principal.
- O deploy é automatizado para ambientes de produção e staging.

## **Próximos Passos**
- Melhorar a cobertura de testes automatizados.
- Implementação de ferramentas de análise estática de código.
- Integração contínua com monitoramento de performance.

---
Esse documento será atualizado conforme novas diretrizes forem adicionadas ao projeto.

