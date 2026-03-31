import uuid
from sqlalchemy.orm import Session
from database import SessionLocal, engine
from database_models import Base, Service, ServiceCategory

# Create tables if they don't exist
Base.metadata.create_all(bind=engine)

def seed_services():
    db = SessionLocal()
    try:
        # Clear existing services to avoid duplicates during development
        # db.query(Service).delete() 
        # Or just add new ones if they don't exist
        
        new_services = [
            # Segment A: Instant Wash
            {"name": "Vrumo Swift Wash", "description": "Quick exterior refresh. Pressure rinse. 30-40 mins.", "price": 299.0, "category": ServiceCategory.car},
            {"name": "Vrumo Signature Wash", "description": "Full exterior + interior refresh. Pressure rinse. 60-75 mins.", "price": 549.0, "category": ServiceCategory.car},
            
            # Segment B: Colony Monthly
            {"name": "Vrumo Colony Care", "description": "4 professional foam washes/month. Always on schedule.", "price": 999.0, "category": ServiceCategory.car},
            {"name": "Vrumo Colony Elite", "description": "4 foam washes + full interior every visit.", "price": 1499.0, "category": ServiceCategory.car},
            
            # Segment C: Society Subscription
            {"name": "Vrumo Society Shield", "description": "Alt-day bucket wash + weekly interior. RWA compliant.", "price": 2000.0, "category": ServiceCategory.car},
            {"name": "Vrumo Society Prestige", "description": "Alt-day bucket + interior 4x + quarterly detail.", "price": 2800.0, "category": ServiceCategory.car},
            
            # Segment D: Deep Clean
            {"name": "Cabin Detox", "description": "Full cabin deep clean. 90-120 mins.", "price": 1499.0, "category": ServiceCategory.car},
            {"name": "Paint Refresh", "description": "Exterior decontamination + seal. 90-120 mins.", "price": 1799.0, "category": ServiceCategory.car},
            {"name": "Vrumo Grand Detox", "description": "Complete interior + exterior detailing. 3 hours.", "price": 2499.0, "category": ServiceCategory.car},
        ]
        
        for s_data in new_services:
            # Check if service already exists by name
            exists = db.query(Service).filter(Service.name == s_data["name"]).first()
            if not exists:
                service = Service(
                    id=str(uuid.uuid4()),
                    name=s_data["name"],
                    description=s_data["description"],
                    price=s_data["price"],
                    category=s_data["category"],
                    is_active=True
                )
                db.add(service)
                print(f"Added service: {s_data['name']}")
            else:
                # Update price if it changed
                exists.price = s_data["price"]
                exists.description = s_data["description"]
                print(f"Updated service: {s_data['name']}")
        
        db.commit()
        print("Seeding completed successfully!")
    except Exception as e:
        print(f"Error seeding services: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_services()
