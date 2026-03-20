# Preventive Care Dashboard

A Flask-based web application that helps users manage their preventive healthcare by displaying upcoming appointments, providing age-based health guidelines, and listing local healthcare providers.

## Features

- **Upcoming Appointments**: View scheduled medical appointments with date, time, hospital, and purpose
- **Age-Based Health Guidelines**: Get personalized health screening recommendations based on your age range (18-30, 31-50, 51+)
- **Healthcare Providers**: Browse local healthcare providers and their specializations

## Tech Stack

- **Backend**: Flask (Python web framework)
- **Frontend**: HTML5, CSS3, Jinja2 templating
- **Testing**: pytest, Hypothesis (property-based testing)

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd Hackathon-2026
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

1. Start the Flask development server:
```bash
python app.py
```

2. Open your browser and navigate to:
```
http://127.0.0.1:5000
```

3. Interact with the dashboard:
   - View your upcoming appointments
   - Select your age range to get personalized health screening recommendations
   - Browse local healthcare providers and their specializations

## Testing

Run the test suite:
```bash
pytest
```

Run tests with coverage:
```bash
pytest --cov=. --cov-report=html
```

## Project Structure

```
Hackathon-2026/
├── app.py                 # Main Flask application
├── Templates/
│   └── home.html         # Dashboard HTML template
├── Static/
│   └── style.css         # Stylesheet
├── tests/
│   ├── __init__.py
│   ├── conftest.py       # Test configuration
│   ├── test_properties.py # Property-based tests
│   ├── test_unit.py      # Unit tests
│   └── test_integration.py # Integration tests
├── requirements.txt      # Python dependencies
└── README.md            # This file
```

## Development

The application uses hardcoded data for demonstration purposes. In a production environment, you would integrate with a database and external APIs for real appointment and provider data.

## License

[Add your license here]
