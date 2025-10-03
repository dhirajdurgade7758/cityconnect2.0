from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model, login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.core.paginator import Paginator
from django.core.mail import send_mail
from django.http import JsonResponse
from django.db.models import Q

from cityconnect import settings
from .forms import  UserRegisterForm
from .models import News,  UserBadge
from .utils import get_badge_info, get_user_badges # assuming utils.py contains these functions
from store.models import Redemption # Import Redemption from the store app
from issues.models import IssuePost, Task, Comment
import logging
logger = logging.getLogger(__name__)

def home(request):
    return render(request, 'core/home.html')



@login_required
def news_view(request):
    news_items = News.objects.order_by('-created_at')
    return render(request, 'core/news.html', {'news_items': news_items})

def news_detail_modal(request, news_id):
    """Returns the content for a single news item to be loaded into a modal."""
    news_item = get_object_or_404(News, id=news_id)
    return render(request, 'core/partials/news_detail_modal.html', {'news_item': news_item})

@login_required
def profile(request):
    user = request.user
    issue_posts = IssuePost.objects.filter(user=user)
    tasks = Task.objects.filter(user=user)
    redemptions = Redemption.objects.filter(user=user) # Fetch from store app

    context = {
        'user': user,
        'eco_coins': user.eco_coins,
        'issue_post_count': issue_posts.count(),
        'task_count': tasks.count(),
        'redemption_count': redemptions.count(),
        'recent_issue_posts': issue_posts.order_by('-created_at')[:3],
        'recent_tasks': tasks.order_by('-submitted_at')[:3],
        'recent_redemptions': redemptions.order_by('-redeemed_at')[:3], # Use redeemed_at
    }
    return render(request, 'core/profile.html', context)


@login_required
def leaderboard(request):
    User = get_user_model()
    top_users_raw = User.objects.filter(role='citizen').order_by('-eco_coins')[:10]

    # Attach badge info to each user
    top_users = []
    for user in top_users_raw:
        badge_name, badge_color, badge_emoji = get_badge_info(user.eco_coins)
        top_users.append({
            'user': user,
            'badge_name': badge_name,
            'badge_color': badge_color,
            'badge_emoji': badge_emoji,
        })

    return render(request, 'core/leaderboard.html', {'top_users': top_users})


def user_register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()

            # Send welcome email
            subject = 'Welcome to CityConnect!'
            message = f"Hello {user.username},\n\nWelcome to CityConnect! 🎉\n\nYou can now report civic issues, earn EcoCoins, and make your city better!"
            from_email = settings.DEFAULT_FROM_EMAIL
            recipient_list = [user.email]

            send_mail(subject, message, from_email, recipient_list, fail_silently=True)
            logger.info(f"Welcome email sent to {user.email}")

            login(request, user)
            messages.success(request, "Registration successful! Welcome to CityConnect!")
            return redirect('home')
        else:
            messages.error(request, "Registration failed. Please correct the errors.")
    else:
        form = UserRegisterForm()
    return render(request, 'core/register.html', {'form': form})


def user_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f"Welcome back, {user.username}!")
            return redirect('home')
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()
    return render(request, 'core/login.html', {'form': form})


@login_required
def user_logout(request):
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect('login')



@login_required
def dashboard(request):
    user = request.user

    # Issue Posts
    issue_posts = IssuePost.objects.filter(user=user)
    total_issue_posts = issue_posts.count()
    recent_issue_posts = issue_posts.order_by('-created_at')[:5]

    # Tasks
    tasks = Task.objects.filter(user=user)
    total_tasks = tasks.filter(is_verified=True).count()
    pending_tasks = tasks.filter(is_verified=False).count()
    recent_tasks = tasks.order_by('-submitted_at')[:5]

    # Coins
    total_coins = user.eco_coins
    badge_name, badge_color, badge_emoji = get_badge_info(total_coins)

    # Redemption (from store app)
    pending_redemptions = Redemption.objects.filter(user=user, status='pending').count()

    # Achievement Badges
    achievement_badges = get_user_badges(user)
    
    # Badge notifications
    new_badges = UserBadge.objects.filter(user=user).order_by('-unlocked_at')[:5]
    if not request.session.get('notified_badges'):
        request.session['notified_badges'] = [b.badge_name for b in new_badges]
        notify_badges = new_badges
    else:
        notify_badges = [
            b for b in new_badges if b.badge_name not in request.session['notified_badges']
        ]
        request.session['notified_badges'] += [b.badge_name for b in notify_badges]

    context = {
        'total_issue_posts': total_issue_posts, # Renamed from total_reports
        'total_tasks': total_tasks,
        'total_coins': total_coins,
        'pending_tasks': pending_tasks,
        'pending_redemptions': pending_redemptions,
        'recent_issue_posts': recent_issue_posts, # Renamed from recent_reports
        'recent_tasks': recent_tasks,

        # Coin-based badge
        'badge_name': badge_name,
        'badge_color': badge_color,
        'badge_emoji': badge_emoji,

        # Achievement badges
        'achievement_badges': achievement_badges,
    }

    return render(request, 'core/dashboard.html', context)

