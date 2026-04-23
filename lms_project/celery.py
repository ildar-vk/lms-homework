import os
from celery import Celery

# Устанавливаем модуль настроек Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lms_project.settings')

app = Celery('lms_project')

# Загружаем настройки из Django
app.config_from_object('django.conf:settings', namespace='CELERY')

# Автоматически находим задачи в приложениях
app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
