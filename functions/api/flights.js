// SerpApi Google Flights lookup.
// This returns dated Google Flights itineraries, including nonstop status,
// scheduled times, and observed prices for the requested search.

export async function onRequestPost(context) {
  const { request, env } = context;
  const headers = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type',
    'Content-Type': 'application/json'
  };

  try {
    const { origin, destination, departureDate, returnDate, adults = 1, nonStop = true } = await request.json();
    if (!env.SERPAPI_KEY) return reply({ success: false, code: 'provider_not_configured', error: 'SerpApi key is not configured' }, headers, 503);

    const url = new URL('https://serpapi.com/search');
    url.searchParams.set('engine', 'google_flights');
    url.searchParams.set('api_key', env.SERPAPI_KEY);
    url.searchParams.set('departure_id', origin);
    url.searchParams.set('arrival_id', destination);
    url.searchParams.set('type', returnDate ? '1' : '2');
    url.searchParams.set('outbound_date', departureDate);
    if (returnDate) url.searchParams.set('return_date', returnDate);
    url.searchParams.set('stops', nonStop ? '1' : '0');
    url.searchParams.set('travel_class', '1');
    url.searchParams.set('adults', String(adults));
    url.searchParams.set('currency', 'USD');
    url.searchParams.set('gl', 'us');
    url.searchParams.set('hl', 'en');
    url.searchParams.set('exclude_basic', 'true');

    const response = await fetch(url);
    const data = await response.json();
    if (!response.ok || data.error) return reply({ success: false, code: 'provider_error', error: data.error || `SerpApi returned ${response.status}` }, headers, response.status);

    const itineraries = [...(data.best_flights || []), ...(data.other_flights || [])];
    const flights = itineraries
      .filter(itinerary => !nonStop || !itinerary.layovers?.length)
      .map((itinerary, index) => normalizeItinerary(itinerary, origin, destination, departureDate, returnDate, index, data.search_metadata?.google_flights_url))
      .filter(Boolean)
      .sort((a, b) => a.price - b.price)
      .slice(0, 10);

    return reply({ success: true, flights, count: flights.length, cached: Boolean(data.search_metadata?.cached_page_link), source: 'SerpApi Google Flights', searchParams: { origin, destination, departureDate, returnDate, adults, nonStop } }, headers);
  } catch (error) {
    return reply({ success: false, code: 'provider_error', error: error.message }, headers, 500);
  }
}

function normalizeItinerary(itinerary, origin, destination, departureDate, returnDate, index, googleFlightsUrl) {
  const segments = Array.isArray(itinerary.flights) ? itinerary.flights : [];
  if (!segments.length || !Number.isFinite(Number(itinerary.price))) return null;

  const first = segments[0];
  const last = segments[segments.length - 1];
  const carrier = airlineCode(first);
  return {
    id: `${origin}-${destination}-${departureDate}-${index}`,
    price: Number(itinerary.price), currency: 'USD', direct: !itinerary.layovers?.length,
    carrier, carrierName: first.airline || carrier || 'Multiple airlines', flightNumber: first.flight_number || null,
    departure: first.departure_airport ? { airport: first.departure_airport.id || origin, time: first.departure_airport.time || null } : { airport: origin },
    arrival: last.arrival_airport ? { airport: last.arrival_airport.id || destination, time: last.arrival_airport.time || null } : { airport: destination },
    returnDate: returnDate || null, duration: itinerary.total_duration || segments.reduce((sum, segment) => sum + (Number(segment.duration) || 0), 0),
    bookingUrl: googleFlightsUrl || `https://www.google.com/travel/flights?q=${encodeURIComponent(`flights from ${origin} to ${destination}`)}`,
    verified: true, source: 'SerpApi Google Flights'
  };
}

function airlineCode(segment) {
  const numberMatch = String(segment.flight_number || '').match(/^([A-Z0-9]{2})/);
  if (numberMatch) return numberMatch[1];
  const logoMatch = String(segment.airline_logo || '').match(/\/([A-Z0-9]{2})\.png(?:\?|$)/i);
  return logoMatch ? logoMatch[1].toUpperCase() : segment.airline || '';
}

function reply(payload, headers, status = 200) { return new Response(JSON.stringify(payload), { headers, status }); }

export async function onRequestOptions() {
  return new Response(null, { headers: { 'Access-Control-Allow-Origin': '*', 'Access-Control-Allow-Methods': 'GET, POST, OPTIONS', 'Access-Control-Allow-Headers': 'Content-Type' } });
}
