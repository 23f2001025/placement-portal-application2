from celery_app import celery
from flask_mail import Message
from extensions import mail

_flask_app = None

def get_flask_app():
    
    global _flask_app
    if _flask_app is None:
        from app import create_app
        _flask_app = create_app()
    return _flask_app


@celery.task(bind=True, max_retries=3)
def send_interview_email(self, student_email, student_name, drive_title, interview_date, start_time, panel_no):
    app = get_flask_app()
    with app.app_context():
        try:
            msg = Message(
                subject=f"Interview Scheduled - {drive_title}",
                recipients=[student_email],
                body=(
                    f"Hi {student_name},\n\n"
                    f"Your interview for {drive_title} has been scheduled.\n\n"
                    f"Date: {interview_date}\n"
                    f"Time: {start_time}\n"
                    f"Panel: {panel_no}\n\n"
                    f"All the best!"
                )
            )
            mail.send(msg)
            return {"status": "sent", "to": student_email}
        except Exception as e:
            raise self.retry(exc=e, countdown=10)