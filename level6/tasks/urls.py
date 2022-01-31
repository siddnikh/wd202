from django.urls import path
from . import views

urlpatterns = [
    path("tasks/", views.GenericTaskView.as_view()),
    path("add-task/", views.CreateTaskView.as_view()),
    path("delete-task/<int:index>/", views.delete_task),
    path("complete_task/<int:index>/", views.complete_task),
    path("completed_tasks/", views.completed_tasks),
    path("all_tasks/", views.all_tasks),
]