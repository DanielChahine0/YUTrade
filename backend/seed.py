"""Seed the database with dummy data for demo/presentation purposes."""

import sys
import os
from uuid import uuid4
from urllib.request import urlopen, Request
from urllib.error import URLError

sys.path.insert(0, os.path.dirname(__file__))

from datetime import datetime, timedelta
from app.database import SessionLocal, engine, Base
from app.models.user import User
from app.models.listing import Listing
from app.models.image import Image
from app.models.message import Message
from app.utils.security import hash_password
from app.config import settings

# Ensure uploads directory exists
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)

# Ensure tables exist
Base.metadata.create_all(bind=engine)


def download_image(url: str):
    """Download an image from a URL. Returns bytes or None on failure."""
    try:
        req = Request(url, headers={"User-Agent": "YUTrade-Seed/1.0"})
        with urlopen(req, timeout=15) as resp:
            return resp.read()
    except (URLError, OSError) as e:
        print(f"    Warning: Failed to download {url}: {e}")
        return None


# Curated Unsplash image URLs — each matches the listing item
LISTING_IMAGE_URLS = [
    # Textbooks (0-4)
    "https://images.unsplash.com/photo-1532012197267-da84d127e765?w=600&h=400&fit=crop",   # open book
    "https://images.unsplash.com/photo-1596495578065-6e0763fa1178?w=600&h=400&fit=crop",   # math equations
    "https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?w=600&h=400&fit=crop",      # stack of books
    "https://images.unsplash.com/photo-1509228468518-180dd4864904?w=600&h=400&fit=crop",    # math/chalkboard
    "https://images.unsplash.com/photo-1497633762265-9d179a990aa6?w=600&h=400&fit=crop",    # textbooks
    # Electronics (5-8)
    "https://images.unsplash.com/photo-1564466809058-bf4114d55352?w=600&h=400&fit=crop",    # calculator
    "https://images.unsplash.com/photo-1527864550417-7fd91fc51a46?w=600&h=400&fit=crop",    # computer mouse
    "https://images.unsplash.com/photo-1606220588913-b3aacb4d2f46?w=600&h=400&fit=crop",    # airpods
    "https://images.unsplash.com/photo-1618384887929-16ec33fab9ef?w=600&h=400&fit=crop",    # mechanical keyboard
    # Furniture (9-11)
    "https://images.unsplash.com/photo-1594620302200-9a762244a156?w=600&h=400&fit=crop",    # bookshelf
    "https://images.unsplash.com/photo-1580480055273-228ff5388ef8?w=600&h=400&fit=crop",    # desk chair
    "https://images.unsplash.com/photo-1518455027359-f3f8164ba6bd?w=600&h=400&fit=crop",    # desk/workspace
    # Clothing (12-13)
    "https://images.unsplash.com/photo-1556821840-3a63f95609a7?w=600&h=400&fit=crop",      # hoodie
    "https://images.unsplash.com/photo-1539533018447-63fcce2678e3?w=600&h=400&fit=crop",    # winter jacket
    # Other (14-15)
    "https://images.unsplash.com/photo-1548839140-29a749e1cf4d?w=600&h=400&fit=crop",      # water pitcher
    "https://images.unsplash.com/photo-1585515320310-259814833e62?w=600&h=400&fit=crop",    # slow cooker
    # Sold (16-17)
    "https://images.unsplash.com/photo-1635070041078-e363dbe005cb?w=600&h=400&fit=crop",    # physics equations
    "https://images.unsplash.com/photo-1625842268584-8f3296236761?w=600&h=400&fit=crop",    # USB hub
]


db = SessionLocal()

# Check if listings WITH images already exist
existing_listing = db.query(Listing).first()
if existing_listing and db.query(Image).first():
    print("Database already has listings with images. Skipping seed.")
    db.close()
    sys.exit(0)

# If listings exist but no images, wipe them so we re-seed with images
if existing_listing:
    print("Found listings without images — clearing and re-seeding...")
    db.query(Message).delete()
    db.query(Image).delete()
    db.query(Listing).delete()
    db.commit()

print("Seeding database...")

# ── Users ──────────────────────────────────────────────────────────────────
password = hash_password("password123")

seed_users = [
    ("raj1308@my.yorku.ca", "Rajendra Brahmbhatt", 30),
    ("daniel@my.yorku.ca", "Daniel Chahine", 28),
    ("lakshan@my.yorku.ca", "Lakshan Kandeepan", 25),
    ("mickey@my.yorku.ca", "Mickey Byalsky", 20),
    ("mai@my.yorku.ca", "Mai Komar", 15),
    ("harnain@my.yorku.ca", "Harnaindeep Kaur", 10),
]

users = []
for email, name, days_ago in seed_users:
    existing = db.query(User).filter(User.email == email).first()
    if existing:
        # Make sure existing user is verified so they can be used
        if not existing.is_verified:
            existing.is_verified = True
            db.commit()
        users.append(existing)
    else:
        u = User(email=email, password_hash=password, name=name, is_verified=True, created_at=datetime.utcnow() - timedelta(days=days_ago))
        db.add(u)
        db.commit()
        db.refresh(u)
        users.append(u)

