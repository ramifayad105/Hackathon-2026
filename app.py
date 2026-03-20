from flask import Flask, render_template, request

app = Flask(__name__, template_folder='Templates', static_folder='Static')

# ── Data ──────────────────────────────────────────────────────────────────────

appointments = [
    {
        'date': 'April 10, 2026',
        'time': '9:00 AM',
        'hospital': 'City General Hospital',
        'purpose': 'Annual Physical Exam',
    },
    {
        'date': 'April 22, 2026',
        'time': '2:30 PM',
        'hospital': 'Riverside Medical Center',
        'purpose': 'Cholesterol Screening',
    },
    {
        'date': 'May 5, 2026',
        'time': '11:00 AM',
        'hospital': 'Northside Health Clinic',
        'purpose': 'Blood Pressure Check',
    },
]

health_guidelines = {
    '18-30': [
        'Blood pressure check',
        'BMI check',
        'Cholesterol screening',
        'Mental health screening',
    ],
    '31-50': [
        'Heart disease risk assessment',
        'Diabetes screening',
        'Mammogram',
        'Colonoscopy',
    ],
    '51+': [
        'Bone density test',
        'Vision and hearing test',
        'Flu and shingles vaccines',
        'Cognitive health checkup',
    ],
}

# ── Healthy range evaluators per test ─────────────────────────────────────────
# Each function receives (value_string, age_range) and returns True if healthy.

def _parse_bp(val):
    """Parse 'systolic/diastolic' or just systolic."""
    parts = val.replace(' ', '').split('/')
    try:
        sys = int(parts[0])
        dia = int(parts[1]) if len(parts) > 1 else None
        return sys, dia
    except (ValueError, IndexError):
        return None, None

def evaluate_health(test, value, age_range):
    t = test.lower()
    v = value.strip()

    if 'blood pressure' in t:
        sys, dia = _parse_bp(v)
        if sys is None:
            return None
        sys_ok = sys < 130
        dia_ok = (dia < 85) if dia is not None else True
        return sys_ok and dia_ok

    if 'bmi' in t:
        try:
            bmi = float(v)
            return 18.5 <= bmi <= 24.9
        except ValueError:
            return None

    if 'cholesterol' in t:
        try:
            chol = float(v)
            return chol < 200
        except ValueError:
            return None

    if 'diabetes' in t or 'blood sugar' in t or 'glucose' in t:
        try:
            glucose = float(v)
            return glucose < 100
        except ValueError:
            return None

    if 'bone density' in t or 't-score' in t:
        try:
            score = float(v)
            return score >= -1.0
        except ValueError:
            return None

    # For qualitative checks (mammogram, colonoscopy, vaccines, etc.)
    # treat any non-empty entry as "done" → green
    return True if v else None


