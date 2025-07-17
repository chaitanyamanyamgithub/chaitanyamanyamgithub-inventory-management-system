# Detailed Setup Instructions

## 1. Database Setup
Before running the application, you need to set up the MySQL database:

1. Open `config.py` and update the MySQL connection settings:
   ```python
   MYSQL_HOST = os.environ.get('MYSQL_HOST') or 'localhost'
   MYSQL_USER = os.environ.get('MYSQL_USER') or 'root' # Replace with your MySQL username
   MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD') or 'your_password_here' # Replace with your actual MySQL password
   MYSQL_DB = os.environ.get('MYSQL_DB') or 'inventory_db'
   ```

2. Create the database and load schema:
   - Open MySQL Command Line Client or MySQL Workbench
   - Run the following command to create the database:
     ```sql
     CREATE DATABASE IF NOT EXISTS inventory_db;
     ```
   - Import the database schema from the `database_schema.sql` file:
     ```
     mysql -u root -p inventory_db < database_schema.sql
     ```
     (Enter your MySQL password when prompted)

## 2. Python Virtual Environment
It's recommended to use a virtual environment to run the application:

1. Create a virtual environment:
   ```
   python -m venv venv
   ```

2. Activate the virtual environment:
   - Windows: `venv\Scripts\activate`
   - macOS/Linux: `source venv/bin/activate`

3. Install required packages:
   ```
   pip install -r requirements.txt
   pip install cryptography  # Required for MySQL authentication
   ```

## 3. Running the Application
After setting up the database and virtual environment:

1. Make sure the virtual environment is activated

2. Run the application:
   ```
   python run.py
   ```

3. Access the application in your web browser at: http://localhost:5000

4. Login with the default admin credentials:
   - Username: admin
   - Password: admin123

## 4. Troubleshooting

If you encounter database connection issues:
1. Verify MySQL is running
2. Check your MySQL password in `config.py`
3. Make sure the database exists
4. Test connection with the provided `test_db.py` script:
   ```
   python test_db.py
   ```

If you get dependency errors:
1. Make sure all packages in `requirements.txt` are installed
2. Try reinstalling specific packages that give errors
3. Ensure you're using Python 3.6+ version 