raj, daniel, lakshan, mickey, mai, harnain = users

print(f"  Created {len(users)} users (password: password123)")

# ── Listings ───────────────────────────────────────────────────────────────
listings_data = [
    # Textbooks
    Listing(seller_id=raj.id, title="EECS 2011 Data Structures Textbook", description="Goodrich & Tamassia, 6th edition. Some highlighting in chapters 1-5, otherwise great condition. Perfect for EECS 2011.", price=35.00, category="Textbooks", status="active", created_at=datetime.utcnow() - timedelta(days=2)),
    Listing(seller_id=daniel.id, title="Calculus: Early Transcendentals 9th Ed", description="James Stewart. Clean copy, no markings. Used for MATH 1300/1310.", price=50.00, category="Textbooks", status="active", created_at=datetime.utcnow() - timedelta(days=5)),
    Listing(seller_id=lakshan.id, title="Introduction to Algorithms (CLRS)", description="Cormen, Leiserson, Rivest, Stein. The classic algorithms textbook. Hardcover, minor shelf wear.", price=45.00, category="Textbooks", status="active", created_at=datetime.utcnow() - timedelta(days=1)),
    Listing(seller_id=mai.id, title="Discrete Mathematics and Its Applications", description="Rosen, 8th edition. Useful for EECS 1019. Has some pencil notes that can be erased.", price=30.00, category="Textbooks", status="active", created_at=datetime.utcnow() - timedelta(days=7)),
    Listing(seller_id=harnain.id, title="Operating System Concepts (Dinosaur Book)", description="Silberschatz, 10th edition. Great for EECS 3221. Like new condition.", price=40.00, category="Textbooks", status="active", created_at=datetime.utcnow() - timedelta(days=3)),

    # Electronics
    Listing(seller_id=mickey.id, title="TI-84 Plus CE Graphing Calculator", description="Texas Instruments TI-84 Plus CE. Works perfectly, comes with USB charging cable. Great for math and stats courses.", price=75.00, category="Electronics", status="active", created_at=datetime.utcnow() - timedelta(days=4)),
    Listing(seller_id=raj.id, title="Logitech MX Master 3S Mouse", description="Wireless mouse, barely used for one semester. Comes with USB-C cable and dongle. Ergonomic design.", price=60.00, category="Electronics", status="active", created_at=datetime.utcnow() - timedelta(hours=12)),
    Listing(seller_id=daniel.id, title="Apple AirPods Pro 2nd Gen", description="Used for 3 months. All ear tips included, original case. Battery health still excellent.", price=150.00, category="Electronics", status="active", created_at=datetime.utcnow() - timedelta(days=6)),
    Listing(seller_id=lakshan.id, title="Mechanical Keyboard - Keychron K2", description="Wireless mechanical keyboard, brown switches. RGB backlight. Great for coding.", price=55.00, category="Electronics", status="active", created_at=datetime.utcnow() - timedelta(days=8)),

    # Furniture
    Listing(seller_id=mai.id, title="IKEA KALLAX Shelf Unit", description="4x2 shelf unit in white. Perfect for dorm room. Minor scuffs on the side. Must pick up from Keele campus area.", price=40.00, category="Furniture", status="active", created_at=datetime.utcnow() - timedelta(days=10)),
    Listing(seller_id=harnain.id, title="Ergonomic Desk Chair", description="Mesh back office chair with lumbar support. Adjustable height and armrests. Used for one year.", price=85.00, category="Furniture", status="active", created_at=datetime.utcnow() - timedelta(days=9)),
    Listing(seller_id=mickey.id, title="Foldable Study Desk", description="Compact desk, great for small spaces. White top with metal legs. Easy to fold and store.", price=25.00, category="Furniture", status="active", created_at=datetime.utcnow() - timedelta(days=14)),

    # Clothing
    Listing(seller_id=raj.id, title="YorkU Lions Hoodie - Size L", description="Official York University hoodie, red with white logo. Worn a few times, no stains. Very warm for winter.", price=30.00, category="Clothing", status="active", created_at=datetime.utcnow() - timedelta(days=3)),
    Listing(seller_id=daniel.id, title="North Face Winter Jacket - Size M", description="Black puffer jacket. Kept me warm through two York winters. Great condition.", price=90.00, category="Clothing", status="active", created_at=datetime.utcnow() - timedelta(days=11)),

    # Other
    Listing(seller_id=lakshan.id, title="Brita Water Filter Pitcher", description="Large 10-cup pitcher with 2 spare filters. Moving out and can't take it with me.", price=15.00, category="Other", status="active", created_at=datetime.utcnow() - timedelta(days=2)),
    Listing(seller_id=mai.id, title="Crock-Pot Slow Cooker 6-Quart", description="Used maybe 5 times. Perfect for meal prepping in residence. Comes with lid and manual.", price=20.00, category="Other", status="active", created_at=datetime.utcnow() - timedelta(days=13)),

    # Sold listings
    Listing(seller_id=raj.id, title="Physics for Scientists & Engineers", description="Serway & Jewett, 10th edition. SOLD to a PHYS 1410 student.", price=40.00, category="Textbooks", status="sold", created_at=datetime.utcnow() - timedelta(days=20)),
    Listing(seller_id=mickey.id, title="USB-C Hub 7-in-1", description="Anker hub with HDMI, USB-A, SD card reader. Sold.", price=30.00, category="Electronics", status="sold", created_at=datetime.utcnow() - timedelta(days=18)),
]

