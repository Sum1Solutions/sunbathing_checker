# Sunball Finder agent entry

Read README.md, WATCH_BRIEF.md, and API_COST_REVIEW.md first. This is the local Codex project
`Sunball Tracker` at `/Users/jb/coding/sunball-finder`.

Goal: help Jon find comfortable sunny trips with suitable nonstop flights and
good rates at his key favorite hotels, eventually through a recurring responsibility
assigned to his dot. Use flexible sunbathing categories and explain tradeoffs;
do not turn current numeric UI defaults into mandatory watch thresholds.
Jon selected the specific hotels already listed in the app; watch-hotels.json
records that list. Resolve current property identities without assuming the
legacy brand buckets are correct. Daily checks should retain comparable prices,
track meaningful changes, and include sourced local events. Historical patterns
can suggest future timing; label these leads speculative until actual forecasts
support them. No predictive accuracy or live schedule has been established.

Current app: index.html; active flight endpoint: functions/api/flights.js.
The hotels.js and skyscanner.js endpoints are older experiments, unused by the UI.

Preserve existing changes. Check Git status before edits. Never store provider
keys in source or expose them to the browser. Run smoke-test.js before deployment;
report network failures separately from assertion failures.

For travel alerts, require fresh sourced weather and dated flight evidence.
generateDemoWeather is synthetic and must never qualify an alert. Static route
tables are candidates, not proof of availability. Verify both directions of a
round trip, state passengers/currency/fare inclusions, and align travel dates with
the weather window. Missing data means unknown, not no availability.

Respect explicit user constraints. Weather categories are provisional preference
judgments, grounded in real forecasts. Evaluate sunshine, warmth, wind, rain, and
usable outdoor hours together. Judge value using airfare plus dated favorite-hotel
rates including taxes/fees; do not call a rate a deal without a valid comparison.
Keep alerts quiet unless a new worthwhile
match or meaningful improvement is found. Record observation times and deduplicate
offers. Search narrowly before spending provider credits. No booking is authorized.

Do not claim a dot connection, schedule, or alert delivery is working until it
has been configured and a real run has been verified.
