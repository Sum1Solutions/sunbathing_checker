const MAIN_CITIES = [
  "Miami, FL",
  "Fort Lauderdale, FL",
  "West Palm Beach, FL",
  "Naples, FL",
  "Key West, FL",
  "Tampa, FL",
  "Sarasota, FL",
  "Fort Myers, FL",
  "Daytona Beach, FL",
  "Orlando, FL",
  "Jacksonville, FL",
  "Pensacola, FL",
  "Panama City, FL"
];

const CITY_COORDINATES = {
  "Miami, FL": [25.7617, -80.1918],
  "Fort Lauderdale, FL": [26.1224, -80.1373],
  "Naples, FL": [26.1420, -81.7948],
  "Key West, FL": [24.5553, -81.7800],
  "Tampa, FL": [27.9506, -82.4572],
  "Sarasota, FL": [27.3364, -82.5307],
  "Fort Myers, FL": [26.6406, -81.8723],
  "Daytona Beach, FL": [29.2108, -81.0228],
  "Orlando, FL": [28.5383, -81.3792],
  "Jacksonville, FL": [30.3322, -81.6557],
  "Pensacola, FL": [30.4213, -87.2169],
  "Panama City, FL": [30.1588, -85.6602],
  "West Palm Beach, FL": [26.7153, -80.0534]
};

const WEATHER_ICONS = {
  'Sunny': '☀️',
  'Clear': '☀️',
  'Mostly Clear': '🌤',
  'Partly Sunny': '🌤',
  'Mostly Sunny': '🌤',
  'Partly Cloudy': '⛅️',
  'Mostly Cloudy': '🌥',
  'Cloudy': '☁️',
  'Rain': '🌧',
  'Light Rain': '🌧',
  'Showers': '🌧',
  'Slight Chance Rain Showers': '🌦',
  'Chance Rain Showers': '🌦',
  'Thunderstorms': '⛈',
  'Chance Thunderstorms': '⛈',
  'Slight Chance Thunderstorms': '⛈',
  'Scattered Thunderstorms': '⛈',
  'Isolated Thunderstorms': '⛈',
  'Scattered Showers': '🌦',
  'Isolated Showers': '🌦',
  'Heavy Rain': '🌧',
  'Drizzle': '🌧',
  'Light Drizzle': '🌧',
  'Heavy Drizzle': '🌧',
  'Light Showers': '🌦',
  'Heavy Showers': '🌧'
};

function getWeatherIcon(condition) {
  // Try exact match first
  if (WEATHER_ICONS[condition]) {
    return WEATHER_ICONS[condition];
  }
  
  // Try case-insensitive match
  const conditionLower = condition.toLowerCase();
  for (const [key, value] of Object.entries(WEATHER_ICONS)) {
    if (key.toLowerCase() === conditionLower) {
      return value;
    }
  }
  
  // Try partial matches
  if (conditionLower.includes('sun') || conditionLower.includes('clear')) {
    if (conditionLower.includes('partly')) {
      return '🌤';
    }
    return '☀️';
  } else if (conditionLower.includes('cloud')) {
    if (conditionLower.includes('partly') || conditionLower.includes('scattered')) {
      return '⛅️';
    } else if (conditionLower.includes('mostly')) {
      return '🌥';
    }
    return '☁️';
  } else if (conditionLower.includes('rain') || conditionLower.includes('shower')) {
    if (conditionLower.includes('slight chance') || conditionLower.includes('chance') || conditionLower.includes('scattered')) {
      return '🌦';
    }
    if (conditionLower.includes('heavy')) {
      return '🌧';
    }
    return '🌧';
  } else if (conditionLower.includes('thunder') || conditionLower.includes('storm')) {
    return '⛈';
  }
  
  // Default to sunny if no match found
  console.log(`No weather icon match found for: ${condition}`);
  return '☀️';
}

function getWindIcon(windSpeedStr) {
  try {
    const speedParts = windSpeedStr.toLowerCase().split(' ');
    let speed;
    if (speedParts.includes('to')) {
      speed = parseFloat(speedParts[speedParts.indexOf('to') + 1]);
    } else {
      speed = parseFloat(speedParts[0]);
    }
    
    if (speed === 0) return '🌫';
    if (speed <= 5) return '🍃';
    if (speed <= 10) return '💨';
    if (speed <= 15) return '💨💨';
    if (speed <= 20) return '💨💨💨';
    return '💨💨💨💨';
  } catch (error) {
    return '💨';
  }
}

