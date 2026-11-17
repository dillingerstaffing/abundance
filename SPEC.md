# ABUNDANCE: design spec

Brief (from the X thread, @superpager to @grok, Nov 16 2026): monitor the actual
costs of food, housing, energy, transport and healthcare in a given city, and
test the abundance thesis: essentials should consume a steadily smaller share
of a full-time minimum-wage paycheck. Grok's named sources: BLS CPI and average
prices, Zillow ZORI/ZHVI, HUD Fair Market Rents, EIA rates, AAA daily gas
prices, CMS hospital data, C2ER COLI, ocity.org.

Constraint set: 100% free to run, hosted on GitHub Pages (static), no API keys,
no build step, every number traceable to a reliable public source, as close to
real time as free sources allow.

## Data assemblies (all verified live Nov 16 2026)

| Assembly | Source | Cadence | Carries |
|---|---|---|---|
| Geocode | Open-Meteo Geocoding API | live | any city name to lat/lon, state, population |
| Place resolve | US Census TIGERweb (Incorporated Places, then CDP) | live | lat/lon to Census place GEOID |
| City economics | Census Reporter (ACS 2024 5-year) | annual | population, median household income, median gross rent, median home value, housing units, vacancy |
| Atmosphere | Open-Meteo Forecast + Air Quality APIs | 15 min / hourly | temperature, wind, solar radiation W/m2, US AQI, PM2.5 |
| Infrastructure | ohsome API counts + Overpass API point geometry (OpenStreetMap) | near live (OSM edits) | counts and point geometry for food, health, transport, energy POIs |
| Wages | US DOL state minimum wage table (embedded, retrieved Nov 16 2026) | annual | state minimum wage for the paycheck math |
| National context | BLS Public API v2 (no key) | monthly | CPI food at home, CPI medical care, CPI all items |

Thread sources not integrated, stated plainly in the app: Zillow and HUD need
keys or bulk downloads with no CORS access; AAA publishes no free API; EIA
requires a key. Their roles are covered by Census ACS (housing), BLS (food and
health prices), and OSM (facility supply).

## MECE decomposition of the interface

Seven assemblies. Every UI mechanic belongs to exactly one; together they are
the whole instrument.

1. WORLD SHELL: MapLibre GL canvas on CARTO vector basemaps (dark matter,
   voyager), camera flights, minimap, north reset, style toggle, attribution.
2. LENSES (Civ VII lens system): Overview, Housing, Food, Energy, Transport,
   Health, Air and Sun. A lens re-skins pin and hex color, re-orders the
   dossier, and re-aims the hex layer at one category.
3. DRILL STACK (dig down / dig up): L0 Nation (city pins) to L1 City
   (dossier + hex field) to L2 Hex (micro census of one cell) and back up by
   breadcrumb, Esc, or zooming out. Depth is a state, never a page change.
4. CITY DOSSIER (Civ city screen): one row per essentials category with value,
   per-10k density, score bar, source tag, freshness stamp; headline panel
   carries the Abundance Score and the paycheck math.
5. DATA ASSEMBLIES: the seven fetchers above, each with timeout, failure
   state shown as "unavailable" (never an invented number), and a cache.
6. SCORING: per-category 0 to 100 by min-max normalization (log scale for
   densities) across the 15 reference cities; composite is the plain mean.
   Rent burden = median gross rent / (wage x 173.33 h). Weights and formulas
   are printed in the Method panel in the app.
7. CHROME: top yields HUD (city, score, rent burden, live temp, AQI, clock),
   search, wage stepper, legend, method modal, toasts, keyboard map
   (arrows pan, + and - zoom, Esc digs up, 1 to 7 switch lenses).

## Assembly theory note

Primitives: pin, hex, chip, gauge, row, button. Components are assemblies of
primitives (lens rail, dossier row, HUD strip). Screens are assemblies of
components (nation view, city view, hex view). Assembly index of the full
instrument: 3 (primitive to component to screen to instrument). No screen is
hand-built outside this stack, so every mechanic inherits the same spacing,
type, and state rules.

