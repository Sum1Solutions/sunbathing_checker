# 🌞 Sunbathing Weather Forecaster

A smart weather app that helps you find the perfect conditions for sunbathing in Florida! The app uses the National Weather Service (NWS) API to fetch 7-day forecasts and evaluates conditions using our unique "Flamingo Rating" system.

## 🌞 Features

- 7-day weather forecast for Florida locations
- Flamingo rating system (0-5 flamingos) based on:
  - Temperature (min/max thresholds)
  - Wind speed
  - Weather conditions
- Smart weather condition icons (☀️, 🌤, ⛅️, etc.)
- Wind speed indicators (🌫, 🍃, 💨)
- Pre-configured Florida cities:
  - Miami
  - Fort Lauderdale
  - West Palm Beach
  - Naples
  - Key West
  - Tampa
  - And more!

## 🚀 Getting Started

### Local Development

1. Clone the repository
2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   # For development:
   pip install -r requirements.txt
   
   # For exact versions:
   pip install -r requirements.txt.lock
   ```
4. Create a `.env` file with your email for the NWS API:
   ```
   USER_EMAIL=your.email@example.com
   ```
5. Run the app:
   ```bash
   python app.py
   ```

### Deployment on Cloudflare Pages

1. Connect your GitHub repository to Cloudflare Pages
2. Configure build settings:
   - Build command: `pip install -r requirements.txt.lock && gunicorn app:app --workers 2`
   - Environment variables:
     - `USER_EMAIL`: Your email for the NWS API
   - Python version: 3.9

The app will automatically deploy when you push changes to your repository.

## 💻 Technical Details

- Built with Flask 3.1.0
- Uses National Weather Service (NWS) API for accurate forecasts
- No API key required (just email for user agent)
- Responsive design with modern UI
- Smart weather condition parsing with dynamic icons
- Intelligent wind speed indicators
- Customizable rating criteria:
  - Temperature range (72-85°F default)
  - Maximum wind speed (10 mph default)
  - Acceptable weather conditions

## 📦 Dependencies

Core dependencies (see `requirements.txt.lock` for exact versions):
- Flask - Web framework
- Requests - HTTP client for NWS API
- Python-dotenv - Environment variable management
- Gunicorn - Production WSGI server

## 🔄 Development Workflow

1. Make changes to the code
2. Test locally using `python app.py`
3. Commit and push changes
4. Cloudflare Pages will automatically:
   - Install dependencies from `requirements.txt.lock`
   - Start the app with Gunicorn (2 workers)
   - Deploy to the edge network

## 🔒 Privacy

The app only requires an email address for the NWS API user agent. No personal data is collected or stored.

## 🤝 Contributing

Feel free to open issues or submit pull requests with improvements!
