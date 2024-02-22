import django_filters
from django import forms
from .models import *

PRIORITY = (
    ('LW', 'Low'),
    ('MD', 'Medium'),
    ('IP', 'Important'),
    ('UR', 'Urgent'),
    ('IU', 'Important & Urgent'),
)

class TaskFilter(django_filters.FilterSet):
    priority = django_filters.MultipleChoiceFilter(field_name='priority', choices=PRIORITY, widget=forms.CheckboxSelectMultiple())
    class Meta:
        model = Task
        fields = ['list', 'priority', 'status', 'assignee']


