from django.contrib.auth.views import LoginView
from django.contrib.auth import login
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth.models import User  # or your custom User model
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from issues.models import IssuePost
from django.contrib import messages
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views import View
import googlemaps
from django.conf import settings

User = get_user_model()

class DepartmentAdminLoginView(LoginView):
    template_name = 'admin_panel/admin_login.html'
    redirect_authenticated_user = True

    def form_valid(self, form):
        user = form.get_user()

        # Check if user is admin and has department set
        if user.role != 'admin' or not user.department:
            messages.error(self.request, "You are not authorized to access the admin dashboard.")
            return redirect('admin_panel:admin_login')

        login(self.request, user)
        # Redirect to their department dashboard
        return redirect(reverse('admin_panel:department_dashboard', kwargs={'department': user.department}))




# Mixin to check user role and department
def admin_department_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('admin_panel:admin_login')
        if request.user.role != 'admin':
            messages.error(request, "You must be an admin to access this page.")
            return redirect('admin_panel:admin_login')
        if request.user.department != kwargs.get('department'):
            messages.error(request, "You do not have permission to view this department.")
            return redirect('admin_panel:admin_login')
        return view_func(request, *args, **kwargs)
    return wrapper


@login_required
@admin_department_required
def department_dashboard(request, department):
    issues = IssuePost.objects.filter(department=department).order_by('-created_at')
    context = {
        'issues': issues,
        'department': department,
    }
    return render(request, 'admin_panel/dashboard.html', context)


@login_required
@admin_department_required
def issue_detail(request, department, issue_id):
    issue = get_object_or_404(IssuePost, id=issue_id, department=department)

    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in dict(IssuePost.STATUS_CHOICES):
            issue.status = new_status
            issue.save()
            messages.success(request, "Issue status updated.")
            return redirect(reverse('admin_panel:issue_detail', args=[department, issue_id]))

    context = {
        'issue': issue,
        'department': department,
        'status_choices': IssuePost.STATUS_CHOICES,
    }
    return render(request, 'admin_panel/issue_detail.html', context)

from django.contrib.auth import logout

@login_required
def admin_logout(request):
    logout(request)
    return redirect('admin_panel:admin_login')


class MapView(View): 
    template_name = "admin_panel/map.html"

    def get(self,request): 
        key = settings.GOOGLE_API_KEY
        issues = IssuePost.objects.filter(reported_latitude__isnull=False, location_name__isnull=False)
        locations = []

        for a in issues:
            data = {
                'lat': float(a.reported_latitude), 
                'lng': float(a.reported_longitude), 
                'name': a.location_name,
                'image':a.image.url,
                'description': a.description,
            }
            locations.append(data)
        print(locations)
        context = {
            "key":key, 
            "locations": locations
        }

        return render(request, self.template_name, context)


class MapView(View): 
    template_name = "admin_panel/map.html"

    def get(self,request): 
        key = settings.GOOGLE_API_KEY
        issues = IssuePost.objects.filter(reported_latitude__isnull=False, location_name__isnull=False)
        locations = []

        for a in issues:
            data = {
                'lat': float(a.reported_latitude), 
                'lng': float(a.reported_longitude), 
                'name': a.location_name,
                'image':a.image.url,
                'description': a.description,
            }
            locations.append(data)
        print(locations)
        context = {
            "key":key, 
            "locations": locations
        }

        return render(request, self.template_name, context)