function calculateFlamingoRating(period) {
  let rating = 0;
  const temp = period.temperature;
  const sky = period.shortForecast.toLowerCase();
  
  // Temperature rating (0-5)
  if (temp >= 75 && temp <= 85) rating += 5;
  else if (temp > 85) rating += 3;
  else if (temp >= 65) rating += 2;
  else rating += 1;
  
  // Sky conditions rating (0-5)
  if (sky.includes('sunny') && !sky.includes('partly')) rating += 5;
  else if (sky.includes('sunny') || sky.includes('clear')) rating += 4;
  else if (sky.includes('cloud')) rating += 3;
  else if (sky.includes('rain') || sky.includes('storm')) rating += 1;
  
  return rating;
}

async function getHeaders(env) {
  return {
    'User-Agent': `(sunbathing-checker, ${env.USER_EMAIL})`,
    'Accept': 'application/geo+json'
  };
}

async function getWeatherData(lat, lon, env) {
  const headers = await getHeaders(env);
  const maxRetries = 3;
  let retries = 0;

  while (retries < maxRetries) {
    try {
      const pointsUrl = `https://api.weather.gov/points/${lat},${lon}`;
      const pointsResponse = await fetch(pointsUrl, { headers });
      
      if (!pointsResponse.ok) {
        throw new Error(`Points API failed with status: ${pointsResponse.status}`);
      }
      
      const pointsData = await pointsResponse.json();
      const forecastUrl = pointsData.properties.forecast;
      
      const forecastResponse = await fetch(forecastUrl, { headers });
      if (!forecastResponse.ok) {
        throw new Error(`Forecast API failed with status: ${forecastResponse.status}`);
      }
      
      const forecastData = await forecastResponse.json();
      return forecastData.properties.periods;
    } catch (error) {
      retries++;
      if (retries === maxRetries) {
        throw new Error(`Failed to fetch weather data after ${maxRetries} attempts: ${error.message}`);
      }
      // Exponential backoff
      await new Promise(resolve => setTimeout(resolve, Math.pow(2, retries) * 1000));
    }
  }
}

const HTML_TEMPLATE = `<!DOCTYPE html>
<html>
<head>
    <title>Tracey's Sunbathing Forecaster</title>
    <style>
        body {
            font-family: system-ui, -apple-system, sans-serif;
            line-height: 1.6;
            margin: 0;
            padding: 0;
            background: linear-gradient(135deg, #87CEEB, #E0F4FF);
            min-height: 100vh;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }
        .header {
            text-align: center;
            margin-bottom: 30px;
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }
        h1 {
            margin: 0;
            color: #FF69B4;
            font-size: 2.5em;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 15px;
        }
        .emoji {
            font-size: 1.2em;
        }
        .subtitle {
            color: #666;
            font-size: 1.2em;
            margin-top: 10px;
        }
        .location-form {
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        }
        select {
            width: 100%;
            padding: 10px;
            font-size: 1.1em;
            border: 1px solid #ddd;
            border-radius: 5px;
            margin-bottom: 15px;
        }
        button {
            background: #FF69B4;
            color: white;
            border: none;
            padding: 12px 25px;
            font-size: 1.1em;
            border-radius: 5px;
            cursor: pointer;
            transition: background 0.3s;
        }
        button:hover {
            background: #FF1493;
        }
        .rating-legend {
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            margin-top: 20px;
        }
        .rating-legend h3 {
            color: #FF69B4;
            margin-top: 0;
            text-align: center;
            font-size: 1.5em;
        }
        .rating-row {
            display: flex;
            align-items: center;
            margin: 10px 0;
            padding: 10px;
            background: #f8f9fa;
            border-radius: 5px;
        }
        .rating-flamingos {
            min-width: 150px;
            letter-spacing: 2px;
        }
        .rating-description {
            flex-grow: 1;
            color: #555;
        }
        .loading-overlay {
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(255, 255, 255, 0.9);
            z-index: 1000;
            justify-content: center;
            align-items: center;
        }
        .loading-content {
            text-align: center;
            padding: 20px;
            border-radius: 10px;
            background: white;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }
        .loading-spinner {
            border: 4px solid #f3f3f3;
            border-top: 4px solid #FF69B4;
            border-radius: 50%;
            width: 40px;
            height: 40px;
            animation: spin 1s linear infinite;
            margin: 0 auto 10px;
        }
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        .error-message {
            background: #ffebee;
            color: #c62828;
            padding: 15px;
            border-radius: 5px;
            margin: 10px 0;
            display: none;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1><span class="emoji">☀️</span> Tracey's Sunbathing Forecaster <span class="emoji">🦩</span></h1>
            <div class="subtitle">Find the perfect time to soak up the Florida sun!</div>
        </div>

        <div class="location-form">
            <form id="locationForm">
                <select id="citySelect" required>
                    <option value="">Select a Florida City</option>
                    ${MAIN_CITIES.map(city => `<option value="${city}">${city}</option>`).join('')}
                </select>
                <button type="submit">Get Forecast</button>
            </form>
        </div>

        <div id="results"></div>
        <div id="errorMessage" class="error-message"></div>

        <div class="rating-legend">
            <h3>Flamingo Rating Guide</h3>
            <div class="rating-row">
                <div class="rating-flamingos">🦩🦩🦩🦩🦩</div>
                <div class="rating-description">Perfect sunbathing conditions! (8-10)</div>
            </div>
            <div class="rating-row">
                <div class="rating-flamingos">🦩🦩🦩🦩</div>
                <div class="rating-description">Great conditions (6-7)</div>
            </div>
            <div class="rating-row">
                <div class="rating-flamingos">🦩🦩🦩</div>
                <div class="rating-description">Good conditions (4-5)</div>
            </div>
            <div class="rating-row">
                <div class="rating-flamingos">🦩🦩</div>
                <div class="rating-description">Fair conditions (2-3)</div>
            </div>
            <div class="rating-row">
                <div class="rating-flamingos">🦩</div>
                <div class="rating-description">Poor conditions (0-1)</div>
            </div>
        </div>
    </div>

    <div class="loading-overlay" id="loadingOverlay">
        <div class="loading-content">
            <div class="loading-spinner"></div>
            <div class="loading-message">Checking the sunshine...</div>
        </div>
    </div>

    <script>
        document.getElementById('locationForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            const loadingOverlay = document.getElementById('loadingOverlay');
            const resultsDiv = document.getElementById('results');
            const errorMessage = document.getElementById('errorMessage');
            
            loadingOverlay.style.display = 'flex';
            resultsDiv.innerHTML = '';
            errorMessage.style.display = 'none';
            
            try {
                const locationSelect = document.getElementById('citySelect');
                const selectedLocation = locationSelect.value;
                
                const response = await fetch('/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ location: selectedLocation })
                });
                
                if (!response.ok) {
                    throw new Error('Failed to fetch weather data. Please try again later.');
                }
                
                const data = await response.json();
                resultsDiv.innerHTML = data.html;
            } catch (error) {
                errorMessage.textContent = error.message;
                errorMessage.style.display = 'block';
            } finally {
                loadingOverlay.style.display = 'none';
            }
        });
    </script>
</body>
</html>`;

