// Amadeus Hotel Search API
// Route: /api/hotels

let amadeusToken = null;
let tokenExpiry = 0;

async function getAmadeusToken(env) {
  if (amadeusToken && Date.now() < tokenExpiry) {
    return amadeusToken;
  }

  const clientId = env.AMADEUS_CLIENT_ID;
  const clientSecret = env.AMADEUS_CLIENT_SECRET;
  if (!clientId || !clientSecret) throw new Error('Amadeus credentials are not configured');

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
    const { cityCode, checkInDate, checkOutDate, adults = 1, maxPrice } = body;

    const token = await getAmadeusToken(env);

    // Step 1: Get hotels in the city
    const hotelListUrl = new URL('https://test.api.amadeus.com/v1/reference-data/locations/hotels/by-city');
    hotelListUrl.searchParams.set('cityCode', cityCode);
    hotelListUrl.searchParams.set('radius', '30');
    hotelListUrl.searchParams.set('radiusUnit', 'MILE');

    const hotelListResp = await fetch(hotelListUrl.toString(), {
      headers: { 'Authorization': `Bearer ${token}` }
    });
    const hotelListData = await hotelListResp.json();

    if (hotelListData.errors || !hotelListData.data?.length) {
      return new Response(JSON.stringify({
        success: false,
        error: hotelListData.errors?.[0]?.detail || 'No hotels found',
        note: 'Amadeus sandbox has limited hotel data'
      }), { headers: corsHeaders });
    }

    // Get first 10 hotel IDs
    const hotelIds = hotelListData.data.slice(0, 10).map(h => h.hotelId);

    // Step 2: Get offers for these hotels
    const offersUrl = new URL('https://test.api.amadeus.com/v3/shopping/hotel-offers');
    offersUrl.searchParams.set('hotelIds', hotelIds.join(','));
    offersUrl.searchParams.set('checkInDate', checkInDate);
    offersUrl.searchParams.set('checkOutDate', checkOutDate);
    offersUrl.searchParams.set('adults', adults.toString());
    offersUrl.searchParams.set('currency', 'USD');
    if (maxPrice) offersUrl.searchParams.set('priceRange', `0-${maxPrice}`);

    const offersResp = await fetch(offersUrl.toString(), {
      headers: { 'Authorization': `Bearer ${token}` }
    });
    const offersData = await offersResp.json();

    if (offersData.errors) {
      // Still return hotel list even if offers fail
      return new Response(JSON.stringify({
        success: true,
        hotels: hotelListData.data.slice(0, 10).map(h => ({
          id: h.hotelId,
          name: h.name,
          address: h.address,
          geoCode: h.geoCode,
          price: null,
          offers: [],
          verified: true,
          source: 'Amadeus'
        })),
        note: 'Hotel list found, but no availability for these dates',
        count: Math.min(10, hotelListData.data.length)
      }), { headers: corsHeaders });
    }

    // Format hotel offers
    const hotels = (offersData.data || []).map(hotel => ({
      id: hotel.hotel.hotelId,
      name: hotel.hotel.name,
      address: hotel.hotel.address,
      rating: hotel.hotel.rating,
      price: hotel.offers?.[0]?.price?.total ? parseFloat(hotel.offers[0].price.total) : null,
      pricePerNight: hotel.offers?.[0]?.price?.total
        ? (parseFloat(hotel.offers[0].price.total) / Math.max(1, daysBetween(checkInDate, checkOutDate))).toFixed(0)
        : null,
      currency: hotel.offers?.[0]?.price?.currency || 'USD',
      roomType: hotel.offers?.[0]?.room?.description?.text || 'Standard Room',
      cancellation: hotel.offers?.[0]?.policies?.cancellation?.description?.text || 'See hotel policy',
      bookingUrl: `https://www.google.com/travel/hotels/entity/${hotel.hotel.hotelId}`,
      offers: hotel.offers?.slice(0, 2) || [],
      verified: true,
      source: 'Amadeus'
    }));

    return new Response(JSON.stringify({
      success: true,
      hotels,
      count: hotels.length,
      searchParams: { cityCode, checkInDate, checkOutDate }
    }), { headers: corsHeaders });

  } catch (error) {
    return new Response(JSON.stringify({
      success: false,
      error: error.message
    }), { headers: corsHeaders, status: 500 });
  }
}

function daysBetween(date1, date2) {
  const d1 = new Date(date1);
  const d2 = new Date(date2);
  return Math.ceil((d2 - d1) / (1000 * 60 * 60 * 24));
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
