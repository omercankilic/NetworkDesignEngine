# ACYCLIC DIGRAPH GENERATION
import networkx as nx
import random
import matplotlib.pyplot as plt
import tkinter as tk

unit_cost_per_hop = 0.5  # for each hop in a path costs
nodeCounts = []
testNumberForNodeCount = 3
edgeAddingRate = 0.75


class EdgeCostObj:
    def __init__(self, edgeItself, capacity):
        self.edge = edgeItself
        self.capacity = capacity
        self.pathAndBandwidth = []


def select_random_and_remove(myList):
    if myList:
        random_item = random.choice(myList)
        myList.remove(random_item)
        return random_item
    else:
        return None


def getTestNodeCounts():
    def process_input():
        input_text = entry.get()
        integers = [int(x) for x in input_text.split(",")]
        nodeCounts.extend(integers)
        window.destroy()

    # Create the main window
    window = tk.Tk()
    window.title("List of node counts")

    # Create a label
    label = tk.Label(window, text="Enter a list of node counts:")
    label.pack(pady=10)

    # Create an entry field for input
    entry = tk.Entry(window, width=40)
    entry.pack(padx=10, pady=5)

    # Create a button to process the input
    button = tk.Button(window, text="Submit", command=process_input)
    button.pack(pady=10)

    # Run the GUI main loop
    window.mainloop()


def sortCostList(costList):
    id = 0
    sortedCostList = []
    for i in costList:
        sortedCostList.append((id, i))
        id = id + 1
    sortedCostList = sorted(sortedCostList, key=lambda x: x[1])
    return sortedCostList


def over_capacity_assignment(paths):
    overCapacityPercentages = []
    for i in paths:
        overCapacityPercentages.append(40)  # random.randint(40, 60))
    return overCapacityPercentages


def define_cost_for_path(paths):
    path_costs = []
    for path in paths:
        path_costs.append(len(path) * unit_cost_per_hop)
    return path_costs


def sumListElements(sumList):
    total = 0
    for i in sumList:
        total = total + i

    return total


def find_all_paths(G):
    # Find all simple paths from node 0 to node n
    all_paths = list(nx.all_simple_paths(G, source=0, target=G.number_of_nodes() - 1))
    # for path in all_paths:
    #     print(str(len(path)) + '\n')
    return all_paths


def generate_flow_demands(G):
    # Generate random flow demands for each path from node 0 to node n-1
    flow_demands = []
    all_paths = list(nx.all_simple_paths(G, source=0, target=G.number_of_nodes() - 1))
    for path in all_paths:
        # Determine the lowest capacity link in the path
        min_capacity = min(G[u][v]["capacity"] for u, v in zip(path, path[1:]))
        # Generate a random flow demand between 1 and the lowest capacity link
        flow_demand = random.randint(1, min_capacity)
        # flow_demands[tuple(path)] = flow_demand
        flow_demands.append(flow_demand)
    return flow_demands


def generate_random_dag(n):
    # Create an empty DAG
    G = nx.DiGraph()

    # Add nodes to the DAG
    for i in range(n):
        G.add_node(i)

    # Add edges to the DAG
    for i in range(n - 1):
        for j in range(i + 1, n):
            if random.random() < edgeAddingRate:
                capacity = random.randint((n - 1) / 2 * n + 100, (n - 1) / 2 * n + 200)
                G.add_edge(i, j, capacity=capacity)

    # Ensure that there is at least one path from node 0 to node n
    if not nx.has_path(G, 0, n - 1):
        return generate_random_dag(n)

    # Ensure that the DAG has no cycles
    try:
        cycle = nx.find_cycle(G)
        return generate_random_dag(n)
    except nx.NetworkXNoCycle:
        return G


nodeResultsCheap = []
nodeResultsMidCase = []
nodeResultsExpensive = []
nodeResultsRandom = []
# Tests will be run for a number of node counts.
# We are getting the a list of integer as node counts from user.
getTestNodeCounts()

# It takes long time for calculations with more than
# 30 nodes. So, we remove it from the list.
for nodeC in nodeCounts:
    if nodeC > 30 | nodeC <= 0:
        nodeCounts.remove(nodeC)

# open file to write data

