from app import create_app, db  # Ensure you have the create_app function in app.py

# Create the Flask application instance
app = create_app()

with app.app_context():  # Create an application context
    # Drop all tables
    db.drop_all()

    # Create new tables
    db.create_all()

    print("Database has been reset.")
