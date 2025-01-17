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
    
    for period in periods:
        temp = float(period['temperature'])
        wind_speed = float(period['windSpeed'].split()[0])  # Extract number from "10 mph"
        conditions = period['shortForecast']
        is_day = period['isDaytime']
        
        min_temp = min_day_temp if is_day else min_night_temp
        
        if temp < min_temp:
            return False
        if wind_speed > max_wind:
            return False
        if not any(cond.lower() in conditions.lower() for cond in allowed_conditions):
            return False
    return True

HTML_TEMPLATE = r"""
<!DOCTYPE html>
<html>
<head>
    <title>Sunbathing Weather Checker</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .container {
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        h1, h2 {
            color: #2c3e50;
            text-align: center;
            margin: 10px 0;
        }
        .criteria-selector {
            margin-bottom: 15px;
            padding: 15px;
            background: #f8f9fa;
            border-radius: 5px;
        }
        .criteria-row {
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 10px;
            margin-bottom: 10px;
        }
        .criteria-group {
            flex: 1;
            min-width: 200px;
        }
        .location-selector {
            display: flex;
            justify-content: center;
            gap: 20px;
            margin: 10px 0;
        }
        input[type="number"] {
            width: 60px;
            padding: 5px;
            border: 1px solid #ddd;
            border-radius: 4px;
        }
        label {
            font-size: 14px;
            color: #34495e;
            margin-right: 10px;
        }
        button {
            background-color: #3498db;
            color: white;
            padding: 8px 16px;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-size: 14px;
            width: 100%;
            max-width: 200px;
            margin: 10px auto;
            display: block;
        }
        .results {
            margin-top: 15px;
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 15px;
        }
        .location-results {
            background: #f8f9fa;
            padding: 15px;
            border-radius: 5px;
        }
        .location-name {
            font-size: 16px;
            font-weight: bold;
            margin-bottom: 10px;
            color: #2c3e50;
        }
        .day-forecast {
            margin: 8px 0;
            padding: 8px;
            background: white;
            border-radius: 5px;
            font-size: 13px;
        }
        .good-day { border-left: 4px solid #27ae60; }
        .bad-day { border-left: 4px solid #e74c3c; }
        .weather-details {
            margin: 5px 0;
            line-height: 1.3;
        }
        .summary-box {
            background: #e8f4f8;
            padding: 10px;
            border-radius: 5px;
            margin-bottom: 15px;
            font-size: 13px;
        }
        .summary-box p {
            margin: 5px 0;
        }
        .weather-icon {
            font-size: 20px;
            margin-right: 5px;
        }
        .info-tooltip {
            position: relative;
            display: inline-block;
            cursor: help;
        }
        .info-tooltip .tooltip-text {
            visibility: hidden;
            width: 200px;
            background-color: #555;
            color: #fff;
            text-align: center;
            border-radius: 6px;
            padding: 5px;
            position: absolute;
            z-index: 1;
            bottom: 125%;
            left: 50%;
            margin-left: -100px;
            opacity: 0;
            transition: opacity 0.3s;
        }
        .info-tooltip:hover .tooltip-text {
            visibility: visible;
            opacity: 1;
        }
        .detailed-forecast {
            font-style: italic;
            margin-top: 5px;
            font-size: 13px;
            color: #666;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🌞 Sunbathing Weather Checker</h1>
        
        {% if request.method == 'POST' %}
        <div class="summary-box">
            <h3>Current Settings</h3>
            <p><strong>Minimum Day Temperature:</strong> {{ criteria.get('min_day_temp') }}°F</p>
            <p><strong>Minimum Night Temperature:</strong> {{ criteria.get('min_night_temp') }}°F</p>
            <p><strong>Maximum Wind Speed:</strong> {{ criteria.get('max_wind') }} mph</p>
            <p><strong>Weather Conditions:</strong> {{ ', '.join(criteria.get('allowed_conditions', [])) }}</p>
            <p><strong>Selected Locations:</strong> {{ ', '.join(request.form.getlist('locations')) }}</p>
        </div>
        {% endif %}
        
        <form method="post">
            <div class="criteria-selector">
                <div class="criteria-row">
                    <div class="criteria-group">
                        <label>Min Day Temp (°F):
                            <input type="number" name="min_day_temp" value="{{ criteria.get('min_day_temp', 75) }}" min="0" max="120">
                        </label>
                        <label>Min Night Temp (°F):
                            <input type="number" name="min_night_temp" value="{{ criteria.get('min_night_temp', 65) }}" min="0" max="120">
                        </label>
                        <label>Max Wind (mph):
                            <input type="number" name="max_wind" value="{{ criteria.get('max_wind', 15) }}" min="0" max="50">
                        </label>
                    </div>
                    <div class="criteria-group">
                        <div class="criteria-title">
                            Acceptable Weather Conditions 
                            <span class="info-tooltip">ℹ️
                                <span class="tooltip-text">
                                    Sunny: Full sun with no clouds
                                    Mostly Sunny: 70-90% sun coverage
                                    Partly Sunny: 40-70% sun coverage
                                    Clear: No clouds (typically used for nighttime)
                                </span>
                            </span>
                        </div>
                        {% for condition in ['Sunny', 'Mostly Sunny', 'Partly Sunny', 'Clear'] %}
                        <label>
                            <input type="checkbox" name="conditions" value="{{ condition }}"
                                {% if condition in criteria.get('allowed_conditions', []) %}checked{% endif %}>
                            {{ condition }}
                        </label>
                        {% endfor %}
                    </div>
                </div>
                
                <div class="location-selector">
                    {% for location in locations %}
                    <label>
                        <input type="checkbox" id="{{ location }}" name="locations" value="{{ location }}">
                        {{ location }}
                    </label>
                    {% endfor %}
                </div>
            </div>
            
            <button type="submit">Check Weather</button>
        </form>
        
        {% if results %}
        <div class="results">
            {% for location, days in results.items() %}
            <div class="location-results">
                <div class="location-name">{{ location }}</div>
                {% for day in days %}
                <div class="day-forecast {% if day.is_good %}good-day{% else %}bad-day{% endif %}">
                    {{ day.date | safe }}<br>
                    {% for label, period in day.periods %}
                    <div class="weather-details">
                        <strong>{{ label }}:</strong> {{ period.temperature }}°{{ period.temperatureUnit }}
                        <br>
                        <span class="weather-icon">🌡️</span> {{ period.temperature }}°{{ period.temperatureUnit }}
                        <br>
                        <span class="weather-icon">🌤️</span> {{ period.shortForecast }}
                        <br>
                        <span class="weather-icon">💨</span> Wind: {{ period.windSpeed }} {{ period.windDirection }}
                        <div class="detailed-forecast">
                            {{ period.detailedForecast }}
                        </div>
                    </div>
                    {% if not loop.last %}<hr>{% endif %}
                    {% endfor %}
                    {% if day.is_good %}
                    <br>✨ Great for sunbathing!
                    {% else %}
                    <br>❌ Not ideal for sunbathing
                    {% endif %}
                </div>
                {% endfor %}
            </div>
            {% endfor %}
        </div>
        {% endif %}
    </div>
</body>
</html>
"""

