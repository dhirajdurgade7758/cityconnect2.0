import os
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from core.models import User
from django.utils.text import slugify

def task_image_upload_path(instance, filename):
    base, ext = os.path.splitext(filename)
    return f"tasks/{slugify(base)}{ext}"

class Task(models.Model):
    TASK_TYPE_CHOICES = [
        ('Recycling & Waste Management', 'Recycling & Waste Management'),
        ('Environmental Conservation', 'Environmental Conservation'),
        ('Community Engagement', 'Community Engagement'),
        ('Miscellaneous', 'Miscellaneous')
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=100, help_text="A short, descriptive title for your task.")
    description = models.TextField(help_text="Provide details about the task you completed, including location and impact.")
    task_type = models.CharField(max_length=50, choices=TASK_TYPE_CHOICES)
    proof_image = models.ImageField(upload_to=task_image_upload_path, null=True, blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)
    admin_feedback = models.TextField(blank=True, null=True) 

    eco_coins_awarded = models.PositiveIntegerField(default=0) # Additional coins on verification

    # Reported location (from browser geolocation)
    reported_latitude = models.FloatField(null=True, blank=True)
    reported_longitude = models.FloatField(null=True, blank=True)
    # AI verification results
    is_verified = models.BooleanField(default=False)
    verification_method = models.CharField(max_length=50, null=True, blank=True)  # e.g., 'openai' or 'huggingface'
    verification_score = models.FloatField(null=True, blank=True)
    verification_details = models.TextField(null=True, blank=True)

    def save(self, *args, **kwargs):
    # update user's eco_coins before saving
        if self.eco_coins_awarded:
            self.user.eco_coins += self.eco_coins_awarded
            self.user.save()
        super().save(*args, **kwargs)  # actually save the Task!
    def __str__(self):
        return f"{self.user.username} - {self.get_task_type_display()}"


def issue_image_upload_path(instance, filename):
    return os.path.join('issues', timezone.now().strftime('%Y/%m/%d'), filename)

class IssuePost(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('resolved', 'Resolved'),
    ]
    DEPARTMENT_CHOICES = [
        ('public_works', 'Public Works Department'),
        ('water_supply', 'Water Supply Department'),
        ('waste_management', 'Waste Management Department'),
        ('electricity', 'Electricity Department')
    ]

    id = models.AutoField(primary_key=True, editable=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='issue_posts')
    title = models.CharField(max_length=150)
    description = models.TextField()
    image = models.ImageField(upload_to='issue_posts/', blank=True, null=True)
    department = models.CharField(max_length=50, choices=DEPARTMENT_CHOICES, help_text="Select the relevant department for this issue.")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='pending'
    )
    likes_count = models.PositiveIntegerField(default=0)
    comments_count = models.PositiveIntegerField(default=0)
    # Reported location (from browser geolocation)
    reported_latitude = models.FloatField(null=True, blank=True)
    reported_longitude = models.FloatField(null=True, blank=True)
    location_name = models.CharField(max_length=255, null=True, blank=True)  
    location_map_url = models.URLField(max_length=500, null=True, blank=True)  
    # AI verification results
    is_verified = models.BooleanField(default=False)
    verification_method = models.CharField(max_length=50, null=True, blank=True)  # e.g., 'openai' or 'huggingface'
    verification_score = models.FloatField(null=True, blank=True)
    verification_details = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.title} - {self.user.username}"

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Issue Post'
        verbose_name_plural = 'Issue Posts'
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['status']),
            models.Index(fields=['department']), # New index for department
        ]

    def is_liked_by(self):
        user = self.user
        """Check if the post is liked by the current user"""
        if not user.is_authenticated:
            return False
        return self.likes.filter(user=user).exists()

    def update_counts(self):
        """Update denormalized counts"""
        self.likes_count = self.likes.count()
        self.comments_count = self.comments.count()
        self.save(update_fields=['likes_count', 'comments_count'])


    
class SavedPost(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='saved_posts')
    post = models.ForeignKey(IssuePost, on_delete=models.CASCADE)
    saved_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'post')

    def __str__(self):
        return f"{self.user.username} saved {self.post.id}"

class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(IssuePost, on_delete=models.CASCADE, related_name='comments')
    text = models.TextField(max_length=300)
    timestamp = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-timestamp']
        verbose_name = 'Comment'
        verbose_name_plural = 'Comments'
        indexes = [
            models.Index(fields=['-timestamp']),
        ]

    def __str__(self):
        return f"{self.user.username} on {self.post.title}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.post.update_counts()


class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(IssuePost, on_delete=models.CASCADE, related_name='likes')
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'post')
        verbose_name = 'Like'
        verbose_name_plural = 'Likes'
        indexes = [
            models.Index(fields=['-timestamp']),
        ]

    def __str__(self):
        return f"{self.user.username} liked {self.post.title}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.post.update_counts()