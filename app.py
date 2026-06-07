# app.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import List, Tuple, Optional
import os

from graph_loader import load_graph, time_cost, distance_cost, money_cost, eco_cost, ev_energy_cost
from router import shortest_path, path_cost, route_ev_constrained
from multicriteria import route_weighted, pareto_routes
from dynamics import apply_traffic, close_road, route_with_turn_penalties

app = FastAPI(title="OptimaPath AI: Intelligent Route Planner Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

G_base = load_graph("roads.csv")

class RouteRequest(BaseModel):
    src: str
    dst: str
    objective: str = "time"  # time | distance | money | eco | ev_energy | weighted | ev_constrained
    alpha: float = 1.0
    beta: float = 0.01
    gamma: float = 10.0
    traffic_edges: List[Tuple[str, str]] = []
    close_edges: List[Tuple[str, str]] = []
    apply_turn_penalties: bool = False
    turn_penalty_sec: float = 15.0
    initial_battery_kwh: float = 10.0
    min_battery_kwh: float = 2.0

def path_to_geojson(G, path):
    coordinates = []
    for u, v in zip(path[:-1], path[1:]):
        edge = G[u][v]
        coordinates.append([edge["lon_u"], edge["lat_u"]])
    last_edge = G[path[-2]][path[-1]]
    coordinates.append([last_edge["lon_v"], last_edge["lat_v"]])
    return {
        "type": "Feature",
        "geometry": {
            "type": "LineString",
            "coordinates": coordinates
        },
        "properties": {}
    }

@app.post("/route")
def compute_route(req: RouteRequest):
    G = G_base.copy()
    
    if req.traffic_edges:
        apply_traffic(G, req.traffic_edges, factor=2.5)
        
    for u, v in req.close_edges:
        try:
            close_road(G, u, v)
        except Exception:
            pass
            
    if not G.has_node(req.src) or not G.has_node(req.dst):
        raise HTTPException(status_code=400, detail="Source or Destination node does not exist in graph network.")
        
    try:
        ev_recharged = False
        recharge_stations = []
        
        if req.objective == "ev_constrained":
            path, ev_recharged, recharge_stations = route_ev_constrained(
                G, req.src, req.dst, req.initial_battery_kwh, req.min_battery_kwh
            )
        elif req.apply_turn_penalties:
            cost_map = {
                "time": time_cost, 
                "distance": distance_cost, 
                "money": money_cost, 
                "eco": eco_cost,
                "ev_energy": ev_energy_cost
            }
            cfn = cost_map.get(req.objective, time_cost)
            path = route_with_turn_penalties(G, req.src, req.dst, cfn, req.turn_penalty_sec)
        elif req.objective == "weighted":
            path = route_weighted(G, req.src, req.dst, req.alpha, req.beta, req.gamma)
        else:
            path = shortest_path(G, req.src, req.dst, req.objective)
            
        tot_time = path_cost(G, path, time_cost)
        tot_dist = path_cost(G, path, distance_cost)
        tot_tolls = path_cost(G, path, money_cost)
        tot_energy = path_cost(G, path, ev_energy_cost)
        
        # Add mock charge delays
        if ev_recharged:
            tot_time += 120.0  # Add 120s dynamic charging delay to stats
            
        geojson = path_to_geojson(G, path)
        
        # Retrieve charging coordinates if recharged
        charger_coords = []
        for ch in recharge_stations:
            # Locate coordinate of charging node
            out_edges = list(G.out_edges(ch, data=True))
            if out_edges:
                charger_coords.append({"id": ch, "lat": out_edges[0][2]["lat_u"], "lon": out_edges[0][2]["lon_u"]})
        
        return {
            "status": "success",
            "path": path,
            "eta_sec": round(tot_time, 2),
            "distance_m": round(tot_dist, 2),
            "tolls": int(tot_tolls),
            "energy_kwh": round(tot_energy, 2),
            "ev_recharged": ev_recharged,
            "recharge_stations": charger_coords,
            "geojson": geojson
        }
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"No feasible path found: {str(e)}")

@app.get("/alternatives")
def get_alternatives(src: str, dst: str, k: int = 5):
    if not G_base.has_node(src) or not G_base.has_node(dst):
        raise HTTPException(status_code=400, detail="Invalid source or destination node.")
    try:
        pareto = pareto_routes(G_base, src, dst, k=k)
        routes = []
        for path, scores in pareto:
            routes.append({
                "path": path,
                "eta_sec": round(scores[0], 2),
                "distance_m": round(scores[1], 2),
                "tolls": int(scores[2]),
                "geojson": path_to_geojson(G_base, path)
            })
        return {"alternatives": routes}
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.get("/", response_class=HTMLResponse)
def serve_dashboard():
    if os.path.exists("index.html"):
        with open("index.html", "r", encoding="utf-8") as f:
            return f.read()
    return "<h3>OptimaPath AI Frontend dashboard index.html not found!</h3>"
