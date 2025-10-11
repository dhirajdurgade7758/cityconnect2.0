import os
import django

# 1️⃣ Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cityconnect.settings')
django.setup()

# 2️⃣ Import models AFTER setup
from core.models import User
from issues.models import IssuePost  # ✅ change to your app name if different

# 3️⃣ Get an existing user (use your own username if needed)
user = User.objects.first()
if not user:
    raise Exception("❌ No users found. Create one using 'python manage.py createsuperuser'.")

# 4️⃣ Create sample issues
more_issues = [
    {
        "title": "Open manhole near Gole Ka Mandir",
        "description": "An open manhole on the main road near Gole Ka Mandir poses a danger to pedestrians and two-wheelers.",
        "department": "public_works",
        "reported_latitude": 26.2228,
        "reported_longitude": 78.2049,
        "location_name": "Gole Ka Mandir, Gwalior",
        "location_map_url": "https://www.google.com/maps?q=26.2228,78.2049",
        "status": "pending",
        "is_verified": True,
        "verification_method": "openai",
        "verification_score": 0.89,
    },
    {
        "title": "Street flooded after rainfall near Thatipur",
        "description": "After last night's heavy rain, streets near Thatipur are flooded due to poor drainage maintenance.",
        "department": "water_supply",
        "reported_latitude": 26.2192,
        "reported_longitude": 78.2042,
        "location_name": "Thatipur, Gwalior",
        "location_map_url": "https://www.google.com/maps?q=26.2192,78.2042",
        "status": "in_progress",
        "is_verified": True,
        "verification_method": "openai",
        "verification_score": 0.91,
    },
    {
        "title": "Garbage pile-up at Phoolbagh area",
        "description": "Garbage has been accumulating near Phoolbagh garden, emitting foul smell and attracting stray animals.",
        "department": "waste_management",
        "reported_latitude": 26.2164,
        "reported_longitude": 78.1821,
        "location_name": "Phoolbagh, Gwalior",
        "location_map_url": "https://www.google.com/maps?q=26.2164,78.1821",
        "status": "pending",
        "is_verified": True,
        "verification_method": "openai",
        "verification_score": 0.93,
    },
    {
        "title": "Frequent power cuts near Morar Cantt",
        "description": "Residents of Morar Cantt facing frequent power cuts throughout the day for the past week.",
        "department": "electricity",
        "reported_latitude": 26.2435,
        "reported_longitude": 78.2392,
        "location_name": "Morar Cantt, Gwalior",
        "location_map_url": "https://www.google.com/maps?q=26.2435,78.2392",
        "status": "in_progress",
        "is_verified": False,
    },
    {
        "title": "Clogged drainage near Gwalior Railway Station",
        "description": "The drainage system near Gwalior Railway Station is blocked, causing dirty water overflow on footpaths.",
        "department": "water_supply",
        "reported_latitude": 26.2116,
        "reported_longitude": 78.1751,
        "location_name": "Gwalior Railway Station",
        "location_map_url": "https://www.google.com/maps?q=26.2116,78.1751",
        "status": "pending",
        "is_verified": True,
        "verification_method": "openai",
        "verification_score": 0.88,
    },
]

for data in more_issues:
    IssuePost.objects.create(user=user, **data)

print("✅ Added 5 more demo issues successfully!")
