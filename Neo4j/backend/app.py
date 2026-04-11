"""
Flask backend for the Mangaluru Bus Navigator.
"""

import heapq
import os
from collections import defaultdict

from flask import Flask, jsonify, render_template, request
from flask_cors import CORS
from neo4j import GraphDatabase

app = Flask(
    __name__,
    template_folder="../../frontend/templates",
    static_folder="../../frontend/static",
)
CORS(app)

NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "")

TRANSFER_PENALTY = 1.25

driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))


def run_query(cypher, **params):
    with driver.session() as session:
        return [dict(record) for record in session.run(cypher, **params)]


def build_stop_lookup():
    rows = run_query(
        """
        MATCH (s:BusStop)
        RETURN s.id AS id, s.name AS name, s.lat AS lat,
               s.lng AS lng, s.zone AS zone, s.is_hub AS is_hub
        """
    )
    return {row["id"]: row for row in rows}


def load_route_graph(weight_field="weight_distance"):
    if weight_field == "weight_time":
        weight_expr = "COALESCE(rel.weight_time, rel.time_min, 2.0)"
    elif weight_field == "weight_distance":
        weight_expr = "COALESCE(rel.weight_distance, rel.distance_km, 0.5)"
    else:
        weight_expr = "1.0"

    rows = run_query(
        f"""
        MATCH (a:BusStop)-[rel:NEXT_STOP]->(b:BusStop)
        RETURN a.id AS from_id, b.id AS to_id,
               rel.route_id AS route_id, rel.route_no AS route_no,
               COALESCE(rel.distance_km, 0.5) AS distance_km,
               COALESCE(rel.time_min, 2.0) AS time_min,
               {weight_expr} AS weight
        """
    )

    adjacency = defaultdict(list)
    for row in rows:
        edge = {
            "to_id": row["to_id"],
            "route_id": row["route_id"],
            "route_no": row["route_no"],
            "distance_km": float(row["distance_km"]),
            "time_min": float(row["time_min"]),
            "weight": float(row["weight"]),
        }
        adjacency[row["from_id"]].append(edge)

        reverse_edge = dict(edge)
        reverse_edge["to_id"] = row["from_id"]
        adjacency[row["to_id"]].append(reverse_edge)

    return adjacency


def build_route_segments(stop_sequence, route_sequence, stops):
    route_segments = []
    if not route_sequence:
        return route_segments

    current_route = route_sequence[0]
    segment_start = stops[stop_sequence[0]]["name"]

    for idx, route_no in enumerate(route_sequence[1:], start=1):
        if route_no != current_route:
            route_segments.append(
                {
                    "route_no": current_route,
                    "from_stop": segment_start,
                    "to_stop": stops[stop_sequence[idx]]["name"],
                }
            )
            current_route = route_no
            segment_start = stops[stop_sequence[idx]]["name"]

    route_segments.append(
        {
            "route_no": current_route,
            "from_stop": segment_start,
            "to_stop": stops[stop_sequence[-1]]["name"],
        }
    )
    return route_segments


def find_path_by_transfers(from_id, to_id):
    stops = build_stop_lookup()
    adjacency = load_route_graph("hops")

    if from_id not in stops or to_id not in stops:
        return None

    queue = [(0, 0, from_id, None)]
    best_cost = {(from_id, None): (0, 0)}
    previous = {}
    best_target = None

    while queue:
        transfers, hops, node_id, current_route = heapq.heappop(queue)
        state = (node_id, current_route)

        if best_cost.get(state) != (transfers, hops):
            continue

        if node_id == to_id:
            best_target = state
            break

        for edge in adjacency.get(node_id, []):
            next_route = edge["route_id"]
            next_transfers = transfers + (1 if current_route and current_route != next_route else 0)
            candidate = (next_transfers, hops + 1)
            next_state = (edge["to_id"], next_route)

            if next_state not in best_cost or candidate < best_cost[next_state]:
                best_cost[next_state] = candidate
                previous[next_state] = (state, edge)
                heapq.heappush(queue, (*candidate, edge["to_id"], next_route))

    if not best_target:
        return None

    path_states = []
    cursor = best_target
    while cursor in previous:
        path_states.append(previous[cursor][1])
        cursor = previous[cursor][0]
    path_states.reverse()

    stop_sequence = [from_id]
    route_sequence = []
    total_distance = 0.0
    total_time = 0.0

    for edge in path_states:
        stop_sequence.append(edge["to_id"])
        route_sequence.append(edge["route_no"])
        total_distance += edge["distance_km"]
        total_time += edge["time_min"]

    routes_used = []
    for route_no in route_sequence:
        if not routes_used or routes_used[-1] != route_no:
            routes_used.append(route_no)

    transfers, hops = best_cost[best_target]
    return {
        "stops": [stops[stop_id] for stop_id in stop_sequence],
        "routes_used": routes_used,
        "route_segments": build_route_segments(stop_sequence, route_sequence, stops),
        "hops": hops,
        "transfers": transfers,
        "distance_km": round(total_distance, 2),
        "time_min": round(total_time, 1),
        "optimization": "fewest_transfers",
    }


