#!/usr/bin/env python3
"""Sensor-network Vietoris--Rips homology example.

This script accompanies Lecture 15.  It shows two related computations:

1. fixed-scale homology from explicit boundary matrices over Z_2;
2. persistent homology from a Vietoris--Rips filtration using GUDHI.

The default data set is a ring of sensors around a central region.  The central
circle drawn in the figures is a visual guide; the computations use only the
sensor coordinates and pairwise distances.
"""

import argparse
import math
from pathlib import Path

import numpy as np

try:
  import gudhi as gd
except ImportError:
  gd = None


def parseArguments():
  parser = argparse.ArgumentParser(
    description="Compute fixed-scale and persistent H_1 for a sensor ring."
  )
  parser.add_argument(
    "--sensors",
    type=int,
    default=28,
    help="number of sensors in the ring",
  )
  parser.add_argument(
    "--ring-radius",
    type=float,
    default=1.0,
    help="mean radius of the sensor ring",
  )
  parser.add_argument(
    "--hole-radius",
    type=float,
    default=0.45,
    help="radius of the central visual guide",
  )
  parser.add_argument(
    "--coverage-radius",
    type=float,
    default=0.28,
    help="radius of the drawn sensing disks; not used in the VR computation",
  )
  parser.add_argument(
    "--noise",
    type=float,
    default=0.04,
    help="radial and angular jitter of sensor positions",
  )
  parser.add_argument("--seed", type=int, default=0, help="random seed")
  parser.add_argument(
    "--selected-scale",
    type=float,
    default=0.55,
    help="scale used for the fixed homology calculation and graph plot",
  )
  parser.add_argument(
    "--max-edge-length",
    type=float,
    default=1.8,
    help="maximum edge length for the Rips filtration",
  )
  parser.add_argument(
    "--max-dimension",
    type=int,
    default=2,
    help="maximum simplex dimension for the Rips complex",
  )
  parser.add_argument(
    "--simplex-print-limit",
    type=int,
    default=25,
    help="number of filtration simplices printed from GUDHI",
  )
  parser.add_argument(
    "--no-show",
    action="store_true",
    help="do not open interactive plot windows",
  )
  parser.add_argument(
    "--save-dir",
    type=Path,
    default=None,
    help="directory where figures are saved",
  )
  return parser.parse_args()


def generateSensorPoints(sensorCount, ringRadius, noiseLevel, seed):
  if sensorCount < 4:
    raise ValueError("At least four sensors are needed for a ring example.")

  rng = np.random.default_rng(seed)
  theta = np.linspace(0.0, 2.0*math.pi, sensorCount, endpoint=False)
  theta = theta+0.25*noiseLevel*rng.standard_normal(sensorCount)
  radii = ringRadius+noiseLevel*rng.standard_normal(sensorCount)
  points = np.column_stack([radii*np.cos(theta), radii*np.sin(theta)])
  return points


def computeDistanceMatrix(points):
  differences = points[:, None, :]-points[None, :, :]
  return np.linalg.norm(differences, axis=2)


def buildVRSimplicesAtScale(points, scale):
  distances = computeDistanceMatrix(points)
  vertexCount = len(points)
  vertices = list(range(vertexCount))
  edges = []
  triangles = []

  for i in range(vertexCount):
    for j in range(i+1, vertexCount):
      if distances[i, j] <= scale:
        edges.append((i, j))

  edgeSet = set(edges)
  for i in range(vertexCount):
    for j in range(i+1, vertexCount):
      if (i, j) not in edgeSet:
        continue
      for k in range(j+1, vertexCount):
        if (i, k) in edgeSet and (j, k) in edgeSet:
          triangles.append((i, j, k))

  return vertices, edges, triangles


def buildBoundaryMatrices(vertexCount, edges, triangles):
  d1 = np.zeros((vertexCount, len(edges)), dtype=int)
  edgeIndex = {}

  for column, (i, j) in enumerate(edges):
    d1[i, column] = 1
    d1[j, column] = 1
    edgeIndex[(i, j)] = column

  d2 = np.zeros((len(edges), len(triangles)), dtype=int)
  for column, (i, j, k) in enumerate(triangles):
    for edge in ((i, j), (i, k), (j, k)):
      d2[edgeIndex[edge], column] = 1

  return d1, d2


