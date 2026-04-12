from app import app, celery
with app.app_context():
    result = celery.send_task("tasks.jobs.send_monthly_report")
    print("Task ID:", result.id)
    print("Waiting for result...")
    output = result.get(timeout=30)
    print("Done:", output)