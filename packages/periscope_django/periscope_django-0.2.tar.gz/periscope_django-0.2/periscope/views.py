import json
import re
from django.conf import settings
from django.db import connection, transaction
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

BAD_WORDS = {'drop', 'delete', 'update', 'into', 'insert', 'index', 'add', 'remove', 'grant', 'revoke', 'create',
             'createdb', 'createuser', 'createrole', 'destroy', 'disconnect', 'exec', 'execute', 'dropdb', 'primary',
             'key', 'rollback', ';', '--'}

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
      cursor.execute(command)
      data = [dict(zip([column[0] for column in cursor.description], [str(cell) for cell in row])) for row in cursor.fetchall()]
  except Exception as e:
    error = e.message
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
  return HttpResponse(json.dumps(response))
