from task_manager.celery import app
from .models import Report
from .utils import generate_report
from django.utils import timezone
from datetime import timedelta, datetime
from django.core.mail import send_mail
from django.conf import settings
from django.db.models import F
    
@app.task(name='send_unsent_reports')
def send_unsent_reports():
    '''Goes through report objects to see which one's last_sent '''
    current_datetime = timezone.localtime() #get current date and time
    report_objects = Report.objects.annotate(
        delta=current_datetime - F('last_sent')
        ).filter(delta__gte=timedelta(days=1))
        #in the statement above 'delta' stores the time difference between the time of last sent report and current datetime.
        #if delta is more than 1 day, it is queued for sending a report. This helps in accounting for worker downtimes.
    for r in report_objects:
        user = r.user
        subject = 'Your daily tasks report'
        message = generate_report(user)
        recipient_list = [user.email, ]
        send_mail(subject=subject, message=message, recipient_list=recipient_list,fail_silently=False, from_email=settings.EMAIL_HOST_USER)
        #setting last sent to 'time's time with current date
        dt = datetime.combine(current_datetime.date(), r.time)
        r.set_last_sent(dt)
        print(f'Sent an email to {user.email} about their tasks report.')