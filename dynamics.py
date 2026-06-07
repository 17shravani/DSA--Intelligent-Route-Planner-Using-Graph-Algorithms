# dynamics.py
import heapq

def apply_traffic(G, edge_list, factor=1.5):
    """
    Applies live traffic latency multiplier factor to target edges.
    Example: factor = 1.5 increases travel duration by 50% on those segments.
    """
    for u, v in edge_list:
        if G.has_edge(u, v):
            G[u][v]["traffic_factor"] = factor

def close_road(G, u, v):
    """Dynamically removes a road segment (closure simulation)."""
    if G.has_edge(u, v):
        G.remove_edge(u, v)

def route_with_turn_penalties(G, src, dst, base_cost_fn, turn_penalty_sec=15.0):
    """
    Computes optimal route incorporating turn penalties.
    To enforce turn penalties, states must track (current_node, previous_node) to notice street transitions.
    """
    # Min-Heap entry format: (total_cost, current_node, previous_node)
    pq = [(0.0, src, None)]
    visited = {}
    parent = {}
    
    while pq:
        cost, node, prev = heapq.heappop(pq)
        state_key = (node, prev)
        
        if state_key in visited and cost >= visited[state_key]:
            continue
        visited[state_key] = cost
        
        if node == dst:
            # Rebuild path
            path = [node]
            curr_state = (node, prev)
            while curr_state in parent:
                prev_node, grand_prev = parent[curr_state]
                path.append(prev_node)
                curr_state = (prev_node, grand_prev)
            return list(reversed(path))
            
        for _, neighbor, attrs in G.out_edges(node, data=True):
            base_edge_cost = base_cost_fn(attrs)
            turn_cost = 0.0
            
            # If transitioning between roads (e.g. prev -> node -> neighbor), apply penalty if it constitutes a turn.
            if prev is not None:
                # Basic turn penalty approximation:
                # If the road class changes or it isn't a direct straight line relative alignment.
                prev_attrs = G[prev][node]
                # If road class changes, we treat it as an intersection transition / turn
                if prev_attrs.get("road_class") != attrs.get("road_class"):
                    turn_cost = turn_penalty_sec
                    
            heapq.heappush(pq, (cost + base_edge_cost + turn_cost, neighbor, node))
            parent[(neighbor, node)] = (node, prev)
            
    raise ValueError(f"No path found with turn penalties from {src} to {dst}")
