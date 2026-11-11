import os
import json
import math
from datetime import datetime, timedelta
import urllib.request
import urllib.error

# Benchmark Rates (INR) for Indian Civil Construction (2025-2026 Standards)
RATES = {
    'cement_bag_50kg': 395.0,        # ₹ per 50kg bag (OPC/PPC)
    'steel_ton': 66000.0,            # ₹ per Metric Tonne (Fe500D TMT)
    'sand_cft': 58.0,                # ₹ per cft (M-Sand / River Sand blend)
    'brick_unit': 9.50,              # ₹ per brick / AAC block equivalent
    'aggregate_cft': 44.0,           # ₹ per cft (20mm & 10mm graded granite)
    'base_cost_per_sqft': {
        'Residential': 2100.0,
        'Commercial': 2450.0,
        'Industrial': 1950.0,
        'Apartment': 2300.0,
        'Villa': 2750.0
    }
}

# Material Thumb Rules per sq.ft of built-up area (Based on IS 456 & CPWD norms)
MATERIAL_COEFFICIENTS = {
    'Residential': {
        'cement_bags_per_sqft': 0.40,
        'steel_kg_per_sqft': 3.90,
        'sand_cft_per_sqft': 1.80,
        'bricks_per_sqft': 17.0,
        'aggregate_cft_per_sqft': 1.35
    },
    'Commercial': {
        'cement_bags_per_sqft': 0.45,
        'steel_kg_per_sqft': 4.80,
        'sand_cft_per_sqft': 1.95,
        'bricks_per_sqft': 14.0,
        'aggregate_cft_per_sqft': 1.55
    },
    'Industrial': {
        'cement_bags_per_sqft': 0.38,
        'steel_kg_per_sqft': 5.20,
        'sand_cft_per_sqft': 1.70,
        'bricks_per_sqft': 10.0,
        'aggregate_cft_per_sqft': 1.65
    },
    'Apartment': {
        'cement_bags_per_sqft': 0.43,
        'steel_kg_per_sqft': 4.30,
        'sand_cft_per_sqft': 1.85,
        'bricks_per_sqft': 16.0,
        'aggregate_cft_per_sqft': 1.45
    },
    'Villa': {
        'cement_bags_per_sqft': 0.42,
        'steel_kg_per_sqft': 4.10,
        'sand_cft_per_sqft': 1.90,
        'bricks_per_sqft': 18.0,
        'aggregate_cft_per_sqft': 1.40
    }
}

# Standard phase percentage weights of total project timeline
PHASE_WEIGHTS = [
    {"name": "Site preparation", "weight": 0.06, "desc": "Soil testing, site leveling, boundary demarcation, water & power supply establishment."},
    {"name": "Foundation", "weight": 0.12, "desc": "Excavation, anti-termite treatment, PCC, isolated/raft footings, and plinth beam casting."},
    {"name": "Structural work", "weight": 0.28, "desc": "Reinforced concrete columns, framing beams, lintels, and multi-floor slab casting."},
    {"name": "Brickwork", "weight": 0.16, "desc": "Exterior and interior masonry wall construction, door/window frame fixing."},
    {"name": "Electrical and plumbing", "weight": 0.11, "desc": "Conduit routing, sanitary sewer piping, distribution boards, water supply lines."},
    {"name": "Plastering", "weight": 0.09, "desc": "Internal two-coat smooth cement plaster and external weather-shield rough plaster."},
    {"name": "Flooring", "weight": 0.07, "desc": "Screed leveling, vitrified tiling, skirting, granite threshold installations."},
    {"name": "Painting", "weight": 0.06, "desc": "Putty coats, acrylic primer application, and dual-layer premium emulsion finish."},
    {"name": "Final inspection", "weight": 0.05, "desc": "Quality audit, snag list rectifications, pressure testing, municipal compliance handover."}
]

def parse_date(date_str, fallback=None):
    if not date_str:
        return fallback or datetime.now()
    try:
        return datetime.strptime(date_str, "%Y-%m-%d")
    except Exception:
        return fallback or datetime.now()

def format_currency_inr(amount):
    """Format number into Indian Rupee formatting (e.g. ₹ 1,45,00,000)"""
    amount = round(amount)
    s = str(amount)
    if len(s) <= 3:
        return f"₹ {s}"
    last3 = s[-3:]
    remaining = s[:-3]
    parts = []
    while len(remaining) > 2:
        parts.insert(0, remaining[-2:])
        remaining = remaining[:-2]
    if remaining:
        parts.insert(0, remaining)
    return f"₹ {','.join(parts)},{last3}"

