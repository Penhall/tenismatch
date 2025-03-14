import os
import re
import glob
from pathlib import Path

# Configurar diretórios do projeto
PROJECT_ROOT = Path("D:/PYTHON/tenismatch")
APP_DIRS = [d for d in (PROJECT_ROOT / "apps").iterdir() if d.is_dir()]
TEMPLATE_DIRS = [PROJECT_ROOT / "templates"]
for app_dir in APP_DIRS:
    template_dir = app_dir / "templates"
    if template_dir.exists():
        TEMPLATE_DIRS.append(template_dir)

# Encontrar todos os templates existentes
existing_templates = []
for template_dir in TEMPLATE_DIRS:
    templates = glob.glob(str(template_dir) + "/**/*.html", recursive=True)
    for template in templates:
        # Converter para caminho relativo
        rel_path = os.path.relpath(template, str(template_dir))
        existing_templates.append(rel_path)

# Encontrar todos arquivos Python (views)
view_files = []
for app_dir in APP_DIRS:
    python_files = glob.glob(str(app_dir) + "/**/*.py", recursive=True)
    view_files.extend([f for f in python_files if "views" in f])

# Padrão para encontrar referências a templates
template_pattern = r"template_name\s*=\s*['\"]([^'\"]+)['\"]"

# Verificar cada arquivo de view
template_references = []
for view_file in view_files:
    with open(view_file, 'r', encoding='utf-8') as f:
        content = f.read()
        matches = re.findall(template_pattern, content)
        for match in matches:
            template_references.append({
                'file': view_file,
                'template': match
            })

# Comparar referências com templates existentes
missing_templates = []
for ref in template_references:
    if ref['template'] not in existing_templates:
        missing_templates.append(ref)

# Imprimir resultados
print(f"Templates referenciados mas não encontrados:")
for missing in missing_templates:
    print(f"Arquivo: {missing['file']}")
    print(f"   Template faltando: {missing['template']}")
    print()