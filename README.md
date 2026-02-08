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

This creates optimal conditions for vitamin D synthesis, habenula reset, and general wellness recharge.

## Features

### Weather Scanning
- Real-time 7-day forecasts from NWS (free, no API key required)
- "Feels like" temperature calculation (wind chill / heat index)
- Sunshine percentage estimation from forecast descriptions
- Consecutive day window detection
- Sunball score ranking (0-100)
- Click any destination card to expand for full details

### Multi-Airline Flight Search
Nonstop routes from PVD and BOS via:
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
```

## Architecture

```
sunball-finder/
├── index.html              # Single-page app (client-side only)
├── wrangler.toml           # Cloudflare config
└── functions/api/          # Legacy API functions (not used in v2)
```

**100% client-side** — No backend required. Weather data comes directly from the free NWS API. All flight, hotel, and restaurant links go directly to booking sites.

## APIs & Cost

| API | Purpose | Cost |
|-----|---------|------|
| **NWS Weather** | 7-day forecasts | Free (public API, no key) |

**No API keys required. No usage costs. No rate limit concerns for normal use.**

The NWS API is a free public service. All other functionality uses direct links to external booking sites.

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

## The Habenula Connection

The habenula is the brain's "disappointment center" — it responds to light exposure and is implicated in seasonal affective disorder. Winter sun exposure in optimal conditions can help reset circadian rhythms and improve mood. This tool optimizes for the specific weather conditions that maximize safe, comfortable sun exposure.

## Future: Akathisia Management Integration

This tool may eventually integrate with broader akathisia management protocols, helping identify optimal travel windows for therapeutic sun exposure as part of a holistic approach to movement disorder management.

---

*For birds heading south for their habenula and health* 🦩
