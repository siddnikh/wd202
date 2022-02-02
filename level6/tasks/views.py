from django.shortcuts import render, redirect
from django.views.generic.base import View
from .models import Task
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.detail import DetailView
from django.contrib.auth.forms import UserCreationForm #remmeber to update the settings.py file for login url, etc.
from django.contrib.auth.views import LoginView
from django.contrib.auth.mixins import LoginRequiredMixin
from .utils import AuthenticationManager, TaskCreateForm

class UserLoginView(LoginView):
    template_name = 'tasks/user_login.html'
    success_url = '/tasks/'

class UserCreationView(CreateView):
    form_class = UserCreationForm
    template_name = "tasks/user_signup.html"
    success_url = '/user/login/'

class GenericDetailView(AuthenticationManager, DetailView, LoginRequiredMixin):
    model = Task
    template_name = "tasks/task_detail.html"

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

class GenericTaskUpdateView(AuthenticationManager, UpdateView, LoginRequiredMixin):
    model = Task
    form_class = TaskCreateForm
    template_name = 'tasks/update_task.html'
    success_url = '/tasks'

class GenericTaskCreateView(CreateView, LoginRequiredMixin):
    form_class = TaskCreateForm
    template_name = 'tasks/create_task.html'
    success_url = '/tasks/'

    def form_valid(self, form):
        """If the form is valid, save the associated model."""
        self.object = form.save()
        self.object.user = self.request.user
        return super().form_valid(form)

class GenericTaskView(AuthenticationManager, ListView, LoginRequiredMixin):
    queryset = Task.objects.filter(completed = False, deleted = False)
    template_name = "tasks/tasks.html"
    context_object_name = "tasks"
    paginate_by = 5

    def get_queryset(self):
        search_term = self.request.GET.get("search")
        if search_term:
            tasks = Task.objects.filter(title__icontains = search_term)
        else:
            tasks = Task.objects.filter(completed = False, deleted = False)
        return tasks
 
class GenericTaskCompleteView(AuthenticationManager, DeleteView, LoginRequiredMixin):

    model = Task
    template_name = 'tasks/complete_task.html'
    success_url = '/tasks/'

    #Manipulating DeleteView functions to make this work.
    def form_valid(self, form):
        success_url = self.get_success_url()
        self.object.completed = True
        self.object.save()
        return redirect(success_url)

class GenericCompletedTasksView(AuthenticationManager, ListView, LoginRequiredMixin):

    queryset = None
    template_name = "tasks/completed.html"
    context_object_name = "tasks"

    def get_queryset(self):
        tasks = Task.objects.filter(completed = True, deleted = False, user = self.request.user)
        return tasks

class GenericAllTasksView(AuthenticationManager, ListView, LoginRequiredMixin):
    queryset = Task.objects.filter(deleted = False)
    template_name = "tasks/all_tasks.html"
    context_object_name = "tasks"