from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from .models import Task

def tasks_view(request):
    search_term = request.GET.get("search")
    if search_term:
        tasks = Task.objects.filter(title__icontains = search_term)
    else:
        tasks = Task.objects.filter(completed = False, deleted = False)
    tasks_done = Task.objects.filter(completed = True, deleted = False)
    return render(request, 'tasks/tasks.html', {
        "tasks": tasks,
        "available": (len(tasks_done) > 0)
    })

def add_task(request):
    task = request.GET.get("task")
    Task(title = task).save()
    return redirect('/tasks')

def delete_task(request, index): 
    Task.objects.get(id = index).delete() #using overloaded function
    return redirect('/tasks')

def complete_task(request, index):
    t = Task.objects.get(id = index)
    t.completed = True
    t.save()
    return redirect('/tasks')

def completed_tasks(request):
    tasks = Task.objects.all().filter(completed = True)
    return render(request, 'tasks/completed.html', {
        "avaialable": (len(tasks) > 0),
        "completed": tasks,
    })

def all_tasks(request):
    tasks = Task.objects.filter(completed = False, deleted = False)
    tasks_done = Task.objects.filter(completed = True, deleted = False)
    return render(request, "tasks/all_tasks.html", {
        "completed" : tasks_done,
        "pending": tasks
    })
