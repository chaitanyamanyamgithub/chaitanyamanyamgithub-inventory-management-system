import pymysql
import os
from dotenv import load_dotenv

load_dotenv()

def create_database():
    try:
        # Connect to MySQL server (without specifying database)
        connection = pymysql.connect(
            host=os.environ.get('MYSQL_HOST', 'localhost'),
            user=os.environ.get('MYSQL_USER', 'root'),
            password=os.environ.get('MYSQL_PASSWORD', ''),
            charset='utf8mb4'
        )
        
        cursor = connection.cursor()
        
        # Create database
        cursor.execute("CREATE DATABASE IF NOT EXISTS inventory_db")
        print("✅ Database 'inventory_db' created successfully!")
        
        # Use the database
        cursor.execute("USE inventory_db")
        
        # Read and execute the schema file
        with open('database_schema.sql', 'r', encoding='utf-8') as f:
            schema_content = f.read()
        
        # Split by semicolon and execute each statement
        statements = schema_content.split(';')
        
        for statement in statements:
            statement = statement.strip()
            if statement and not statement.startswith('--'):
                try:
                    cursor.execute(statement)
                except Exception as e:
                    if "already exists" not in str(e).lower():
                        print(f"Warning: {e}")
        
        connection.commit()
        print("✅ Database schema created successfully!")
        
        cursor.close()
        connection.close()
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    if create_database():
        print("\n🎉 Database setup completed!")
        print("Now you can run: python init_db.py")
    else:
        print("\n❌ Database setup failed!")
