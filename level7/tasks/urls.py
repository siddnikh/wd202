from django.urls import path
from . import views
from django.contrib.auth.views import LogoutView
from django.views.generic import RedirectView
from tasks.apiviews import TaskViewSet, HistoryViewSet
from rest_framework.routers import SimpleRouter

router = SimpleRouter()
router.register('api/task', TaskViewSet)
router.register('api/history', HistoryViewSet)

urlpatterns = [
    path('', RedirectView.as_view(url='/tasks')),
    path("tasks/", views.GenericTaskView.as_view()),
    path('create-task/', views.GenericTaskCreateView.as_view()),
    path("delete-task/<pk>/", views.GenericTaskDeleteView.as_view()),
    path("completed_tasks/", views.GenericCompletedTasksView.as_view()),
    path("all_tasks/", views.GenericAllTasksView.as_view()),
    path("update-task/<pk>/", views.GenericTaskUpdateView.as_view()),
    path('user/signup/', views.UserCreationView.as_view()),
    path('user/login/', views.UserLoginView.as_view()),
    path('user/logout/', LogoutView.as_view())
] + router.urls