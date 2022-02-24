from task_manager.celery import app
from .models import Report, User
from .utils import generate_report
from django.utils import timezone
from datetime import date, datetime, time
from django.core.mail import send_mail
from django.conf import settings

@app.task(name='send_report_email')
def send_report_email(user_id):
    user = User.objects.get(pk=user_id)
    subject = 'Your daily tasks report'
    message = generate_report(user)
    recipient_list = [user.email, ]
    send_mail(subject=subject, message=message, recipient_list=recipient_list,fail_silently=False, from_email=settings.EMAIL_HOST_USER)
    print(f'Sent an email to {user.email} about their tasks report.')

@app.task(name='check_unsent_reports')
def check_unsent_reports():
    print("Checking for any unsent reports.")
    time_now = time(hour=timezone.localtime().hour, minute=timezone.localtime().minute)
    dt = date(1,1,1)
    dt1 = datetime.combine(dt, time_now)
    report_objects = Report.objects.filter(time__gte=time_now) #the time object stores no date, so if a report's time_to_be_sent is larger than the current time,
    #it needs to be sent on this current day
    for r in report_objects:
        dt2 = datetime.combine(dt, r.time)
        if (dt1 - dt2).seconds <= 60:
            send_report_email.delay(r.user.id)