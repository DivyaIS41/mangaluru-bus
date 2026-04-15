"""
Builds graph-ready bus data from CSV-backed route data.
Self-contained - no external dependencies on missing files.
"""

from __future__ import annotations

import csv
import math
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path
from statistics import mean

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR.parent / "data"

# City center coordinates (Mangaluru)
CITY_CENTER = (12.8698, 74.8426)

# Canonical route CSV source.
# We intentionally load one network version at a time to avoid mixing
# alternate route datasets into a single graph.
PRIMARY_ROUTE_CSV = BASE_DIR / "csv" / "bus-data-old.csv"

CSV_FILES = [PRIMARY_ROUTE_CSV]

STOPS_CSV = DATA_DIR / "stops.csv"
DISTANCES_CSV = DATA_DIR / "stop_distances.csv"

# Stop name aliases for normalization
STOP_ALIASES = {
    "alake": "Alake",
    "ashoknagar": "Ashoknagar",
    "adyarpadav": "Adyar Padav",
    "baana": "Kaana",
    "baikampady": "Baikampady",
    "baikampadyindustrialestate": "Baikampady Industrial Estate",
    "bajalpakkaladka": "Bajal Pakkaladka",
    "balmatta": "Balmatta",
    "bendoorwell": "Bendoorwell",
    "bengare": "Bengre",
    "bikampady": "Baikampady",
    "bikkarnakatta": "Bikarnakatte",
    "buntshostel": "Bunts Hostel",
    "canararubber": "Canara Rubber",
    "carstreet": "Car Street",
    "chelairpadavu": "Chelyarpadavu",
    "chilimbi": "Chilimbi",
    "chithrapuracross": "Chithrapura Cross",
    "citycentre": "State Bank",
    "esi": "ESI",
    "ekkur": "Ekkur",
    "falneer": "Falneer",
    "falnir": "Falneer",
    "hampankatta": "Hampankatta",
    "jalliguddecross": "Jalligudde Cross",
    "jmroad": "JM Road",
    "jokatte": "Jokatte",
    "jeppu": "Jeppu",
    "jeppinamogaru": "Jeppinamogaru",
    "jeppupatna": "Jeppupatna",
    "jyoti": "Jyothi",
    "jyothi": "Jyothi",
    "kaana": "Kaana",
    "kaikamba": "Kaikamba",
    "kalavar": "Kalavar",
    "kankanadi": "Kankanady",
    "kankanady": "Kankanady",
    "karmar": "Karmar",
    "katipalla": "Katipalla",
    "kavoor": "Kavoor",
    "kodikalcross": "Kodikal Cross",
    "kodikalschool": "Kodikal School",
    "kudpu": "Kudpu",
    "kudputemple": "Kudpu Temple",
    "kudupu": "Kudpu",
    "kulai": "Kulai",
    "kuloor": "Kulur",
    "kulur": "Kulur",
    "kulurchurch": "Kulur Church",
    "kulshekarchowki": "Kulshekar Chowki",
    "kunjathbail": "Kunjathbail",
    "kuntikana": "Kuntikana",
    "ladyhill": "Lady Hill",
    "lalbagh": "Lalbagh",
    "lighthousehill": "Light House Hill",
    "mallikatte": "Mallikatte",
    "mangaldevi": "Mangaldevi",
    "mangaladevi": "Mangaldevi",
    "mangalajyothi": "Mangala Jyothi",
    "mannagudda": "Mannagudde",
    "mannagudde": "Mannagudde",
    "maroli": "Maroli",
    "marnamikatta": "Marnamikatta",
    "mcfcolony": "MCF Colony",
    "merlapadav": "Merlapadav",
    "milagres": "Milagres",
    "moodushedde": "Moodushedde",
    "morgansgate": "Morgans Gate",
    "mukka": "Mukka",
    "mugeru": "Mugeru",
    "muthappagudi": "Muthappagudi",
    "nagori": "Nagori",
    "nandigudda": "Nandigudde",
    "nandigudde": "Nandigudde",
    "nanthoor": "Nanthoor",
    "neermarga": "Neermarga",
    "nirmarga": "Neermarga",
    "nitkkrec": "NITK",
    "nitk": "NITK",
    "nithk": "NITK",
    "ontemar": "Ontemar",
    "pachanady": "Pachhanady",
    "pachhanady": "Pachhanady",
    "padeel": "Padil",
    "padil": "Padil",
    "paldane": "Paldane",
    "panambur": "Panambur",
    "pandeshwar": "Pandeshwar",
    "parkodi": "Parkodi",
    "pedamale": "Pedamale",
    "pilikula": "Pilikula",
    "polali": "Polali",
    "porttemple": "Port Temple",
    "preetinagar": "Preetinagar",
    "pumpwell": "Pumpwell",
    "sasihithlu": "Sasihithlu",
    "sasihitlu": "Sasihithlu",
    "sashihithlu": "Sasihithlu",
    "shedigudde": "Shedigudde",
    "shaktinagar": "Shaktinagar",
    "shivabagh": "Shivabagh",
    "shivbagh": "Shivabagh",
    "statebank": "State Bank",
    "surathkal": "Surathkal",
    "talapady": "Talapady",
    "tannirbavi": "Tannirbavi",
    "tannirbhavi": "Tannirbavi",
    "tannirbhavibeach": "Tannirbavi Beach",
    "tannirbhavibeachroad": "Tannirbavi Beach",
    "thokottu": "Thokottu",
    "ulayibettuschool": "Ulayibettu School",
    "ulaibettu": "Ulaibettu",
    "ulaibettu": "Ulaibettu",
    "urwastore": "Urwa Store",
    "urwastores": "Urwa Store",
    "valencia": "Valencia",
    "vamanjoor": "Vamanjoor",
    "vamanjuru": "Vamanjoor",
    "wenlockhospital": "Wenlock Hospital",
    "yemmekere": "Yemmekere",
}

