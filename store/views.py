from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.utils import timezone
from django.db import transaction
from django.core.paginator import Paginator
from django.db.models import Q
from .models import StoreOffer, Redemption
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor
import logging

logger = logging.getLogger(__name__)

@login_required
def store_view(request):
    """Main store view with filtering capabilities"""
    try:
        # Get filter parameters
        search_query = request.GET.get('search', '').strip()
        category_filter = request.GET.get('category', 'all')
        sort_by = request.GET.get('sort', 'name')
        
        # Base queryset - only active offers within date range
        offers = StoreOffer.objects.filter(
            is_active=True
        )
        
        # Apply search filter
        if search_query:
            offers = offers.filter(
                Q(name__icontains=search_query) |
                Q(description__icontains=search_query) |
                Q(location_name__icontains=search_query)
            )
        
        # Apply category filter
        if category_filter != 'all':
            offers = offers.filter(offer_type=category_filter)
        
        # Apply sorting
        sort_options = {
            'name': 'name',
            'coins_asc': 'coins_required',
            'coins_desc': '-coins_required',
            'stock': '-stock',
            'newest': '-created_at'
        }
        offers = offers.order_by(sort_options.get(sort_by, 'newest'))
        
        context = {
            'offers': offers,
            'search_query': search_query,
            'category_filter': category_filter,
            'sort_by': sort_by,
            'total_offers': offers.count(),
            'user_coins': request.user.eco_coins,
        }
        
        return render(request, 'store/store.html', context)
        
    except Exception as e:
        logger.error(f"Error in store_view: {str(e)}")
        messages.error(request, "An error occurred while loading the store.")
        return render(request, 'store/store.html', {'offers': [], 'user_coins': request.user.eco_coins})

@login_required
def redeem_offer(request, offer_id):
    """Redeem an offer"""
    if request.method != 'POST':
        messages.error(request, "Invalid request method.")
        return redirect('store_view')
    
    try:
        with transaction.atomic():
            # Get the offer and lock it for update
            offer = get_object_or_404(
                StoreOffer.objects.select_for_update(),
                id=offer_id
            )
            
            # Refresh user data to get latest coin balance
            request.user.refresh_from_db()
            
            # Validation checks
            if request.user.eco_coins < offer.coins_required:
                messages.error(
                    request,
                    f"You need {offer.coins_required - request.user.eco_coins} more EcoCoins to redeem this offer."
                )
                return redirect('store_view')
            
            if not offer.is_available():
                messages.error(request, "This offer is no longer available.")
                return redirect('store_view')
            
            if offer.stock <= 0:
                messages.error(request, "This offer is out of stock.")
                return redirect('store_view')
            
            # Deduct coins from user
            request.user.eco_coins -= offer.coins_required
            request.user.save()
            
            # Reduce stock
            offer.stock -= 1
            offer.save()
            
            # Create redemption record
            redemption = Redemption.objects.create(
                user=request.user,
                offer=offer,
                coins_spent=offer.coins_required
            )
            
            messages.success(
                request,
                f"Successfully redeemed '{offer.name}'! Your voucher code is: {redemption.voucher_code}"
            )
            return redirect('redemption_voucher', redemption_id=redemption.id)
            
    except Exception as e:
        logger.error(f"Error in redeem_offer: {str(e)}")
        messages.error(request, "An error occurred during redemption. Please try again.")
        return redirect('store_view')


@login_required
def redemption_voucher(request, redemption_id):
    """Display redemption voucher"""
    try:
        redemption = get_object_or_404(Redemption, id=redemption_id, user=request.user)
        return render(request, 'store/voucher.html', {'redemption': redemption})
    except Exception as e:
        logger.error(f"Error in redemption_voucher: {str(e)}")
        messages.error(request, "Voucher not found.")
        return redirect('store_view')

@login_required
def download_voucher_pdf(request, redemption_id):
    """Generate and download PDF voucher"""
    try:
        redemption = get_object_or_404(Redemption, id=redemption_id, user=request.user)
        
        # Create PDF response
        response = HttpResponse(content_type='application/pdf')
        filename = f"voucher_{redemption.voucher_code}.pdf"
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        
        # Create PDF
        p = canvas.Canvas(response, pagesize=A4)
        width, height = A4
        
        # Header
        p.setFont("Helvetica-Bold", 20)
        p.drawString(50, height - 50, "EcoCoin Store - Redemption Voucher")
        
        # Voucher details
        y = height - 100
        p.setFont("Helvetica-Bold", 14)
        p.drawString(50, y, f"Offer: {redemption.offer.name}")
        
        y -= 30
        p.setFont("Helvetica", 12)
        p.drawString(50, y, f"Description: {redemption.offer.description}")
        
        y -= 25
        p.drawString(50, y, f"Location: {redemption.offer.location_name}")
        
        y -= 25
        p.drawString(50, y, f"Coins Spent: {redemption.coins_spent}")
        
        y -= 25
        p.setFont("Helvetica-Bold", 12)
        p.drawString(50, y, f"Voucher Code: {redemption.voucher_code}")
        
        y -= 25
        p.setFont("Helvetica", 12)
        p.drawString(50, y, f"Redeemed On: {redemption.redeemed_at.strftime('%B %d, %Y at %H:%M')}")
        
        y -= 25
        p.drawString(50, y, f"Valid Until: {redemption.offer.end_date.strftime('%B %d, %Y')}")
        
        # Terms
        y -= 50
        p.setFont("Helvetica-Bold", 12)
        p.drawString(50, y, "Terms & Conditions:")
        
        terms = [
            "• This voucher is valid for one-time use only",
            "• Present this voucher at the specified location",
            "• Cannot be exchanged for cash",
            "• Valid only until the expiration date"
        ]
        
        p.setFont("Helvetica", 10)
        for term in terms:
            y -= 20
            p.drawString(70, y, term)
        
        p.showPage()
        p.save()
        
        return response
        
    except Exception as e:
        logger.error(f"Error in download_voucher_pdf: {str(e)}")
        messages.error(request, "Error generating PDF.")
        return redirect('redemption_voucher', redemption_id=redemption_id)

@login_required
def redemption_history(request):
    """View user's redemption history"""
    try:
        redemptions = Redemption.objects.filter(user=request.user).select_related('offer')
        
        # Pagination
        paginator = Paginator(redemptions, 10)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        
        total_spent = sum(r.coins_spent for r in redemptions)
        
        context = {
            'redemptions': page_obj,
            'total_spent': total_spent,
            'total_redemptions': redemptions.count()
        }
        
        return render(request, 'store/redemption_history.html', context)
        
    except Exception as e:
        logger.error(f"Error in redemption_history: {str(e)}")
        messages.error(request, "Error loading redemption history.")
        return render(request, 'store/redemption_history.html', {'redemptions': []})

@login_required
def offer_detail(request, offer_id):
    """View offer details"""
    try:
        offer = get_object_or_404(StoreOffer, id=offer_id, is_active=True)
        context = {
            'offer': offer,
            'can_afford': request.user.eco_coins >= offer.coins_required,
            'user_coins': request.user.eco_coins
        }
        return render(request, 'store/offer_detail.html', context)
    except Exception as e:
        logger.error(f"Error in offer_detail: {str(e)}")
        messages.error(request, "Offer not found.")
        return redirect('store_view')
