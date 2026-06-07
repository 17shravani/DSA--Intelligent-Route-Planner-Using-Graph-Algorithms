# data_builder.py
import csv
import math

def write_grid(n=6, spacing_m=300):
    """
    Generates a synthetic city grid map data of n x n intersection nodes.
    Each intersection node coordinates are computed with small offsets from Bangalore center coordinates.
    Saves output to roads.csv.
    """
    rows = []
    node_id = lambda i, j: f"N{i}_{j}"
    coords = {}
    
    # Let's anchor the city center (e.g. Bangalore center: Lat 12.9716, Lon 77.5946)
    base_lat, base_lon = 12.9716, 77.5946
    
    for i in range(n):
        for j in range(n):
            # 0.0025 degree is roughly 275 meters
            lat = base_lat + i * 0.0025
            lon = base_lon + j * 0.0025
            coords[node_id(i, j)] = (lat, lon)
            
    def add_road(u, v, dist, speed, toll, one_way, cls):
        lat_u, lon_u = coords[u]
        lat_v, lon_v = coords[v]
        rows.append([u, v, lat_u, lon_u, lat_v, lon_v, dist, speed, toll, one_way, cls])

    # Build bidirectional roads on grid edges
    for i in range(n):
        for j in range(n):
            # Horizontal connections
            if j + 1 < n:
                u = node_id(i, j)
                v = node_id(i, j+1)
                # Normal residential road
                add_road(u, v, spacing_m, 40, 0, 0, "residential")
                add_road(v, u, spacing_m, 40, 0, 0, "residential")
            
            # Vertical connections
            if i + 1 < n:
                u = node_id(i, j)
                v = node_id(i+1, j)
                add_road(u, v, spacing_m, 35, 0, 0, "residential")
                add_road(v, u, spacing_m, 35, 0, 0, "residential")

    # Add a high-speed express arterial avenue with toll along row index 3
    for j in range(n - 1):
        u = node_id(3, j)
        v = node_id(3, j+1)
        add_road(u, v, spacing_m, 80, 2, 0, "primary")  # 2 toll units
        add_road(v, u, spacing_m, 80, 2, 0, "primary")

    # Add a diagonal link acting as a one-way high-speed shortcut
    # Connects N0_0 directly to N2_2
    add_road(node_id(0, 0), node_id(2, 2), spacing_m * 2.8, 60, 0, 1, "link")
    
    # Connect N1_4 directly to N4_1 as a fast ring-road segment
    add_road(node_id(1, 4), node_id(4, 1), spacing_m * 3.5, 70, 1, 0, "secondary")
    add_road(node_id(4, 1), node_id(1, 4), spacing_m * 3.5, 70, 1, 0, "secondary")

    with open("roads.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow("u,v,lat_u,lon_u,lat_v,lon_v,distance_m,speed_kph,toll,one_way,road_class".split(","))
        w.writerows(rows)
    print("roads.csv written with synthetic city grid topology.")

if __name__ == "__main__":
    write_grid()
