# Sunball Finder

**Tracey's Sun Ball Finder** — For birds heading south for their habenula and health.

A South Florida vacation finder with weather, flights, hotels, and verified rental search.

## Live

https://sunball-finder.pages.dev

## APIs Used

| API | Purpose | Auth |
|-----|---------|------|
| **NWS Weather** | South FL weather forecasts | None (free) |
| **Amadeus** | Flight & hotel search | OAuth (sandbox creds in wrangler.toml) |
| **Skyscanner** | Better flight coverage | RapidAPI key (secret) |

## Setup

```bash
# Install
npm install -g wrangler

# Local dev
wrangler pages dev .

# Deploy
wrangler pages deploy .
```

### Secrets

```bash
# Skyscanner (free tier, better route coverage)
# Get key: https://rapidapi.com/skyscanner/api/skyscanner-flight-search
wrangler pages secret put RAPIDAPI_KEY
```

Amadeus sandbox credentials are already in `wrangler.toml` (safe for sandbox use).

## Architecture

```
sunball-finder/
├── index.html              # Single-page app
├── wrangler.toml           # Cloudflare config
└── functions/api/          # Cloudflare Pages Functions
    ├── flights.js          # Amadeus flight search
    ├── hotels.js           # Amadeus hotel search
    └── skyscanner.js       # Skyscanner via RapidAPI
```

## Features

- **Weather**: 7-day forecast for Miami, Fort Lauderdale, West Palm Beach
- **Flights**: Searches Skyscanner first, falls back to Amadeus
- **Hotels**: Real Amadeus hotel offers with pricing
- **Rentals**: Pre-filled search links to Airbnb, VRBO, Booking.com
- **Natural language search**: "oceanfront 2br under $200/night pet-friendly"

## Flight Data Priority

1. **Skyscanner** (RapidAPI) — Better route coverage, free tier
2. **Amadeus** (sandbox) — Fallback, limited routes in sandbox

Results show source badge: green = Skyscanner, blue = Amadeus.

## Default Settings

- **Departure**: PVD (Providence)
- **Dates**: Configurable (designed for Jan 1-15)
- **Budget**: $500-1500/week rentals, $300-600 flights
