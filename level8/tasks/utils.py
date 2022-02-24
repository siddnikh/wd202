from urllib import request
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http.response import HttpResponseRedirect
from .models import Task, Report
from django.forms import ModelForm, ValidationError, CharField, PasswordInput, TextInput, EmailField
from django.contrib.auth.forms import AuthenticationForm, UsernameField, UserCreationForm
from django.utils.translation import gettext, gettext_lazy as _
from django.contrib.auth import password_validation, models

class TaskCascadeMixin:

    def form_valid(self, form):
        self.object = form.save()
        self.object.user = self.request.user
        if self.object.status == 'COMPLETED': self.object.completed = True
        p = self.object.priority
        task = Task.objects.filter(user=self.request.user, completed=False, deleted=False, priority=p).first()
        #New task to non-collision p value, updating task to non-collision p value
        if task is None or task == self.object:
            return super().form_valid(form)
        
        # Cascading logic
        task.priority += 1
        tasks_to_update = []
        tasks_to_update.append(task)
        p += 1
        task = Task.objects.filter(user=self.request.user, completed=False, deleted=False, priority=p).first()
        while task is not None:
            task.priority += 1
            tasks_to_update.append(task)
            p += 1
            task = Task.objects.filter(user=self.request.user, completed=False, deleted=False, priority=p).first()
        Task.objects.bulk_update(tasks_to_update, ['priority'])
        return super().form_valid(form)

class AuthenticationManager(LoginRequiredMixin):

    def get_queryset(self):
        tasks = Task.objects.filter(deleted = False, user = self.request.user)
        return tasks

class PassRequestToFormViewMixin:
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs

class UserLoginForm(AuthenticationForm):
    username = UsernameField(widget=TextInput(attrs={
        'autofocus': True,
        'class': 'bg-gray-100 h-14 appearance-none rounded-xl my-6 w-full py-2 px-4 text-black leading-tight'
        }))
    password = CharField(
        label=_("Password"),
        strip=False,
        widget=PasswordInput(attrs={
            'autocomplete': 'current-password',
            'class': 'bg-gray-100 h-14 appearance-none rounded-xl my-6 w-full py-2 px-4 text-black leading-tight'
            }),
    )

class UserSignUpForm(UserCreationForm):

    username = UsernameField(widget=TextInput(attrs={
        'autofocus': True,
        'class': 'bg-gray-100 h-14 appearance-none rounded-xl my-6 w-full py-2 px-4 text-black leading-tight'
        }),
        help_text = _('150 characters or fewer. Letters, digits and @/./+/-/_ only.'))
    
    email = EmailField(widget=TextInput(attrs={
        'class': 'bg-gray-100 h-14 appearance-none rounded-xl my-6 w-full py-2 px-4 text-black leading-tight',
    }))

    password1 = CharField(
        label=_("Password"),
        strip=False,
        widget=PasswordInput(attrs={
            'autocomplete': 'current-password',
            'class': 'bg-gray-100 h-14 appearance-none rounded-xl my-6 w-full py-2 px-4 text-black leading-tight'
            }),
        help_text=password_validation.password_validators_help_text_html(),
    )
    password2 = CharField(
        label=_("Password confirmation"),
        widget=PasswordInput(attrs={
                'autocomplete': 'new-password',
                'class': 'bg-gray-100 h-14 appearance-none rounded-xl my-6 w-full py-2 px-4 text-black leading-tight'
                }),
        strip=False,
        help_text=_("Enter the same password as before, for verification."),
        )

    class Meta:
        model = models.User
        fields = ['username'] 

class TaskCreateForm(ModelForm):

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request')
        super(TaskCreateForm, self).__init__(*args, **kwargs)
        self.fields['title'].widget.attrs.update({
            'class': 'bg-gray-100 h-14 appearance-none rounded-xl my-6 w-full py-2 px-4 text-black leading-tight'
        })
        self.fields['description'].widget.attrs.update({
            'class': 'bg-gray-100 h-40 appearance-none rounded-xl my-6 w-full py-2 px-4 text-black leading-tight'
        })
        self.fields['priority'].widget.attrs.update({
            'class': 'block bg-gray-100 appearance-none rounded-xl my-6 py-2 px-4 text-black leading-tight'
        })
        self.fields['status'].widget.attrs.update({
            'class': 'h-5 w-5 text-black',
        })

    def clean_priority(self):
        priority = self.cleaned_data['priority']
        if(priority <= 0):
            raise ValidationError("Priority has to be larger than 0.")
        return priority

    def clean_title(self):
        title = self.cleaned_data['title']
        if(len(title) < 10):
            raise ValidationError("Title should be longer than 10 characters.")
        return title

    class Meta:
        model = Task
        fields = ['title', 'priority', 'description', 'completed', 'status']

class ReportForm(ModelForm):

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request')
        super(ReportForm, self).__init__(*args, **kwargs)
        self.fields['time'].widget.attrs.update({
        'class': 'bg-gray-100 h-10 appearance-none rounded-xl my-6 w-full py-2 px-4 text-black leading-tight'
        })
    
    def save(self, commit=True):
        if self.errors:
            raise ValueError(
                "The %s could not be %s because the data didn't validate." % (
                    self.instance._meta.object_name,
                    'created' if self.instance._state.adding else 'changed',
                )
            )
        if commit:
            # If committing, save the instance and the m2m data immediately.
            self.instance.user = self.request.user
            self.instance.last_sent = self.instance.time
            self.instance.save()
            self._save_m2m()
        else:
            # If not committing, add a method to the form to allow deferred
            # saving of m2m data.
            self.save_m2m = self._save_m2m
        return self.instance

    save.alters_data = True
    
    class Meta:
        model = Report
        fields = ['time']

def generate_report(user):
    tasks = Task.objects.filter(user=user)
    report = f'''Hi {user.username}, this is the status of your tasks:
    Pending: {tasks.filter(status='PENDING').count()}
    In Progress: {tasks.filter(status='IN_PROGRESS').count()}
    Completed: {tasks.filter(status='COMPLETED').count()}
    Cancelled: {tasks.filter(status='CANCELLED').count()}'''
    return report