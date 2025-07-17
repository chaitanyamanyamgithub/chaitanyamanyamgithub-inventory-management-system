from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from app.models import Customer
from app import db

bp = Blueprint('customers', __name__, url_prefix='/customers')

@bp.route('/')
@login_required
def index():
    sort_by = request.args.get('sort_by', 'id')
    sort_order = request.args.get('sort_order', 'asc')
    valid_columns = ['id', 'name', 'phone', 'email', 'address', 'created_at']
    if sort_by not in valid_columns:
        sort_by = 'id'
    if sort_order.lower() not in ['asc', 'desc']:
        sort_order = 'asc'
    query = Customer.query.filter_by(business_id=current_user.business_id)
    if sort_order == 'asc':
        query = query.order_by(getattr(Customer, sort_by).asc())
    else:
        query = query.order_by(getattr(Customer, sort_by).desc())
    customers = query.all()
    return render_template('customers/index.html', 
                          customers=customers, 
                          sort_by=sort_by, 
                          sort_order=sort_order)

@bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    if request.method == 'POST':
        name = request.form.get('name')
        phone = request.form.get('phone')
        email = request.form.get('email')
        address = request.form.get('address')
        try:
            customer = Customer(name=name, phone=phone, email=email, address=address, business_id=current_user.business_id)
            db.session.add(customer)
            db.session.commit()
            flash('Customer added successfully', 'success')
            if 'from_sales' in request.form:
                return redirect(url_for('sales.create', customer_id=customer.id))
            return redirect(url_for('customers.index'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error adding customer: {str(e)}', 'danger')
    from_sales = request.args.get('from_sales', False)
    return render_template('customers/create.html', from_sales=from_sales)

@bp.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    customer = Customer.query.filter_by(id=id, business_id=current_user.business_id).first()
    if not customer:
        flash('Customer not found', 'danger')
        return redirect(url_for('customers.index'))
    if request.method == 'POST':
        customer.name = request.form.get('name')
        customer.phone = request.form.get('phone')
        customer.email = request.form.get('email')
        customer.address = request.form.get('address')
        try:
            db.session.commit()
            flash('Customer updated successfully', 'success')
            return redirect(url_for('customers.index'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating customer: {str(e)}', 'danger')
    return render_template('customers/edit.html', customer=customer)

@bp.route('/delete/<int:id>', methods=['POST'])
@login_required
def delete(id):
    customer = Customer.query.filter_by(id=id, business_id=current_user.business_id).first()
    if not customer:
        flash('Customer not found', 'danger')
        return redirect(url_for('customers.index'))
    try:
        # Check if customer has sales
        from app.models import Sale
        sale_count = Sale.query.filter_by(customer_id=id, business_id=current_user.business_id).count()
        if sale_count > 0:
            flash('Cannot delete customer with existing sales records', 'danger')
            return redirect(url_for('customers.index'))
        db.session.delete(customer)
        db.session.commit()
        flash('Customer deleted successfully', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting customer: {str(e)}', 'danger')
    return redirect(url_for('customers.index'))

@bp.route('/history/<int:id>')
@login_required
def history(id):
    customer = Customer.query.filter_by(id=id, business_id=current_user.business_id).first()
    if not customer:
        flash('Customer not found', 'danger')
        return redirect(url_for('customers.index'))
    from app.models import Sale, SaleItem
    sales = (
        db.session.query(Sale, db.func.count(SaleItem.id).label('item_count'))
        .join(SaleItem, Sale.id == SaleItem.sale_id)
        .filter(Sale.customer_id == id, Sale.business_id == current_user.business_id)
        .group_by(Sale.id)
        .order_by(Sale.sale_date.desc())
        .all()
    )
    return render_template('customers/history.html', customer=customer, sales=sales) 