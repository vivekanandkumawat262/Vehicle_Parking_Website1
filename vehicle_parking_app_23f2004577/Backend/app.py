from flask import Flask 
from applications.config import LocalDevelopmentConfig 
from applications.database import db 
from applications.models import User 
from applications.security import jwt 
from werkzeug.security import generate_password_hash
from flask_cors import CORS 
from applications.celery_init import celery_init_app

app = None 

def create_app():
    app = Flask(__name__)
    app.config.from_object(LocalDevelopmentConfig)
    db.init_app(app)
    jwt.init_app(app)
    # ✅ Allow frontend access (CORS fix)
    CORS(app, resources={r"*": {"origins": ["http://localhost:5173"]}}, supports_credentials=True)

    app.app_context().push()
    return app



app = create_app()
celery = celery_init_app(app)
celery.autodiscover_tasks()

from applications.routes import *

if __name__ == "__main__":
    with app.app_context():  # Important for Flask to access DB
        db.create_all()  # Create tables if they don't exist

        # Check if admin already exists
        admin = User.query.filter_by(username="admin").first()
        if not admin:
            # Add admin user
            admin_user = User(
                username="admin",
                email="admin@gmail.com",
                # password_hash=generate_password_hash("123456"),  # hash password
                password_hash="123456",  # hash password
                role="admin"
            )
            db.session.add(admin_user)
            db.session.commit()
            print("Admin user created successfully!")
        else:
            print("Admin already exists.")

    app.run(debug=True)