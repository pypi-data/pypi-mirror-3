__version__ = '0.9'

try:
  from django.conf import settings
except ImportError:
  settings = None

if settings:
  try:
    from django.conf.urls import include, url
  except ImportError:
    from django.conf.urls.defaults import include, url


  try:
    db_backend = settings.DATABASES['default']['ENGINE']
    if db_backend == 'django.db.backends.postgresql_psycopg2':
      __django_database__ = 'postgres'
    elif db_backend == 'django.db.backends.mysql':
      __django_database__ = 'mysql'
    else:
      __django_database__ = ''
  except (ImportError, AttributeError, TypeError):
    __django_database__ = ''


  try:
    root_project = __import__(settings.ROOT_URLCONF)
    urlpatterns = root_project.urls.urlpatterns
  except ImportError:
    urlpatterns = None
  except AttributeError:
    try:
      urlpatterns = root_project.urlpatterns
    except AttributeError:
      urlpatterns = None

  if urlpatterns:
    urlpatterns += (url(r'^periscope/', include('periscope.urls')),)
