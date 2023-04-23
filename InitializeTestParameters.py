
# ACYCLIC DIGRAPH GENERATION
import networkx as nx
import random
import matplotlib.pyplot as plt

def find_all_paths(G):
    # Find all simple paths from node 0 to node n
    all_paths = list(nx.all_simple_paths(G, source=0, target=G.number_of_nodes()-1))

    return all_paths

def generate_flow_demands(G):
    # Generate random flow demands for each path from node 0 to node n-1
    flow_demands = {}
    all_paths = list(nx.all_simple_paths(G, source=0, target=G.number_of_nodes()-1))
    for path in all_paths:
        # Determine the lowest capacity link in the path
        min_capacity = min(G[u][v]['capacity'] for u, v in zip(path, path[1:]))
        # Generate a random flow demand between 1 and the lowest capacity link
        flow_demand = random.randint(1, min_capacity)
        flow_demands[tuple(path)] = flow_demand

    return flow_demands

def generate_random_dag(n):
    # Create an empty DAG
    G = nx.DiGraph()

    # Add nodes to the DAG
    for i in range(n):
        G.add_node(i)

    # Add edges to the DAG
    for i in range(n-1):
        for j in range(i+1, n):
            if random.random() < 0.5:
                capacity = random.randint(20, 30)
                print('cap '+str(capacity))
                G.add_edge(i, j,capacity=capacity)

    # Ensure that there is at least one path from node 0 to node n
    if not nx.has_path(G, 0, n-1):
        return generate_random_dag(n)

    # Ensure that the DAG has no cycles
    try:
        cycle = nx.find_cycle(G)
        return generate_random_dag(n)
    except nx.NetworkXNoCycle:
        return G

# Generate a random DAG with 10 nodes
G = generate_random_dag(5)

# Find all paths from node 0 to node n
all_paths = find_all_paths(G)

# Generate Flow Demands
flow_demands = generate_flow_demands(G)

print("Flow demands:")
for path, flow_demand in flow_demands.items():
    print("Path: {}, Flow demand: {}".format(path, flow_demand))

# # Print the results
# print("All paths from node 0 to node n:")
# for path in all_paths:
#     print(path)

# Plot the DAG
nx.draw(G, with_labels=True)
plt.show()

