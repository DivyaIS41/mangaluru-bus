# Dataset Processing

This directory handles converting CSV bus route data into a Neo4j graph database.

## Files

### `csv_graph_data.py`

Transforms raw CSV route data into a structured graph format.

**Key Functions:**

- `build_graph_dataset()` - Main entry point, returns graph structure
- `normalize_stop_name()` - Standardizes stop names using STOP_ALIASES
- `calculate_zone()` - Assigns zones based on geographic proximity
- Stop name aliases for handling variations

**Processing Steps:**

1. Load route CSV files from `csv/`
2. Parse stop sequences from each route
3. Normalize and deduplicate stop names
4. Calculate coordinates (from `stops.csv` or approximated)
5. Estimate distances and travel times
6. Build graph data structure

### `load_graph.py`

Loads the processed graph data into Neo4j.

**Usage:**

```bash
python load_graph.py
```

**What it does:**

1. Connects to Neo4j using credentials from `.env.local`
2. Clears existing graph (optional - can be modified)
3. Creates nodes:
   - `BusStop` - Individual stops with name, coordinates, zone
   - `Route` - Bus routes identified by route number
   - `Landmark` (optional) - Places of interest
   - `Zone` - Geographic areas
4. Creates relationships:
   - `SERVES` - Route serves stop
   - `NEXT_STOP` - Stop ordering within a route
   - `NEAR` - Stop near landmark
   - `IN_ZONE` - Stop in zone

**Database Schema:**

```cypher
// BusStop nodes
CREATE (s:BusStop {
    id: "stop_123",
    name: "Bus Stand",
    lat: 12.8698,
    lng: 74.8426,
    zone: "City Centre",
    is_hub: true
})

// Route nodes
CREATE (r:Route {
    route_id: "route_001",
    route_no: "1",
    name: "City Loop",
    source_file: "bus-data.csv"
})

// NEXT_STOP relationships
CREATE (s1:BusStop)-[rel:NEXT_STOP {
    route_id: "route_001",
    route_no: "1",
    distance_km: 0.5,
    time_min: 2.0,
    weight_distance: 0.5,
    weight_time: 2.0
}]->(s2:BusStop)
```

### `load_simple.py`

Alternative lightweight loader for testing (if present).

## CSV Directory

### `bus-data.csv` & `bus-data-old.csv`

Raw route data files. Each row represents a complete bus route.

**Expected Format:**

```csv
id,busNumber,description,stops
1,1,City Loop,"Bus Stand,Balmatta,Bejai,Car Street,..."
2,2,Industrial Route,"Baikampady,Industrial Estate,..."
```

**Fields:**

- `id` - Unique route identifier
- `busNumber` - Public route number
- `description` - Route name/description
- `stops` - Comma-separated list of stops in order

**Notes:**

- Currently loads only ONE CSV at a time (defined as `PRIMARY_ROUTE_CSV` in `csv_graph_data.py`)
- This avoids mixing different network versions
- To switch CSV, update `PRIMARY_ROUTE_CSV` variable

## Stop Name Normalization

The system handles common variations in stop names via `STOP_ALIASES`:

```python
STOP_ALIASES = {
    "alake": "Alake",
    "ashoknagar": "Ashoknagar",
    "baikampady": "Baikampady",
    # ... hundreds more
}
```

**Why needed:**

- Input data is inconsistent (spaces, capitalization, abbreviations)
- Public data sources use different naming conventions
- User input might not match exactly

**How it works:**

1. Stop names are lowercased and deduplicated
2. Looked up in STOP_ALIASES
3. If found, replaced with canonical name
4. If not found, used as-is

**Adding aliases:**

```python
# In csv_graph_data.py
STOP_ALIASES = {
    # ... existing entries ...
    "myalias": "Canonical Stop Name",
}
```

## Zone Assignment

Stops are assigned to zones based on:

1. Explicit zone in `data/stops.csv` (if provided)
2. Geographic proximity to known zone coordinates
3. Default zone (e.g., "Other")

## Development & Testing

### Run Data Processing

```bash
python csv_graph_data.py
```

This validates the data structure without touching the database.

### Inspect Processed Data

```python
from csv_graph_data import build_graph_dataset

graph = build_graph_dataset()
print(f"Routes: {len(graph['routes'])}")
print(f"Stops: {len(graph['stops'])}")
print(f"Edges: {len(graph['edges'])}")

# Inspect a route
route = graph['routes'][0]
print(f"Route {route['route_no']}: {route['name']}")
print(f"Stops: {route['stops']}")
```

### Load to Database

```bash
# After validation
python load_graph.py
```

Then query in Neo4j Browser:

```cypher
MATCH (s:BusStop) RETURN COUNT(s) AS total_stops
MATCH (r:Route) RETURN COUNT(r) AS total_routes
MATCH ()-[e:NEXT_STOP]-() RETURN COUNT(e) AS total_connections
```

## Common Issues

### Stop Name Mismatches

**Error:** Route has 20 stops but only 15 found in database

**Solution:**
1. Check for typos in CSV
2. Add missing stops to `data/stops.csv`
3. Add aliases to `STOP_ALIASES` in `csv_graph_data.py`
4. Reload graph: `python load_graph.py`

### Coordinate Issues

**Error:** Stops appear in wrong location on map

**Solution:**
1. Verify coordinates in `data/stops.csv`
2. Check for lat/lng swap (should be lat first)
3. Ensure WGS84 format (not other projections)

### Duplicate Stops

**Error:** Same stop appears multiple times with different IDs

**Solution:**
1. Check stop name aliases
2. Ensure CSV uses consistent stop names
3. Run deduplication: `python csv_graph_data.py --deduplicate`

## Adding New Data

To add a new route CSV:

1. Ensure format matches `bus-data.csv`
2. Create new file in `csv/` directory
3. Add to `CSV_FILES` list in `csv_graph_data.py`
4. Validate with `build_graph_dataset()`
5. Load to database: `python load_graph.py`

**Important:** Currently loads only `PRIMARY_ROUTE_CSV`. To load multiple datasets, modify the loader logic.

## Performance Tips

- Stop name lookups use in-memory dictionaries (fast)
- Stop coordinates are calculated once and cached
- Distance calculations use haversine (efficient) or pre-computed (fastest)
- Index stops by ID and name in Neo4j for query performance

## Related Files

- `config.py` - Database configuration
- `data/stops.csv` - Stop coordinates and metadata
- `data/stop_distances.csv` - Enrichment distances
- `Neo4j/backend/app.py` - Query API that uses this data
