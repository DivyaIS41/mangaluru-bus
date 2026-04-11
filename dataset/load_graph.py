"""
Loads the Mangaluru bus network into Neo4j from CSV-backed route data.
Now supports real distances and times.

Usage:
    python load_graph.py
"""

import math
import os
from neo4j import GraphDatabase
from csv_graph_data import build_graph_dataset

# Neo4j configuration
NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "")


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


def clear_db(session):
    """Clear all existing data from the database"""
    session.run("MATCH (n) DETACH DELETE n")
    print("  Cleared existing data.")


def create_constraints(session):
    """Create necessary constraints and indexes"""
    # Older versions of this project used a uniqueness constraint on route_no.
    # The CSV data contains legitimate duplicate route numbers with different paths,
    # so we drop that legacy constraint before creating the new route_id constraint.
    session.run("DROP CONSTRAINT route_no IF EXISTS")
    session.run("DROP CONSTRAINT route_route_no IF EXISTS")
    session.run("DROP INDEX route_no IF EXISTS")
    session.run("CREATE CONSTRAINT IF NOT EXISTS FOR (s:BusStop) REQUIRE s.id IS UNIQUE")
    session.run("CREATE CONSTRAINT IF NOT EXISTS FOR (r:Route) REQUIRE r.route_id IS UNIQUE")
    session.run("CREATE INDEX IF NOT EXISTS FOR (r:Route) ON (r.route_no)")
    session.run("CREATE INDEX IF NOT EXISTS FOR (s:BusStop) ON (s.name)")
    session.run("CREATE INDEX IF NOT EXISTS FOR (s:BusStop) ON (s.zone)")
    print("  Constraints and indexes created.")


def load_stops(session, stops):
    """Load bus stops into Neo4j"""
    for stop_id, name, lat, lng, zone, is_hub in stops:
        session.run(
            """
            MERGE (s:BusStop {id: $id})
            SET s.name = $name,
                s.lat = $lat,
                s.lng = $lng,
                s.zone = $zone,
                s.is_hub = $is_hub
            """,
            id=stop_id,
            name=name,
            lat=lat,
            lng=lng,
            zone=zone,
            is_hub=is_hub,
        )
    print(f"  Loaded {len(stops)} bus stops.")


def load_routes_and_edges(session, routes, edge_distances):
    """Load routes and create NEXT_STOP relationships with real distances"""
    for route in routes:
        # Create route node
        session.run(
            """
            MERGE (r:Route {route_id: $route_id})
            SET r.route_no = $route_no,
                r.name = $name,
                r.operator = $operator,
                r.source_file = $source_file
            """,
            route_id=route["route_id"],
            route_no=route["route_no"],
            name=route["name"],
            operator=route["operator"],
            source_file=route["source_file"],
        )

        stops = route["stops"]
        stop_names = route["stop_names"]

        # Create SERVES relationships
        for stop_id in stops:
            session.run(
                """
                MATCH (r:Route {route_id: $route_id})
                MATCH (s:BusStop {id: $stop_id})
                MERGE (r)-[:SERVES]->(s)
                """,
                route_id=route["route_id"],
                stop_id=stop_id,
            )

        # Create NEXT_STOP relationships with distances
        for idx in range(len(stops) - 1):
            from_id = stops[idx]
            to_id = stops[idx + 1]
            from_name = stop_names[idx]
            to_name = stop_names[idx + 1]
            
            # Get precomputed distance if available
            edge_key = (from_name, to_name)
            if edge_key in edge_distances:
                distance_km = edge_distances[edge_key]["distance_km"]
                time_min = edge_distances[edge_key]["time_min"]
            else:
                # Fallback to haversine (should not happen with proper data)
                # Get coordinates
                from_coords = session.run(
                    "MATCH (s:BusStop {id: $id}) RETURN s.lat AS lat, s.lng AS lng",
                    id=from_id
                ).single()
                to_coords = session.run(
                    "MATCH (s:BusStop {id: $id}) RETURN s.lat AS lat, s.lng AS lng",
                    id=to_id
                ).single()
                distance_km = haversine_km(
                    from_coords["lat"], from_coords["lng"],
                    to_coords["lat"], to_coords["lng"]
                )
                time_min = distance_km * 3.5
            
            session.run(
                """
                MATCH (a:BusStop {id: $from_id})
                MATCH (b:BusStop {id: $to_id})
                MERGE (a)-[rel:NEXT_STOP {route_id: $route_id, seq: $seq}]->(b)
                SET rel.route_no = $route_no,
                    rel.distance_km = $distance_km,
                    rel.time_min = $time_min,
                    rel.weight_distance = $weight_distance,
                    rel.weight_time = $weight_time
                """,
                from_id=from_id,
                to_id=to_id,
                route_id=route["route_id"],
                route_no=route["route_no"],
                seq=idx,
                distance_km=round(distance_km, 3),
                time_min=round(time_min, 1),
                weight_distance=round(distance_km, 3),
                weight_time=round(time_min, 1),
            )

    print(f"  Loaded {len(routes)} routes with weighted stop sequences.")


