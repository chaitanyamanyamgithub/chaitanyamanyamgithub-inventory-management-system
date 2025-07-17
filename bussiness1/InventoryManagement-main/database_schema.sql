-- Database Schema for Inventory Management System

CREATE DATABASE IF NOT EXISTS inventory_db;
USE inventory_db;

-- Businesses Table (Create this first)
CREATE TABLE IF NOT EXISTS businesses (
    id INT AUTO_INCREMENT PRIMARY KEY,
    business_name VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL,
    phone VARCHAR(20) NOT NULL,
    address TEXT NOT NULL,
    gst_number VARCHAR(30) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Users Table
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    full_name VARCHAR(100) NOT NULL,
    email VARCHAR(100),
    role ENUM('admin', 'staff') NOT NULL DEFAULT 'staff',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    business_id INT NULL,
    FOREIGN KEY (business_id) REFERENCES businesses(id)
);

-- Create default admin user (password: admin123)
INSERT INTO users (username, password, full_name, role) 
VALUES ('admin', '$2b$12$sZlZJm57KJxIGHBuiJW/YOCSRrpS7g1Jl5NfFqO.YId1AYl9B.R4a', 'Admin User', 'admin')
ON DUPLICATE KEY UPDATE username = username;

-- Product Categories
CREATE TABLE IF NOT EXISTS categories (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE,
    description TEXT
);

-- Insert some default categories
INSERT INTO categories (name) VALUES 
('General')
ON DUPLICATE KEY UPDATE name = name;

-- Remove this problematic section
-- SELECT* FROM CATEGORIES;
-- DELETE FROM  CATEGORIES
-- WHERE NAME IN('Electronics','Clothing','Books','Food','Home');

-- Products Table
CREATE TABLE IF NOT EXISTS products (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    category_id INT NOT NULL,
    purchase_price DECIMAL(10, 2) NOT NULL,
    selling_price DECIMAL(10, 2) NOT NULL,
    unit VARCHAR(20) NOT NULL,
    current_stock DECIMAL(10, 2) DEFAULT 0,
    min_stock_level DECIMAL(10, 2) DEFAULT 10,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (category_id) REFERENCES categories(id)
);

