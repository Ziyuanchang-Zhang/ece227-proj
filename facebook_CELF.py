import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import random
from collections import defaultdict, deque
import heapq

# === Parameter Configuration ===
input_file = "facebook_combined.txt"
p = 0.1
num_seeds = 40 # 10, 20, 30
steps = 1000  # Number of repetitions for each IC simulation

# === Step 1: Build the graph (bidirectional edges, directed graph) ===
print("Loading graph...")
G = nx.DiGraph()
with open(input_file) as f:
    for line in f:
        u, v = map(int, line.strip().split())
        G.add_edge(u, v, weight=p)
        G.add_edge(v, u, weight=p)
print(f"Graph loaded. Nodes: {G.number_of_nodes()}, Edges: {G.number_of_edges()}")

# === Step 2: Define the Independent Cascade (IC) model ===
def run_ic_once(G, seeds, p=0.1):
    activated = set(seeds)
    frontier = set(seeds)
    while frontier:
        new_frontier = set()
        for u in frontier:
            for v in G.successors(u):
                if v not in activated and random.random() <= G[u][v].get('weight', p):
                    activated.add(v)
                    new_frontier.add(v)
        frontier = new_frontier
    return activated

def run_ic(G, seeds, p=0.1, steps=20):
    return np.mean([len(run_ic_once(G, seeds, p)) for _ in range(steps)])

# === Step 3: Implement CELF ===
def celf(G, k, p=0.1, steps=20):
    queue = []
    for node in G.nodes():
        spread = run_ic(G, [node], p=p, steps=steps)
        heapq.heappush(queue, (-spread, node, 0))  # (negative_gain, node, last_updated)

    selected = []
    spread_cache = {}
    round_num = 0

    while len(selected) < k:
        neg_gain, node, last_updated = heapq.heappop(queue)
        if last_updated == round_num:
            selected.append(node)
            spread_cache[node] = -neg_gain
            round_num += 1
            print(f"[{round_num}/{k}] Selected: {node}, Marginal Gain: {-neg_gain:.2f}")
        else:
            spread = run_ic(G, selected + [node], p=p, steps=steps)
            new_gain = spread - sum(spread_cache.values())
            heapq.heappush(queue, (-new_gain, node, round_num))

    return selected

# === Step 4: Run CELF and evaluate ===
print("\nRunning CELF...")
seeds = celf(G, k=num_seeds, p=p, steps=steps)
avg_spread = run_ic(G, seeds, p=p, steps=steps)
coverage = avg_spread / G.number_of_nodes() * 100

print("\nCELF result")
print(f"Seeds: {seeds}")
print(f"Avg Infected: {avg_spread:.2f} / {G.number_of_nodes()}")
print(f"Coverage: {coverage:.2f}%")



'''
Result:
Loading graph...
Graph loaded. Nodes: 4039, Edges: 176468

Running CELF...
[1/40] Selected: 2200, Marginal Gain: 2986.30
[2/40] Selected: 827, Marginal Gain: 65.85
[3/40] Selected: 4023, Marginal Gain: 11.25
[4/40] Selected: 3988, Marginal Gain: -6.25
[5/40] Selected: 1656, Marginal Gain: 2.00
[6/40] Selected: 763, Marginal Gain: -5.25
[7/40] Selected: 3896, Marginal Gain: -1.45
[8/40] Selected: 885, Marginal Gain: -6.10
[9/40] Selected: 830, Marginal Gain: 0.95
[10/40] Selected: 176, Marginal Gain: 10.50
[11/40] Selected: 3440, Marginal Gain: 5.40
[12/40] Selected: 4014, Marginal Gain: 3.35
[13/40] Selected: 820, Marginal Gain: -5.60
[14/40] Selected: 1612, Marginal Gain: -8.45
[15/40] Selected: 2595, Marginal Gain: 18.95
[16/40] Selected: 793, Marginal Gain: -13.75
[17/40] Selected: 766, Marginal Gain: -12.80
[18/40] Selected: 814, Marginal Gain: 17.90
[19/40] Selected: 789, Marginal Gain: -0.95
[20/40] Selected: 3751, Marginal Gain: -2.20
[21/40] Selected: 337, Marginal Gain: 22.10
[22/40] Selected: 686, Marginal Gain: -7.65
[23/40] Selected: 737, Marginal Gain: 0.15
[24/40] Selected: 757, Marginal Gain: -5.95
[25/40] Selected: 713, Marginal Gain: -4.65
[26/40] Selected: 818, Marginal Gain: 3.65
[27/40] Selected: 769, Marginal Gain: 6.05
[28/40] Selected: 4010, Marginal Gain: -1.05
[29/40] Selected: 1899, Marginal Gain: -16.45
[30/40] Selected: 149, Marginal Gain: 19.15
[31/40] Selected: 887, Marginal Gain: 6.20
[32/40] Selected: 1942, Marginal Gain: -9.20
[33/40] Selected: 54, Marginal Gain: -1.45
[34/40] Selected: 1671, Marginal Gain: -4.00
[35/40] Selected: 1699, Marginal Gain: -10.60
[36/40] Selected: 170, Marginal Gain: 21.95
[37/40] Selected: 712, Marginal Gain: -2.60
[38/40] Selected: 1147, Marginal Gain: 5.10
[39/40] Selected: 126, Marginal Gain: -12.35
[40/40] Selected: 765, Marginal Gain: 1.85

 CELF result
Seeds: [2200, 827, 4023, 3988, 1656, 763, 3896, 885, 830, 176, 3440, 4014, 820, 1612, 2595, 793, 766, 814, 789, 3751, 337, 686, 737, 757, 713, 818, 769, 4010, 1899, 149, 887, 1942, 54, 1671, 1699, 170, 712, 1147, 126, 765]
Avg Infected: 3077.70 / 4039
Coverage: 76.20%
'''
