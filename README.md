# 🌞 Sunbathing Weather Forecaster

A smart weather app that helps you find the perfect conditions for sunbathing in Florida! The app uses the National Weather Service (NWS) API to fetch 7-day forecasts and evaluates conditions using our unique "Flamingo Rating" system.

## 🌟 Project Status

This project has two implementations:

### Python Version (Main Branch)
- ✅ Fully functional Flask implementation
- ✅ Running successfully locally
- ❌ Not compatible with Cloudflare Pages (Python not supported)
- 🔄 Currently on the `main` branch

### NPM Version (NPM Branch)
- ✅ Cloudflare Workers implementation
- 🚧 Work in progress
- ✅ Compatible with Cloudflare Pages
- 🔄 Available on the `npm` branch

To switch between versions:
```bash
# For Python version
git checkout main

# For NPM version
git checkout npm
```

## 🌞 Features

- 7-day weather forecast for Florida locations
- Flamingo rating system (0-10 flamingos) based on:
  - Temperature (optimal range: 75-85°F)
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

### Python Version (Main Branch)

1. Clone the repository
2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Create a `.env` file with your email for the NWS API:
   ```
   USER_EMAIL=your.email@example.com
   ```
5. Run the app:
   ```bash
   python app.py
   ```

### NPM Version (NPM Branch)

1. Switch to the NPM branch:
   ```bash
   git checkout npm
   ```
2. Install dependencies:
   ```bash
   npm install
   ```
3. Create a `.dev.vars` file with your email:
   ```
   USER_EMAIL=your.email@example.com
   ```
4. Run the development server:
   ```bash
   npm run dev
   ```

## 💻 Technical Details

### Python Version
- Built with Flask 3.1.0
- Uses National Weather Service (NWS) API
- No API key required (just email for user agent)
- Responsive design with modern UI

### NPM Version
- Built with Cloudflare Workers
- Pure JavaScript implementation
- Same features as Python version
- Optimized for edge deployment

## 📦 Dependencies

### Python Version
Core dependencies (see `requirements.txt` for exact versions):
- Flask - Web framework
- Requests - HTTP client for NWS API
- Python-dotenv - Environment variable management
- Gunicorn - Production WSGI server

### NPM Version
Core dependencies (see `package.json`):
- @cloudflare/workers-types
- wrangler

## 🔒 Privacy

The app only requires an email address for the NWS API user agent. No personal data is collected or stored.

## 🤝 Contributing

Feel free to open issues or submit pull requests with improvements!
