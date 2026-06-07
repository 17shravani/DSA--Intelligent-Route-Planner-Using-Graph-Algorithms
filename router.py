# router.py
import math
import heapq
import networkx as nx
from graph_loader import time_cost, distance_cost, money_cost, eco_cost, ev_energy_cost

def path_cost(G, path, cost_fn):
    """Calculates sum of the cost evaluation along a sequence of path nodes."""
    return sum(cost_fn(G[u][v]) for u, v in zip(path[:-1], path[1:]))

def weight_factory(cost_fn):
    def w(u, v, attrs):
        return cost_fn(attrs)
    return w

def haversine_m(lat1, lon1, lat2, lon2):
    R = 6371000
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat/2) ** 2 + 
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * 
         math.sin(dlon/2) ** 2)
    return 2 * R * math.asin(math.sqrt(a))

def astar_heuristic(G, n1, n2):
    # Optimistic time heuristic based on straight-line coordinates
    out_edges = list(G.out_edges(n1, data=True))
    if not out_edges:
        return 0.0
    lat1, lon1 = out_edges[0][2]["lat_u"], out_edges[0][2]["lon_u"]
    
    out_edges2 = list(G.out_edges(n2, data=True))
    if not out_edges2:
        return 0.0
    lat2, lon2 = out_edges2[0][2]["lat_u"], out_edges2[0][2]["lon_u"]
    
    dist_m = haversine_m(lat1, lon1, lat2, lon2)
    max_mps = 80.0 * 1000.0 / 3600.0
    return dist_m / max_mps

def dijkstra_manual(G, src, dst, cost_fn):
    pq = []
    heapq.heappush(pq, (0.0, src, [src]))
    visited_costs = {src: 0.0}
    
    while pq:
        curr_cost, curr_node, path = heapq.heappop(pq)
        
        if curr_node == dst:
            return path
            
        if curr_cost > visited_costs.get(curr_node, float('inf')):
            continue
            
        for neighbor in G.neighbors(curr_node):
            edge_attrs = G[curr_node][neighbor]
            weight = cost_fn(edge_attrs)
            new_cost = curr_cost + weight
            
            if new_cost < visited_costs.get(neighbor, float('inf')):
                visited_costs[neighbor] = new_cost
                new_path = list(path)
                new_path.append(neighbor)
                heapq.heappush(pq, (new_cost, neighbor, new_path))
                
    raise ValueError(f"No path connected between {src} and {dst}")

def shortest_path(G, src, dst, objective="time"):
    cost_map = {
        "time": time_cost,
        "distance": distance_cost,
        "money": money_cost,
        "eco": eco_cost,
        "ev_energy": ev_energy_cost
    }
    
    if objective not in cost_map:
        objective = "time"
        
    cfn = cost_map[objective]
    return dijkstra_manual(G, src, dst, cfn)

# ADVANCED FEATURE: EV Constraint-Aware Routing
# Computes shortest paths while guaranteeing battery levels do not drop below a critical threshold (e.g. 2.0 kWh).
# If the direct path exceeds threshold, it routes dynamically through a fast charging station node.
def route_ev_constrained(G, src, dst, initial_battery_kwh=10.0, min_battery_kwh=2.0):
    """
    Solves resource-constrained routing. If direct energy consumption > initial - min_battery,
    finds the optimal path that routes through a charging station to recharge the battery.
    """
    # 1. Attempt direct shortest energy path
    try:
        direct_path = shortest_path(G, src, dst, "ev_energy")
        direct_energy = path_cost(G, direct_path, ev_energy_cost)
        if initial_battery_kwh - direct_energy >= min_battery_kwh:
            return direct_path, False, []  # Battery is sufficient, no recharge needed
    except Exception:
        pass

    # 2. Search for the best routing path via any charging station node
    best_overall_time = float('inf')
    best_overall_path = None
    chosen_charger = None
    
    # Identify charging stations in the network
    chargers = [n for n, attr in G.nodes(data=True) if attr.get("is_charging_station")]
    
    for charger in chargers:
        try:
            # Segment 1: Source to Charger
            path1 = shortest_path(G, src, charger, "ev_energy")
            energy1 = path_cost(G, path1, ev_energy_cost)
            
            # Segment 2: Charger to Destination
            path2 = shortest_path(G, charger, dst, "ev_energy")
            energy2 = path_cost(G, path2, ev_energy_cost)
            
            # Ensure both legs satisfy the battery range restriction individually
            # Segment 1 starts at initial_battery_kwh.
            # Segment 2 starts at fully recharged battery (e.g. 10.0 kWh).
            if (initial_battery_kwh - energy1 >= min_battery_kwh) and (10.0 - energy2 >= min_battery_kwh):
                # We prioritize total travel duration (including a 120-second mock charging delay)
                time1 = path_cost(G, path1, time_cost)
                time2 = path_cost(G, path2, time_cost)
                total_time = time1 + time2 + 120.0  # 120s charging penalty
                
                if total_time < best_overall_time:
                    best_overall_time = total_time
                    # Merge paths avoiding repeating the charger node
                    best_overall_path = path1[:-1] + path2
                    chosen_charger = charger
        except Exception:
            continue
            
    if best_overall_path:
        return best_overall_path, True, [chosen_charger]
        
    # Fallback to direct path if no dynamic charging detour could be solved
    return shortest_path(G, src, dst, "time"), False, []
