from flask import Flask, g, session, redirect, url_for, request
from flask_pymongo import PyMongo
from config import Config
from routes import auth_bp, admin_bp, user_bp
from services import AuthService, ProductService
from feature_flags import FeatureFlags

app = Flask(__name__)
app.config.from_object(Config)

# Initialize MongoDB
mongo = PyMongo(app)

# Setup feature flags
feature_flags = FeatureFlags(mongo)

# Create services
auth_service = AuthService(mongo)
product_service = ProductService(mongo, feature_flags)

# Register blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(user_bp)

@app.before_request
def before_request():
    # Add services to g object for access in routes
    g.mongo = mongo
    g.auth_service = auth_service
    g.product_service = product_service
    g.feature_flags = feature_flags
    
    # Add user to g if logged in
    g.user = session.get('user')

@app.route('/')
def index():
    return redirect(url_for('auth.login'))

if __name__ == '__main__':
    # Initialize feature flags in the database if they don't exist
    for flag_name, enabled in app.config['FEATURE_FLAGS'].items():
        feature_flags.update_flag(flag_name, enabled)
    
    app.run(debug=True)