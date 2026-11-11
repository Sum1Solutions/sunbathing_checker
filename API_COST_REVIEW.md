# Affordable watch design

Reviewed October 6, 2026. Recommendation based on repository history and current
vendor documentation; no paid subscription or provider migration was performed.
Account-specific quotas, keys, and live result coverage remain unverified.

## What was previously changed

Git commit c675a4d replaced the active flight search with SerpApi on September 4.
969295b made flight checks opt-in and 5a74379 added a one-hour edge cache.
The current UI uses that flight endpoint; hotels.js still targets the Amadeus
test environment and selects the first ten city hotels, not the favorite list.
skyscanner.js retains an old RapidAPI Browse Quotes integration. Its comment
claiming unlimited free requests is historical and was not verified. Neither
legacy endpoint should be the foundation of this watch without fresh validation.

## Recommended architecture

Keep the existing website as a viewer and interactive search surface. Build a
small scheduled collector with persistent observations and a shared quota ledger.
Use ordinary code for collection, comparison, and weather categorization; reserve
dot reasoning/browser work for interpreting events, checking ambiguous properties,
and validating strong opportunities. Full browser or language-model research on
every destination every day would consume time and account allowance even where
there is no separate API charge.

Run the daily decision cycle across all destinations, but refresh inputs at
different cadences:

- Weather: daily, hourly variables at beach/pool locations. Open-Meteo is a
  candidate for consistent geographic coverage and historical inputs; retain NWS
  as a source/check where suitable. Never replace a failed forecast with demo days.
- Historical weather: fetch bounded seasonal data once, save it, and refresh
  infrequently. Historical reanalysis is modeled data, not a promise for a date.
- Events: official calendars weekly, and recheck shortlisted events before an
  alert; use ordinary pages or feeds where available rather than paid search for
  every city each day.
- Flights/hotels: bounded daily shortlist plus a rotating exploration allocation
  for promising future periods. Weather-first alone misses advance bargains;
  reserve some queries for seasonal/event leads. Report what was checked and
  data age, so partial coverage is visible.
- Finalists: verify both flight directions and favorite-hotel total/terms before
  notifying. Browser checks at the airline/hotel can validate member rates and
  benefits that public search results cannot establish.

Start locally with a scheduled Codex/dot run and SQLite/JSON observations; the
computer must be available. For independent operation, use a separate Cloudflare
Worker with Cron and D1. The existing Pages configuration is not a scheduled
collector. Free Workers limits require small batches and measured CPU use; a
paid Workers plan starts at $5/month if needed. Notification delivery and dot
access are separate pieces that still need configuration and verification.

## Current cost options

| Option | Published cost/allowance | Role and limitation |
| --- | --- | --- |
| Open-Meteo open access | $0 for non-commercial use; 10,000 calls/day, 300,000/month | Personal weather/history candidate; attribution and terms apply; no uptime guarantee |
| SerpApi Free | $0; 250 searches/month | Cheapest pilot using the current flight integration; flights and hotels share the search budget |
| SerpApi Starter | $25/month; 1,000 searches/month | More shortlist coverage with little migration work |
| SearchApi Developer | $40/month; 10,000 searches/month | Candidate for broader coverage; advertised Flights/Hotels products need a live comparative pilot before migration |
| Cloudflare Workers | Free tier; paid starts at $5/month | Collector hosting, separate from travel-search spend and agent usage |

Sources:
https://open-meteo.com/en/pricing
https://open-meteo.com/en/docs/historical-weather-api
https://serpapi.com/pricing
https://serpapi.com/google-hotels-api
https://www.searchapi.io/pricing
https://developers.cloudflare.com/workers/platform/pricing/
https://developers.cloudflare.com/workers/platform/limits/

SerpApi counts successful searches, including empty result sets; failed and cached
searches are excluded under its published billing rules. Budget conservatively
for every attempted provider request, then reconcile observed usage. A hotel city
search may return multiple favorites, but completeness is not guaranteed; detail
requests, pagination, additional dates, and return-flight verification may add
calls. Resolve property identities once and reuse provider IDs/tokens.

## Search budget arithmetic

These are derived upper-bound planning examples using 31 days and one request
per listed lookup. Actual verification sequences may cost more.

- Lean free pilot: 6 routine provider calls/day = 186/month; reserve 64 for
  verification, exploration, and setup. This is selective coverage, not all hotels.
- SerpApi Starter: 25 routine calls/day = 775/month; reserve 225 of the 1,000.
- SearchApi candidate: 250 routine calls/day = 7,750/month; reserve 2,250 of 10,000.
- Naive one-date scan: 68 hotel entries + 19 destinations × 2 origins = 106
  calls/day, or 3,286/month, before details/return checks. Four date combinations
  become 13,144/month. Some hotels are aliases, and grouped city search can reduce
  calls, but neither reduction should be assumed before testing.

Use a durable quota ledger shared by website and collector, reserve credits before
dispatch, cap retries/concurrency, and stop rather than renew automatically.
Protect paid searches from unrestricted public triggering: current /api/flights
has no authentication or shared daily budget. Cache canonical identical searches
within a daily run, retaining original observation time; refresh final candidates
when stale. The existing one-hour edge cache alone does not save daily queries.

## Provider choice and next validation

Begin with SerpApi's free tier and existing account if available. Add favorite-
hotel search via the same provider, preserve optional flight price insights, and
build observation history without buying a historical fare dataset. A free pilot
will rotate coverage and may miss short-lived deals; make that tradeoff explicit.

If measured needs exceed 250 but fit 1,000 searches, $25/month is the lower cash
commitment. Above 1,000, compare SearchApi's $40 tier against SerpApi's $75/5,000
tier: SearchApi is cheaper on advertised volume, but coverage, freshness, return
itinerary support, and hotel rate completeness must decide the switch. A cheap
request with unusable results is not good value.

Amadeus Self-Service documentation lists exclusions for low-cost carriers and
several major airlines, making it a weak sole flight source for this repo's
carrier mix. The FAQ was found in official search but its page could not be
fetched in this review; recheck the limitation before any implementation decision.
https://admin.developers.amadeus.com/self-service/apis-docs/guides/developer-guides/faq/

Pilot a few representative destinations, favored hotels, both origins, multiple
dates and room/fare terms. Measure successful usable results per credit, missed
properties/carriers, rate completeness, latency, and manual verification effort.
SearchApi documentation fetches failed in this review; pricing/product advertising
was readable, but technical parity was not established. Do not migrate on price
alone. Do not treat a dot's browser as a free unlimited scraping service.

The watch remains unimplemented. This review changes the design recommendation,
not runtime behavior, account billing, or notification status.
