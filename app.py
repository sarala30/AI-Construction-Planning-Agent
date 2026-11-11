import os
from datetime import timedelta
from flask import Flask, render_template, request, jsonify, redirect, url_for, session, abort, flash
import database
import ai_planner

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'buildmind-ai-secret-key-2026-concept2-login')
app.permanent_session_lifetime = timedelta(days=14)

# Initialize SQLite database on module import
database.init_db()

# List of open public endpoints that do not require login
PUBLIC_ENDPOINTS = {'login', 'register', 'forgot_password', 'auth_google', 'static'}

@app.before_request
def check_authentication():
    """Protect application routes while allowing public auth endpoints."""
    # Allow static assets and public auth endpoints
    if request.endpoint in PUBLIC_ENDPOINTS or request.path.startswith('/static/'):
        return None
    
    # Check if user is logged in
    if 'user_id' not in session:
        if request.path.startswith('/api/'):
            return jsonify({'success': False, 'message': 'Authentication required. Please sign in.'}), 401
        return redirect(url_for('login', next=request.path))

def get_current_user():
    user_id = session.get('user_id')
    if user_id:
        user = database.get_user_by_id(user_id)
        if user:
            return user
    return {
        'id': session.get('user_id', 1),
        'username': session.get('username', 'rajesh.sharma'),
        'full_name': session.get('full_name', 'Rajesh Sharma'),
        'role': session.get('user_role', 'Senior Project Director'),
        'initials': session.get('user_initials', 'RS')
    }

@app.context_processor
def inject_global_template_vars():
    return {
        'current_user': get_current_user(),
        'app_name': 'BuildMind AI',
        'app_tagline': 'Plan Smarter. Build Better.'
    }

# ================= AUTHENTICATION ROUTES (CONCEPT 2) ================= #

@app.route('/login', methods=['GET', 'POST'])
def login():
    # If already logged in, redirect to dashboard
    if 'user_id' in session:
        return redirect(url_for('dashboard'))

    error_message = None
    success_message = None
    
    if request.method == 'POST':
        is_json = request.is_json
        data = request.get_json() if is_json else request.form
        
        email = (data.get('email') or '').strip()
        password = data.get('password') or ''
        remember = data.get('remember') in [True, 'on', 'true', '1']

        if not email or not password:
            msg = "Please enter both your email address and password."
            if is_json:
                return jsonify({'success': False, 'message': msg}), 400
            error_message = msg
        else:
            user = database.authenticate_user(email, password)
            if user:
                # Set session
                session['user_id'] = user['id']
                session['username'] = user['username']
                session['full_name'] = user['full_name']
                session['user_role'] = user['role']
                session['user_initials'] = user['avatar_initials']
                if remember:
                    session.permanent = True
                else:
                    session.permanent = False

                next_url = request.args.get('next') or url_for('dashboard')
                if is_json:
                    return jsonify({'success': True, 'redirect_url': next_url, 'message': 'Sign in successful!'})
                return redirect(next_url)
            else:
                msg = "Invalid email address or password. Please verify your credentials."
                if is_json:
                    return jsonify({'success': False, 'message': msg}), 401
                error_message = msg

    return render_template('login.html', error=error_message, success=success_message)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))

    error_message = None
    if request.method == 'POST':
        is_json = request.is_json
        data = request.get_json() if is_json else request.form
        
        full_name = (data.get('full_name') or '').strip()
        email = (data.get('email') or '').strip()
        password = data.get('password') or ''
        confirm_password = data.get('confirm_password') or ''
        role = (data.get('role') or 'Project Engineer').strip()

        if not full_name or not email or not password:
            error_message = "All fields are required."
        elif '@' not in email or '.' not in email:
            error_message = "Please enter a valid email address."
        elif len(password) < 6:
            error_message = "Password must be at least 6 characters long."
        elif password != confirm_password:
            error_message = "Passwords do not match."
        else:
            user, err = database.create_user(full_name, email, password, role)
            if err:
                error_message = err
            else:
                session['user_id'] = user['id']
                session['username'] = user['username']
                session['full_name'] = user['full_name']
                session['user_role'] = user['role']
                session['user_initials'] = user['avatar_initials']
                if is_json:
                    return jsonify({'success': True, 'redirect_url': url_for('dashboard')})
                return redirect(url_for('dashboard'))

        if is_json and error_message:
            return jsonify({'success': False, 'message': error_message}), 400

    return render_template('register.html', error=error_message)

@app.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    message = None
    is_success = False
    
    if request.method == 'POST':
        is_json = request.is_json
        data = request.get_json() if is_json else request.form
        email = (data.get('email') or '').strip()
        new_password = data.get('new_password') or ''

        if not email:
            message = "Please enter your registered email address."
        elif not new_password or len(new_password) < 6:
            message = "Please provide a new password with at least 6 characters."
        else:
            success, msg = database.reset_user_password(email, new_password)
            is_success = success
            message = msg

        if is_json:
            return jsonify({'success': is_success, 'message': message}), (200 if is_success else 400)

    return render_template('forgot_password.html', message=message, is_success=is_success)

