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
        "Clear"
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
    
    # Print the first period to see all available data
    forecast_data = resp_forecast.json()
    first_period = forecast_data["properties"]["periods"][0]
    print("Available forecast data for each period:", first_period.keys())
    print("Sample period data:", first_period)
    
    return forecast_data

def parse_next_3_days(forecast_data):
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
    
    if not allowed_conditions:  # If no conditions are selected, none are allowed
        return False
    
    # Group periods into day/night pairs
    day_period = None
    night_period = None
    
    for period in periods:
        if period['isDaytime']:
            day_period = period
        else:
            night_period = period
            # We have a complete day/night pair, check conditions
            if day_period:  # Make sure we have both periods
                # Check day conditions
                day_temp = float(day_period['temperature'])
                day_wind = float(day_period['windSpeed'].split()[0])
                day_conditions = day_period['shortForecast']
                
                # Check night conditions
                night_temp = float(night_period['temperature'])
                
                # Day must meet all criteria
                day_temp_ok = day_temp >= min_day_temp
                day_wind_ok = day_wind <= max_wind
                day_conditions_ok = any(cond.lower() in day_conditions.lower() for cond in allowed_conditions)
                
                # Night only needs to meet temperature requirement
                night_temp_ok = night_temp >= min_night_temp
                
                if day_temp_ok and day_wind_ok and day_conditions_ok and night_temp_ok:
                    return True
                
            # Reset for next pair
            day_period = None
            night_period = None
    
    return False

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
        return 0
    
    # Check if basic requirements are met
    if not is_sunbathing_day([day_period], criteria):
        return 0
        
    score = 0
    min_day_temp = criteria.get('min_day_temp', DEFAULT_CRITERIA['min_day_temp'])
    min_night_temp = criteria.get('min_night_temp', DEFAULT_CRITERIA['min_night_temp'])
    max_wind = criteria.get('max_wind', DEFAULT_CRITERIA['max_wind'])
    
    # Day temperature rating (0-2 flamingos)
    day_temp = float(day_period['temperature'])
    if day_temp >= min_day_temp + 15:  # Perfect temp
        score += 2
    elif day_temp >= min_day_temp + 7:  # Very good temp
        score += 1
    
    # Night temperature bonus (0-0.5 flamingos)
    night_temp = float(night_period['temperature'])
    if night_temp >= min_night_temp + 5:
        score += 0.5
    
    # Wind rating (0-1 flamingo)
    day_wind = float(day_period['windSpeed'].split()[0])
    if day_wind <= max_wind - 7:  # Light breeze
        score += 1
    
    # Conditions rating (0-1.5 flamingos)
    conditions = day_period['shortForecast'].lower()
    if 'sunny' in conditions:  # Perfect sunny day
        score += 1.5
    elif 'mostly sunny' in conditions:  # Almost perfect
        score += 1
    elif 'partly sunny' in conditions:  # Good enough
        score += 0.5
    elif 'clear' in conditions:  # Clear but not specified as sunny
        score += 0.5
    
    # Round to nearest 0.5
    score = round(score * 2) / 2
    
    # Add minimum 1 flamingo if it meets basic requirements
    if score < 1 and is_sunbathing_day([day_period], criteria):
        score = 1
    
    return score