## Visual law

Dark cartography first (CARTO dark matter), hairline 1px borders, 2 to 3px
radii, JetBrains Mono for numerals and labels, no glow, no pill chrome, dense
tabular rows. Camera moves are flights, never jumps. Live values pulse once on
update, then hold still.

## Addendum, Nov 16 2026: phone layout and data states (after Chris's iOS report)

Chris opened the live site on iOS and found the phone layout broken: headline yields invisible, category rows unreachable, hex cells apparently empty. A phone-viewport audit (390x844 and 375x667, Chromium and WebKit engines, touch input, all APIs served from captured real payloads) measured the causes and the fixes:

- HUD: on phones the single flex row crushed the yields strip to 0px wide (693px of content in a 0px slot). The HUD now wraps to two rows on narrow screens: brand/search/buttons, then the yields strip at full width, internally scrollable, every yield reachable.
- Dossier: the bottom sheet used max-height:44% with four pinned chrome blocks; on a 667px phone the scrollable body measured 0px tall, so categories, BLS strip and hex panel rendered into a zero-height box. The sheet now has a definite height (52vh, then 52dvh as the enhanced declaration), the sources footer scrolls with the body instead of pinning, score descriptions hide on phones, and a grip + EXPAND button grows the sheet to calc(100dvh - 156px), stopping below the drill bar.
- Lens rail: it was positioned over the sheet and intercepted its touches. It now docks directly above the collapsed sheet (bottom: calc(52dvh + 14px)) and fades out while the sheet is expanded (category rows inside the sheet switch lenses). The hex legend, previously display:none on phones, rides above the rail in compact form.
- Drill bar: it wrapped to two rows and overflowed the right edge. It is now a single non-wrapping internally scrollable strip; the L1 crumb drops the city name on narrow screens.
- Camera: flying to a city on a phone centered it under the sheet. flyTo now takes a -22% viewport-height offset on narrow screens so the city and its densest hexes land in the visible map area.
- Data states (the "missing data" half of the report): loading, loaded and failed were indistinguishable (all showed "--"), and a failed Overpass fetch was cached as an empty result for the whole session. Now every category row states loading vs unavailable, a failed row retries its fetch on tap, hex geometry tracks loading/ok/fail per city and category, failures are never cached, the hex panel shows the state explicitly with a RETRY button, and a panel left open refreshes itself when its data lands. Hex panel content also gained context: cell count against the city total, named sites listed individually, unnamed sites grouped by kind with counts, and a truncation note at the Overpass 900-element cap.
- Boot order: Ocean City's counts now load and the city opens before the other 14 cities stream in, instead of after the whole board.
- Overpass endpoints: a third mirror (overpass.nchc.org.tw) added after overpass-api.de and kumi.

Verification: the audit battery (no horizontal overflow, yields reachable, no rail/sheet overlap, touch-swipe scrolls the dossier, footer reachable at scroll bottom, hex tap opens a populated panel, sheet expands/collapses, method modal scrolls and closes, zero console errors) passes at both phone sizes in Chromium and WebKit, plus Overpass failure and 15-second-delay modes for the state UI, plus a desktop regression pass. One emulator caveat: the software-rendered WebKit in the test VM intermittently takes >15s to make hex features hit-testable; on GPU hardware this does not occur, and the same engine passed the tap test in other runs.

Boot resilience follow-up (same evening): the first live check of the phone fix found the Ocean City dossier complete but 5 of 15 reference-city pins still on ".." after 3.5 minutes (the last five in the queue), because a slow ohsome can make each city's two count rounds take a minute or more and a city that failed both rounds was stranded for the session. Counts requests now time out at 20s instead of 30s, and after the main pass a recovery sweep retries every city still missing a category; if any city still fails after that, a toast says so and names the recovery (tap the pin, selection already retries counts). Verified in the harness with a flaky-ohsome mode that fails the first 12 count requests for exactly those five cities: all 15 cities end scored, all counts ok.