for listing in listings_data:
    db.add(listing)
db.commit()
for listing in listings_data:
    db.refresh(listing)

print(f"  Created {len(listings_data)} listings")

# ── Images ────────────────────────────────────────────────────────────────
image_count = 0
print("  Downloading images...")
for i, listing in enumerate(listings_data):
    url = LISTING_IMAGE_URLS[i] if i < len(LISTING_IMAGE_URLS) else f"https://picsum.photos/seed/listing{i}/600/400"
    img_bytes = download_image(url)
    if img_bytes:
        filename = f"{uuid4()}.jpg"
        disk_path = os.path.join(settings.UPLOAD_DIR, filename)
        with open(disk_path, "wb") as f:
            f.write(img_bytes)
        img = Image(listing_id=listing.id, file_path=f"uploads/{filename}", position=0)
        db.add(img)
        image_count += 1
db.commit()

print(f"  Downloaded {image_count} images")

# ── Messages ───────────────────────────────────────────────────────────────
# Daniel asks Raj about the Data Structures textbook
textbook_listing = listings_data[0]  # Raj's EECS 2011 textbook
messages_data = [
    Message(listing_id=textbook_listing.id, sender_id=daniel.id, receiver_id=raj.id, content="Hey, is this textbook still available?", created_at=datetime.utcnow() - timedelta(hours=10)),
    Message(listing_id=textbook_listing.id, sender_id=raj.id, receiver_id=daniel.id, content="Yes it is! Are you taking EECS 2011 this semester?", created_at=datetime.utcnow() - timedelta(hours=9)),
    Message(listing_id=textbook_listing.id, sender_id=daniel.id, receiver_id=raj.id, content="Yeah, starting next week. Can we meet at the Student Centre?", created_at=datetime.utcnow() - timedelta(hours=8)),
    Message(listing_id=textbook_listing.id, sender_id=raj.id, receiver_id=daniel.id, content="Sure, how about Thursday at 2pm? I'll be near the Tim Hortons.", created_at=datetime.utcnow() - timedelta(hours=7)),

    # Lakshan asks Mickey about the calculator
    Message(listing_id=listings_data[5].id, sender_id=lakshan.id, receiver_id=mickey.id, content="Would you take $60 for the calculator?", created_at=datetime.utcnow() - timedelta(hours=5)),
    Message(listing_id=listings_data[5].id, sender_id=mickey.id, receiver_id=lakshan.id, content="I can do $65, it's practically new.", created_at=datetime.utcnow() - timedelta(hours=4)),
    Message(listing_id=listings_data[5].id, sender_id=lakshan.id, receiver_id=mickey.id, content="Deal! Where should we meet?", created_at=datetime.utcnow() - timedelta(hours=3)),

    # Mai asks Raj about the mouse
    Message(listing_id=listings_data[6].id, sender_id=mai.id, receiver_id=raj.id, content="Hi! Is the MX Master still available? Does it work with Mac?", created_at=datetime.utcnow() - timedelta(hours=2)),
    Message(listing_id=listings_data[6].id, sender_id=raj.id, receiver_id=mai.id, content="Yes and yes! It works with Mac, Windows, and Linux. Bluetooth + dongle.", created_at=datetime.utcnow() - timedelta(hours=1)),

    # Harnain asks Daniel about the jacket
    Message(listing_id=listings_data[13].id, sender_id=harnain.id, receiver_id=daniel.id, content="Is the North Face jacket waterproof?", created_at=datetime.utcnow() - timedelta(hours=6)),
    Message(listing_id=listings_data[13].id, sender_id=daniel.id, receiver_id=harnain.id, content="It's water resistant, not fully waterproof. But it handled snow just fine.", created_at=datetime.utcnow() - timedelta(hours=5, minutes=30)),
]

for msg in messages_data:
    db.add(msg)
db.commit()

print(f"  Created {len(messages_data)} messages across 4 conversations")

db.close()

print("\nDone! You can log in with any of these accounts:")
print("  Email: raj1308@my.yorku.ca     Password: password123")
print("  Email: daniel@my.yorku.ca      Password: password123")
print("  Email: lakshan@my.yorku.ca     Password: password123")
print("  Email: mickey@my.yorku.ca      Password: password123")
print("  Email: mai@my.yorku.ca         Password: password123")
print("  Email: harnain@my.yorku.ca     Password: password123")
