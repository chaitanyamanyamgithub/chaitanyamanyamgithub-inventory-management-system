# Inventory Management System

A comprehensive web application for managing retail operations including sales, purchases, inventory management, customer and supplier management.

## 🚀 Features

- **User Authentication**: Secure login/logout system with role-based access
- **Sales Management**: Create and track sales transactions
- **Purchase Management**: Manage supplier purchases and inventory restocking
- **Inventory Tracking**: Real-time inventory levels with low stock alerts
- **Customer Management**: Maintain customer database and transaction history
- **Supplier Management**: Track supplier information and purchase history
- **Reporting & Analytics**: Generate reports for sales, purchases, and inventory
- **Multi-user Support**: Admin and staff user roles
- **Responsive Design**: Mobile-friendly interface

## 🛠️ Technology Stack

- **Frontend**: HTML5, CSS3, Bootstrap 5, JavaScript
- **Backend**: Python Flask
- **Database**: MySQL
- **Authentication**: Flask-Login
- **ORM**: SQLAlchemy

## 📋 Prerequisites

- Python 3.8 or higher
- MySQL Server 5.7 or higher
- pip (Python package manager)

## 🔧 Installation

### 1. Clone the Repository
```bash
git clone <your-repository-url>
cd inventory-management-system
```

### 2. Create Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Database Setup

#### Option A: Quick Setup (Recommended)
Run the interactive setup script:
```bash
python setup_db.py
```

#### Option B: Manual Setup
1. Create a MySQL database:
```sql
CREATE DATABASE inventory_db;
```

2. Configure environment variables:
```bash
# Copy the template
cp .env.template .env

# Edit .env with your database credentials
# Update MYSQL_USER, MYSQL_PASSWORD, etc.
```

### 5. Initialize Database Schema
```bash
# Run the schema to create tables
mysql -u root -p inventory_db < database_schema.sql
```

### 6. (Optional) Load Sample Data
```bash
python init_db.py
```

### 7. Run the Application
```bash
python run.py
```

Visit http://localhost:5000 in your browser.

## 👤 Default Login

- **Username**: admin
- **Password**: admin123

⚠️ **Important**: Change the default password after first login!

## 📁 Project Structure

```
inventory-management-system/
├── app/
│   ├── models/          # Database models
│   ├── routes/          # Route handlers
│   ├── templates/       # HTML templates
│   └── utils/           # Utility functions
├── config.py            # Application configuration
├── run.py              # Application entry point
├── requirements.txt    # Python dependencies
├── database_schema.sql # Database schema
└── init_db.py         # Sample data loader
```

## 🔒 Security Features

- Password hashing with bcrypt
- Session management
- CSRF protection
- Input validation and sanitization
- Role-based access control

## 📊 Database Schema

The system uses a normalized database design with the following main tables:
- Users (authentication and authorization)
- Products (inventory items)
- Categories (product categorization)
- Customers (customer information)
- Suppliers (supplier information)
- Sales (sales transactions)
- Purchases (purchase transactions)
- Company Info (business information)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

## 🆘 Support

If you encounter any issues or have questions, please create an issue in the repository.

## 🔮 Future Enhancements

- [ ] REST API endpoints
- [ ] Advanced reporting and analytics
- [ ] Email notifications
- [ ] Barcode scanning
- [ ] Multi-location support
- [ ] Export/Import functionality
- [ ] Advanced user permissions 