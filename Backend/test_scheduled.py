
from task import send_deadline_reminders, send_monthly_report

print(send_deadline_reminders.delay())
print(send_monthly_report.delay())