@app.route("/", methods=["GET", "POST"])
def home():
    selected_locations = []
    results_html = {}
    user_criteria = DEFAULT_CRITERIA.copy()

    if request.method == "POST":
        # Get user criteria
        user_criteria['min_day_temp'] = int(request.form.get('min_day_temp', DEFAULT_CRITERIA['min_day_temp']))
        user_criteria['min_night_temp'] = int(request.form.get('min_night_temp', DEFAULT_CRITERIA['min_night_temp']))
        user_criteria['max_wind'] = int(request.form.get('max_wind', DEFAULT_CRITERIA['max_wind']))
        user_criteria['allowed_conditions'] = request.form.getlist('conditions') or DEFAULT_CRITERIA['allowed_conditions']

        selected_locations = request.form.getlist("locations")
        if not selected_locations:
            return "Please select at least one location."
        
        for loc in selected_locations:
            lat = LOCATIONS[loc]["lat"]
            lon = LOCATIONS[loc]["lon"]
            try:
                forecast_json = get_forecast(lat, lon)
                parsed_data = parse_next_3_days(forecast_json)
                results_html[loc] = []
                
                for day_info in parsed_data:
                    date_str = day_info["date"]
                    day_periods = day_info["periods"]
                    sunbathing_yes = is_sunbathing_day(
                        [period[1] for period in day_periods],
                        user_criteria
                    )
                    
                    results_html[loc].append({
                        "date": Markup(f"<strong>{date_str}</strong>"),
                        "periods": day_periods,
                        "is_good": sunbathing_yes
                    })
            except Exception as e:
                results_html[loc] = [{
                    "date": "",
                    "periods": [],
                    "is_good": False,
                    "forecast": Markup(f"Error fetching data: {e}")
                }]

    return render_template_string(
        HTML_TEMPLATE,
        locations=LOCATIONS.keys(),
        results=results_html,
        criteria=user_criteria
    )

if __name__ == "__main__":
    app.run(debug=True)
