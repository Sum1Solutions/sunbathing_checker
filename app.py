#!/usr/bin/env python3

import datetime
import requests
import os
import json
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
            "isDaytime": period["isDaytime"],
            "cloudCover": period.get("cloudCover", 0)
        }
        
        label = "Night" if not period["isDaytime"] else "Day"
        results[-1]["periods"].append((label, simplified_period))
    return results

def is_sunbathing_day(periods, criteria):
    min_day_temp = criteria.get('min_day_temp', DEFAULT_CRITERIA['min_day_temp'])
    min_night_temp = criteria.get('min_night_temp', DEFAULT_CRITERIA['min_night_temp'])
    max_wind = criteria.get('max_wind', DEFAULT_CRITERIA['max_wind'])
    allowed_conditions = criteria.get('allowed_conditions', DEFAULT_CRITERIA['allowed_conditions'])
    
    if not allowed_conditions:  # If no conditions are selected, use defaults
        allowed_conditions = DEFAULT_CRITERIA['allowed_conditions']
    
    # We only need the day period for basic check
    day_period = None
    for period in periods:
        if period['isDaytime']:
            day_period = period
            break
    
    if not day_period:  # No day period found
        print(f"No day period found")
        return False

    # Check day conditions
    day_temp = float(day_period['temperature'])
    day_wind = float(day_period['windSpeed'].split()[0])
    day_conditions = day_period['shortForecast'].lower()
    
    # Day must meet all criteria
    day_temp_ok = day_temp >= min_day_temp
    day_wind_ok = day_wind <= max_wind
    
    # Check for both exact matches and partial matches in conditions
    day_conditions_ok = False
    for cond in allowed_conditions:
        cond_lower = cond.lower()
        if cond_lower == 'scattered rain':
            if 'scattered' in day_conditions and ('rain' in day_conditions or 'shower' in day_conditions):
                day_conditions_ok = True
                break
        elif cond_lower in day_conditions:
            day_conditions_ok = True
            break
    
    print(f"Day check - Temp: {day_temp}°F (>= {min_day_temp}°F: {day_temp_ok})")
    print(f"Day check - Wind: {day_wind} mph (<= {max_wind} mph: {day_wind_ok})")
    print(f"Day check - Conditions: {day_conditions} (matches {allowed_conditions}: {day_conditions_ok})")
    
    return day_temp_ok and day_wind_ok and day_conditions_ok

def calculate_day_flamingo_rating(day_periods, criteria):
    """Calculate flamingo rating for an entire day (day and night periods)"""
    # Find the day and night periods
    day_period = None
    night_period = None
    for label, period in day_periods:
        if period['isDaytime']:
            day_period = period
        else:
            night_period = period
    
    if not day_period or not night_period:
        print(f"Missing day or night period")
        return 0
    
    print(f"\nCalculating flamingo rating for {day_period['name']}")
    print(f"Day conditions: {day_period['shortForecast']}")
    print(f"Day temp: {day_period['temperature']}°F")
    print(f"Day wind: {day_period['windSpeed']}")
    print(f"Night temp: {night_period['temperature']}°F")
    
    # Start with perfect score of 5 flamingos
    score = 5.0
    min_day_temp = criteria.get('min_day_temp', DEFAULT_CRITERIA['min_day_temp'])
    min_night_temp = criteria.get('min_night_temp', DEFAULT_CRITERIA['min_night_temp'])
    max_wind = criteria.get('max_wind', DEFAULT_CRITERIA['max_wind'])
    
    # Day temperature rating (can lose up to 1.5 flamingos)
    day_temp = float(day_period['temperature'])
    if day_temp < min_day_temp:
        score -= 2
        print(f"Temperature below minimum (-2): {day_temp}°F < {min_day_temp}°F")
    
    # Night temperature rating (can lose up to 1.5 flamingos)
    night_temp = float(night_period['temperature'])
    if night_temp < min_night_temp:
        score -= 1
        print(f"Night temp below minimum (-1): {night_temp}°F < {min_night_temp}°F")
    
    # Wind rating (can lose up to 1 flamingo)
    day_wind = float(day_period['windSpeed'].split()[0])
    if day_wind > max_wind:
        score -= 1.0
        print(f"Wind above maximum (-1.0): {day_wind} mph > {max_wind} mph")
    
    # Conditions rating (can lose up to 1 flamingo)
    conditions = day_period['shortForecast'].lower()
    if any(x in conditions for x in ['rain', 'shower', 'storm', 'thunder']):
        score -= 1.0
        print("Poor conditions - rain/storms (-1.0)")
    elif any(x in conditions for x in ['cloudy', 'overcast']):
        score -= 0.5
        print("Suboptimal conditions - cloudy (-0.5)")
    
    # Round to nearest integer and ensure score is between 0 and 5
    score = round(score)
    score = max(0, min(5, score))
    
    print(f"Final flamingo rating: {score}")
    return score

