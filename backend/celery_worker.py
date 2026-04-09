from celery import Celery
from celery.schedules import crontab


def make_celery(app):
    celery = Celery(
        app.import_name,
        broker=app.config["CELERY_BROKER_URL"],
        backend=app.config["CELERY_RESULT_BACKEND"],
        include=["tasks.jobs"],
    )
    celery.conf.update({
        'broker_url': app.config["CELERY_BROKER_URL"],
        'result_backend': app.config["CELERY_RESULT_BACKEND"],
    })
    celery.conf.timezone = "UTC"

    celery.conf.beat_schedule = {
        "daily-deadline-reminders": {
            "task": "tasks.jobs.send_deadline_reminders",
            "schedule": crontab(hour=8, minute=0),
        },
        "monthly-activity-report": {
            "task": "tasks.jobs.send_monthly_report",
            "schedule": crontab(day_of_month=1, hour=6, minute=0),
        },
    }

    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask
    return celery


def register_tasks(celery):
    from tasks.jobs import register_tasks as _reg
    _reg(celery)