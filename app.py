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
            "isDaytime": period["isDaytime"]
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
    """Get a detailed evaluation of the entire day for sunbathing."""
    day_period = None
    night_period = None
    for label, period in day_periods:
        if period['isDaytime']:
            day_period = period
        else:
            night_period = period
    
    if not day_period or not night_period:
        return {
            'rating': 0,
            'flamingo_explanation': "Unable to rate - missing day or night data",
            'day_period': day_period,
            'night_period': night_period
        }
    
    # Track deductions and explanations
    deductions = []
    min_day_temp = criteria.get('min_day_temp', DEFAULT_CRITERIA['min_day_temp'])
    min_night_temp = criteria.get('min_night_temp', DEFAULT_CRITERIA['min_night_temp'])
    max_wind = criteria.get('max_wind', DEFAULT_CRITERIA['max_wind'])
    
    # Start with perfect score
    score = 5.0
    
    # Day temperature assessment
    day_temp = float(day_period['temperature'])
    if day_temp < min_day_temp:
        score -= 2
        deductions.append(f"🌡️ Day temperature is {day_temp}°F, which is below the minimum {min_day_temp}°F (-2 flamingos)")
    
    # Night temperature assessment
    night_temp = float(night_period['temperature'])
    if night_temp < min_night_temp:
        score -= 1
        deductions.append(f"🌙 Night temperature drops to {night_temp}°F, below the minimum {min_night_temp}°F (-1 flamingo)")
    
    # Wind assessment
    day_wind = float(day_period['windSpeed'].split()[0])
    if day_wind > max_wind:
        score -= 1.0
        deductions.append(f"💨 Wind speed of {day_wind} mph makes sunbathing less comfortable (-1 flamingo)")
    
    # Conditions assessment
    conditions = day_period['shortForecast'].lower()
    if any(x in conditions for x in ['rain', 'shower', 'storm', 'thunder']):
        score -= 1.0
        deductions.append(f"🌧️ Weather conditions show {day_period['shortForecast']} - less suitable for sunbathing (-1 flamingo)")
    elif any(x in conditions for x in ['cloudy', 'overcast']):
        score -= 1.0
        deductions.append(f"☁️ {day_period['shortForecast']} - reduced sun exposure (-1 flamingo)")
    
    # Round to nearest integer and ensure score is between 0 and 5
    score = round(score)
    score = max(0, min(5, score))
    
    # Create the explanation
    if score == 5:
        explanation = "🦩🦩🦩🦩🦩 Perfect sunbathing conditions! All parameters are ideal."
    elif score == 0:
        explanation = "❌ Not suitable for sunbathing today.\n\n"
    else:
        explanation = f"🦩 {score} flamingos for today.\n\n"
        
    if deductions:
        explanation += "Here's why:\n\n"
        for deduction in deductions:
            explanation += f"• {deduction}\n"
    
    return {
        'rating': score,
        'flamingo_explanation': explanation,
        'day_period': day_period,
        'night_period': night_period
    }

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
            background-color: #fff5f5;
            color: #2c3e50;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            padding: 30px;
            border-radius: 15px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        h1 {
            color: #ff69b4;
            text-align: center;
            font-size: 2.8em;
            margin-bottom: 30px;
            text-shadow: 1px 1px 2px rgba(0,0,0,0.1);
        }
        .location-select {
            width: 100%;
            padding: 12px;
            margin-bottom: 10px;
            border: 2px solid #ffb6c1;
            border-radius: 8px;
            font-size: 1.1em;
            background-color: white;
            cursor: pointer;
        }
        .custom-location {
            display: none;
            margin-top: 10px;
        }
        .custom-location.active {
            display: block;
        }
        .custom-location input {
            width: calc(50% - 10px);
            padding: 8px;
            margin: 5px;
            border: 1px solid #ffb6c1;
            border-radius: 4px;
        }
        .custom-location label {
            display: block;
            margin: 5px;
            color: #666;
            font-size: 0.9em;
        }
        .submit-btn {
            width: 100%;
            padding: 15px;
            margin: 20px 0;
            background-color: #ff69b4;
            color: white;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-size: 1.2em;
            font-weight: 600;
            transition: background-color 0.3s ease;
        }
        .submit-btn:hover {
            background-color: #ff1493;
        }
        .criteria-selector {
            background-color: #fff0f5;
            padding: 20px;
            border-radius: 10px;
            margin: 20px 0;
            border: 2px solid #ffb6c1;
        }
        .criteria-row {
            display: flex;
            gap: 20px;
            flex-wrap: wrap;
        }
        .criteria-group {
            flex: 1;
            min-width: 300px;
        }
        .criteria-group label {
            display: block;
            margin: 10px 0;
        }
        .criteria-group input[type="number"] {
            width: 80px;
            padding: 5px;
            border: 1px solid #ffb6c1;
            border-radius: 4px;
            margin-left: 10px;
        }
        .checkbox-group {
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
            margin-top: 10px;
        }
        .checkbox-label {
            display: flex;
            align-items: center;
            background: white;
            padding: 8px 12px;
            border-radius: 20px;
            border: 1px solid #ffb6c1;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        .checkbox-label:hover {
            background: #fff0f5;
        }
        .checkbox-label input {
            margin-right: 8px;
        }
        .checkbox-label.checked {
            background: #ff69b4;
            color: white;
            border-color: #ff69b4;
        }
        
        .day-forecast {
            margin: 30px 0;
            border: 2px solid #ffb6c1;
            border-radius: 10px;
            overflow: hidden;
            cursor: pointer;
        }
        
        .day-header {
            background-color: #fff0f5;
            padding: 15px;
            border-bottom: 2px solid #ffb6c1;
            display: flex;
            justify-content: space-between;
            align-items: center;
            transition: background-color 0.3s ease;
        }
        
        .day-forecast:hover .day-header {
            background-color: #ffe0eb;
        }
        
        .date {
            font-size: 1.5em;
            font-weight: bold;
            color: #ff69b4;
        }
        
        .flamingo-rating {
            font-size: 2.5em;
        }
        
        .conditions {
            padding: 20px;
            background: white;
            display: none;  /* Hidden by default */
            transition: all 0.3s ease;
        }
        
        .conditions.active {
            display: block;
        }
        
        .expand-icon {
            font-size: 1.2em;
            margin-left: 10px;
            transition: transform 0.3s ease;
        }
        
        .day-forecast.active .expand-icon {
            transform: rotate(180deg);
        }
        
        .flamingo-explanation {
            background: #fff0f5;
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 15px;
            border-left: 4px solid #ff69b4;
        }
        
        .day-conditions, .night-conditions {
            margin: 10px 0;
            padding: 10px;
            background: #fff0f5;
            border-radius: 6px;
        }
        
        .detailed-forecast {
            font-style: italic;
            color: #666;
            margin-top: 10px;
            font-size: 0.9em;
        }
        
        .location-name {
            font-size: 1.4em;
            font-weight: 600;
            color: #ff69b4;
            margin-bottom: 15px;
            padding-bottom: 10px;
            border-bottom: 2px solid #ffb6c1;
            text-align: center;
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
            color: #ff69b4;
        }
        
        .loading.active {
            display: flex;
        }
        
        .error-message {
            background-color: #ffe6e6;
            border: 2px solid #ff69b4;
            color: #ff1493;
            padding: 15px;
            border-radius: 8px;
            margin: 20px 0;
            text-align: center;
            font-weight: bold;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Tracey's Forecast 🌞</h1>
        
        {% if error %}
        <div class="error-message">
            {{ error }}
        </div>
        {% endif %}
        
        <form method="POST" onsubmit="showLoading()">
            <div class="criteria-selector">
                <div class="criteria-row">
                    <div class="criteria-group">
                        <label>Select Locations:</label>
                        {% for location in locations %}
                        <div class="checkbox-label">
                            <input type="checkbox" name="selected_locations" value="{{ location }}" 
                                   {% if location in selected_locations %}checked{% endif %}>
                            {{ location }}
                        </div>
                        {% endfor %}
                    </div>
                    <div class="criteria-group">
                        <label>Minimum Day Temperature (°F):
                            <input type="number" name="min_day_temp" value="{{ criteria.min_day_temp }}" min="0" max="120">
                        </label>
                        <label>Minimum Night Temperature (°F):
                            <input type="number" name="min_night_temp" value="{{ criteria.min_night_temp }}" min="0" max="120">
                        </label>
                        <label>Maximum Wind Speed (mph):
                            <input type="number" name="max_wind" value="{{ criteria.max_wind }}" min="0" max="50">
                        </label>
                    </div>
                    <div class="criteria-group">
                        <label>Allowed Weather Conditions:</label>
                        <div class="checkbox-group">
                            {% for condition in default_criteria.allowed_conditions %}
                            <div class="checkbox-label">
                                <input type="checkbox" name="allowed_conditions" value="{{ condition }}"
                                       {% if condition in criteria.allowed_conditions %}checked{% endif %}>
                                {{ condition }}
                            </div>
                            {% endfor %}
                        </div>
                    </div>
                </div>
                <button type="submit" class="submit-btn">Check Weather ☀️</button>
            </div>
        </form>
        
        <div id="loading" class="loading">
            <p>💅 Checking the sunshine... Please wait! 🌞</p>
        </div>
        
        <div class="results">
            {% for location, days in results.items() %}
            <div class="location-results">
                <div class="location-name">{{ location }}</div>
                {% for day in days %}
                <div class="day-forecast" onclick="toggleDetails(this)">
                    <div class="day-header">
                        <div class="date">{{ day.date }}</div>
                        <div style="display: flex; align-items: center;">
                            <div class="flamingo-rating">
                                {% if day.rating == 0 %}
                                    ❌
                                {% else %}
                                    {% for i in range(day.rating) %}🦩{% endfor %}
                                {% endif %}
                            </div>
                            <span class="expand-icon">▼</span>
                        </div>
                    </div>
                    <div class="conditions">
                        <div class="flamingo-explanation">
                            {{ day.flamingo_explanation|replace('\n', '<br>')|safe }}
                        </div>
                        <div class="day-conditions">
                            <strong>Day:</strong> {{ day.day_period.shortForecast }}
                            ({{ day.day_period.temperature }}°{{ day.day_period.temperatureUnit }},
                            {{ day.day_period.windSpeed }})
                        </div>
                        <div class="night-conditions">
                            <strong>Night:</strong> {{ day.night_period.shortForecast }}
                            ({{ day.night_period.temperature }}°{{ day.night_period.temperatureUnit }},
                            {{ day.night_period.windSpeed }})
                        </div>
                        <div class="detailed-forecast">
                            {{ day.day_period.detailedForecast }}
                        </div>
                    </div>
                </div>
                {% endfor %}
            </div>
            {% endfor %}
        </div>
    </div>
    <script>
        function showLoading() {
            document.getElementById("loading").classList.add("active");
        }
        
        function toggleDetails(element) {
            element.classList.toggle('active');
            const conditions = element.querySelector('.conditions');
            conditions.classList.toggle('active');
        }
        
        // Update checkbox label styling when checked/unchecked
        document.querySelectorAll('.checkbox-label input[type="checkbox"]').forEach(checkbox => {
            checkbox.addEventListener('change', function() {
                this.parentElement.classList.toggle('checked', this.checked);
            });
            // Initialize state
            checkbox.parentElement.classList.toggle('checked', checkbox.checked);
        });
    </script>
</body>
</html>
"""

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        # Get selected locations
        selected_locations = request.form.getlist('selected_locations')
        if not selected_locations:
            return render_template_string(
                HTML_TEMPLATE,
                results={},
                locations=LOCATIONS.keys(),
                criteria=DEFAULT_CRITERIA,
                default_criteria=DEFAULT_CRITERIA,
                selected_locations=['Fort Lauderdale'],
                error="Please select at least one location! 🌴"
            )
            
        # Get user criteria from form
        user_criteria = {
            'min_day_temp': float(request.form.get('min_day_temp', DEFAULT_CRITERIA['min_day_temp'])),
            'min_night_temp': float(request.form.get('min_night_temp', DEFAULT_CRITERIA['min_night_temp'])),
            'max_wind': float(request.form.get('max_wind', DEFAULT_CRITERIA['max_wind'])),
            'allowed_conditions': request.form.getlist('allowed_conditions') or DEFAULT_CRITERIA['allowed_conditions']
        }
        
        results = {}
        for location in selected_locations:
            if location not in LOCATIONS:
                continue
                
            lat, lon = LOCATIONS[location]['lat'], LOCATIONS[location]['lon']
            try:
                forecast_data = get_forecast(lat, lon)
                days = parse_next_7_days(forecast_data)
                results[location] = []
                
                for day in days:
                    day_periods = []
                    day_period = None
                    night_period = None
                    
                    # Extract day and night periods
                    for period_label, period in day['periods']:
                        if period['isDaytime']:
                            day_period = period
                        else:
                            night_period = period
                    
                    if day_period and night_period:
                        evaluation = get_day_evaluation([(None, day_period), (None, night_period)], user_criteria)
                        results[location].append({
                            'date': day['date'],
                            'rating': evaluation['rating'],
                            'flamingo_explanation': evaluation['flamingo_explanation'],
                            'day_period': evaluation['day_period'],
                            'night_period': evaluation['night_period']
                        })
            except Exception as e:
                print(f"Error getting forecast for {location}: {e}")
                continue
        
        return render_template_string(
            HTML_TEMPLATE,
            results=results,
            locations=LOCATIONS.keys(),
            criteria=user_criteria,
            default_criteria=DEFAULT_CRITERIA,
            selected_locations=selected_locations,
            error=None
        )
    
    return render_template_string(
        HTML_TEMPLATE,
        results={},
        locations=LOCATIONS.keys(),
        criteria=DEFAULT_CRITERIA,
        default_criteria=DEFAULT_CRITERIA,
        selected_locations=['Fort Lauderdale'],
        error=None
    )

if __name__ == "__main__":
    app.run(debug=True, port=5001)
