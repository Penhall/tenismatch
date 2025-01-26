@echo off

mkdir apps\admin
mkdir apps\admin\templates
mkdir apps\admin\templates\analyst
mkdir apps\admin\templates\manager
mkdir apps\admin\static\admin\css
mkdir apps\admin\static\admin\js

echo # /tenismatch/apps/admin/__init__.py > apps\admin\__init__.py
echo # /tenismatch/apps/admin/apps.py > apps\admin\apps.py
echo # /tenismatch/apps/admin/models.py > apps\admin\models.py
echo # /tenismatch/apps/admin/views.py > apps\admin\views.py
echo # /tenismatch/apps/admin/urls.py > apps\admin\urls.py
echo # /tenismatch/apps/admin/forms.py > apps\admin\forms.py
echo # /tenismatch/apps/admin/services.py > apps\admin\services.py

echo # /tenismatch/apps/admin/templates/analyst/dashboard.html > apps\admin\templates\analyst\dashboard.html
echo # /tenismatch/apps/admin/templates/analyst/model_creation.html > apps\admin\templates\analyst\model_creation.html
echo # /tenismatch/apps/admin/templates/analyst/data_upload.html > apps\admin\templates\analyst\data_upload.html
echo # /tenismatch/apps/admin/templates/analyst/training.html > apps\admin\templates\analyst\training.html

echo # /tenismatch/apps/admin/templates/manager/dashboard.html > apps\admin\templates\manager\dashboard.html
echo # /tenismatch/apps/admin/templates/manager/model_review.html > apps\admin\templates\manager\model_review.html
echo # /tenismatch/apps/admin/templates/manager/metrics.html > apps\admin\templates\manager\metrics.html
echo # /tenismatch/apps/admin/templates/manager/approvals.html > apps\admin\templates\manager\approvals.html

echo Created admin structure successfully!