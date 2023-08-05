DATABASES = {
   'default' : {
       'ENGINE' : 'django.db.backends.postgresql_psycopg2',
       'NAME' : 'django-graph',
       'USER' : 'django',
       'PASSWORD': 'django'
   },
}

INSTALLED_APPS = (
    'dag',
    'dag.tests',
    'django.contrib.contenttypes',
)
