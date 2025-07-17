from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user
from datetime import datetime
from app.models import CompanyInfo, Product, Customer, Supplier, Sale, Purchase, Category
from app import db

bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    return redirect(url_for('auth.login'))

@bp.route('/dashboard')
@login_required
def dashboard():
    company_info = CompanyInfo.query.get(1)
    product_count = Product.query.filter_by(business_id=current_user.business_id).count()
    customer_count = Customer.query.count()
    supplier_count = Supplier.query.count()
    low_stock = (
        db.session.query(Product.id, Product.name, Product.current_stock, Product.min_stock_level, Category.name.label('category'))
        .join(Category)
        .filter(Product.current_stock <= Product.min_stock_level, Product.business_id == current_user.business_id)
        .order_by((Product.current_stock / Product.min_stock_level))
        .limit(5)
        .all()
    )
    recent_sales = (
        db.session.query(Sale.id, Sale.invoice_number, Sale.sale_date, Sale.total_amount, Customer.name.label('customer_name'))
        .outerjoin(Customer, Sale.customer_id == Customer.id)
        .filter(Sale.business_id == current_user.business_id)
        .order_by(Sale.sale_date.desc())
        .limit(5)
        .all()
    )
    recent_purchases = (
        db.session.query(Purchase.id, Purchase.reference_number, Purchase.purchase_date, Purchase.total_amount, Supplier.name.label('supplier_name'))
        .join(Supplier, Purchase.supplier_id == Supplier.id)
        .filter(Purchase.business_id == current_user.business_id)
        .order_by(Purchase.purchase_date.desc())
        .limit(5)
        .all()
    )
    return render_template(
        'dashboard.html',
        company_info=company_info,
        product_count=product_count,
        customer_count=customer_count,
        supplier_count=supplier_count,
        low_stock=low_stock,
        recent_sales=recent_sales,
        recent_purchases=recent_purchases,
        now=datetime.now()
    ) 