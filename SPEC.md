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
