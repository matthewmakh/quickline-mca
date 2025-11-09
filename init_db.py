#!/usr/bin/env python3
"""
Initialize Flask-Migrate for the project
"""
import os
import sys

# Add the parent directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from flask_migrate import Migrate, init, migrate, upgrade

app = create_app()
migrate_obj = Migrate(app, db)

if __name__ == '__main__':
    with app.app_context():
        print("Initializing Flask-Migrate...")
        
        # Check if migrations folder exists
        if not os.path.exists('migrations'):
            print("Creating migrations folder...")
            os.system('flask db init')
        
        print("Creating migration...")
        os.system('flask db migrate -m "Initial migration"')
        
        print("Applying migration...")
        os.system('flask db upgrade')
        
        print("\n✅ Database initialized successfully!")
