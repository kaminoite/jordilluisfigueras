"""
 * pagerankDampingExample.py
 *
 * Copyright (c) 2026, Jordi-Lluis Figueras
 *
 * OpenAI Codex / ChatGPT 5.5 has been used in the editing of this file.
 *
"""

"""Compute damped PageRank on the Lecture 11 four-page example.

Usage:
  python3 pagerankDampingExample.py
  python3 pagerankDampingExample.py --alpha 0.85 0.50 0.95
  python3 pagerankDampingExample.py --iterations 100 --tol 1e-12

The graph is the directed graph from Lecture 11:
  B -> A, B -> C, C -> A, D -> A, D -> B, D -> C,
with A as a dangling page.

The script uses NetworkX to store the directed graph, but implements the
dangling-node correction and damping iteration explicitly so that the update is
visible.
"""

import argparse

try:
  import networkx as nx
except ImportError as error:
  raise SystemExit(
    "This script requires NetworkX. On Debian/Ubuntu, use a virtual environment:\n"
    "  python3 -m venv .venv\n"
    "  source .venv/bin/activate\n"
    "  python3 -m pip install networkx"
  ) from error


defaultAlphaValues = [0.85]
defaultIterations = 100
defaultTolerance = 1e-12
nodeOrder = ["A", "B", "C", "D"]


def parseArguments():
  parser = argparse.ArgumentParser(description = "Compute damped PageRank on the Lecture 11 graph")
  parser.add_argument(
    "--alpha",
    nargs = "+",
    type = float,
    default = defaultAlphaValues,
    help = "damping factor values; NetworkX calls this parameter alpha",
  )
  parser.add_argument("--iterations", type = int, default = defaultIterations, help = "maximum number of iterations")
  parser.add_argument("--tol", type = float, default = defaultTolerance, help = "L1 convergence tolerance")
  parser.add_argument("--decimals", type = int, default = 6, help = "number of decimals in printed scores")
  args = parser.parse_args()

  if args.iterations <= 0:
    parser.error("--iterations must be positive")

  if args.tol <= 0:
    parser.error("--tol must be positive")

  if args.decimals < 0:
    parser.error("--decimals must be nonnegative")

  for alpha in args.alpha:
    if alpha <= 0 or alpha >= 1:
      parser.error("each --alpha value must satisfy 0 < alpha < 1")

  return args


def buildLectureGraph():
  graph = nx.DiGraph()
  graph.add_nodes_from(nodeOrder)
  graph.add_edges_from(
    [
      ("B", "A"),
      ("B", "C"),
      ("C", "A"),
      ("D", "A"),
      ("D", "B"),
      ("D", "C"),
    ]
  )
  return graph


def dampedPageRank(graph, alpha, maxIterations, tolerance):
  nodes = list(nodeOrder)
  nNodes = len(nodes)
  ranks = {node: 1.0 / nNodes for node in nodes}

  for step in range(1, maxIterations + 1):
    nextRanks = {node: (1.0 - alpha) / nNodes for node in nodes}
    danglingMass = sum(ranks[node] for node in nodes if graph.out_degree(node) == 0)

    for node in nodes:
      nextRanks[node] += alpha * danglingMass / nNodes

    for source in nodes:
      successors = list(graph.successors(source))
      if len(successors) == 0:
        continue

      contribution = alpha * ranks[source] / len(successors)
      for target in successors:
        nextRanks[target] += contribution

    error = sum(abs(nextRanks[node] - ranks[node]) for node in nodes)
    ranks = nextRanks

    if error < tolerance:
      return ranks, step, error

  return ranks, maxIterations, error


def formatRankTable(ranks, decimals):
  ordered = sorted(ranks.items(), key = lambda item: (-item[1], item[0]))
  for position, (node, score) in enumerate(ordered, start = 1):
    print(f"  {position}. {node}: {score:.{decimals}f}")


def printGraphSummary(graph):
  print("Directed graph from Lecture 11:")
  for node in nodeOrder:
    successors = list(graph.successors(node))
    if successors:
      print(f"  {node} -> {', '.join(successors)}")
    else:
      print(f"  {node} -> dangling page")

  danglingNodes = [node for node in nodeOrder if graph.out_degree(node) == 0]
  print(f"\nDangling nodes: {', '.join(danglingNodes)}")


def main():
  args = parseArguments()
  graph = buildLectureGraph()

  printGraphSummary(graph)

  for alpha in args.alpha:
    ranks, nIterations, error = dampedPageRank(graph, alpha, args.iterations, args.tol)
    print(f"\nDamped PageRank with alpha = {alpha:.4f}:")
    formatRankTable(ranks, args.decimals)
    print(f"  iterations: {nIterations}")
    print(f"  final L1 change: {error:.3e}")
    print(f"  total rank: {sum(ranks.values()):.{args.decimals}f}")


if __name__ == "__main__":
  main()
