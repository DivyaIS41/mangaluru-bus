# Flask Backend API

This directory contains the Flask API server that powers the Mangaluru Bus Navigator frontend.

## Overview

The backend provides RESTful endpoints for:

- Finding bus stops by name or location
- Searching for routes between two stops
- Computing optimal paths using pathfinding algorithms
- Retrieving route and zone information

## Architecture

```
app.py
├── Neo4j Database Connection
├── Route Graphs (in-memory caches)
├── Pathfinding Engine (Dijkstra)
└── REST API Endpoints
    ├── /api/stops
    ├── /api/routes
    ├── /api/paths
    └── / (HTML Frontend)
```

## Getting Started

### 1. Install Dependencies

```bash
pip install Flask Flask-CORS neo4j
```

### 2. Configure Database

Create `.env.local` in project root:

```env
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_password
```

### 3. Load Data

```bash
cd dataset
python load_graph.py
cd ..
```

### 4. Run Server

```bash
cd Neo4j/backend
python app.py
```

The server will start at `http://localhost:5000`

## API Endpoints

### `GET /api/stops`

Get all bus stops or search for specific stops.

**Query Parameters:**

- `q` (optional) - Search query (stop name substring)
- `limit` (optional) - Maximum results (default: 50)

**Response:**

```json
[
  {
    "id": "stop_123",
    "name": "Bus Stand",
    "lat": 12.8698,
    "lng": 74.8426,
    "zone": "City Centre",
    "is_hub": true
  }
]
```

**Examples:**

```bash
# Get all stops
curl http://localhost:5000/api/stops

# Search for stops
curl http://localhost:5000/api/stops?q=balmatta

# Limit results
curl http://localhost:5000/api/stops?q=station&limit=10
```

### `GET /api/routes`

Get bus routes or search for routes.

**Query Parameters:**

- `q` (optional) - Search query (route number or name)
- `stop_id` (optional) - Filter routes serving a specific stop

**Response:**

```json
[
  {
    "route_id": "route_001",
    "route_no": "1",
    "name": "City Loop",
    "stops": ["Bus Stand", "Balmatta", "Car Street", ...],
    "source_file": "bus-data.csv"
  }
]
```

**Examples:**

```bash
# Get all routes
curl http://localhost:5000/api/routes

# Search routes
curl http://localhost:5000/api/routes?q=1

# Routes serving a specific stop
curl http://localhost:5000/api/routes?stop_id=stop_123
```

### `GET /api/direct-routes`

Find direct routes between two stops (same bus route).

**Query Parameters:**

- `from_id` (required) - Starting stop ID
- `to_id` (required) - Destination stop ID

**Response:**

```json
{
  "from_stop": "Bus Stand",
  "to_stop": "Balmatta",
  "routes": [
    {
      "route_no": "1",
      "name": "City Loop",
      "stops": ["Bus Stand", "...", "Balmatta"],
      "stop_count": 5
    }
  ]
}
```

**Example:**

```bash
curl http://localhost:5000/api/direct-routes?from_id=stop_123&to_id=stop_456
```

### `GET /api/paths`

Compute optimal paths between two stops using various criteria.

**Query Parameters:**

- `from_id` (required) - Starting stop ID
- `to_id` (required) - Destination stop ID
- `weight_field` (optional) - `weight_distance` or `weight_time` (default: `weight_distance`)

**Response:**

```json
[
  {
    "path": [
      {
        "id": "stop_123",
        "name": "Bus Stand",
        "lat": 12.8698,
        "lng": 74.8426,
        "arrival_time": 0.0
      },
      {
        "id": "stop_456",
        "name": "Balmatta",
        "lat": 12.8713,
        "lng": 74.8397,
        "arrival_time": 2.0
      }
    ],
    "route_segments": [
      {
        "route_no": "1",
        "from_stop": "Bus Stand",
        "to_stop": "Balmatta"
      }
    ],
    "total_distance_km": 0.5,
    "total_time_min": 2.0,
    "distance_rank": 1,
    "time_rank": 1
  }
]
```

**Examples:**

```bash
# Shortest distance path
curl http://localhost:5000/api/paths?from_id=stop_123&to_id=stop_456&weight_field=weight_distance

# Shortest time path
curl http://localhost:5000/api/paths?from_id=stop_123&to_id=stop_456&weight_field=weight_time
```

## Core Functions

### `build_stop_lookup()`

