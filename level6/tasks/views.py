from django.shortcuts import redirect
from .models import Task
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
#remmeber to update the settings.py file for login url, etc.
from django.contrib.auth.views import LoginView
from django.contrib.auth.mixins import LoginRequiredMixin
from .utils import AuthenticationManager, TaskCreateForm, PassRequestToFormViewMixin, UserLoginForm, UserSignUpForm, cascading_tasks

class UserLoginView(LoginView):
    form_class = UserLoginForm
    template_name = 'tasks/user_login.html'
    success_url = '/tasks/'

class UserCreationView(CreateView):
    form_class = UserSignUpForm
    template_name = "tasks/user_signup.html"
    success_url = '/user/login/'

class GenericTaskDeleteView(AuthenticationManager, DeleteView, LoginRequiredMixin):

    model = Task
    template_name = 'tasks/delete_task.html'
    success_url = '/tasks'

    #soft deletion
    def form_valid(self, form):
        success_url = self.get_success_url()
        self.object.deleted = True
        self.object.save()
        return redirect(success_url)

class GenericTaskUpdateView(PassRequestToFormViewMixin, AuthenticationManager, UpdateView, LoginRequiredMixin):
    model = Task
    form_class = TaskCreateForm
    template_name = 'tasks/update_task.html'
    success_url = '/tasks'

class GenericTaskCreateView(PassRequestToFormViewMixin, CreateView, LoginRequiredMixin):
    form_class = TaskCreateForm
    template_name = 'tasks/create_task.html'
    success_url = '/tasks/'

    def form_valid(self, form):
        """If the form is valid, save the associated model."""
        self.object = form.save()
        self.object.user = self.request.user
        t = Task.objects.filter(priority = self.object.priority, user = self.request.user, completed = False, deleted = False).exists()
        if t is not None:
            objs = cascading_tasks(self.object.priority, self.request.user)
            for obj in objs:
                obj.priority += 1
            Task.objects.bulk_update(objs, ['priority'])
        return super().form_valid(form)

class GenericTaskView(AuthenticationManager, ListView, LoginRequiredMixin):
    queryset = None
    template_name = "tasks/tasks.html"
    context_object_name = "tasks"

    def get_queryset(self):
        tasks = Task.objects.filter(user = self.request.user, completed = False, deleted = False).order_by('priority')
        return tasks

class GenericCompletedTasksView(AuthenticationManager, ListView, LoginRequiredMixin):

    queryset = None
    template_name = "tasks/completed.html"
    context_object_name = "tasks"

    def get_queryset(self):
        tasks = Task.objects.filter(completed = True, deleted = False, user = self.request.user).order_by('priority')
        return tasks

class GenericAllTasksView(AuthenticationManager, ListView, LoginRequiredMixin):
    
    queryset = None
    template_name = "tasks/all_tasks.html"
    context_object_name = "tasks"

    def get_queryset(self):
        tasks = Task.objects.filter(deleted = False, user = self.request.user).order_by('priority')
        return tasks