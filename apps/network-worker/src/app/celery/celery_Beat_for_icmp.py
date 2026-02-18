# backend/app/tasks/celery_Beat_for_icmp.py
from celery.schedules import crontab
from celery_app import app

app.conf.beat_schedule = {
    "every-10-min-active": {
        "task": "schedule_all_pings",
        "schedule": crontab(minute="*/10"),
        "args": (True,),
    },
    "every-hour-all-devices": {
        "task": "schedule_all_pings",
        "schedule": crontab(minute=0, hour="*"),
        "args": (False,),
    },
    "snmp-every-minute": {
        "task": "snmp.schedule_all_scans",
        "schedule": 60.0,
    },
}
