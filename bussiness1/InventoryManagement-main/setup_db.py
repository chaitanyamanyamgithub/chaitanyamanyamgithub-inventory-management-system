#!/usr/bin/env python3
"""
Database Setup Helper Script
This script helps you set up the database configuration for the Inventory Management System.
"""

import os
import sys
import shutil
from getpass import getpass

def setup_database_config():
    """Interactive setup for database configuration"""
    
    print("🚀 Inventory Management System - Database Setup")
    print("=" * 50)
    
    # Check if .env already exists
    if os.path.exists('.env'):
        response = input("⚠️  .env file already exists. Overwrite? (y/N): ").lower()
        if response != 'y':
            print("❌ Setup cancelled.")
            return False
    
    # Copy template if it doesn't exist
    if not os.path.exists('.env.template'):
        print("❌ Error: .env.template file not found!")
        return False
    
    print("\n📝 Please provide your database configuration:")
    
    # Get database configuration
    db_host = input("Database Host (default: localhost): ").strip() or "localhost"
    db_user = input("Database User (default: root): ").strip() or "root"
    db_password = getpass("Database Password: ").strip()
    db_name = input("Database Name (default: inventory_db): ").strip() or "inventory_db"
    
    # Generate secret key
    import secrets
    secret_key = secrets.token_urlsafe(32)
    
    # Create .env content
    env_content = f"""# Database Configuration
DATABASE_URL=mysql://{db_user}:{db_password}@{db_host}/{db_name}

# MySQL Configuration (Alternative)
MYSQL_HOST={db_host}
MYSQL_USER={db_user}
MYSQL_PASSWORD={db_password}
MYSQL_DB={db_name}

# Security
SECRET_KEY={secret_key}

# Flask Configuration
FLASK_ENV=development
FLASK_DEBUG=True
"""
    
    # Write .env file
    try:
        with open('.env', 'w') as f:
            f.write(env_content)
        
        print("\n✅ .env file created successfully!")
        print("\n📋 Next steps:")
        print(f"1. Create the database: CREATE DATABASE {db_name};")
        print("2. Run the schema: mysql -u root -p inventory_db < database_schema.sql")
        print("3. (Optional) Load sample data: python init_db.py")
        print("4. Start the application: python run.py")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating .env file: {e}")
        return False

def main():
    if len(sys.argv) > 1 and sys.argv[1] in ['-h', '--help']:
        print(__doc__)
        return
    
    try:
        setup_database_config()
    except KeyboardInterrupt:
        print("\n❌ Setup interrupted by user.")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    main()
