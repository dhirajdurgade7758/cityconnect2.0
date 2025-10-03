from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone


# Extended user with roles (Citizen or Admin)
class User(AbstractUser):
    ROLE_CHOICES = (
        ('citizen', 'Citizen'),
        ('admin', 'Admin'),
    )
    DEPARTMENT_CHOICES = [
        ('public_works', 'Public Works Department'),
        ('water_supply', 'Water Supply Department'),
        ('waste_management', 'Waste Management Department'),
        ('electricity', 'Electricity Department')
    ]

    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='citizen')
    department = models.CharField(max_length=50, choices=DEPARTMENT_CHOICES, blank=True, null=True)
    eco_coins = models.PositiveIntegerField(default=0)
    area = models.CharField(max_length=100, blank=True)

    def clean(self):
        from django.core.exceptions import ValidationError
        # If user is admin, department must be set
        if self.role == 'admin' and not self.department:
            raise ValidationError('Department must be set for admin users.')
        # If user is citizen, department must be blank/null
        if self.role == 'citizen' and self.department:
            raise ValidationError('Citizens should not have a department assigned.')

    def __str__(self):
        return self.username


class News(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
    


class UserBadge(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    badge_type = models.CharField(max_length=20, choices=[
        ('eco', 'EcoCoin Badge'),
        ('achievement', 'Achievement Badge')
    ])
    badge_name = models.CharField(max_length=100)
    unlocked_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'badge_name')

    def __str__(self):
        return f"{self.user.username} - {self.badge_name}"
    
