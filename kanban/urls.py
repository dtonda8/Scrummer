from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("sprint/<int:board_id>", views.single_board, name="single_board"),
    path("sprint/<int:board_id>/<str:view_mode>", views.single_board, name="single_board"),
    path("sprint/new/", views.create_board, name="create_board"),
    path("sprint/<int:board_id>/edit/", views.edit_board, name="edit_board"),
    path("sprint/<int:board_id>/delete/", views.delete_board, name="delete_board"),
    path("task/<int:task_id>", views.task, name="task"),   
    path("task/new/", views.create_task, name="create_task"),
    path("sprint/<int:board_id>/task/new/", views.create_task, name="create_task"),
    path("task/<int:task_id>/edit/", views.edit_task, name="edit_task"),
    path("task/<int:task_id>/delete/", views.delete_task, name="delete_task"),
    path("task/update-list/<int:task_id>", views.update_task_list, name="update_task_list"),
    path("sprint/<int:board_id>/list/new/", views.create_list, name="create_list"),
    path('sprint/<int:board_id>/task/new/', views.create_task, name='create_task'),
    path("sprint/<int:board_id>/list/<int:list_id>/edit/", views.edit_list, name="edit_list"),
    path("sprint/<int:board_id>/list/<int:list_id>/delete/", views.delete_list, name="delete_list"),
    path("sort/<int:board_id>", views.sort, name='sort'),
    path("update_progress/", views.update_progress, name='update_progress'),
    path("velocity-chart/", views.velocity_chart, name="velocity_chart"),
]



"""
urlpatterns = [
    path("", views.index, name="index"),
    path("task/<int:task_id>", views.task, name="task"),
    path("task/create/", views.create_task, name="create_task"),
    path("task/<int:task_id>/edit/", views.edit_task, name="edit_task"),
    path("task/<int:task_id>/delete/", views.delete_task, name="delete_task"),
    path("task/update-board/<int:task_id>", views.update_task_board, name="update_task_board"),
    
]
"""