@echo off

:: Criar diretórios
mkdir apps\matching\urls
mkdir apps\profiles\urls
mkdir templates\profiles
mkdir templates\users

:: Criar arquivos urls.py
echo # /tenismatch/apps/matching/urls.py > apps\matching\urls.py
echo # /tenismatch/apps/profiles/urls.py > apps\profiles\urls.py

:: Criar arquivos templates
echo # /tenismatch/templates/profiles/detail.html > templates\profiles\detail.html
echo # /tenismatch/templates/profiles/preferences.html > templates\profiles\preferences.html
echo # /tenismatch/templates/users/profile.html > templates\users\profile.html

:: Criar arquivos apps.py
echo # /tenismatch/apps/users/apps.py > apps\users\apps.py
echo # /tenismatch/apps/matching/apps.py > apps\matching\apps.py
echo # /tenismatch/apps/profiles/apps.py > apps\profiles\apps.py

echo Arquivos faltantes criados com sucesso!