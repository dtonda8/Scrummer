from django.contrib.auth.decorators import login_required
from .models import Board, Task, List, User, SprintParticipation
from django.shortcuts import render, redirect, get_object_or_404
from .forms import TaskForm, BoardForm, ListForm
import json
from django.utils import timezone
from .filters import TaskFilter
import datetime



@login_required(login_url="/login/")
def index(request):
    """View function for home page of site."""
    boards = Board.objects.all()
    tasks = Task.objects.filter(list=None)

    board_stats = {}

    for board in boards:
        lists = List.objects.filter(board=board)

        num_tasks_todo = 0
        num_tasks_doing = 0
        num_tasks_done = 0

        for list in lists:
            num_tasks_todo += Task.objects.filter(list=list, status='NS').count()
            num_tasks_doing += Task.objects.filter(list=list, status='IP').count()
            num_tasks_done += Task.objects.filter(list=list, status='CP').count()
        
        board_stats.update({board.id: {
            'amount_of_tasks': num_tasks_todo + num_tasks_doing + num_tasks_done,
            'amount_of_tasks_todo': num_tasks_todo,
            'amount_of_tasks_doing': num_tasks_doing,
            'amount_of_tasks_done': num_tasks_done,
            'amount_of_lists': len(lists),
        }})
        
    context = {"boards": boards, "tasks": tasks, "board_stats": board_stats}

    return render(request, "kanban/index.html", context)

@login_required(login_url="/login/")
def single_board(request, board_id, view_mode=None):
    lists = List.objects.filter(board=board_id)
    tasks = Task.objects.all()
    board = Board.objects.get(pk=board_id)

    taskFilter = TaskFilter(request.GET, queryset=tasks)
    tasks = taskFilter.qs
    # group tasks by lists
    list_to_task = {l: sorted(tasks.filter(list=l), key=lambda t: t.time_moved, reverse=False) for l in lists}

    vm = view_mode
    if view_mode is None:
        vm = 'kanban'
    

    product_backlog = tasks.filter(list=None)
    
    context = {'list_to_task': list_to_task, 'board': board, 'taskFilter': taskFilter, 'view_mode': vm, 'product_backlog': product_backlog}

    return render(request, "kanban/single_board.html", context)

@login_required(login_url="/login/")
def create_board(request):
    if request.method == "POST":
        form = BoardForm(request.POST, is_edit=False)
        if form.is_valid():
            form.save()
            create_sprint_participation()
            return redirect('index')
    else:
        form = BoardForm(is_edit=False)
    return render(request, 'kanban/board_form.html', {'form': form, 'new': True})

@login_required(login_url="/login/")
def edit_board(request, board_id):
    board = get_object_or_404(Board, pk=board_id)
    if request.method == "POST":
        form = BoardForm(request.POST, instance=board, is_edit=True)
        if form.is_valid():
            form.save()
            return redirect('single_board', board_id=board_id)
    else:
        form = BoardForm(instance=board, is_edit=True)
       
    return render(request, 'kanban/board_form.html', {'form': form, 'new': False, 'board': board})

@login_required(login_url="/login/")
def delete_board(request, board_id):
    board = get_object_or_404(Board, pk=board_id)
    if request.method == "POST":
        board.delete()
        return redirect('index')
    return render(request, 'kanban/delete_board.html', {'board': board})

@login_required(login_url="/login/")
def create_list(request, board_id):
    board = get_object_or_404(Board, pk=board_id)
    order = get_next_order(board)
    
    if request.method == "POST":
        form = ListForm(request.POST, initial={'current_board': board, 'order': order})
        if form.is_valid():
            list_instance = form.save(commit=False)
            list_instance.board = board
            list_instance.save()
            return redirect('single_board', board_id=board_id)
    else:
        form = ListForm(initial={'current_board': board, 'order': order})

    context = {'form': form, 'new': True, 'board_id': board_id}
    return render(request, 'kanban/list_form.html', context)

