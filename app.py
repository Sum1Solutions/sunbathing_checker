#!/usr/bin/env python3

import datetime
import requests
import os
from dotenv import load_dotenv
from flask import Flask, request, render_template_string
from markupsafe import Markup

# Load environment variables
load_dotenv()

app = Flask(__name__)

USER_AGENT = f"SunbathingChecker/1.0 ({os.getenv('USER_EMAIL')})"

LOCATIONS = {
    "Naples": {"lat": 26.1420, "lon": -81.7948},
    "Fort Lauderdale": {"lat": 26.1224, "lon": -80.1373},
    "Miami": {"lat": 25.7617, "lon": -80.1918},
    "San Juan": {"lat": 18.4655, "lon": -66.1057},
}

MAIN_CITIES = [
    "Miami, FL", "Fort Lauderdale, FL", "Naples, FL", "Key West, FL",
    "San Juan", "Puerto Rico"
]

CITY_COORDINATES = {
    "Miami, FL": (25.7617, -80.1918),
    "Fort Lauderdale, FL": (26.1224, -80.1373),
    "Naples, FL": (26.1420, -81.7948),
    "Key West, FL": (24.5553, -81.7800),
    "San Juan, Puerto Rico": (18.4655, -66.1057),
}

# Default criteria
DEFAULT_CRITERIA = {
    "min_day_temp": 75,
    "min_night_temp": 65,
    "max_wind": 15,
    "allowed_conditions": [
        "Sunny",
        "Mostly Sunny",
        "Partly Sunny",
        "Partly Cloudy",
        "Clear",
        "Scattered Rain"
    ]
}

DEFAULT_SUNBATHING_CRITERIA = {
    "min_day_temp": 80,
    "max_wind": 10,
    "required_condition": "sunball"
}

def get_forecast(lat, lon):
    points_url = f"https://api.weather.gov/points/{lat},{lon}"
    headers = {"User-Agent": USER_AGENT, "Accept": "application/geo+json"}
    resp_points = requests.get(points_url, headers=headers)
    resp_points.raise_for_status()
    forecast_url = resp_points.json()["properties"]["forecast"]
    
    # Get the full 7-day forecast
    resp_forecast = requests.get(forecast_url, headers=headers)
    resp_forecast.raise_for_status()
    
    forecast_data = resp_forecast.json()
    print("\nForecast data for coordinates:", lat, lon)
    first_period = forecast_data["properties"]["periods"][0]
    print("First period data:", {
        "name": first_period["name"],
        "temperature": first_period["temperature"],
        "wind": first_period["windSpeed"],
        "shortForecast": first_period["shortForecast"]
    })
    
    return forecast_data

def parse_next_7_days(forecast_data):
    periods = forecast_data["properties"]["periods"]
    
    # Get up to 7 days of forecasts (14 periods for day/night)
    results = []
    current_date = None
    for period in periods[:14]:  # Extended from 6 to 14 periods
        start_time = datetime.datetime.fromisoformat(period["startTime"].replace('Z', '+00:00'))
        date_str = start_time.strftime("%A, %B %d")
        
        if date_str != current_date:
            current_date = date_str
            results.append({"date": date_str, "periods": []})
        
        # Create a simplified period object with only the fields we know exist
        simplified_period = {
            "name": period["name"],
            "temperature": period["temperature"],
            "temperatureUnit": period["temperatureUnit"],
            "windSpeed": period["windSpeed"],
            "windDirection": period.get("windDirection", ""),
            "shortForecast": period["shortForecast"],
            "detailedForecast": period["detailedForecast"],
            "isDaytime": period["isDaytime"]
        }
        
        label = "Night" if not period["isDaytime"] else "Day"
        results[-1]["periods"].append((label, simplified_period))
    return results

