from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
import uuid

User = get_user_model()

class StoreOffer(models.Model):
    OFFER_TYPE_CHOICES = [
        ('shop_offer', 'Shop Offer'),
        ('donor_gift', 'Donor Gift'),
        ('event_ticket', 'Event Ticket'),
        ('eco_reward', 'Eco Reward'),
    ]

    name = models.CharField(max_length=255)
    description = models.TextField()
    image = models.ImageField(upload_to='store_offers/', blank=True, null=True)
    coins_required = models.PositiveIntegerField()
    offer_type = models.CharField(max_length=20, choices=OFFER_TYPE_CHOICES)
    location_name = models.CharField(max_length=255)
    location_map_url = models.URLField(blank=True, null=True)
    stock = models.PositiveIntegerField(default=0)
    start_date = models.DateField()
    end_date = models.DateField()
    added_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="offers_added")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def is_available(self):
        return (
            self.is_active
            and self.stock > 0
            and self.start_date <= timezone.now().date() <= self.end_date
        )

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['-created_at']


class Redemption(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="redemptions")
    offer = models.ForeignKey(StoreOffer, on_delete=models.CASCADE, related_name="redemptions")
    coins_spent = models.PositiveIntegerField()
    redeemed_at = models.DateTimeField(auto_now_add=True)
    voucher_code = models.CharField(max_length=20, unique=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='completed')

    def save(self, *args, **kwargs):
        if not self.voucher_code:
            self.voucher_code = str(uuid.uuid4()).split('-')[0].upper()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username} - {self.offer.name}"

    class Meta:
        ordering = ['-redeemed_at']
