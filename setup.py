#!/usr/bin/env python3
"""
Setup script for QuickLine LLC MCA Platform
Initializes the database and creates an admin user
"""

import os
import sys
from getpass import getpass

# Add the parent directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models import User


def setup_database():
    """Initialize the database"""
    app = create_app()
    
    with app.app_context():
        print("🚀 Setting up QuickLine LLC MCA Platform...")
        print("\n📊 Creating database tables...")
        
        try:
            db.create_all()
            print("✅ Database tables created successfully!")
        except Exception as e:
            print(f"❌ Error creating database tables: {e}")
            return False
        
        return True


def create_admin_user():
    """Create the initial admin user"""
    app = create_app()
    
    with app.app_context():
        # Check if admin already exists
        existing_admin = User.query.filter_by(username='admin').first()
        if existing_admin:
            print("\n⚠️  Admin user already exists!")
            response = input("Do you want to create a new admin user? (y/n): ")
            if response.lower() != 'y':
                return True
        
        print("\n👤 Create Admin User")
        print("-" * 40)
        
        username = input("Username (default: admin): ").strip() or "admin"
        email = input("Email (default: admin@quickline.com): ").strip() or "admin@quickline.com"
        first_name = input("First Name (default: Admin): ").strip() or "Admin"
        last_name = input("Last Name (default: User): ").strip() or "User"
        
        while True:
            password = getpass("Password: ")
            confirm_password = getpass("Confirm Password: ")
            
            if password != confirm_password:
                print("❌ Passwords do not match. Please try again.")
                continue
            
            if len(password) < 6:
                print("❌ Password must be at least 6 characters.")
                continue
            
            break
        
        try:
            admin = User(
                username=username,
                email=email,
                role='admin',
                first_name=first_name,
                last_name=last_name
            )
            admin.set_password(password)
            
            db.session.add(admin)
            db.session.commit()
            
            print(f"\n✅ Admin user '{username}' created successfully!")
            print(f"\n📝 Login credentials:")
            print(f"   URL: http://localhost:5000/auth/login")
            print(f"   Email: {email}")
            print(f"   Username: {username}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error creating admin user: {e}")
            db.session.rollback()
            return False


def create_sample_rep():
    """Create a sample rep user"""
    app = create_app()
    
    with app.app_context():
        print("\n👥 Create Sample Rep User? (optional)")
        response = input("Create a sample rep user? (y/n): ")
        
        if response.lower() != 'y':
            return True
        
        try:
            rep = User(
                username='rep1',
                email='rep1@quickline.com',
                role='rep',
                first_name='John',
                last_name='Doe'
            )
            rep.set_password('rep123')
            
            db.session.add(rep)
            db.session.commit()
            
            print(f"✅ Sample rep user created!")
            print(f"   Email: rep1@quickline.com")
            print(f"   Password: rep123")
            
            return True
            
        except Exception as e:
            print(f"❌ Error creating rep user: {e}")
            db.session.rollback()
            return False


def main():
    """Main setup function"""
    print("=" * 50)
    print("  QuickLine LLC - MCA Platform Setup")
    print("=" * 50)
    
    # Setup database
    if not setup_database():
        print("\n❌ Setup failed at database creation step.")
        sys.exit(1)
    
    # Create admin user
    if not create_admin_user():
        print("\n❌ Setup failed at admin user creation step.")
        sys.exit(1)
    
    # Create sample rep (optional)
    create_sample_rep()
    
    print("\n" + "=" * 50)
    print("🎉 Setup completed successfully!")
    print("=" * 50)
    print("\n📚 Next steps:")
    print("   1. Run the application: python run.py")
    print("   2. Visit: http://localhost:5000")
    print("   3. Login with your admin credentials")
    print("   4. Test the public application form: http://localhost:5000/apply")
    print("\n💡 Tips:")
    print("   - Change default passwords immediately")
    print("   - Configure your .env file for production")
    print("   - Check README.md for deployment instructions")
    print("\n")


if __name__ == '__main__':
    main()
