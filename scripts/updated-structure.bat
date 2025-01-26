@echo off

mkdir apps\admin
mkdir apps\admin\templates\analyst
mkdir apps\admin\templates\manager
mkdir static\admin\css
mkdir static\admin\js

echo # /tenismatch/apps/admin/__init__.py > apps\admin\__init__.py
echo # /tenismatch/apps/admin/apps.py > apps\admin\apps.py
echo # /tenismatch/apps/admin/models.py > apps\admin\models.py
echo # /tenismatch/apps/admin/views.py > apps\admin\views.py
echo # /tenismatch/apps/admin/urls.py > apps\admin\urls.py
echo # /tenismatch/apps/admin/forms.py > apps\admin\forms.py
echo # /tenismatch/apps/admin/services.py > apps\admin\services.py
echo # /tenismatch/apps/admin/signals.py > apps\admin\signals.py
echo # /tenismatch/apps/admin/tests.py > apps\admin\tests.py

echo # /tenismatch/apps/admin/templates/admin/base_admin.html > apps\admin\templates\admin\base_admin.html
echo # /tenismatch/apps/admin/templates/analyst/dashboard.html > apps\admin\templates\analyst\dashboard.html
echo # /tenismatch/apps/admin/templates/analyst/model_creation.html > apps\admin\templates\analyst\model_creation.html
echo # /tenismatch/apps/admin/templates/analyst/data_upload.html > apps\admin\templates\analyst\data_upload.html
echo # /tenismatch/apps/admin/templates/analyst/training.html > apps\admin\templates\analyst\training.html
echo # /tenismatch/apps/admin/templates/analyst/training_detail.html > apps\admin\templates\analyst\training_detail.html

echo # /tenismatch/apps/admin/templates/manager/dashboard.html > apps\admin\templates\manager\dashboard.html
echo # /tenismatch/apps/admin/templates/manager/model_review.html > apps\admin\templates\manager\model_review.html
echo # /tenismatch/apps/admin/templates/manager/metrics.html > apps\admin\templates\manager\metrics.html
echo # /tenismatch/apps/admin/templates/manager/approvals.html > apps\admin\templates\manager\approvals.html

echo Created admin structure successfully!