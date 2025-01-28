# Estrutura do Projeto TenisMatch

```
d:/PYTHON/tenismatch/
├── .gitignore
├── asgi.py
├── manage.py
├── README.md
├── requirements.txt
├── apps/
│   ├── matching/
│   │   ├── ml/
│   │   │   ├── dataset.py
│   │   │   └── training.py
│   │   ├── services/
│   │   │   ├── data_processor.py
│   │   │   └── recommender.py
│   │   ├── urls/
│   │   ├── migrations/
│   │   │   └── 0001_initial.py
│   │   ├── __init__.py
│   │   ├── apps.py
│   │   ├── forms.py
│   │   ├── models.py
│   │   ├── urls.py
│   │   └── views.py
│   ├── profiles/
│   │   ├── migrations/
│   │   │   ├── 0001_initial.py
│   │   │   └── 0002_profile_preferred_brands_profile_preferred_colors_and_more.py
│   │   ├── urls/
│   │   ├── __init__.py
│   │   ├── apps.py
│   │   ├── forms.py
│   │   ├── models.py
│   │   ├── urls.py
│   │   └── views.py
│   ├── tenis_admin/
│   │   ├── static/
│   │   │   └── admin/
│   │   │       ├── css/
│   │   │       └── js/
│   │   ├── templates/
│   │   │   ├── admin/
│   │   │   │   └── base_admin.html
│   │   │   ├── analyst/
│   │   │   │   ├── dashboard.html
│   │   │   │   ├── data_upload.html
│   │   │   │   ├── generate_data.html
│   │   │   │   ├── model_creation.html
│   │   │   │   ├── training_detail.html
│   │   │   │   └── training.html
│   │   │   └── manager/
│   │   │       ├── approvals.html
│   │   │       ├── dashboard.html
│   │   │       ├── metrics.html
│   │   │       └── model_review.html
│   │   ├── migrations/
│   │   │   ├── 0001_initial.py
│   │   │   └── 0002_dataset_dataset_type_dataset_file_size_and_more.py
│   │   ├── __init__.py
│   │   ├── apps.py
│   │   ├── forms.py
│   │   ├── mixins.py
│   │   ├── models.py
│   │   ├── services.py
│   │   ├── signals.py
│   │   ├── storage.py
│   │   ├── tests_deployment.py
│   │   ├── tests_integration.py
│   │   ├── tests.py
│   │   ├── urls.py
│   │   └── views.py
│   └── users/
│       ├── migrations/
│       │   ├── 0001_initial.py
│       │   └── 0002_user_premium_until.py
│       ├── __init__.py
│       ├── apps.py
│       ├── forms.py
│       ├── middleware.py
│       ├── models.py
│       ├── serializers.py
│       ├── urls.py
│       └── views.py
├── core/
│   ├── __init__.py
│   ├── settings.py
│   ├── urs.py
│   └── wsgi.py
├── docs/
│   ├── about.md
│   └── estrutura.md
├── media/
│   ├── avatars/
│   │   ├── image.png
│   │   ├── WhatsApp_Image_2025-01-04_at_11.48.18.jpeg
│   │   └── WhatsApp_Image_2025-01-13_at_10.58.25.jpeg
│   └── datasets/
│       ├── dataset_1.csv
│       ├── dataset_2.csv
│       ├── dataset_QEuJA4Z.csv
│       ├── dataset.csv
│       └── vendas.csv
├── resources/
│   ├── img1.png
│   ├── img2.jpg
│   └── img3.jpg
├── scripts/
│   ├── create-admin-structure.bat
│   ├── create-missing-files.bat
│   ├── create-structure-windows.bat
│   ├── create-structure.sh
│   ├── new-structure.bat
│   └── updated-structure.bat
├── static/
│   ├── admin/
│   │   ├── css/
│   │   └── js/
│   ├── css/
│   │   └── styles.css
│   ├── img/
│   │   ├── default-avatar.jpeg
│   │   ├── default-avatar.jpeg.png
│   │   ├── default-avatar.png
│   │   ├── hero-image.jpg
│   │   └── testimonials/
│   │       ├── user1.jpg
│   │       ├── user2.jpg
│   │       └── user3.jpg
│   └── tenis_admin/
│       ├── css/
│       └── js/
└── templates/
    ├── matching/
    │   ├── match_detail.html
    │   ├── match_list.html
    │   └── sneaker_form.html
    ├── profiles/
    │   ├── dashboard.html
    │   ├── detail.html
    │   ├── edit.html
    │   └── preferences.html
    ├── users/
    │   ├── login.html
    │   ├── profile.html
    │   └── signup.html
    ├── about.html
    ├── base.html
    ├── landing.html
    └── signup_premium.html
