# OptimaPath AI: Intelligent Route Planner Using Graph Algorithms

OptimaPath AI is a production-grade, highly optimized routing and navigation engine built to calculate multi-objective shortest paths on road networks. It supports custom weights for time, distance, and tolls, simulates real-time traffic conditions, handles street blockages, computes turn penalties, and exposes a high-fidelity interactive dashboard.

## 🚀 Key Features

* **Multi-Criteria Optimization**: Choose between Fastest, Shortest, Toll-Avoidance, Eco-Friendly, or custom weighted formulas.
* **Custom Dijkstra Implementation**: Pure Python min-heap implementation showcasing fundamental DSA graph algorithms.
* **Dynamic Constraints**: Live dynamic traffic congestion vectors, turn penalties, and physical road blockages.
* **Pareto-Optimal Frontiers**: Compiles multi-criteria alternatives where no route dominates another.
* **Interactive Map Dashboard**: High-fidelity dark-themed Leaflet front-end.
* **Clean & Modular**: Enterprise-ready architecture with clean separation of datasets, routing core, APIs, and client views.

---

## 🛠️ Folder Structure

```
Intelligent-Route-Planner-Graph-Algorithms/
│
├── data_builder.py     # Grid layout coordinates dataset generator
├── roads.csv           # Loaded CSV containing edges, speeds, coordinates, and tolls
├── graph_loader.py     # Parses roads.csv and evaluates edge cost functions
├── router.py           # Dijkstra core path solver
├── multicriteria.py    # Custom multi-criteria and Pareto filters
├── dynamics.py         # Handles live traffic congestion and turn penalties
├── app.py              # FastAPI backend controller
├── index.html          # HTML5 premium UI dashboard with Leaflet map Integration
├── main.py             # App entrypoint (runs Server or CLI)
├── test_routing.py     # Algorithmic correctness test cases
└── requirements.txt    # Application dependency manifest
```

---

## 🏁 Installation & Running

### 1. Prerequisites
Ensure Python 3.10+ is installed on your local environment.

### 2. Install Dependencies
Run the command below in your shell terminal:
```bash
pip install -r requirements.txt
```

### 3. Generate Map Data
Build the synthetic road grid dataset:
```bash
python data_builder.py
```

### 4. Run CLI Console Interface
```bash
python main.py --mode cli
```

### 5. Start the Web Dashboard
```bash
python main.py --mode server
```
Navigate to **[http://127.0.0.1:8000](http://127.0.0.1:8000)** inside your web browser.

---

## 📚 DSA Core Concept Explanations

### Adjacency List Representation
Roads are stored using directed graphs where intersections are vertices ($V$) and roads are edges ($E$). Rather than an inefficient adjacency matrix, we use adjacency lists represented natively by dictionaries in Python inside NetworkX: `G[u][v]` holds edge attributes such as speed, length, and coordinate coordinates.

### Dijkstra's Shortest Path
We implemented a priority queue shortest path engine using a min-heap structure (`heapq` module). Starting from the origin, the frontier expands outwards, always relaxing the closest node first:
$$d(v) = \min(d(v), d(u) + w(u, v))$$
Time Complexity: $\mathcal{O}((E + V) \log V)$
Space Complexity: $\mathcal{O}(V + E)$

---

## 👥 Interview Preparation Q&A

### 1. Explain your project.
**Answer:** I built **OptimaPath AI**, an intelligent route planning platform that computes optimal paths using custom graph algorithms. Intersections are nodes and roads are weighted edges. It goes beyond simple shortest-path solvers by offering multi-criteria balancing (tolls, duration, distance, eco-impact), simulating turn penalties, dynamic traffic updates, and showcasing these paths visually on a Leaflet mapping dashboard.

### 2. Why is an Adjacency List preferred over an Adjacency Matrix for road networks?
**Answer:** Road networks are sparse graphs where the average degree of a node (intersections) is typically less than 4. An adjacency matrix consumes $\mathcal{O}(V^2)$ memory, which is wasteful. An adjacency list consumes $\mathcal{O}(V + E)$ space, making it efficient for large-scale spatial datasets.
