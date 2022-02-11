from django.shortcuts import redirect
from .models import Task
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
#remmeber to update the settings.py file for login url, etc.
from django.contrib.auth.views import LoginView
from django.contrib.auth.mixins import LoginRequiredMixin
from .utils import AuthenticationManager, TaskCreateForm, PassRequestToFormViewMixin, UserLoginForm, UserSignUpForm
from django.db import transaction

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
        p = self.object.priority
        tasks_to_update = []
        task = None
        try: task = Task.objects.get(priority = p, user = self.request.user, completed = False, deleted = False)
        except: pass
        while task is not None:
            tasks_to_update.append(task)
            p += 1
            try: task = Task.objects.get(priority = p, user = self.request.user, completed = False, deleted = False)
            except: task = None
        if len(tasks_to_update) > 0:
            for task_to_update in tasks_to_update:
                task_to_update.priority += 1
            Task.objects.bulk_update(tasks_to_update, ['priority'])
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