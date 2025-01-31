# weather_evaluation.py
CONDITION_SCORES = {
    'clear': 1.0,
    'sunny': 1.0,
    'partly_cloudy': 0.8,
    'cloudy': 0.6,
    'overcast': 0.4,
    'rain': 0.2,
    'storm': 0.1
}

CONDITION_TYPES = {
    'clear': ['clear', 'sunny'],
    'partly_cloudy': ['partly sunny', 'partly cloudy'],
    'cloudy': ['cloudy', 'mostly cloudy'],
    'overcast': ['overcast'],
    'rain': ['rain', 'showers', 'drizzle'],
    'storm': ['thunderstorm', 'storm', 'lightning']
}

CONDITION_ICONS = {
    'clear': '☀️',
    'sunny': '☀️',
    'partly_cloudy': '⛅',
    'cloudy': '☁️',
    'overcast': '☁️',
    'rain': '🌧️',
    'storm': '⛈️',
    'unknown': '❓'
}

def get_condition_icon(condition_type):
    """Get the appropriate weather icon for a condition type."""
    return CONDITION_ICONS.get(condition_type, CONDITION_ICONS['unknown'])

def get_condition_type(short_forecast):
    """Classify the weather condition based on the short forecast."""
    lower_forecast = short_forecast.lower()
    for condition_type, keywords in CONDITION_TYPES.items():
        if any(keyword in lower_forecast for keyword in keywords):
            return condition_type
    return 'unknown'

def get_condition_score(short_forecast, cloud_cover=None, allowed_conditions=None):
    """Calculate a condition score based on the forecast, cloud cover, and allowed conditions."""
    condition_type = get_condition_type(short_forecast)
    
    # If allowed conditions are specified and this condition isn't allowed, return 0
    if allowed_conditions and condition_type not in allowed_conditions:
        return 0.0, condition_type  # Return both score and condition type
    
    base_score = CONDITION_SCORES.get(condition_type, 0.5)
    
    # Adjust score based on cloud cover if available
    if cloud_cover is not None and condition_type in ['cloudy', 'overcast', 'partly_cloudy']:
        return base_score * (1 - (cloud_cover / 100)), condition_type
    
    return base_score, condition_type
