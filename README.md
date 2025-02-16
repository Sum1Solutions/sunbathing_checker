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
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Create a `.env` file with your email for the NWS API:
   ```
   USER_EMAIL=your.email@example.com
   ```
4. Run the app:
   ```bash
   python app.py
   ```

### Deployment

This app is configured for deployment on Cloudflare Pages:

1. Connect your GitHub repository to Cloudflare Pages
2. Configure build settings:
   - Build command: `pip install -r requirements.txt && gunicorn app:app`
   - Environment variables:
     - `USER_EMAIL`: Your email for the NWS API

The app will automatically deploy when you push changes to your repository.

## 💻 Technical Details

- Built with Flask
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

- Flask (3.0.2)
- Requests (2.32.2)
- Python-dotenv (1.0.1)
- Gunicorn (21.2.0)

## 🔒 Privacy

The app only requires an email address for the NWS API user agent. No personal data is collected or stored.

## 🤝 Contributing

Feel free to open issues or submit pull requests with improvements!