def is_acceptable_condition(condition, selected_conditions):
    condition = condition.lower()
    selected_conditions = selected_conditions.lower()
    
    if 'sunball' in selected_conditions:
        return any(word in condition for word in ['clear', 'sunny', 'mostly sunny'])
    elif 'clouds' in selected_conditions:
        return any(word in condition for word in ['partly cloudy', 'mostly cloudy', 'overcast'])
    elif 'rain' in selected_conditions:
        return 'rain' in condition
    return False

def is_great_sunbathing_day(day_period, criteria):
    # Check temperature
    if float(day_period['temperature']) < criteria['min_day_temp']:
        return False
    
    # Check wind speed
    if float(day_period['windSpeed'].split()[0]) > criteria['max_wind']:
        return False
    
    # Check weather condition
    if not is_acceptable_condition(day_period['shortForecast'], criteria['required_condition']):
        return False
    
    return True

def evaluate_day_reason(day_period, criteria):
    """Return a reason string for the evaluation of the day_period based on criteria."""
    try:
        temp = float(day_period['temperature'])
        wind_speed = float(day_period['windSpeed'].split()[0])
    except Exception as e:
        return "Error parsing weather data."
    condition = day_period['shortForecast'].lower()
    reasons = []
    if temp < criteria['min_day_temp']:
        reasons.append(f"temperature is too low ({temp}°F, required >= {criteria['min_day_temp']}°F)")
    if wind_speed > criteria['max_wind']:
        reasons.append(f"wind speed is too high ({wind_speed} mph, required <= {criteria['max_wind']} mph)")
    if not is_acceptable_condition(day_period['shortForecast'], criteria['required_condition']):
        reasons.append(f"forecast is not '{criteria['required_condition']}' (got '{day_period['shortForecast']}')")
    if not reasons:
        return f"Great conditions: {temp}°F, {wind_speed} mph, forecast: {day_period['shortForecast']}"
    return "; ".join(reasons)

