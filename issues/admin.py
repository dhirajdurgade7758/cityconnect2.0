from django.contrib import admin

# Register your models here.
from .models import IssuePost, Task, Comment
admin.site.register(IssuePost)
admin.site.register(Task)
admin.site.register(Comment)