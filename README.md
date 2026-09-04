# Tracey’s Sunball Finder

**Tracey’s Sunball Finder** — Finding bright, comfortable weather windows for a warmer escape.

A tool for New Englanders seeking optimal sun exposure during winter. Scans warm destinations for consecutive days of ideal weather, cross-referenced with nonstop flights from PVD/BOS.

## Live

https://sunball-finder.pages.dev

## What is a "Sunball Window"?

A sunball window is a consecutive stretch of days with:
- **75%+ sunshine** (mostly sunny to clear skies)
- **Feels-like temperature in target range** (default: 72°F ±10°)
- **3+ consecutive days** meeting both criteria

This is a weather-planning heuristic for comfortable outdoor time. UVB light can contribute to vitamin D production in uncovered skin, while bright daytime light is a strong cue for the circadian clock. Actual vitamin D production varies by season, latitude, cloud cover, skin pigmentation, age, clothing, and sunscreen. Sunball Locator is not a medical device or a recommendation for a specific amount of sun exposure.

## Features

### Weather Scanning
- Real-time 7-day forecasts from NWS (free, no API key required)
- "Feels like" temperature calculation (wind chill / heat index)
- Sunshine percentage estimation from forecast descriptions
- Consecutive day window detection
- Sunball score ranking (0-100) for qualifying consecutive windows
- Clear “No Sunball window” state when good days are not consecutive
- Click any destination card to expand for full details

### Multi-Airline Flight Search
Verified dated nonstop results from PVD and BOS via SerpApi's Google Flights engine when configured. Flight searches are opt-in: click **Check flights** on an individual destination so a weather scan does not spend flight-search credits.
- **JetBlue** (Tracey flies free!)
- **Southwest**
- **Breeze**
- **Spirit**
- **Frontier**

Toggle airports on/off to filter which flights appear.

### Cannabis-Friendly Destinations
- **Recreational legal**: CA (LAX, SAN), NV (LAS), AZ (PHX)
- **Medical available**: PR (SJU), FL (all cities), LA (MSY)
- **Decriminalized**: USVI (STT, STX)
- Filter: show all (have med card), prefer rec, or require rec only
- Each destination includes a Google Maps search for nearby cannabis storefronts
- Hotel options and dispensary searches are revealed only when requested
- Retail access, possession limits, reciprocity, and visitor eligibility vary; verify current local rules before travel

### Hotel Preferences
- **Marriott Bonvoy** properties (for status benefits)
- **Noble House** boutique collection
- **Beach properties** for coastal sun exposure
- Direct links to Google search and Marriott booking

### Google destination links
- Open a large Google Maps area view centered on each destination
- Search nearby hotels and cannabis storefronts in Google Maps
- Reveal the curated hotel names for a destination with **Check hotels**
- Reveal a current Google Maps storefront search with **Check dispensaries**
- Search Google Hotels for the selected city and dates
- Search Google Flights after dated nonstop availability is verified

### Restaurant Recommendations
- Curated restaurant picks for each destination
- Direct links to **OpenTable** and **Resy** for reservations

## Destinations (19 total)

| Code | City | State | Cannabis | Airlines from PVD | Airlines from BOS |
|------|------|-------|----------|-------------------|-------------------|
| LAX | Los Angeles | CA | Rec | Breeze | JetBlue, Spirit |
| SAN | San Diego | CA | Rec | Breeze | JetBlue, Spirit |
| LAS | Las Vegas | NV | Rec | Breeze, Spirit | JetBlue, Southwest, Spirit |
| PHX | Phoenix | AZ | Rec | Breeze | JetBlue, Southwest, Spirit |
| SJU | San Juan | PR | Med | JetBlue | JetBlue, Spirit |
| STT | St. Thomas | USVI | Decrim | - | JetBlue, Spirit |
| STX | St. Croix | USVI | Decrim | - | JetBlue |
| FLL | Fort Lauderdale | FL | Med | JetBlue, Breeze, Spirit | JetBlue, Southwest, Spirit |
| MIA | Miami | FL | Med | Spirit | JetBlue, Spirit |
| PBI | West Palm Beach | FL | Med | JetBlue, Breeze | JetBlue |
| TPA | Tampa | FL | Med | JetBlue, Breeze, Southwest, Spirit, Frontier | JetBlue, Southwest, Spirit, Frontier |
| RSW | Fort Myers | FL | Med | Breeze, Southwest | JetBlue, Southwest, Spirit |
| MCO | Orlando | FL | Med | JetBlue, Breeze, Southwest, Spirit, Frontier | JetBlue, Southwest, Spirit, Frontier |
| JAX | Jacksonville | FL | Med | Breeze | JetBlue |
| CHS | Charleston | SC | None | Breeze, JetBlue | JetBlue, Southwest |
| SAV | Savannah | GA | None | Breeze | JetBlue |
| MYR | Myrtle Beach | SC | None | Spirit | Spirit |
| MSY | New Orleans | LA | Med | Breeze, Spirit | JetBlue, Southwest, Spirit |
| AUS | Austin | TX | None | Breeze | JetBlue, Southwest, Spirit |

