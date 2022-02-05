from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Task
from django.forms import ModelForm, ValidationError, CharField, PasswordInput, TextInput
from django.contrib.auth.forms import AuthenticationForm, UsernameField, UserCreationForm
from django.utils.translation import gettext, gettext_lazy as _
from django.contrib.auth import password_validation, models

def cascading_tasks(priority, user):
    '''Returns a list of objects whose priority is to be increased by 1 when cascading tasks.'''
    objs = []
    t = Task.objects.filter(priority = priority, user = user, completed = False, deleted = False).first()
    if t is not None:
        objs.append(t)
        for obj in cascading_tasks(priority + 1, user): objs.append(obj)
    return objs

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
        self.fields['completed'].widget.attrs.update({
            'class': 'h-5 w-5 text-black',
            'type': 'checkbox'
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
        fields = ['title', 'priority', 'description', 'completed']