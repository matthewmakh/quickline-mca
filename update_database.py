"""
Update database with new tables: activity_logs and withdrawal_requests
Run this after pulling latest code
"""
from app import create_app, db
from app.models import ActivityLog, WithdrawalRequest

def update_database():
    app = create_app()
    
    with app.app_context():
        print("Creating new tables...")
        
        # Create new tables
        db.create_all()
        
        print("✅ Database updated successfully!")
        print("   - activity_logs table created")
        print("   - withdrawal_requests table created")
        
        # Check tables exist
        inspector = db.inspect(db.engine)
        tables = inspector.get_table_names()
        
        print(f"\n📊 Current tables in database:")
        for table in sorted(tables):
            print(f"   - {table}")

if __name__ == "__main__":
    update_database()