Second-source counts (same evening, after the live recheck): the follow-up live check ran into an ohsome outage (0 of 15 pins in 6 minutes; the ohsome API also timed out from the VM shell while other egress worked). The dossier behaved as designed under the outage (rows labeled unavailable with tap-to-retry, composite withheld, nothing invented), but the counts had only one source. fetchCounts now falls back, per category, to an Overpass `out count` query over the same tag sets when ohsome fails both rounds; provenance is tracked per category and the dossier source line reads "via Overpass fallback" when it applies. The city-open toast no longer claims "ready" when counts are missing; it says some counts are unavailable and names the row-tap retry. Verified in the harness with ohsome fully down: all 15 cities score from the fallback with identical values, and the standard phone battery still passes at both sizes.

Progressive opening (same evening, after the third live check): with ohsome down and Overpass also slow from the checking browser, the previous build's boot waited for the home city's full counts (including the sequential fallback) before opening its dossier, so nothing rendered for 6 minutes even though Census, weather and air data were available. Loading is now phased everywhere: loadCityData renders after the Census/weather/air phase and again after counts; the boot opens the home city immediately after the reference fast pass and streams its counts behind the open dossier; the Overpass count fallback runs in parallel across categories with a 15s per-endpoint budget; fetchCounts is deduplicated while in flight. Proof in the harness with ohsome fully down and the fallback artificially crawled at 20s per query: the Ocean City dossier opens in 1.6s with real housing, rent burden and temperature, and the composite completes when the counts land. The standard phone battery still passes at both sizes.

Selected-city auto-retry (same evening, after the fourth live check): the progressive build opened the dossier in seconds live and 4 of 15 pins resolved within 2 minutes, but the open city's own counts had no timed retry of their own (the boot recovery sweep reaches the home city only after the whole queue drains). An open city with missing counts now retries on a slow clock (45s, 90s, then every 120s, at most 5 attempts, stopping when complete or when the user navigates away), so a flapping counts service completes the dossier by itself. Verified in the harness: with both count rounds forced to fail, the retry chain is armed (state visible) while the score is still blank, and the dossier completes when a later attempt lands.

Hex tiling correction (Nov 17): the hexagon polygons were drawn with vertices starting at 0 degrees while the grid spacing (dx = sqrt(3) R, dy = 1.5 R, alternate rows offset by dx/2) is the exact tiling for vertices starting at 30 degrees. The drawn cells therefore overlapped their neighbours by roughly 250 to 300 m, left uncovered slivers, and a site could be counted into one cell while falling inside the drawn polygon of another, so fills sat visibly off their clusters. hexPoly now starts at 30 degrees; verified numerically (4,000 sampled points: every point lies inside its nearest-centre hexagon, max centre distance 948 m against R = 950). The same change adds an Overpass concurrency guard (at most two queries in flight): a parallel burst was exhausting the instances' per-IP slots, so geometry and count fallbacks queued, timed out, and starved each other.

Pin anchor correction (Nov 17): the .pin rule declared position:relative, which overrides MapLibre's own position:absolute for marker elements (equal specificity, later stylesheet wins). Every pin therefore rendered displaced from its coordinate, about 280 px south at the checking window size, at every zoom, while flyTo and the dossiers stayed correct. The declaration is removed; markers are absolute again, and their absolutely positioned children (tip, ring) anchor to the pin as before. The defect was present since launch and was missed by every earlier check because none compared a pin's rendered position against its city on the basemap; Chris spotted it visually. Same run: counts are now merged, never replaced. A later fetch round that fails a category no longer erases a value an earlier round landed (observed live: Ocean City Food and Transport flipped back to unavailable minutes after loading, because the auto-retry re-fetched the whole city and overwrote them with nulls). fetchCounts seeds from the city's known counts and only fetches categories still missing.

