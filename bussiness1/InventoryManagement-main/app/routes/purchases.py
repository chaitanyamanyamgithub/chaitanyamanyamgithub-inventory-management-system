from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify
from flask_login import login_required, current_user
from datetime import datetime
import json
from app.models import Purchase, PurchaseItem, Supplier, Product, Category, CompanyInfo
from app import db
from decimal import Decimal

bp = Blueprint('purchases', __name__, url_prefix='/purchases')

@bp.route('/')
@login_required
def index():
    start_date = request.args.get('start_date', '')
    end_date = request.args.get('end_date', '')
    supplier_id = request.args.get('supplier_id', '')
    search = request.args.get('search', '')
    sort_by = request.args.get('sort_by', 'purchase_date')
    sort_order = request.args.get('sort_order', 'desc')
    valid_columns = ['id', 'purchase_date', 'reference_number', 'total_amount']
    if sort_by not in valid_columns:
        sort_by = 'purchase_date'
    if sort_order.lower() not in ['asc', 'desc']:
        sort_order = 'desc'
    query = Purchase.query.filter_by(business_id=current_user.business_id)
    if start_date:
        query = query.filter(Purchase.purchase_date >= start_date)
    if end_date:
        query = query.filter(Purchase.purchase_date <= end_date)
    if supplier_id:
        query = query.filter(Purchase.supplier_id == supplier_id)
    if search:
        query = query.join(Supplier).filter((Purchase.reference_number.ilike(f'%{search}%')) | (Supplier.name.ilike(f'%{search}%')))
    if sort_by == 'supplier_name':
        query = query.join(Supplier).order_by(getattr(Supplier.name, sort_order)())
    else:
        query = query.order_by(getattr(getattr(Purchase, sort_by), sort_order)())
    purchases = query.all()
    suppliers = Supplier.query.order_by(Supplier.name).all()
    all_products = Product.query.filter_by(business_id=current_user.business_id).order_by(Product.name).all()
    return render_template(
        'purchases/index.html',
        purchases=purchases,
        suppliers=suppliers,
        filters={
            'start_date': start_date,
            'end_date': end_date,
            'supplier_id': supplier_id,
            'search': search
        },
        sort_by=sort_by,
        sort_order=sort_order
    )

@bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    if request.method == 'POST':
        supplier_id = request.form.get('supplier_id')
        purchase_date = request.form.get('purchase_date')
        reference_number = request.form.get('reference_number')
        notes = request.form.get('notes')
        items_json = request.form.get('items')
        total_amount = float(request.form.get('total_amount', 0))
        if not items_json:
            flash('No items in the purchase', 'danger')
            return redirect(url_for('purchases.create'))
        items = json.loads(items_json)
        if not items:
            flash('No items in the purchase', 'danger')
            return redirect(url_for('purchases.create'))
        try:
            purchase = Purchase(
                supplier_id=supplier_id,
                reference_number=reference_number,
                purchase_date=purchase_date,
                total_amount=total_amount,
                notes=notes,
                user_id=current_user.id,
                business_id=current_user.business_id
            )
            db.session.add(purchase)
            db.session.flush()  # Get purchase.id
            for item in items:
                product_id = item['product_id']
                quantity = float(item['quantity'])
                unit_price = float(item['unit_price'])
                total_price = quantity * unit_price
                purchase_item = PurchaseItem(
                    purchase_id=purchase.id,
                    product_id=product_id,
                    quantity=quantity,
                    unit_price=unit_price,
                    total_price=total_price
                )
                db.session.add(purchase_item)
                # Update product stock
                product = Product.query.get(product_id)
                if product:
                    product.current_stock += Decimal(str(quantity))
            db.session.commit()
            flash('Purchase recorded successfully', 'success')
            return redirect(url_for('purchases.view', id=purchase.id))
        except Exception as e:
            db.session.rollback()
            flash(f'Error recording purchase: {str(e)}', 'danger')
    suppliers = Supplier.query.order_by(Supplier.name).all()
    products = Product.query.filter_by(business_id=current_user.business_id).join(Category).order_by(Product.name).all()
    selected_supplier_id = request.args.get('supplier_id', '')
    return render_template(
        'purchases/create.html',
        suppliers=suppliers,
        products=products,
        selected_supplier_id=selected_supplier_id,
        today=datetime.now().strftime('%Y-%m-%d')
    )

@bp.route('/view/<int:id>')
@login_required
def view(id):
    purchase = Purchase.query.filter_by(id=id, business_id=current_user.business_id).first()
    if not purchase:
        flash('Purchase not found', 'danger')
        return redirect(url_for('purchases.index'))
    items = PurchaseItem.query.filter_by(purchase_id=id).all()
    # Fetch business info for the current user
    company_info = current_user.business
    return render_template(
        'purchases/view.html',
        purchase=purchase,
        items=items,
        company_info=company_info
    )

@bp.route('/delete/<int:id>', methods=['POST'])
@login_required
def delete(id):
    purchase = Purchase.query.filter_by(id=id, business_id=current_user.business_id).first()
    if not purchase:
        flash('Purchase not found', 'danger')
        return redirect(url_for('purchases.index'))
    try:
        PurchaseItem.query.filter_by(purchase_id=purchase.id).delete()
        db.session.delete(purchase)
        db.session.commit()
        flash('Purchase deleted successfully', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting purchase: {str(e)}', 'danger')
    return redirect(url_for('purchases.index'))

@bp.route('/get-product/<int:id>')
@login_required
def get_product(id):
    product = Product.query.filter_by(id=id).first()
    if not product:
        return jsonify({'error': 'Product not found'}), 404
    return jsonify(product.to_dict()) 