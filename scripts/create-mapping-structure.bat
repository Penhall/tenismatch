# /tenismatch/scripts/create_mapping_structure.bat
@echo off

REM Criar diretórios
mkdir "..\apps\tenis_admin\templates\analyst\mapping"

REM Criar/atualizar arquivos
echo # /tenismatch/apps/tenis_admin/models.py > "..\apps\tenis_admin\models.py"
echo # /tenismatch/apps/tenis_admin/services/mapping_service.py > "..\apps\tenis_admin\services\mapping_service.py"
echo # /tenismatch/apps/tenis_admin/views.py > "..\apps\tenis_admin\views.py"

REM Templates
echo # /tenismatch/apps/tenis_admin/templates/analyst/mapping/preview.html > "..\apps\tenis_admin\templates\analyst\mapping\preview.html"
echo # /tenismatch/apps/tenis_admin/templates/analyst/mapping/mapping.html > "..\apps\tenis_admin\templates\analyst\mapping\mapping.html"
echo # /tenismatch/apps/tenis_admin/templates/analyst/mapping/confirmation.html > "..\apps\tenis_admin\templates\analyst\mapping\confirmation.html"

REM Forms e URLs
echo # /tenismatch/apps/tenis_admin/forms.py > "..\apps\tenis_admin\forms.py"
echo # /tenismatch/apps/tenis_admin/urls.py > "..\apps\tenis_admin\urls.py"

echo Estrutura de arquivos criada com sucesso!