def generate_ai_construction_plan(project_data):
    """
    Core AI & Civil Engineering Engine.
    Processes project specifications and generates comprehensive:
    1. Project Summary
    2. Construction Phases
    3. Material Requirements
    4. Budget Breakdown
    5. Project Timeline
    6. Risk Analysis
    """
    project_name = project_data.get('project_name', 'Modern Residential Complex')
    construction_type = project_data.get('construction_type', 'Residential')
    location = project_data.get('location', 'India')
    plot_area = float(project_data.get('plot_area', 2400))
    builtup_area = float(project_data.get('builtup_area', 3200))
    floors = project_data.get('floors', 'G + 1 Floor')
    bedrooms = int(project_data.get('bedrooms', 3) or 0)
    bathrooms = int(project_data.get('bathrooms', 3) or 0)
    user_budget = float(project_data.get('budget', 7500000))
    start_date_str = project_data.get('start_date', '')
    completion_date_str = project_data.get('completion_date', '')
    selected_options = project_data.get('ai_options', [
        "Construction Planning", "Material Requirements", "Budget Estimation",
        "Labour Requirements", "Construction Timeline", "Risk Analysis", "Resource Planning"
    ])

    start_dt = parse_date(start_date_str, datetime.now() + timedelta(days=7))
    comp_dt = parse_date(completion_date_str, start_dt + timedelta(days=330))
    
    total_days = max(60, (comp_dt - start_dt).days)
    total_weeks = math.ceil(total_days / 7)

    # 1. Material Calculations (IS 456 / CPWD thumb rules)
    coeffs = MATERIAL_COEFFICIENTS.get(construction_type, MATERIAL_COEFFICIENTS['Residential'])
    
    # Adjust coefficients based on number of floors
    floor_factor = 1.0
    if '3' in floors or '4' in floors:
        floor_factor = 1.08
    elif '5' in floors or 'High' in floors or 'Apartment' in construction_type:
        floor_factor = 1.15
        
    cement_bags = round(builtup_area * coeffs['cement_bags_per_sqft'] * floor_factor)
    steel_tons = round((builtup_area * coeffs['steel_kg_per_sqft'] * floor_factor) / 1000.0, 2)
    sand_cft = round(builtup_area * coeffs['sand_cft_per_sqft'] * floor_factor)
    bricks_count = round(builtup_area * coeffs['bricks_per_sqft'])
    aggregate_cft = round(builtup_area * coeffs['aggregate_cft_per_sqft'] * floor_factor)

    cement_cost = round(cement_bags * RATES['cement_bag_50kg'])
    steel_cost = round(steel_tons * RATES['steel_ton'])
    sand_cost = round(sand_cft * RATES['sand_cft'])
    brick_cost = round(bricks_count * RATES['brick_unit'])
    aggregate_cost = round(aggregate_cft * RATES['aggregate_cft'])
    
    primary_materials_cost = cement_cost + steel_cost + sand_cost + brick_cost + aggregate_cost
    
    # Total Material Cost covers finishing, plumbing, wiring, woodwork, tile etc. (~56% of standard construction)
    base_sqft_rate = RATES['base_cost_per_sqft'].get(construction_type, 2100.0)
    benchmark_total_cost = round(builtup_area * base_sqft_rate)
    
    # Breakdown allocations
    est_material_cost = round(benchmark_total_cost * 0.56)
    est_labour_cost = round(benchmark_total_cost * 0.28)
    est_equipment_cost = round(benchmark_total_cost * 0.08)
    est_other_expenses = round(benchmark_total_cost * 0.08)
    total_estimated_cost = est_material_cost + est_labour_cost + est_equipment_cost + est_other_expenses

    # Variance against user budget
    budget_diff = round(user_budget - total_estimated_cost)
    if budget_diff >= 0:
        variance_label = f"Favorable: ₹ {abs(budget_diff):,} reserve margin ({round((budget_diff/user_budget)*100, 1)}%)"
        budget_health = "Healthy"
    else:
        variance_label = f"Deficit: ₹ {abs(budget_diff):,} required ({round((abs(budget_diff)/user_budget)*100, 1)}% over budget)"
        budget_health = "Caution - Value Engineering Recommended"

    # 2. Construction Phases & Timeline
    phases = []
    timeline = []
    current_phase_start = start_dt
    
    for idx, p in enumerate(PHASE_WEIGHTS):
        phase_days = max(7, round(total_days * p['weight']))
        phase_weeks = max(1, round(phase_days / 7))
        phase_end = current_phase_start + timedelta(days=phase_days)
        
        # Determine status relative to start date
        status = "Scheduled"
        progress = 0
        
        phases.append({
            "id": idx + 1,
            "name": p['name'],
            "duration": f"{phase_weeks} weeks ({phase_days} days)",
            "days": phase_days,
            "weeks": phase_weeks,
            "start_date": current_phase_start.strftime("%d %b %Y"),
            "end_date": phase_end.strftime("%d %b %Y"),
            "status": status,
            "progress": progress,
            "details": p['desc']
        })
        
        timeline.append({
            "phase": p['name'],
            "start_date": current_phase_start.strftime("%Y-%m-%d"),
            "end_date": phase_end.strftime("%Y-%m-%d"),
            "duration_days": phase_days,
            "duration_weeks": phase_weeks,
            "is_critical": idx in [1, 2, 5, 8], # Foundation, Structure, Plastering, Inspection are Critical Path
            "details": p['desc']
        })
        
        current_phase_start = phase_end + timedelta(days=1)

    # 3. Materials List Structure
    materials = [
        {
            "material": "Cement",
            "spec": "PPC 53 / 43 Grade (IS 1489 / IS 269)",
            "quantity": cement_bags,
            "unit": "Bags (50 kg)",
            "rate": RATES['cement_bag_50kg'],
            "total_cost": cement_cost,
            "assumption": f"Thumb rule of {coeffs['cement_bags_per_sqft']} bags/sq.ft for structural frame, masonry mortar & plastering"
        },
        {
            "material": "Steel",
            "spec": "Fe500D High Ductility TMT Rebar (IS 1786)",
            "quantity": steel_tons,
            "unit": "Metric Tonnes",
            "rate": RATES['steel_ton'],
            "total_cost": steel_cost,
            "assumption": f"Structural steel density of {coeffs['steel_kg_per_sqft']} kg/sq.ft for {floors} RCC structure"
        },
        {
            "material": "Sand",
            "spec": "Manufactured Sand (M-Sand) Zone II (IS 383)",
            "quantity": sand_cft,
            "unit": "Cubic Feet (cft)",
            "rate": RATES['sand_cft'],
            "total_cost": sand_cost,
            "assumption": f"Calculated at {coeffs['sand_cft_per_sqft']} cft/sq.ft for concrete mix (M20/M25) and brick joint mortar"
        },
        {
            "material": "Bricks",
            "spec": "Class 1 Red Clay / AAC Blocks (IS 1077)",
            "quantity": bricks_count,
            "unit": "Units / Blocks",
            "rate": RATES['brick_unit'],
            "total_cost": brick_cost,
            "assumption": f"Wall enclosure layout at ~{coeffs['bricks_per_sqft']} units/sq.ft for external 9-inch and internal 4.5-inch walls"
        },
        {
            "material": "Aggregate",
            "spec": "20mm & 10mm Graded Blue Metal (IS 383)",
            "quantity": aggregate_cft,
            "unit": "Cubic Feet (cft)",
            "rate": RATES['aggregate_cft'],
            "total_cost": aggregate_cost,
            "assumption": f"Coarse aggregate ratio at {coeffs['aggregate_cft_per_sqft']} cft/sq.ft for RCC structural footings, slabs & beams"
        }
    ]

    # 4. Budget Breakdown Structure
    budget_breakdown = {
        "material_cost": est_material_cost,
        "labour_cost": est_labour_cost,
        "equipment_cost": est_equipment_cost,
        "other_expenses": est_other_expenses,
        "total_estimated_cost": total_estimated_cost,
        "user_budget": user_budget,
        "variance": budget_diff,
        "variance_label": variance_label,
        "budget_health": budget_health,
        "cost_per_sqft": round(total_estimated_cost / builtup_area, 2),
        "percentages": {
            "material": round((est_material_cost / total_estimated_cost) * 100, 1),
            "labour": round((est_labour_cost / total_estimated_cost) * 100, 1),
            "equipment": round((est_equipment_cost / total_estimated_cost) * 100, 1),
            "other": round((est_other_expenses / total_estimated_cost) * 100, 1)
        }
    }

    # 5. Risk Analysis
    risks = [
        {
            "category": "Potential Construction Delays",
            "severity": "Medium",
            "description": f"Seasonal weather transitions and monsoon rainfall in {location} can cause soil mudding and slow down concrete curing phases.",
            "mitigation": "Schedule sub-structure excavation during dry season; use high early strength admixtures and waterproof plastic tarpaulins for fresh slab casting."
        },
        {
            "category": "Budget & Raw Material Risks",
            "severity": "High",
            "description": "Commodity inflation in TMT steel rebar and cement prices can introduce 6-12% variance in procurement bills during peak structural periods.",
            "mitigation": "Establish fixed-price procurement agreements with authorized regional distributors with a minimum 45-day price freeze buffer."
        },
        {
            "category": "Labour Shortages & Festive Downtime",
            "severity": "Medium",
            "description": "Critical skilled trades (shuttering carpenters, bar benders, licensed electricians) typically face attendance dips during festive calendar periods.",
            "mitigation": "Mobilize multi-skilled subcontractor teams with staggered milestone incentives and advance work-front planning."
        },
        {
            "category": "Sub-surface & Soil Variation",
            "severity": "Low",
            "description": f"Plot area ({plot_area:,.0f} sq.ft) excavation may reveal hard rock or loose clay strata, affecting foundation footing depth.",
            "mitigation": "Mandate a 3-point Standard Penetration Test (SPT) soil report prior to final footing reinforcement bar cutting."
        }
    ]

    recommendations = [
        f"Procure Fe500D grade rebar bearing ISI marks and mill test certificates to ensure compliance for {floors} structural load.",
        f"Implement cube testing (M25 grade) at 7-day and 28-day intervals for all slab and column casting milestones.",
        f"Maintain a site contingency reserve of ₹ {round(total_estimated_cost * 0.05):,} (5% of overall budget) to absorb unforeseen soil or municipal revisions.",
        "Deploy digital daily material tracking to prevent cement bag wastage and steel scrap loss beyond 3.5% threshold."
    ]

    disclaimer = (
        "IMPORTANT NOTICE: All estimates, material quantities, timeline schedules, and cost figures presented herein "
        "are preliminary computational forecasts generated by BuildMind AI using Indian standard civil engineering benchmarks "
        "(IS 456, IS 875, and CPWD specifications). Actual requirements will vary depending on site topography, soil bearing capacity, "
        "final architectural drawings, structural engineering designs, and market conditions. All projections must be reviewed, "
        "verified, and stamped by a registered civil/structural engineer and licensed architect before contractual execution."
    )

    risk_analysis = {
        "risks": risks,
        "recommendations": recommendations,
        "disclaimer": disclaimer
    }

    # 6. Summary Structure
    summary = {
        "project_name": project_name,
        "construction_type": construction_type,
        "total_area": builtup_area,
        "plot_area": plot_area,
        "floors": floors,
        "bedrooms": bedrooms,
        "bathrooms": bathrooms,
        "location": location,
        "estimated_budget": total_estimated_cost,
        "user_budget": user_budget,
        "cost_per_sqft": round(total_estimated_cost / builtup_area, 2),
        "total_duration_weeks": total_weeks,
        "total_duration_days": total_days,
        "start_date": start_dt.strftime("%d %b %Y"),
        "completion_date": comp_dt.strftime("%d %b %Y")
    }

    raw_ai_notes = f"Generated by BuildMind AI Engine using Indian Civil Construction Code IS 456 & CPWD benchmarks. Built-up area: {builtup_area:,.0f} sq.ft across {floors}."

    # Try LLM enhancement if GEMINI_API_KEY is configured
    try_llm_enhancement(project_data, summary, risk_analysis)

    return {
        "summary": summary,
        "phases": phases,
        "materials": materials,
        "budget_breakdown": budget_breakdown,
        "timeline": timeline,
        "risk_analysis": risk_analysis,
        "selected_options": selected_options,
        "raw_ai_notes": raw_ai_notes
    }

