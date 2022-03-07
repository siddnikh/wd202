from django.urls import path, include
from . import views
from django.contrib.auth.views import LogoutView
from django.views.generic import RedirectView
from tasks.apiviews import TaskViewSet, HistoryViewSet
from rest_framework_nested.routers import SimpleRouter, NestedSimpleRouter

router = SimpleRouter()
router.register(r'task', TaskViewSet)
#router.register('api/history', HistoryViewSet, basename="babushla")

task_router = NestedSimpleRouter(router, r'task', lookup='task')
task_router.register(r'history', HistoryViewSet, basename='task-history')

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
    path('user/logout/', LogoutView.as_view()),
    path(r'', include(router.urls)),
    path(r'', include(task_router.urls)),
    path('user/configure/', views.ReportConfigureView.as_view())
]