def get_day_evaluation(day_periods, criteria):
    """Get a detailed evaluation of the entire day for sunbathing."""
    # Find the day and night periods
    day_period = None
    night_period = None
    for label, period in day_periods:
        if period['isDaytime']:
            day_period = period
        else:
            night_period = period
    
    if not day_period or not night_period:
        return ["⚠️ Incomplete day/night data"]
    
    min_day_temp = criteria.get('min_day_temp', DEFAULT_CRITERIA['min_day_temp'])
    min_night_temp = criteria.get('min_night_temp', DEFAULT_CRITERIA['min_night_temp'])
    max_wind = criteria.get('max_wind', DEFAULT_CRITERIA['max_wind'])
    
    evaluation = []
    
    # Day temperature evaluation
    day_temp = float(day_period['temperature'])
    if day_temp >= min_day_temp + 15:
        evaluation.append("🌡️ Perfect daytime temperature!")
    elif day_temp >= min_day_temp + 7:
        evaluation.append("🌡️ Very comfortable daytime temperature")
    elif day_temp >= min_day_temp:
        evaluation.append("🌡️ Daytime temperature meets minimum requirements")
    else:
        evaluation.append("❄️ Too cold during the day for sunbathing")
    
    # Night temperature evaluation
    night_temp = float(night_period['temperature'])
    if night_temp >= min_night_temp + 5:
        evaluation.append("🌙 Perfect night temperature!")
    elif night_temp >= min_night_temp:
        evaluation.append("🌙 Comfortable night temperature")
    else:
        evaluation.append("🌙 Too cold at night")
    
    # Wind evaluation
    day_wind = float(day_period['windSpeed'].split()[0])
    if day_wind <= max_wind - 7:
        evaluation.append("🍃 Perfect light breeze")
    elif day_wind <= max_wind:
        evaluation.append("💨 Acceptable wind conditions")
    else:
        evaluation.append("🌪️ Too windy for comfort")
    
    # Sun conditions evaluation
    conditions = day_period['shortForecast'].lower()
    if 'sunny' in conditions:
        evaluation.append("☀️ Perfect sunny conditions!")
    elif 'mostly sunny' in conditions:
        evaluation.append("🌤️ Very good sun exposure")
    elif 'partly sunny' in conditions or 'partly cloudy' in conditions:
        evaluation.append("⛅ Moderate sun exposure")
    elif 'clear' in conditions:
        evaluation.append("🌅 Clear skies")
    else:
        evaluation.append("☁️ Not ideal sun conditions")
    
    return evaluation

HTML_TEMPLATE = r"""
<!DOCTYPE html>
<html>
<head>
    <title>Tracey's Forecast 🌞</title>
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
            margin: 15px 0;
            border: 2px solid #ffb6c1;
            border-radius: 8px;
            font-size: 1.1em;
            background-color: white;
            cursor: pointer;
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
        .flamingo-display {
            text-align: center;
            padding: 20px;
            font-size: 4em;
            margin: 15px 0;
        }
        .day-container {
            margin: 30px 0;
            border: 2px solid #ffb6c1;
            border-radius: 10px;
            overflow: hidden;
        }
        .day-header {
            background-color: #fff0f5;
            padding: 15px;
            border-bottom: 2px solid #ffb6c1;
            text-align: center;
        }
        .day-title {
            font-size: 1.5em;
            font-weight: bold;
            color: #ff69b4;
            margin-bottom: 15px;
        }
        .periods-container {
            display: flex;
            gap: 20px;
            padding: 20px;
        }
        .period-details {
            flex: 1;
            padding: 20px;
            border-radius: 8px;
            background-color: #fff0f5;
        }
        .period-title {
            font-size: 1.2em;
            font-weight: bold;
            color: #ff69b4;
            margin-bottom: 15px;
            text-align: center;
        }
        .weather-stats {
            background-color: white;
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 15px;
        }
        .weather-stat {
            margin: 10px 0;
        }
        .detailed-forecast {
            font-style: italic;
            color: #666;
            line-height: 1.4;
            font-size: 0.9em;
        }
        .criteria-selector {
            background-color: #fff0f5;
            padding: 20px;
            border-radius: 10px;
            margin: 20px 0;
            border: 2px solid #ffb6c1;
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
    </style>
</head>
<body>
    <div class="container">
        <h1>Tracey's Forecast 🌞</h1>
        
        <form method="POST" onsubmit="showLoading()">
            <select name="location" class="location-select">
                {% for loc in locations %}
                <option value="{{ loc }}" {% if loc == 'Miami' %}selected{% endif %}>{{ loc }}</option>
                {% endfor %}
            </select>

            <div class="criteria-selector">
                <div class="criteria-row">
                    <div class="criteria-group">
                        <label>Minimum Day Temperature (°F):
                            <input type="number" name="min_day_temp" value="{{ criteria.get('min_day_temp', 75) }}">
                        </label>
                        <label>Minimum Night Temperature (°F):
                            <input type="number" name="min_night_temp" value="{{ criteria.get('min_night_temp', 65) }}">
                        </label>
                        <label>Maximum Wind Speed (mph):
                            <input type="number" name="max_wind" value="{{ criteria.get('max_wind', 15) }}">
                        </label>
                    </div>
                    <div class="criteria-group">
                        <label>Weather Conditions:</label>
                        {% for condition in ['Sunny', 'Mostly Sunny', 'Partly Sunny', 'Partly Cloudy', 'Clear'] %}
                        <label class="checkbox-label">
                            <input type="checkbox" name="conditions" value="{{ condition }}"
                                {% if condition in criteria.get('allowed_conditions', []) %}checked{% endif %}>
                            {{ condition }}
                        </label>
                        {% endfor %}
                    </div>
                </div>
            </div>
            
            <button type="submit" class="submit-btn">Check Weather</button>
        </form>

        <div id="loading" class="loading">
            <p>💅 Checking the sunshine... Please wait! 🌞</p>
        </div>

        {% if request.method == 'POST' %}
        <div class="summary-box">
            <h3>Current Settings</h3>
            <p><strong>Minimum Day Temperature:</strong> {{ criteria.get('min_day_temp') }}°F</p>
            <p><strong>Minimum Night Temperature:</strong> {{ criteria.get('min_night_temp') }}°F</p>
            <p><strong>Maximum Wind Speed:</strong> {{ criteria.get('max_wind') }} mph</p>
            <p><strong>Weather Conditions:</strong> {{ ', '.join(criteria.get('allowed_conditions', [])) }}</p>
            <p><strong>Selected Location:</strong> {{ location }}</p>
        </div>
        {% endif %}
        
        {% if results %}
        <div class="results">
            {% for location, days in results.items() %}
            <div class="location-results">
                <div class="location-name">{{ location }}</div>
                {% for day in days %}
                    {% set flamingo_rating = calculate_day_flamingo_rating(day.periods, criteria) %}
                    <div class="day-container">
                        <div class="day-header">
                            <div class="day-title">{{ day.date }}</div>
                            {% if flamingo_rating > 0 %}
                            <div class="flamingo-display">
                                {{ "🦩" * (flamingo_rating|int) }}
                            </div>
                            {% endif %}
                        </div>
                        
                        <div class="periods-container">
                            {% for period_label, period in day.periods %}
                                <div class="period-details">
                                    <div class="period-title">{{ period_label }}</div>
                                    <div class="weather-stats">
                                        <div class="weather-stat">
                                            <strong>Temperature:</strong> {{ period.temperature }}°{{ period.temperatureUnit }}
                                        </div>
                                        <div class="weather-stat">
                                            <strong>Wind:</strong> {{ period.windSpeed }} {{ period.windDirection }}
                                        </div>
                                        <div class="weather-stat">
                                            <strong>Conditions:</strong> {{ period.shortForecast }}
                                        </div>
                                    </div>
                                    <div class="detailed-forecast">
                                        {{ period.detailedForecast }}
                                    </div>
                                </div>
                            {% endfor %}
                        </div>
                    </div>
                {% endfor %}
            </div>
            {% endfor %}
        </div>
        {% endif %}
    </div>
    <script>
        function showLoading() {
            document.getElementById("loading").classList.add("active");
        }
    </script>
</body>
</html>
"""