def rankMod2(matrix):
  reduced = matrix.copy()%2
  rowCount, columnCount = reduced.shape
  rank = 0
  row = 0

  for column in range(columnCount):
    pivot = None

    for candidate in range(row, rowCount):
      if reduced[candidate, column] == 1:
        pivot = candidate
        break

    if pivot is None:
      continue

    if pivot != row:
      reduced[[row, pivot]] = reduced[[pivot, row]]

    for candidate in range(rowCount):
      if candidate != row and reduced[candidate, column] == 1:
        reduced[candidate, :] = (reduced[candidate, :]+reduced[row, :])%2

    rank += 1
    row += 1

    if row == rowCount:
      break

  return rank


def computeFixedScaleHomology(points, scale):
  vertices, edges, triangles = buildVRSimplicesAtScale(points, scale)
  d1, d2 = buildBoundaryMatrices(len(vertices), edges, triangles)
  rankD1 = rankMod2(d1)
  rankD2 = rankMod2(d2)

  return {
    "vertices": vertices,
    "edges": edges,
    "triangles": triangles,
    "rankD1": rankD1,
    "rankD2": rankD2,
    "beta0": len(vertices)-rankD1,
    "beta1": len(edges)-rankD1-rankD2,
  }


def printFixedScaleHomology(result, scale):
  print(f"\nFixed-scale Vietoris--Rips complex at r = {scale:.4f}")
  print("  vertices  =", len(result["vertices"]))
  print("  edges     =", len(result["edges"]))
  print("  triangles =", len(result["triangles"]))
  print("  rank d1   =", result["rankD1"])
  print("  rank d2   =", result["rankD2"])
  print("  beta_0    =", result["beta0"])
  print("  beta_1    =", result["beta1"])


def manualBoundaryExamples():
  print("\nManual boundary matrix checks over Z_2")

  d1Path = np.array([
    [1, 0, 0],
    [1, 1, 0],
    [0, 1, 1],
    [0, 0, 1],
  ], dtype=int)

  rankD1Path = rankMod2(d1Path)
  beta1Path = 3-rankD1Path
  print("\nPath graph")
  print("  rank d1 =", rankD1Path)
  print("  beta_1  =", beta1Path)

  d1Square = np.array([
    [1, 0, 0, 1],
    [1, 1, 0, 0],
    [0, 1, 1, 0],
    [0, 0, 1, 1],
  ], dtype=int)

  rankD1Square = rankMod2(d1Square)
  beta1Square = 4-rankD1Square
  print("\nSquare cycle")
  print("  rank d1 =", rankD1Square)
  print("  beta_1  =", beta1Square)

  d1Triangle = np.array([
    [1, 1, 0],
    [1, 0, 1],
    [0, 1, 1],
  ], dtype=int)
  d2Triangle = np.array([
    [1],
    [1],
    [1],
  ], dtype=int)

  rankD1Triangle = rankMod2(d1Triangle)
  rankD2Triangle = rankMod2(d2Triangle)
  beta1Triangle = 3-rankD1Triangle-rankD2Triangle
  print("\nFilled triangle")
  print("  rank d1 =", rankD1Triangle)
  print("  rank d2 =", rankD2Triangle)
  print("  beta_1  =", beta1Triangle)

  d1FilledSquare = np.array([
    [1, 0, 0, 1, 1],
    [1, 1, 0, 0, 0],
    [0, 1, 1, 0, 1],
    [0, 0, 1, 1, 0],
  ], dtype=int)
  d2FilledSquare = np.array([
    [1, 0],
    [1, 0],
    [0, 1],
    [0, 1],
    [1, 1],
  ], dtype=int)

  rankD1FilledSquare = rankMod2(d1FilledSquare)
  rankD2FilledSquare = rankMod2(d2FilledSquare)
  beta1FilledSquare = 5-rankD1FilledSquare-rankD2FilledSquare
  print("\nSquare filled by two triangles")
  print("  rank d1 =", rankD1FilledSquare)
  print("  rank d2 =", rankD2FilledSquare)
  print("  beta_1  =", beta1FilledSquare)


