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

providers = [
    {
        'name': 'City General Hospital',
        'specializations': ['General Medicine', 'Cardiology', 'Oncology'],
    },
    {
        'name': 'Riverside Medical Center',
        'specializations': ['Preventive Care', 'Diabetes Management', 'Nutrition'],
    },
    {
        'name': 'Northside Health Clinic',
        'specializations': ['Family Medicine', 'Mental Health', 'Pediatrics'],
    },
]

# ── Routes ────────────────────────────────────────────────────────────────────

@app.route('/', methods=['GET', 'POST'])
def index():
    selected_age = None
    recommended_tests = []

    if request.method == 'POST':
        selected_age = request.form.get('age_range', '')
        recommended_tests = health_guidelines.get(selected_age, [])

    return render_template(
        'home.html',
        appointments=appointments,
        providers=providers,
        selected_age=selected_age,
        recommended_tests=recommended_tests,
    )


if __name__ == '__main__':
    app.run(debug=True)