def load_landmarks(session, landmarks):
    """Load landmarks and connect them to nearby stops"""
    for name, stop_id, lm_type in landmarks:
        session.run(
            """
            MERGE (l:Landmark {name: $name})
            SET l.type = $type
            WITH l
            MATCH (s:BusStop {id: $stop_id})
            MERGE (l)-[:NEAR]->(s)
            """,
            name=name,
            type=lm_type,
            stop_id=stop_id,
        )
    print(f"  Loaded {len(landmarks)} landmarks.")


def load_zones(session, stops):
    """Create zone nodes and connect stops to them"""
    zones = set(stop[4] for stop in stops)
    for zone in zones:
        session.run("MERGE (:Zone {name: $name})", name=zone)

    for stop_id, _, _, _, zone, _ in stops:
        session.run(
            """
            MATCH (s:BusStop {id: $stop_id})
            MATCH (z:Zone {name: $zone})
            MERGE (s)-[:IN_ZONE]->(z)
            """,
            stop_id=stop_id,
            zone=zone,
        )
    print(f"  Loaded {len(zones)} zones.")


def create_reverse_edges(session):
    """Create reverse NEXT_STOP relationships for bidirectional traversal"""
    # Keep the graph traversable in both directions using the same relationship type.
    session.run(
        """
        MATCH (a)-[rel:NEXT_STOP]->(b)
        MERGE (b)-[rev:NEXT_STOP {route_id: rel.route_id, seq: rel.seq, reverse_of: true}]->(a)
        SET rev.route_no = rel.route_no,
            rev.distance_km = rel.distance_km,
            rev.time_min = rel.time_min,
            rev.weight_distance = rel.weight_distance,
            rev.weight_time = rel.weight_time
        """
    )
    print("  Created reverse NEXT_STOP relationships.")


def verify(session):
    """Verify the loaded data"""
    stops = session.run("MATCH (s:BusStop) RETURN count(s) AS c").single()["c"]
    routes = session.run("MATCH (r:Route) RETURN count(r) AS c").single()["c"]
    rels = session.run("MATCH ()-[r]->() RETURN count(r) AS c").single()["c"]
    edges = session.run("MATCH ()-[r:NEXT_STOP]->() RETURN count(r) AS c").single()["c"]
    
    print("\n  Verification:")
    print(f"    BusStop nodes      : {stops}")
    print(f"    Route nodes        : {routes}")
    print(f"    Total relationships: {rels}")
    print(f"    NEXT_STOP edges    : {edges}")
    
    # Sample some edges to verify distances
    sample = session.run(
        """
        MATCH (a)-[r:NEXT_STOP]->(b)
        RETURN a.name AS from_stop, b.name AS to_stop, 
               r.distance_km AS distance, r.time_min AS time
        LIMIT 5
        """
    )
    print("\n  Sample edges:")
    for record in sample:
        print(f"    {record['from_stop']} → {record['to_stop']}: {record['distance']} km, {record['time']} min")


def main():
    print("=" * 60)
    print("Mangaluru Bus Network Loader")
    print("=" * 60)
    
    print("\nPreparing CSV-backed graph dataset...")
    dataset = build_graph_dataset()
    print(f"\nDataset summary:")
    print(f"  - {len(dataset['stops'])} unique stops")
    print(f"  - {len(dataset['routes'])} routes")
    print(f"  - {len(dataset['edge_distances'])} unique stop pairs with distances")
    print(f"  - {len(dataset['landmarks'])} landmarks")

    print("\nConnecting to Neo4j...")
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))

    try:
        driver.verify_connectivity()
        print("  Connected successfully!")
    except Exception as exc:
        print(f"\n  ERROR: Could not connect to Neo4j.")
        print(f"  {exc}")
        print("\n  Make sure:")
        print("  1. Neo4j is running (neo4j start)")
        print("  2. The password in this file matches your Neo4j installation")
        print("  3. The database is accessible at bolt://localhost:7687")
        return

    with driver.session() as session:
        print("\nLoading graph data into Neo4j...")
        print("-" * 40)
        clear_db(session)
        create_constraints(session)
        load_stops(session, dataset["stops"])
        load_routes_and_edges(session, dataset["routes"], dataset["edge_distances"])
        load_landmarks(session, dataset["landmarks"])
        load_zones(session, dataset["stops"])
        create_reverse_edges(session)
        verify(session)

    driver.close()
    print("\n" + "=" * 60)
    print("SUCCESS! Graph data loaded into Neo4j")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Open Neo4j Browser: http://localhost:7474")
    print("2. Start the Flask app: python app.py")
    print("3. Open your browser at http://localhost:5000")
    print("\nExample Cypher queries to test:")
    print("  MATCH (s:BusStop) RETURN s LIMIT 10")
    print("  MATCH (r:Route)-[:SERVES]->(s) RETURN r.route_no, collect(s.name) LIMIT 5")
    print("  MATCH path = shortestPath((a:BusStop {name:'State Bank'})-[*]-(b:BusStop {name:'Kankanady'})) RETURN path")


if __name__ == "__main__":
    main()
