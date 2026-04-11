"""
Mangaluru Bus Network Dataset
Real stops and routes based on public route information.
Coordinates are actual GPS locations in Mangaluru.
"""

STOPS = [
    # id, name, latitude, longitude, zone, is_hub
    ("S01", "State Bank",            12.8698, 74.8426, "City Centre",     True),
    ("S02", "Hampankatta",           12.8674, 74.8423, "City Centre",     True),
    ("S03", "Lalbagh",               12.8713, 74.8397, "City Centre",     True),
    ("S04", "Bejai",                 12.8832, 74.8426, "North",           False),
    ("S05", "Kadri",                 12.8874, 74.8538, "North",           False),
    ("S06", "Kankanady",             12.8925, 74.8560, "North",           False),
    ("S07", "Bajpe",                 12.9621, 74.8126, "Airport Zone",    True),
    ("S08", "Balmatta",              12.8666, 74.8467, "City Centre",     False),
    ("S09", "Bunts Hostel",          12.8600, 74.8432, "South",           False),
    ("S10", "KMC Hospital",          12.8638, 74.8450, "City Centre",     False),
    ("S11", "Wenlock Hospital",      12.8726, 74.8392, "City Centre",     False),
    ("S12", "Urwa",                  12.8549, 74.8380, "South",           False),
    ("S13", "Attavar",               12.8780, 74.8329, "West",            False),
    ("S14", "Mangaladevi",           12.8740, 74.8484, "City Centre",     False),
    ("S15", "Kanjirapadi",           12.8820, 74.8590, "North",           False),
    ("S16", "Pumpwell",              12.8978, 74.8467, "North",           False),
    ("S17", "Bondel",                12.8910, 74.8350, "North",           False),
    ("S18", "Falnir",                12.8760, 74.8460, "City Centre",     False),
    ("S19", "Jyothi",                12.8650, 74.8400, "City Centre",     False),
    ("S20", "Kulur",                 12.8440, 74.8320, "South",           False),
    ("S21", "Mulki",                 13.0830, 74.7930, "North Outskirts", False),
    ("S22", "Moodabidri",            13.0680, 74.9900, "East Outskirts",  False),
    ("S23", "Surathkal",             13.0120, 74.7930, "North",           False),
    ("S24", "Mangalore Central Stn", 12.8694, 74.8431, "City Centre",    True),
    ("S25", "Kottara",               12.9130, 74.8570, "North",           False),
]

ROUTES = [
    {
        "route_no": "1",
        "name": "State Bank - Kunjathbail",
        "operator": "Private",
        "stops": ["S01", "S02", "S08", "S10", "S14", "S18", "S04", "S05"]
    },
    {
        "route_no": "1C",
        "name": "State Bank - Kadri",
        "operator": "Private",
        "stops": ["S01", "S02", "S08", "S10", "S18", "S05", "S06"]
    },
    {
        "route_no": "2G",
        "name": "Bajpe - State Bank",
        "operator": "KSRTC",
        "stops": ["S07", "S16", "S04", "S03", "S01", "S24"]
    },
    {
        "route_no": "3",
        "name": "State Bank - Bondel",
        "operator": "Private",
        "stops": ["S01", "S03", "S11", "S13", "S17", "S04"]
    },
    {
        "route_no": "5",
        "name": "Lalbagh - Urwa",
        "operator": "Private",
        "stops": ["S03", "S11", "S01", "S19", "S09", "S12", "S20"]
    },
    {
        "route_no": "7",
        "name": "State Bank - Surathkal",
        "operator": "KSRTC",
        "stops": ["S01", "S03", "S04", "S16", "S25", "S23"]
    },
    {
        "route_no": "9",
        "name": "Hampankatta - Pumpwell",
        "operator": "Private",
        "stops": ["S02", "S08", "S18", "S04", "S16", "S25"]
    },
    {
        "route_no": "10",
        "name": "State Bank - Moodabidri",
        "operator": "KSRTC",
        "stops": ["S01", "S02", "S14", "S15", "S06", "S25", "S22"]
    },
    {
        "route_no": "11",
        "name": "Central Station - Kankanady",
        "operator": "Private",
        "stops": ["S24", "S01", "S02", "S08", "S10", "S06"]
    },
    {
        "route_no": "14",
        "name": "Lalbagh - Bajpe Airport",
        "operator": "KSRTC",
        "stops": ["S03", "S01", "S04", "S16", "S17", "S07"]
    },
    {
        "route_no": "15",
        "name": "Bunts Hostel - Kadri",
        "operator": "Private",
        "stops": ["S09", "S19", "S02", "S08", "S10", "S18", "S05"]
    },
    {
        "route_no": "20",
        "name": "State Bank - Mulki",
        "operator": "KSRTC",
        "stops": ["S01", "S03", "S04", "S16", "S25", "S23", "S21"]
    },
]

LANDMARKS = [
    # name, near_stop_id, type
    ("Bajpe Airport",         "S07", "transport"),
    ("KMC Hospital",          "S10", "hospital"),
    ("Wenlock Hospital",      "S11", "hospital"),
    ("Mangala Stadium",       "S01", "landmark"),
    ("City Centre Mall",      "S02", "shopping"),
    ("Mangaladevi Temple",    "S14", "temple"),
    ("NITK Surathkal",        "S23", "education"),
    ("Moodabidri Jain Temple","S22", "temple"),
    ("Mangalore Central Rly", "S24", "transport"),
    ("St. Aloysius College",  "S08", "education"),
]