def buildRipsComplex(points, maxEdgeLength, maxDimension):
  rips = gd.RipsComplex(points=points, max_edge_length=maxEdgeLength)
  simplexTree = rips.create_simplex_tree(max_dimension=maxDimension)
  simplexTree.compute_persistence(homology_coeff_field=2)
  return simplexTree


def printSimplices(simplexTree, limit):
  print("\nFirst simplices in the filtration:")
  for index, (simplex, filtrationValue) in enumerate(simplexTree.get_filtration()):
    if index >= limit:
      print(f"  ... ({simplexTree.num_simplices()} simplices total)")
      break
    print(f"  simplex={simplex}, filtration={filtrationValue:.4f}")


def intervalLifetime(interval):
  birth, death = interval
  if np.isinf(death):
    return np.inf
  return death-birth


def printPersistence(simplexTree):
  print("\nBetti numbers at the end of the filtration:", simplexTree.betti_numbers())

  intervals = [
    tuple(interval)
    for interval in simplexTree.persistence_intervals_in_dimension(1)
  ]
  intervals.sort(key=intervalLifetime, reverse=True)

  print("\nH_1 persistence intervals, sorted by lifetime:")
  if len(intervals) == 0:
    print("  no H_1 intervals found")
    return intervals

  for birth, death in intervals:
    if np.isinf(death):
      lifetime = "infinite"
      deathText = "inf"
    else:
      lifetime = f"{death-birth:.4f}"
      deathText = f"{death:.4f}"
    print(f"  birth={birth:.4f}, death={deathText}, lifetime={lifetime}")

  return intervals


def plotLimits(points, coverageRadius, holeRadius):
  padding = max(0.35, coverageRadius, holeRadius)*1.25
  xMin = np.min(points[:, 0])-padding
  xMax = np.max(points[:, 0])+padding
  yMin = np.min(points[:, 1])-padding
  yMax = np.max(points[:, 1])+padding
  return xMin, xMax, yMin, yMax


def plotSensorField(points, coverageRadius, holeRadius):
  import matplotlib.pyplot as plt
  from matplotlib.patches import Circle

  figure, axis = plt.subplots(figsize=(5, 5))

  for point in points:
    disk = Circle(
      point,
      coverageRadius,
      facecolor="#e7e2f7",
      edgecolor="#4a368c",
      alpha=0.22,
      linewidth=0.8,
    )
    axis.add_patch(disk)

  guide = Circle(
    (0.0, 0.0),
    holeRadius,
    fill=False,
    edgecolor="#dc8c3c",
    linestyle="--",
    linewidth=2.0,
  )
  axis.add_patch(guide)
  axis.scatter(points[:, 0], points[:, 1], color="#4a368c", zorder=3)

  xMin, xMax, yMin, yMax = plotLimits(points, coverageRadius, holeRadius)
  axis.set_xlim(xMin, xMax)
  axis.set_ylim(yMin, yMax)
  axis.set_aspect("equal")
  axis.set_title("Sensor field with a central gap")
  axis.set_xlabel("x")
  axis.set_ylabel("y")
  axis.grid(True, alpha=0.25)
  return figure


