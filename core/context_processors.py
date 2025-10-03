from issues.models import Task

def notification_counts(request):
    if request.user.is_authenticated:
        pending_tasks = Task.objects.filter(user=request.user, is_verified=False).count()
    else:
        pending_tasks = 0

    return {
        'pending_tasks': pending_tasks,
        'pending_redemptions': 0, # Removed from core context, handled by store app
    }
