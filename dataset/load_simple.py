"""
Simple loader for Mangaluru bus network
"""

import sys
import math
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from neo4j import GraphDatabase
from config import get_neo4j_config
from csv_graph_data import build_graph_dataset

NEO4J_CONFIG = get_neo4j_config()
NEO4J_URI = NEO4J_CONFIG["uri"]
NEO4J_USER = NEO4J_CONFIG["user"]
NEO4J_PASSWORD = NEO4J_CONFIG["password"]

def haversine_km(lat1, lng1, lat2, lng2):
    radius = 6371.0
    d_lat = math.radians(lat2 - lat1)
    d_lng = math.radians(lng2 - lng1)
    a = (math.sin(d_lat / 2) ** 2 +
         math.cos(math.radians(lat1)) *
         math.cos(math.radians(lat2)) *
         math.sin(d_lng / 2) ** 2)
    return radius * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

def clear_db(session):
    session.run("MATCH (n) DETACH DELETE n")
    print("  Cleared database")

def create_constraints(session):
    session.run("CREATE CONSTRAINT IF NOT EXISTS FOR (s:BusStop) REQUIRE s.id IS UNIQUE")
    session.run("CREATE CONSTRAINT IF NOT EXISTS FOR (r:Route) REQUIRE r.route_id IS UNIQUE")
    print("  Constraints created")

def load_stops(session, stops):
    for stop_id, name, lat, lng, zone, is_hub in stops:
        session.run(
            """
            MERGE (s:BusStop {id: $id})
            SET s.name = $name, s.lat = $lat, s.lng = $lng,
                s.zone = $zone, s.is_hub = $is_hub
            """,
            id=stop_id, name=name, lat=lat, lng=lng, zone=zone, is_hub=is_hub
        )
    print(f"  Loaded {len(stops)} stops")

def load_routes(session, routes, edge_distances):
    for route in routes:
        # Create route
        session.run(
            """
            MERGE (r:Route {route_id: $route_id})
            SET r.route_no = $route_no, r.name = $name,
                r.operator = $operator, r.source_file = $source_file
            """,
            route_id=route["route_id"], route_no=route["route_no"],
            name=route["name"], operator=route["operator"],
            source_file=route["source_file"]
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
                route_id=route["route_id"], stop_id=stop_id
            )
        
        # Create NEXT_STOP relationships
        for idx in range(len(stops) - 1):
            from_id = stops[idx]
            to_id = stops[idx + 1]
            from_name = stop_names[idx]
            to_name = stop_names[idx + 1]
            
            # Get distance
            edge_key = (from_name, to_name)
            if edge_key in edge_distances:
                distance_km = edge_distances[edge_key]["distance_km"]
                time_min = edge_distances[edge_key]["time_min"]
            else:
                # Get coordinates and calculate
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
            
            # Create relationship with ALL properties
            session.run(
                """
                MATCH (a:BusStop {id: $from_id})
                MATCH (b:BusStop {id: $to_id})
                MERGE (a)-[rel:NEXT_STOP {route_id: $route_id, seq: $seq}]->(b)
                SET rel.route_no = $route_no,
                    rel.distance_km = $distance_km,
                    rel.time_min = $time_min,
                    rel.weight_distance = $distance_km,
                    rel.weight_time = $time_min
                """,
                from_id=from_id, to_id=to_id,
                route_id=route["route_id"], route_no=route["route_no"],
                seq=idx, distance_km=round(distance_km, 3),
                time_min=round(time_min, 1)
            )
    
    print(f"  Loaded {len(routes)} routes")

def main():
    print("Building dataset...")
    dataset = build_graph_dataset()
    
    print(f"Dataset: {len(dataset['stops'])} stops, {len(dataset['routes'])} routes")
    
    print("Connecting to Neo4j...")
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
    
    with driver.session() as session:
        print("Loading data...")
        clear_db(session)
        create_constraints(session)
        load_stops(session, dataset["stops"])
        load_routes(session, dataset["routes"], dataset["edge_distances"])
        
        # Verify
        stops_count = session.run("MATCH (s:BusStop) RETURN count(s) AS c").single()["c"]
        routes_count = session.run("MATCH (r:Route) RETURN count(r) AS c").single()["c"]
        edges_count = session.run("MATCH ()-[r:NEXT_STOP]->() RETURN count(r) AS c").single()["c"]
        
        print(f"\nVerification:")
        print(f"  Stops: {stops_count}")
        print(f"  Routes: {routes_count}")
        print(f"  Edges: {edges_count}")
    
    driver.close()
    print("\nDone!")

if __name__ == "__main__":
    main()