def plotGraphAtScale(points, scale, coverageRadius, holeRadius):
  import matplotlib.pyplot as plt
  from matplotlib.patches import Circle

  _, edges, _ = buildVRSimplicesAtScale(points, scale)
  figure, axis = plt.subplots(figsize=(5, 5))

  for i, j in edges:
    axis.plot(
      [points[i, 0], points[j, 0]],
      [points[i, 1], points[j, 1]],
      color="#376eb4",
      linewidth=1.3,
    )

  guide = Circle(
    (0.0, 0.0),
    holeRadius,
    fill=False,
    edgecolor="#dc8c3c",
    linestyle="--",
    linewidth=2.0,
  )
  axis.add_patch(guide)
  axis.scatter(points[:, 0], points[:, 1], color="#4a368c", zorder=3)

  xMin, xMax, yMin, yMax = plotLimits(points, coverageRadius, holeRadius)
  axis.set_xlim(xMin, xMax)
  axis.set_ylim(yMin, yMax)
  axis.set_aspect("equal")
  axis.set_title(f"Pairwise detection graph at r = {scale:.2f}")
  axis.set_xlabel("x")
  axis.set_ylabel("y")
  axis.grid(True, alpha=0.25)
  return figure


def plotH1Barcode(intervals, maxEdgeLength):
  import matplotlib.pyplot as plt

  figure, axis = plt.subplots(figsize=(7, 3))

  if len(intervals) == 0:
    axis.text(0.5, 0.5, "No H_1 intervals", ha="center", va="center")
    axis.set_axis_off()
    return figure

  finiteDeaths = [death for _, death in intervals if not np.isinf(death)]
  xMax = max([maxEdgeLength]+finiteDeaths)*1.05

  for index, (birth, death) in enumerate(intervals):
    if np.isinf(death):
      end = xMax
      axis.hlines(index, birth, end, color="#dc8c3c", linewidth=2.5)
      axis.plot(end, index, marker=">", color="#dc8c3c")
    else:
      axis.hlines(index, birth, death, color="#376eb4", linewidth=2.5)

  axis.set_xlim(0.0, xMax*1.02)
  axis.set_xlabel("scale")
  axis.set_ylabel("H_1 class")
  axis.set_title("Persistent H_1 barcode")
  axis.set_ylim(-1, len(intervals))
  axis.grid(True, axis="x", alpha=0.25)
  return figure


def saveFigures(figures, saveDir):
  if saveDir is None:
    return

  saveDir.mkdir(parents=True, exist_ok=True)
  for name, figure in figures:
    figure.savefig(saveDir/name, dpi=200, bbox_inches="tight")
    print(f"Saved {saveDir/name}")


def runPersistence(points, arguments):
  if gd is None:
    print("\nGUDHI is not installed. Install it with: pip install gudhi")
    print("Skipping persistent homology, but fixed-scale homology was computed.")
    return []

  simplexTree = buildRipsComplex(
    points,
    arguments.max_edge_length,
    arguments.max_dimension,
  )

  print("\nPersistent Vietoris--Rips computation with GUDHI")
  print("  number of simplices =", simplexTree.num_simplices())
  printSimplices(simplexTree, arguments.simplex_print_limit)
  return printPersistence(simplexTree)


def main():
  arguments = parseArguments()

  if arguments.no_show:
    import matplotlib
    matplotlib.use("Agg")

  points = generateSensorPoints(
    arguments.sensors,
    arguments.ring_radius,
    arguments.noise,
    arguments.seed,
  )

  print("Sensor ring example")
  print("  sensors        =", arguments.sensors)
  print("  selected scale =", arguments.selected_scale)
  print("  max edge       =", arguments.max_edge_length)

  manualBoundaryExamples()

  fixedResult = computeFixedScaleHomology(points, arguments.selected_scale)
  printFixedScaleHomology(fixedResult, arguments.selected_scale)

  intervals = runPersistence(points, arguments)

  figures = [
    (
      "sensorField.png",
      plotSensorField(points, arguments.coverage_radius, arguments.hole_radius),
    ),
    (
      "graphAtScale.png",
      plotGraphAtScale(
        points,
        arguments.selected_scale,
        arguments.coverage_radius,
        arguments.hole_radius,
      ),
    ),
  ]

  if len(intervals) > 0:
    figures.append(("h1Barcode.png", plotH1Barcode(intervals, arguments.max_edge_length)))

  saveFigures(figures, arguments.save_dir)

  if not arguments.no_show:
    import matplotlib.pyplot as plt
    plt.show()


if __name__ == "__main__":
  main()
