from celery import Celery
from celery.schedules import crontab

celery = Celery(
    "placement_tasks",
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/0"
)

celery.conf.beat_schedule = {
    'daily-deadline-reminders': {
        'task': 'task.send_deadline_reminders',
        'schedule': crontab(hour=9, minute=0),  
    },
    'monthly-admin-report': {
        'task': 'task.send_monthly_report',
        'schedule': crontab(hour=8, minute=0, day_of_month=1),   
    },
}
celery.conf.timezone = 'Asia/Kolkata'   