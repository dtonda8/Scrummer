from django.contrib import admin

from .models import List, Task, Board

admin.site.register(List)
admin.site.register(Task)
admin.site.register(Board)
