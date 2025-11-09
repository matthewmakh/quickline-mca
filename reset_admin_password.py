"""
Reset admin password
"""
from app import create_app, db
from app.models import User
from getpass import getpass

def reset_admin_password():
    app = create_app()
    
    with app.app_context():
        admin = User.query.filter_by(email='info@quicklinellc.com').first()
        
        if not admin:
            print("❌ Admin user not found!")
            return
        
        print(f"Found admin user: {admin.email}")
        new_password = getpass("Enter new password: ")
        confirm = getpass("Confirm password: ")
        
        if new_password != confirm:
            print("❌ Passwords don't match!")
            return
        
        admin.set_password(new_password)
        db.session.commit()
        
        print("✅ Admin password updated successfully!")
        print(f"   Email: {admin.email}")
        print(f"   Login at: http://127.0.0.1:5000/auth/login")

if __name__ == "__main__":
    reset_admin_password()
