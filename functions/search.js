// Cloudflare Worker for Sunball Finder
// Handles natural language search + verification

export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);

    if (url.pathname === '/api/search') {
      return handleSearch(request, env);
    }

    if (url.pathname === '/api/verify') {
      return handleVerify(request, env);
    }

    return new Response('Not found', { status: 404 });
  }
};

async function handleSearch(request, env) {
  const body = await request.json();
  const { description, dateRange, budget, departure } = body;

  // Parse natural language description
  const searchCriteria = parseDescription(description);

  // Search multiple sources
  const results = await Promise.all([
    searchAirbnb(searchCriteria, dateRange, budget),
    searchVRBO(searchCriteria, dateRange, budget),
    // Add more sources
  ]);

  // Flatten and verify each result
  const allListings = results.flat();
  const verifiedListings = await Promise.all(
    allListings.map(listing => verifyListing(listing, env))
  );

  // Filter out failed verifications
  const confirmedListings = verifiedListings.filter(l => l.verified);

  return new Response(JSON.stringify({
    success: true,
    searchCriteria,
    listings: confirmedListings,
    warnings: verifiedListings.filter(l => !l.verified).map(l => ({
      title: l.title,
      reason: l.verificationFailReason
    }))
  }), {
    headers: { 'Content-Type': 'application/json' }
  });
}

function parseDescription(description) {
  // Extract key features from natural language
  const desc = description.toLowerCase();

  return {
    propertyType: extractPropertyType(desc),
    floors: extractFloors(desc),
    beachProximity: desc.includes('beach') || desc.includes('ocean') || desc.includes('waterfront'),
    pool: desc.includes('pool'),
    clean: desc.includes('clean'),
    nice: desc.includes('nice') || desc.includes('quality') || desc.includes('good'),
    minBedrooms: extractBedrooms(desc),
    features: extractFeatures(desc)
  };
}

function extractPropertyType(desc) {
  if (desc.includes('condo')) return 'condo';
  if (desc.includes('house')) return 'house';
  if (desc.includes('apartment')) return 'apartment';
  if (desc.includes('studio')) return 'studio';
  return 'any';
}

function extractFloors(desc) {
  if (desc.includes('two floor') || desc.includes('2 floor') || desc.includes('two-story') || desc.includes('2-story')) return 2;
  if (desc.includes('three floor') || desc.includes('3 floor')) return 3;
  return null;
}

function extractBedrooms(desc) {
  const match = desc.match(/(\d+)\s*(bed|br|bedroom)/);
  return match ? parseInt(match[1]) : null;
}

function extractFeatures(desc) {
  const features = [];
  if (desc.includes('parking')) features.push('parking');
  if (desc.includes('wifi') || desc.includes('internet')) features.push('wifi');
  if (desc.includes('kitchen')) features.push('kitchen');
  if (desc.includes('washer') || desc.includes('laundry')) features.push('laundry');
  if (desc.includes('ac') || desc.includes('air conditioning')) features.push('ac');
  if (desc.includes('balcony')) features.push('balcony');
  if (desc.includes('view')) features.push('view');
  return features;
}

// Verification functions

async function verifyListing(listing, env) {
  const checks = {
    addressExists: await verifyAddressExists(listing.address),
    priceReasonable: verifyPriceReasonable(listing.price, listing.location),
    photosOriginal: await verifyPhotosOriginal(listing.photos),
    hostVerified: await verifyHost(listing.hostId, listing.source),
    listingActive: await verifyListingActive(listing.url),
    noScamIndicators: checkScamIndicators(listing)
  };

  const allPassed = Object.values(checks).every(c => c.pass);

  return {
    ...listing,
    verified: allPassed,
    verificationChecks: checks,
    verificationFailReason: allPassed ? null :
      Object.entries(checks)
        .filter(([k, v]) => !v.pass)
        .map(([k, v]) => v.reason)
        .join('; ')
  };
}