export default {
  async fetch(request, env) {
    try {
      const url = new URL(request.url);
      
      // Serve static HTML for root path
      if (request.method === 'GET' && url.pathname === '/') {
        return new Response(HTML_TEMPLATE, {
          headers: { 'Content-Type': 'text/html' },
        });
      }
      
      if (request.method === 'POST') {
        const data = await request.json();
        const location = data.location;
        const coordinates = CITY_COORDINATES[location];
        
        if (!coordinates) {
          return new Response(JSON.stringify({ 
            error: 'Invalid location selected' 
          }), {
            status: 400,
            headers: { 'Content-Type': 'application/json' }
          });
        }
        
        const [lat, lon] = coordinates;
        const forecast = await getWeatherData(lat, lon, env);
        
        let forecastHtml = '';
        let currentDay = '';
        
        for (const period of forecast) {
          const date = new Date(period.startTime);
          const dayStr = date.toLocaleDateString('en-US', { weekday: 'long', month: 'short', day: 'numeric' });
          
          if (dayStr !== currentDay) {
            if (currentDay) forecastHtml += '</div>';
            currentDay = dayStr;
            forecastHtml += `<div class="forecast-day"><h3>${dayStr}</h3>`;
          }
          
          const flamingoRating = calculateFlamingoRating(period);
          const flamingoEmojis = '🦩'.repeat(flamingoRating);
          
          forecastHtml += `
              <div class="forecast-period">
                  <div class="period-name">${period.name}</div>
                  <div class="weather-details">
                      <span class="temp">${period.temperature}°F</span>
                      <span class="conditions"><span class="weather-icon">${getWeatherIcon(period.shortForecast)}</span> ${period.shortForecast}</span>
                      <span class="wind"><span class="wind-icon">${getWindIcon(period.windSpeed)}</span> ${period.windSpeed}</span>
                      <span class="rating" title="Flamingo Rating: ${flamingoRating}/10">${flamingoEmojis}</span>
                  </div>
              </div>`;
        }
        
        if (currentDay) forecastHtml += '</div>';
        
        return new Response(JSON.stringify({ 
          html: forecastHtml 
        }), {
          headers: { 'Content-Type': 'application/json' }
        });
      }
      
      return new Response('Not Found', { status: 404 });
    } catch (error) {
      return new Response(JSON.stringify({ 
        error: error.message 
      }), {
        status: 500,
        headers: { 'Content-Type': 'application/json' }
      });
    }
  }
};
