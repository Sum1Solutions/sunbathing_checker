# Sunny trip watch: orientation and handoff

Inspected October 6, 2026. This file records the requested direction and code
observations; it does not establish a running watch.

## Requested outcome

Jon wants his dot eventually to access this project, regularly find good weather
with good nonstop flights and good rates at the key hotels he likes, and alert
him when a worthwhile combination appears. Rank weather by practical sunbathing
quality rather than treating the current numeric defaults as rigid gates.
The repo is already a local Codex project named **Sunball Tracker**.
Read API_COST_REVIEW.md for the October 6 provider and architecture review.
The daily cycle should scan weather broadly and price a bounded rotating shortlist,
with a shared quota ledger; it need not re-query every hotel/date every day.

## Current implementation observed

- Single HTML app hosted on Cloudflare Pages; README lists
  https://sunball-finder.pages.dev. Live availability was not verified: the shell
  smoke test failed at fetch, before content assertions.
- 19 destinations; PVD and BOS origins; default weather criteria are 72°F ±10°F,
  at least 75% estimated sunshine, and at least 3 consecutive qualifying days.
- NWS forecasts are fetched in the browser. Sunshine is inferred from forecast
  language. On request failure, synthetic days from generateDemoWeather are used
  and labeled estimates. These cannot support real travel alerts.
- Flight lookups are opt-in POST requests to /api/flights, backed by SerpApi
  Google Flights with a server-side SERPAPI_KEY and one-hour edge cache. Production
  secret presence and a successful live fare lookup have not been verified.
- Flight dates use the selected start date and a hard-coded return nine days
  later, rather than the detected best weather window. One adult is requested.
- The flight handler normalizes returned segments and prices but does not provide
  independently verified return-leg details. Nonstop labeling checks absence of
  layovers; segment continuity and both directions need stronger verification.
- Static airline route lists narrow the candidate set and may become stale.
- Hotels currently use curated names and external search links, without live
  rate comparison. Marriott/Noble House preferences and cannabis filters exist;
  whether those preferences apply to Jon's watch needs confirmation.
- No scheduler, stored watch preferences, offer history, deduplication, or alert
  delivery is implemented in this repository.

## Preferences to establish

Confirm origins, passengers, trip length, departure flexibility/notice, acceptable
flight times/durations, and baggage/fare class, plus useful price reference points.
Jon confirmed the specific hotels already mentioned in the repo as the watch list;
watch-hotels.json captures those names across all destinations. Verify current
property identities, aliases, locations, and operating status before looking up
rates; legacy brand buckets are not proof of affiliation. Hotel rates are required in the value
assessment. App defaults are provisional, not Jon's confirmed watch settings.
Jon proposed a daily check; use America/New_York. Exact run time remains unset.

## Daily checks, changes, and anticipation

Each daily run should save comparable airfare and favorite-hotel quotes, total
trip cost, availability, weather category/confidence, and relevant local events.
Keep observation time distinct from travel dates. Compare identical trips over
time and comparable alternative dates separately: changing rooms, stay lengths,
fare inclusions, or cancellation terms must not masquerade as a price drop.

Provisional alert policy (proposed starting values, not calibrated results):

- A newly complete trip has good/excellent forecast-backed sunbathing weather and
  unusually good value relative to a valid comparable baseline: initially at or
  below the 25th percentile of comparable observed total prices.
- A previously tracked good/excellent trip drops at least 10% AND $150 in total
  cost compared with its last alerted comparable quote, or its first comparable
  quote when it has never been alerted. Record flight and hotel contributions.
- Weather improves from mixed to good/excellent while a previously identified
  good rate remains available, or a favored hotel becomes available at good value.
- An interesting local event creates a worthwhile combination; identify the
  event's appeal as a proposed fit until Jon's interests are known. Events also
  supply crowd, traffic, availability, and price-pressure context.

Daily checking is not daily messaging. Recheck a candidate before alerting, and
deduplicate by hotel, room/rate terms, flights, and travel dates. Small price
movements alone do not trigger alerts. Before sufficient comparable history
exists, mark baseline confidence low and avoid inventing historical percentiles.
An initial percentile baseline should require at least 20 independent comparable
observations spanning 14 days; cached repeats do not count as new observations.
These sample requirements are provisional policy, not statistical validation.

Use two planning horizons:

1. Near-term opportunities: actual destination forecasts plus current dated
   nonstop flights and hotel quotes. Assess sunbathing at the hotel's beach/pool
   location, not merely the airport or city center.
2. Advance watchlist: seasonal historical weather distributions, observed price
   history, booking lead time, weekday/holiday patterns, and sourced event dates
   identify promising future periods. Label these as speculative timing leads,
   not forecast-backed weather promises. Refresh once actual forecasts arrive.

