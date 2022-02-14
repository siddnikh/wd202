from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Task
from django.forms import ModelForm, ValidationError, CharField, PasswordInput, TextInput
from django.contrib.auth.forms import AuthenticationForm, UsernameField, UserCreationForm
from django.utils.translation import gettext, gettext_lazy as _
from django.contrib.auth import password_validation, models

class TaskCascadeMixin:

    def form_valid(self, form):
        """If the form is valid, save the associated model."""
        self.object = form.save()
        self.object.user = self.request.user
        # during task creation
        if self.object.status == 'COMPLETED': self.object.completed = True
        else: self.object.completed = False
        # Cascading logic
        p = self.object.priority
        tasks_to_update = []
        task = Task.objects.filter(priority = p,
                                    user = self.request.user,
                                    completed = False,
                                    deleted = False).first()
        while task is not None:
            tasks_to_update.append(task)
            p += 1
            task = Task.objects.filter(priority = p,
                                        user = self.request.user,
                                        completed = False,
                                        deleted = False).first()
        if len(tasks_to_update) > 0:
            for task_to_update in tasks_to_update:
                task_to_update.priority += 1
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
    
    def clean_user(self):
        user = self.request.user
        return user 

    class Meta:
        model = Task
        fields = ['title', 'priority', 'description', 'completed', 'status']