def try_llm_enhancement(project_data, summary, risk_analysis):
    """
    Optional LLM integration: If GEMINI_API_KEY is present, enhances the risk analysis
    and engineering notes with site-specific LLM intelligence.
    Fails safely without throwing any exceptions.
    """
    api_key = os.environ.get('GEMINI_API_KEY')
    if not api_key:
        return
    
    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
        prompt = (
            f"As a Senior Civil Engineer in India, give 2 quick specific site construction tips and 1 primary risk "
            f"for a {project_data.get('construction_type')} project located in {project_data.get('location')} "
            f"with built-up area of {project_data.get('builtup_area')} sq.ft and {project_data.get('floors')}."
        )
        payload = json.dumps({
            "contents": [{"parts": [{"text": prompt}]}]
        }).encode('utf-8')
        
        req = urllib.request.Request(url, data=payload, headers={'Content-Type': 'application/json'}, method='POST')
        with urllib.request.urlopen(req, timeout=5) as response:
            res_data = json.loads(response.read().decode('utf-8'))
            candidate = res_data.get('candidates', [{}])[0].get('content', {}).get('parts', [{}])[0].get('text', '')
            if candidate:
                risk_analysis['ai_engineer_notes'] = candidate.strip()
    except Exception:
        # Gracefully proceed with native engineering calculations
        pass
