# /tenismatch/apps/tenis_admin/services/data_generation_service.py
import pandas as pd
import numpy as np
import json
import os
from django.conf import settings
from datetime import datetime

class DataGenerationService:
    @staticmethod
    def generate_synthetic_data(n_samples, include_labels=True):
        """
        Gera dados sintéticos para o modelo de recomendação baseado em tênis.
        Pode ser usado diretamente pelo serviço ou pela view.
        """
        # Lista de marcas de tênis possíveis
        marcas = ['Nike', 'Adidas', 'Puma', 'Reebok', 'New Balance', 'Asics', 'Vans', 'Converse']
        
        # Lista de estilos possíveis
        estilos = ['Casual', 'Esportivo', 'Social', 'Vintage', 'Streetwear', 'Skate', 'Running', 'Basketball']
        
        # Lista de cores possíveis
        cores = ['Preto', 'Branco', 'Azul', 'Vermelho', 'Cinza', 'Verde', 'Amarelo', 'Rosa', 'Roxo', 'Laranja']
        
        # Faixas de preço
        precos_min = 100
        precos_max = 1200
        
        # Gerar dados aleatórios
        data = {
            'tenis_marca': np.random.choice(marcas, size=n_samples),
            'tenis_estilo': np.random.choice(estilos, size=n_samples),
            'tenis_cores': [np.random.choice(cores, size=np.random.randint(1, 3)).tolist() for _ in range(n_samples)],
            'tenis_preco': np.random.uniform(precos_min, precos_max, size=n_samples).round(2),
            'idade': np.random.randint(18, 60, size=n_samples),
            'genero': np.random.choice(['M', 'F', 'Outro'], size=n_samples, p=[0.48, 0.48, 0.04]),
            'estado_civil': np.random.choice(['Solteiro', 'Casado', 'Divorciado', 'Viúvo'], size=n_samples)
        }
        
        # Adicionar labels para treinamento supervisionado se solicitado
        if include_labels:
            # Simular compatibilidade entre perfis
            data['compatibilidade'] = np.zeros(n_samples)
            
            for i in range(n_samples):
                # Fatores que aumentam compatibilidade
                comp_score = 0.0
                
                # Preferências de marca (maior peso)
                if data['tenis_marca'][i] in ['Nike', 'Adidas']:
                    comp_score += 0.3
                elif data['tenis_marca'][i] in ['Puma', 'Reebok']:
                    comp_score += 0.2
                else:
                    comp_score += 0.1
                    
                # Preferências de estilo
                if data['tenis_estilo'][i] in ['Casual', 'Streetwear']:
                    comp_score += 0.2
                elif data['tenis_estilo'][i] in ['Esportivo', 'Running']:
                    comp_score += 0.15
                else:
                    comp_score += 0.1
                    
                # Faixas de preço (indicador de hábitos de consumo)
                if data['tenis_preco'][i] > 500:
                    comp_score += 0.1
                    
                # Adicionar alguma aleatoriedade
                comp_score += np.random.uniform(0, 0.4)
                
                # Normalizar entre 0 e 1
                comp_score = min(max(comp_score, 0), 1)
                
                data['compatibilidade'][i] = round(comp_score, 2)
        
        # Converter valores de lista para strings JSON (para compatibilidade com CSV)
        data['tenis_cores'] = [json.dumps(cores) for cores in data['tenis_cores']]
        
        return data
    
    @staticmethod
    def save_synthetic_data(data, user_id, dataset_name=None):
        """
        Salva dados sintéticos como um dataset para uso posterior.
        
        Args:
            data: dicionário com os dados gerados
            user_id: ID do usuário que está criando o dataset
            dataset_name: nome opcional para o dataset
        
        Returns:
            Caminho para o arquivo salvo
        """
        from ..models import Dataset
        import uuid
        
        # Criar o dataframe
        df = pd.DataFrame(data)
        
        # Gerar nome de arquivo único
        if not dataset_name:
            dataset_name = f"synthetic_dataset_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        filename = f"{dataset_name}_{uuid.uuid4().hex[:8]}.csv"
        
        # Garantir que o diretório existe
        dataset_dir = os.path.join(settings.MEDIA_ROOT, 'datasets')
        os.makedirs(dataset_dir, exist_ok=True)
        
        # Caminho completo para o arquivo
        file_path = os.path.join(dataset_dir, filename)
        
        # Salvar o CSV
        df.to_csv(file_path, index=False)
        
        # Criar entrada no banco de dados
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        try:
            user = User.objects.get(id=user_id)
            
            # Criar o objeto Dataset
            dataset = Dataset.objects.create(
                name=dataset_name,
                description=f"Dataset sintético com {len(df)} amostras",
                file=f"datasets/{filename}",
                dataset_type='generated',
                status='ready',
                records_count=len(df),
                uploaded_by=user
            )
            
            return {
                'success': True,
                'dataset': dataset,
                'file_path': file_path
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }