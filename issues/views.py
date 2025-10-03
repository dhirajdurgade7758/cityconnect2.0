from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model, login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.core.paginator import Paginator
from django.core.mail import send_mail
from django.http import JsonResponse
from django.db.models import Q
import requests

from cityconnect import settings
from issues.services import *
from .forms import TaskForm, CommentForm, IssuePostForm
from .models import Task, IssuePost, Like, Comment, SavedPost

import logging
logger = logging.getLogger(__name__)
# Create your views here.

def verify_task(request, task_id):
    # This view is likely for admin panel or internal use, keeping it as is.
    task = get_object_or_404(Task, id=task_id)
    task.is_verified = True
    task.award_eco_coins()
    messages.success(request, f"{task.eco_coins_awarded} EcoCoins awarded!")
    return redirect('admin_task_list') # Assuming an admin URL for tasks

def reverse_geocode(lat, lon):
    """
    Get a human-readable location name from coordinates using OpenStreetMap's Nominatim API.
    Returns the display name or None.
    """
    try:
        url = f"https://nominatim.openstreetmap.org/reverse"
        params = {
            "lat": lat,
            "lon": lon,
            "format": "json",
            "zoom": 16,  # Adjust detail level
            "addressdetails": 1
        }
        headers = {
            "User-Agent": "CityConnectApp/1.0"
        }
        resp = requests.get(url, params=params, headers=headers, timeout=5)
        resp.raise_for_status()
        data = resp.json()
        return data.get("display_name")
    except Exception as e:
        print("Reverse geocoding error:", e)
        return None


@login_required
def create_issue_post(request):
    if request.method == 'POST':
        form = IssuePostForm(request.POST, request.FILES)
        if form.is_valid():
            issue = form.save(commit=False)
            issue.user = request.user

            # Save reported location from form
            lat = form.cleaned_data.get("reported_latitude")
            lon = form.cleaned_data.get("reported_longitude")
            issue.reported_latitude = lat
            issue.reported_longitude = lon

            # Generate location_name and map URL if coordinates provided
            if lat and lon:
                location_name = reverse_geocode(lat, lon)
                issue.location_name = location_name
                issue.location_map_url = f"https://www.google.com/maps?q={lat},{lon}"

            issue.save()

            # Build verification text query
            title = (form.cleaned_data.get("title") or "").strip()
            description = (form.cleaned_data.get("description") or "").strip()
            text_query = "Verify whether the image shows: " + " ".join(filter(None, [title, description]))

            # AI verification
            verification_result = {"error": "No verifier configured"}
            try:
                if getattr(settings, "GEMINI_API_KEY", None):
                    verification_result = verify_issue_image_gemini(issue.image.path, prompt=text_query)
                elif getattr(settings, "HF_API_KEY", None):
                    verification_result = verify_issue_image_huggingface(issue.image.path, text_query=text_query)
            except Exception as e:
                verification_result = {"error": str(e)}

            # Save AI verification results
            if verification_result and "error" not in verification_result:
                issue.is_verified = verification_result.get("is_verified", False)
                issue.verification_method = "gemini" if getattr(settings, "GEMINI_API_KEY", None) else "huggingface"
                issue.verification_score = verification_result.get("score")
                issue.verification_details = verification_result.get("details")
                issue.save()

            # Notify user
            if "error" in verification_result:
                messages.warning(request, "Issue saved. Image verification not completed: " + verification_result["error"])
            else:
                messages.success(request, "Issue saved. Image verification completed.")

            return redirect("feed")

        else:
            messages.error(request, "Error creating issue post. Please check your input.")
    else:
        form = IssuePostForm()

    return render(request, 'issues/create_issue_post.html', {'form': form})

@login_required
def feed(request):
    status_filter = request.GET.get('status')
    department_filter = request.GET.get('department') # New filter
    search_query = request.GET.get('q')
    
    posts = IssuePost.objects.select_related('user')\
                           .prefetch_related('likes', 'comments')
    
    if status_filter:
        posts = posts.filter(status=status_filter)

    if department_filter: # Apply new department filter
        posts = posts.filter(department=department_filter)
    posts = posts.filter(is_verified=True)  # Only show verified posts by default)
    if search_query:
        posts = posts.filter(
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(location_details__icontains=search_query)
        )
    
    departments = IssuePost.DEPARTMENT_CHOICES # Get department choices for filter
    
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    saved_posts = SavedPost.objects.filter(user=request.user).values_list('post_id', flat=True)
    for post in page_obj:
        print(post.location_name)
    
    context = {
        'posts': page_obj,
        'saved_posts': saved_posts,
        'status_filter': status_filter,
        'department_filter': department_filter, # Pass to template
        'search_query': search_query,
        'status_choices': IssuePost.STATUS_CHOICES,
        'department_choices': departments, # Pass to template
    }
    
    return render(request, 'issues/feed.html', context)

@login_required
def toggle_like(request, post_id):
    post = get_object_or_404(IssuePost, id=post_id)
    
    like, created = Like.objects.get_or_create(
        user=request.user,
        post=post
    )
    
    if not created:
        like.delete()
        messages.info(request, "Like removed.")
    else:
        messages.success(request, "Post liked!")
    
    # Re-render the post card to update like count/icon
    context = {
        'post': post,
        'request': request,
        'saved_posts': SavedPost.objects.filter(user=request.user).values_list('post_id', flat=True) # Needed for post_card
    }
    return render(request, 'issues/partials/post_card.html', context)


@login_required
def post_detail(request, post_id):
    post = get_object_or_404(
        IssuePost.objects.select_related('user')
                        .prefetch_related('likes', 'comments__user'),
        id=post_id
    )
    
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.user = request.user
            comment.post = post
            comment.save()
            messages.success(request, "Comment added!")
            return redirect('post_detail', post_id=post.id)
        else:
            messages.error(request, "Error adding comment.")
    else:
        form = CommentForm()
    comments = post.comments.select_related('user').order_by('-timestamp')
    context = {
        'comments': comments,
        'post': post,
        'form': form,
        'is_liked_by': post.is_liked_by(request.user),
    }
    
    return render(request, 'issues/post_detail.html', context)


@login_required
def update_post_status(request, post_id):
    if request.method == 'POST' and request.user.is_staff:
        post = get_object_or_404(IssuePost, id=post_id)
        new_status = request.POST.get('status')
        
        if new_status in dict(IssuePost.STATUS_CHOICES).keys():
            post.status = new_status
            post.save()
            messages.success(request, f"Post status updated to {post.get_status_display()}.")
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'status': 'success',
                    'new_status': post.get_status_display()
                })
        else:
            messages.error(request, "Invalid status provided.")
    else:
        messages.error(request, "You are not authorized to perform this action.")
    
    return redirect('post_detail', post_id=post_id)


@login_required
def post_comments(request, post_id):
    """View to handle comment display and creation"""
    post = get_object_or_404(IssuePost, id=post_id)
    
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.user = request.user
            comment.post = post
            comment.save()
            messages.success(request, "Comment added!")
            if request.headers.get('HX-Request'):
                # Return the updated comments list for HTMX
                comments = post.comments.select_related('user').order_by('-timestamp')
                return render(request, 'issues/partials/comments_list.html', {
                    'comments': comments,
                    'post': post
                })
            return redirect('feed')
        else:
            messages.error(request, "Error adding comment.")
    
    # GET request - return all comments
    comments = post.comments.select_related('user').order_by('-timestamp')
    return render(request, 'issues/partials/comments_list.html', {
        'comments': comments,
        'post': post
    })

@login_required
def comment_form(request, post_id):
    """Return just the comment form for HTMX"""
    post = get_object_or_404(IssuePost, id=post_id)
    comments = post.comments.select_related('user').order_by('-timestamp')
    return render(request, 'issues/partials/comment_form.html', {
        'comments': comments,
        'post': post
    })


@login_required
def toggle_save_post(request, post_id):
    post = get_object_or_404(IssuePost, id=post_id)
    saved, created = SavedPost.objects.get_or_create(user=request.user, post=post)

    if not created:
        saved.delete()
        messages.info(request, "Post unsaved.")
    else:
        messages.success(request, "Post saved!")

    # Get updated saved posts list after toggle
    saved_posts = SavedPost.objects.filter(user=request.user).values_list('post_id', flat=True)

    context = {
        'post': post,
        'saved_posts': saved_posts,
        'csrf_token': request.META.get("CSRF_COOKIE")
    }

    return render(request, 'issues/partials/post_card.html', context)


@login_required
def saved_posts_view(request):
    posts = (
        IssuePost.objects
        .filter(savedpost__user=request.user)  # only posts that are saved by this user
        .select_related('user')               # optimize FK to user
        .prefetch_related('likes', 'comments') # optimize related sets
    )
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'issues/saved_posts.html', {'saved_posts': page_obj})
# def proof_image_upload_path(instance, filename):
#     filename = filename.replace(" ", "_")  # replace spaces with underscore
#     return f'tasks/{filename}'

@login_required
def tasks(request):
    if request.method == 'POST':
        form = TaskForm(request.POST, request.FILES)
        if form.is_valid():
            task = form.save(commit=False)
            task.user = request.user
            task.reported_latitude = form.cleaned_data.get("reported_latitude")
            task.reported_longitude = form.cleaned_data.get("reported_longitude")
            task.save()
            title = (form.cleaned_data.get("title") or "").strip()
            description = (form.cleaned_data.get("description") or "").strip()
            text_query = f"Verify and score EcoCoins for: {title}. {description}"
            verification_result = {"error": "No verifier configured"}

            try:
                if getattr(settings, "GEMINI_API_KEY", None):
                    verification_result = verify_task_image_gemini(task.proof_image.path, text_query)
                elif getattr(settings, "HF_API_KEY", None):
                    verification_result = verify_issue_image_huggingface(task.proof_image.path, text_query=text_query)
            except Exception as e:
                verification_result = {"error": str(e)}

            if verification_result and "error" not in verification_result:
                task.is_verified = verification_result.get("is_verified", False)
                task.verification_method = "gemini" if getattr(settings, "GEMINI_API_KEY", None) else "huggingface"
                task.verification_score = verification_result.get("score")
                task.verification_details = verification_result.get("details")
                task.eco_coins_awarded = verification_result.get("eco_coins", 0)
                task.save()

            if "error" in verification_result:
                messages.warning(request, "Task saved. Image verification not completed: " + verification_result["error"])
            else:
                messages.success(
                    request,
                    f"Task submitted! You earned {task.eco_coins_awarded} EcoCoins based on AI assessment. "
                    "More may be added upon admin review!"
                )
            return redirect("tasks")
        else:
            messages.error(request, "Error submitting task. Please check the form.")
    else:
        form = TaskForm()

    task_list = Task.objects.filter(user=request.user).order_by('-submitted_at')
    paginator = Paginator(task_list, 5)
    page_obj = paginator.get_page(request.GET.get('page'))

    return render(request, 'issues/tasks.html', {'form': form, 'page_obj': page_obj})
