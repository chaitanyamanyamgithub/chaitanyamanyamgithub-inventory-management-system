from flask import Flask, render_template
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

db = SQLAlchemy(app)

login_manager = LoginManager(app)
login_manager.login_view = 'auth.login'

from app.routes import auth, main, sales, purchases, products, customers, suppliers, inventory

app.register_blueprint(auth.bp)
app.register_blueprint(main.bp)
app.register_blueprint(sales.bp)
app.register_blueprint(purchases.bp)
app.register_blueprint(products.bp)
app.register_blueprint(customers.bp)
app.register_blueprint(suppliers.bp)
app.register_blueprint(inventory.bp)

@app.errorhandler(404)
def page_not_found(e):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('errors/500.html'), 500

@app.context_processor
def inject_business_info():
    business_info = None
    try:
        from app.models.user import Business  # Adjust import as needed
        business_info = db.session.query(Business).order_by(Business.id.desc()).first()
    except Exception:
        business_info = None
    return dict(business_info=business_info) 