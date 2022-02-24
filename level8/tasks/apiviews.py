from tasks.models import Task, History
from rest_framework.serializers import ModelSerializer, SlugRelatedField
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend, FilterSet, CharFilter, ChoiceFilter, DateTimeFilter
from .models import STATUS_CHOICES

class TaskFilter(FilterSet):
    title = CharFilter(lookup_expr="icontains")
    status = ChoiceFilter(choices = STATUS_CHOICES)

class TaskSerializer(ModelSerializer):
    class Meta:
        model = Task
        fields = ['title', 'completed', 'status', 'priority']

class TaskViewSet(ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer

    permission_classes = (IsAuthenticated,)

    filter_backends = (DjangoFilterBackend, )
    filterset_class = TaskFilter

    def get_queryset(self):
        return Task.objects.filter(user = self.request.user, deleted = False)

class HistoryFilter(FilterSet):
    status = ChoiceFilter(field_name = 'new_status', choices = STATUS_CHOICES)
    start_date = DateTimeFilter(field_name='date_of_update', lookup_expr='gte')
    end_date = DateTimeFilter(field_name='date_of_update', lookup_expr='lte')

class HistorySerializer(ModelSerializer):

    task = SlugRelatedField(slug_field='title', read_only=True)

    class Meta:
        model = History
        fields = ['task', 'old_status', 'new_status', 'date_of_update']

class HistoryViewSet(ReadOnlyModelViewSet):
    queryset = None
    serializer_class = HistorySerializer
    permission_classes = (IsAuthenticated,)
    filter_backends = (DjangoFilterBackend, )
    filterset_class = HistoryFilter

    def get_queryset(self):
        return History.objects.filter(task__user = self.request.user, task=self.kwargs['task_pk'])