# Data Directory

This directory contains CSV files that provide enrichment data for the bus network.

## Files

### `stops.csv`

Provides real coordinates and metadata for bus stops.

**Format:**
```csv
stop_name,lat,lng,zone,is_hub
State Bank,12.8698,74.8426,City Centre,TRUE
Lalbagh,12.8713,74.8397,City Centre,FALSE
```

**Fields:**
- `stop_name` (string): Name of the bus stop
- `lat` (float): Latitude coordinate (WGS84)
- `lng` (float): Longitude coordinate (WGS84)
- `zone` (string): Administrative zone or area
- `is_hub` (boolean): TRUE if this is a major transit hub

**Usage:**
- Loaded by `dataset/csv_graph_data.py` to enhance BusStop nodes
- Provides accurate coordinates for map display
- Used to categorize stops into zones

### `stop_distances.csv`

Provides pre-calculated distances between specific stop pairs (optional).

**Format:**
```csv
from_stop,to_stop,distance_km,time_min
Bus Stand,Balmatta,2.5,8
Balmatta,Kadri,1.8,6
```

**Fields:**
- `from_stop` (string): Starting stop name
- `to_stop` (string): Destination stop name
- `distance_km` (float): Road distance in kilometers
- `time_min` (float): Estimated travel time in minutes

**Usage:**
- Optional enrichment for more accurate routing
- Overrides haversine distance calculations if present
- Used to generate realistic transit times considering traffic patterns

## Creating/Updating Data Files

### For stop_name Matching

Stop names must match those in the route CSV files. Common variations are handled via `STOP_ALIASES` in `csv_graph_data.py`, but exact matches are preferred.

### Coordinate Sources

Coordinates can be obtained from:
- Google Maps / Google My Business
- OpenStreetMap
- GPS survey data
- Official transport authority records

**Format Notes:**
- Use WGS84 (EPSG:4326) coordinates
- Latitude: -90 to 90
- Longitude: -180 to 180
- Use decimal degrees (e.g., 12.8698, not 12°52'11")

### Data Validation

Before committing updates:

```python
# Validate CSV format
import csv

with open('stops.csv', 'r') as f:
    reader = csv.DictReader(f)
    for row in reader:
        assert -90 <= float(row['lat']) <= 90, f"Invalid lat: {row['lat']}"
        assert -180 <= float(row['lng']) <= 180, f"Invalid lng: {row['lng']}"
        assert row['is_hub'].upper() in ['TRUE', 'FALSE'], f"Invalid hub: {row['is_hub']}"
```

## Privacy & Security

- These files contain no personal data
- Coordinates are public information (bus stops are public facilities)
- Safe to commit to version control
- No credentials or secrets should be stored here

## Adding New Data Sources

If you have additional enrichment data:

1. Document the format and source
2. Add validation to loading code
3. Update this README
4. Create a feature branch for review

## Related Files

- `dataset/csv_graph_data.py` - Loading and transformation logic
- `dataset/csv/bus-data.csv` - Main route data
- `dataset/load_graph.py` - Database loading script
