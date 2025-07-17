import pymysql
from config import Config

def test_connection():
    try:
        # Connect to the MySQL server
        connection = pymysql.connect(
            host=Config.MYSQL_HOST,
            user=Config.MYSQL_USER,
            password=Config.MYSQL_PASSWORD,
            database=Config.MYSQL_DB,
            cursorclass=pymysql.cursors.DictCursor
        )
        
        print("Successfully connected to MySQL!")
        
        # Check if we can execute a query
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1 AS test_result")
            result = cursor.fetchone()
            print("Query test result:", result)
            
        # Close the connection
        connection.close()
        print("Connection closed successfully")
        return True
        
    except Exception as e:
        print(f"Error connecting to MySQL: {e}")
        return False

if __name__ == "__main__":
    # First, try to create the database if it doesn't exist
    try:
        conn = pymysql.connect(
            host=Config.MYSQL_HOST,
            user=Config.MYSQL_USER,
            password=Config.MYSQL_PASSWORD
        )
        cursor = conn.cursor()
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {Config.MYSQL_DB}")
        conn.commit()
        cursor.close()
        conn.close()
        print(f"Database '{Config.MYSQL_DB}' created or already exists")
    except Exception as e:
        print(f"Could not create database: {e}")
    
    # Now test the connection
    test_connection() 