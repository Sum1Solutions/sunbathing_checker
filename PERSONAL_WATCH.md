# Personal watch: working preview

Built October 6, 2026. Open http://127.0.0.1:8788/watch.html while the local
preview is running. Start it with `node scripts/preview.mjs` from this repo.

## Available now

- Real Open-Meteo hourly forecasts for 19 destinations, with no demo-weather fallback.
- Flexible good/excellent/mixed/poor sunbathing judgments from 11am–4pm warmth,
  cloud, wind, and rain; best dates for the selected stay length. Arrival/departure
  days are excluded from the stay score. Extended forecasts are labeled lower confidence.
- Specific existing favorite-hotel selectors, PVD/BOS choices, and adult count.
- Opt-in hotel-zone beach, coast, and sky cameras (`Check live beach cams` / `Check live sky & resort cams`), prioritized by the selected favorite hotel, with a lazy-mounted live sky/cloud/wind map preview, Windy daylight replay backup, and on-demand OpenStreetMap/coordinate backup lookup.
- On-demand flight lookups through the existing production flight endpoint in
  local preview. No production key is downloaded or shown.
- Three-year historical modeled-weather exploration for seasonal timing.
- Browser-saved comparable quotes and export, with user-verified quote entry for
  actual airfare/hotel totals and rate terms. The app flags 10% AND $150 declines
  with good/excellent weather; this is a fitted initial policy, not proven value.
- A conservative session provider-call reservation limit. It is not a durable
  monthly quota or a shared account usage meter.
- Runnable free daily weather collector: `node scripts/watch-daily.mjs`. It stores
  snapshots/history under ~/.local/share/sunball-finder by default; set
  SUNBALL_DATA_DIR to another private location if desired. It makes no paid price
  calls. It is not scheduled automatically and does not deliver notifications.

## Existing connections verified

Cloudflare production secret-name listing returned SERPAPI_KEY, AMADEUS_CLIENT_ID,
AMADEUS_CLIENT_SECRET, RAPIDAPI_KEY, and GOOGLE_MAPS_KEY. Secret values were not
read. Presence does not establish quota, provider account status, or result quality.

## Built but awaiting private deployment

functions/api/watch-rates.js searches the selected hotel's public rates through
SerpApi and follows the outbound departure token to verify a nonstop return. It
returns explicit incomplete/unknown states when either direction or hotel terms
are missing. Public hotel quotes never automatically qualify a verified alert.

Production secrets are server-side and unavailable to local code. The preview
therefore uses only the existing deployed flight endpoint; the new hotel/return
handler has mocked contract tests, not a successful live provider test. Deploying
it requires a WATCH_ACCESS_TOKEN secret, entered in the dashboard when prompted,
so arbitrary public visitors cannot spend personal search credits. It still needs
an enforced durable quota ledger before unattended paid collection.

Do not deploy the repository root as static content without reviewing what is
published. Serve only the website assets and appropriate Functions. Private
observations must stay outside the published directory.

## Remaining work

Daily unattended price collection, durable quota accounting, delivered alerts,
automated sourced event collection, verified hotel identities/coordinates, and
forecast-prediction evaluation are not active. Events are currently explicit
research links. Seasonal analysis is city-area reanalysis, not hotel microclimate
or a prediction of future weather/prices. Personal preferences/date lengths default
to four nights and one adult and can be changed; they are not inferred facts.

The existing index.html flamingo edits were preserved. No production deployment,
subscription, or booking was performed.

## Verification

`node scripts/watch-test.mjs` checks missing data, weather ordering, contiguous
stays, comparable-price changes, and incomplete quotes staying out of alerts.
`node scripts/watch-api-test.mjs` checks provider configuration, public-access
blocking, allowed hotel validation, outbound/return handling, and incomplete hotel
terms. Browser verification exercised actual weather scans across all destinations.

The free collector also succeeded for 19/19 destinations with observations saved
in a temporary test directory. A live local-preview BOS–SAN search for October
14–18 returned an observed $741 quote via the existing endpoint; the UI explicitly
marked return verification and hotel pricing incomplete. Historical exploration
returned San Diego seasonal results for 2023–2025. These are time-bound test
observations, not a current booking recommendation. Cloudflare Functions compiled
successfully, without deployment.
