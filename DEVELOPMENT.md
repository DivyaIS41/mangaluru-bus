# Development Guide

This guide helps you set up a development environment and contribute to the Mangaluru Bus Navigator project.

## Prerequisites

- Python 3.8 or higher
- Neo4j 4.x or 5.x (running locally or accessible via network)
- Git

## Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/mangaluru-bus.git
cd mangaluru-bus
```

### 2. Create a Python Virtual Environment

```bash
# On Windows
python -m venv venv
venv\Scripts\activate

# On macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

If `requirements.txt` doesn't exist, install manually:

```bash
pip install Flask Flask-CORS neo4j python-dotenv
```

### 4. Configure Environment Variables

Copy the example configuration:

```bash
cp .env.example .env.local
```

Then edit `.env.local` with your Neo4j credentials:

```env
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_actual_password
```

**Important:** `.env.local` is ignored by Git and should never be committed.

### 5. Set Up Neo4j Database

#### Option A: Local Neo4j Installation

1. Download and install Neo4j Desktop from [neo4j.com/download](https://neo4j.com/download)
2. Create a new project and start a database instance
3. Set the password and update `.env.local`

#### Option B: Docker

```bash
docker run -d \
  --name neo4j \
  --publish=7687:7687 \
  --env NEO4J_AUTH=neo4j/password \
  neo4j:latest
```

Update `.env.local` with `bolt://localhost:7687` and your password.

### 6. Load Initial Data

```bash
python dataset/load_graph.py
```

This will:
- Parse the CSV bus data
- Create graph nodes and relationships in Neo4j
- Index stops for fast lookup

### 7. Run the Flask Backend

```bash
cd Neo4j/backend
python app.py
```

The API should be available at `http://localhost:5000`

### 8. Access the Frontend

Open your browser to `http://localhost:5000` to see the interactive map.

## Project Architecture

### Database Layer (`dataset/`)
- Loads CSV data and transforms it into a graph structure
- Creates Neo4j nodes (BusStop, Route, Landmark, Zone) and relationships
- Handles coordinate normalization and distance calculations

### Backend (`Neo4j/backend/`)
- Flask API that queries the Neo4j database
- Implements pathfinding algorithms (Dijkstra for shortest routes)
- Exposes endpoints for stop lookup, route search, and transit findings

### Frontend (`frontend/`)
- Leaflet-based interactive map
- Displays bus stops, routes, and computed paths
- Allows users to select stops and compute optimal routes

## Common Development Tasks

### Running Tests

```bash
# If you have pytest configured
pytest tests/
```

### Database Cleanup

To clear the database and reload:

```bash
python -c "
from neo4j import GraphDatabase
from config import get_neo4j_config

config = get_neo4j_config()
driver = GraphDatabase.driver(config['uri'], auth=(config['user'], config['password']))

with driver.session() as session:
    session.run('MATCH (n) DETACH DELETE n')
    print('Database cleared')
"

# Then reload
python dataset/load_graph.py
```

### Debugging the Backend

Add debug logging to `Neo4j/backend/app.py`:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

Or run Flask with verbose mode:

```bash
FLASK_ENV=development FLASK_DEBUG=1 python Neo4j/backend/app.py
```

### Viewing Neo4j Browser

Open your browser to:
- Local instance: `http://localhost:7474/browser/` (or port 7474 if different)
- Enter credentials and run Cypher queries directly

Example query to inspect stops:

```cypher
MATCH (s:BusStop) 
RETURN s.name, s.lat, s.lng 
LIMIT 10
```

## Code Style

- Follow PEP 8 for Python code
- Use type hints where practical
- Comment complex algorithms and business logic
- Keep functions small and focused

## Before Submitting a Pull Request

1. Ensure no `.env.local` or secrets are committed
2. Test with a fresh environment
3. Update documentation if you've changed behavior
4. Run data verification to ensure graph integrity

Example verification:

```bash
python -c "
from dataset.csv_graph_data import build_graph_dataset
graph_data = build_graph_dataset()
print(f'Routes: {len(graph_data[\"routes\"])}')
print(f'Stops: {len(graph_data[\"stops\"])}')
"
```

## Troubleshooting

### "Connection refused" Neo4j error

- Check if Neo4j is running
- Verify `NEO4J_URI` matches your instance
- Ensure correct port (default 7687 for Bolt)

### "Import error: No module named 'config'"

- Ensure you're running from the project root
- Verify path insertion in files: `sys.path.insert(0, str(PROJECT_ROOT))`

### Flask app not loading static files

- Check `static_folder` path in `Neo4j/backend/app.py`
- Verify `frontend/static/` exists with CSS and JS files

## Resources

- [Flask Documentation](https://flask.palletsprojects.com/)
- [Neo4j Python Driver](https://neo4j.com/docs/python-manual/current/)
- [Cypher Query Language](https://neo4j.com/docs/cypher-manual/current/)
- [Leaflet.js Documentation](https://leafletjs.com/reference.html)

## Questions or Issues?

Please open an issue on GitHub or contact the maintainers.
