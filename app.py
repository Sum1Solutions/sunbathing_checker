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
    
    # Check if basic requirements are met
    if not is_sunbathing_day([day_period], criteria):
        print(f"Basic requirements not met for day")
        return 0
        
    score = 0
    min_day_temp = criteria.get('min_day_temp', DEFAULT_CRITERIA['min_day_temp'])
    min_night_temp = criteria.get('min_night_temp', DEFAULT_CRITERIA['min_night_temp'])
    max_wind = criteria.get('max_wind', DEFAULT_CRITERIA['max_wind'])
    
    # Day temperature rating (0-2 flamingos)
    day_temp = float(day_period['temperature'])
    if day_temp >= min_day_temp + 15:  # Perfect temp
        score += 2
        print(f"Perfect day temp (+2): {day_temp}°F >= {min_day_temp + 15}°F")
    elif day_temp >= min_day_temp + 7:  # Very good temp
        score += 1
        print(f"Very good day temp (+1): {day_temp}°F >= {min_day_temp + 7}°F")
    else:
        print(f"Basic day temp (0): {day_temp}°F")
    
    # Night temperature bonus (0-0.5 flamingos)
    night_temp = float(night_period['temperature'])
    if night_temp >= min_night_temp + 5:
        score += 0.5
        print(f"Good night temp (+0.5): {night_temp}°F >= {min_night_temp + 5}°F")
    else:
        print(f"Basic night temp (0): {night_temp}°F")
    
    # Wind rating (0-1 flamingo)
    day_wind = float(day_period['windSpeed'].split()[0])
    if day_wind <= max_wind - 7:  # Light breeze
        score += 1
        print(f"Light wind (+1): {day_wind} mph <= {max_wind - 7} mph")
    else:
        print(f"Moderate/strong wind (0): {day_wind} mph")
    
    # Conditions rating (0-1.5 flamingos)
    conditions = day_period['shortForecast'].lower()
    if 'sunny' in conditions and not any(x in conditions for x in ['scattered', 'rain', 'shower']):
        score += 1.5
        print("Perfect sunny day (+1.5)")
    elif 'mostly sunny' in conditions and not any(x in conditions for x in ['scattered', 'rain', 'shower']):
        score += 1
        print("Almost perfect sunny day (+1)")
    elif 'partly sunny' in conditions and not any(x in conditions for x in ['scattered', 'rain', 'shower']):
        score += 0.5
        print("Partly sunny day (+0.5)")
    elif 'clear' in conditions:
        score += 0.5
        print("Clear day (+0.5)")
    elif ('scattered' in conditions and ('rain' in conditions or 'shower' in conditions)):
        score += 0.25
        print("Scattered rain day (+0.25)")
    else:
        print(f"Other conditions (0): {conditions}")
    
    # Round to nearest 0.5
    score = round(score * 2) / 2
    
    # Add minimum 1 flamingo if it meets basic requirements
    if score < 1 and is_sunbathing_day([day_period], criteria):
        score = 1
        print("Minimum score applied (+1)")
    
    print(f"Final flamingo score: {score}")
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
    if 'sunny' in conditions and 'scattered' not in conditions:
        evaluation.append("☀️ Perfect sunny conditions!")
    elif 'mostly sunny' in conditions and 'scattered' not in conditions:
        evaluation.append("🌤️ Very good sun exposure")
    elif 'partly sunny' in conditions or 'partly cloudy' in conditions:
        evaluation.append("⛅ Moderate sun exposure")
    elif 'clear' in conditions:
        evaluation.append("🌅 Clear skies")
    elif 'scattered' in conditions:
        evaluation.append("🌦️ Scattered rain conditions")
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
        .flamingo-display {
            text-align: center;
            padding: 10px;
            font-size: 2.5em;
            margin: 10px 0;
            min-height: 60px;
        }
        .flamingo-display .no-sunbathing {
            font-size: 0.5em;
            color: #666;
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
            text-align: center;
            padding: 20px;
            font-size: 1.2em;
            color: #ff69b4;
        }
        .loading.active {
            display: block;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Tracey's Forecast 🌞</h1>
        
        <form method="POST" onsubmit="showLoading()">
            <div class="criteria-selector">
                <div class="criteria-row">
                    <div class="criteria-group">
                        <h3>Location</h3>
                        <select name="location" class="location-select" onchange="toggleCustomLocation(this.value)">
                            {% for loc in locations %}
                            <option value="{{ loc }}" {% if loc == location %}selected{% endif %}>{{ loc }}</option>
                            {% endfor %}
                            <option value="other" {% if location == 'other' %}selected{% endif %}>Other (Custom)</option>
                        </select>
                        <div id="customLocation" class="custom-location {% if location == 'other' %}active{% endif %}">
                            <label>Enter coordinates for your location:</label>
                            <input type="number" name="custom_lat" step="0.0001" placeholder="Latitude (e.g., 26.1420)" 
                                value="{{ custom_lat if custom_lat else '' }}" required>
                            <input type="number" name="custom_lon" step="0.0001" placeholder="Longitude (e.g., -81.7948)" 
                                value="{{ custom_lon if custom_lon else '' }}" required>
                        </div>
                    </div>
                    
                    <div class="criteria-group">
                        <h3>Temperature & Wind</h3>
                        <label>
                            Minimum Day Temperature:
                            <input type="number" name="min_day_temp" value="{{ criteria.get('min_day_temp', 75) }}">°F
                        </label>
                        <label>
                            Minimum Night Temperature:
                            <input type="number" name="min_night_temp" value="{{ criteria.get('min_night_temp', 65) }}">°F
                        </label>
                        <label>
                            Maximum Wind Speed:
                            <input type="number" name="max_wind" value="{{ criteria.get('max_wind', 15) }}">mph
                        </label>
                    </div>
                    
                    <div class="criteria-group">
                        <h3>Acceptable Weather Conditions</h3>
                        <div class="checkbox-group">
                            {% for condition in ['Sunny', 'Mostly Sunny', 'Partly Sunny', 'Partly Cloudy', 'Clear', 'Scattered Rain'] %}
                            <label class="checkbox-label {% if condition in criteria.get('allowed_conditions', []) %}checked{% endif %}">
                                <input type="checkbox" name="conditions" value="{{ condition }}"
                                    {% if condition in criteria.get('allowed_conditions', []) %}checked{% endif %}>
                                {{ condition }}
                            </label>
                            {% endfor %}
                        </div>
                    </div>
                </div>
                
                <button type="submit" class="submit-btn">Check Weather</button>
            </div>
        </form>

        <div id="loading" class="loading">
            <p>💅 Checking the sunshine... Please wait! 🌞</p>
        </div>

        {% if results %}
        <div class="results">
            {% for location, days in results.items() %}
            <div class="location-results">
                <div class="location-name">{{ location }}</div>
                {% for day in days %}
                    {% set flamingo_rating = calculate_day_flamingo_rating(day.periods, criteria)|round|int %}
                    <div class="day-container">
                        <div class="day-header">
                            <div class="day-title">{{ day.date }}</div>
                            <div class="flamingo-display">
                                {% if flamingo_rating > 0 %}
                                    {{ "🦩" * flamingo_rating }}
                                {% else %}
                                    <div class="no-sunbathing">
                                        ❌ Not ideal for sunbathing
                                    </div>
                                {% endif %}
                            </div>
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
        
        function toggleCustomLocation(value) {
            const customLocation = document.getElementById('customLocation');
            const inputs = customLocation.getElementsByTagName('input');
            
            if (value === 'other') {
                customLocation.classList.add('active');
                for (let input of inputs) {
                    input.required = true;
                }
            } else {
                customLocation.classList.remove('active');
                for (let input of inputs) {
                    input.required = false;
                }
            }
        }
        
        // Update checkbox label styling when checked/unchecked
        document.querySelectorAll('.checkbox-label input[type="checkbox"]').forEach(checkbox => {
            checkbox.addEventListener('change', function() {
                this.parentElement.classList.toggle('checked', this.checked);
            });
        });
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
        
        print("\nUser criteria:", user_criteria)

        selected_locations = request.form.getlist("location")
        if not selected_locations:
            return "Please select at least one location."

        results = {}
        for location in selected_locations:
            if location == 'other':
                lat = float(request.form.get('custom_lat'))
                lon = float(request.form.get('custom_lon'))
            elif location not in LOCATIONS:
                continue
            else:
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
            custom_lat=request.form.get('custom_lat'),
            custom_lon=request.form.get('custom_lon'),
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
    app.run(debug=True, port=5001)