@login_required(login_url="/login/")
def edit_list(request, board_id, list_id):
    board = get_object_or_404(Board, pk=board_id)
    list_instance = get_object_or_404(List, pk=list_id)

    if request.method == "POST":
        form = ListForm(request.POST, instance=list_instance)
        if form.is_valid():
            list_instance = form.save(commit=False)
            list_instance.board = board
            list_instance.save()
            return redirect('single_board', board_id=board_id)
    else:
        form = ListForm(instance=list_instance)

    return render(request, 'kanban/list_form.html', {'form': form, 'new': False, 'board_id': board_id, 'list_id': list_id})

@login_required(login_url="/login/")
def delete_list(request, board_id, list_id):
    list_instance = get_object_or_404(List, pk=list_id)

    if request.method == "POST":
        board_id = list_instance.board.id
        list_instance.delete()
        return redirect('single_board', board_id=board_id)

    return render(request, 'kanban/delete_list.html', {'list': list_instance, 'board_id': board_id})

@login_required(login_url="/login/")
def task(request, task_id):
    task = Task.objects.get(pk=task_id)
    context = {"task": task}
    return render(request, "kanban/task.html", context)

@login_required(login_url="/login/")
def create_task(request, board_id=None):
    if request.method == "POST":
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.board_id = board_id
            task.save()
            
            if board_id is None:
                return redirect('index')
            return redirect('single_board', board_id=board_id)
        
    else:
        form = TaskForm()
        form.fields['list'].choices = get_list_form_field()

    return render(request, 'kanban/task_form.html', {'form': form, 'new': True, 'board_id': board_id})

@login_required(login_url="/login/")
def edit_task(request, task_id):
    task = get_object_or_404(Task, pk=task_id)
    if request.method == "POST":
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            form.save()
            if task.list:
                board_id = task.list.board.id
                return redirect('single_board', board_id=board_id)
            return redirect('index')
    else:
        form = TaskForm(instance=task)
        form.fields['list'].choices = get_list_form_field()
        
    return render(request, 'kanban/task_form.html', {'form': form, 'new': False, 'task': task})

@login_required(login_url="/login/")
def delete_task(request, task_id):
    task = get_object_or_404(Task, pk=task_id)
    if request.method == "POST":
        if task.list:
            board_id = task.list.board.id
            task.delete()
            return redirect('single_board', board_id=board_id)
        return redirect('index')
    return render(request, 'kanban/delete_task.html', {'task': task})

def update_task_list(request, task_id):
    if request.method == "POST":
        requestBody = json.loads(request.body)
        listID = requestBody.get("listID")
        task = get_object_or_404(Task, pk=task_id)
        list = None

        if (listID != None):
            list = List.objects.get(pk=listID)
            # update board date range 
            if task.completion_date is not None:
                board = list.board
                completion_date = datetime.date(task.completion_date.year, task.completion_date.month, task.completion_date.day)

                if board.start_date > completion_date:
                    board.start_date = completion_date
                if board.end_date < completion_date:
                    board.end_date = completion_date
                board.save()

        task.list = list
        task.time_moved = timezone.now()
        task.save()

    return redirect("index")

def sort(request, board_id):
    list_ids = request.POST.getlist('list_order')
    lst = [] 
    for idx, list_id in enumerate(list_ids, start=1):
        lst = List.objects.get(pk=list_id)
        lst.order = idx
        lst.save()

    lists = List.objects.filter(board=board_id)
    tasks = Task.objects.all()
    board = Board.objects.get(pk=board_id)

    taskFilter = TaskFilter(request.GET, queryset=tasks)
    tasks = taskFilter.qs
    list_to_task = {l: sorted(tasks.filter(list=l), key=lambda t: t.time_moved, reverse=False) for l in lists}
    context = {'list_to_task': list_to_task, 'board': board}

    return render(request, "kanban/board_lists.html", context)

@login_required(login_url="/login/")
def update_progress(request):
    sprint_participation = SprintParticipation.objects.filter(user=request.user)
    if request.method == 'POST':
        # Get user and sprints from sprint participation
        for sp in sprint_participation:
            daily_progress = sp.daily_progress

            # Get daily progress from form
            for day_num in daily_progress:
                progress_value = request.POST.get(f"daily_progress_{ day_num }_{ sp.sprint.id }")
                sp.set_progress_for_day(day_num, progress_value)
            sp.save()
            
        return redirect('index')  # Redirect to a success page after saving the form
    else:
        create_sprint_participation()

    # get sprint participation for current user
    return render(request, 'kanban/update_progress.html', {'sprint_participation': sprint_participation})

