import os
from celery import Celery
from django.conf import settings

# Configura a variável de ambiente para o settings do Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'jota_api.settings')

app = Celery('jota_api')

# Configuração usando as configurações do Django
app.config_from_object('django.conf:settings', namespace='CELERY')

# Descobre e registra automaticamente as tarefas nos apps do Django
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')