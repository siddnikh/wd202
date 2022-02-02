from django.urls import path
from . import views
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path("tasks/", views.GenericTaskView.as_view()),
    path('create-task/', views.GenericTaskCreateView.as_view()),
    path("delete-task/<pk>/", views.GenericTaskDeleteView.as_view()),
    path('detailed-task/<pk>/', views.GenericDetailView.as_view()),
    path("complete_task/<pk>/", views.GenericTaskCompleteView.as_view()),
    path("completed_tasks/", views.GenericCompletedTasksView.as_view()),
    path("all_tasks/", views.GenericAllTasksView.as_view()),
    path("update-task/<pk>/", views.GenericTaskUpdateView.as_view()),
    path('user/signup/', views.UserCreationView.as_view()),
    path('user/login/', views.UserLoginView.as_view()),
    path('user/logout/', LogoutView.as_view())
]