Contention fix (Nov 17): the boot fired the home city's counts and the 14-city background pass simultaneously, and the Overpass queue was strictly FIFO, so the open city's fallback counts and hex geometry waited behind background cities while the shared services throttled the burst. Three changes: the background pass now waits until the home city's load settles (or 30 s) before starting; Overpass requests from the open city take a priority lane in the two-slot queue; the hex grid draws immediately on selection instead of after the full counts phase. The ohsome per-request timeout drops to 12 s so a hanging counts service yields to the fallback sooner.

Field gate and fallback scope (Nov 17): scores are ranks against the 15-city field, and a rank computed while only a few cities have reported is a provisional midpoint that collapses as the field fills (observed live: Ocean City composite 62 on a thin field, settling to 49 minutes later). Scores and composites now appear only once at least 8 of the 15 cities report in every category; measured values and counts always show, with a note in the dossier explaining the gate. The Overpass count fallback is scoped to the city on screen and to the recovery sweep, since running heavy fallback queries for all 15 cities through two slots stalled the background board. The auto-retry chain now toasts the city name plus ready when its counts complete.

Healing horizon (Nov 17): the open city's retry chain previously cancelled itself when the user drilled up to the nation view, and the board got exactly one recovery sweep. The chain now survives navigation (fetching pauses while its city is off screen and resumes when it returns) and runs up to 12 attempts over about 22 minutes; the board re-sweeps every 4 minutes up to 4 more times while any city remains stranded. Both exist because the free OpenStreetMap services throttle shared network addresses for minutes at a time and then recover; the app's job in those windows is to keep asking politely and to label everything it does not yet have.

