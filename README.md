# Sunbathing Weather Checker

The **Sunbathing Weather Checker** is a Python web app that helps you determine whether there are some suitable sunbathing days coming up in Naples, Fort Lauderdale, and/or Miami. It uses real-time weather data from the **National Weather Service (NWS) API**.

## Features

- Select locations: Naples, Fort Lauderdale, or Miami.
- Displays a detailed forecast for the next 3 days (AM/PM breakdown).
- Highlights whether conditions are ideal for sunbathing (based on temperature and sunshine).

## Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/Sum1Solutions/sunbathing_checker.git
   cd sunbathing_checker
   ```

2. Create and activate a virtual environment (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows, use: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up environment variables:
   - Copy `.env.example` to `.env` (or create a new `.env` file)
   - Update `USER_EMAIL` in `.env` with your email address:
     ```
     USER_EMAIL=your.email@example.com
     ```

5. Run the application:
   ```bash
   python app.py
   ```
   The app will be available at `http://localhost:5000`

## How It Works

1. Users select one or more locations from the web interface.
2. The app fetches real-time weather data from the NWS API for each selected location.
3. Analyzes temperature, wind, and forecast conditions for sunbathing suitability.
4. Displays the results on the same page.

## Ideal Sunbathing Conditions

The app considers the following criteria to determine if conditions are suitable for sunbathing:
- **Temperature**: A minimum temperature threshold (e.g., 75°F) is required for both morning (AM) and afternoon (PM) periods.
- **Sunshine**: The app checks for a minimum amount of sunshine hours per day, with a preference for forecasts that include "Sunny," "Mostly Sunny," or similar terms.

## Detailed Sunbathing Conditions Analysis

The app performs a detailed analysis of the weather forecast to determine the suitability of conditions for sunbathing. This includes:

- **Temperature Analysis**: The app checks the temperature forecast for both morning and afternoon periods to ensure that it meets the minimum temperature threshold.
- **Sunshine Analysis**: The app analyzes the forecast to determine the amount of sunshine hours per day, taking into account the time of day and the intensity of the sunshine.
- **Wind Analysis**: The app also considers the wind forecast to ensure that it is not too windy, which could make sunbathing uncomfortable.

## Additional Features

- **Email Notifications**: Users can opt to receive email notifications about upcoming sunbathing days based on their preferences. The app allows users to customize their notification settings, including the frequency and timing of notifications.
- **Historical Weather Data**: The app provides access to historical weather data to help users plan future sunbathing activities. This feature allows users to view past weather patterns and make informed decisions about when to plan their sunbathing activities.

## Criteria for Sunbathing Weather

- Sunshine conditions: Forecast includes "Sunny," "Mostly Sunny," or similar terms.
- Minimum temperature: At least 75°F in both morning (AM) and afternoon (PM).

## Technologies Used

- **Flask**: Web framework for building the app.
- **Requests**: For fetching weather data from the NWS API.
- **HTML/CSS**: For rendering the user interface.
- **python-dotenv**: For managing environment variables.

## License

This project is licensed under the MIT License.
