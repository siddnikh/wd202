from django.db import models
from django.contrib.auth.models import User

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