providers = [
    {
        'name': 'City General Hospital',
        'specializations': ['General Medicine', 'Cardiology', 'Oncology'],
        'phone': '(555) 100-2000',
        'address': '100 Main St, Suite 1',
        'hours': 'Mon–Fri 7am–6pm',
        'details': [
            'Full-service emergency department open 24/7',
            'Advanced cardiac imaging and stress testing',
            'Oncology infusion center with specialist consultations',
            'In-house lab and radiology services',
        ],
    },
    {
        'name': 'Riverside Medical Center',
        'specializations': ['Preventive Care', 'Diabetes Management', 'Nutrition'],
        'phone': '(555) 200-3000',
        'address': '200 River Rd',
        'hours': 'Mon–Sat 8am–5pm',
        'details': [
            'Comprehensive annual wellness exams and health screenings',
            'Certified diabetes educators and continuous glucose monitoring support',
            'Registered dietitian consultations and meal planning',
            'Cholesterol and blood pressure management programs',
        ],
    },
    {
        'name': 'Northside Health Clinic',
        'specializations': ['Family Medicine', 'Mental Health', 'Pediatrics'],
        'phone': '(555) 300-4000',
        'address': '300 North Ave',
        'hours': 'Mon–Fri 8am–7pm, Sat 9am–1pm',
        'details': [
            'Primary care for all ages from newborns to seniors',
            'Licensed therapists offering individual and group counseling',
            'Pediatric immunizations and developmental screenings',
            'Telehealth appointments available',
        ],
    },
    {
        'name': 'ECU Health Medical Center',
        'specializations': ['Academic Medicine', 'Cardiology', 'Neurology', 'Orthopedics'],
        'phone': '(252) 847-4100',
        'address': '2100 Stantonsburg Rd, Greenville, NC 27834',
        'hours': 'Open 24/7 — Emergency & Inpatient Services',
        'details': [
            'Level I Trauma Center serving eastern North Carolina',
            'ECU Health Heart & Vascular Center with interventional cardiology',
            'Comprehensive stroke and neurology program',
            'Orthopedic surgery, joint replacement, and sports medicine',
            'Cancer care through ECU Health Cancer Center',
            'Teaching hospital affiliated with East Carolina University',
        ],
    },
    {
        'name': 'Vidant Beaufort Hospital',
        'specializations': ['Emergency Care', 'General Surgery', 'Family Medicine', 'Imaging'],
        'phone': '(252) 975-4100',
        'address': '628 E 12th St, Washington, NC 27889',
        'hours': 'Emergency 24/7, Outpatient Mon–Fri 8am–5pm',
        'details': [
            'Full-service community hospital in Beaufort County',
            'Emergency department with board-certified physicians',
            'Advanced diagnostic imaging including CT and MRI',
            'Outpatient surgery center and wound care clinic',
            'Primary care and specialty physician practices',
        ],
    },
    {
        'name': 'Carteret Health Care',
        'specializations': ['Coastal Medicine', 'Orthopedics', 'Women\'s Health', 'Rehabilitation'],
        'phone': '(252) 499-6000',
        'address': '3500 Arendell St, Morehead City, NC 28557',
        'hours': 'Emergency 24/7, Clinics Mon–Fri 8am–5pm',
        'details': [
            'Coastal community hospital serving Crystal Coast region',
            'Orthopedic and sports medicine specialists',
            'Women\'s health services including obstetrics and mammography',
            'Physical therapy and cardiac rehabilitation programs',
            'Walk-in urgent care and primary care network',
        ],
    },
    {
        'name': 'Onslow Memorial Hospital',
        'specializations': ['Emergency Medicine', 'Maternity Care', 'Cardiology', 'General Surgery'],
        'phone': '(910) 577-2345',
        'address': '317 Western Blvd, Jacksonville, NC 28546',
        'hours': 'Open 24/7 — Emergency & Inpatient Services',
        'details': [
            'Serving Jacksonville and Onslow County communities',
            'Family Birth Place with Level II nursery',
            'Cardiac catheterization lab and heart center',
            'Comprehensive cancer care and infusion services',
            'Multiple primary care and specialty clinics throughout the area',
        ],
    },
    {
        'name': 'Nash UNC Health Care',
        'specializations': ['Regional Healthcare', 'Oncology', 'Neuroscience', 'Bariatric Surgery'],
        'phone': '(252) 962-8000',
        'address': '2460 Curtis Ellis Dr, Rocky Mount, NC 27804',
        'hours': 'Emergency 24/7, Outpatient Mon–Fri 7am–6pm',
        'details': [
            'Regional medical center serving Nash and Edgecombe counties',
            'Comprehensive cancer center with radiation oncology',
            'Neuroscience center with stroke certification',
            'Bariatric surgery program and weight management',
            'Advanced wound care and hyperbaric medicine',
        ],
    },
    {
        'name': 'Wilson Medical Center',
        'specializations': ['Community Healthcare', 'Diabetes Care', 'Pulmonology', 'Gastroenterology'],
        'phone': '(252) 399-8040',
        'address': '1705 Tarboro St SW, Wilson, NC 27893',
        'hours': 'Emergency 24/7, Clinics Mon–Fri 8am–5pm',
        'details': [
            'Community hospital serving Wilson County',
            'Diabetes education and management programs',
            'Pulmonary function testing and sleep studies',
            'Endoscopy center and digestive health services',
            'Primary care medical group with multiple locations',
        ],
    },
    {
        'name': 'Outer Banks Hospital',
        'specializations': ['Coastal Emergency Care', 'Family Medicine', 'Urgent Care', 'Telemedicine'],
        'phone': '(252) 449-4500',
        'address': '4800 S Croatan Hwy, Nags Head, NC 27959',
        'hours': 'Emergency 24/7, Urgent Care 7 days 8am–8pm',
        'details': [
            'Only hospital serving the Outer Banks barrier islands',
            'Emergency services for residents and tourists',
            'Urgent care centers in Nags Head and Avon',
            'Telemedicine consultations with specialists',
            'Primary care and walk-in services year-round',
        ],
    },
]

# ── Routes ────────────────────────────────────────────────────────────────────

@app.route('/', methods=['GET', 'POST'])
def index():
    selected_age = None
    recommended_tests = []
    user_values = {}
    health_status = {}
    unhealthy_tests = []
    saved = False

    if request.method == 'POST':
        selected_age = request.form.get('age_range', '')
        recommended_tests = health_guidelines.get(selected_age, [])

        any_values = any(
            request.form.get(t.lower().replace(' ', '_'), '').strip()
            for t in recommended_tests
        )

        if any_values:
            for test in recommended_tests:
                key = test.lower().replace(' ', '_')
                val = request.form.get(key, '').strip()
                if val:
                    user_values[test] = val
                    result = evaluate_health(test, val, selected_age)
                    health_status[test] = result
                    if result is False:
                        unhealthy_tests.append(test)
            saved = True

    return render_template(
        'home.html',
        appointments=appointments,
        providers=providers,
        selected_age=selected_age,
        recommended_tests=recommended_tests,
        user_values=user_values,
        health_status=health_status,
        unhealthy_tests=unhealthy_tests,
        saved=saved,
    )


if __name__ == '__main__':
    app.run(debug=True)