-- Customers Table
CREATE TABLE IF NOT EXISTS customers (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    phone VARCHAR(20),
    email VARCHAR(100),
    address TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Suppliers Table
CREATE TABLE IF NOT EXISTS suppliers (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    contact_person VARCHAR(100),
    phone VARCHAR(20),
    email VARCHAR(100),
    address TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Sales Header Table
CREATE TABLE IF NOT EXISTS sales (
    id INT AUTO_INCREMENT PRIMARY KEY,
    customer_id INT,
    invoice_number VARCHAR(20) NOT NULL UNIQUE,
    sale_date DATE NOT NULL,
    total_amount DECIMAL(10, 2) NOT NULL,
    notes TEXT,
    user_id INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES customers(id),
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Sales Details Table
CREATE TABLE IF NOT EXISTS sale_items (
    id INT AUTO_INCREMENT PRIMARY KEY,
    sale_id INT NOT NULL,
    product_id INT NOT NULL,
    quantity DECIMAL(10, 2) NOT NULL,
    unit_price DECIMAL(10, 2) NOT NULL,
    total_price DECIMAL(10, 2) NOT NULL,
    FOREIGN KEY (sale_id) REFERENCES sales(id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(id)
);

-- Purchases Header Table
CREATE TABLE IF NOT EXISTS purchases (
    id INT AUTO_INCREMENT PRIMARY KEY,
    supplier_id INT NOT NULL,
    reference_number VARCHAR(20) NOT NULL,
    purchase_date DATE NOT NULL,
    total_amount DECIMAL(10, 2) NOT NULL,
    notes TEXT,
    user_id INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (supplier_id) REFERENCES suppliers(id),
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Purchases Details Table
CREATE TABLE IF NOT EXISTS purchase_items (
    id INT AUTO_INCREMENT PRIMARY KEY,
    purchase_id INT NOT NULL,
    product_id INT NOT NULL,
    quantity DECIMAL(10, 2) NOT NULL,
    unit_price DECIMAL(10, 2) NOT NULL,
    total_price DECIMAL(10, 2) NOT NULL,
    FOREIGN KEY (purchase_id) REFERENCES purchases(id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(id)
);

-- Stock Adjustments Table
CREATE TABLE IF NOT EXISTS stock_adjustments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    product_id INT NOT NULL,
    adjustment_date DATE NOT NULL,
    quantity DECIMAL(10, 2) NOT NULL,
    reason TEXT NOT NULL,
    user_id INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id) REFERENCES products(id),
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Company Information
CREATE TABLE IF NOT EXISTS company_info (
    id INT PRIMARY KEY DEFAULT 1,
    company_name VARCHAR(100) NOT NULL,
    address TEXT,
    phone VARCHAR(20),
    email VARCHAR(100),
    website VARCHAR(100),
    tax_id VARCHAR(50),
    logo_path VARCHAR(255),
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Insert default company info
INSERT INTO company_info (company_name, address, phone, email) 
VALUES ('Your Business Name', 'Your Business Address', '+1234567890', 'contact@yourbusiness.com')
ON DUPLICATE KEY UPDATE company_name = company_name;

UPDATE company_info
SET company_name = 'Your Business Name',
    address='Your Business Address',
    phone='+1234567890',
    email='contact@yourbusiness.com'
WHERE id = 1;

-- Note: Businesses table is already created at the top

-- TRIGGERS

-- Trigger to update product stock after purchase
DELIMITER //
CREATE TRIGGER after_purchase_insert
AFTER INSERT ON purchase_items
FOR EACH ROW
BEGIN
    UPDATE products
    SET current_stock = current_stock + NEW.quantity
    WHERE id = NEW.product_id;
END //
DELIMITER ;

-- Trigger to update product stock after purchase update
DELIMITER //
CREATE TRIGGER after_purchase_update
AFTER UPDATE ON purchase_items
FOR EACH ROW
BEGIN
    UPDATE products
    SET current_stock = current_stock - OLD.quantity + NEW.quantity
    WHERE id = NEW.product_id;
END //
DELIMITER ;

-- Trigger to update product stock after purchase delete
DELIMITER //
CREATE TRIGGER after_purchase_delete
AFTER DELETE ON purchase_items
FOR EACH ROW
BEGIN
    UPDATE products
    SET current_stock = current_stock - OLD.quantity
    WHERE id = OLD.product_id;
END //
DELIMITER ;

-- Trigger to update product stock after sale
DELIMITER //
CREATE TRIGGER after_sale_insert
AFTER INSERT ON sale_items
FOR EACH ROW
BEGIN
    UPDATE products
    SET current_stock = current_stock - NEW.quantity
    WHERE id = NEW.product_id;
END //
DELIMITER ;

-- Trigger to update product stock after sale update
DELIMITER //
CREATE TRIGGER after_sale_update
AFTER UPDATE ON sale_items
FOR EACH ROW
BEGIN
    UPDATE products
    SET current_stock = current_stock + OLD.quantity - NEW.quantity
    WHERE id = NEW.product_id;
END //
DELIMITER ;

-- Trigger to update product stock after sale delete
DELIMITER //
CREATE TRIGGER after_sale_delete
AFTER DELETE ON sale_items
FOR EACH ROW
BEGIN
    UPDATE products
    SET current_stock = current_stock + OLD.quantity
    WHERE id = OLD.product_id;
END //
DELIMITER ;

-- Trigger to update product stock after manual adjustment
DELIMITER //
CREATE TRIGGER after_adjustment_insert
AFTER INSERT ON stock_adjustments
FOR EACH ROW
BEGIN
    UPDATE products
    SET current_stock = current_stock + NEW.quantity
    WHERE id = NEW.product_id;
END //
DELIMITER ; 