Polite client (Nov 17, at Chris's direction: do not get rate limited, apply professional best practices): (1) localStorage cache, counts and hex sites for 24 h, Census for 7 days, so repeat visits cost the free services nothing and the board fills instantly from cache. (2) A per-host circuit breaker in both fetch paths: 3 consecutive failures trigger a cooling-off period (60 s doubling to at most 4 min) during which calls fail locally with zero network traffic, and a 429 or 503 Retry-After is always honoured. (3) Retry diet: fetchCounts makes one attempt per category per call (the 2.5 s immediate retry round is gone); the open city retries at 1 min, 3 min, then every 8 min; board re-sweeps run every 10 min, at most 3. (4) The Overpass count fallback is a single combined query for all missing categories instead of one query each. (5) The boot's background pass pauses 600 ms between cities. The footer now discloses the caching and backoff policy.

Never blank (Nov 17, at Chris's direction: once data is pulled it should always render, show how up to date it is, and always be able to render the latest): the repo ships data-snapshot.js, a dated snapshot of the ohsome counts for all 15 preset cities across all six categories, built by tools/build_snapshot.py (which parses the cities, boxes, and filters out of index.html so they cannot drift, and fetches from the same Census Reporter population figures the page uses). At boot every preset city is seeded from the snapshot, or from fresher figures saved on the device when those are newer, so dossiers, pins, scores, and hex fills render from the first paint. Live refresh then replaces the dated figures in place whenever the services answer: the boot pass refreshes every city once, opening a city refreshes it once in the background, and a REFRESH button in the dossier header refreshes the open city on demand. A failed refresh changes nothing on screen. The freshness line under each city name states the counts' provenance and date (snapshot, saved, live fetch, or live), and each category row carries the same label until that category has been fetched live this session. Only a call that actually fetched live data may renew the on-device cache stamp, so dated figures can never re-stamp themselves as fresh. Hex site geometry is not snapshotted (ohsome's geometry endpoint refuses this network with a 403 while its count endpoint answers, and Overpass is unreachable from here); site lists keep loading live in the browser over the counts-painted hex floor.

One reactive store (Nov 17, at Chris's direction: follow state management professional practices, a single reactive source of truth for all front-end state): all application state lives in exactly two places, S (navigation and view state) and the cities map (per-city data), and the rules are enforced by construction. Fetchers and event handlers only write state, then call commit(); they never touch the DOM and never call a render function. commit() batches: any number of writes within a frame produce ONE render() pass, and render() is the only place data meets the DOM. render() first derives everything derived in one place (deriveScores(): raw values for every city, then the reference field's ranges, then every city's scores and composites), then paints every view from that same state: pins, the dossier or nation panel, the breadcrumbs, the lens rail, the hex field. The panel's scroll position is preserved across repaints of the same view and reset when the view changes. Two views therefore cannot describe different states; the hex map/panel divergence was this bug class, and it is now structurally impossible rather than guarded case by case. The MapLibre surface is the one carve-out: drawHexes() paints it from store state, invoked by render() only when a hex input changes (city, lens category, geometry state or length, counting box, or an explicit re-open nonce), and directly by MapLibre's own style.load event and the hex panel's retry button, which must repaint or refetch on otherwise unchanged state. One-shot, store-independent displays (the clock, the BLS strip, the search suggestion list) and pure chrome (method overlay, sheet expansion) are view-local: they share no state with the store and cannot diverge from it. The device cache and the bundled snapshot are inputs: they write into the store through the same paths as live fetches (seedCity, cacheGet merges inside the fetchers).

Healing completed (Nov 17): the retry chain and the board passes originally healed counts only, so a Census failure at open stranded a city's housing row, burden figures, and scores for the whole session, failed hex site data was never retried, and a background city whose Census fetch failed could hold the scoring field below its gate. The open city's chain now re-runs its full data load (Census, weather, air, counts) and redraws failed hex geometry on the same polite clock; the slow pass, recovery sweep, and re-sweeps retry Census alongside counts; stranded detection counts a missing Census record as stranded. Search failures (geocoding down, no Census place for a result) now surface a message instead of failing silently. Hex geometry remains Overpass-only for now: the counts service's geometry endpoint returns an Apache 403 to every network tested (VM, fetch service, cloud browser), so it cannot serve as the second source; the per-endpoint wait for geometry is bounded at 30 s, with the healing chain retrying failed geometry for as long as the city stays open. (Two extra Overpass instances were added to the rotation and removed the same day: unverified, and one is the prime suspect in the zero-burial incident below.)

No zero burial (Nov 17, found by verification, not by a user): a live refresh of Austin returned 0 for every category from the Overpass fallback (a degraded reply: a regional instance answering for another continent, or a query that timed out mid-flight), and refreshCounts accepted the zeros over the snapshot's real figures, cached them on the device, and dragged Austin's score from 53 to 22; on the next visit the poisoned cache outranked the snapshot at seeding. The rules now: a live 0 never overwrites a held positive count in any merge; a cached 0 never outranks a positive snapshot figure at seeding; the saved label and date are claimed only when a saved figure is actually used. fetchCounts was already safe by construction (its fallback only fills categories that are missing); refreshCounts, which refetches everything, was the hole. The snapshot is a floor on values, not just on presence.

Tiled geometry (Nov 17, after Chris re-reported Austin still not loading on fresh reloads): the single whole-box site query was the wrong shape for large cities; the service kills it and the reply never lands, while small-city queries complete. fetchGeomRaw now tiles any box larger than 0.02 square degrees into quadrants (a quarter of the scan each), merges the points with type/id dedupe, and allows 60 s per endpoint attempt so a slow legitimate query can finish. Two gaps in the healing story were also closed: the retry chain now treats a failed site fetch for the open city's current lens as missing data (for a snapshot-complete city it was the only missing piece and the chain never started), and a failed site fetch starts the chain itself. The counts service's geometry endpoint was ruled out as a second source the same day: GET returns an Apache 403 from every network tested and a POST probe (approved by Chris) received no response at all in 40 s.
