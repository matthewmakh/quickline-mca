"""
Initialize production database on Railway
Creates tables and initial admin user if needed
"""
import os
from app import create_app, db
from app.models import User

def init_production_db():
    """Initialize database and create admin user if not exists"""
    app = create_app()
    
    with app.app_context():
        # Create all tables
        db.create_all()
        print("✅ Database tables created successfully!")
        
        # Check if admin user exists
        admin = User.query.filter_by(email='info@quicklinellc.com').first()
        
        if not admin:
            # Create admin user
            admin = User(
                username='admin',
                email='info@quicklinellc.com',
                role='admin',
                first_name='Admin',
                last_name='User'
            )
            # Set password from environment variable or use default
            admin_password = os.environ.get('ADMIN_PASSWORD', 'ChangeMe123!')
            admin.set_password(admin_password)
            
            db.session.add(admin)
            db.session.commit()
            
            print(f"✅ Admin user created: {admin.email}")
            print(f"⚠️  Please change the password immediately after first login!")
        else:
            print(f"ℹ️  Admin user already exists: {admin.email}")
        
        # Count existing records
        user_count = User.query.count()
        print(f"\n📊 Database Status:")
        print(f"   - Users: {user_count}")
        
        print("\n✅ Production database initialization complete!")

if __name__ == "__main__":
    init_production_db()
