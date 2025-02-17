const HEADERS = {
  'User-Agent': `(sunbathing-checker, ${process.env.USER_EMAIL})`,
  'Accept': 'application/geo+json'
};

async function getWeatherData(lat, lon) {
  const pointsUrl = `https://api.weather.gov/points/${lat},${lon}`;
  const pointsResponse = await fetch(pointsUrl, { headers: HEADERS });
  const pointsData = await pointsResponse.json();
  
  const forecastUrl = pointsData.properties.forecast;
  const forecastResponse = await fetch(forecastUrl, { headers: HEADERS });
  const forecastData = await forecastResponse.json();
  
  return forecastData.properties.periods;
}

function calculateFlamingoRating(period) {
  let rating = 0;
  const temp = period.temperature;
  const sky = period.shortForecast.toLowerCase();
  
  // Temperature rating
  if (temp >= 75 && temp <= 85) rating += 5;
  else if (temp > 85) rating += 3;
  else if (temp >= 65) rating += 2;
  else rating += 1;
  
  // Sky conditions rating
  if (sky.includes('sunny') && !sky.includes('partly')) rating += 5;
  else if (sky.includes('sunny') || sky.includes('clear')) rating += 4;
  else if (sky.includes('cloud')) rating += 3;
  else if (sky.includes('rain') || sky.includes('storm')) rating += 1;
  
  return rating;
}

export default {
  async fetch(request, env) {
    try {
      const url = new URL(request.url);
      
      // Serve static HTML for root path
      if (url.pathname === '/') {
        return new Response(
          `<!DOCTYPE html>
          <html>
          <head>
            <title>Sunbathing Weather Checker</title>
            <style>
              body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
              .forecast { margin: 20px 0; padding: 10px; border: 1px solid #ccc; }
              .flamingo { color: #ff69b4; }
            </style>
          </head>
          <body>
            <h1>🌞 Florida Sunbathing Weather Checker</h1>
            <form id="location-form">
              <label for="location">Enter Florida location (lat,lon):</label><br>
              <input type="text" id="location" name="location" placeholder="28.5383,-81.3792" required><br>
              <button type="submit">Check Weather</button>
            </form>
            <div id="results"></div>
            <script>
              document.getElementById('location-form').addEventListener('submit', async (e) => {
                e.preventDefault();
                const location = document.getElementById('location').value;
                const [lat, lon] = location.split(',').map(n => n.trim());
                
                const response = await fetch(\`/forecast/\${lat}/\${lon}\`);
                const data = await response.json();
                
                const resultsDiv = document.getElementById('results');
                resultsDiv.innerHTML = data.periods.map(period => \`
                  <div class="forecast">
                    <h3>\${period.name}</h3>
                    <p>\${period.shortForecast}</p>
                    <p>Temperature: \${period.temperature}°\${period.temperatureUnit}</p>
                    <p class="flamingo">Flamingo Rating: \${period.flamingoRating}/10 🦩</p>
                  </div>
                \`).join('');
              });
            </script>
          </body>
          </html>`,
          {
            headers: { 'Content-Type': 'text/html' },
          }
        );
      }
      
      // Handle forecast API requests
      const forecastMatch = url.pathname.match(/^\/forecast\/(-?\d+\.?\d*)\/(-?\d+\.?\d*)$/);
      if (forecastMatch) {
        const [_, lat, lon] = forecastMatch;
        const periods = await getWeatherData(lat, lon);
        
        // Add flamingo ratings
        const periodsWithRatings = periods.map(period => ({
          ...period,
          flamingoRating: calculateFlamingoRating(period)
        }));
        
        return new Response(
          JSON.stringify({ periods: periodsWithRatings }),
          {
            headers: { 'Content-Type': 'application/json' }
          }
        );
      }
      
      return new Response('Not Found', { status: 404 });
    } catch (error) {
      return new Response(JSON.stringify({ error: error.message }), {
        status: 500,
        headers: { 'Content-Type': 'application/json' }
      });
    }
  }
};
