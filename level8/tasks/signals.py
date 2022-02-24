from time import strptime
from django.db.models.signals import post_save
from .models import Task, History, Report
from django.dispatch import receiver
from task_manager.celery import app, crontab
from datetime import *

@receiver(post_save, sender=Task, dispatch_uid="update_history_api")
def update_history(sender, instance, **kwargs):
    h = History.objects.filter(task = instance).order_by('id').last()

    # When the object is updated but there's no change in status
    if h is not None and instance.status == h.new_status:
        pass
    # When there is a new task created
    elif h is None:
        History.objects.create(task=instance, old_status=None, new_status=instance.status)
    # When a task's status is updated
    else:
        history_queryset = History.objects.filter(task = instance)
        History.objects.create(task=instance, old_status=h.new_status, new_status=instance.status)