# BuildMind AI – AI Construction Planner

An intelligent, enterprise civil engineering planning platform built with **Python Flask**, **SQLite**, and **JavaScript**, adhering strictly to the **BuildMind AI Dashboard Concept 1** design system.

---

## Features

### 1. BuildMind AI Login Page (Concept 2 – Minimal White & Blue)
- **Split-Screen Layout**: Two-column layout with a left branding section and right login card.
- **Left Branding Section**:
  - Blue construction/house icon with **BuildMind AI** logo.
  - Official Tagline: **"Plan Smarter. Build Better."**
  - Main Heading: **"AI Construction Planning Agent"**
  - Supporting Text: **"Plan your projects with AI and build your dream."**
  - Realistic vector artwork featuring a multi-storey building under construction with concrete slabs, structural steel framing, and an authentic yellow tower crane.
  - Soft light-blue radial gradient shapes and blueprint grid accents.
- **Right Login Card**:
  - Large white card with rounded corners (`border-radius: 20px`) and subtle shadow.
  - Blue construction safety helmet icon at the top.
  - Heading: **"Welcome Back!"** and subtitle: **"Sign in to continue to BuildMind AI."**
  - Email Address input with email icon and validation.
  - Password input with lock icon and interactive show/hide password toggle.
  - "Remember me" checkbox and "Forgot password?" link.
  - Royal blue full-width "Sign In" button with arrow icon and smooth hover.
  - "OR" divider line.
  - "Continue with Google" button with official multi-colored Google logo.
  - "Don't have an account? Register" link to the Concept 2 registration flow.
- **Security & Functionality**:
  - Passwords hashed using Werkzeug `generate_password_hash` (never stored in plain text).
  - Session-based authentication with "Remember me" support.
  - Default Demo Login: `rajesh.sharma@buildmind.ai` / `password123`.

### 2. Consistent Dashboard Concept 1 Design
- **Color Theme**: Clean white & light-blue palette (`#f4f7fc` background with `#dbeafe` / `#eff6ff` accents).
- **Buttons**: Royal blue primary buttons (`#1d4ed8` / `#2563eb`) with smooth interactive states.
- **Typography**: Dark navy headings and body text (`#0f172a` / `#1e293b`) using the *Plus Jakarta Sans* typeface.
- **Left Sidebar**:
  - BuildMind AI logo with architectural blueprint icon.
  - Dashboard, My Projects, **AI Planner (highlighted in royal blue)**, Material Estimator, Cost Estimator, Timeline, Security Centre, Launch Readiness, AI Assistant, Reports, Profile & Settings, Logout.
- **Top Navigation**: Search bar, light/dark mode switch, notification counter, user profile picture and dropdown menu.

### 2. AI Construction Planner Page
- **Hero Banner**: "AI Construction Planner" heading, subtitle, and an architectural vector illustration of a modern building with construction scaffolding and crane.
- **Project Information Form**:
  1. Project Name
  2. Construction Type (*Residential, Commercial, Industrial, Apartment, Villa*)
  3. Location
  4. Plot Area (sq. ft.)
  5. Built-up Area (sq. ft.)
  6. Number of Floors (*Ground Floor Only to G+5+ High Rise*)
  7. Number of Bedrooms
  8. Number of Bathrooms
  9. Project Budget in Indian Rupees (₹)
  10. Expected Start Date (date picker)
  11. Expected Completion Date (date picker)
- **AI Planning Options** (*What should AI generate?*):
  - Multi-select interactive cards for: *Construction Planning, Material Requirements, Budget Estimation, Labour Requirements, Construction Timeline, Risk Analysis, Resource Planning*.
- **Generate AI Plan Button**: Prominent royal blue button with step-by-step civil engineering calculation loading modal.

### 3. AI Generated Results Section
- **A. Project Summary**: KPI cards displaying project name, location, typology, built-up area, floors, total estimated cost, and cost per sq. ft.
- **B. Construction Phases**: 9 sequential milestones (*Site preparation, Foundation, Structural work, Brickwork, Electrical and plumbing, Plastering, Flooring, Painting, Final inspection*).
- **C. Material Requirements**: Bill of quantities for **Cement** (bags), **Steel** (rebar MT), **Sand** (cft), **Bricks** (units), and **Aggregate** (cft) with unit rates and IS 456 / CPWD thumb rule assumptions.
- **D. Budget Breakdown**: Stacked cost progress bars and summary cards for Material (~56%), Labour (~28%), Equipment (~8%), and Other Expenses (~8%) with comparison to the client's allocated budget.
- **E. Project Timeline**: Visual schedule tracking phase dates, durations in weeks/days, and critical path highlights.
- **F. Risk Analysis & Recommendations**: Risk severity ratings (*High, Medium, Low*), mitigations for weather/monsoon delays and commodity price volatility, engineering recommendations, and preliminary verification disclaimer.

### 4. Additional Actions
- **Save Project**: Persists plan and project records to the SQLite database.
- **Download PDF Report**: Generates an official, print-ready multi-page engineering document (`/project/<id>/report`).
- **Edit Project**: Smoothly scrolls back to form fields for quick parameter tweaking.
- **Regenerate Plan**: Triggers real-time re-computation with new parameters.
- **Back to Dashboard**: Navigates seamlessly back to the approved BuildMind AI Dashboard Concept 1.

---

## Quick Start

### 1. Requirements
- Python 3.10+ (Flask is already installed)

### 2. Run the Web Application
```bash
python app.py
```
The application will start on `http://127.0.0.1:5000`.

### 3. Run Automated Tests
```bash
python test_app.py
```
Runs the end-to-end unit tests covering all routes, validations, AI plan calculations, and SQLite persistence.
