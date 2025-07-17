# Inventory Management System - Installation Guide

This guide will walk you through the process of setting up and running the Inventory Management System.

## Prerequisites

- Python 3.8 or higher
- MySQL Server 5.7 or higher
- pip (Python package manager)

## Installation Steps

### 1. Clone or Download the Repository

```bash
git clone <repository-url>
cd inventory-management-system
```

### 2. Create a Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/macOS
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure MySQL Database

Make sure your MySQL server is running and create a database:

```sql
CREATE DATABASE inventory_db;
```

Update the database connection details in `config.py` if needed:

```python
# MySQL Database configuration
MYSQL_HOST = 'localhost'
MYSQL_USER = 'root'
MYSQL_PASSWORD = 'password'
MYSQL_DB = 'inventory_db'
```

### 5. Initialize the Database

Run the SQL script to create tables:

```bash
# Connect to MySQL and run the schema
mysql -u root -p inventory_db < database_schema.sql
```

### 6. (Optional) Load Sample Data

If you want to work with sample data, run the initialization script:

```bash
python init_db.py
```

### 7. Run the Application

```bash
python run.py
```

The application will start running at http://localhost:5000.

## Default Login Credentials

- **Username:** admin
- **Password:** admin123

## Application Structure

- `app/` - Main application directory
  - `models/` - Database models
  - `routes/` - Route handlers
  - `templates/` - HTML templates
  - `__init__.py` - Application initialization
- `config.py` - Configuration settings
- `database_schema.sql` - Database schema
- `init_db.py` - Sample data generator
- `run.py` - Application entry point

## Troubleshooting

### Database Connection Issues

If you encounter database connection issues, verify:

1. MySQL server is running
2. Database credentials in `config.py` are correct
3. The database `inventory_db` exists
4. The MySQL user has appropriate permissions

### Module Import Errors

If you encounter any module import errors, ensure:

1. The virtual environment is activated
2. All dependencies are installed correctly

## Next Steps

After installation, you can:

1. Access the dashboard at http://localhost:5000
2. Add your company information
3. Start managing your inventory, sales, and purchases 