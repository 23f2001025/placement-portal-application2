from celery_app import celery
from flask_mail import Message
from extensions import mail
from datetime import datetime, timedelta
from models import db 

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


@celery.task(bind=True)
def send_deadline_reminders(self):
    app = get_flask_app()
    with app.app_context():
        from models import CampusDrive, Application, Student

        tomorrow = datetime.utcnow().date() + timedelta(days=1)

        
        drives = CampusDrive.query.filter(
            db.func.date(CampusDrive.deadline) == tomorrow
        ).all()

        sent_count = 0

        for drive in drives:
            already_applied_ids = {
                a.student_id for a in Application.query.filter_by(drive_id=drive.id).all()
            }

            eligible_students = Student.query.filter(
                Student.cgpa >= drive.cutoff_cgpa,
                Student.is_blacklisted == False
            ).all()

            for student in eligible_students:
                if student.id in already_applied_ids:
                    continue
                if not student.email:
                    continue

                try:
                    msg = Message(
                        subject=f"Deadline Tomorrow: {drive.job_title}",
                        recipients=[student.email],
                        body=(
                            f"Hi {student.name},\n\n"
                            f"This is a reminder that the application deadline for "
                            f"{drive.job_title} is tomorrow ({drive.deadline.strftime('%Y-%m-%d')}).\n\n"
                            f"Don't miss out — apply now through the placement portal!\n\n"
                            f"Package: {drive.package_lpa} LPA\n"
                            f"Location: {drive.location or 'Not specified'}"
                        )
                    )
                    mail.send(msg)
                    sent_count += 1
                except Exception as e:
                    print(f"Failed to send reminder to {student.email}: {e}")

        return {"status": "done", "reminders_sent": sent_count}



@celery.task(bind=True)
def send_monthly_report(self):
    app = get_flask_app()
    with app.app_context():
        from models import CampusDrive, Application, Admin
        from datetime import date

        today = date.today()
        first_of_this_month = today.replace(day=1)
        first_of_last_month = (first_of_this_month - timedelta(days=1)).replace(day=1)

        drives_last_month = CampusDrive.query.filter(
            CampusDrive.created_on >= first_of_last_month,
            CampusDrive.created_on < first_of_this_month
        ).all()

        total_drives = len(drives_last_month)
        total_applied = 0
        total_selected = 0

        drive_rows = ""
        for d in drives_last_month:
            apps = Application.query.filter_by(drive_id=d.id).all()
            applied = len(apps)
            selected = sum(1 for a in apps if a.status == "selected")
            total_applied += applied
            total_selected += selected

            drive_rows += f"""
            <tr>
                <td>{d.job_title}</td>
                <td>{applied}</td>
                <td>{selected}</td>
            </tr>
            """

        html_body = f"""
        <html>
        <body style="font-family: Arial, sans-serif;">
            <h2>Monthly Placement Report - {first_of_last_month.strftime('%B %Y')}</h2>
            <p><b>Total Drives Conducted:</b> {total_drives}</p>
            <p><b>Total Applications:</b> {total_applied}</p>
            <p><b>Total Students Selected:</b> {total_selected}</p>

            <h3>Drive-wise Breakdown</h3>
            <table border="1" cellpadding="8" cellspacing="0" style="border-collapse: collapse;">
                <tr style="background:#1e293b; color:white;">
                    <th>Drive</th>
                    <th>Applications</th>
                    <th>Selected</th>
                </tr>
                {drive_rows if drive_rows else "<tr><td colspan='3'>No drives this month</td></tr>"}
            </table>
        </body>
        </html>
        """

        admins = Admin.query.all()
        recipients = []
        
        admin_email = app.config.get('ADMIN_REPORT_EMAIL')

        if admin_email:
            msg = Message(
                subject=f"Monthly Placement Report - {first_of_last_month.strftime('%B %Y')}",
                recipients=[admin_email],
                html=html_body
            )
            mail.send(msg)

        return {"status": "sent", "drives": total_drives, "applied": total_applied, "selected": total_selected}