from django.contrib import admin
from .models import StoreOffer, Redemption

@admin.register(StoreOffer)
class StoreOfferAdmin(admin.ModelAdmin):
    list_display = ('name', 'offer_type', 'coins_required', 'stock', 'is_active', 'start_date', 'end_date', 'added_by')
    list_filter = ('offer_type', 'is_active', 'start_date', 'end_date')
    search_fields = ('name', 'description', 'location_name')
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)
    fieldsets = (
        (None, {
            'fields': ('name', 'description', 'image', 'offer_type', 'coins_required', 'stock')
        }),
        ('Location Details', {
            'fields': ('location_name', 'location_map_url')
        }),
        ('Availability', {
            'fields': ('start_date', 'end_date', 'is_active')
        }),
        ('Admin Info', {
            'fields': ('added_by',)
        }),
    )
    raw_id_fields = ('added_by',) # For large number of users

@admin.register(Redemption)
class RedemptionAdmin(admin.ModelAdmin):
    list_display = ('user', 'offer', 'coins_spent', 'redeemed_at', 'voucher_code', 'status')
    list_filter = ('status', 'redeemed_at', 'offer__offer_type')
    search_fields = ('user__username', 'offer__name', 'voucher_code')
    date_hierarchy = 'redeemed_at'
    ordering = ('-redeemed_at',)
    raw_id_fields = ('user', 'offer')