Creates an in-memory dictionary mapping stop IDs to stop details for fast lookup.

```python
stops = build_stop_lookup()
print(stops["stop_123"])  # Returns stop details
```

### `load_route_graph(weight_field="weight_distance")`

Builds graph for pathfinding using specified weight metric.

- `weight_distance` - Uses distance in km
- `weight_time` - Uses estimated time in minutes

**Returns:** Adjacency list structure

```python
graph = load_route_graph("weight_distance")
# graph["stop_123"] = [
#     {"to_id": "stop_456", "distance_km": 0.5, "weight": 0.5},
#     ...
# ]
```

### `find_paths(from_id, to_id, weight_field, max_transfers=...)`

Computes all possible paths using Dijkstra's algorithm.

**Key Parameters:**

- `TRANSFER_PENALTY_*` - Extra cost when changing routes
- `DEFAULT_DWELL_TIME_*` - Time to wait/board at stops

**Returns:** List of path objects sorted by weight

## Configuration

### Neo4j Settings

```python
NEO4J_URI = "bolt://localhost:7687"  # Or your Neo4j instance
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "")
```

### Pathfinding Parameters

```python
TRANSFER_PENALTY_DISTANCE = 0.0       # Extra km when changing routes
TRANSFER_PENALTY_TIME = 8.0           # Extra minutes when changing routes
DEFAULT_DWELL_TIME_MIN = 1.5          # Avg wait/board time at stop
```

### Flask Settings

```python
app.config['JSON_SORT_KEYS'] = False
CORS(app)  # Enable CORS for frontend requests
```

## Debugging

### Enable Debug Logging

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Then run
python app.py
```

### Test Queries

```bash
# Check if backend is running
curl http://localhost:5000/

# Get all stops
curl http://localhost:5000/api/stops

# Query specific endpoint
curl http://localhost:5000/api/stops?q=bus%20stand
```

### Database Issues

In Python:

```python
from neo4j import GraphDatabase
from config import get_neo4j_config

config = get_neo4j_config()
driver = GraphDatabase.driver(config['uri'], auth=(config['user'], config['password']))

with driver.session() as session:
    result = session.run("MATCH (n:BusStop) RETURN COUNT(n)")
    print(f"Total stops: {result.single()[0]}")
```

## Performance Optimization

### Caching

Stops are cached at startup:

```python
STOP_LOOKUP = build_stop_lookup()
```

Routes are loaded per-request (can be cached if needed):

```python
# Consider caching for large graphs
ROUTE_GRAPH_DISTANCE = None
ROUTE_GRAPH_TIME = None

def get_route_graph(metric):
    global ROUTE_GRAPH_DISTANCE, ROUTE_GRAPH_TIME
    if metric == "weight_distance" and ROUTE_GRAPH_DISTANCE is None:
        ROUTE_GRAPH_DISTANCE = load_route_graph("weight_distance")
    # ...
```

### Query Optimization

Long paths use Dijkstra's algorithm (efficient for large graphs). For better performance:

- Index BusStop nodes by ID and name
- Monitor Neo4j query performance via browser
- Consider pre-computing common paths

## Deployment

### Production Considerations

1. **Environment Variables** - Use `.env.production` on server
2. **Error Handling** - Wrap routes with try-except
3. **CORS** - Restrict to specific domains
4. **Rate Limiting** - Implement to prevent abuse
5. **SSL/TLS** - Use HTTPS in production

Example production config:

```python
app.config['ENV'] = 'production'
app.config['DEBUG'] = False

# Restrict CORS
CORS(app, resources={
    r"/api/*": {"origins": ["https://yourdomain.com"]}
})
```

### Running with Gunicorn

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

## Troubleshooting

### Port Already in Use

```bash
# Find process using port 5000
lsof -i :5000

# Kill it
kill -9 <PID>

# Or run on different port
python app.py --port 8080
```

### Neo4j Connection Failed

1. Check Neo4j is running
2. Verify credentials in `.env.local`
3. Test connection: See Debugging section above

### Paths Not Found

1. Verify stops exist: `curl http://localhost:5000/api/stops`
2. Check database has routes: `curl http://localhost:5000/api/routes`
3. Increase `max_transfers` limit in pathfinding

## Related Files

- `config.py` - Shared configuration
- `frontend/templates/index.html` - Frontend consuming this API
- `dataset/load_graph.py` - Database setup
