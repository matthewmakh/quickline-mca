"""
Clear all data from the database except the admin account.
WARNING: This will delete ALL applications, customers, lines of credit, and activity logs!
Only the admin user account will remain.
"""
from app import create_app, db
from app.models import User, Customer, Application, LineOfCredit, ActivityLog, WithdrawalRequest

def clear_database():
    """Clear all data except admin account"""
    app = create_app()
    
    with app.app_context():
        print("⚠️  WARNING: This will delete ALL data except the admin account!")
        print("=" * 60)
        
        # Count current records
        print("\nCurrent database records:")
        print(f"  Applications: {Application.query.count()}")
        print(f"  Customers: {Customer.query.count()}")
        print(f"  Lines of Credit: {LineOfCredit.query.count()}")
        print(f"  Withdrawal Requests: {WithdrawalRequest.query.count()}")
        print(f"  Activity Logs: {ActivityLog.query.count()}")
        print(f"  Users (total): {User.query.count()}")
        print(f"  Admins: {User.query.filter_by(role='admin').count()}")
        print(f"  Reps: {User.query.filter_by(role='rep').count()}")
        
        confirm = input("\n⚠️  Type 'DELETE ALL' to confirm: ")
        
        if confirm != "DELETE ALL":
            print("❌ Cancelled. No data was deleted.")
            return
        
        print("\n🗑️  Deleting data...")
        
        # Delete in order to avoid foreign key constraints
        deleted_counts = {}
        
        # 1. Delete withdrawal requests
        count = WithdrawalRequest.query.delete()
        deleted_counts['Withdrawal Requests'] = count
        print(f"  ✓ Deleted {count} withdrawal requests")
        
        # 2. Delete activity logs
        count = ActivityLog.query.delete()
        deleted_counts['Activity Logs'] = count
        print(f"  ✓ Deleted {count} activity logs")
        
        # 3. Delete lines of credit
        count = LineOfCredit.query.delete()
        deleted_counts['Lines of Credit'] = count
        print(f"  ✓ Deleted {count} lines of credit")
        
        # 4. Delete customers
        count = Customer.query.delete()
        deleted_counts['Customers'] = count
        print(f"  ✓ Deleted {count} customers")
        
        # 5. Delete applications
        count = Application.query.delete()
        deleted_counts['Applications'] = count
        print(f"  ✓ Deleted {count} applications")
        
        # 6. Delete non-admin users (reps)
        count = User.query.filter(User.role != 'admin').delete()
        deleted_counts['Rep Users'] = count
        print(f"  ✓ Deleted {count} rep users")
        
        # Commit all deletions
        db.session.commit()
        
        print("\n✅ Database cleared successfully!")
        print("\nRemaining data:")
        print(f"  Admin users: {User.query.filter_by(role='admin').count()}")
        
        # Show admin usernames
        admins = User.query.filter_by(role='admin').all()
        for admin in admins:
            print(f"    - {admin.username} ({admin.email})")
        
        print("\n" + "=" * 60)
        print("Summary of deleted records:")
        for entity, count in deleted_counts.items():
            print(f"  {entity}: {count}")

if __name__ == '__main__':
    clear_database()