def find_weighted_path(from_id, to_id, weight_field, optimize_by):
    stops = build_stop_lookup()
    adjacency = load_route_graph(weight_field)

    if from_id not in stops or to_id not in stops:
        return None

    queue = [(0.0, 0, 0, from_id, None, 0.0, 0.0)]
    best_cost = {(from_id, None): (0.0, 0, 0, 0.0, 0.0)}
    previous = {}
    best_target = None

    while queue:
        total_cost, transfers, hops, node_id, current_route, total_dist, total_time = heapq.heappop(queue)
        state = (node_id, current_route)

        if best_cost.get(state) != (total_cost, transfers, hops, total_dist, total_time):
            continue

        if node_id == to_id:
            best_target = state
            break

        for edge in adjacency.get(node_id, []):
            next_route = edge["route_id"]
            next_transfers = transfers + (1 if current_route and current_route != next_route else 0)
            step_cost = edge["weight"]

            if current_route and current_route != next_route:
                step_cost += TRANSFER_PENALTY

            candidate = (
                round(total_cost + step_cost, 6),
                next_transfers,
                hops + 1,
                round(total_dist + edge["distance_km"], 6),
                round(total_time + edge["time_min"], 6),
            )
            next_state = (edge["to_id"], next_route)

            if next_state not in best_cost or candidate < best_cost[next_state]:
                best_cost[next_state] = candidate
                previous[next_state] = (state, edge)
                heapq.heappush(
                    queue,
                    (candidate[0], candidate[1], candidate[2], edge["to_id"], next_route, candidate[3], candidate[4]),
                )

    if not best_target:
        return None

    path_states = []
    cursor = best_target
    while cursor in previous:
        path_states.append(previous[cursor][1])
        cursor = previous[cursor][0]
    path_states.reverse()

    stop_sequence = [from_id]
    route_sequence = []
    total_distance = 0.0
    total_time = 0.0

    for edge in path_states:
        stop_sequence.append(edge["to_id"])
        route_sequence.append(edge["route_no"])
        total_distance += edge["distance_km"]
        total_time += edge["time_min"]

    routes_used = []
    for route_no in route_sequence:
        if not routes_used or routes_used[-1] != route_no:
            routes_used.append(route_no)

    _, transfers, hops, _, _ = best_cost[best_target]
    return {
        "stops": [stops[stop_id] for stop_id in stop_sequence],
        "routes_used": routes_used,
        "route_segments": build_route_segments(stop_sequence, route_sequence, stops),
        "hops": hops,
        "transfers": transfers,
        "distance_km": round(total_distance, 2),
        "time_min": round(total_time, 1),
        "optimization": optimize_by,
    }


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/stops")
def get_stops():
    rows = run_query(
        """
        MATCH (s:BusStop)
        RETURN s.id AS id, s.name AS name, s.lat AS lat,
               s.lng AS lng, s.zone AS zone, s.is_hub AS is_hub
        ORDER BY s.name
        """
    )
    return jsonify(rows)


@app.route("/api/routes")
def get_routes():
    rows = run_query(
        """
        MATCH (r:Route)-[:SERVES]->(s:BusStop)
        RETURN r.route_id AS route_id, r.route_no AS route_no,
               r.name AS name, r.operator AS operator,
               collect({id: s.id, name: s.name, lat: s.lat, lng: s.lng}) AS stops
        ORDER BY r.route_no, r.name
        """
    )
    return jsonify(rows)


@app.route("/api/find-path")
def find_path():
    from_id = request.args.get("from_id")
    to_id = request.args.get("to_id")
    optimize_by = request.args.get("optimize_by", "distance")

    if not from_id or not to_id:
        return jsonify({"error": "from_id and to_id are required"}), 400

    if from_id == to_id:
        return jsonify({"error": "Source and destination cannot be the same stop"}), 400

    try:
        if optimize_by == "transfers":
            result = find_path_by_transfers(from_id, to_id)
        elif optimize_by == "time":
            result = find_weighted_path(from_id, to_id, "weight_time", "time")
        else:
            result = find_weighted_path(from_id, to_id, "weight_distance", "distance")

        if not result:
            return jsonify({"error": "No path found between these stops"}), 404

        return jsonify(result)
    except Exception as exc:
        print(f"Error in /api/find-path: {exc}")
        return jsonify({"error": str(exc)}), 500


@app.route("/api/hubs")
def get_hubs():
    rows = run_query(
        """
        MATCH (r:Route)-[:SERVES]->(s:BusStop)
        RETURN s.id AS id, s.name AS name, s.lat AS lat, s.lng AS lng,
               s.zone AS zone, count(DISTINCT r.route_id) AS route_count
        ORDER BY route_count DESC, s.name
        LIMIT 10
        """
    )
    return jsonify(rows)


@app.route("/api/reachable")
def get_reachable():
    stop_id = request.args.get("stop_id")
    max_hops = int(request.args.get("max_hops", 4))

    if not stop_id:
        return jsonify({"error": "stop_id is required"}), 400

    rows = run_query(
        f"""
        MATCH (start:BusStop {{id: $stop_id}})
        MATCH (start)-[:NEXT_STOP*1..{max_hops}]-(dest:BusStop)
        WHERE dest.id <> $stop_id
        RETURN DISTINCT dest.id AS id, dest.name AS name,
               dest.lat AS lat, dest.lng AS lng, dest.zone AS zone
        ORDER BY dest.name
        """,
        stop_id=stop_id,
    )
    return jsonify(rows)


@app.route("/api/landmarks")
def get_landmarks():
    rows = run_query(
        """
        MATCH (l:Landmark)-[:NEAR]->(s:BusStop)
        RETURN l.name AS landmark, l.type AS type,
               s.id AS stop_id, s.name AS stop_name,
               s.lat AS lat, s.lng AS lng
        """
    )
    return jsonify(rows)


@app.route("/api/routes-through/<stop_id>")
def routes_through_stop(stop_id):
    rows = run_query(
        """
        MATCH (r:Route)-[:SERVES]->(s:BusStop {id: $stop_id})
        RETURN DISTINCT r.route_no AS route_no, r.name AS name, r.operator AS operator
        ORDER BY r.route_no, r.name
        """,
        stop_id=stop_id,
    )
    return jsonify(rows)


if __name__ == "__main__":
    print("Starting Mangaluru Bus Navigator...")
    app.run(debug=True, port=5000)
