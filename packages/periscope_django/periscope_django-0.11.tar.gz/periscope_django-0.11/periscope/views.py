import json
import re
try:
  from collections import OrderedDict
except ImportError:
  from OrderedDict import OrderedDict
from periscope import __version__, __django_database__
from django.conf import settings
from django.db import connection, transaction
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

BAD_WORDS = set(['drop', 'delete', 'update', 'into', 'insert', 'index', 'add', 'remove', 'grant', 'revoke', 'create',
             'createdb', 'createuser', 'createrole', 'destroy', 'disconnect', 'exec', 'execute', 'dropdb', 'primary',
             'key', 'rollback', ';', '--'])

MAX_ROWS = 2000
MAX_SIZE = MAX_ROWS * 500

def login_required(view):
  def decorator(request):
    try:
      if request.POST['password'] == settings.PERISCOPE_PASSWORD:
        return view(request)
      else:
        raise Exception('Password invalid.')
    except Exception as e:
      return HttpResponse(json.dumps({'error': str(e)}))
  return decorator

@csrf_exempt
@login_required
@transaction.commit_manually
def look(request):
  try: 
    command = request.POST['sql'].strip()
    command_words = re.sub(r'\s+', ' ', re.sub(r'[^a-zA-Z0-9_]', ' ', command.lower())).split(' ')
    data = error = None
    if not command:
      pass
    elif set(command_words) & BAD_WORDS:
      error = 'Potentially harmful keyword found. Blocking command.'
    else:
      cursor = connection.cursor()
      if __django_database__ == 'postgres':
        cursor.execute("explain %s" % command)
        match = re.search("rows=(\d+) width=(\d+)\)$", cursor.fetchall()[0][0])
        row_count = int(match.group(1))
        width = int(match.group(2))
        if row_count > MAX_ROWS:
          raise Exception("Command blocked because it may be too slow. Estimated at %d rows. Commands must return fewer than %d rows." % (row_count, MAX_ROWS))
        if row_count * width > MAX_SIZE:
          raise Exception("Command blocked because it may be too slow. Estimated at %d bytes. Commands must use fewer than %d bytes." % (row_count * width, MAX_SIZE))
      cursor.execute(command)
      data = [OrderedDict(zip([column[0] for column in cursor.description], [unicode(cell) for cell in row])) for row in cursor.fetchall()]
  except Exception as e:
    if len(e.args) == 2:
      error = str(e.args[1]) # In Django DatabaseErrors, args[0] is the code and args[1] is the message
    else:
      error = str(e)
  finally:
    transaction.rollback()
  response = {'error': error} if error else {'data': data, 'error': None}
  return HttpResponse(json.dumps(response))

@csrf_exempt
@login_required
def login(request):
  try:
    table_names = connection.introspection.table_names()
    cursor = connection.cursor()
    tables = []
    for t in table_names:
      cursor.execute("select column_name, data_type from information_schema.columns where table_name = %s", [t])
      tables.append({
        'name': t,
        'columns': [{'name': column[0], 'sql_type': column[1]} for column in cursor.fetchall()]
      })
    response = {'tables': tables, 'error': None}
  except Exception as e:
    response = {'error': str(e)} 
  response.update({
    'version': __version__,
    'database_type': __django_database__,
    'server_type': 'django'
  })
  return HttpResponse(json.dumps(response))
