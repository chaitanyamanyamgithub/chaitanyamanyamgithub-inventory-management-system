from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify
from flask_login import login_required, current_user
from datetime import datetime
import json
from app.models import Sale, SaleItem, Customer, Product, Category, CompanyInfo
from app import db
from decimal import Decimal

bp = Blueprint('sales', __name__, url_prefix='/sales')

@bp.route('/')
@login_required
def index():
    start_date = request.args.get('start_date', '')
    end_date = request.args.get('end_date', '')
    customer_id = request.args.get('customer_id', '')
    search = request.args.get('search', '')
    sort_by = request.args.get('sort_by', 'sale_date')
    sort_order = request.args.get('sort_order', 'desc')
    valid_columns = ['id', 'sale_date', 'invoice_number', 'total_amount']
    if sort_by not in valid_columns:
        sort_by = 'sale_date'
    if sort_order.lower() not in ['asc', 'desc']:
        sort_order = 'desc'
    query = Sale.query.filter_by(business_id=current_user.business_id)
    if start_date:
        query = query.filter(Sale.sale_date >= start_date)
    if end_date:
        query = query.filter(Sale.sale_date <= end_date)
    if customer_id:
        query = query.filter(Sale.customer_id == customer_id)
    if search:
        query = query.join(Customer).filter((Sale.invoice_number.ilike(f'%{search}%')) | (Customer.name.ilike(f'%{search}%')))
    if sort_by == 'customer_name':
        query = query.join(Customer).order_by(getattr(Customer.name, sort_order)())
    else:
        query = query.order_by(getattr(getattr(Sale, sort_by), sort_order)())
    sales = query.all()
    customers = Customer.query.order_by(Customer.name).all()
    return render_template(
        'sales/index.html',
        sales=sales,
        customers=customers,
        filters={
            'start_date': start_date,
            'end_date': end_date,
            'customer_id': customer_id,
            'search': search
        },
        sort_by=sort_by,
        sort_order=sort_order
    )

@bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    if request.method == 'POST':
        customer_id = request.form.get('customer_id') or None
        sale_date = request.form.get('sale_date')
        notes = request.form.get('notes')
        items_json = request.form.get('items')
        total_amount = float(request.form.get('total_amount', 0))
        if not items_json:
            flash('No items in the sale', 'danger')
            return redirect(url_for('sales.create'))
        items = json.loads(items_json)
        if not items:
            flash('No items in the sale', 'danger')
            return redirect(url_for('sales.create'))
        try:
            today = datetime.now().strftime('%Y%m%d')
            last_sale = Sale.query.filter(Sale.invoice_number.like(f'INV-{today}-%')).order_by(Sale.id.desc()).first()
            last_num = 1
            if last_sale and last_sale.invoice_number:
                try:
                    last_num = int(last_sale.invoice_number.split('-')[2]) + 1
                except:
                    pass
            invoice_number = f'INV-{today}-{last_num:04d}'
            sale = Sale(
                customer_id=customer_id,
                invoice_number=invoice_number,
                sale_date=sale_date,
                total_amount=total_amount,
                notes=notes,
                user_id=current_user.id,
                business_id=current_user.business_id
            )
            db.session.add(sale)
            db.session.flush()  # Get sale.id
            for item in items:
                product_id = item['product_id']
                quantity = float(item['quantity'])
                unit_price = float(item['unit_price'])
                total_price = quantity * unit_price
                sale_item = SaleItem(
                    sale_id=sale.id,
                    product_id=product_id,
                    quantity=quantity,
                    unit_price=unit_price,
                    total_price=total_price
                )
                db.session.add(sale_item)
                # Decrement product stock
                product = Product.query.get(product_id)
                if product:
                    product.current_stock -= Decimal(str(quantity))
            db.session.commit()
            flash('Sale recorded successfully', 'success')
            return redirect(url_for('sales.view', id=sale.id))
        except Exception as e:
            db.session.rollback()
            flash(f'Error recording sale: {str(e)}', 'danger')
    customers = Customer.query.order_by(Customer.name).all()
    products = Product.query.filter(Product.current_stock > 0, Product.business_id == current_user.business_id).join(Category).order_by(Product.name).all()
    selected_customer_id = request.args.get('customer_id', '')
    return render_template(
        'sales/create.html',
        customers=customers,
        products=products,
        selected_customer_id=selected_customer_id,
        today=datetime.now().strftime('%Y-%m-%d')
    )

@bp.route('/view/<int:id>')
@login_required
def view(id):
    sale = Sale.query.filter_by(id=id, business_id=current_user.business_id).first()
    if not sale:
        flash('Sale not found', 'danger')
        return redirect(url_for('sales.index'))
    items = SaleItem.query.filter_by(sale_id=id).all()
    # Annotate sale with customer details
    if sale.customer_id:
        customer = Customer.query.filter_by(id=sale.customer_id).first()
        if customer:
            sale.customer_name = customer.name
            sale.customer_address = customer.address
            sale.customer_phone = customer.phone
    else:
        sale.customer_name = None
        sale.customer_address = None
        sale.customer_phone = None
    company_info = CompanyInfo.query.get(1)
    return render_template(
        'sales/view.html',
        sale=sale,
        items=items,
        company_info=company_info
    )

@bp.route('/delete/<int:id>', methods=['POST'])
@login_required
def delete(id):
    sale = Sale.query.filter_by(id=id, business_id=current_user.business_id).first()
    if not sale:
        flash('Sale not found', 'danger')
        return redirect(url_for('sales.index'))
    try:
        SaleItem.query.filter_by(sale_id=sale.id).delete()
        db.session.delete(sale)
        db.session.commit()
        flash('Sale deleted successfully', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting sale: {str(e)}', 'danger')
    return redirect(url_for('sales.index'))

@bp.route('/get-product/<int:id>')
@login_required
def get_product(id):
    product = Product.query.filter_by(id=id).first()
    if not product:
        return jsonify({'error': 'Product not found'}), 404
    return jsonify(product) 