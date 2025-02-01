# Sunbathing Checker

A weather forecasting app that helps you find the best days for sunbathing based on your preferences.

## Features

- **Customizable Criteria**: Set your ideal temperature, wind speed, and weather conditions
- **Condition Categories**: Choose from Sunball (clear/sunny), Clouds (partly/mostly cloudy), or Rain
- **7-Day Forecast**: Get detailed weather predictions for the upcoming week
- **Modern UI**: Clean, intuitive interface with responsive design

## Recent Updates

- Improved condition matching logic
- Removed scoring system for simpler evaluation
- Enhanced UI with better input fields and layout

## How to Use

1. Select your location from the dropdown
2. Set your preferred minimum temperature and maximum wind speed
3. Choose your desired weather condition category
4. View results and plan your sunbathing days!

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

## Technologies Used

- **Flask**: Web framework for building the app.
- **Requests**: For fetching weather data from the NWS API.
- **HTML/CSS**: For rendering the user interface.
- **python-dotenv**: For managing environment variables.

## License

This project is licensed under the MIT License.