# Other key functions: 
def get_next_order(board):
    board_lists = List.objects.filter(board=board)
    if board_lists:
        return board_lists.latest('order').order + 1
    return 1 # first in board

def get_list_form_field():
    list_form_field = []
    list_form_field.append((None, "None"))

    for board in Board.objects.all().order_by('id'):
        list_form_field.append(
            (board.title,
            [
                (list.id, list.title) for list in List.objects.filter(board=board).order_by('id')
            ])
        )
    return list_form_field


def create_sprint_participation():
    """
    Creates sprint participation models for all users and sprints.
    This should be called whenever a user/sprint is created. And when the user accesses the update_progress page.
    """
    for user in User.objects.all():
        for sprint in Board.objects.all():
            # check if sprint participation already exists
            if not SprintParticipation.objects.filter(user=user, sprint=sprint).exists():
                sprint_participation = SprintParticipation(user=user, sprint=sprint, daily_progress=create_daily_progress_dict(sprint))
                sprint_participation.save()


def create_daily_progress_dict(sprint):
    daily_progress_dict = {}
    num_days = (sprint.end_date - sprint.start_date).days + 1
    for day_num in range(1, num_days + 1):
        daily_progress_dict[day_num] = 0
    return daily_progress_dict


def velocity_chart(request):
    """
    Creates a velocity chart, showing commited vs completed tasks for each of the 5 most recently completed sprints, in chronological order.
    """
    current_date = datetime.date.today()

    sprints = Board.objects.filter(end_date__lte=current_date).order_by('end_date')[:5]

    sprint_data = [
        {
            'sprint_title': sprint.title,
            'total_tasks': Task.objects.filter(list__board=sprint).count(),
            'completed_tasks': Task.objects.filter(list__board=sprint, status=Task.Status.COMPLETED).count(),
        }
       
        for sprint in sprints
    ]

    context = {
        'sprint_data': json.dumps(sprint_data),
    }

    return render(request, 'kanban/velocity_chart.html', context)









"""""
def index(request):
    """#View function for home page of site.
"""
    # Redirect user to login page if they haven't logged in yet
    if not request.user.is_authenticated:
        return redirect("login/")

    boards = Board.objects.all()
    tasks = Task.objects.all()

    # group tasks by boards
    board_to_task = {b: sorted(tasks.filter(board=b), key=lambda t: t.time_moved, reverse=False) for b in boards}

    context = {"board_to_task": board_to_task}

    return render(request, "kanban/index.html", context)


@login_required(login_url="/login/")
def task(request, task_id):
    task = Task.objects.get(pk=task_id)
    context = {"task": task}
    return render(request, "kanban/task.html", context)

@login_required(login_url="/login/")
def create_task(request):
    if request.method == "POST":
        form = TaskForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('index')
    else:
        form = TaskForm()
    return render(request, 'kanban/create_task.html', {'form': form})

@login_required(login_url="/login/")
def edit_task(request, task_id):
    task = get_object_or_404(Task, pk=task_id)
    if request.method == "POST":
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            form.save()
            return redirect('index')
    else:
        form = TaskForm(instance=task)
    return render(request, 'kanban/edit_task.html', {'form': form})

@login_required(login_url="/login/")
def delete_task(request, task_id):
    task = get_object_or_404(Task, pk=task_id)
    if request.method == "POST":
        task.delete()
        return redirect('index')
    return render(request, 'kanban/delete_task.html', {'task': task})

def update_task_board(request, task_id):
    if request.method == "POST":
        
        requestBody = json.loads(request.body)

        boardName = requestBody.get("boardName")

        task = get_object_or_404(Task, pk=task_id)
        board = Board.objects.get(title=boardName)
        task.board = board
        task.time_moved = timezone.now()
        task.save()

    return redirect("index")

#</form> class="form__container">
"""""