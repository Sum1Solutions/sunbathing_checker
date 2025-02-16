# Sunbathing Checker

A weather forecasting app that helps you find the best days for sunbathing based on your preferences. Uses the National Weather Service API to provide accurate 7-day forecasts for South Florida and Caribbean locations.

## Features

- **Flamingo Rating System**: Intuitive 5-flamingo scale for weather quality:
  - 🦩🦩🦩🦩🦩 Perfect conditions
  - 🦩🦩🦩 Good conditions
  - ❌ Not suitable
- **Multi-Location Support**: Compare weather across multiple locations simultaneously
- **Flexible Weather Conditions**:
  - Sunball: Clear/sunny days only
  - Clouds Okay: Accepts clear, partly cloudy, or mostly cloudy
  - Just Not Rain: Accepts any conditions except rain
- **Customizable Criteria**:
  - Minimum temperature threshold
  - Maximum wind speed limit
  - Preferred weather conditions

## Recent Updates

- Added intuitive flamingo rating system (❌ to 5 🦩)
- Improved cloud condition handling - now accepts partly/mostly cloudy when "Clouds Okay" is selected
- Enhanced UI with card-based layout and visual rating scale
- Added multi-location selection support

## How to Use

1. Select one or more locations from the list
2. Set your weather preferences:
   - Minimum temperature (default: 75°F)
   - Maximum wind speed (default: 15 mph)
3. Choose your weather condition preference:
   - **Sunball**: Only clear/sunny days
   - **Clouds Okay**: Accepts clear through mostly cloudy
   - **Just Not Rain**: Any conditions except rain
4. View the 7-day forecast with flamingo ratings!

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
   Then visit `http://localhost:5000` in your browser.

## Weather Evaluation Criteria

The flamingo rating is determined by these factors:
- **Temperature**: Must meet minimum threshold (default 75°F)
- **Wind Speed**: Must be below maximum limit (default 15 mph)
- **Weather Conditions**: Based on selected preference
  - Sunball: Only clear/sunny conditions
  - Clouds Okay: Accepts clear, partly cloudy, or mostly cloudy
  - Just Not Rain: Any conditions without rain

Perfect conditions (🦩🦩🦩🦩🦩) require all criteria to be met.
