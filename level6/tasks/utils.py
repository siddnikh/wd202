from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Task
from django.forms import ModelForm, ValidationError, CharField, PasswordInput, TextInput
from django.contrib.auth.forms import AuthenticationForm, UsernameField
from django.utils.translation import gettext, gettext_lazy as _

def cascading_tasks(priority, user):
    
    t = Task.objects.filter(priority = priority, user = user, deleted = False).first()
    if t is not None:
        cascading_tasks(priority + 1, user)
        t.increase_priority()

class AuthenticationManager(LoginRequiredMixin):

    def get_queryset(self):
        search_term = self.request.GET.get("search")
        if search_term:
            tasks = Task.objects.filter(title__icontains = search_term)
        else:
            tasks = Task.objects.filter(deleted = False, user = self.request.user)
        return tasks

class PassRequestToFormViewMixin:
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs

class UserLoginForm(AuthenticationForm):
    username = UsernameField(widget=TextInput(attrs={'autofocus': True, 'class': 'bg-gray-100 h-20 appearance-none rounded-xl my-6 w-full py-2 px-4 text-black leading-tight'}))
    password = CharField(
        label=_("Password"),
        strip=False,
        widget=PasswordInput(attrs={'autocomplete': 'current-password', 'class': 'bg-gray-100 h-20 appearance-none rounded-xl my-6 w-full py-2 px-4 text-black leading-tight'}),
    )

class TaskCreateForm(ModelForm):

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request')
        super().__init__(*args, **kwargs)

    def clean_priority(self):
        priority = self.cleaned_data['priority']
        t = Task.objects.filter(priority = priority, user = self.request.user, deleted = False).exists()
        if t:
            cascading_tasks(priority, self.request.user)    
        return priority

    def clean_title(self):
        title = self.cleaned_data['title']
        if(len(title) < 10):
            raise ValidationError("Title should be longer than 10 characters.")
        return title
    
    class Meta:
        model = Task
        fields = ['title', 'priority', 'description', 'completed']