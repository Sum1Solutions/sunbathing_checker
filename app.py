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
    "Miami, FL",
    "Fort Lauderdale, FL",
    "West Palm Beach, FL",
    "Naples, FL",
    "Key West, FL",
    "Tampa, FL",
    "Sarasota, FL",
    "Fort Myers, FL",
    "Daytona Beach, FL",
    "Orlando, FL",
    "Jacksonville, FL",
    "Pensacola, FL",
    "Panama City, FL"
]

CITY_COORDINATES = {
    "Miami, FL": (25.7617, -80.1918),
    "Fort Lauderdale, FL": (26.1224, -80.1373),
    "Naples, FL": (26.1420, -81.7948),
    "Key West, FL": (24.5553, -81.7800),
    "Tampa, FL": (27.9506,-82.4572),
    "Sarasota, FL": (27.3364,-82.5307),
    "Fort Myers, FL": (26.6406,-81.8723),
    "Daytona Beach, FL": (29.2108,-81.0228),
    "Orlando, FL": (28.5383,-81.3792),
    "Jacksonville, FL": (30.3322,-81.6557),
    "Pensacola, FL": (30.4213,-87.2169),
    "Panama City, FL": (30.1588,-85.6602),
    "West Palm Beach, FL": (26.7153,-80.0534)
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
    "min_temp": 78,
    "max_temp": 87,
    "max_wind": 15,
    "required_condition": "clouds"
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
    """
    Evaluate if the weather condition meets the selected criteria.
    More permissive when there's only a slight chance of rain.
    """
    condition = condition.lower()
    selected_conditions = selected_conditions.lower()
    
    # Special handling for slight chances
    has_slight = 'slight' in condition or 'slight chance' in condition
    
    # Check for rain indicators, but be more permissive with slight chances
    rain_indicators = ['rain', 'shower', 'storm', 'thunderstorm', 'precipitation']
    has_rain = any(indicator in condition for indicator in rain_indicators)
    
    # If it's only a slight chance of rain, we'll be more permissive
    if has_slight and has_rain:
        has_rain = False  # Override rain detection for slight chances
    
    # For sunball option, we need clear or sunny conditions
    if 'sunball' in selected_conditions:
        # Positive conditions for sunball
        sunny_indicators = ['sunny', 'clear']
        # Negative conditions that disqualify even if sunny is mentioned
        negative_indicators = ['mostly cloudy']  # Removed 'partly', 'chance', 'slight'
        
        has_sunny = any(indicator in condition for indicator in sunny_indicators)
        has_negative = any(indicator in condition for indicator in negative_indicators)
        
        # For sunball, we'll allow slight chances if the base condition is sunny
        if has_slight:
            return has_sunny and not has_negative
        else:
            return has_sunny and not has_negative and not has_rain
    
    # For clouds option, we accept clear to mostly cloudy
    elif 'clouds' in selected_conditions:
        acceptable_cloud_conditions = [
            'clear',
            'sunny',
            'partly sunny',
            'mostly sunny',
            'partly cloudy',
            'mostly cloudy'
        ]
        # Be more permissive with clouds option - allow slight chances
        return any(cloud_type in condition for cloud_type in acceptable_cloud_conditions) or has_slight
    
    # For not_rain option, we'll allow slight chances
    elif 'not_rain' in selected_conditions:
        return not has_rain or has_slight
    
    return False

def evaluate_min_temperature(temp, min_temp):
    """
    Evaluate minimum temperature and return rating level:
        3 = meets or exceeds minimum
        2 = within 5 degrees below minimum (reduce final rating by 1)
        1 = within 10 degrees below minimum (reduce final rating by 2)
        0 = more than 10 degrees below minimum (X)
    """
    if temp >= min_temp:
        return 3
    elif temp >= min_temp - 5:
        return 2
    elif temp >= min_temp - 10:
        return 1
    return 0

def evaluate_max_temperature(temp, max_temp):
    """
    Evaluate maximum temperature and return rating level:
        3 = at or below maximum
        2 = within 5 degrees above maximum (reduce final rating by 1)
        1 = within 10 degrees above maximum (reduce final rating by 2)
        0 = more than 10 degrees above maximum (X)
    """
    if temp <= max_temp:
        return 3
    elif temp <= max_temp + 5:
        return 2
    elif temp <= max_temp + 10:
        return 1
    return 0

def evaluate_wind_speed(wind_speed, max_wind):
    """
    Evaluate wind speed and return rating level:
        3 = at or below maximum
        2 = within 5 mph above maximum (reduce final rating by 1)
        1 = within 10 mph above maximum (reduce final rating by 2)
        0 = more than 10 mph above maximum (X)
    """
    if wind_speed <= max_wind:
        return 3
    elif wind_speed <= max_wind + 5:
        return 2
    elif wind_speed <= max_wind + 10:
        return 1
    return 0

def calculate_flamingo_rating(evaluation):
    """Calculate number of flamingos based on conditions, temperature, and wind ratings"""
    # Start with 5 flamingos
    rating = 5
    
    # Reduce rating based on minimum temperature
    if evaluation['min_temp_rating'] == 0:
        return 0  # Automatic fail if temp is too low
    elif evaluation['min_temp_rating'] == 1:
        rating -= 2  # -2 flamingos if temp is within 10° below min
    elif evaluation['min_temp_rating'] == 2:
        rating -= 1  # -1 flamingo if temp is within 5° below min
    
    # Reduce rating based on maximum temperature
    if evaluation['max_temp_rating'] == 0:
        return 0  # Automatic fail if temp is too high
    elif evaluation['max_temp_rating'] == 1:
        rating -= 2  # -2 flamingos if temp is within 10° above max
    elif evaluation['max_temp_rating'] == 2:
        rating -= 1  # -1 flamingo if temp is within 5° above max
    
    # Reduce rating based on wind speed
    if evaluation['wind_rating'] == 0:
        return 0  # Automatic fail if wind is too high
    elif evaluation['wind_rating'] == 1:
        rating -= 2  # -2 flamingos if wind is within 10 mph above max
    elif evaluation['wind_rating'] == 2:
        rating -= 1  # -1 flamingo if wind is within 5 mph above max
    
    # Reduce rating for unacceptable conditions
    if not evaluation['condition_ok']:
        return 0  # Automatic fail for unacceptable conditions
    
    return max(0, rating)  # Ensure rating doesn't go below 0

def is_great_sunbathing_day(day_period, criteria):
    temp = day_period['temperature']
    min_temp_rating = evaluate_min_temperature(temp, criteria['min_temp'])
    max_temp_rating = evaluate_max_temperature(temp, criteria['max_temp'])
    wind_speed = parse_wind_speed(day_period['windSpeed'])
    wind_rating = evaluate_wind_speed(wind_speed, criteria['max_wind'])
    condition_ok = is_acceptable_condition(day_period['shortForecast'], criteria['required_condition'])
    
    evaluation = {
        'min_temp_rating': min_temp_rating,
        'max_temp_rating': max_temp_rating,
        'wind_rating': wind_rating,
        'condition_ok': condition_ok
    }
    
    evaluation['flamingo_rating'] = calculate_flamingo_rating(evaluation)
    evaluation['is_great'] = evaluation['flamingo_rating'] == 5
    
    return evaluation

def evaluate_day_reason(day_period, criteria):
    """Return a reason string for the evaluation of the day_period based on criteria."""
    try:
        temp = int(float(day_period['temperature']))
        wind_speed = parse_wind_speed(day_period['windSpeed'])
        min_temp_rating = evaluate_min_temperature(temp, criteria['min_temp'])
        max_temp_rating = evaluate_max_temperature(temp, criteria['max_temp'])
        wind_rating = evaluate_wind_speed(wind_speed, criteria['max_wind'])
    except Exception as e:
        return "Error parsing weather data."
    
    reasons = []
    
    # Minimum temperature reasons
    if min_temp_rating == 0:
        reasons.append(f"temperature is too low ({temp}°F, more than 10° below minimum {criteria['min_temp']}°F)")
    elif min_temp_rating == 1:
        reasons.append(f"temperature is low ({temp}°F, within 10° of minimum {criteria['min_temp']}°F, -2 flamingos)")
    elif min_temp_rating == 2:
        reasons.append(f"temperature is slightly low ({temp}°F, within 5° of minimum {criteria['min_temp']}°F, -1 flamingo)")
    
    # Maximum temperature reasons
    if max_temp_rating == 0:
        reasons.append(f"temperature is too high ({temp}°F, more than 10° above maximum {criteria['max_temp']}°F)")
    elif max_temp_rating == 1:
        reasons.append(f"temperature is high ({temp}°F, within 10° of maximum {criteria['max_temp']}°F, -2 flamingos)")
    elif max_temp_rating == 2:
        reasons.append(f"temperature is slightly high ({temp}°F, within 5° of maximum {criteria['max_temp']}°F, -1 flamingo)")
    
    # Wind speed reasons
    if wind_rating == 0:
        reasons.append(f"wind speed is too high ({wind_speed} mph, more than 10 mph above maximum {criteria['max_wind']} mph)")
    elif wind_rating == 1:
        reasons.append(f"wind speed is high ({wind_speed} mph, within 10 mph of maximum {criteria['max_wind']} mph, -2 flamingos)")
    elif wind_rating == 2:
        reasons.append(f"wind speed is slightly high ({wind_speed} mph, within 5 mph of maximum {criteria['max_wind']} mph, -1 flamingo)")
    
    # Condition reasons
    if not is_acceptable_condition(day_period['shortForecast'], criteria['required_condition']):
        reasons.append(f"forecast is not acceptable (got '{day_period['shortForecast']}')")
    
    return "; ".join(reasons) if reasons else "Perfect sunbathing conditions!"

def parse_wind_speed(wind_speed_str):
    try:
        return int(float(wind_speed_str.split()[0]))
    except (ValueError, IndexError):
        return 0

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
            color: #333;
        }
        .container {
            width: 90%;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }
        .header {
            text-align: center;
            margin-bottom: 30px;
            padding: 20px;
            background: white;
            border-radius: 10px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }
        .header h1 {
            margin: 0;
            color: #2c5282;
        }
        .rating-scale {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 10px;
            margin: 20px 0;
            padding: 20px;
            background: white;
            border-radius: 10px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }
        .rating-scale div {
            padding: 10px;
            border-radius: 5px;
            background: #f7fafc;
        }
        .form-section {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }
        .form-group {
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }
        .form-group h3 {
            margin-top: 0;
            color: #2c5282;
            border-bottom: 2px solid #e2e8f0;
            padding-bottom: 10px;
        }
        .input-field {
            width: 100%;
            padding: 8px;
            margin: 5px 0 15px 0;
            border: 1px solid #e2e8f0;
            border-radius: 5px;
            font-size: 16px;
        }
        .input-label {
            display: block;
            margin-top: 10px;
            color: #4a5568;
            font-weight: 500;
        }
        .temperature-group {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 15px;
            margin-bottom: 15px;
        }
        .temperature-input {
            display: flex;
            flex-direction: column;
        }
        .radio-group {
            display: flex;
            flex-direction: column;
            gap: 10px;
            margin: 10px 0;
        }
        .radio-label {
            display: flex;
            align-items: center;
            padding: 8px;
            border-radius: 5px;
            background: #f7fafc;
            cursor: pointer;
        }
        .radio-label:hover {
            background: #edf2f7;
        }
        .submit-btn {
            width: 100%;
            padding: 12px;
            background: #2c5282;
            color: white;
            border: none;
            border-radius: 5px;
            font-size: 16px;
            cursor: pointer;
            margin-top: 20px;
        }
        .submit-btn:hover {
            background: #2b6cb0;
        }
        .location-results {
            background: white;
            padding: 20px;
            border-radius: 10px;
            margin: 20px 0;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }
        .day-card {
            background: #f7fafc;
            padding: 20px;
            margin: 15px 0;
            border-radius: 8px;
            display: grid;
            grid-template-columns: 1fr;
            gap: 15px;
        }
        .card-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding-bottom: 10px;
            border-bottom: 1px solid #e2e8f0;
        }
        .evaluation-section {
            display: flex;
            gap: 15px;
            align-items: flex-start;
            background: #edf2f7;
            padding: 12px;
            border-radius: 5px;
            margin-top: -5px;
        }
        .flamingo-rating {
            font-size: 2rem;
            flex-shrink: 0;
            min-width: 150px;
            text-align: center;
        }
        .evaluation-reason {
            color: #4a5568;
            flex-grow: 1;
            padding-top: 8px;
        }
        .weather-details {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 15px;
            padding: 10px 0;
            margin-top: 5px;
        }
        .weather-item {
            background: white;
            padding: 10px;
            border-radius: 5px;
            text-align: center;
        }
        .location-select {
            cursor: pointer;
        }
        .location-select option {
            padding: 8px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>☀️ Tracey's Sunbathing Forecaster 🦩</h1>
        </div>

        <div class="rating-scale">
            <div>🦩🦩🦩🦩🦩 Perfect: Meets all criteria perfectly</div>
            <div>🦩🦩🦩🦩 Good: One minor issue</div>
            <div>🦩🦩🦩 Fair: One major issue or two minor issues</div>
            <div>🦩🦩 Marginal: Multiple issues</div>
            <div>🦩 Borderline: Several significant issues</div>
            <div>❌ Not Suitable: Conditions don't meet minimum requirements</div>
        </div>

        <form method="POST" id="weatherForm">
            <div class="form-section">
                <div class="form-group">
                    <h3>📍 Select Locations</h3>
                    <select name="location" id="location" class="input-field location-select" required multiple>
                        {% for city in cities %}
                        <option value="{{ city }}" {% if city in form_data.locations %}selected{% endif %}>{{ city }}</option>
                        {% endfor %}
                    </select>
                </div>

                <div class="form-group">
                    <h3>🌡 Temperature & Wind</h3>
                    <div class="temperature-group">
                        <div class="temperature-input">
                            <label class="input-label">Minimum Temperature (°F):</label>
                            <input type="number" name="min_temp" id="min_temp" value="{{ form_data.min_temp }}" min="0" max="120" class="input-field" required>
                        </div>
                        <div class="temperature-input">
                            <label class="input-label">Maximum Temperature (°F):</label>
                            <input type="number" name="max_temp" id="max_temp" value="{{ form_data.max_temp }}" min="0" max="120" class="input-field" required>
                        </div>
                    </div>
                    <label>Maximum Wind Speed (mph):</label>
                    <input type="number" name="max_wind" id="max_wind" value="{{ form_data.max_wind }}" min="0" max="50" class="input-field" required>
                </div>

                <div class="form-group">
                    <h3>☀️ Weather Conditions</h3>
                    <div class="radio-group">
                        <label class="radio-label">
                            <input type="radio" name="required_condition" value="sunball" {% if form_data.required_condition == 'sunball' %}checked{% endif %}> 
                            <span>Sunball (Clear/Sunny)</span>
                        </label>
                        <label class="radio-label">
                            <input type="radio" name="required_condition" value="clouds" {% if form_data.required_condition == 'clouds' %}checked{% endif %}> 
                            <span>Clouds Okay (Including Clear/Partly/Mostly Cloudy)</span>
                        </label>
                        <label class="radio-label">
                            <input type="radio" name="required_condition" value="not_rain" {% if form_data.required_condition == 'not_rain' %}checked{% endif %}> 
                            <span>Just Not Rain (Any conditions except rain)</span>
                        </label>
                    </div>
                </div>
            </div>

            <button type="submit" class="submit-btn">Check Weather Forecast</button>
        </form>

        {% if results %}
            {% for location in results %}
            <div class="location-results">
                <h2>7 Day Weather and Evaluation for {{ location.name }}</h2>
                {% for day in location.days %}
                <div class="day-card">
                    <div class="card-header">
                        <strong>{{ day.date }}</strong>
                    </div>
                    
                    <div class="evaluation-section">
                        <div class="flamingo-rating">
                            {% if day.flamingo_rating == 5 %}
                            🦩🦩🦩🦩🦩
                            {% elif day.flamingo_rating == 4 %}
                            🦩🦩🦩🦩
                            {% elif day.flamingo_rating == 3 %}
                            🦩🦩🦩
                            {% elif day.flamingo_rating == 2 %}
                            🦩🦩
                            {% elif day.flamingo_rating == 1 %}
                            🦩
                            {% else %}
                            ❌
                            {% endif %}
                        </div>
                        <div class="evaluation-reason">
                            {{ day.reason }}
                        </div>
                    </div>
                    
                    <div class="weather-details">
                        <div class="weather-item">
                            <div>Conditions</div>
                            <strong>☀️ {{ day.day_period.shortForecast }}</strong>
                        </div>
                        <div class="weather-item">
                            <div>Temperature</div>
                            <strong>🌡 {{ day.day_period.temperature }}°F</strong>
                        </div>
                        <div class="weather-item">
                            <div>Wind Speed</div>
                            <strong>💨 {{ day.day_period.windSpeed }}</strong>
                        </div>
                    </div>
                </div>
                {% endfor %}
            </div>
            {% endfor %}
        {% endif %}
    </div>

    <script>
        // Function to handle double-click on location options
        function handleLocationDoubleClick(e) {
            // Prevent the default double-click behavior
            e.preventDefault();
            
            if (e.target.tagName === 'OPTION') {
                // Clear other selections
                const options = e.target.parentElement.options;
                for (let i = 0; i < options.length; i++) {
                    options[i].selected = options[i] === e.target;
                }
                
                // Submit the form
                document.getElementById('weatherForm').submit();
            }
        }

        // Function to initialize event listeners
        function initializeEventListeners() {
            const locationSelect = document.getElementById('location');
            if (locationSelect) {
                // Remove existing listener to prevent duplicates
                locationSelect.removeEventListener('dblclick', handleLocationDoubleClick);
                // Add the event listener
                locationSelect.addEventListener('dblclick', handleLocationDoubleClick);
            }
        }

        // Initialize on page load
        initializeEventListeners();

        // Initialize after form submission (in case of partial page updates)
        document.addEventListener('DOMContentLoaded', initializeEventListeners);
    </script>
</body>
</html>
"""

@app.route("/", methods=["GET", "POST"])
def home():
    message = None
    results = None
    form_data = {
        "min_temp": DEFAULT_SUNBATHING_CRITERIA["min_temp"],
        "max_temp": DEFAULT_SUNBATHING_CRITERIA["max_temp"],
        "max_wind": DEFAULT_SUNBATHING_CRITERIA["max_wind"],
        "required_condition": DEFAULT_SUNBATHING_CRITERIA["required_condition"],
        "locations": []
    }

    if request.method == "POST":
        try:
            locations = request.form.getlist("location")
            min_temp = int(request.form.get("min_temp", DEFAULT_SUNBATHING_CRITERIA["min_temp"]))
            max_temp = int(request.form.get("max_temp", DEFAULT_SUNBATHING_CRITERIA["max_temp"]))
            max_wind = int(request.form.get("max_wind", DEFAULT_SUNBATHING_CRITERIA["max_wind"]))
            required_condition = request.form.get("required_condition", DEFAULT_SUNBATHING_CRITERIA["required_condition"])

            form_data = {
                "min_temp": min_temp,
                "max_temp": max_temp,
                "max_wind": max_wind,
                "required_condition": required_condition,
                "locations": locations
            }

            if not locations:
                message = "Please select at least one location."
            else:
                results = []
                for location in locations:
                    if location in CITY_COORDINATES:
                        lat, lon = CITY_COORDINATES[location]
                        forecast_data = get_forecast(lat, lon)
                        parsed_days = parse_next_7_days(forecast_data)
                        location_results = {"name": location, "days": []}
                        
                        for day in parsed_days:
                            day_period = None
                            for label, period in day.get("periods", []):
                                if label == "Day":
                                    day_period = period
                            if day_period:
                                # Convert temperature to integer
                                day_period['temperature'] = int(float(day_period['temperature']))
                                # Convert wind speed to integer
                                day_period['windSpeed'] = f"{parse_wind_speed(day_period['windSpeed'])} mph"
                                
                                evaluation = is_great_sunbathing_day(day_period, {
                                    "min_temp": min_temp,
                                    "max_temp": max_temp,
                                    "max_wind": max_wind,
                                    "required_condition": required_condition
                                })
                                reason = evaluate_day_reason(day_period, {
                                    "min_temp": min_temp,
                                    "max_temp": max_temp,
                                    "max_wind": max_wind,
                                    "required_condition": required_condition
                                })
                                location_results["days"].append({
                                    "date": day.get("date"),
                                    "is_great": evaluation['is_great'],
                                    "reason": reason,
                                    "day_period": day_period,
                                    "min_temp_rating": evaluation['min_temp_rating'],
                                    "max_temp_rating": evaluation['max_temp_rating'],
                                    "wind_ok": evaluation['wind_rating'],
                                    "condition_ok": evaluation['condition_ok'],
                                    "flamingo_rating": evaluation['flamingo_rating']
                                })
                        
                        if location_results["days"]:
                            results.append(location_results)
                            message = "7-day forecast evaluated."
                        else:
                            message = "No valid day periods found."
                    else:
                        message = "City not recognized."
        except ValueError as e:
            message = "Please enter valid numbers for temperature and wind speed."
        except Exception as e:
            message = f"An error occurred: {str(e)}"
    
    return render_template_string(
        HTML_TEMPLATE,
        message=message,
        results=results,
        cities=MAIN_CITIES,
        form_data=form_data
    )

if __name__ == "__main__":
    app.run(debug=True, port=5001)