@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        # Get user criteria
        user_criteria = {}
        user_criteria['min_day_temp'] = int(request.form.get('min_day_temp', DEFAULT_CRITERIA['min_day_temp']))
        user_criteria['min_night_temp'] = int(request.form.get('min_night_temp', DEFAULT_CRITERIA['min_night_temp']))
        user_criteria['max_wind'] = int(request.form.get('max_wind', DEFAULT_CRITERIA['max_wind']))
        user_criteria['allowed_conditions'] = request.form.getlist('conditions') or DEFAULT_CRITERIA['allowed_conditions']

        selected_locations = request.form.getlist("location")
        if not selected_locations:
            return "Please select at least one location."

        results = {}
        for location in selected_locations:
            if location not in LOCATIONS:
                continue
            lat = LOCATIONS[location]["lat"]
            lon = LOCATIONS[location]["lon"]
            
            try:
                forecast_data = get_forecast(lat, lon)
                days = parse_next_3_days(forecast_data)
                results[location] = days
            except Exception as e:
                print(f"Error getting forecast for {location}: {e}")
                continue

        return render_template_string(
            HTML_TEMPLATE,
            locations=LOCATIONS.keys(),
            results=results,
            criteria=user_criteria,
            location=selected_locations[0],
            is_sunbathing_day=is_sunbathing_day,
            calculate_day_flamingo_rating=calculate_day_flamingo_rating,
            get_day_evaluation=get_day_evaluation
        )

    return render_template_string(
        HTML_TEMPLATE,
        locations=LOCATIONS.keys(),
        results={},
        criteria=DEFAULT_CRITERIA,
        is_sunbathing_day=is_sunbathing_day,
        calculate_day_flamingo_rating=calculate_day_flamingo_rating,
        get_day_evaluation=get_day_evaluation
    )

if __name__ == "__main__":
    app.run(debug=True)
