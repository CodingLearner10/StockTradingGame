# app.py
# app.py
from flask import Flask, render_template, redirect, url_for, request, session, flash
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from models import db, User, Stock, StockOwnership, add_initial_stocks

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///stocks.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = 'your_secret_key'

    # Initialize database and migration
    db.init_app(app)
    migrate = Migrate(app, db)

    return app

# Create the app instance
app = create_app()

# Set up the application context to create tables and add initial stocks
with app.app_context():
    db.create_all()  # Create the database tables
    add_initial_stocks()  # Call to add initial stocks

    
@app.route('/')
def home():
    return render_template('home.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            session['user_id'] = user.id
            return redirect(url_for('menu'))  # Redirect to the menu page
        else:
            flash('Login failed: User not found or incorrect password.')
    return render_template('login.html')

@app.route('/portfolio')
def portfolio():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user = User.query.get(session['user_id'])
    stock_ownership = StockOwnership.query.filter_by(user_id=user.id).all()
    return render_template('portfolio.html', stock_ownership=stock_ownership)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Optionally hash the password here before saving (recommended)
        hashed_password = password  # You should use a hashing function

        # Check if the username already exists
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            return "Username already exists. Please choose a different username."

        try:
            # Create a new user with a default balance
            new_user = User(username=username, password=hashed_password, balance=1000.0)  
            db.session.add(new_user)
            db.session.commit()
            return redirect(url_for('login'))  # Redirect to the login page after registration
        except Exception as e:
            db.session.rollback()  # Roll back the session in case of error
            return f"An error occurred during registration: {str(e)}"
    
    return render_template('register.html')

@app.route('/settings', methods=['GET', 'POST'])
def settings():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))  # Redirect to login if not authenticated

    user = User.query.get(user_id)

    if request.method == 'POST':
        # Handle form submission to change password or delete account
        if 'change_password' in request.form:
            new_password = request.form['new_password']
            user.password = new_password  # Update password (consider hashing in production)
            db.session.commit()
            return redirect(url_for('settings'))  # Redirect back to settings

        elif 'delete_account' in request.form:
            db.session.delete(user)  # Delete user account
            db.session.commit()
            session.pop('user_id', None)  # Remove user from session
            return redirect(url_for('register'))  # Redirect to register page

    return render_template('settings.html', user=user)

@app.route('/trade', methods=['GET', 'POST'])
def trade():
    if 'user_id' not in session:
        return redirect(url_for('login'))  # Redirect to login if not logged in

    if request.method == 'POST':
        action = request.form['action']
        stock_name = request.form['stock_name']
        quantity = int(request.form['quantity'])

        # Fetch the user data from the database
        user = User.query.get(session['user_id'])

        # Perform the buy/sell action based on the user's selection
        if action == 'buy':
            stock_price = get_stock_price(stock_name)  # Assume a function that gets the current stock price
            total_cost = stock_price * quantity
            if user.balance >= total_cost:
                # Update user's portfolio
                portfolio_item = StockOwnership.query.filter_by(user_id=user.id, stock_name=stock_name).first()
                if portfolio_item:
                    portfolio_item.quantity += quantity
                else:
                    new_portfolio_item = StockOwnership(user_id=user.id, stock_name=stock_name, quantity=quantity)
                    db.session.add(new_portfolio_item)

                # Deduct from user balance
                user.balance -= total_cost
                db.session.commit()
                flash(f"Bought {quantity} of {stock_name} for {total_cost}.", 'success')  # Success message
            else:
                flash('Not enough balance to complete this transaction.', 'error')  # Error message

        elif action == 'sell':
            portfolio_item = StockOwnership.query.filter_by(user_id=user.id, stock_name=stock_name).first()
            if portfolio_item and portfolio_item.quantity >= quantity:
                stock_price = get_stock_price(stock_name)  # Assume a function that gets the current stock price
                total_income = stock_price * quantity
                portfolio_item.quantity -= quantity

                # Remove stock from portfolio if quantity is 0
                if portfolio_item.quantity == 0:
                    db.session.delete(portfolio_item)

                # Add income to user balance
                user.balance += total_income
                db.session.commit()
                flash(f"Sold {quantity} of {stock_name} for {total_income}.", 'success')  # Success message
            else:
                flash('Not enough stocks to sell.', 'error')  # Error message

        # Redirect to the portfolio page after the transaction
        return redirect(url_for('portfolio'))

    return render_template('trade.html')




@app.route('/menu')
def menu():
    if 'user_id' not in session:
        return redirect(url_for('login'))  # Redirect to login if not logged in
    return render_template('menu.html')  # Render the menu template for logged-in users

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)


import sqlite3
from flask import g

# Function to get the database connection
def get_db():
    if not hasattr(g, 'db'):
        g.db = sqlite3.connect('stocks.db')  # Make sure 'stocks.db' is the correct path to your DB
    return g.db

# Function to fetch the stock price from the database
def get_stock_price(stock_name):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT price FROM stocks WHERE name = ?", (stock_name,))
    result = cursor.fetchone()  # Fetch the first matching result
    if result:
        return result[0]  # Return the price if found
    return None  # Return None if stock is not found

    return stock_prices.get(stock_name, 0.0)



