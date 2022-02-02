from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Task
from django.forms import ModelForm, ValidationError

class AuthenticationManager(LoginRequiredMixin):

    def get_queryset(self):
        search_term = self.request.GET.get("search")
        if search_term:
            tasks = Task.objects.filter(title__icontains = search_term)
        else:
            tasks = Task.objects.filter(deleted = False, user = self.request.user)
        return tasks

class TaskCreateForm(ModelForm):

    def clean_title(self):
        title = self.cleaned_data['title']
        if(len(title) < 10):
            raise ValidationError("Title should be longer than 10 characters.")
        return title.upper()
    
    class Meta:
        model = Task
        fields = ['title', 'description', 'completed']