def get_day_evaluation(day_periods, criteria):
    """Evaluate a day's weather for sunbathing."""
    day_period = None
    night_period = None
    
    # Extract day and night periods
    for period_label, period in day_periods:
        if period['isDaytime']:
            day_period = period
        else:
            night_period = period
    
    if not day_period:
        return {
            'rating': 0,
            'flamingo_explanation': "No daytime forecast available 😢",
            'day_period': None,
            'night_period': None
        }

    # Get weights from criteria or use defaults
    weights = criteria.get('weights', {'temperature': 0.4, 'wind': 0.3, 'conditions': 0.3})
    
    # Temperature evaluation
    temp = float(day_period['temperature'])
    min_temp = float(criteria['min_day_temp'])
    temp_score = 1.0 if temp >= min_temp else max(0.0, 1.0 - (min_temp - temp) / 10)
    
    # Wind evaluation
    wind_speed = float(day_period['windSpeed'].split()[0])  # Extract numeric part
    max_wind = float(criteria['max_wind'])
    wind_score = 1.0 if wind_speed <= max_wind else max(0.0, 1.0 - (wind_speed - max_wind) / 5)
    
    # Condition evaluation
    condition_score, condition_type = get_condition_score(
        day_period['shortForecast'],
        day_period.get('cloudCover'),
        criteria.get('allowed_conditions')
    )
    
    # Get the appropriate weather icon
    weather_icon = get_condition_icon(condition_type)
    
    # Calculate weighted total score
    total_score = (
        weights['temperature'] * temp_score +
        weights['wind'] * wind_score +
        weights['conditions'] * condition_score
    )
    
    # Convert to flamingo rating (1-5)
    flamingo_rating = max(1, min(5, round(total_score * 5)))
    
    # Generate explanation
    deductions = []
    if temp < min_temp:
        deductions.append(f"temperature is {temp}°F (minimum {min_temp}°F)")
    if wind_speed > max_wind:
        deductions.append(f"wind speed is {wind_speed}mph (maximum {max_wind}mph)")
    if condition_score < 0.8:  # Less than partly cloudy
        deductions.append(f"conditions are {weather_icon} {day_period['shortForecast'].lower()}")
    
    if deductions:
        explanation = f"Here's why: {', '.join(deductions)}."
    else:
        explanation = f"Perfect sunbathing conditions! {weather_icon}"
    
    return {
        'rating': flamingo_rating,
        'flamingo_explanation': explanation,
        'day_period': day_period,
        'night_period': night_period
    }

def get_condition_score(short_forecast, cloud_cover, allowed_conditions):
    # Implement the new scoring system here
    # For now, just return a score based on the presence of allowed conditions
    score = 0.0
    for condition in allowed_conditions:
        if condition.lower() in short_forecast.lower():
            score += 1.0 / len(allowed_conditions)
    return score, short_forecast

def get_condition_icon(condition):
    # Implement the new condition icon system here
    # For now, just return a default icon
    return "☀️"

