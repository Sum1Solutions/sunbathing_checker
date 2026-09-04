# Sunball Finder

**Tracey's Sunball Finder** — Finding perfect weather windows for Vitamin D & wellness recharge.

A tool for New Englanders seeking optimal sun exposure during winter. Scans warm destinations for consecutive days of ideal weather, cross-referenced with nonstop flights from PVD/BOS.

## Live

https://sunball-finder.pages.dev

## What is a "Sunball Window"?

A sunball window is a consecutive stretch of days with:
- **75%+ sunshine** (mostly sunny to clear skies)
- **Feels-like temperature in target range** (default: 72°F ±10°)
- **3+ consecutive days** meeting both criteria

This is a weather-planning heuristic for comfortable outdoor time. UVB light can contribute to vitamin D production in uncovered skin, while bright daytime light is a strong cue for the circadian clock. Actual vitamin D production varies by season, latitude, cloud cover, skin pigmentation, age, clothing, and sunscreen. Sunball Finder is not a medical device or a recommendation for a specific amount of sun exposure.

## Features

### Weather Scanning
- Real-time 7-day forecasts from NWS (free, no API key required)
- "Feels like" temperature calculation (wind chill / heat index)
- Sunshine percentage estimation from forecast descriptions
- Consecutive day window detection
- Sunball score ranking (0-100)
- Click any destination card to expand for full details

### Multi-Airline Flight Search
Verified dated nonstop results from PVD and BOS via SerpApi's Google Flights engine when configured:
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

### Hotel Preferences
- **Marriott Bonvoy** properties (for status benefits)
- **Noble House** boutique collection
- **Beach properties** for coastal sun exposure
- Direct links to Google search and Marriott booking

### Google destination links
- Open a large Google Maps area view centered on each destination
- Search Google Hotels for the selected city and dates
- Search Google Flights after live nonstop availability is verified

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
```

## Architecture

```
sunball-finder/
├── index.html              # Single-page app (client-side only)
├── wrangler.toml           # Cloudflare config
└── functions/api/          # Cloudflare Pages Functions for flight and hotel data
```

Weather data comes directly from the free NWS API. Flight lookups run through the Cloudflare Pages Function so the SerpApi key stays server-side; hotel and restaurant links go directly to external sites.

## APIs & Cost

| API | Purpose | Cost |
|-----|---------|------|
| **NWS Weather** | 7-day forecasts | Free (public API, no key) |

NWS is a free public service. The SerpApi key is stored as a Cloudflare Pages Secret; all other functionality uses direct links to external booking sites.

## Security Considerations

- No user data collected or stored
- No authentication required
- No API keys exposed (NWS is keyless)
- All external links open in new tabs
- No cookies or tracking
- Cloudflare Pages provides DDoS protection and SSL

## Criteria Defaults

- **Target temperature**: 72°F feels-like
- **Temperature range**: ±10°F (62-82°F window)
- **Minimum sunshine**: 75% (mostly sunny)
- **Consecutive days**: 3+
- **Airports**: PVD + BOS (toggle to filter)
- **Cannabis**: All destinations (assumes med card)

## The daylight connection

Sunball Finder is grounded in two established pieces of physiology, without trying to turn either into a treatment claim:

- UVB radiation from sunlight can trigger vitamin D synthesis in uncovered skin. The amount varies with season, latitude, cloud cover, skin pigmentation, age, clothing, and sunscreen. UV exposure also carries skin-cancer risk, so avoid burning and use appropriate protection. See the [NIH Office of Dietary Supplements vitamin D fact sheet](https://ods.od.nih.gov/factsheets/VitaminD-Consumer/).
- Light and dark are the strongest environmental cues for circadian rhythms. Bright daytime light helps the body align its internal clock with the day-night cycle. See the [National Institute of General Medical Sciences circadian rhythms overview](https://www.nigms.nih.gov/education/fact-sheets/Pages/circadian-rhythms).

The app plans comfortable, bright-weather travel windows; it does not prescribe sun exposure, diagnose a deficiency, or provide medical treatment.

---

*For birds heading toward brighter days* 🦩
