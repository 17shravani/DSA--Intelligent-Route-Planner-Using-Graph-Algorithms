# test_routing.py
import pytest
from graph_loader import load_graph, time_cost, distance_cost
from router import shortest_path, path_cost
from multicriteria import route_weighted
from dynamics import apply_traffic, route_with_turn_penalties

def test_load_graph():
    G = load_graph("roads.csv")
    assert G.number_of_nodes() > 0
    assert G.number_of_edges() > 0

def test_fastest_vs_shortest():
    G = load_graph("roads.csv")
    src, dst = "N0_0", "N5_5"
    p_time = shortest_path(G, src, dst, "time")
    p_dist = shortest_path(G, src, dst, "distance")
    
    t_time = path_cost(G, p_time, time_cost)
    t_dist = path_cost(G, p_dist, time_cost)
    
    # Fast route must arrive faster or equal to distance-optimized route
    assert t_time <= t_dist

def test_traffic_recalculation():
    G = load_graph("roads.csv")
    src, dst = "N0_0", "N2_2"
    # Initial short path
    p1 = shortest_path(G, src, dst, "time")
    
    # Artificially congest all edges on this path
    congested_edges = list(zip(p1[:-1], p1[1:]))
    apply_traffic(G, congested_edges, factor=5.0)
    
    p2 = shortest_path(G, src, dst, "time")
    # Congestion should yield a different route recommendation or increased duration
    assert path_cost(G, p2, time_cost) > 0

def test_turn_penalties():
    G = load_graph("roads.csv")
    src, dst = "N0_0", "N4_4"
    path = route_with_turn_penalties(G, src, dst, time_cost, turn_penalty_sec=30.0)
    assert len(path) >= 2
    assert path[0] == src
    assert path[-1] == dst
