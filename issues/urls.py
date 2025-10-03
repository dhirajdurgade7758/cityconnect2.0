from django.urls import path, include
from . import views

urlpatterns = [

    path('post/create/', views.create_issue_post, name='create_issue_post'),  # Renamed for clarity
    path('feed/', views.feed, name='feed'),
    path('post/<int:post_id>/', views.post_detail, name='post_detail'),
    path('post/<int:post_id>/like/', views.toggle_like, name='toggle_like'),
    path('post/<int:post_id>/update-status/', views.update_post_status, name='update_post_status'),
    path('post/<int:post_id>/comments/', views.post_comments, name='post_comments'),
    path('post/<int:post_id>/comments/form/', views.comment_form, name='comment_form'),
    path('saved/', views.saved_posts_view, name='saved_posts'),
    path('post/<int:post_id>/save/', views.toggle_save_post, name='toggle_save_post'),
    path('verify-task/<int:task_id>/', views.verify_task, name='verify_task'),  # Admin/internal use
    path('tasks/', views.tasks, name='tasks'),
]