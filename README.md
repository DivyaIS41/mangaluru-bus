# Mangaluru Bus Navigator

A graph-based bus route exploration project built with `Flask`, `Neo4j`, and `Leaflet`.

The project models the Mangaluru bus network as a graph where bus stops are connected in route order. It lets users:

- browse bus stops on a map,
- inspect major hubs,
- find routes between two stops,
- compare route choices by distance, time, or transfers.

## What This Project Does

The application converts bus route CSV data into a Neo4j graph and exposes that graph through a Flask API. A Leaflet frontend consumes the API and renders stops, routes, and path results on an interactive map.

At a high level:

- `dataset/` prepares and loads graph data into Neo4j.
- `Neo4j/backend/` provides API endpoints for the frontend.
- `frontend/templates/` contains the map-based UI.

## Tech Stack

- `Python`
- `Flask`
- `Neo4j`
- `Cypher`
- `Leaflet`
- `OpenStreetMap`

## Project Structure

```text
mangaluru-bus/
|-- README.md
|-- data/
|   |-- stops.csv
|   |-- stop_distances.csv
|-- dataset/
|   |-- csv/
|   |   |-- bus-data.csv
|   |   |-- bus-data-old.csv
|   |-- csv_graph_data.py
|   |-- load_graph.py
|-- Neo4j/
|   |-- backend/
|   |   |-- app.py
|-- frontend/
|   |-- templates/
|   |   |-- index.html
```

## How Neo4j Is Used

Neo4j is the core graph database in this project.

The bus network is stored using:

- `(:BusStop)` nodes for bus stops
- `(:Route)` nodes for bus routes
- `(:Route)-[:SERVES]->(:BusStop)` relationships to show which stops belong to a route
- `(:BusStop)-[:NEXT_STOP]->(:BusStop)` relationships to show stop-to-stop travel order
- `(:Landmark)-[:NEAR]->(:BusStop)` relationships for nearby places
- `(:BusStop)-[:IN_ZONE]->(:Zone)` relationships for zone grouping

This graph structure makes route traversal much more natural than storing the network only in tabular form.

## Data Sources

The current system uses these route-sequence CSV files:

- `dataset/csv/bus-data.csv`
- `dataset/csv/bus-data-old.csv`

These files contain:

- `id`
- `busNumber`
- `description`
- `stops`

The optional enrichment files are:

- `data/stops.csv`
- `data/stop_distances.csv`

### `stops.csv`

This file provides real stop coordinates and optional metadata.

Expected format:

```csv
stop_name,lat,lng,zone,is_hub
State Bank,12.8698,74.8426,City Centre,TRUE
Lalbagh,12.8713,74.8397,City Centre,FALSE
```

### `stop_distances.csv`

This file provides stop-to-stop road distance and travel time.

Expected format:

```csv
from_stop,to_stop,distance_km,time_min
State Bank,Lalbagh,1.2,4
Lalbagh,Ashoknagar,2.1,6
```

If these enrichment files are missing, the project falls back to:

- inferred or interpolated stop coordinates,
- straight-line haversine distance,
- estimated time based on distance.

## Current Route Optimization Modes

The backend supports multiple route-finding strategies:

- `distance`
  Uses weighted search based on `distance_km`
- `time`
  Uses weighted search based on `time_min`
- `transfers`
  Prefers the route with the fewest transfers

The API endpoint is:

```text
/api/find-path?from_id=<STOP_ID>&to_id=<STOP_ID>&optimize_by=distance
```

Examples:

```text
/api/find-path?from_id=S001&to_id=S050&optimize_by=distance
/api/find-path?from_id=S001&to_id=S050&optimize_by=time
/api/find-path?from_id=S001&to_id=S050&optimize_by=transfers
```

## Setup

### 1. Install Python dependencies

```bash
pip install flask flask-cors neo4j
```

### 2. Start Neo4j

Make sure Neo4j Desktop is running and your database instance is started.

The default connection used in the code is:

```text
bolt://localhost:7687
username: neo4j
password: set via environment variable
```

Set credentials before running the loader or backend:

```bash
set NEO4J_URI=bolt://localhost:7687
set NEO4J_USER=neo4j
set NEO4J_PASSWORD=your_password_here
```

## Load the Graph Data

From the project dataset folder:

```bash
cd mangaluru-bus/dataset
python load_graph.py
```

This script:

- reads route CSV data,
- normalizes stop names,
- creates stop and route nodes,
- creates `SERVES` and `NEXT_STOP` relationships,
- adds weighted distance and time fields,
- loads zones and landmarks into Neo4j.

## Run the Backend

From the backend folder:

```bash
cd mangaluru-bus/Neo4j/backend
python app.py
```

The Flask app starts on:

```text
http://localhost:5000
```

## Main API Endpoints

- `/`
  Frontend page
- `/api/stops`
  Returns all bus stops
- `/api/routes`
  Returns routes with their stops
- `/api/find-path`
  Finds an optimized path between two stops
- `/api/hubs`
  Returns top hub stops by route count
- `/api/reachable`
  Returns stops reachable within a number of hops
- `/api/landmarks`
  Returns landmarks and nearest stops
- `/api/routes-through/<stop_id>`
  Returns routes passing through a stop

## How the Data Pipeline Works

1. Route CSV files are read by `dataset/csv_graph_data.py`.
2. Stop names are normalized using alias mappings.
3. Stop metadata is built from real coordinate data if available.
4. Missing coordinates are interpolated or approximated.
5. Edge distance and time values are loaded from `stop_distances.csv` if available.
6. `dataset/load_graph.py` pushes the final graph into Neo4j.
7. `Neo4j/backend/app.py` queries Neo4j and performs route optimization.
8. `frontend/templates/index.html` renders the results on a map.

## Known Limitations

- The route CSVs only contain stop order, not actual map geometry.
- Without `stops.csv`, some map marker positions are approximated.
- Without `stop_distances.csv`, distance and time are estimated.
- Drawn route polylines connect stop markers directly and do not follow real roads.

Because of that, the graph logic can still work, but map accuracy depends heavily on the quality of the additional stop and edge datasets.

## Recommended Next Improvements

- Add complete `stops.csv` coverage for all stops
- Add accurate `stop_distances.csv` data for consecutive stop pairs
- Add route shape/polyline data for road-accurate drawing
- Add a frontend selector for optimization mode
- Add tests for data normalization and pathfinding

## Troubleshooting

### Constraint error on `Route.route_no`

If Neo4j throws an error about duplicate `route_no`, it means an older uniqueness constraint still exists.

Check constraints in Neo4j:

```cypher
SHOW CONSTRAINTS;
```

Drop the old route number constraint if needed:

```cypher
DROP CONSTRAINT route_no IF EXISTS;
DROP CONSTRAINT route_route_no IF EXISTS;
```

Then reload the graph with:

```bash
python load_graph.py
```

### Import error for `mangaluru_bus_data`

If VS Code reports:

```text
Import "mangaluru_bus_data" could not be resolved
```

make sure you are opening and running the current project files, not older copies from another directory such as `Downloads`.

## Summary

This project demonstrates how a public transport network can be represented as a graph and queried for useful travel insights. Neo4j handles the structural network model, Flask exposes the graph through APIs, and Leaflet presents the results visually on a map.

With better stop-coordinate and edge-distance datasets, the same architecture can support much more accurate real-world route planning.
