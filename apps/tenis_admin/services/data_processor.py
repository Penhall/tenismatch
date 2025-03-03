from django.core.exceptions import ValidationError

class DataProcessorService:
    @staticmethod
    def validate_dataset(dataset):
        """Valida a estrutura e conteúdo de um dataset"""
        required_columns = {'jogador', 'idade', 'nivel_habilidade', 'estilo_jogo'}
        if not required_columns.issubset(dataset.columns):
            missing = required_columns - set(dataset.columns)
            raise ValidationError(f'Colunas obrigatórias faltando: {missing}')

    @staticmethod
    def clean_data(dataset):
        """Realiza limpeza básica dos dados"""
        dataset = dataset.dropna()
        dataset = dataset.drop_duplicates()
        return dataset

    @classmethod
    def process_input_data(cls, dataset):
        """Processamento completo dos dados de entrada"""
        cls.validate_dataset(dataset)
        return cls.clean_data(dataset)
