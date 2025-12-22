// Amadeus Flight Search API
// Route: /api/flights

// Token cache (in-memory, resets on cold start)
let amadeusToken = null;
let tokenExpiry = 0;

async function getAmadeusToken(env) {
  if (amadeusToken && Date.now() < tokenExpiry) {
    return amadeusToken;
  }

  const clientId = env.AMADEUS_CLIENT_ID || 'TxHvvDOaq7kAwF8e9CgrKmNIGblZnYKs';
  const clientSecret = env.AMADEUS_CLIENT_SECRET || 'LJrvgjNbK4a6lgUC';

  const response = await fetch('https://test.api.amadeus.com/v1/security/oauth2/token', {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body: `grant_type=client_credentials&client_id=${clientId}&client_secret=${clientSecret}`
  });

  const data = await response.json();
  amadeusToken = data.access_token;
  tokenExpiry = Date.now() + (data.expires_in * 1000) - 60000;
  return amadeusToken;
}

export async function onRequestPost(context) {
  const { request, env } = context;

  const corsHeaders = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type',
    'Content-Type': 'application/json'
  };

  try {
    const body = await request.json();
    const { origin, destination, departureDate, returnDate, adults = 1 } = body;

    const token = await getAmadeusToken(env);

    const searchUrl = new URL('https://test.api.amadeus.com/v2/shopping/flight-offers');
    searchUrl.searchParams.set('originLocationCode', origin);
    searchUrl.searchParams.set('destinationLocationCode', destination);
    searchUrl.searchParams.set('departureDate', departureDate);
    if (returnDate) searchUrl.searchParams.set('returnDate', returnDate);
    searchUrl.searchParams.set('adults', adults.toString());
    searchUrl.searchParams.set('max', '5');
    searchUrl.searchParams.set('currencyCode', 'USD');

    const flightResponse = await fetch(searchUrl.toString(), {
      headers: { 'Authorization': `Bearer ${token}` }
    });

    const flightData = await flightResponse.json();

    if (flightData.errors) {
      return new Response(JSON.stringify({
        success: false,
        error: flightData.errors[0]?.detail || 'Flight search failed',
        note: 'Using Amadeus sandbox - some routes may not have data'
      }), { headers: corsHeaders });
    }

    const flights = (flightData.data || []).map(offer => ({
      id: offer.id,
      price: parseFloat(offer.price.total),
      currency: offer.price.currency,
      itineraries: offer.itineraries.map(it => ({
        duration: it.duration,
        segments: it.segments.map(seg => ({
          departure: { airport: seg.departure.iataCode, time: seg.departure.at },
          arrival: { airport: seg.arrival.iataCode, time: seg.arrival.at },
          carrier: seg.carrierCode,
          flightNumber: seg.number,
          duration: seg.duration
        }))
      })),
      bookingClass: offer.travelerPricings?.[0]?.fareDetailsBySegment?.[0]?.cabin || 'ECONOMY',
      seatsAvailable: offer.numberOfBookableSeats,
      verified: true,
      source: 'Amadeus'
    }));

    return new Response(JSON.stringify({
      success: true,
      flights,
      count: flights.length,
      searchParams: { origin, destination, departureDate, returnDate }
    }), { headers: corsHeaders });

  } catch (error) {
    return new Response(JSON.stringify({
      success: false,
      error: error.message
    }), { headers: corsHeaders, status: 500 });
  }
}

export async function onRequestOptions() {
  return new Response(null, {
    headers: {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type',
    }
  });
}
