from django import forms
from .models import Task, Board, List, SprintParticipation

class TaskForm(forms.ModelForm):
    list = forms.ModelChoiceField(queryset=List.objects.all().order_by('order'), empty_label="---------", required=False)

    class Meta:
        model = Task
        fields = ['title', 'description', 'list', 'assignee', 'priority', 'status','tag', 'points', 'completion_date', 'hours_spent', 'expected_hours']
        widgets = {
            'completion_date': forms.widgets.DateInput(attrs={'type': 'date'})
        }
   
class BoardForm(forms.ModelForm):
    def __init__(self,*args,**kwargs):
        self.is_edit = kwargs.pop('is_edit')
        super(BoardForm,self).__init__(*args,**kwargs)
        if self.is_edit:
            self.fields['start_date'].disabled = True
            self.fields['end_date'].disabled = True
        
    class Meta:
        model = Board
        fields = ['title', 'start_date', 'end_date']
        widgets = {
            'end_date': forms.widgets.DateInput(attrs={'type': 'date'}),
            'start_date': forms.widgets.DateInput(attrs={'type': 'date'})
        }

    def clean(self):
        # Source: https://stackoverflow.com/a/7356307
        cleaned_data = super().clean()
        start_date = cleaned_data.get("start_date")
        end_date = cleaned_data.get("end_date")

        # get earliest task completion date
        # earliest_task_completion_date = Task.objects.all().order_by('end_date').first().end_date

        if end_date < start_date:
            raise forms.ValidationError("End date should be greater than start date.")
        
        if self.is_edit and start_date > self.instance.start_date:
            raise forms.ValidationError("Start date cannot be moved to a later date")
        
        if self.is_edit and end_date < self.instance.end_date:
            raise forms.ValidationError("End date cannot be moved to an earlier date")
    

class ListForm(forms.ModelForm):
    class Meta:
        model = List
        fields = ['title', 'board', 'order']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['order'].disabled = True
