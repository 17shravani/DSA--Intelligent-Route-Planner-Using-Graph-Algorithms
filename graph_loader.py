# graph_loader.py
import csv
import networkx as nx

def load_graph(csv_path="roads.csv"):
    """
    Loads road network graph from a CSV file into a directed NetworkX graph.
    Computes base travel times for each edge dynamically.
    Includes advanced node classification for electric vehicles (charging stations)
    and custom speed characteristics.
    """
    G = nx.DiGraph()
    with open(csv_path, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            u, v = row["u"], row["v"]
            attrs = {
                "lat_u": float(row["lat_u"]),
                "lon_u": float(row["lon_u"]),
                "lat_v": float(row["lat_v"]),
                "lon_v": float(row["lon_v"]),
                "distance_m": float(row["distance_m"]),
                "speed_kph": float(row["speed_kph"]),
                "toll": int(row["toll"]),
                "one_way": int(row["one_way"]),
                "road_class": row["road_class"],
                "traffic_factor": 1.0  # Dynamic traffic multiplier
            }
            # Calculate base travel time in seconds
            speed_mps = attrs["speed_kph"] * 1000.0 / 3600.0
            attrs["base_sec"] = attrs["distance_m"] / speed_mps
            
            # Advanced Feature: EV Energy Consumption estimation
            # Cruising at primary roads consumes less energy per unit distance than stops on residential roads
            consumption_factor = 0.15 if attrs["road_class"] == "primary" else 0.22
            attrs["ev_energy_kwh"] = (attrs["distance_m"] / 1000.0) * consumption_factor
            
            G.add_edge(u, v, **attrs)
            
    # Designate specific grid nodes as EV Fast Charging Stations
    charging_stations = {"N1_1", "N3_3", "N4_4"}
    for node in G.nodes():
        G.nodes[node]["is_charging_station"] = (node in charging_stations)
        
    return G

# Pluggable Optimization Objectives
def time_cost(e):
    return e["base_sec"] * e.get("traffic_factor", 1.0)

def distance_cost(e):
    return e["distance_m"]

def money_cost(e):
    return e["toll"]

def eco_cost(e):
    class_factor = 0.85 if e["road_class"] == "primary" else 1.0
    return time_cost(e) * class_factor

def ev_energy_cost(e):
    return e["ev_energy_kwh"]
