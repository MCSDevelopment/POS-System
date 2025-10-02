from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), nullable=False, unique=True, index=True)
    password_hash = db.Column(db.String(128), nullable=False)
    pin = db.Column(db.String(4), nullable=False)

    # Roles: customer, employee, admin
    role = db.Column(db.String(20), nullable=False, default="customer")

    __table_args__ = (
        db.UniqueConstraint('email', name='uq_user_email'),
    )

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def is_admin(self):
        return self.role == "admin"

    def is_employee(self):
        return self.role == "employee"

    def is_customer(self):
        return self.role == "customer"



class Product(db.Model): 
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    category = db.Column(db.String(50), nullable=False, default="General")
    sku = db.Column(db.String(6), nullable=False, default="N/A")

    stock = db.Column(db.Integer, nullable=False, default=0)
    last_restocked = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    price = db.Column(db.Float, nullable=False)
    image_url = db.Column(db.String(255), nullable=False)

    def __repr__(self):
        return f"<Product {self.name}>"


class Customer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, index=True)
    phone = db.Column(db.String(20), unique=True, index=True, nullable=False)  # used for loyalty lookup
    address = db.Column(db.String(255))
    loyalty_points = db.Column(db.Integer, default=0)  # tracks accumulated points
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    orders = db.relationship("Order", back_populates="customer", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Customer {self.name} | {self.phone} | Points: {self.loyalty_points}>"

    def add_points(self, amount):
        """Add loyalty points to this customer."""
        self.loyalty_points += amount

    def redeem_points(self, amount):
        """Redeem points if available."""
        if self.loyalty_points >= amount:
            self.loyalty_points -= amount
            return True
        return False



class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey("customer.id"), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    total_price = db.Column(db.Float, nullable=False, default=0.0)
    status = db.Column(db.String(50), default="pending")  # e.g., pending, completed, canceled

    customer = db.relationship("Customer", back_populates="orders")
    items = db.relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Order {self.id} - Customer {self.customer_id}>"


class OrderItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey("order.id"), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey("product.id"), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    price = db.Column(db.Float, nullable=False)  # snapshot of price at time of order

    order = db.relationship("Order", back_populates="items")
    product = db.relationship("Product")

    def __repr__(self):
        return f"<OrderItem {self.product_id} x {self.quantity}>"