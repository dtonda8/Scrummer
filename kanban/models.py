from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
import datetime

class Board(models.Model):
    title = models.CharField(max_length=100)
    start_date = models.DateField(default=datetime.date.today)
    one_week_later = datetime.date.today() + datetime.timedelta(days=7)
    end_date = models.DateField(default=one_week_later)

    def __str__(self):
        return self.title

    @property
    def is_before_start_date(self):
        return datetime.date.today() < self.start_date
    
    @property
    def is_after_end_date(self):
        return datetime.date.today() > self.end_date
    
    @property
    def is_active(self):
        return not self.is_before_start_date and not self.is_after_end_date

class SprintParticipation(models.Model):
    sprint = models.ForeignKey(Board, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    daily_progress = models.JSONField(default=dict)  
    """
    Format of daily_progress
    {int: int}
    {day_num: progress_value}

    e.g. {1: 10, 2: 3} means that the user worked 10 hours in day 1 and 3 hours in day 2 
    day_num is measured from the start date of the sprint(board)
    To get users sprint progress for a particular sprint (Board), use SprintParticipation.objects.get(sprint=board_in_question, user=user_in_question)
    use daily_progress.get(day_num, 0) to get the progress value for a particular day
    """

    class Meta:
        unique_together = ('sprint', 'user')

    def set_progress_for_day(self, day_num, progress_value):
        self.daily_progress[day_num] = progress_value

    def get_progress_for_day(self, day_num):
        return self.daily_progress.get(day_num, 0)


class List(models.Model):
    title = models.CharField(max_length=100)
    board = models.ForeignKey(Board, on_delete=models.CASCADE, null=True, blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']
        
    def __str__(self):
        return self.title
    
class Task(models.Model):
    class Priority(models.TextChoices):
        LOW = "LW", ("Low")
        MEDIUM = "MD", ("Medium")
        IMPORTANT = "IP", ("Important")
        URGENT = "UR", ("Urgent")
        IMPORTANT_URGENT = "IU", ("Important & Urgent")

    class Status(models.TextChoices):
        NOT_STARTED = "NS", ("Not Started")
        IN_PROGRESS = "IP", ("In Progress")
        COMPLETED = "CP", ("Completed")
        
    class Tag(models.TextChoices):
        NONE = "None", ('None')
        FRONT_END = "FE", ("Frontend")
        BACK_END = "BE", ("Backend")
        API = "API", ("API")
        DATABASE = "DB", ("Database")
        FRAMEWORK = "FR",("Framework")
        TESTING = "T", ("Testing")
        UI_UX = "UIUX", ('UI/UX')
    class Points(models.TextChoices):
        NONE = "None", ('None')
        ONE = "1",("1")
        TWO = "2", ("2")
        THREE = "3",("3")
        FOUR = "4",("4")
        FIVE = "5",("5")
        SIX = "6", ("6")
        SEVEN = "7",("7")
        EIGHT = "8",("8")
        NINE = "9",("9")
        TEN = "10",("10")


    title = models.CharField(max_length=100)
    description = models.CharField(max_length=500)
    list = models.ForeignKey(List, on_delete=models.CASCADE, null=True, blank=True)
    assignee = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    priority = models.CharField(max_length=2, choices=Priority.choices, default=Priority.MEDIUM)
    status = models.CharField(max_length=2, choices=Status.choices, default=Status.NOT_STARTED)
    tag = models.CharField(max_length=4, choices=Tag.choices, default=Tag.NONE)
    points = models.CharField(max_length=4, choices=Points.choices, default=Points.NONE)

    time_moved = models.DateTimeField(auto_now=True)
    completion_date = models.DateTimeField(null=True, blank=True)
    hours_spent = models.IntegerField(default=0)
    expected_hours = models.IntegerField(default=0)

    def __str__(self):
        return self.title