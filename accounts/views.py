import datetime
from django.shortcuts import render, redirect
from .forms import UserRegisterForm
from django.contrib import messages
from django.contrib.auth import login
from django.urls import reverse_lazy
from django.contrib.auth.views import PasswordResetView
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.decorators import login_required, user_passes_test
from kanban.models import SprintParticipation, Board, Task, List, User
from .filters import SprintFilter
import json
import math


def register(request):
    if request.method == "POST":
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("/")
        messages.error(request, "Error, please try again")
    form = UserRegisterForm()
    context = {"form": form}
    return render(request, "accounts/register.html", context)


class ResetPasswordView(SuccessMessageMixin, PasswordResetView):
    template_name = 'accounts/password_reset.html'
    email_template_name = 'accounts/password_reset_email.html'
    subject_template_name = 'accounts/password_reset_subject.txt'
    success_url = reverse_lazy('password_reset_done')

def user_in_admin_group(user):
    return user.groups.filter(name="ADMIN").exists()


@login_required(login_url="/login/")
@user_passes_test(user_in_admin_group, login_url="/")
def team_stats(request):
    user_to_time_spent = {} # {user.id: sprint_}, where daily progress is a dict of {day_num: time_spent}

    sprint_participation = SprintParticipation.objects.all()
    sprint_filter = SprintFilter(request.GET, queryset=sprint_participation)
    sprint_contribs = sprint_filter.qs
    
    selected_sprint = request.GET.get('sprint')
    week_number = request.GET.get('week_number')
    form_error = ""

    title = "Team Statistics"
    total_num_days = 0
    sprints_seen = set()

    for sc in sprint_contribs:
        username = sc.user.username
        dp = sc.daily_progress
        time_spent = 0
        for time in dp.values():
            time_spent += int(time)

        if sc.sprint not in sprints_seen:
            sprints_seen.add(sc.sprint)
            total_num_days += len(dp.keys())

        user_to_time_spent[username] = user_to_time_spent.get(username, 0) + time_spent
    
    average = 0 
    num_users = 0
    # Calculate daily averages and total average
    for user in user_to_time_spent.keys():
        user_to_time_spent[user] = user_to_time_spent[user] / total_num_days
        average += user_to_time_spent[user]
        num_users += 1

    average = average / num_users
    entire_team_average = average

    if selected_sprint is not None and len(selected_sprint) == 0 and week_number is not None and len(week_number) > 0:
        form_error = "Cannot select week number without selecting a sprint first"
    
    elif week_number and len(week_number) > 0: # sprint selected:
        average = 0
        title = "Team Sprint Statistics for Week " + week_number
        week_number = int(week_number)
        start_day =  (week_number - 1) * 7 + 1
        last_day = start_day

        for sc in sprint_contribs:
            username = sc.user.username
            dp = sc.daily_progress
            if str(start_day) not in dp.keys():
                form_error = "Week number selected is out of range for sprint " + sc.sprint.title
                break
            time_spent = 0
            for day in range(start_day, start_day + 7):
                if str(day) in dp.keys():
                    time_spent += int(dp.get(str(day), 0))
                else:
                    last_day = day - 1
                    break

            user_to_time_spent[username] = time_spent / (last_day - start_day + 1)
            average += user_to_time_spent[username]
        
        average = average / len(user_to_time_spent.keys())

    sprint_id = request.GET.get('sprint')
    day_to_story_points_actual = {}
    day_to_story_points_ideal = {}
    burndown_title = "Sprint Burndown Chart"
    burndown_form_error = ''
    
    if sprint_id and len(sprint_id) > 0:
        sprint = Board.objects.get(pk=sprint_id)
        burndown_title = "Sprint Burndown Chart for " + sprint.title
        # Get corresponding lists
        lists = List.objects.filter(board=sprint)
        total_story_points = 0
        for lst in lists:
            for task in Task.objects.filter(list=lst):
                if task.points.isnumeric():
                    total_story_points += int(task.points)

        print(total_story_points)
                ### Burn down 
        # Strategy: get total number of story points for sprint
        # print(type(sprint.start_date))
        # completion_date = datetime.date(task.completion_date.year, task.completion_date.month, task.completion_date.day)
        total_days = (sprint.end_date - sprint.start_date).days + 1
        day_to_story_points_ideal = {day: round(total_story_points * (total_days - day) / total_days) for day in range(1, total_days + 1)}
        day_to_story_points_ideal[1] = total_story_points
        day_to_story_points_ideal[total_days] = 0
        day_to_story_points_actual = {day: total_story_points for day in range(1, total_days + 1)}
        
        # Get corresponding lists
        lists = List.objects.filter(board=sprint)
        for lst in lists:
            for task in Task.objects.filter(list=lst):
                # get date of task completion
                if task.completion_date is not None:
                    task_completion_date = datetime.date(task.completion_date.year, task.completion_date.month, task.completion_date.day)

                    if task_completion_date < sprint.start_date:
                        completion_day = 1
                    else:
                        completion_day = (task_completion_date - sprint.start_date).days + 1

                    # Update story points completed for each day after completion date
                    if task.points.isnumeric():
                        for day in range(completion_day, total_days + 1):
                            day_to_story_points_actual[day] = max(0, day_to_story_points_actual[day] - int(task.points))
    
    else:
        burndown_form_error = "To view burndown chart, select a sprint"

    user_id = request.GET.get('user')
    if user_id and len(user_id) > 0:
        user = User.objects.get(pk=user_id)
        title = "Team Statistics for " + user.username

    # Calculate the three requested variables
    total_time_spent = sum(user_to_time_spent.values())
    total_num_days = 0
    sprints_seen = set()

    for sc in sprint_contribs:
        if sc.sprint not in sprints_seen:
            sprints_seen.add(sc.sprint)
            total_num_days += len(sc.daily_progress.keys())

    average_time_per_day_per_member = round(total_time_spent / total_num_days,2)
    num_users = len(user_to_time_spent)
    entire_team_average = round(total_time_spent / num_users,2)

    context = {
        'sprint_filter': sprint_filter, 
        'time_spent_data': json.dumps(user_to_time_spent),
        'title': title,
        'axisX_title': "User",
        'axisY_title': "Daily Average Time Spent (hours)",
        'stripLines': json.dumps({'value': average, 'label': "Average"}),
        'form_error': form_error,
        'day_to_story_points_ideal': json.dumps(day_to_story_points_ideal),
        'day_to_story_points_actual': json.dumps(day_to_story_points_actual),
        'burndown_title': burndown_title,
        'burndown_form_error': burndown_form_error,
        'entire_team_average': entire_team_average,
        'average_time_per_day_per_member': average_time_per_day_per_member,
    }
    
    return render(request, 'team_stats.html', context=context)