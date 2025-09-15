import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key'
    MONGO_URI = os.environ.get('MONGO_URI') or 'mongodb://localhost:27017/product_recommender'
    
    # Feature flag defaults - can be overridden in the database
    FEATURE_FLAGS = {
        'advanced_recommendations': False,  # Enhanced recommendation algorithm
        'image_upload': True,              # Allow image uploads for products
        'user_preferences': False,         # User preference tracking
        'admin_analytics': False,          # Analytics dashboard for admins
    }
