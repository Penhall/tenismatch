import os

def generate_filtered_directory_structure_md(root_dir, output_file, extensions=None, ignore_dirs=None):
    """
    Gera um arquivo markdown com a estrutura de diretórios, filtrando por extensões específicas.
    
    Args:
        root_dir (str): Diretório raiz para iniciar a varredura
        output_file (str): Caminho do arquivo markdown a ser criado
        extensions (list): Lista de extensões a serem incluídas (ex: ['.py', '.html'])
        ignore_dirs (list): Lista de diretórios a serem ignorados
    """
    if extensions is None:
        extensions = ['.py', '.html']
    
    if ignore_dirs is None:
        ignore_dirs = ['.git', '__pycache__', 'venv', 'env', 'node_modules', '.pytest_cache']
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(f"# Estrutura de Diretórios do Projeto\n\n")
        f.write(f"Exibindo apenas arquivos com extensões: {', '.join(extensions)}\n\n")
        f.write("```\n")
        
        for root, dirs, files in os.walk(root_dir):
            # Ignorar diretórios indesejados
            dirs[:] = [d for d in dirs if d not in ignore_dirs]
            
            # Filtrar arquivos por extensão
            filtered_files = [file for file in files if os.path.splitext(file)[1].lower() in extensions]
            
            # Só mostrar o diretório se tiver arquivos que correspondam ao filtro
            if filtered_files:
                level = root.replace(root_dir, '').count(os.sep)
                indent = '    ' * level
                f.write(f"{indent}{os.path.basename(root) or os.path.abspath(root)}/\n")
                
                subindent = '    ' * (level + 1)
                for file in sorted(filtered_files):
                    f.write(f"{subindent}{file}\n")
        
        f.write("```\n")

# Substitua pelo caminho do seu projeto
project_dir = "D:/PYTHON/tenismatch/apps"
output_file = "D:/PYTHON/tenismatch/scripts/project_structure.md"

# Filtrar apenas arquivos Python e HTML
extensions = ['.py', '.html']

generate_filtered_directory_structure_md(project_dir, output_file, extensions)
print(f"Estrutura de diretórios gerada em: {output_file}")