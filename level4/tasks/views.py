from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect

tasks = []
tasks_done = []

def tasks_view(request):
    return render(request, "tasks/tasks.html", {
        "avaialable": (len(tasks_done) > 0),
        "tasks": tasks
    })

def add_task(request):
    task = request.GET.get("task")
    tasks.append(task)
    return redirect('/tasks')

def delete_task(request, index): 
    del tasks[index - 1]
    return redirect('/tasks')

def complete_task(request, index):
    tasks_done.append(tasks[index - 1])
    del tasks[index - 1]
    return redirect('/tasks')

def completed_tasks(request):
    return render(request, 'tasks/completed.html', {
        "avaialable": (len(tasks_done) > 0),
        "completed": tasks_done,
    })

def all_tasks(request):
    return render(request, "tasks/all_tasks.html", {
        "completed" : tasks_done,
        "pending": tasks
    })
