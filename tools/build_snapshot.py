#!/usr/bin/env python3
"""Build data-snapshot.js for the Abundance map.

Fetches OpenStreetMap counts (ohsome) for every preset city and every
category, and writes them as a dated snapshot the page ships with. The
page renders the snapshot instantly (never blank) and refreshes live on
top whenever the free services answer. Run from the repo root:
python3 tools/build_snapshot.py

Hex site geometry is not snapshotted: ohsome's geometry endpoint
refuses this network (Apache 403, while the count endpoint answers),
and Overpass is unreachable from here, so site lists keep loading live
in the browser, with the counts-painted hex fills as their floor.

The city boxes mirror boxFor() in index.html exactly: the population
comes from the same Census Reporter tables the page uses, and the
filters are parsed out of index.html so they can never drift apart.
"""
import json, math, re, sys, time, urllib.parse, urllib.request

UA = {"User-Agent": "abundance-snapshot-builder (github.com/dillingerstaffing/abundance)"}
import os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
html = open(ROOT + "/index.html").read()

presets = []
for m in re.finditer(r"\{name:'([^']+)',state:'[^']*',code:'([A-Z]{2})',lat:([\d.\-]+),lon:([\d.\-]+),geoid:'(\d+)'", html):
    presets.append({"name": m.group(1), "code": m.group(2), "lat": float(m.group(3)), "lon": float(m.group(4)), "geoid": m.group(5)})
cats = []
for m in re.finditer(r"\{id:'(\w+)', name:'[^']*', color:'[^']*', osm:'([^']*)'", html):
    cats.append({"id": m.group(1), "osm": m.group(2)})
assert len(presets) == 15, presets
assert len(cats) == 6, cats


def get_json(url, timeout=45):
    # the counts service slows down under load; a single unretried timeout
    # must not kill a 15-city build, so retry with real backoff
    last = None
    for attempt, wait in enumerate((0, 5, 15, 45)):
        if wait:
            time.sleep(wait)
        try:
            req = urllib.request.Request(url, headers=UA)
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return json.load(r)
        except Exception as e:  # timeouts, resets, 5xx: ride them out
            last = e
    raise last


def box_for(city, pop):
    half_km = min(16, max(5, 4 + math.sqrt(max(pop, 1000)) / 220))
    d_lat = half_km / 111.32
    d_lon = half_km / (111.32 * math.cos(math.radians(city["lat"])))
    return (city["lon"] - d_lon, city["lat"] - d_lat, city["lon"] + d_lon, city["lat"] + d_lat)


def acs_pop(geoid):
    u = ("https://api.censusreporter.org/1.0/data/show/latest?table_ids=B01003"
         "&geo_ids=16000US" + geoid)
    d = get_json(u)
    g = d["data"]["16000US" + geoid]["B01003"]
    return g["estimate"]["B01003001"]


def ohsome_count(bbox, filt):
    bb = ",".join(str(round(x, 6)) for x in bbox)
    u = ("https://api.ohsome.org/v1/elements/count?bboxes=" + bb +
         "&filter=" + urllib.parse.quote(filt))
    d = get_json(u)
    return int(d["result"][0]["value"])


def main():
    snap = {"asOf": int(time.time() * 1000), "counts": {}, "geom": {}}
    # checkpoint after every city, so a killed or timed-out build resumes
    # where it stopped instead of starting over (and re-asking the service
    # for cities it already answered)
    ckpt_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".snapshot-checkpoint.json")
    if os.path.exists(ckpt_path):
        try:
            ck = json.load(open(ckpt_path))
            if int(time.time() * 1000) - ck["asOf"] < 6 * 3600 * 1000:
                snap = ck
                print("resuming from checkpoint:", len(snap["counts"]), "cities done", flush=True)
        except Exception:
            pass
    for city in presets:
        key = city["name"] + "|" + city["code"]
        if key in snap["counts"]:
            print(key, "already fetched, skipping", flush=True)
            continue
        pop = acs_pop(city["geoid"])
        bbox = box_for(city, pop)
        counts = {}
        for cat in cats:
            counts[cat["id"]] = ohsome_count(bbox, cat["osm"])
            time.sleep(0.35)
        snap["counts"][key] = counts
        with open(ckpt_path, "w") as f:
            json.dump(snap, f)
        print(key, counts, flush=True)
    js = "window.ABUNDANCE_SNAPSHOT=" + json.dumps(snap, separators=(",", ":")) + ";\n"
    out_path = ROOT + "/data-snapshot.js"
    tmp_path = out_path + ".tmp"
    with open(tmp_path, "w") as f:
        f.write(js)
    os.replace(tmp_path, out_path)
    if os.path.exists(ckpt_path):
        os.remove(ckpt_path)
    print("wrote", out_path, ",", len(js), "bytes, asOf", snap["asOf"], flush=True)


if __name__ == "__main__":
    sys.exit(main())
