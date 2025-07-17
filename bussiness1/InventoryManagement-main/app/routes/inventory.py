from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from app.models import Product, Category, PurchaseItem, Purchase, SaleItem, Sale, Supplier, Customer
from app import db
from collections import defaultdict
import datetime as dt

bp = Blueprint('inventory', __name__, url_prefix='/inventory')

@bp.route('/')
@login_required
def index():
    category_id = request.args.get('category_id', '')
    product_id = request.args.get('product_id', '')
    search = request.args.get('search', '')
    low_stock = request.args.get('low_stock', '')
    sort_by = request.args.get('sort_by', 'id')
    sort_order = request.args.get('sort_order', 'asc')
    valid_columns = ['id', 'name', 'category_id', 'current_stock', 'selling_price', 'purchase_price', 'is_low_stock']
    if sort_by not in valid_columns:
        sort_by = 'id'
    if sort_order.lower() not in ['asc', 'desc']:
        sort_order = 'asc'
    query = Product.query.filter_by(business_id=current_user.business_id)
    if category_id:
        query = query.filter(Product.category_id == category_id)
    if product_id:
        query = query.filter(Product.id == product_id)
    if search:
        query = query.join(Category).filter((Product.name.ilike(f'%{search}%')) | (Category.name.ilike(f'%{search}%')))
    if low_stock:
        query = query.filter(Product.current_stock <= Product.min_stock_level)
    if sort_by == 'category_id':
        query = query.join(Category).order_by(getattr(Category.name, sort_order)())
    elif sort_by == 'is_low_stock':
        query = query.order_by((Product.current_stock <= Product.min_stock_level).desc(), Product.name.asc())
    else:
        query = query.order_by(getattr(getattr(Product, sort_by), sort_order)())
    products = query.all()
    categories = Category.query.filter_by(business_id=current_user.business_id).order_by(Category.name).all()
    all_products = Product.query.filter_by(business_id=current_user.business_id).order_by(Product.name).all()
    return render_template(
        'inventory/index.html',
        products=products,
        categories=categories,
        all_products=all_products,
        filters={
            'category_id': category_id,
            'product_id': product_id,
            'low_stock': low_stock
        },
        sort_by=sort_by,
        sort_order=sort_order
    )

@bp.route('/ledger/<int:product_id>')
@login_required
def ledger(product_id):
    product = Product.query.filter_by(id=product_id, business_id=current_user.business_id).first()
    if not product:
        flash('Product not found', 'danger')
        return redirect(url_for('inventory.index'))
    start_date = request.args.get('start_date', '')
    end_date = request.args.get('end_date', '')
    purchase_query = PurchaseItem.query.join(Purchase).join(Supplier).filter(PurchaseItem.product_id == product_id)
    if start_date:
        purchase_query = purchase_query.filter(Purchase.purchase_date >= start_date)
    if end_date:
        purchase_query = purchase_query.filter(Purchase.purchase_date <= end_date)
    purchases = purchase_query.all()
    sale_query = SaleItem.query.join(Sale).outerjoin(Customer).filter(SaleItem.product_id == product_id)
    if start_date:
        sale_query = sale_query.filter(Sale.sale_date >= start_date)
    if end_date:
        sale_query = sale_query.filter(Sale.sale_date <= end_date)
    sales = sale_query.all()

    # Annotate purchases
    for p in purchases:
        p.party = p.purchase.supplier.name if p.purchase and p.purchase.supplier else ''
        p.ref_id = p.purchase.id if p.purchase else ''
        p.reference_number = p.purchase.reference_number if p.purchase else ''
    # Annotate sales
    for s in sales:
        s.party = s.sale.customer.name if s.sale and s.sale.customer else ''
        s.ref_id = s.sale.id if s.sale else ''
        s.reference_number = s.sale.invoice_number if s.sale else ''

    day_map = defaultdict(lambda: {'purchases': [], 'sales': []})
    all_dates = set()
    for p in purchases:
        d = p.purchase.purchase_date
        day_map[d]['purchases'].append(p)
        all_dates.add(d)
    for s in sales:
        d = s.sale.sale_date
        day_map[d]['sales'].append(s)
        all_dates.add(d)
    all_dates = sorted(all_dates)
    closing_stock = product.current_stock
    date_list = list(reversed(all_dates))
    stock_by_day = {}
    for d in date_list:
        total_purchased = sum(x.quantity for x in day_map[d]['purchases'])
        total_sold = sum(x.quantity for x in day_map[d]['sales'])
        opening_stock = closing_stock - total_purchased + total_sold
        stock_by_day[d] = {
            'date': d,
            'opening_stock': opening_stock,
            'total_purchased': total_purchased,
            'total_sold': total_sold,
            'closing_stock': closing_stock,
            'purchases': day_map[d]['purchases'],
            'sales': day_map[d]['sales']
        }
        closing_stock = opening_stock
    ledger_rows = [stock_by_day[d] for d in sorted(stock_by_day.keys())]
    return render_template('inventory/ledger.html', product=product, ledger_rows=ledger_rows, start_date=start_date, end_date=end_date) 