# 🌞 Sunbathing Weather Forecaster

A smart weather app that helps you find the perfect conditions for sunbathing in Florida! The app uses the National Weather Service (NWS) API to fetch 7-day forecasts and evaluates conditions using our unique "Flamingo Rating" system.

## 🦩 Flamingo Rating System

The app rates each day's sunbathing conditions on a scale of 0-5 flamingos (🦩), considering:

### Temperature Rating
- **Minimum Temperature** (Default: 78°F)
  - At or above minimum: Full points
  - Within 5° below (73-77°F): -1 flamingo
  - Within 10° below (68-72°F): -2 flamingos
  - More than 10° below: ❌ No sunbathing

- **Maximum Temperature** (Default: 87°F)
  - At or below maximum: Full points
  - Within 5° above (88-92°F): -1 flamingo
  - Within 10° above (93-97°F): -2 flamingos
  - More than 10° above: ❌ No sunbathing

### Wind Speed Rating (Default max: 15 mph)
- At or below maximum: Full points
- Within 5 mph above (16-20 mph): -1 flamingo
- Within 10 mph above (21-25 mph): -2 flamingos
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

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Create a `.env` file with your email for the NWS API:
   ```
   USER_AGENT_EMAIL=your.email@example.com
   ```
4. Run the app:
   ```bash
   python app.py
   ```

## 💻 Technical Details

- Built with Flask
- Uses National Weather Service (NWS) API
- No API key required (just email for user agent)
- Responsive design with modern UI
- Double-click location selection
- Real-time forecast evaluation

## 📦 Dependencies

- Flask
- Requests
- Python-dotenv
- Gunicorn (for production)

## 🔒 Privacy

The app only requires an email address for the NWS API user agent. No personal data is collected or stored.

## 🤝 Contributing

Feel free to open issues or submit pull requests with improvements!
