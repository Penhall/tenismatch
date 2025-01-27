@echo off

mkdir apps\tenis_admin
mkdir apps\tenis_admin\templates\analyst
mkdir apps\tenis_admin\templates\manager
mkdir static\tenis_admin\css
mkdir static\tenis_admin\js

echo # /tenismatch/apps/tenis_admin/__init__.py > apps\tenis_admin\__init__.py
echo # /tenismatch/apps/tenis_admin/apps.py > apps\tenis_admin\apps.py
echo # /tenismatch/apps/tenis_admin/models.py > apps\tenis_admin\models.py
echo # /tenismatch/apps/tenis_admin/views.py > apps\tenis_admin\views.py
echo # /tenismatch/apps/tenis_admin/urls.py > apps\tenis_admin\urls.py
echo # /tenismatch/apps/tenis_admin/forms.py > apps\tenis_admin\forms.py
echo # /tenismatch/apps/tenis_admin/services.py > apps\tenis_admin\services.py
echo # /tenismatch/apps/tenis_admin/signals.py > apps\tenis_admin\signals.py
echo # /tenismatch/apps/tenis_admin/tests.py > apps\tenis_admin\tests.py

echo # /tenismatch/apps/tenis_admin/templates/analyst/dashboard.html > apps\tenis_admin\templates\analyst\dashboard.html
echo # /tenismatch/apps/tenis_admin/templates/analyst/model_creation.html > apps\tenis_admin\templates\analyst\model_creation.html
echo # /tenismatch/apps/tenis_admin/templates/analyst/data_upload.html > apps\tenis_admin\templates\analyst\data_upload.html
echo # /tenismatch/apps/tenis_admin/templates/analyst/training.html > apps\tenis_admin\templates\analyst\training.html
echo # /tenismatch/apps/tenis_admin/templates/analyst/training_detail.html > apps\tenis_admin\templates\analyst\training_detail.html

echo # /tenismatch/apps/tenis_admin/templates/manager/dashboard.html > apps\tenis_admin\templates\manager\dashboard.html
echo # /tenismatch/apps/tenis_admin/templates/manager/model_review.html > apps\tenis_admin\templates\manager\model_review.html
echo # /tenismatch/apps/tenis_admin/templates/manager/metrics.html > apps\tenis_admin\templates\manager\metrics.html
echo # /tenismatch/apps/tenis_admin/templates/manager/approvals.html > apps\tenis_admin\templates\manager\approvals.html

echo Structure created successfully!