async function verifyAddressExists(address) {
  // Use Google Maps Geocoding API to verify address exists
  // This prevents confabulated addresses
  try {
    // In production: call Google Maps API
    // const response = await fetch(`https://maps.googleapis.com/maps/api/geocode/json?address=${encodeURIComponent(address)}&key=${env.GOOGLE_MAPS_KEY}`);
    // const data = await response.json();
    // return { pass: data.results.length > 0, reason: 'Address verified via Google Maps' };

    return { pass: true, reason: 'Address verification pending API setup' };
  } catch (error) {
    return { pass: false, reason: 'Could not verify address exists' };
  }
}

function verifyPriceReasonable(price, location) {
  // Market rate checks for South Florida
  const marketRates = {
    'naples': { min: 80, max: 400 },
    'fort-lauderdale': { min: 70, max: 350 },
    'miami': { min: 80, max: 500 },
    'key-west': { min: 120, max: 600 },
    'west-palm-beach': { min: 65, max: 300 }
  };

  const rates = marketRates[location] || { min: 60, max: 400 };

  if (price < rates.min * 0.5) {
    return { pass: false, reason: `Price $${price} is suspiciously low (market: $${rates.min}-${rates.max})` };
  }
  if (price > rates.max * 1.5) {
    return { pass: false, reason: `Price $${price} is unusually high` };
  }

  return { pass: true, reason: `Price within market range for ${location}` };
}

async function verifyPhotosOriginal(photos) {
  // In production: use reverse image search API
  // Check if photos appear on other unrelated listings (scam indicator)
  return { pass: true, reason: 'Photo verification pending' };
}

async function verifyHost(hostId, source) {
  // In production: check host history on platform
  return { pass: true, reason: 'Host verification pending' };
}

async function verifyListingActive(url) {
  // In production: fetch the URL and verify it's still live
  return { pass: true, reason: 'Listing active check pending' };
}

function checkScamIndicators(listing) {
  const redFlags = [];

  // Check for common scam patterns
  if (listing.title && listing.title.includes('!!!')) {
    redFlags.push('Excessive punctuation in title');
  }
  if (listing.description && listing.description.toLowerCase().includes('wire transfer')) {
    redFlags.push('Mentions wire transfer');
  }
  if (listing.description && listing.description.toLowerCase().includes('western union')) {
    redFlags.push('Mentions Western Union');
  }
  if (listing.contactMethod === 'email_only') {
    redFlags.push('Only accepts email contact (no platform messaging)');
  }
  if (listing.paymentOffPlatform) {
    redFlags.push('Requests payment outside platform');
  }

  return {
    pass: redFlags.length === 0,
    reason: redFlags.length > 0 ? `Scam indicators: ${redFlags.join(', ')}` : 'No scam indicators detected'
  };
}

// Placeholder search functions - would connect to real APIs

async function searchAirbnb(criteria, dateRange, budget) {
  // In production: use Airbnb unofficial API or approved scraping
  // For now, return empty - no confabulation
  return [];
}

async function searchVRBO(criteria, dateRange, budget) {
  // In production: use VRBO API
  return [];
}

async function handleVerify(request, env) {
  const body = await request.json();
  const { url } = body;

  // Verify a specific listing URL is real and active
  try {
    const response = await fetch(url, {
      headers: { 'User-Agent': 'Mozilla/5.0 (compatible; SunballFinder/1.0)' }
    });

    if (!response.ok) {
      return new Response(JSON.stringify({
        verified: false,
        reason: `Listing returned ${response.status}`
      }), { headers: { 'Content-Type': 'application/json' }});
    }

    const html = await response.text();

    // Check if it's actually a rental listing
    const isRental = html.includes('book') || html.includes('reserve') || html.includes('price');

    return new Response(JSON.stringify({
      verified: isRental,
      reason: isRental ? 'Listing appears active' : 'Could not confirm this is an active rental'
    }), { headers: { 'Content-Type': 'application/json' }});

  } catch (error) {
    return new Response(JSON.stringify({
      verified: false,
      reason: `Error fetching listing: ${error.message}`
    }), { headers: { 'Content-Type': 'application/json' }});
  }
}
