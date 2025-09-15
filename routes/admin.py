from flask import Blueprint, request, render_template, redirect, url_for, session, g, flash
from werkzeug.utils import secure_filename
import os

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

# Middleware to check if user is admin
@admin_bp.before_request
def check_admin():
    user = session.get('user')
    if not user or user.get('role') != 'admin':
        flash('Access denied. Admin privileges required.', 'danger')
        return redirect(url_for('auth.login'))

@admin_bp.route('/')
def dashboard():
    # Get all products for the admin dashboard
    products = g.product_service.get_products()
    
    # Check if the analytics feature is enabled
    show_analytics = g.feature_flags.is_enabled('admin_analytics', session.get('user'))
    
    return render_template('admin/dashboard.html', 
                           products=products, 
                           show_analytics=show_analytics)

@admin_bp.route('/add_product', methods=['GET', 'POST'])
def add_product():
    if request.method == 'POST':
        name = request.form.get('name')
        cost = float(request.form.get('cost'))
        category = request.form.get('category')
        description = request.form.get('description', '')
        
        # Handle image upload if the feature is enabled
        image_url = request.form.get('image_url', '')
        if g.feature_flags.is_enabled('image_upload', session.get('user')) and 'image' in request.files:
            file = request.files['image']
            if file.filename:
                filename = secure_filename(file.filename)
                # In a real app, you'd save the file and set the URL
                # For simplicity, we'll just use the form URL
                # file.save(os.pathi wa.join(app.config['UPLOAD_FOLDER'], filename))
                # image_url = url_for('static', filename=f'uploads/{filename}')
        
        product = g.product_service.add_product(name, cost, image_url, category, description)
        flash(f'Product "{name}" added successfully!', 'success')
        return redirect(url_for('admin.dashboard'))
    
    return render_template('admin/add_product.html', 
                          image_upload_enabled=g.feature_flags.is_enabled('image_upload', session.get('user')))

@admin_bp.route('/feature_flags', methods=['GET', 'POST'])
def manage_feature_flags():
    if request.method == 'POST':
        flag_name = request.form.get('flag_name')
        enabled = request.form.get('enabled') == 'true'
        
        # Update the feature flag
        g.feature_flags.update_flag(flag_name, enabled)
        flash(f'Feature flag "{flag_name}" updated successfully!', 'success')
        
    # Get all feature flags
    flags = g.feature_flags.flags
    return render_template('admin/feature_flags.html', flags=flags)