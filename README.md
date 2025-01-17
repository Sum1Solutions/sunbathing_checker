# Sunbathing Weather Checker

The **Sunbathing Weather Checker** is a Python web app that helps you determine whether the next 3 days are suitable for sunbathing in Naples, Fort Lauderdale, or Miami. It uses real-time weather data from the **National Weather Service (NWS) API**.

## Features

- Select locations: Naples, Fort Lauderdale, or Miami.
- Displays a detailed forecast for the next 3 days (AM/PM breakdown).
- Highlights whether conditions are ideal for sunbathing (based on temperature and sunshine).

## Installation

1. Clone this repository:
   ```bash
   git clone [your-repo-url]
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