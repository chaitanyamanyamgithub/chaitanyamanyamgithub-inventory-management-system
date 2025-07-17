from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from app.models import Supplier
from app import db

bp = Blueprint('suppliers', __name__, url_prefix='/suppliers')

@bp.route('/')
@login_required
def index():
    suppliers = Supplier.query.order_by(Supplier.name).all()
    return render_template('suppliers/index.html', suppliers=suppliers)

@bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    if request.method == 'POST':
        name = request.form.get('name')
        contact_person = request.form.get('contact_person')
        phone = request.form.get('phone')
        email = request.form.get('email')
        address = request.form.get('address')
        try:
            supplier = Supplier(name=name, contact_person=contact_person, phone=phone, email=email, address=address)
            db.session.add(supplier)
            db.session.commit()
            flash('Supplier added successfully', 'success')
            return redirect(url_for('suppliers.index'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error adding supplier: {str(e)}', 'danger')
    return render_template('suppliers/create.html')

@bp.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    supplier = Supplier.query.filter_by(id=id).first()
    if not supplier:
        flash('Supplier not found', 'danger')
        return redirect(url_for('suppliers.index'))
    if request.method == 'POST':
        supplier.name = request.form.get('name')
        supplier.contact_person = request.form.get('contact_person')
        supplier.phone = request.form.get('phone')
        supplier.email = request.form.get('email')
        supplier.address = request.form.get('address')
        try:
            db.session.commit()
            flash('Supplier updated successfully', 'success')
            return redirect(url_for('suppliers.index'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating supplier: {str(e)}', 'danger')
    return render_template('suppliers/edit.html', supplier=supplier)

@bp.route('/delete/<int:id>', methods=['POST'])
@login_required
def delete(id):
    supplier = Supplier.query.filter_by(id=id).first()
    if not supplier:
        flash('Supplier not found', 'danger')
        return redirect(url_for('suppliers.index'))
    try:
        db.session.delete(supplier)
        db.session.commit()
        flash('Supplier deleted successfully', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting supplier: {str(e)}', 'danger')
    return redirect(url_for('suppliers.index'))

@bp.route('/history/<int:id>')
@login_required
def history(id):
    supplier = Supplier.query.filter_by(id=id).first()
    if not supplier:
        flash('Supplier not found', 'danger')
        return redirect(url_for('suppliers.index'))
    
    # Get supplier purchase history
    purchases = supplier.purchases
    
    return render_template('suppliers/history.html', supplier=supplier, purchases=purchases) 