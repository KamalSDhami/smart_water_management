import networkx as nx
from collections import deque

def simulate_water_flow(G, source_idx, initial_pressure, flow_rate):
    # BFS traversal on MST
    visited = set()
    queue = deque()
    results = {}
    queue.append((source_idx, 0, initial_pressure))  # (node, time, pressure)
    visited.add(source_idx)
    results[source_idx] = (0, initial_pressure)
    while queue:
        node, time, pressure = queue.popleft()
        for neighbor in G.neighbors(node):
            if neighbor not in visited:
                edge_weight = G[node][neighbor]['weight']
                # Time to reach = distance / flow_rate
                t = time + edge_weight / flow_rate
                # Pressure drop: simple linear drop per unit distance
                p = max(pressure - 0.5 * edge_weight, 0)
                results[neighbor] = (t, p)
                queue.append((neighbor, t, p))
                visited.add(neighbor)
    return results