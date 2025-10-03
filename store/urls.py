from django.urls import path
from . import views

urlpatterns = [
    path('', views.store_view, name='store_view'),
    path('offer/<int:offer_id>/', views.offer_detail, name='offer_detail'),
    path('redeem/<int:offer_id>/', views.redeem_offer, name='redeem_offer'),
    path('voucher/<int:redemption_id>/', views.redemption_voucher, name='redemption_voucher'),
    path('voucher/<int:redemption_id>/download/', views.download_voucher_pdf, name='download_voucher_pdf'),
    path('history/', views.redemption_history, name='redemption_history'),
]
