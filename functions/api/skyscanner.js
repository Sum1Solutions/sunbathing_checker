// Skyscanner Flight Search via RapidAPI
// Route: /api/skyscanner
//
// FREE TIER: Unlimited requests, 50/min rate limit
// Get your key at: https://rapidapi.com/skyscanner/api/skyscanner-flight-search

const RAPIDAPI_HOST = 'skyscanner-skyscanner-flight-search-v1.p.rapidapi.com';

export async function onRequestPost(context) {
  const { request, env } = context;

  const corsHeaders = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type',
    'Content-Type': 'application/json'
  };

  // Check for RapidAPI key
  const apiKey = env.RAPIDAPI_KEY;
  if (!apiKey) {
    return new Response(JSON.stringify({
      success: false,
      error: 'RapidAPI key not configured',
      setup: 'Get free key at https://rapidapi.com/skyscanner/api/skyscanner-flight-search then run: wrangler pages secret put RAPIDAPI_KEY'
    }), { headers: corsHeaders });
  }

  try {
    const body = await request.json();
    const { origin, destination, departureDate, returnDate, adults = 1 } = body;

    // Use Browse Quotes for cached prices (faster, more reliable)
    const quotesUrl = `https://${RAPIDAPI_HOST}/apiservices/browsequotes/v1.0/US/USD/en-US/${origin}-sky/${destination}-sky/${departureDate}`;

    const response = await fetch(quotesUrl, {
      headers: {
        'X-RapidAPI-Key': apiKey,
        'X-RapidAPI-Host': RAPIDAPI_HOST
      }
    });

    const data = await response.json();

    if (!response.ok) {
      return new Response(JSON.stringify({
        success: false,
        error: data.message || 'Skyscanner API error',
        status: response.status
      }), { headers: corsHeaders });
    }

    // Parse quotes into flight results
    const carriers = {};
    (data.Carriers || []).forEach(c => { carriers[c.CarrierId] = c.Name; });

    const places = {};
    (data.Places || []).forEach(p => { places[p.PlaceId] = p; });

    const flights = (data.Quotes || []).map(quote => ({
      id: quote.QuoteId,
      price: quote.MinPrice,
      currency: data.Currencies?.[0]?.Code || 'USD',
      direct: quote.Direct,
      carrier: carriers[quote.OutboundLeg?.CarrierIds?.[0]] || 'Multiple',
      departure: {
        airport: places[quote.OutboundLeg?.OriginId]?.IataCode || origin,
        date: quote.OutboundLeg?.DepartureDate
      },
      arrival: {
        airport: places[quote.OutboundLeg?.DestinationId]?.IataCode || destination
      },
      bookingUrl: `https://www.skyscanner.com/transport/flights/${origin}/${destination}/${departureDate.replace(/-/g, '')}/?adults=${adults}&currency=USD`,
      verified: true,
      source: 'Skyscanner'
    }));

    // Sort by price
    flights.sort((a, b) => a.price - b.price);

    return new Response(JSON.stringify({
      success: true,
      flights: flights.slice(0, 5),
      count: flights.length,
      searchParams: { origin, destination, departureDate },
      source: 'Skyscanner via RapidAPI'
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
