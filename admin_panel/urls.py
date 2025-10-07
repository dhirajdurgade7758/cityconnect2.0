from django.urls import path
from . import views


urlpatterns = [
    path('login/', views.DepartmentAdminLoginView.as_view(), name='admin_login'),
    path('logout/', views.admin_logout, name='admin_logout'),

    path('<str:department>/', views.department_dashboard, name='department_dashboard'),
    path('<str:department>/issue/<int:issue_id>/', views.issue_detail, name='issue_detail'),
    path("map", views.MapView.as_view(), name='my_map_view'), 
    path("resolve_issue/<int:id>/", views.resolve_issue, name="resolve_issue"),
    path("issue_list", views.issue_list, name="issue_list"), 
]
