# multicriteria.py
import networkx as nx
from graph_loader import time_cost, distance_cost, money_cost

def weighted_cost(attrs, alpha=1.0, beta=0.01, gamma=10.0):
    """
    Computes a linear combination of routing criteria:
    cost = alpha * time_sec + beta * distance_m + gamma * tolls
    Allows custom user preferences (e.g. balancing speed and cost).
    """
    return alpha * time_cost(attrs) + beta * distance_cost(attrs) + gamma * money_cost(attrs)

def route_weighted(G, src, dst, alpha=1.0, beta=0.01, gamma=10.0):
    """Computes a single shortest path using weighted preference coefficients."""
    w = lambda u, v, attrs: weighted_cost(attrs, alpha, beta, gamma)
    return nx.shortest_path(G, src, dst, weight=w)

def k_shortest_paths(G, src, dst, k=5, weight_fn=time_cost):
    """Enumerates top K unique alternative path proposals using simple k-shortest paths search."""
    w = lambda u, v, attrs: weight_fn(attrs)
    try:
        return list(nx.shortest_simple_paths(G, src, dst, weight=w))[:k]
    except nx.NetworkXNoPath:
        return []

def pareto_routes(G, src, dst, k=10):
    """
    Discovers Pareto-optimal routing alternatives from candidate set.
    A route is included if no other candidate has strictly better attributes across all dimensions.
    Returns list of tuples: (route_node_list, (time_sec, distance_m, toll_units))
    """
    candidates = k_shortest_paths(G, src, dst, k=k, weight_fn=time_cost)
    scored = []
    
    for path in candidates:
        t = sum(time_cost(G[u][v]) for u, v in zip(path[:-1], path[1:]))
        d = sum(distance_cost(G[u][v]) for u, v in zip(path[:-1], path[1:]))
        m = sum(money_cost(G[u][v]) for u, v in zip(path[:-1], path[1:]))
        scored.append((path, (t, d, m)))
        
    pareto = []
    # Retain non-dominated options
    for path, scores in scored:
        is_dominated = False
        for other_path, other_scores in scored:
            if other_path == path:
                continue
            # A route dominates another if it is better or equal in all criteria AND strictly better in at least one.
            better_or_equal = all(o_val <= s_val for o_val, s_val in zip(other_scores, scores))
            strictly_better = any(o_val < s_val for o_val, s_val in zip(other_scores, scores))
            if better_or_equal and strictly_better:
                is_dominated = True
                break
        if not is_dominated:
            pareto.append((path, scores))
            
    return pareto