if len(nodeCounts) >= 1:
    file = open("Note.txt", "w")
    for nodeCount in nodeCounts:
        tempCheap = []
        tempMid = []
        tempRand = []
        tempExp = []
        for m in range(0, testNumberForNodeCount):
            # Generate a random DAG with 10 nodes
            G = generate_random_dag(nodeCount)

            # Find all paths from node 0 to node n
            allPaths = find_all_paths(G)

            # over bandwidth assignment percentage rates.
            overCapacityPercentages = over_capacity_assignment(allPaths)

            # Determining the path costs
            pathCosts = define_cost_for_path(allPaths)

            # sorted path cost list
            sortedCostList = sortCostList(pathCosts)

            # Generate Flow Demands
            flowDemands = generate_flow_demands(G)

            # getting all edges
            edgesInGraph = []
            for edge in G.edges():
                x = EdgeCostObj(edge, G.get_edge_data(edge[0], edge[1])["capacity"])
                j = 0
                for path in allPaths:
                    if any(
                        edge == (path[i], path[i + 1]) for i in range(len(path) - 1)
                    ):
                        # (path id, assigned banwidth, flow demand, cost of assigning a unit of bandwidth,expensive cost assignment,random cost assignment)
                        x.pathAndBandwidth.append(
                            [j, 0, flowDemands[j], pathCosts[j], 0, 0, 0]
                        )
                    j = j + 1
                edgesInGraph.append(x)

            # assign bandwidth to edges efficiently.
            for edgeObj in edgesInGraph:
                if len(edgeObj.pathAndBandwidth) > 0:
                    tempBw = edgeObj.capacity / len(edgeObj.pathAndBandwidth)
                    totalBwAssigned = 0
                    # Assigning bandwidth
                    for bw in edgeObj.pathAndBandwidth:
                        if bw[2] <= tempBw:
                            bw[1] = bw[2]
                            bw[4] = bw[2]
                            bw[6] = bw[2]
                            totalBwAssigned = totalBwAssigned + bw[2]
                        else:
                            bw[1] = tempBw
                            bw[4] = tempBw
                            bw[6] = tempBw
                            totalBwAssigned = totalBwAssigned + tempBw
                    # if there is available capacity not assigned, assign this capacity
                    # to path without passing the limits.
                    remainedCapacity = 0
                    if totalBwAssigned < edgeObj.capacity:
                        remainedCapacity = edgeObj.capacity - totalBwAssigned
                        # allocate remained capacity to the cheapest paths.
                        # find the cheapest path.
                        for cheapest in sortedCostList:
                            for pathOfEdge in edgeObj.pathAndBandwidth:
                                if pathOfEdge[0] == cheapest[0]:
                                    limit = pathOfEdge[2] + (
                                        pathOfEdge[2]
                                        * (overCapacityPercentages[pathOfEdge[0]] / 100)
                                    )
                                    if (limit - pathOfEdge[1]) >= remainedCapacity:
                                        pathOfEdge[1] = pathOfEdge[1] + remainedCapacity
                                        remainedCapacity = 0
                                        break
                                    else:
                                        remainedCapacity = remainedCapacity - (
                                            limit - pathOfEdge[1]
                                        )
                                        pathOfEdge[1] = limit

                                if remainedCapacity <= 0:
                                    break
                            if remainedCapacity <= 0:
                                break

                    # Calculate Mid Case
                    if totalBwAssigned < edgeObj.capacity:
                        remainedCapacity = edgeObj.capacity - totalBwAssigned
                        # allocate remained capacity to the most expensive path
                        for midExpensive in list(reversed(sortedCostList)):
                            for pathOfEdge in edgeObj.pathAndBandwidth:
                                if pathOfEdge[0] == midExpensive[0]:
                                    limit = pathOfEdge[2] + (
                                        pathOfEdge[2]
                                        * (overCapacityPercentages[pathOfEdge[0]] / 100)
                                    )
                                    if (limit - pathOfEdge[4]) >= remainedCapacity:
                                        pathOfEdge[4] = pathOfEdge[4] + remainedCapacity
                                        remainedCapacity = 0
                                        break
                                    else:
                                        remainedCapacity = remainedCapacity - (
                                            limit - pathOfEdge[4]
                                        )
                                        pathOfEdge[4] = limit
                                if remainedCapacity <= 0:
                                    break
                            if remainedCapacity <= 0:
                                break

                    if totalBwAssigned < edgeObj.capacity:
                        remainedCapacity = edgeObj.capacity - totalBwAssigned
                        # allocate remained capacity randomly
                        tempCostList = list(sortedCostList)
                        randomChoice = random.choice(tempCostList)
                        while randomChoice != None:
                            tempCostList.remove(randomChoice)
                            for pathOfEdge in edgeObj.pathAndBandwidth:
                                if pathOfEdge[0] == randomChoice[0]:
                                    limit = pathOfEdge[2] + (
                                        pathOfEdge[2]
                                        * (overCapacityPercentages[pathOfEdge[0]] / 100)
                                    )
                                    if (limit - pathOfEdge[6]) >= remainedCapacity:
                                        pathOfEdge[6] = pathOfEdge[6] + remainedCapacity
                                        remainedCapacity = 0
                                        break
                                    else:
                                        remainedCapacity = remainedCapacity - (
                                            limit - pathOfEdge[6]
                                        )
                                        pathOfEdge[6] = limit
                                if remainedCapacity <= 0:
                                    break
                            if remainedCapacity <= 0:
                                break

                            if len(tempCostList) >= 1:
                                randomChoice = random.choice(tempCostList)
                            else:
                                break
                    # Calculate Worst case: Most expensive scenario
                    remainedCapacity = edgeObj.capacity
                    for expensive in list(reversed(sortedCostList)):
                        for pathOfEdge in edgeObj.pathAndBandwidth:
                            if pathOfEdge[0] == expensive[0]:
                                limit = (
                                    pathOfEdge[2]
                                    + (
                                        pathOfEdge[2]
                                        * (overCapacityPercentages[pathOfEdge[0]])
                                    )
                                    / 100
                                )
                                if limit - pathOfEdge[5] >= remainedCapacity:
                                    pathOfEdge[5] = pathOfEdge[5] + remainedCapacity
                                    remainedCapacity = 0
                                    break
                                else:
                                    remainedCapacity = remainedCapacity - (
                                        limit - pathOfEdge[5]
                                    )
                                    pathOfEdge[5] = limit
                            if remainedCapacity <= 0:
                                break
                        if remainedCapacity <= 0:
                            break

            totalCostCheapest = 0
            totalCostMidCase = 0
            totalCostRandom = 0
            totalCostExpensive = 0
            # Calculate the cheapest case for the edges
            for edgeObj in edgesInGraph:
                for pathEdge in edgeObj.pathAndBandwidth:
                    # if the bandwidth allocation for this path is larger than demand
                    # we add it to the total cost. Otherwise, it is not calculated as total cost.
                    if pathEdge[1] - pathEdge[2] > 0:
                        totalCostCheapest = totalCostCheapest + pathCosts[
                            pathEdge[0]
                        ] * (pathEdge[1] - pathEdge[2])

            # Calculate the mid algorithm cost for the edge
            for edgeObj in edgesInGraph:
                for pathEdge in edgeObj.pathAndBandwidth:
                    if pathEdge[4] - pathEdge[2] > 0:
                        totalCostMidCase = totalCostMidCase + pathCosts[pathEdge[0]] * (
                            pathEdge[4] - pathEdge[2]
                        )

            # Calculating the cost for the worst case scenario.
            # In this scenario there may be unused links.
            for edgeObj in edgesInGraph:
                for pathEdge in edgeObj.pathAndBandwidth:
                    if pathEdge[5] - pathEdge[2] > 0:
                        totalCostExpensive = totalCostExpensive + pathCosts[
                            pathEdge[0]
                        ] * (pathEdge[5] - pathEdge[2])

            # Calculating the cost for the random case.
            for edgeObj in edgesInGraph:
                for pathEdge in edgeObj.pathAndBandwidth:
                    if pathEdge[6] - pathEdge[2] > 0:
                        totalCostRandom = totalCostRandom + pathCosts[pathEdge[0]] * (
                            pathEdge[6] - pathEdge[2]
                        )

            # We are pushing the extra bandwidth allocation values to the list.
            tempCheap.append(totalCostCheapest)
            tempMid.append(totalCostMidCase)
            tempExp.append(totalCostExpensive)
            tempRand.append(totalCostRandom)

        cheapT = sumListElements(tempCheap) / testNumberForNodeCount
        midT = sumListElements(tempMid) / testNumberForNodeCount
        expT = sumListElements(tempExp) / testNumberForNodeCount
        randT = sumListElements(tempRand) / testNumberForNodeCount

        file.write("Node Count : " + str(nodeCount) + "\n")
        file.write("Heuristic: " + str(cheapT) + " $" + "\n")
        file.write("MidCase  : " + str(midT) + " $" + "\n")
        file.write("Expensive: " + str(expT) + " $" + "\n")
        file.write("Random   : " + str(randT) + " $" + "\n\n")
        # adding results for this node count to list
        nodeResultsCheap.append(cheapT)
        nodeResultsMidCase.append(midT)
        nodeResultsExpensive.append(expT)
        nodeResultsRandom.append(randT)

    file.close()
    width = 1
    indices = list(range(len(nodeResultsCheap)))
    randomCaseFigure = plt.figure()
    plt.title("Random case cost")
    plt.xticks(indices, nodeCounts)
    plt.bar(
        [i * width for i in indices],
        nodeResultsRandom,
        width,
        color="red",
        label="Random Case",
    )

    heuristicFigure = plt.figure()
    plt.title("Heuristic Case Cost")
    plt.xticks(indices, nodeCounts)
    plt.bar(
        [i * width for i in indices],
        nodeResultsCheap,
        width,
        color="skyblue",
        label="My Heuristic",
    )

    midCaseFigure = plt.figure()
    plt.title("Mid Case Cost")
    plt.xticks(indices, nodeCounts)
    plt.bar(
        [i * width for i in indices],
        nodeResultsMidCase,
        width,
        color="orange",
        label="Mid Case",
    )

    worstCaseFigure = plt.figure()
    plt.title("Worst Case Cost")
    plt.xticks(indices, nodeCounts)
    plt.bar(
        [i * width for i in indices],
        nodeResultsExpensive,
        width,
        color="blue",
        label="Worst Case",
    )
    # Adding Label
    plt.xlabel("Node Counts")
    plt.ylabel("Calculated Cost")

    plt.legend()
    plt.show()
