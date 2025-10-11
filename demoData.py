import os
import django
from datetime import date, timedelta

def setup_django():
    """
    Sets up the Django environment to allow standalone script execution.
    Replace 'your_project_name' with the actual name of your project folder.
    """
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cityconnect.settings')
    django.setup()

def run():
    """
    Main function to create and save the store offers.
    """
    print("Setting up Django environment...")
    setup_django()

    # Imports must happen after django.setup()
    from django.contrib.auth import get_user_model
    # Replace 'your_app_name' with the name of the app where StoreOffer is defined
    from store.models import StoreOffer

    User = get_user_model()

    print("Fetching the superuser to assign as the offer creator...")
    # Ensure you have at least one superuser in your database.
    # If not, create one: python manage.py createsuperuser
    # NEW, FIXED CODE
    try:
        # Use .filter().first() to safely get the first available superuser
        user = User.objects.filter(is_superuser=True).first()
        if not user:
            # Manually raise this error if .first() returns None
            raise User.DoesNotExist
    except User.DoesNotExist:
        print("\n--- ERROR ---")
        print("No superuser found. Please create one by running:")
        print("python manage.py createsuperuser")
        print("---------------")
        return

    # --- Data for 5 Sample Offers ---
    offer_data = [
        {
            "name": "20% Off at Green Cafe",
            "description": "Enjoy a 20% discount on your total bill. Valid on all food and beverages.",
            "coins_required": 150,
            "offer_type": "shop_offer",
            "location_name": "Green Cafe, City Center, Gwalior",
            "stock": 50,
        },
        {
            "name": "Free Organic Tote Bag",
            "description": "Receive a free reusable tote bag with any purchase over ₹500. Gifted by our eco-donor program.",
            "coins_required": 250,
            "offer_type": "donor_gift",
            "location_name": "Eco-Friendly Hub, Lashkar, Gwalior",
            "stock": 100,
        },
        {
            "name": "Ticket to 'Green Earth' Seminar",
            "description": "Get one free ticket to our annual environmental awareness seminar.",
            "coins_required": 300,
            "offer_type": "event_ticket",
            "location_name": "Gwalior Convention Center",
            "stock": 25,
        },
        {
            "name": "Plant a Tree Eco Reward",
            "description": "Redeem your coins to have a tree planted in your name through our local partner NGO.",
            "coins_required": 500,
            "offer_type": "eco_reward",
            "location_name": "Gwalior Reforestation Project",
            "stock": 999,  # High stock for a service-based reward
        },
        {
            "name": "₹100 Voucher at The Organic Store",
            "description": "A flat ₹100 discount voucher redeemable on a minimum purchase of ₹400.",
            "coins_required": 100,
            "offer_type": "shop_offer",
            "location_name": "The Organic Store, Morar, Gwalior",
            "stock": 75,
        }
    ]

    print("Deleting existing offers to prevent duplicates...")
    StoreOffer.objects.all().delete()

    print("Creating 5 new store offers...")
    today = date.today()
    for data in offer_data:
        offer = StoreOffer.objects.create(
            name=data["name"],
            description=data["description"],
            coins_required=data["coins_required"],
            offer_type=data["offer_type"],
            location_name=data["location_name"],
            location_map_url="https://maps.google.com/?q=" + data["location_name"].replace(" ", "+"),
            stock=data["stock"],
            start_date=today,
            end_date=today + timedelta(days=45),  # Make offers valid for 45 days
            added_by=user,
            is_active=True,
        )
        print(f"  -> Successfully created: '{offer.name}'")

    print("\n✅ Script finished successfully. 5 offers have been added to the database.")

# --- This allows the script to be run from the command line ---
if __name__ == '__main__':
    run()