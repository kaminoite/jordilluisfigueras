"""
 * smallWorldWattsStrogatz.py
 *
 * Copyright (c) 2026, Jordi-Lluis Figueras
 *
 * OpenAI Codex / ChatGPT 5.5 has been used in the editing of this file.
 *
"""

"""Explore clustering and path lengths in Watts-Strogatz networks.

Usage:
  python3 smallWorldWattsStrogatz.py
  python3 smallWorldWattsStrogatz.py --nodes 100 --neighbors 4 --trials 30
  python3 smallWorldWattsStrogatz.py --probabilities 0 0.01 0.05 0.1 0.5 1

The script prints average statistics over several random trials. The small-world
effect is visible when a small rewiring probability greatly reduces path length
while clustering remains relatively high.
"""

import argparse
import statistics

try:
  import networkx as nx
except ImportError as error:
  raise SystemExit(
    "This script requires NetworkX. On Debian/Ubuntu, use a virtual environment:\n"
    "  python3 -m venv .venv\n"
    "  source .venv/bin/activate\n"
    "  python3 -m pip install networkx"
  ) from error


defaultNodes = 60
defaultNeighbors = 4
defaultTrials = 20
defaultSeed = 2026
defaultProbabilities = [0.0, 0.01, 0.03, 0.05, 0.10, 0.30, 1.0]


def parseArguments():
  parser = argparse.ArgumentParser(description = "Explore the Watts-Strogatz small-world model")
  parser.add_argument("--nodes", type = int, default = defaultNodes, help = "number of nodes")
  parser.add_argument("--neighbors", type = int, default = defaultNeighbors, help = "number of ring neighbors per node")
  parser.add_argument("--trials", type = int, default = defaultTrials, help = "number of random trials per probability")
  parser.add_argument("--seed", type = int, default = defaultSeed, help = "base random seed")
  parser.add_argument(
    "--probabilities",
    nargs = "+",
    type = float,
    default = defaultProbabilities,
    help = "rewiring probabilities to test",
  )
  parser.add_argument("--decimals", type = int, default = 4, help = "number of decimals in printed statistics")
  args = parser.parse_args()

  if args.nodes <= 2:
    parser.error("--nodes must be larger than 2")

  if args.neighbors <= 0:
    parser.error("--neighbors must be positive")

  if args.neighbors >= args.nodes:
    parser.error("--neighbors must be smaller than --nodes")

  if args.neighbors % 2 != 0:
    parser.error("--neighbors must be even for the Watts-Strogatz ring construction")

  if args.trials <= 0:
    parser.error("--trials must be positive")

  if args.decimals < 0:
    parser.error("--decimals must be nonnegative")

  for probability in args.probabilities:
    if probability < 0 or probability > 1:
      parser.error("each rewiring probability must satisfy 0 <= p <= 1")

  return args


def largestConnectedSubgraph(graph):
  if nx.is_connected(graph):
    return graph, 1.0

  largestComponent = max(nx.connected_components(graph), key = len)
  componentFraction = len(largestComponent) / graph.number_of_nodes()
  return graph.subgraph(largestComponent).copy(), componentFraction


def computeTrialStatistics(nNodes, nNeighbors, probability, seed):
  graph = nx.watts_strogatz_graph(nNodes, nNeighbors, probability, seed = seed)
  connectedGraph, componentFraction = largestConnectedSubgraph(graph)
  return {
    "clustering": nx.average_clustering(graph),
    "pathLength": nx.average_shortest_path_length(connectedGraph),
    "diameter": nx.diameter(connectedGraph),
    "componentFraction": componentFraction,
  }


def meanStatistic(statisticsList, key):
  return statistics.mean(item[key] for item in statisticsList)


def printHeader(args):
  print("Watts-Strogatz small-world experiment")
  print(f"  nodes: {args.nodes}")
  print(f"  neighbors per node in initial ring: {args.neighbors}")
  print(f"  trials per probability: {args.trials}")
  print()
  print("p        clustering   path length   diameter   largest component")
  print("---------------------------------------------------------------")


def printStatisticsRow(probability, statisticsList, decimals):
  clustering = meanStatistic(statisticsList, "clustering")
  pathLength = meanStatistic(statisticsList, "pathLength")
  diameter = meanStatistic(statisticsList, "diameter")
  componentFraction = meanStatistic(statisticsList, "componentFraction")
  print(
    f"{probability:<8.3g} "
    f"{clustering:>10.{decimals}f} "
    f"{pathLength:>13.{decimals}f} "
    f"{diameter:>10.{decimals}f} "
    f"{componentFraction:>18.{decimals}f}"
  )


def printInterpretation():
  print("\nInterpretation:")
  print("  For p = 0 the graph is highly clustered but distances are relatively long.")
  print("  For small positive p, shortcuts usually reduce distances faster than they destroy clustering.")
  print("  For p close to 1, the graph behaves more like a random graph: short paths, lower clustering.")


def main():
  args = parseArguments()
  printHeader(args)

  for probabilityIndex, probability in enumerate(args.probabilities):
    statisticsList = []
    for trial in range(args.trials):
      seed = args.seed + 1000 * probabilityIndex + trial
      trialStatistics = computeTrialStatistics(args.nodes, args.neighbors, probability, seed)
      statisticsList.append(trialStatistics)

    printStatisticsRow(probability, statisticsList, args.decimals)

  printInterpretation()


if __name__ == "__main__":
  main()
