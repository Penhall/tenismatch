
# Estrutura de Datasets e Modelos de IA

## **Visão Geral**
O **TenisMatch** utiliza um pipeline de Machine Learning baseado em datasets personalizados para criar um sistema de recomendação. O sistema processa e armazena datasets enviados por analistas, permitindo o treinamento e a validação de modelos de IA.

## **Pipeline de Dados**
O fluxo de dados segue as seguintes etapas:

1. **Upload do Dataset**: O analista faz o upload de arquivos CSV, JSON ou XLSX.
2. **Validação e Processamento**: O sistema verifica a estrutura do arquivo, garantindo que esteja no formato esperado.
3. **Armazenamento**: O dataset é salvo no banco de dados e no sistema de arquivos.
4. **Treinamento do Modelo**: O modelo de IA é treinado utilizando os dados processados.
5. **Revisão e Aprovação**: O gerente avalia os modelos treinados e aprova ou rejeita.
6. **Implantação**: Modelos aprovados são disponibilizados para recomendação em produção.

## **Estrutura do Banco de Dados**
O sistema utiliza um banco de dados relacional para armazenar datasets e modelos treinados. As tabelas principais são:

- **datasets**: Armazena informações sobre cada dataset carregado.
- **ai_models**: Contém os modelos treinados e suas métricas.
- **model_versions**: Histórico de versões dos modelos.

### **Modelo Dataset**
```python
class Dataset(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    file = models.FileField(upload_to='datasets/')
    records_count = models.IntegerField(default=0)
    status = models.CharField(
        max_length=20,
        choices=[('processing', 'Processando'), ('ready', 'Pronto')],
        default='processing'
    )
```

### **Modelo AI Model**
```python
class AIModel(models.Model):
    name = models.CharField(max_length=100)
    dataset = models.ForeignKey(Dataset, on_delete=models.CASCADE)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=20,
        choices=[('draft', 'Rascunho'), ('review', 'Em Revisão'), ('approved', 'Aprovado')],
        default='draft'
    )
    model_file = models.FileField(upload_to='models/')
    accuracy = models.FloatField(null=True, blank=True)
```

## **Processamento e Validação de Dados**
Durante o upload, o sistema realiza as seguintes validações:
- Estrutura do arquivo (colunas obrigatórias)
- Tipos de dados esperados
- Tratamento de valores nulos
- Registro do número de amostras

Exemplo de validação no Django:
```python
def validate_dataset(file):
    if not file.name.endswith(('.csv', '.json', '.xlsx')):
        raise ValidationError("Formato de arquivo não suportado.")
```

## **Treinamento de Modelos de IA**
Os modelos de IA utilizam **Scikit-learn** e técnicas como:
- **Filtragem baseada em conteúdo**
- **Filtragem colaborativa**
- **Redes neurais artificiais** (futuras versões)

Processo de treinamento:
```python
def train_model(dataset):
    data = pd.read_csv(dataset.file.path)
    model = RandomForestClassifier()
    model.fit(data['features'], data['labels'])
    return model
```

## **Aprovação e Implantação**
Após o treinamento, os modelos passam por uma revisão:
- Modelos com **precisão acima de 80%** são enviados para aprovação.
- O gerente pode aprovar/rejeitar via painel administrativo.
- Modelos aprovados são salvos para uso nas recomendações.

## **Próximos Passos**
- Implementação de métricas avançadas para avaliação dos modelos
- Melhorias no pipeline de pré-processamento de dados
- Integração com frameworks de deep learning (TensorFlow, PyTorch)

---
Esse documento será atualizado conforme novas funcionalidades forem adicionadas ao sistema.

