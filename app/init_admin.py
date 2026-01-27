"""
Script to create an initial admin user.
Run this once to set up the first admin user.
"""

from sqlalchemy.orm import Session
from app.database import SessionLocal, init_db
from app import models
from app.auth import get_password_hash, get_user_by_username
import sys

def create_admin_user(
    username: str = "admin",
    email: str = "admin@example.com",
    password: str = "Admin123!",
    full_name: str = "System Administrator"
):
    """Create an initial admin user"""
    db: Session = SessionLocal()
    
    try:
        # Initialize database
        init_db()
        
        # Check if admin already exists
        existing_user = get_user_by_username(db, username)
        if existing_user:
            print(f"User '{username}' already exists!")
            return False
        
        # Create admin user
        admin_user = models.User(
            username=username,
            email=email,
            hashed_password=get_password_hash(password),
            full_name=full_name,
            is_active=True,
            is_superuser=True
        )
        
        db.add(admin_user)
        db.commit()
        db.refresh(admin_user)
        
        print(f"✅ Admin user created successfully!")
        print(f"Username: {username}")
        print(f"Email: {email}")
        print(f"Password: {password}")
        print(f"\n⚠️  IMPORTANT: Change the password after first login!")
        
        return True
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error creating admin user: {str(e)}")
        return False
    finally:
        db.close()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        username = sys.argv[1]
        email = sys.argv[2] if len(sys.argv) > 2 else f"{username}@example.com"
        password = sys.argv[3] if len(sys.argv) > 3 else "Admin123!"
        full_name = sys.argv[4] if len(sys.argv) > 4 else "System Administrator"
        create_admin_user(username, email, password, full_name)
    else:
        create_admin_user()
