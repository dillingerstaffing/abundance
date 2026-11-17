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