## Setup

```bash
# Install Wrangler
npm install -g wrangler

# Local dev
wrangler pages dev .

# Deploy
wrangler pages deploy .

# Lightweight production smoke test (Node 18+; no install required)
node smoke-test.js

# Test another environment
node smoke-test.js https://your-preview.pages.dev

# Configure the production flight-search secret (secure terminal prompt)
wrangler pages secret put SERPAPI_KEY --project-name sunball-finder
```

## Architecture

```
sunball-finder/
├── index.html              # Single-page app (client-side only)
├── wrangler.toml           # Cloudflare config
└── functions/api/          # Cloudflare Pages Functions for flight and hotel data
```

Weather data comes directly from the free NWS API. Flight lookups run through the Cloudflare Pages Function so the SerpApi key stays server-side; hotel and restaurant links go directly to external sites.

The local `file:///.../index.html` file is useful for reviewing the static UI, but it cannot run the `/api/flights` Function. Use `wrangler pages dev .` for a local end-to-end test.

## APIs & Cost

| API | Purpose | Cost |
|-----|---------|------|
| **NWS Weather** | 7-day forecasts | Free (public API, no key) |
| **SerpApi Google Flights** | Opt-in dated nonstop fares and times | Free account tier; paid plans vary |

NWS is a free public service. The SerpApi key is stored as a Cloudflare Pages Secret; all other functionality uses direct links to external booking sites. SerpApi generally counts one successful search as one credit. The app caches an identical flight request at Cloudflare’s edge for one hour, so repeated checks for the same origin, destination, dates, passenger count, and nonstop setting avoid another provider request.

## Security Considerations

- No user data collected or stored
- No authentication required
- No API keys exposed (NWS is keyless)
- All external links open in new tabs
- No first-party cookies or tracking are used by the app; external sites may apply their own policies after a user opens a link
- Cloudflare Pages provides DDoS protection and SSL

## Criteria Defaults

- **Target temperature**: 72°F feels-like
- **Temperature range**: ±10°F (62-82°F window)
- **Minimum sunshine**: 75% (mostly sunny)
- **Consecutive days**: 3+
- **Airports**: PVD + BOS (toggle to filter)
- **Cannabis**: All destinations (assumes med card)

## Flight provider notes

SerpApi’s Google Flights engine is a third-party search service, not an official Google Flights API. Results are treated as observed search results, not a booking guarantee. A route can have no result for a particular date even when an airline operates it seasonally or on other days.

The repository also contains older `functions/api/hotels.js` and `functions/api/skyscanner.js` handlers from earlier experiments. The current UI does not call those handlers; hotel discovery currently uses direct Google/Marriott links, and the active flight handler is `functions/api/flights.js`.

## Production checklist

- Open [the production site](https://sunball-finder.pages.dev), not the local `file:///` file, for live Functions.
- Confirm `SERPAPI_KEY` is present as a Cloudflare Pages Secret.
- Run `node smoke-test.js https://sunball-finder.pages.dev` after deployment.
- Run a weather scan, then use **Check flights** on one destination only when needed.
- Treat forecast sunshine as an estimate from NWS descriptions; the app does not measure UV or vitamin D production.

## The daylight connection

Tracey’s Sunball Finder is grounded in two established pieces of physiology, without trying to turn either into a treatment claim:

- UVB radiation from sunlight can trigger vitamin D synthesis in uncovered skin. The amount varies with season, latitude, cloud cover, skin pigmentation, age, clothing, and sunscreen. UV exposure also carries skin-cancer risk, so avoid burning and use appropriate protection. See the [NIH Office of Dietary Supplements vitamin D fact sheet](https://ods.od.nih.gov/factsheets/VitaminD-Consumer/).
- Light and dark are the strongest environmental cues for circadian rhythms. Bright daytime light helps the body align its internal clock with the day-night cycle. See the [National Institute of General Medical Sciences circadian rhythms overview](https://www.nigms.nih.gov/education/fact-sheets/Pages/circadian-rhythms).

The app plans comfortable, bright-weather travel windows; it does not prescribe sun exposure, diagnose a deficiency, or provide medical treatment.

---

*For birds heading toward brighter days* 🦩
