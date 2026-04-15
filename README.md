# Mangaluru Bus Navigator

[![Security Checks](https://github.com/yourusername/mangaluru-bus/workflows/Security%20Checks/badge.svg)](https://github.com/yourusername/mangaluru-bus/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.8+](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)

A smart graph-based bus route explorer for Mangaluru city built with **Flask**, **Neo4j**, and **Leaflet**. Find optimal bus routes, explore stops on an interactive map, and discover transit patterns using powerful graph algorithms.

## ✨ Features

- 🗺️ **Interactive Map** - Explore bus stops and routes on OpenStreetMap
- 🔍 **Smart Search** - Find stops and routes by name instantly
- 🚌 **Multi-Route Paths** - Discover optimal routes with transfers
- 📊 **Route Optimization** - Compare paths by distance or travel time
- 🎯 **Direct Routes** - Find single-bus connections between stops
- 🌐 **REST API** - Programmatic access to all features
- 📱 **Responsive Design** - Works on desktop and mobile

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- Neo4j 4.x or 5.x
- Git

### Installation

1. **Clone repository**
   ```bash
   git clone https://github.com/yourusername/mangaluru-bus.git
   cd mangaluru-bus
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**
   ```bash
   cp .env.example .env.local
   # Edit .env.local with your Neo4j credentials
   ```

5. **Load data**
   ```bash
   python dataset/load_graph.py
   ```

6. **Run application**
   ```bash
   cd Neo4j/backend
   python app.py
   ```

7. **Open browser**
   - Navigate to `http://localhost:5000`

## 📚 Documentation

- **[Development Guide](DEVELOPMENT.md)** - Setup, debugging, and development workflow
- **[Contributing Guide](CONTRIBUTING.md)** - How to contribute to the project
- **[Backend API](Neo4j/backend/README.md)** - REST API endpoints and usage
- **[Frontend](frontend/README.md)** - Web UI and JavaScript guide
- **[Dataset Processing](dataset/README.md)** - Data loading and graph building
- **[Data Files](data/README.md)** - CSV format and enrichment data

## 🏗️ Architecture

### Three-Tier Design

```
┌─────────────────────────────────────┐
│  Frontend (Leaflet.js + HTML)       │  Interactive map interface
├─────────────────────────────────────┤
│  Backend (Flask + Python)           │  REST API & pathfinding
├─────────────────────────────────────┤
│  Database (Neo4j Graph)             │  Bus network graph
└─────────────────────────────────────┘
```

### Key Components

| Component | Purpose | Location |
|-----------|---------|----------|
| **Data Processing** | Parse CSV → Graph transformation | `dataset/` |
| **Graph Database** | Store bus network as graph | Neo4j instance |
| **Backend API** | Query database & compute paths | `Neo4j/backend/app.py` |
| **Web UI** | Interactive map interface | `frontend/templates/index.html` |

## 🗄️ Graph Schema

The project models the bus network as a property graph:

```
BusStop (Node)
├── id: Stop identifier
├── name: Stop name
├── lat: Latitude
├── lng: Longitude
├── zone: Geographic zone
└── is_hub: Major interchange point?

Route (Node)
├── route_id: Route identifier
├── route_no: Public route number
├── name: Route description
└── stops: All stops on this route

Relationships:
├── SERVES: Route ---[SERVES]---> BusStop
├── NEXT_STOP: BusStop ---[NEXT_STOP]---> BusStop
├── IN_ZONE: BusStop ---[IN_ZONE]---> Zone
└── NEAR: BusStop ---[NEAR]---> Landmark
```

### Why Neo4j?

- **Natural Representation** - Bus routes are inherently graph-structured
- **Path Queries** - Built-in support for route finding (Cypher)
- **Performance** - Fast traversal of nested relationships
- **Flexibility** - Easy to add new stop types or relationships

## 📦 Data Sources

### Primary Data

- **CSV Route Files** - `dataset/csv/bus-data.csv` - Bus routes with stop sequences
- **Canonical Source** - Currently loads `bus-data-old.csv` (prevents version mixing)

### Enrichment Files

- **Stop Metadata** - `data/stops.csv` - Coordinates, zones, hub status
- **Distance Data** - `data/stop_distances.csv` - Pre-calculated distances (optional)

### Data Format

**Route CSV Structure:**
```csv
id,busNumber,description,stops
1,1,City Loop,"Bus Stand,Balmatta,Car Street,..."
```

**Stops CSV Structure:**
```csv
stop_name,lat,lng,zone,is_hub
Bus Stand,12.8698,74.8426,City Centre,TRUE
Balmatta,12.8713,74.8397,City Centre,FALSE
```

See [data/README.md](data/README.md) for detailed formats.

## 🔌 API Endpoints

All endpoints return JSON. See [Backend README](Neo4j/backend/README.md) for full documentation.

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/stops` | GET | Search stops |
| `/api/routes` | GET | List/search routes |
| `/api/direct-routes` | GET | Single-bus connections |
| `/api/paths` | GET | Optimal multi-route paths |

### Example: Find Route Between Stops

```bash
curl "http://localhost:5000/api/paths?from_id=stop_123&to_id=stop_456&weight_field=weight_distance"
```

Response:
```json
[
  {
    "path": [
      {"id": "stop_123", "name": "Bus Stand", "lat": 12.8698, "lng": 74.8426},
      {"id": "stop_456", "name": "Balmatta", "lat": 12.8713, "lng": 74.8397}
    ],
    "route_segments": [{"route_no": "1", "from_stop": "Bus Stand", "to_stop": "Balmatta"}],
    "total_distance_km": 0.5,
    "total_time_min": 2.0
  }
]
```

## 🔒 Security & Privacy

✅ **No Hardcoded Secrets** - All credentials use environment variables
✅ **Configuration Management** - `.env.local` template with examples
✅ **.gitignore Configured** - Prevents accidental secret leaks
✅ **Public Data Only** - No personal information stored
✅ **CI/CD Checks** - GitHub Actions verify no secrets are committed

### Safe for Public GitHub
- Environment variables in `.env.local` (git-ignored)
- Example config in `.env.example`
- No API keys or passwords in code
- Automated security scanning

See [CONTRIBUTING.md](CONTRIBUTING.md#security-guidelines) for security best practices.

## 🛠️ Tech Stack

| Layer | Technology | Version |
|-------|-----------|---------|
| Database | Neo4j | 4.x - 5.x |
| Backend | Flask | 2.3+ |
| Backend | Python | 3.8+ |
| Frontend | Leaflet.js | 1.9+ |
| Maps | OpenStreetMap | Latest |
| API | REST | JSON |

## 📊 Project Structure

```
mangaluru-bus/
├── README.md                    # This file
├── LICENSE                      # MIT License
├── DEVELOPMENT.md               # Development setup guide
├── CONTRIBUTING.md              # Contribution guidelines
├── requirements.txt             # Python dependencies
├── config.py                    # Shared configuration
├── .env.example                 # Environment variable template
├── .gitignore                   # Git ignore rules
│
├── data/                        # Data enrichment
│   ├── README.md
│   ├── stops.csv                # Stop coordinates & metadata
│   └── stop_distances.csv       # Optional distance data
│
├── dataset/                     # Data processing pipeline
│   ├── README.md
│   ├── csv_graph_data.py        # CSV → Graph transformation
│   ├── load_graph.py            # Graph → Neo4j loader
│   ├── load_simple.py           # Alternative loader
│   └── csv/
│       ├── bus-data.csv         # Route data
│       └── bus-data-old.csv     # Previous version
│
├── Neo4j/backend/               # Flask API server
│   ├── README.md
│   └── app.py                   # Flask application
│
├── frontend/                    # Web UI
│   ├── README.md
│   └── templates/
│       └── index.html           # Interactive map
│
└── .github/workflows/           # CI/CD
    └── security-check.yml       # Automated checks
```

## 🔄 How It Works

### 1. Data Pipeline
```
CSV Files → Parse → Normalize → Calculate Distances → Build Graph
```

### 2. Graph Loading
```
Graph Data → Neo4j Driver → Create Nodes → Create Relationships
```

### 3. API Workflow
```
User Request → Flask Route → Run Cypher Query → Return JSON
```

### 4. Frontend Flow
```
Map Loaded → User Searches → Fetch API → Display Results
```

## 📖 Examples

### Search for a Stop

```python
import requests

response = requests.get('http://localhost:5000/api/stops?q=balmatta')
stops = response.json()
for stop in stops:
    print(f"{stop['name']} ({stop['id']})")
```

### Find Optimal Route

```python
response = requests.get(
    'http://localhost:5000/api/paths',
    params={
        'from_id': 'stop_1',
        'to_id': 'stop_42',
        'weight_field': 'weight_distance'
    }
)
paths = response.json()
best_path = paths[0]  # Shortest by distance
print(f"Route: {' → '.join([s['name'] for s in best_path['path']])}")
```

### Query Directly in Neo4j

```cypher
// Find all routes through a specific stop
MATCH (r:Route)-[:SERVES]->(s:BusStop {name: 'Bus Stand'})
RETURN r.route_no, r.name, r.stops
LIMIT 5
```

## 🎯 Future Enhancements

- [ ] Real-time bus tracking
- [ ] Estimated arrival times  
- [ ] Fare calculation
- [ ] Accessibility information
- [ ] Trip planning with alerts
- [ ] Mobile app (React Native)
- [ ] Crowding prediction

## 🐛 Troubleshooting

### Common Issues

**"Connection refused" from Neo4j**
- Check Neo4j is running: `neo4j status`
- Verify credentials in `.env.local`
- Check port 7687 is accessible

**Map not loading**
- Clear browser cache (Ctrl+Shift+Delete)
- Check Flask backend is running
- Open browser console (F12) for errors

**No stops appearing**
- Verify data loaded: `python dataset/load_graph.py`
- Check stops in Neo4j Browser: `MATCH (s:BusStop) RETURN COUNT(s)`

For more help, see [DEVELOPMENT.md](DEVELOPMENT.md#troubleshooting).

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

Quick checklist:
- [ ] Fork the repository
- [ ] Create feature branch (`git checkout -b feature/my-feature`)
- [ ] Make changes and test locally
- [ ] Ensure no `.env.local` secrets are committed
- [ ] Submit pull request with clear description

## 📄 License

This project is licensed under the [MIT License](LICENSE) - see LICENSE file for details.

## 👥 Contributors

<!-- Add your name here when contributing -->
- Project created as a Sem 6 Big Data project

## 📞 Support

- 📖 [Read the docs](DEVELOPMENT.md)
- 🐛 [Report issues](https://github.com/yourusername/mangaluru-bus/issues)
- 💬 [Discussions](https://github.com/yourusername/mangaluru-bus/discussions)

## 🎓 Educational Value

This project demonstrates:

- **Graph Databases** - Neo4j concepts and Cypher queries
- **Backend Development** - Flask REST APIs
- **Data Processing** - CSV parsing and transformation
- **Frontend Skills** - Leaflet.js and interactive maps
- **Algorithm** - Dijkstra's pathfinding
- **Full Stack** - End-to-end development

Perfect for learning Big Data and graph technologies!

---

**Note:** Replace `yourusername` in URLs with your actual GitHub username before pushing.

Made with ❤️ for Mangaluru's transit community

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

### 2. Create local config

Copy the example config and create a local-only file:

```bash
copy .env.example .env.local
```

Then edit `.env.local` and add your actual Neo4j password.

Example:

```text
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_password_here
```

Important:

- `.env.local` is ignored by git
- never commit your real password
- `.env.example` is safe to publish because it contains placeholders only

### 3. Start Neo4j

Make sure Neo4j Desktop is running and your database instance is started.

The project reads Neo4j connection details from:

- environment variables, or
- `.env.local` at the project root

If both exist, environment variables take priority.

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

### App does not connect to Neo4j

Check that:

- Neo4j Desktop is running
- the database instance is started
- `.env.local` contains the correct password
- the connection URI matches your local Neo4j instance

Sample `.env.local`:

```text
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_password_here
```

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

## Summary

This project demonstrates how a public transport network can be represented as a graph and queried for useful travel insights. Neo4j handles the structural network model, Flask exposes the graph through APIs, and Leaflet presents the results visually on a map.

With better stop-coordinate and edge-distance datasets, the same architecture can support much more accurate real-world route planning.