Historical weather should describe the distribution of usable sunbathing days,
not just monthly mean temperature. Climate outlooks provide broad probabilities,
not guaranteed sun on particular dates. Do not promise future fare drops from
a short price series. Save predictions and assess later outcomes before claiming
predictive skill; begin with explainable seasonal and comparable-price baselines.

For events, use official organizers, venues, convention calendars, and destination
tourism sources. Store name, location, dates, source URL, checked time, and whether
the source confirms the current edition. Include nearby hotel areas and transfer
time. Event-driven price pressure is an inference unless observed quotes support
it; do not automatically exclude events or assume Jon wants to attend them.

SerpApi documents optional flight price insights/history, but the current flight
handler discards them. Preserve them with provenance if available; they are
flight-search context, not a favorite-hotel or whole-trip baseline. Hotel history
must come from sourced historical data or accumulated comparable daily quotes.

Sources checked for planning: https://serpapi.com/google-flights-price-insights
and https://www.weather.gov/mfl/climate?tab=nowdata.

## Weather and value categories

Proposed weather categories: excellent for sunbathing, good, mixed/marginal, poor,
and unknown. These labels are a provisional fitted preference model, to be tuned
with Jon's feedback. Evaluate daytime sunshine/cloud cover, temperature, wind,
rain risk, and the length/timing of usable outdoor periods together. Explain why
a trip receives its category and show the forecast evidence. Do not equate an
estimated sunshine percentage with measured sunlight or safe UV exposure.

Rank whole trips using sunbathing quality, convenient nonstop travel, favorite
hotel suitability, and total cost. A slightly cooler sunny sheltered pool day may
be attractive; a warm but windy or rainy beach day may be weak. Those examples
are proposed judgments, not confirmed personal preferences. Surface tradeoffs
instead of enforcing arbitrary temperature, sunshine, or consecutive-day cutoffs.

Judge hotel value against comparable dates, room types, and rate terms at each
favorite property when reliable comparisons exist. Include taxes, resort fees,
and any required extras in the stay total, and show nightly price plus airfare
and combined total. Without a valid baseline, report the observed price and mark
deal quality unknown. Distinguish a cheap trip from a good rate at a favored hotel.
Explicit user constraints remain binding; flexible categories do not override them.

## Implementation path

1. Store confirmed watch preferences separately from UI defaults.
2. Extract weather/window matching into code callable without the browser. Use
   actual forecasts only and support destinations outside NWS coverage with a
   verified provider; preserve unknown/error states and forecast horizon limits.
3. Search flights for the best sunbathing opportunities first, with a bounded
   provider-credit budget. Verify dated nonstop outbound and return itineraries,
   price basis, fare inclusions, and timing against the useful weather days.
4. Search live rates at the key favorite hotels for those dates; compare consistent
   occupancy, room types, taxes/fees, and cancellation terms. Show airfare, hotel
   stay cost, and the combined total separately.
5. Persist comparable daily quotes, check times, event records, forecast evidence,
   and offer fingerprints. Build historical baselines and an advance watchlist.
   Alert only on new worthwhile
   opportunities or a material improvement, with dates, weather evidence,
   airlines/times, price and inclusions, source links, and observation times.
6. Connect the dot's computer access to this checkout, or expose a narrow hosted
   tool/API if remote operation is needed. Local project registration alone does
   not establish dot access. Configure the recurring responsibility and verify
   one complete run plus delivered alert before claiming the watch is active.

## Dot responsibility draft

Use this repository and confirmed watch preferences to check daily for
sunbathing opportunities, good dated nonstop round-trip fares, and rates at the
specific hotels in watch-hotels.json. Track comparable prices and meaningful
changes. Use historical weather, price trends, and sourced local events to flag
promising future timing, clearly distinguished from forecast-backed opportunities.
Rank complete trips by weather category, convenience, hotel fit,
and value; explain material tradeoffs instead of imposing rigid app-default gates.
Check actual forecasts
first, then spend flight queries on the strongest candidates. Never use synthetic
weather or static route lists as availability evidence. Include dated hotel rates
and fees; mark incomplete trip pricing as incomplete. Notify Jon only when a new
worthwhile trip or material improvement
is verified; stay quiet when nothing actionable changes. Report a persistent
failure requiring Jon's action once, with the missing dependency. Include useful
dates, sources, observation times, and booking/search links. Do not book travel.

## Working tree at inspection

Existing index.html changes adjust the flamingo size/spacing and accessible label;
untracked .wrangler/ exists. Both were preserved. This orientation adds AGENTS.md
and WATCH_BRIEF.md without changing runtime behavior or activating a schedule.
