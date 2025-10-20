from celery import Celery
from celery.schedules import crontab
from celery_app import app
import os



app.conf.beat_schedule = {
    'every-thirty-sek-active': {
        'task': 'schedule_all_pings',
        'schedule': crontab(minute='*/10'),
        'args': (True,), 
    },
    'every-10-min-all-devices': { 
        'task': 'schedule_all_pings',
        'schedule': crontab(minute=0), 
        'args': (False,), 
    },
}