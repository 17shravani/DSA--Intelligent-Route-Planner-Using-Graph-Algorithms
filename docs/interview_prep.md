# Interview Prep & Course Concept Guide

This document acts as your comprehensive companion guide to ace code walkthroughs, viva examinations, and software engineering interviews based on your work building **OptimaPath AI**.

## 1. Algorithmic Breakdown

### Dijkstra's Shortest Path
* **What it does**: Computes the shortest path from a single source node to all other nodes in a graph with non-negative edge weights.
* **Why weights must be non-negative**: Dijkstra's algorithm is greedy. It assumes that once a node is popped from the priority queue, its shortest path has been finalized. If negative edge weights were present, a longer path with a negative edge could later reduce the distance, violating this assumption.
* **Time Complexity**: $\mathcal{O}((E + V) \log V)$ when using a binary heap priority queue.
* **Space Complexity**: $\mathcal{O}(V + E)$ to store the graph and priority queue states.

### A* Shortest Path
* **What it does**: Speeds up Dijkstra's algorithm by using a heuristic function $h(n)$ that estimates the distance from node $n$ to the target.
* **Heuristic Condition**: The heuristic must be *admissible* (never overestimates the actual cost to reach the destination) and *consistent* (monotonically non-decreasing).
* **Our Heuristic**: We compute the straight-line Haversine distance from node coordinates to the destination and divide it by the maximum speed limit (80 km/h) to get an optimistic lower bound for travel time.

---

## 2. Dynamic Routing & Turn Penalties

### How turn penalties are modeled:
If you represent a road network using a standard intersection-as-node graph, you cannot easily associate costs with transitions between edges (e.g., a hard left turn). 
To solve this in production:
1. **Turn-Expanded Graphs**: Every intersection node is split into multiple virtual nodes (one for each entry lane). Edges represent valid transitions between lanes and carry turn costs.
2. **State-Tracking Dijkstra**: In this project, we modified the traversal state to track the tuple `(current_node, previous_node)`. When transitioning to a neighbor, we apply a penalty if the road class changes, simulating an intersection turn.

---

## 3. High-Frequency Interview Questions

### Q1. How does Google Maps compute routes so quickly?
**Answer:** Google Maps doesn't run raw Dijkstra on a flat global graph (which would take seconds or minutes). Instead, they use hierarchical routing techniques:
* **Contraction Hierarchies (CH)**: Precomputes "shortcuts" bypassing minor streets to accelerate queries.
* **Hub Labeling / Transit Node Routing**: Identifies key highway access points ("hubs") and precomputes distances between all hubs.
* **Partitioning (e.g., Custom Route Planning)**: Splits the map into local cells and computes routes hierarchically.

### Q2. How did you handle concurrent user routing requests?
**Answer:** In the FastAPI server, we load the base road network into memory once. When a user requests a route with custom dynamic parameters (like closed streets or custom traffic), we create a lightweight copy of the graph using `G.copy()` inside the route handler. This isolates requests and prevents thread race conditions.
