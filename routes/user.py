from flask import Blueprint, request, render_template, session, g, flash

user_bp = Blueprint('user', __name__, url_prefix='/user')

# Middleware to check if user is logged in
@user_bp.before_request
def check_user():
    if 'user' not in session:
        return redirect(url_for('auth.login'))

@user_bp.route('/')
def dashboard():
    return render_template('user/dashboard.html')

@user_bp.route('/search', methods=['GET'])
def search():
    search_term = request.args.get('q', '')
    
    if not search_term:
        return render_template('user/search.html', products=[], recommendations=[])
    
    # Search for products
    products = g.product_service.search_products(search_term)
    
    # Get recommendations
    recommendations = g.product_service.get_recommendations(search_term, session.get('user'))
    
    return render_template('user/search.html', 
                          products=products, 
                          recommendations=recommendations,
                          search_term=search_term)