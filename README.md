# 🌞 Sunbathing Weather Forecaster

A smart weather app that helps you find the perfect conditions for sunbathing in Florida! The app uses the National Weather Service (NWS) API to fetch 7-day forecasts and evaluates conditions using our unique "Flamingo Rating" system.

## 🦩 Flamingo Rating System

The app rates each day's sunbathing conditions on a scale of 0-5 flamingos (🦩), considering:

### Temperature Rating
- **Minimum Temperature** (Default: 72°F)
  - At or above minimum: Full points
  - Within 5° below (67-71°F): -1 flamingo
  - Within 10° below (62-66°F): -2 flamingos
  - More than 10° below: ❌ No sunbathing

- **Maximum Temperature** (Default: 85°F)
  - At or below maximum: Full points
  - Within 5° above (86-90°F): -1 flamingo
  - Within 10° above (91-95°F): -2 flamingos
  - More than 10° above: ❌ No sunbathing

### Wind Speed Rating (Default max: 10 mph)
- At or below maximum: Full points
- Within 5 mph above (11-15 mph): -1 flamingo
- Within 10 mph above (16-20 mph): -2 flamingos
- More than 10 mph above: ❌ No sunbathing

### Weather Conditions
Three options to choose from:
1. **Sunball**: Clear/sunny skies only
2. **Clouds Okay**: Clear to mostly cloudy conditions
3. **Just Not Rain**: Any non-rainy conditions

The app intelligently handles "slight chance" conditions based on your preference.

## 🌴 Supported Locations

Currently supports major Florida cities:
- Miami
- Orlando
- Tampa
- Jacksonville
- Key West
- Fort Lauderdale
- Daytona Beach
- Fort Myers
- Pensacola
- Tallahassee

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
   - Build output directory: `/`
3. Set environment variables in Cloudflare Pages dashboard:
   - `USER_EMAIL`: Your email for the NWS API
   - `PYTHON_VERSION`: `3.9`

## 💻 Technical Details

- Built with Flask
- Uses National Weather Service (NWS) API
- No API key required (just email for user agent)
- Responsive design with modern UI
- Double-click location selection
- Real-time forecast evaluation
- Deployed on Cloudflare Pages

## 📦 Dependencies

- Flask (3.0.2)
- Requests (2.32.2)
- Python-dotenv (1.0.1)
- Gunicorn (21.2.0)

## 🔒 Privacy

The app only requires an email address for the NWS API user agent. No personal data is collected or stored.

## 🤝 Contributing

Feel free to open issues or submit pull requests with improvements!
