from tasks.models import Task
from rest_framework.serializers import ModelSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend, FilterSet, CharFilter, ChoiceFilter
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

    def perform_create(self, serializer):
        serializer.save(user = self.request.user)