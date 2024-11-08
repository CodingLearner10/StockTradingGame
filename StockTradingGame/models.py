from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    balance = db.Column(db.Float, default=1000.0)
    stocks = db.relationship('StockOwnership', backref='owner')

class Stock(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    current_price = db.Column(db.Float, nullable=False)  # Ensure this column is defined

class StockOwnership(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    stock_name = db.Column(db.String(80), nullable=False)
    quantity = db.Column(db.Integer, default=0)

def add_initial_stocks():
    # Ensure the stocks match what you expect to use in your app
    initial_stocks = [
        Stock(name="CompanyA", current_price=100.0),
        Stock(name="CompanyB", current_price=150.0),
        Stock(name="CompanyC", current_price=200.0),
        Stock(name="CompanyD", current_price=250.0)
    ]
    
    for stock in initial_stocks:
        db.session.add(stock)
    db.session.commit()
