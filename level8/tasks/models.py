from time import time
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import datetime

STATUS_CHOICES = (
    ("PENDING", "PENDING"),
    ("IN_PROGRESS", "IN_PROGRESS"),
    ("COMPLETED", "COMPLETED"),
    ("CANCELLED", "CANCELLED"),
)

class Task(models.Model):
    title = models.CharField(max_length = 100)
    description = models.TextField(blank = True, null = True)
    completed = models.BooleanField(default = False)
    created_date = models.DateTimeField(auto_now = True)
    deleted = models.BooleanField(default = False)
    user = models.ForeignKey(User, on_delete = models.CASCADE, null = True, blank = True)
    priority = models.IntegerField(unique = False, null = False, blank = False)
    status = models.CharField(max_length=100, choices=STATUS_CHOICES, default=STATUS_CHOICES[0][0])

    def delete(self):
        self.deleted = True
        self.save()
    
    def increase_priority(self):
        self.priority += 1
        self.save()
    
    def pretty_date(self):
        return self.created_date.strftime("%a %d %b")

    def __str__(self):
        return self.title

class History(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, null = False, blank = False)
    old_status = models.CharField(max_length=100, choices=STATUS_CHOICES, null=True, blank=True, default=None)
    new_status = models.CharField(max_length=100, choices=STATUS_CHOICES, null=False, blank=False)
    date_of_update = models.DateTimeField(editable = False)

    def save(self, *args, **kwargs):
        # checks if the object has been created or not
        if not self.id:
            self.date_of_update = timezone.now()
        return super(History, self).save(*args, **kwargs)

class Report(models.Model):
    time = models.TimeField(auto_now=False, auto_now_add=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)

    def update(self, time):
        self.time = time
        self.save()