HTML_TEMPLATE = r"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {
            font-family: system-ui, -apple-system, sans-serif;
            line-height: 1.6;
            margin: 0;
            padding: 0;
            background: #f0f8ff;
        }
        .container {
            width: 90%;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
        }
        .criteria-selector {
            background: #fff;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
            margin-bottom: 20px;
            text-align: left;
        }
        .criteria-row {
            display: flex;
            justify-content: space-between;
        }
        .criteria-group {
            flex: 1;
            margin-right: 10px;
        }
        .checkbox-group {
            display: flex;
            flex-wrap: wrap;
        }
        .checkbox-label {
            margin-right: 10px;
        }
        .submit-btn {
            width: 100%;
            padding: 10px;
            background-color: #32cd32;
            color: white;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            transition: background-color 0.3s ease;
        }
        .submit-btn:hover {
            background-color: #28a428;
        }
        .reset-btn {
            background-color: #d3d3d3;
            color: black;
            width: 100%;
            padding: 10px;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            transition: background-color 0.3s ease;
        }
        .reset-btn:hover {
            background-color: #c0c0c0;
        }
        .button-group {
            display: flex;
        }
        .button-group .submit-btn {
            flex: 2;
            margin-right: 5px;
        }
        .button-group .reset-btn {
            flex: 1;
        }
        .day-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            cursor: pointer;
            background: #f8f8ff;
            padding: 10px;
            border-radius: 5px;
            margin-top: 10px;
        }
        .pelican-rating {
            display: flex;
            justify-content: flex-end;
        }
        .pelican-icon {
            margin-left: 2px;
        }
        .conditions {
            display: none;
            padding: 10px;
            background: #fff;
            border-radius: 5px;
            margin-top: 5px;
        }
        .day-header.active + .conditions {
            display: block;
        }
        .input-field {
            background-color: #f0f2f6;
            border: 1px solid #e0e3e7;
            border-radius: 8px;
            padding: 12px;
            font-size: 16px;
        }
        .input-field:focus {
            border-color: #4a90e2;
        }
        .input-field:hover {
            border-color: #c8d6e5;
        }
        .input-field-transition {
            transition: all 0.3s ease;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Tracey's Forecaster 🌞</h1>
        
        <form method="POST">
            <div class="criteria-selector">
                <h2>Select City</h2>
                <select name="city" class="location-select input-field input-field-transition">
                    {% for city in MAIN_CITIES %}
                    <option value="{{ city }}">{{ city }}</option>
                    {% endfor %}
                </select>
                <h2>Set Ideal Sunbathing Settings</h2>
                <div style="margin-bottom: 10px;">
                    <label>Min Day Temp (°F):</label>
                    <input type="number" name="min_day_temp" value="{{ criteria.min_day_temp if criteria else DEFAULT_SUNBATHING_CRITERIA.min_day_temp }}" class="input-field input-field-transition">
                </div>
                <div style="margin-bottom: 10px;">
                    <label>Max Wind (mph):</label>
                    <input type="number" name="max_wind" value="{{ criteria.max_wind if criteria else DEFAULT_SUNBATHING_CRITERIA.max_wind }}" class="input-field input-field-transition">
                </div>
                <div style="margin-bottom: 10px;">
                    <label>Required Condition:</label>
                    <select name="required_condition" class="input-field input-field-transition">
                        <option value="sunball">Sunball</option>
                        <option value="clouds">Clouds</option>
                        <option value="rain">Rain</option>
                    </select>
                </div>
            </div>
            <button type="submit" class="submit-btn">Check Weather</button>
        </form>
        
        {% if message %}
        <div class="message">{{ message }}</div>
        {% endif %}
        
        {% if results %}
        <div class="results">
            <h2>7 Day Weather and Evaluation</h2>
            <ul>
                {% for day in results %}
                <li>
                    <strong>{{ day.date }}</strong>: 
                    Temperature: {{ day.day_period.temperature }}°{{ day.day_period.temperatureUnit }}, 
                    Wind: {{ day.day_period.windSpeed }}, 
                    Forecast: {{ day.day_period.shortForecast }}.
                    <br>
                    Evaluation: {% if day.is_great %}Great for sunbathing!{% else %}Not great for sunbathing.{% endif %}
                    <br>
                    Reason: {{ day.reason }}
                </li>
                {% endfor %}
            </ul>
        </div>
        {% endif %}
    </div>
    <script>
        document.querySelectorAll('.day-header').forEach(header => {
            header.addEventListener('click', () => {
                header.classList.toggle('active');
            });
        });
    </script>
</body>
"""

@app.route("/", methods=["GET", "POST"])
def home():
    message = ""
    results = []
    criteria = DEFAULT_SUNBATHING_CRITERIA
    if request.method == "POST":
        city = request.form.get("city")
        # Allow overriding criteria if provided
        criteria = {
            "min_day_temp": float(request.form.get("min_day_temp", DEFAULT_SUNBATHING_CRITERIA['min_day_temp'])),
            "max_wind": float(request.form.get("max_wind", DEFAULT_SUNBATHING_CRITERIA['max_wind'])),
            "required_condition": request.form.get("required_condition", DEFAULT_SUNBATHING_CRITERIA['required_condition']).lower()
        }
        if city in CITY_COORDINATES:
            lat, lon = CITY_COORDINATES[city]
            forecast_data = get_forecast(lat, lon)
            parsed_days = parse_next_7_days(forecast_data)
            for day in parsed_days:
                day_period = None
                for label, period in day.get("periods", []):
                    if period.get("isDaytime", False):
                        day_period = period
                        break
                if day_period:
                    is_great = is_great_sunbathing_day(day_period, criteria)
                    reason = evaluate_day_reason(day_period, criteria)
                    results.append({"date": day.get("date"), "is_great": is_great, "reason": reason, "day_period": day_period})
            if results:
                message = "7-day forecast evaluated."
            else:
                message = "No valid day periods found."
        else:
            message = "City not recognized."
    return render_template_string(HTML_TEMPLATE, message=Markup(message), MAIN_CITIES=MAIN_CITIES, results=results, criteria=criteria)

if __name__ == "__main__":
    app.run(debug=True, port=5001)
