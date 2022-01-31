from django.db import models

class Task(models.Model):
    title = models.CharField(max_length = 100)
    description = models.TextField()
    completed = models.BooleanField(default = False)
    created_date = models.DateTimeField(auto_now = True)
    deleted = models.BooleanField(default = False)

    def delete(self):
        self.deleted = True
        self.save()

    def __str__(self):
        return self.title