# Landmarks data (hardcoded from original)
LANDMARKS = [
    ("Bajpe Airport", "S07", "transport"),
    ("KMC Hospital", "S10", "hospital"),
    ("Wenlock Hospital", "S11", "hospital"),
    ("Mangala Stadium", "S01", "landmark"),
    ("City Centre Mall", "S02", "shopping"),
    ("Mangaladevi Temple", "S14", "temple"),
    ("NITK Surathkal", "S23", "education"),
    ("Moodabidri Jain Temple", "S22", "temple"),
    ("Mangalore Central Rly", "S24", "transport"),
    ("St. Aloysius College", "S08", "education"),
]


def normalize_stop_name(name: str) -> str:
    """Normalize stop name to standard format"""
    token = re.sub(r"[^a-z0-9]+", "", name.lower().strip())
    return STOP_ALIASES.get(token, " ".join(part.capitalize() for part in re.split(r"\s+", name.strip()) if part))


def slugify(value: str) -> str:
    """Create URL-friendly slug"""
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug or "route"


def haversine_km(lat1, lng1, lat2, lng2):
    """Calculate straight-line distance between two points in km"""
    radius = 6371.0
    d_lat = math.radians(lat2 - lat1)
    d_lng = math.radians(lng2 - lng1)
    a = (
        math.sin(d_lat / 2) ** 2
        + math.cos(math.radians(lat1))
        * math.cos(math.radians(lat2))
        * math.sin(d_lng / 2) ** 2
    )
    return radius * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def load_stop_coordinates():
    """Load real coordinates from stops.csv"""
    stops = {}
    
    if not STOPS_CSV.exists():
        print(f"WARNING: {STOPS_CSV} not found. Using fallback coordinates.")
        return stops
    
    with open(STOPS_CSV, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            stop_name = row["stop_name"].strip()
            stops[stop_name] = {
                "lat": float(row["lat"]),
                "lng": float(row["lng"]),
                "zone": row.get("zone", "Unknown"),
                "is_hub": row.get("is_hub", "FALSE").upper() == "TRUE"
            }
    
    print(f"  Loaded {len(stops)} stop coordinates from {STOPS_CSV}")
    return stops


def load_precomputed_distances():
    """Load precomputed road distances from stop_distances.csv"""
    distances = {}
    
    if not DISTANCES_CSV.exists():
        print(f"WARNING: {DISTANCES_CSV} not found. Using haversine fallback.")
        return distances
    
    with open(DISTANCES_CSV, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            from_stop = row["from_stop"].strip()
            to_stop = row["to_stop"].strip()
            key = (from_stop, to_stop)
            distances[key] = {
                "distance_km": float(row["distance_km"]),
                "time_min": float(row.get("time_min", float(row["distance_km"]) * 3.5))
            }
    
    print(f"  Loaded {len(distances)} precomputed distances from {DISTANCES_CSV}")
    return distances


def _read_routes(csv_paths):
    """Read routes from CSV files"""
    routes = []

    for path in csv_paths:
        if not path.exists():
            print(f"  Warning: {path} not found, skipping")
            continue

        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)
            for row in reader:
                bus_no = (row.get("busNumber") or "").strip()
                description = (row.get("description") or bus_no or "Unnamed Route").strip()
                raw_stops = [part.strip() for part in (row.get("stops") or "").split(";") if part.strip()]
                stops = [normalize_stop_name(stop) for stop in raw_stops]

                if len(stops) < 2:
                    continue

                row_id = (row.get("id") or "").strip() or str(len(routes) + 1)
                route_id = f"{bus_no or 'R'}-{row_id}-{slugify(description)}-{slugify(path.stem)}"
                routes.append(
                    {
                        "route_id": route_id,
                        "route_no": bus_no or route_id,
                        "name": description,
                        "operator": "CSV Import",
                        "source_file": path.name,
                        "source_row_id": row_id,
                        "stops": stops,
                    }
                )

    print(f"  Read {len(routes)} route rows from CSV files")
    return routes


def _assign_fallback_coordinates(stop_meta, routes):
    """Assign fallback coordinates for stops missing real coordinates"""
    suggestions = defaultdict(list)

    # Interpolate between known stops
    for route in routes:
        route_stops = route["stops"]
        known = [
            (idx, stop_meta[name]["lat"], stop_meta[name]["lng"], stop_meta[name]["zone"])
            for idx, name in enumerate(route_stops)
            if stop_meta[name]["lat"] is not None and stop_meta[name]["lng"] is not None
        ]

        # Interpolate between known stops
        for (start_idx, start_lat, start_lng, start_zone), (end_idx, end_lat, end_lng, end_zone) in zip(known, known[1:]):
            gap = end_idx - start_idx
            if gap <= 1:
                continue

            for step in range(1, gap):
                stop_name = route_stops[start_idx + step]
                if stop_meta[stop_name]["lat"] is not None:
                    continue

                ratio = step / gap
                lat = start_lat + (end_lat - start_lat) * ratio
                lng = start_lng + (end_lng - start_lng) * ratio
                zone = start_zone if ratio < 0.5 else end_zone
                suggestions[stop_name].append((lat, lng, zone))

        # Extend from first known stop backwards
        if known:
            first_idx, first_lat, first_lng, first_zone = known[0]
            for idx in range(first_idx - 1, -1, -1):
                stop_name = route_stops[idx]
                if stop_meta[stop_name]["lat"] is not None:
                    continue
                offset = 0.004 * (first_idx - idx)
                suggestions[stop_name].append((first_lat - offset, first_lng - offset, first_zone))

            # Extend from last known stop forwards
            last_idx, last_lat, last_lng, last_zone = known[-1]
            for idx in range(last_idx + 1, len(route_stops)):
                stop_name = route_stops[idx]
                if stop_meta[stop_name]["lat"] is not None:
                    continue
                offset = 0.004 * (idx - last_idx)
                suggestions[stop_name].append((last_lat + offset, last_lng + offset, last_zone))

    # Apply interpolated coordinates
    for stop_name, candidates in suggestions.items():
        if stop_meta[stop_name]["lat"] is not None:
            continue
        stop_meta[stop_name]["lat"] = round(mean(lat for lat, _, _ in candidates), 6)
        stop_meta[stop_name]["lng"] = round(mean(lng for _, lng, _ in candidates), 6)
        stop_meta[stop_name]["zone"] = Counter(zone for _, _, zone in candidates).most_common(1)[0][0]

    # Final fallback: place unresolved stops in a circle around city center
    unresolved = [name for name, meta in stop_meta.items() if meta["lat"] is None or meta["lng"] is None]
    for index, stop_name in enumerate(sorted(unresolved)):
        ring = (index // 12) + 1
        offset = (index % 12) * (math.pi / 6)
        stop_meta[stop_name]["lat"] = round(CITY_CENTER[0] + (0.01 * ring * math.sin(offset)), 6)
        stop_meta[stop_name]["lng"] = round(CITY_CENTER[1] + (0.01 * ring * math.cos(offset)), 6)
        stop_meta[stop_name]["zone"] = "Unknown"
        print(f"  Warning: No coordinates for '{stop_name}', using fallback position")


def build_graph_dataset(csv_paths=None):
    """
    Build graph dataset with real coordinates and distances
    """
    csv_paths = [Path(path) for path in (csv_paths or CSV_FILES)]
    
    # Load real data if available
    real_coords = load_stop_coordinates()
    precomputed_distances = load_precomputed_distances()
    
    # Read routes
    routes = _read_routes(csv_paths)
    
    # Collect all unique stop names
    all_stops = set()
    for route in routes:
        all_stops.update(route["stops"])
    
    # Count routes per stop
    route_counts = Counter()
    for route in routes:
        unique_stops = set(route["stops"])
        for stop_name in unique_stops:
            route_counts[stop_name] += 1
    
    # Build stop metadata
    stop_meta = {}
    for stop_name in sorted(all_stops):
        coords = real_coords.get(stop_name, {})
        stop_meta[stop_name] = {
            "id": "",
            "name": stop_name,
            "lat": coords.get("lat"),
            "lng": coords.get("lng"),
            "zone": coords.get("zone", "Unknown"),
            "is_hub": coords.get("is_hub", False) or route_counts[stop_name] >= 4,
            "route_count": route_counts[stop_name],
        }
    
    # Assign fallback coordinates for missing stops
    _assign_fallback_coordinates(stop_meta, routes)
    
    # Assign IDs
    for idx, stop_name in enumerate(sorted(stop_meta), start=1):
        stop_meta[stop_name]["id"] = f"S{idx:03d}"
    
    # Build stops list
    stops = [
        (
            meta["id"],
            meta["name"],
            meta["lat"],
            meta["lng"],
            meta["zone"],
            meta["is_hub"],
        )
        for meta in stop_meta.values()
    ]
    
    # Build routes with stop IDs
    stop_id_lookup = {name: meta["id"] for name, meta in stop_meta.items()}
    graph_routes = []
    for route in routes:
        graph_routes.append(
            {
                "route_id": route["route_id"],
                "route_no": route["route_no"],
                "name": route["name"],
                "operator": route["operator"],
                "source_file": route["source_file"],
                "source_row_id": route.get("source_row_id"),
                "stops": [stop_id_lookup[name] for name in route["stops"]],
                "stop_names": route["stops"],
            }
        )
    
    # Build edge distances (with real or fallback values)
    edge_distances = {}
    for route in routes:
        stops_seq = route["stops"]
        for i in range(len(stops_seq) - 1):
            from_stop = stops_seq[i]
            to_stop = stops_seq[i + 1]
            key = (from_stop, to_stop)
            
            if key in precomputed_distances:
                edge_distances[key] = precomputed_distances[key]
            else:
                # Fallback to straight-line haversine
                from_coords = stop_meta[from_stop]
                to_coords = stop_meta[to_stop]
                dist_km = haversine_km(
                    from_coords["lat"], from_coords["lng"],
                    to_coords["lat"], to_coords["lng"]
                )
                edge_distances[key] = {
                    "distance_km": round(dist_km, 3),
                    "time_min": round(dist_km * 3.5, 1)  # Rough estimate: 3.5 min/km
                }
    
    print(f"  Built {len(stops)} stops, {len(graph_routes)} routes, {len(edge_distances)} unique edges")
    
    # Build landmarks using stop_id_lookup
    landmarks = []
    stop_id_by_name = {meta["name"]: meta["id"] for meta in stop_meta.values()}
    
    # Create a mapping from legacy stop IDs to names (approximate)
    legacy_stop_names = {
        "S01": "State Bank",
        "S02": "Hampankatta", 
        "S07": "Bajpe Airport",
        "S08": "Balmatta",
        "S10": "KMC Hospital",
        "S11": "Wenlock Hospital",
        "S14": "Mangaladevi",
        "S22": "Moodabidri",
        "S23": "Surathkal",
        "S24": "Mangalore Central Station",
    }
    
    for name, legacy_id, lm_type in LANDMARKS:
        stop_name = legacy_stop_names.get(legacy_id)
        if stop_name and stop_name in stop_id_by_name:
            landmarks.append((name, stop_id_by_name[stop_name], lm_type))
    
    print(f"  Loaded {len(landmarks)} landmarks")
    
    return {
        "stops": stops,
        "routes": graph_routes,
        "landmarks": landmarks,
        "edge_distances": edge_distances,
    }
