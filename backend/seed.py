"""Seed the database with dummy data for demo/presentation purposes."""

import sys
import os
import struct
import zlib
from uuid import uuid4

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


def make_placeholder_png(width: int, height: int, r: int, g: int, b: int) -> bytes:
    """Generate a minimal solid-color PNG using only the standard library."""
    def _chunk(chunk_type: bytes, data: bytes) -> bytes:
        c = chunk_type + data
        return struct.pack(">I", len(data)) + c + struct.pack(">I", zlib.crc32(c) & 0xFFFFFFFF)

    raw = b""
    row = b""
    for _ in range(width):
        row += struct.pack("BBB", r, g, b)
    for _ in range(height):
        raw += b"\x00" + row  # filter byte 0 (None) per row

    header = struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)
    sig = b"\x89PNG\r\n\x1a\n"
    return sig + _chunk(b"IHDR", header) + _chunk(b"IDAT", zlib.compress(raw)) + _chunk(b"IEND", b"")


# Category-based colors (R, G, B) for placeholder images
CATEGORY_COLORS = {
    "Textbooks":  (66, 133, 244),   # blue
    "Electronics": (52, 168, 83),    # green
    "Furniture":  (251, 188, 4),     # yellow
    "Clothing":   (234, 67, 53),     # red
    "Other":      (142, 124, 195),   # purple
}


db = SessionLocal()

# Check if listings already exist (users may exist from real registrations)
if db.query(Listing).first():
    print("Database already has listings. Skipping seed.")
    db.close()
    sys.exit(0)

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
for listing in listings_data:
    color = CATEGORY_COLORS.get(listing.category, (128, 128, 128))
    png_bytes = make_placeholder_png(400, 300, *color)
    filename = f"{uuid4()}.png"
    disk_path = os.path.join(settings.UPLOAD_DIR, filename)
    with open(disk_path, "wb") as f:
        f.write(png_bytes)
    img = Image(listing_id=listing.id, file_path=f"uploads/{filename}", position=0)
    db.add(img)
    image_count += 1
db.commit()

print(f"  Created {image_count} placeholder images")

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
