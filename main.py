# main.py
import argparse
import sys
from graph_loader import load_graph, time_cost, distance_cost, money_cost, eco_cost
from router import shortest_path, path_cost
from multicriteria import route_weighted, pareto_routes
from dynamics import apply_traffic, close_road, route_with_turn_penalties

def run_cli():
    print("=" * 60)
    print("      OPTIMAPATH AI - INTELLIGENT ROUTE PLANNER CLI      ")
    print("=" * 60)
    
    # Load default data
    try:
        G = load_graph("roads.csv")
        print(f"Graph loaded successfully: {G.number_of_nodes()} Nodes, {G.number_of_edges()} Edges.")
    except FileNotFoundError:
        print("Error: roads.csv not found! Run 'python data_builder.py' first.")
        sys.exit(1)
        
    print("\nAvailable Nodes:", sorted(list(G.nodes())))
    
    src = input("Enter Source Node (e.g. N0_0): ").strip()
    dst = input("Enter Destination Node (e.g. N5_5): ").strip()
    
    if src not in G or dst not in G:
        print("Error: Source or Destination node not valid!")
        sys.exit(1)
        
    print("\nChoose Optimization Objective:")
    print("1. Fastest Route (Time Optimization)")
    print("2. Shortest Route (Distance Optimization)")
    print("3. Cheapest Route (Tolls Avoidance)")
    print("4. Eco-Friendly Route (Emission Optimization)")
    print("5. Weighted Hybrid (Multi-Criteria)")
    
    choice = input("Enter choice (1-5): ").strip()
    
    objective = "time"
    if choice == "2":
        objective = "distance"
    elif choice == "3":
        objective = "money"
    elif choice == "4":
        objective = "eco"
    elif choice == "5":
        objective = "weighted"
        
    # Option for turn penalties
    turns_choice = input("Apply Turn Penalties? (y/n): ").strip().lower()
    apply_turns = turns_choice == 'y'
    
    # Option for traffic simulation
    traffic_choice = input("Simulate high-traffic on Row 3? (y/n): ").strip().lower()
    if traffic_choice == 'y':
        # Apply congestion on row 3 horizontal links
        traffic_edges = []
        for j in range(5):
            traffic_edges.append((f"N3_{j}", f"N3_{j+1}"))
            traffic_edges.append((f"N3_{j+1}", f"N3_{j}"))
        apply_traffic(G, traffic_edges, factor=2.5)
        print("Dynamic constraint applied: 2.5x traffic slowdown on expressway row 3.")

    print("\nComputing Route...")
    try:
        if apply_turns:
            cost_map = {"time": time_cost, "distance": distance_cost, "money": money_cost, "eco": eco_cost}
            cfn = cost_map.get(objective, time_cost)
            path = route_with_turn_penalties(G, src, dst, cfn, turn_penalty_sec=20.0)
        elif objective == "weighted":
            print("Weighted Formula: cost = 1.0 * time_sec + 0.01 * distance_m + 10.0 * tolls")
            path = route_weighted(G, src, dst, alpha=1.0, beta=0.01, gamma=10.0)
        else:
            path = shortest_path(G, src, dst, objective)
            
        tot_time = path_cost(G, path, time_cost)
        tot_dist = path_cost(G, path, distance_cost)
        tot_tolls = path_cost(G, path, money_cost)
        
        print("\n" + "="*45)
        print("               OPTIMIZED ROUTE SUMMARY               ")
        print("="*45)
        print(f"Origin Node      : {src}")
        print(f"Destination Node : {dst}")
        print(f"Route Path Node sequence:")
        print("  ➔  ".join(path))
        print("-" * 45)
        print(f"Estimated Travel Duration : {round(tot_time, 2)} seconds")
        print(f"Total Traversal Distance  : {round(tot_dist, 2)} meters")
        print(f"Encountered Tolls Gates   : {int(tot_tolls)} gates")
        print("="*45)
        
    except Exception as e:
        print(f"Error computing route: {str(e)}")

def run_server():
    import uvicorn
    print("Starting OptimaPath AI Web Server on http://127.0.0.1:8080 ...")
    uvicorn.run("app:app", host="127.0.0.1", port=8080, reload=True)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="OptimaPath AI CLI / Server Runner")
    parser.add_argument("--mode", choices=["cli", "server"], default="cli", help="Select UI entrypoint")
    args = parser.parse_args()
    
    if args.mode == "server":
        run_server()
    else:
        run_cli()
