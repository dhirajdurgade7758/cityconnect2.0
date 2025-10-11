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
from django.urls import reverse
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import user_passes_test
from django.utils import timezone
from .forms import *
import requests
import logging
from store.models import StoreOffer

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
                'id': a.id,
                'name': a.location_name,
                'image':a.image.url,
                'description': a.description,
                'status':a.status,
                'url': reverse('feed'),
                'resolve_url': reverse('resolve_issue', args=[a.id]),
                'department':a.department,
            }
            locations.append(data)
        print(locations)
        context = {
            "key":key, 
            "locations": locations
        }

        return render(request, self.template_name, context)
    



def is_admin(user):
    return user.is_staff or user.is_superuser

@user_passes_test(is_admin)
def issue_list(request):
    status_filter = request.GET.get('status')
    if status_filter:
        issues = IssuePost.objects.filter(status=status_filter)
    else:
        issues = IssuePost.objects.all()
    return render(request, 'admin_panel/issue_list.html', {'issues': issues})

NODE_API_URL = "http://localhost:3000" 
logger = logging.getLogger(__name__)

@user_passes_test(is_admin)
def resolve_issue(request, id):
    issue = get_object_or_404(IssuePost, id=id)
    if request.method == 'POST':
        form = ResolveIssueForm(request.POST, request.FILES, instance=issue)
        if form.is_valid():
            issue = form.save(commit=False)

            if issue.status == 'resolved':
                issue.resolved_at = timezone.now()
                issue.resolved_by = request.user
                
                user = issue.user # Get the user who reported the issue

                # --- Blockchain Integration Starts Here ---
                try:
                    # 1. Create the reward payload for the API call
                    reward_payload = {
                        'userId': user.username,
                        'amount': 50, # The reward for a resolved issue
                        'reason': f"For reporting and resolving issue ID: {issue.id}"
                    }

                    # 2. Call the blockchain reward endpoint
                    reward_response = requests.post(
                        f"{NODE_API_URL}/api/system/reward",
                        json=reward_payload,
                        timeout=5
                    )
                    reward_response.raise_for_status() # Raise an exception for bad status codes

                    reward_data = reward_response.json()
                    blockchain_user_data = reward_data.get('user')

                    # 3. Update Django DB with the new balance from the blockchain
                    if blockchain_user_data and 'balance' in blockchain_user_data:
                        user.eco_coins = blockchain_user_data['balance']
                        user.save()
                        messages.success(request, f"Successfully awarded 50 EcoCoins to {user.username} via blockchain.")
                    else:
                        messages.error(request, "API call succeeded but returned unexpected data.")

                except requests.exceptions.RequestException as e:
                    logger.error(f"Could not award EcoCoins to {user.username} for issue {issue.id}. Error: {e}")
                    messages.warning(request, f"Issue resolved, but FAILED to award EcoCoins to {user.username}. Please sync manually.")
                # --- Blockchain Integration Ends ---

            else: # If status is changed from 'resolved' to something else
                issue.resolved_at = None
                issue.resolved_by = None
            
            issue.save() # Save the issue object itself
            return redirect('issue_list')
    else:
        form = ResolveIssueForm(instance=issue)
    return render(request, 'admin_panel/resolve_issue.html', {'form': form, 'issue': issue})




# --- Add these for blockchain integration ---
NODE_API_URL = "http://localhost:3000" # Use the correct URL for the Node server
logger = logging.getLogger(__name__)
# ---

def is_admin(user):
    return user.is_authenticated and user.role == 'admin'

@user_passes_test(is_admin)
def create_store_offer(request):
    if request.method == 'POST':
        form = StoreOfferForm(request.POST, request.FILES)
        if form.is_valid():
            # First, save the offer to the Django database
            offer = form.save(commit=False)
            offer.added_by = request.user # Assign the admin who is adding the offer
            offer.save()

            # --- Blockchain Integration Starts Here ---
            try:
                # 1. Prepare the payload for the blockchain API
                # The field names must match what the API expects: name, cost, quantity
                payload = {
                    'name': offer.name,
                    'cost': offer.coins_required,
                    'quantity': offer.stock
                }
                
                # 2. Make the POST request to the Node.js server
                response = requests.post(
                    f"{NODE_API_URL}/api/store/items",
                    json=payload,
                    timeout=5
                )
                response.raise_for_status() # Check for any HTTP errors
                
                messages.success(request, f"Offer '{offer.name}' was created and successfully synced with the blockchain store.")

            except requests.exceptions.RequestException as e:
                logger.error(f"Failed to sync new store offer '{offer.name}' with blockchain. Error: {e}")
                messages.warning(request, f"Offer '{offer.name}' was created in Django, but FAILED to sync with the blockchain. Please add it manually.")
            # --- Blockchain Integration Ends ---

            return redirect('store_offer_list') # Redirect to a list of offers
    else:
        form = StoreOfferForm()
    
    return render(request, 'admin_panel/create_offer_template.html', {'form': form})


@login_required
def store_offer_list(request):
    offers = StoreOffer.objects.all()
    return render(request, 'admin_panel/store_offer_list.html', {'offers': offers})