@app.route('/auth/google')
def auth_google():
    """Continue with Google authentication handler."""
    # Sign in as default user or create/link Google profile
    user = database.get_default_user()
    if user:
        session['user_id'] = user['id']
        session['username'] = user['username']
        session['full_name'] = user['full_name']
        session['user_role'] = user['role']
        session['user_initials'] = user['avatar_initials']
        session.permanent = True
    return redirect(url_for('dashboard'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# ================= APPLICATION CORE ROUTES ================= #

@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/dashboard')
def dashboard():
    user = get_current_user()
    stats = database.get_dashboard_stats(user['id'])
    projects = database.get_user_projects(user['id'])
    return render_template('dashboard.html', active_page='dashboard', stats=stats, projects=projects)

@app.route('/planner')
def planner():
    project_id = request.args.get('project_id', type=int)
    project_data = None
    if project_id:
        user = get_current_user()
        project_data = database.get_project_with_plan(project_id, user['id'])
    return render_template('planner.html', active_page='planner', initial_project=project_data)

@app.route('/projects')
def projects():
    user = get_current_user()
    projects_list = database.get_user_projects(user['id'])
    return render_template('projects.html', active_page='projects', projects=projects_list)

@app.route('/project/<int:project_id>')
def view_project(project_id):
    user = get_current_user()
    project_data = database.get_project_with_plan(project_id, user['id'])
    if not project_data:
        abort(404)
    return render_template('planner.html', active_page='planner', initial_project=project_data)

@app.route('/project/<int:project_id>/report')
def project_report(project_id):
    user = get_current_user()
    project_data = database.get_project_with_plan(project_id, user['id'])
    if not project_data:
        abort(404)
    return render_template('report_print.html', project=project_data)

# ================= API Endpoints ================= #

@app.route('/api/generate-plan', methods=['POST'])
def api_generate_plan():
    user = get_current_user()
    data = request.get_json() or {}
    
    # Validation of required inputs
    errors = []
    project_name = (data.get('project_name') or '').strip()
    construction_type = (data.get('construction_type') or '').strip()
    location = (data.get('location') or '').strip()
    plot_area = data.get('plot_area')
    builtup_area = data.get('builtup_area')
    floors = (data.get('floors') or '').strip()
    budget = data.get('budget')
    start_date = (data.get('start_date') or '').strip()
    completion_date = (data.get('completion_date') or '').strip()
    
    if not project_name:
        errors.append("Project Name is required.")
    if not construction_type:
        errors.append("Construction Type is required.")
    if not location:
        errors.append("Project Location is required.")
    
    try:
        plot_area = float(plot_area)
        if plot_area <= 0:
            errors.append("Plot Area must be a positive number.")
    except (TypeError, ValueError):
        errors.append("Valid Plot Area (in sq. ft.) is required.")
        
    try:
        builtup_area = float(builtup_area)
        if builtup_area <= 0:
            errors.append("Built-up Area must be a positive number.")
    except (TypeError, ValueError):
        errors.append("Valid Built-up Area (in sq. ft.) is required.")
        
    if not floors:
        errors.append("Number of Floors selection is required.")
        
    try:
        budget = float(budget)
        if budget <= 0:
            errors.append("Project Budget must be a positive number.")
    except (TypeError, ValueError):
        errors.append("Valid Project Budget (in ₹) is required.")
        
    if not start_date:
        errors.append("Expected Start Date is required.")
    if not completion_date:
        errors.append("Expected Completion Date is required.")
    if start_date and completion_date and start_date >= completion_date:
        errors.append("Expected Completion Date must be later than the Start Date.")
        
    if errors:
        return jsonify({
            'success': False,
            'errors': errors,
            'message': 'Please resolve the highlighted validation issues before generating the plan.'
        }), 400

    data['plot_area'] = plot_area
    data['builtup_area'] = builtup_area
    data['budget'] = budget
    data['bedrooms'] = int(data.get('bedrooms', 0) or 0)
    data['bathrooms'] = int(data.get('bathrooms', 0) or 0)
    
    try:
        generated_plan = ai_planner.generate_ai_construction_plan(data)
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f"Error generating construction plan: {str(e)}"
        }), 500

    project_id = data.get('project_id')
    try:
        saved_id = database.save_project_and_plan(
            user_id=user['id'],
            project_data=data,
            plan_data=generated_plan,
            project_id=project_id
        )
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f"Plan generated, but saving to database failed: {str(e)}"
        }), 500

    return jsonify({
        'success': True,
        'project_id': saved_id,
        'plan': generated_plan,
        'message': f"Construction plan for '{project_name}' generated and saved successfully!"
    })

@app.route('/api/project/<int:project_id>', methods=['GET'])
def api_get_project(project_id):
    user = get_current_user()
    data = database.get_project_with_plan(project_id, user['id'])
    if not data:
        return jsonify({'success': False, 'message': 'Project not found or access denied.'}), 404
    return jsonify({'success': True, 'project': data})

@app.route('/api/delete-project/<int:project_id>', methods=['POST', 'DELETE'])
def api_delete_project(project_id):
    user = get_current_user()
    success = database.delete_project(project_id, user['id'])
    if success:
        return jsonify({'success': True, 'message': 'Project deleted successfully.'})
    return jsonify({'success': False, 'message': 'Project not found or unauthorized.'}), 404

@app.route('/estimator')
@app.route('/cost-estimator')
@app.route('/timeline')
@app.route('/security')
@app.route('/launch-readiness')
@app.route('/assistant')
@app.route('/reports')
@app.route('/settings')
def feature_in_progress():
    endpoint = request.path.strip('/')
    titles = {
        'estimator': 'Material Estimator',
        'cost-estimator': 'Cost Estimator',
        'timeline': 'Master Timeline',
        'security': 'Security Centre',
        'launch-readiness': 'Launch Readiness',
        'assistant': 'AI Assistant',
        'reports': 'Executive Reports',
        'settings': 'Profile & Settings'
    }
    page_title = titles.get(endpoint, 'Feature Suite')
    return render_template('feature_placeholder.html', active_page=endpoint, page_title=page_title)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
