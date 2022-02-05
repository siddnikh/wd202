from django.db import models
from django.contrib.auth.models import User

class Task(models.Model):
    title = models.CharField(max_length = 100)
    description = models.TextField(blank = True, null = True)
    completed = models.BooleanField(default = False)
    created_date = models.DateTimeField(auto_now = True)
    deleted = models.BooleanField(default = False)
    user = models.ForeignKey(User, on_delete = models.CASCADE, null = True, blank = True)
    priority = models.IntegerField(unique = False, null = False, blank = False)

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