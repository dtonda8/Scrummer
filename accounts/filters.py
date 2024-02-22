import django_filters
from django import forms
from kanban.models import *


class SprintFilter(django_filters.FilterSet):
    class Meta:
        model = SprintParticipation
        fields = ['user', 'sprint']


