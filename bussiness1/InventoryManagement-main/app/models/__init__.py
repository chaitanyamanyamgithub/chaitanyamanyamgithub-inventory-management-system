# Import models here
from app import db
from app.models.user import User, Business
from app.models.product import Product, Category
from app.models.customer import Customer
from app.models.supplier import Supplier
from app.models.sales import Sale, SaleItem
from app.models.purchases import Purchase, PurchaseItem
from app.models.inventory import StockAdjustment
from app.models.company_info import CompanyInfo
# ... existing code ... 