HTML_TEMPLATE = r"""
<!DOCTYPE html>
<html>
<head>
    <title>Tracey's Forecaster 🌞</title>
    <style>
        body {
            font-family: system-ui, -apple-system, sans-serif;
            line-height: 1.6;
            margin: 0;
            padding: 20px;
            background: #f8f9fa;
        }
        .container {
            max-width: 800px;
            margin: 0 auto;
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        h1 {
            color: #ff6f61;
            text-align: center;
            margin-bottom: 30px;
        }
        .criteria-controls {
            background: #fff8f0;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 20px;
        }
        .criteria-row {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 20px;
            margin-bottom: 20px;
        }
        .criteria-item {
            display: flex;
            flex-direction: column;
        }
        .criteria-item label {
            font-weight: 500;
            margin-bottom: 5px;
        }
        .input-with-unit {
            display: flex;
            align-items: center;
            gap: 5px;
            margin-bottom: 8px;
        }
        .input-with-unit input[type="number"] {
            width: 80px;
            padding: 5px;
            border: 1px solid #ddd;
            border-radius: 4px;
        }
        .unit-label {
            color: #666;
            font-size: 0.9em;
        }
        .importance-slider {
            width: 100%;
            margin: 5px 0;
        }
        .slider-value {
            font-size: 0.8em;
            color: #666;
            margin-left: 5px;
        }
        .condition-options {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 10px;
            margin-top: 5px;
        }
        .condition-options label {
            display: flex;
            align-items: center;
            font-size: 0.9em;
            font-weight: normal;
        }
        .condition-options input[type="checkbox"] {
            margin-right: 5px;
        }
        .location-select {
            width: 100%;
            padding: 12px;
            margin-bottom: 20px;
            border: 2px solid #ff6f61;
            border-radius: 8px;
            font-size: 1.1em;
        }
        .submit-btn {
            width: 100%;
            padding: 15px;
            background: #ff6f61;
            color: white;
            border: none;
            border-radius: 8px;
            font-size: 1.2em;
            cursor: pointer;
            margin-top: 20px;
        }
        .submit-btn:hover {
            background: #ff5447;
        }
        .loading {
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(255,255,255,0.8);
            justify-content: center;
            align-items: center;
            font-size: 24px;
            z-index: 1000;
        }
        .loading.active {
            display: flex;
        }
        .results-breakdown {
            margin-top: 20px;
            padding: 15px;
            background: #fff0f5;
            border-radius: 6px;
        }
        .breakdown-item {
            margin: 10px 0;
            padding: 10px;
            background: white;
            border-radius: 4px;
        }
        .day-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            cursor: pointer;
            padding: 5px;
        }
        .day-header:hover {
            background: #f8f9fa;
        }
        .day-details {
            display: none;
            padding: 15px;
            background: #f8f9fa;
            margin-top: 5px;
            border-radius: 4px;
        }
        .day-details.active {
            display: block;
        }
        .breakdown {
            margin-bottom: 15px;
            line-height: 1.6;
        }
        .weather-details {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-top: 15px;
            background: white;
            padding: 12px;
            border-radius: 4px;
        }
        .weather-period {
            display: flex;
            flex-direction: column;
            gap: 5px;
        }
        .weather-period-title {
            font-weight: 600;
            color: #2c3e50;
            margin-bottom: 3px;
        }
        .weather-stat {
            display: flex;
            align-items: center;
            gap: 5px;
            color: #555;
        }
        .toggle-icon {
            font-size: 1.2em;
            transition: transform 0.3s ease;
        }
        .toggle-icon.active {
            transform: rotate(180deg);
        }
        .cloud-cover-indicator {
            display: inline-block;
            padding: 2px 8px;
            border-radius: 12px;
            background: #e3f2fd;
            font-size: 0.9em;
        }
        .results-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
        }
        .toggle-all-btn {
            background: #ff6f61;
            color: white;
            border: none;
            padding: 8px 15px;
            border-radius: 4px;
            cursor: pointer;
            font-size: 0.9em;
            transition: background 0.2s;
        }
        .toggle-all-btn:hover {
            background: #ff5447;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Tracey's Sunball Forecaster</h1>
        
        <form method="POST" onsubmit="showLoading()">
            <select name="location" class="location-select" required>
                <option value="">Select a Location</option>
                {% for loc in locations %}
                <option value="{{ loc }}">{{ loc }}</option>
                {% endfor %}
            </select>

            <div class="criteria-controls">
                <div class="criteria-row">
                    <div class="criteria-item">
                        <label>Min. Day Temp</label>
                        <div class="input-with-unit">
                            <input type="number" name="min_day_temp" value="{{ criteria.min_day_temp }}" required>
                            <span class="unit-label">°F</span>
                        </div>
                        <div style="margin-top: 5px;">
                            <label style="font-size: 0.9em; color: #666;">Temperature Importance</label>
                            <input type="range" min="0" max="100" value="40" class="importance-slider" data-factor="temperature">
                            <span class="slider-value">40% importance</span>
                        </div>
                    </div>
                    <div class="criteria-item">
                        <label>Min. Night Temp</label>
                        <div class="input-with-unit">
                            <input type="number" name="min_night_temp" value="{{ criteria.min_night_temp }}" required>
                            <span class="unit-label">°F</span>
                        </div>
                    </div>
                    <div class="criteria-item">
                        <label>Max Wind Speed</label>
                        <div class="input-with-unit">
                            <input type="number" name="max_wind" value="{{ criteria.max_wind }}" required>
                            <span class="unit-label">mph</span>
                        </div>
                        <div style="margin-top: 5px;">
                            <label style="font-size: 0.9em; color: #666;">Wind Importance</label>
                            <input type="range" min="0" max="100" value="30" class="importance-slider" data-factor="wind">
                            <span class="slider-value">30% importance</span>
                        </div>
                    </div>
                </div>

                <div class="criteria-group">
                    <label>Preferred Conditions <span class="slider-value">30% importance</span></label>
                    <input type="range" min="0" max="100" value="30" class="importance-slider" data-factor="conditions">
                    <div class="condition-options">
                        <label><input type="checkbox" name="conditions" value="clear" checked> Clear/Sunny</label>
                        <label><input type="checkbox" name="conditions" value="partly_cloudy" checked> Partly Cloudy</label>
                        <label><input type="checkbox" name="conditions" value="cloudy"> Cloudy</label>
                        <label><input type="checkbox" name="conditions" value="overcast"> Overcast</label>
                        <label><input type="checkbox" name="conditions" value="rain"> Rain</label>
                        <label><input type="checkbox" name="conditions" value="storm"> Storms</label>
                    </div>
                </div>
            </div>

            <button type="submit" class="submit-btn">Check Weather ☀️</button>
        </form>

        <div id="loading" class="loading">
            <p>🌞 Checking the weather... Please wait! 🦩</p>
        </div>

        <div id="results">
            {% if results %}
                <div class="results-breakdown">
                    <div class="results-header">
                        <h3>Weather Forecast Results</h3>
                        <button type="button" class="toggle-all-btn" onclick="toggleAllDetails()">
                            Show All Details
                        </button>
                    </div>
                    {% for day in results %}
                        <div class="breakdown-item">
                            <div class="day-header" onclick="toggleDetails(this)">
                                <h4 style="margin: 0;">{{ day.date }}</h4>
                                <div style="display: flex; align-items: center;">
                                    <div class="flamingo-rating" style="margin-right: 10px;">
                                        {{ '🦩' * day.rating }}{{ '❌' * (5 - day.rating) }}
                                    </div>
                                    <span class="toggle-icon">▼</span>
                                </div>
                            </div>
                            <div class="day-details">
                                <div class="breakdown">
                                    {{ day.flamingo_explanation|safe }}
                                </div>
                                
                                <div class="weather-details">
                                    <div class="weather-period">
                                        <div class="weather-period-title">Day Conditions</div>
                                        <div class="weather-stat">
                                            🌡️ {{ day.day_period.temperature }}°F
                                        </div>
                                        <div class="weather-stat">
                                            💨 {{ day.day_period.windSpeed }}
                                        </div>
                                        <div class="weather-stat">
                                            ☁️ {{ day.day_period.cloudCover }}% cloud cover
                                        </div>
                                        <div class="weather-stat">
                                            🌤️ {{ day.day_period.shortForecast }}
                                        </div>
                                    </div>
                                    
                                    {% if day.night_period %}
                                    <div class="weather-period">
                                        <div class="weather-period-title">Night Conditions</div>
                                        <div class="weather-stat">
                                            🌡️ {{ day.night_period.temperature }}°F
                                        </div>
                                        <div class="weather-stat">
                                            💨 {{ day.night_period.windSpeed }}
                                        </div>
                                        <div class="weather-stat">
                                            ☁️ {{ day.night_period.cloudCover }}% cloud cover
                                        </div>
                                        <div class="weather-stat">
                                            🌤️ {{ day.night_period.shortForecast }}
                                        </div>
                                    </div>
                                    {% endif %}
                                </div>
                            </div>
                        </div>
                    {% endfor %}
                </div>
            {% endif %}
        </div>
    </div>

    <script>
        document.addEventListener('DOMContentLoaded', function() {
            const form = document.querySelector('form');
            const importanceSliders = document.querySelectorAll('.importance-slider');
            const conditionCheckboxes = document.querySelectorAll('input[name="conditions"]');

            // Update slider value displays
            importanceSliders.forEach(slider => {
                const valueDisplay = slider.nextElementSibling;
                slider.addEventListener('input', () => {
                    valueDisplay.textContent = slider.value + '% importance';
                });
            });

            form.addEventListener('submit', function(e) {
                // Collect the importance weights
                const weights = {};
                importanceSliders.forEach(slider => {
                    weights[slider.dataset.factor] = parseInt(slider.value) / 100;
                });

                // Collect the allowed conditions
                const allowedConditions = [];
                conditionCheckboxes.forEach(checkbox => {
                    if (checkbox.checked) {
                        allowedConditions.push(checkbox.value);
                    }
                });

                // Add the weights and conditions to the form data
                const weightsInput = document.createElement('input');
                weightsInput.type = 'hidden';
                weightsInput.name = 'weights';
                weightsInput.value = JSON.stringify(weights);
                form.appendChild(weightsInput);

                const conditionsInput = document.createElement('input');
                conditionsInput.type = 'hidden';
                conditionsInput.name = 'allowed_conditions';
                conditionsInput.value = JSON.stringify(allowedConditions);
                form.appendChild(conditionsInput);
            });
        });

        function showLoading() {
            document.getElementById("loading").classList.add("active");
        }

        function toggleDetails(header) {
            const details = header.nextElementSibling;
            const icon = header.querySelector('.toggle-icon');
            details.classList.toggle('active');
            icon.classList.toggle('active');
        }

        function toggleAllDetails() {
            const button = document.querySelector('.toggle-all-btn');
            const allDetails = document.querySelectorAll('.day-details');
            const allIcons = document.querySelectorAll('.toggle-icon');
            const isExpanding = button.textContent.includes('Show');

            allDetails.forEach(detail => {
                if (isExpanding) {
                    detail.classList.add('active');
                } else {
                    detail.classList.remove('active');
                }
            });

            allIcons.forEach(icon => {
                if (isExpanding) {
                    icon.classList.add('active');
                } else {
                    icon.classList.remove('active');
                }
            });

            button.textContent = isExpanding ? 'Hide All Details' : 'Show All Details';
        }
    </script>
</body>
</html>
"""

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        location = request.form.get('location')
        
        # Get base criteria
        criteria = {
            'min_day_temp': int(request.form.get('min_day_temp', DEFAULT_CRITERIA['min_day_temp'])),
            'min_night_temp': int(request.form.get('min_night_temp', DEFAULT_CRITERIA['min_night_temp'])),
            'max_wind': int(request.form.get('max_wind', DEFAULT_CRITERIA['max_wind']))
        }
        
        # Get weights and allowed conditions from form
        weights_str = request.form.get('weights')
        if weights_str:
            try:
                criteria['weights'] = json.loads(weights_str)
            except json.JSONDecodeError:
                criteria['weights'] = {'temperature': 0.4, 'wind': 0.3, 'conditions': 0.3}
        
        conditions_str = request.form.get('allowed_conditions')
        if conditions_str:
            try:
                criteria['allowed_conditions'] = json.loads(conditions_str)
            except json.JSONDecodeError:
                criteria['allowed_conditions'] = DEFAULT_CRITERIA['allowed_conditions']
        
        try:
            if location not in LOCATIONS:
                raise ValueError(f"Invalid location: {location}")
            
            lat, lon = LOCATIONS[location]['lat'], LOCATIONS[location]['lon']
            forecast_data = get_forecast(lat, lon)
            parsed_forecast = parse_next_7_days(forecast_data)
            
            results = []
            for day in parsed_forecast:
                evaluation = get_day_evaluation(day['periods'], criteria)
                results.append({
                    'date': day['date'],
                    'rating': evaluation['rating'],
                    'flamingo_explanation': evaluation['flamingo_explanation'],
                    'day_period': evaluation['day_period'],
                    'night_period': evaluation['night_period']
                })
            
            return render_template_string(
                HTML_TEMPLATE,
                results=results,
                locations=LOCATIONS.keys(),
                criteria=criteria,
                error=None
            )
            
        except Exception as e:
            return render_template_string(
                HTML_TEMPLATE,
                results=None,
                locations=LOCATIONS.keys(),
                criteria=DEFAULT_CRITERIA,
                error=str(e)
            )
    
    return render_template_string(
        HTML_TEMPLATE,
        results=None,
        locations=LOCATIONS.keys(),
        criteria=DEFAULT_CRITERIA,
        error=None
    )

if __name__ == "__main__":
    app.run(debug=True, port=5001)
