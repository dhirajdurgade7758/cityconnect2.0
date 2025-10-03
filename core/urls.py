from django.urls import path, include
from . import views
from .groq_chat import chat_api

urlpatterns = [
    path('', views.dashboard, name='home'),
    path('news/', views.news_view, name='news'),
    # New URL for news modal
    path('news/<int:news_id>/modal/', views.news_detail_modal, name='news_detail_modal'),
    path('profile/', views.profile, name='profile'),
    path('leaderboard/', views.leaderboard, name='leaderboard'),
    path('api/chat/', chat_api, name='chat_api'),
    
]

# User authentication URLs
urlpatterns += [
    path('register/', views.user_register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
]
