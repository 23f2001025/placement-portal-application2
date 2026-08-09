from task import send_interview_email

result = send_interview_email.delay(
    "example@gmail.com",
    "Test Student",
    "Backend Developer",
    "2026-09-25",
    "10:00",
    1
)

print("Task queued with id:", result.id)
print("Waiting for result...")


# worker: python -m celery -A task worker --loglevel=info --pool=solo
#beat python -m celery -A task beat --loglevel=info

outcome = result.get(timeout=15)  
print("Result:", outcome)