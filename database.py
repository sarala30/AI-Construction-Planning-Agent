import sqlite3
import json
import os
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'buildmind.db')

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def init_db():
    conn = get_connection()
    try:
        cursor = conn.cursor()
        
        # Users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                full_name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT,
                role TEXT NOT NULL DEFAULT 'Project Engineer',
                avatar_initials TEXT DEFAULT 'RS',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Check if password_hash column exists (for backward compatibility)
        cursor.execute("PRAGMA table_info(users)")
        columns = [col['name'] for col in cursor.fetchall()]
        if 'password_hash' not in columns:
            cursor.execute("ALTER TABLE users ADD COLUMN password_hash TEXT")

        # Projects table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS projects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                project_name TEXT NOT NULL,
                construction_type TEXT NOT NULL,
                location TEXT NOT NULL,
                plot_area REAL NOT NULL,
                builtup_area REAL NOT NULL,
                floors TEXT NOT NULL,
                bedrooms INTEGER DEFAULT 0,
                bathrooms INTEGER DEFAULT 0,
                budget REAL NOT NULL,
                start_date TEXT NOT NULL,
                completion_date TEXT NOT NULL,
                ai_options TEXT NOT NULL,
                status TEXT DEFAULT 'Active',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
            )
        ''')
        
        # Plans table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS plans (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER NOT NULL,
                summary TEXT NOT NULL,
                phases TEXT NOT NULL,
                materials TEXT NOT NULL,
                budget_breakdown TEXT NOT NULL,
                timeline TEXT NOT NULL,
                risk_analysis TEXT NOT NULL,
                selected_options TEXT NOT NULL,
                raw_ai_notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (project_id) REFERENCES projects (id) ON DELETE CASCADE
            )
        ''')
        
        # Create default demo user if not exists or ensure password_hash is set
        default_email = 'rajesh.sharma@buildmind.ai'
        default_pwd_hash = generate_password_hash('password123')
        
        cursor.execute('SELECT id, password_hash FROM users WHERE email = ? OR username = ?', (default_email, 'rajesh.sharma'))
        user = cursor.fetchone()
        if not user:
            cursor.execute('''
                INSERT INTO users (username, full_name, email, password_hash, role, avatar_initials)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', ('rajesh.sharma', 'Rajesh Sharma', default_email, default_pwd_hash, 'Senior Project Director', 'RS'))
            user_id = cursor.lastrowid
            seed_sample_project(cursor, user_id)
        else:
            if not user['password_hash']:
                cursor.execute('UPDATE users SET password_hash = ? WHERE id = ?', (default_pwd_hash, user['id']))
        
        conn.commit()
    finally:
        conn.close()

def seed_sample_project(cursor, user_id):
    project_name = "Skyline Heights Phase 1"
    construction_type = "Residential"
    location = "Whitefield, Bengaluru"
    plot_area = 4500.0
    builtup_area = 6800.0
    floors = "G + 2 Floors"
    bedrooms = 4
    bathrooms = 4
    budget = 14500000.0
    start_date = "2026-03-01"
    completion_date = "2027-02-28"
    ai_options = json.dumps([
        "Construction Planning", "Material Requirements", "Budget Estimation",
        "Labour Requirements", "Construction Timeline", "Risk Analysis", "Resource Planning"
    ])
    
    cursor.execute('''
        INSERT INTO projects (
            user_id, project_name, construction_type, location, plot_area, builtup_area,
            floors, bedrooms, bathrooms, budget, start_date, completion_date, ai_options, status
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (user_id, project_name, construction_type, location, plot_area, builtup_area,
          floors, bedrooms, bathrooms, budget, start_date, completion_date, ai_options, 'Active'))
    
    project_id = cursor.lastrowid
    
    summary = json.dumps({
        "project_name": project_name,
        "construction_type": construction_type,
        "total_area": builtup_area,
        "plot_area": plot_area,
        "floors": floors,
        "location": location,
        "estimated_budget": budget,
        "cost_per_sqft": round(budget / builtup_area, 2),
        "total_duration_weeks": 52
    })
    
    phases = json.dumps([
        {"name": "Site preparation", "duration": "3 weeks", "days": 21, "status": "Completed", "progress": 100, "details": "Site clearing, leveling, boundary demarcation, water/power temporary lines."},
        {"name": "Foundation", "duration": "5 weeks", "days": 35, "status": "In Progress", "progress": 85, "details": "Excavation, PCC 1:4:8, RCC isolated footings, plinth beam casting, anti-termite treatment."},
        {"name": "Structural work", "duration": "14 weeks", "days": 98, "status": "Upcoming", "progress": 0, "details": "RCC columns, beams, slab casting across G+2 floors using M25 grade concrete."},
        {"name": "Brickwork", "duration": "8 weeks", "days": 56, "status": "Upcoming", "progress": 0, "details": "External 9-inch fly ash / red clay brick walls, internal 4.5-inch partition walls."},
        {"name": "Electrical and plumbing", "duration": "6 weeks", "days": 42, "status": "Upcoming", "progress": 0, "details": "Concealed conduit piping, CPVC sanitary piping, electrical switchboard chasing."},
        {"name": "Plastering", "duration": "5 weeks", "days": 35, "status": "Upcoming", "progress": 0, "details": "Internal 1:6 cement plaster with smooth finish, external 2-coat waterproof plaster."},
        {"name": "Flooring", "duration": "4 weeks", "days": 28, "status": "Upcoming", "progress": 0, "details": "Vitrified tiles in living/bedrooms, anti-skid in wet areas, granite on stairways."},
        {"name": "Painting", "duration": "4 weeks", "days": 28, "status": "Upcoming", "progress": 0, "details": "Putty application, primer coat, two coats premium acrylic emulsion interior/exterior."},
        {"name": "Final inspection", "duration": "3 weeks", "days": 21, "status": "Upcoming", "progress": 0, "details": "Snag list clearing, structural load testing audit, municipal occupancy handover."}
    ])
    
    materials = json.dumps([
        {"material": "Cement", "spec": "OPC / PPC 53 & 43 Grade", "quantity": 2720, "unit": "Bags (50 kg)", "rate": 395, "total_cost": 1074400, "assumption": "Approx. 0.40 bags/sq.ft for RCC frame and masonry (IS 456 standards)"},
        {"material": "Steel", "spec": "TMT Rebar Fe500D", "quantity": 27.2, "unit": "Metric Tonnes", "rate": 66000, "total_cost": 1795200, "assumption": "Approx. 4.0 kg/sq.ft for G+2 residential structural frame"},
        {"material": "Sand", "spec": "River Sand / Manufactured M-Sand", "quantity": 12240, "unit": "Cubic Feet (cft)", "rate": 58, "total_cost": 709920, "assumption": "Approx. 1.80 cft/sq.ft for concrete, mortar & plastering works"},
        {"material": "Bricks", "spec": "High-strength AAC / Clay Bricks", "quantity": 115600, "unit": "Nos", "rate": 9.5, "total_cost": 1098200, "assumption": "Approx. 17-18 bricks per sq.ft built-up area for perimeter & partitions"},
        {"material": "Aggregate", "spec": "Graded Granite Coarse (20mm & 10mm)", "quantity": 9180, "unit": "Cubic Feet (cft)", "rate": 44, "total_cost": 403920, "assumption": "Approx. 1.35 cft/sq.ft for structural foundation, columns and slab concrete"}
    ])
    
    budget_breakdown = json.dumps({
        "material_cost": 7975000,
        "labour_cost": 4060000,
        "equipment_cost": 1160000,
        "other_expenses": 1015000,
        "total_estimated_cost": 14210000,
        "budget_variance": 290000,
        "variance_label": "Within Budget (2.0% Reserve Available)",
        "percentages": {"material": 56.1, "labour": 28.6, "equipment": 8.2, "other": 7.1}
    })
    
    timeline = json.dumps([
        {"phase": "Site preparation", "start_week": 1, "end_week": 3, "duration_weeks": 3, "start_date": "2026-03-01", "end_date": "2026-03-21", "is_critical": True},
        {"phase": "Foundation", "start_week": 4, "end_week": 8, "duration_weeks": 5, "start_date": "2026-03-22", "end_date": "2026-04-25", "is_critical": True},
        {"phase": "Structural work", "start_week": 9, "end_week": 22, "duration_weeks": 14, "start_date": "2026-04-26", "end_date": "2026-08-01", "is_critical": True},
        {"phase": "Brickwork", "start_week": 23, "end_week": 30, "duration_weeks": 8, "start_date": "2026-08-02", "end_date": "2026-09-26", "is_critical": False},
        {"phase": "Electrical and plumbing", "start_week": 28, "end_week": 33, "duration_weeks": 6, "start_date": "2026-09-06", "end_date": "2026-10-17", "is_critical": False},
        {"phase": "Plastering", "start_week": 34, "end_week": 38, "duration_weeks": 5, "start_date": "2026-10-18", "end_date": "2026-11-21", "is_critical": True},
        {"phase": "Flooring", "start_week": 39, "end_week": 42, "duration_weeks": 4, "start_date": "2026-11-22", "end_date": "2026-12-19", "is_critical": False},
        {"phase": "Painting", "start_week": 43, "end_week": 46, "duration_weeks": 4, "start_date": "2026-12-20", "end_date": "2027-01-16", "is_critical": False},
        {"phase": "Final inspection", "start_week": 47, "end_week": 49, "duration_weeks": 3, "start_date": "2027-01-17", "end_date": "2027-02-06", "is_critical": True}
    ])
    
    risk_analysis = json.dumps({
        "risks": [
            {
                "category": "Weather & Monsoon Delays",
                "severity": "Medium",
                "description": "Southwest monsoon (June - August) aligns with structural roof slab casting.",
                "mitigation": "Fast-track foundation curing in May; use rapid hardening admixtures and weather tarpaulins for active pours."
            },
            {
                "category": "Material Price Volatility",
                "severity": "High",
                "description": "Rebar steel and cement prices experience 5-10% quarterly price fluctuations.",
                "mitigation": "Lock in vendor supply agreement with advance rate contracts for 60% of structural steel requirements."
            },
            {
                "category": "Excavation / Soil Bearing Risk",
                "severity": "Low",
                "description": "Whitefield subsoil may encounter localized clay pockets requiring deeper footings.",
                "mitigation": "Complete standard penetration test (SPT) geotechnical boring before commencing foundation pit work."
            },
            {
                "category": "Specialized Labour Availability",
                "severity": "Medium",
                "description": "Festive season labour attrition in October/November may slow finishing trades.",
                "mitigation": "Retain finishing subcontractor teams with productivity milestones and staggered holiday schedules."
            }
        ],
        "recommendations": [
            "Procure Fe500D grade rebar with test certificates to ensure seismic ductility.",
            "Implement cubic meter concrete test cubes at 7-day and 28-day curing intervals.",
            "Establish on-site digital daily logs to track actual vs planned material consumption."
        ],
        "disclaimer": "All estimates, quantities, and timelines are preliminary algorithmic projections based on standard civil engineering thumb rules (IS 456 / CPWD norms). Final construction execution must be verified and certified by a licensed structural engineer and registered architect."
    })
    
    cursor.execute('''
        INSERT INTO plans (
            project_id, summary, phases, materials, budget_breakdown, timeline, risk_analysis, selected_options
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (project_id, summary, phases, materials, budget_breakdown, timeline, risk_analysis, ai_options))

def get_default_user():
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users ORDER BY id ASC LIMIT 1')
        user = cursor.fetchone()
        if user:
            return dict(user)
        return None
    finally:
        conn.close()

def get_user_by_id(user_id):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
        user = cursor.fetchone()
        if user:
            return dict(user)
        return None
    finally:
        conn.close()

def get_user_by_email(email):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE LOWER(email) = LOWER(?) OR LOWER(username) = LOWER(?)', (email.strip(), email.strip()))
        user = cursor.fetchone()
        if user:
            return dict(user)
        return None
    finally:
        conn.close()

def authenticate_user(email, password):
    user = get_user_by_email(email)
    if not user:
        return None
    
    # Check password hash
    stored_hash = user.get('password_hash')
    if stored_hash and check_password_hash(stored_hash, password):
        return user
    return None

def create_user(full_name, email, password, role="Project Engineer"):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        email_clean = email.strip().lower()
        username = email_clean.split('@')[0]
        
        # Check uniqueness
        cursor.execute('SELECT id FROM users WHERE LOWER(email) = ? OR LOWER(username) = ?', (email_clean, username))
        if cursor.fetchone():
            return None, "An account with this email address already exists."
        
        # Initials
        parts = full_name.strip().split()
        initials = (parts[0][0] + (parts[-1][0] if len(parts) > 1 else '')).upper()
        
        password_hash = generate_password_hash(password)
        cursor.execute('''
            INSERT INTO users (username, full_name, email, password_hash, role, avatar_initials)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (username, full_name.strip(), email_clean, password_hash, role, initials))
        
        conn.commit()
        new_id = cursor.lastrowid
        cursor.execute('SELECT * FROM users WHERE id = ?', (new_id,))
        return dict(cursor.fetchone()), None
    finally:
        conn.close()

def reset_user_password(email, new_password):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        user = get_user_by_email(email)
        if not user:
            return False, "No account found with this email address."
        
        new_hash = generate_password_hash(new_password)
        cursor.execute('UPDATE users SET password_hash = ? WHERE id = ?', (new_hash, user['id']))
        conn.commit()
        return True, "Password reset successfully. You can now sign in with your new password."
    finally:
        conn.close()

def save_project_and_plan(user_id, project_data, plan_data, project_id=None):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ai_options_json = json.dumps(project_data.get('ai_options', []))
        
        if project_id:
            # Update existing project
            cursor.execute('''
                UPDATE projects SET
                    project_name = ?, construction_type = ?, location = ?,
                    plot_area = ?, builtup_area = ?, floors = ?,
                    bedrooms = ?, bathrooms = ?, budget = ?,
                    start_date = ?, completion_date = ?, ai_options = ?,
                    updated_at = ?
                WHERE id = ? AND user_id = ?
            ''', (
                project_data['project_name'], project_data['construction_type'], project_data['location'],
                float(project_data['plot_area']), float(project_data['builtup_area']), project_data['floors'],
                int(project_data.get('bedrooms', 0) or 0), int(project_data.get('bathrooms', 0) or 0),
                float(project_data['budget']), project_data['start_date'], project_data['completion_date'],
                ai_options_json, now, project_id, user_id
            ))
            
            # Update plan
            cursor.execute('''
                UPDATE plans SET
                    summary = ?, phases = ?, materials = ?,
                    budget_breakdown = ?, timeline = ?, risk_analysis = ?,
                    selected_options = ?, raw_ai_notes = ?
                WHERE project_id = ?
            ''', (
                json.dumps(plan_data.get('summary', {})),
                json.dumps(plan_data.get('phases', [])),
                json.dumps(plan_data.get('materials', [])),
                json.dumps(plan_data.get('budget_breakdown', {})),
                json.dumps(plan_data.get('timeline', [])),
                json.dumps(plan_data.get('risk_analysis', {})),
                ai_options_json,
                plan_data.get('raw_ai_notes', ''),
                project_id
            ))
            final_project_id = project_id
        else:
            # Insert new project
            cursor.execute('''
                INSERT INTO projects (
                    user_id, project_name, construction_type, location,
                    plot_area, builtup_area, floors, bedrooms, bathrooms,
                    budget, start_date, completion_date, ai_options, status
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                user_id, project_data['project_name'], project_data['construction_type'], project_data['location'],
                float(project_data['plot_area']), float(project_data['builtup_area']), project_data['floors'],
                int(project_data.get('bedrooms', 0) or 0), int(project_data.get('bathrooms', 0) or 0),
                float(project_data['budget']), project_data['start_date'], project_data['completion_date'],
                ai_options_json, 'Active'
            ))
            final_project_id = cursor.lastrowid
            
            # Insert plan
            cursor.execute('''
                INSERT INTO plans (
                    project_id, summary, phases, materials,
                    budget_breakdown, timeline, risk_analysis, selected_options, raw_ai_notes
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                final_project_id,
                json.dumps(plan_data.get('summary', {})),
                json.dumps(plan_data.get('phases', [])),
                json.dumps(plan_data.get('materials', [])),
                json.dumps(plan_data.get('budget_breakdown', {})),
                json.dumps(plan_data.get('timeline', [])),
                json.dumps(plan_data.get('risk_analysis', {})),
                ai_options_json,
                plan_data.get('raw_ai_notes', '')
            ))
            
        conn.commit()
        return final_project_id
    finally:
        conn.close()

def get_project_with_plan(project_id, user_id):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT p.*, pl.summary, pl.phases, pl.materials, pl.budget_breakdown, pl.timeline, pl.risk_analysis, pl.selected_options
            FROM projects p
            LEFT JOIN plans pl ON p.id = pl.project_id
            WHERE p.id = ? AND p.user_id = ?
        ''', (project_id, user_id))
        row = cursor.fetchone()
        if not row:
            return None
        
        data = dict(row)
        for field in ['ai_options', 'summary', 'phases', 'materials', 'budget_breakdown', 'timeline', 'risk_analysis', 'selected_options']:
            if data.get(field):
                try:
                    data[field] = json.loads(data[field])
                except Exception:
                    pass
        return data
    finally:
        conn.close()

def get_user_projects(user_id):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT p.id, p.project_name, p.construction_type, p.location, p.plot_area, p.builtup_area,
                   p.floors, p.budget, p.start_date, p.completion_date, p.status, p.created_at,
                   (SELECT COUNT(*) FROM plans WHERE project_id = p.id) as has_plan
            FROM projects p
            WHERE p.user_id = ?
            ORDER BY p.id DESC
        ''', (user_id,))
        rows = cursor.fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()

def delete_project(project_id, user_id):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute('DELETE FROM projects WHERE id = ? AND user_id = ?', (project_id, user_id))
        conn.commit()
        return cursor.rowcount > 0
    finally:
        conn.close()

def get_dashboard_stats(user_id):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) as count, SUM(budget) as total_budget, SUM(builtup_area) as total_area FROM projects WHERE user_id = ?', (user_id,))
        stat = cursor.fetchone()
        
        cursor.execute('''
            SELECT COUNT(pl.id) as plan_count 
            FROM plans pl 
            JOIN projects pr ON pl.project_id = pr.id 
            WHERE pr.user_id = ?
        ''', (user_id,))
        plans = cursor.fetchone()
        
        return {
            "total_projects": stat['count'] or 0,
            "total_budget": stat['total_budget'] or 0.0,
            "total_area": stat['total_area'] or 0.0,
            "total_plans": plans['plan_count'] or 0
        }
    finally:
        conn.close()
