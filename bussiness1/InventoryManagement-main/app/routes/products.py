from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from app.models import Product, Category, StockAdjustment, SaleItem, PurchaseItem
from app import db
from datetime import datetime
from decimal import Decimal

bp = Blueprint('products', __name__, url_prefix='/products')

@bp.route('/')
@login_required
def index():
    sort_by = request.args.get('sort_by', 'id')
    sort_order = request.args.get('sort_order', 'asc')
    valid_columns = ['id', 'name', 'category_id', 'purchase_price', 'selling_price', 'current_stock', 'created_at']
    if sort_by not in valid_columns:
        sort_by = 'id'
    if sort_order.lower() not in ['asc', 'desc']:
        sort_order = 'asc'
    query = Product.query.filter_by(business_id=current_user.business_id)
    if sort_by == 'category_id':
        query = query.join(Category).order_by(getattr(Category.name, sort_order)(), Product.name.asc())
    else:
        query = query.order_by(getattr(getattr(Product, sort_by), sort_order)())
    products = query.all()
    return render_template('products/index.html', products=products, sort_by=sort_by, sort_order=sort_order)

@bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    if request.method == 'POST':
        name = request.form.get('name')
        category_id = request.form.get('category_id')
        new_category = request.form.get('new_category')
        purchase_price = request.form.get('purchase_price')
        selling_price = request.form.get('selling_price')
        unit = request.form.get('unit')
        initial_stock = request.form.get('initial_stock', 0)
        min_stock_level = request.form.get('min_stock_level', 10)
        try:
            if category_id == 'other' and new_category:
                category = Category(name=new_category, business_id=current_user.business_id)
                db.session.add(category)
                db.session.commit()
                category_id = category.id
            next_number = (db.session.query(db.func.coalesce(db.func.max(Product.id), 0) + 1).filter_by(business_id=current_user.business_id).scalar())
            product = Product(
                name=name,
                category_id=category_id,
                purchase_price=purchase_price,
                selling_price=selling_price,
                unit=unit,
                current_stock=initial_stock,
                min_stock_level=min_stock_level,
                business_id=current_user.business_id
            )
            db.session.add(product)
            db.session.commit()
            if float(initial_stock) > 0:
                adjustment = StockAdjustment(
                    product_id=product.id,
                    adjustment_date=datetime.now().date(),
                    quantity=initial_stock,
                    reason='Initial stock',
                    user_id=current_user.id
                )
                db.session.add(adjustment)
                db.session.commit()
            flash('Product added successfully', 'success')
            return redirect(url_for('products.index'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error adding product: {str(e)}', 'danger')
    categories = Category.query.filter_by(business_id=current_user.business_id).order_by(Category.name).all()
    return render_template('products/create.html', categories=categories)

@bp.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    product = Product.query.filter_by(id=id, business_id=current_user.business_id).first()
    if not product:
        flash('Product not found', 'danger')
        return redirect(url_for('products.index'))
    if request.method == 'POST':
        product.name = request.form.get('name')
        product.category_id = request.form.get('category_id')
        product.purchase_price = request.form.get('purchase_price')
        product.selling_price = request.form.get('selling_price')
        product.unit = request.form.get('unit')
        product.min_stock_level = request.form.get('min_stock_level')
        try:
            db.session.commit()
            flash('Product updated successfully', 'success')
            return redirect(url_for('products.index'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating product: {str(e)}', 'danger')
    categories = Category.query.filter_by(business_id=current_user.business_id).order_by(Category.name).all()
    return render_template('products/edit.html', product=product, categories=categories)

@bp.route('/delete/<int:id>', methods=['POST'])
@login_required
def delete(id):
    product = Product.query.filter_by(id=id, business_id=current_user.business_id).first()
    if not product:
        flash('Product not found', 'danger')
        return redirect(url_for('products.index'))
    sale_count = SaleItem.query.filter_by(product_id=id).count()
    purchase_count = PurchaseItem.query.filter_by(product_id=id).count()
    if sale_count > 0 or purchase_count > 0:
        flash('Cannot delete product with existing sales or purchase records', 'danger')
        return redirect(url_for('products.index'))
    try:
        StockAdjustment.query.filter_by(product_id=id).delete()
        db.session.delete(product)
        db.session.commit()
        flash('Product deleted successfully', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting product: {str(e)}', 'danger')
    return redirect(url_for('products.index'))

@bp.route('/stock-adjustment/<int:id>', methods=['GET', 'POST'])
@login_required
def stock_adjustment(id):
    product = Product.query.filter_by(id=id, business_id=current_user.business_id).first()
    if not product:
        flash('Product not found', 'danger')
        return redirect(url_for('products.index'))
    if request.method == 'POST':
        quantity = float(request.form.get('quantity'))
        reason = request.form.get('reason')
        try:
            adjustment = StockAdjustment(
                product_id=id,
                adjustment_date=datetime.now().date(),
                quantity=quantity,
                reason=reason,
                user_id=current_user.id
            )
            db.session.add(adjustment)
            product.current_stock += Decimal(str(quantity))
            db.session.commit()
            flash('Stock adjustment added successfully', 'success')
            return redirect(url_for('inventory.index'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error adjusting stock: {str(e)}', 'danger')
    history = StockAdjustment.query.filter_by(product_id=id).order_by(StockAdjustment.created_at.desc()).all()
    return render_template('products/stock_adjustment.html', product=product, history=history)

@bp.route('/ledger/<int:product_id>')
@login_required
def ledger(product_id):
    conn = mysql.connection
    cursor = conn.cursor(pymysql.cursors.DictCursor)

    # Get product info
    cursor.execute('SELECT p.*, c.name as category_name FROM products p JOIN categories c ON p.category_id = c.id WHERE p.id = %s AND p.business_id = %s', (product_id, current_user.business_id))
    product = cursor.fetchone()
    if not product:
        flash('Product not found', 'danger')
        return redirect(url_for('products.index'))

    # Filters
    start_date = request.args.get('start_date', '')
    end_date = request.args.get('end_date', '')
    txn_type = request.args.get('txn_type', 'both')  # purchase, sale, both

    # Get all purchases for this product
    purchase_query = '''
        SELECT 'purchase' as txn_type, p.purchase_date as date, pi.quantity, pi.unit_price, p.reference_number, p.id as ref_id, s.name as supplier_name
        FROM purchase_items pi
        JOIN purchases p ON pi.purchase_id = p.id
        JOIN suppliers s ON p.supplier_id = s.id
        WHERE pi.product_id = %s AND p.business_id = %s
    '''
    purchase_params = [product_id, current_user.business_id]
    if start_date:
        purchase_query += ' AND p.purchase_date >= %s'
        purchase_params.append(start_date)
    if end_date:
        purchase_query += ' AND p.purchase_date <= %s'
        purchase_params.append(end_date)

    # Get all sales for this product
    sale_query = '''
        SELECT 'sale' as txn_type, s.sale_date as date, si.quantity, si.unit_price, s.invoice_number as reference_number, s.id as ref_id, c.name as customer_name
        FROM sale_items si
        JOIN sales s ON si.sale_id = s.id
        LEFT JOIN customers c ON s.customer_id = c.id
        WHERE si.product_id = %s AND s.business_id = %s
    '''
    sale_params = [product_id, current_user.business_id]
    if start_date:
        sale_query += ' AND s.sale_date >= %s'
        sale_params.append(start_date)
    if end_date:
        sale_query += ' AND s.sale_date <= %s'
        sale_params.append(end_date)

    # Fetch transactions based on txn_type
    txns = []
    if txn_type in ['both', 'purchase']:
        cursor.execute(purchase_query, purchase_params)
        txns += cursor.fetchall()
    if txn_type in ['both', 'sale']:
        cursor.execute(sale_query, sale_params)
        txns += cursor.fetchall()

    # Sort all transactions by date
    txns.sort(key=lambda x: x['date'])

    # Calculate running stock
    opening_stock = product['current_stock']
    closing_stock = opening_stock
    # To get opening stock, we need to subtract all purchases and add all sales after the last transaction
    for txn in reversed(txns):
        if txn['txn_type'] == 'purchase':
            opening_stock -= txn['quantity']
        elif txn['txn_type'] == 'sale':
            opening_stock += txn['quantity']
    # Now, walk forward to calculate stock after each transaction
    running_stock = opening_stock
    for txn in txns:
        txn['opening_stock'] = running_stock
        if txn['txn_type'] == 'purchase':
            txn['purchased'] = txn['quantity']
            txn['sold'] = ''
            running_stock += txn['quantity']
        else:
            txn['purchased'] = ''
            txn['sold'] = txn['quantity']
            running_stock -= txn['quantity']
        txn['closing_stock'] = running_stock

    cursor.close()
    return render_template('products/ledger.html', product=product, txns=txns, opening_stock=opening_stock, closing_stock=product['current_stock'], start_date=start_date, end_date=end_date, txn_type=txn_type)

@bp.route('/categories')
@login_required
def categories():
    categories = Category.query.filter_by(business_id=current_user.business_id).order_by(Category.name).all()
    return render_template('products/categories.html', categories=categories)

@bp.route('/categories/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_category(id):
    category = Category.query.filter_by(id=id, business_id=current_user.business_id).first()
    if not category:
        flash('Category not found', 'danger')
        return redirect(url_for('products.categories'))
    if request.method == 'POST':
        name = request.form.get('name')
        try:
            category.name = name
            db.session.commit()
            flash('Category updated successfully', 'success')
            return redirect(url_for('products.categories'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating category: {str(e)}', 'danger')
    return render_template('products/edit_category.html', category=category)

@bp.route('/categories/delete/<int:id>', methods=['POST'])
@login_required
def delete_category(id):
    category = Category.query.filter_by(id=id, business_id=current_user.business_id).first()
    if not category:
        flash('Category not found', 'danger')
        return redirect(url_for('products.categories'))
    try:
        db.session.delete(category)
        db.session.commit()
        flash('Category deleted successfully', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting category: {str(e)}', 'danger')
    return redirect(url_for('products.categories')) 