"""
 * cityMarkovChain.py
 *
 * Copyright (c) 2026, Jordi-Lluis Figueras
 *
 * Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:
 *
 * Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
 * Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
 *
 * OpenAI Codex / ChatGPT 5.4 has been used in the editing of this file.
 *
 * THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
 *
"""

"""Simulate the Lecture 10 city Markov chain.

Usage:
  python cityMarkovChain.py
  python cityMarkovChain.py --steps 12
  python cityMarkovChain.py --initial 4000 2000 3000 1000 --normalized

The state order is:
  D = Downtown, U = University, R = Residential, I = Industrial

The script uses the same column-stochastic matrix as in lecture10.tex and prints
the trajectory x(t + 1) = P x(t), together with the stationary distribution.
"""

import argparse

import numpy as np


defaultSteps = 10
defaultInitial = [4000.0, 2000.0, 3000.0, 1000.0]
nodeLabels = ["D", "U", "R", "I"]
nodeNames = ["Downtown", "University", "Residential", "Industrial"]

transitionMatrix = np.array(
  [
    [0.5, 0.2, 0.3, 0.1],
    [0.3, 0.6, 0.0, 0.0],
    [0.2, 0.2, 0.5, 0.2],
    [0.0, 0.0, 0.2, 0.7],
  ],
  dtype = float,
)


def parseArguments():
  parser = argparse.ArgumentParser(description = "Simulate the Lecture 10 city Markov chain")
  parser.add_argument("--steps", type = int, default = defaultSteps, help = "number of time steps to simulate")
  parser.add_argument(
    "--initial",
    nargs = 4,
    type = float,
    metavar = ("D", "U", "R", "I"),
    default = defaultInitial,
    help = "initial population vector in the order D U R I",
  )
  parser.add_argument(
    "--normalized",
    action = "store_true",
    help = "normalize the initial vector to total mass 1 before iterating",
  )
  parser.add_argument(
    "--decimals",
    type = int,
    default = 4,
    help = "number of decimals in the printed output",
  )
  args = parser.parse_args()

  if args.steps < 0:
    parser.error("--steps must be nonnegative")

  if args.decimals < 0:
    parser.error("--decimals must be nonnegative")

  if any(value < 0 for value in args.initial):
    parser.error("all initial populations must be nonnegative")

  if sum(args.initial) <= 0:
    parser.error("the initial population must have positive total mass")

  return args


def normalizeVector(vector):
  totalMass = np.sum(vector)
  return vector / totalMass


def formatVector(vector, decimals):
  entries = [f"{label} = {value:.{decimals}f}" for label, value in zip(nodeLabels, vector)]
  return ", ".join(entries)


def stationaryDistribution(matrix):
  eigenvalues, eigenvectors = np.linalg.eig(matrix)
  dominantIndex = np.argmin(np.abs(eigenvalues - 1.0))
  dominantVector = np.real(eigenvectors[:, dominantIndex])

  if np.sum(dominantVector) < 0:
    dominantVector = -dominantVector

  dominantVector = np.maximum(dominantVector, 0.0)
  return normalizeVector(dominantVector)


def simulateTrajectory(matrix, initialState, nSteps):
  trajectory = [initialState.copy()]
  currentState = initialState.copy()

  for _ in range(nSteps):
    currentState = matrix @ currentState
    trajectory.append(currentState.copy())

  return trajectory


def printTransitionMatrix(matrix, decimals):
  print("Transition matrix P (columns sum to 1):")
  for row in matrix:
    print("  " + "  ".join(f"{entry:.{decimals}f}" for entry in row))


def printTrajectory(trajectory, decimals):
  print("\nTrajectory:")
  for step, state in enumerate(trajectory):
    totalMass = np.sum(state)
    print(f"  t = {step:2d}: {formatVector(state, decimals)} | total = {totalMass:.{decimals}f}")


def printStationarySummary(stationaryState, finalState, nSteps, decimals):
  targetState = stationaryState * np.sum(finalState)
  difference = np.linalg.norm(finalState - targetState, ord = 1)
  print("\nStationary distribution x* satisfying P x* = x*:")
  print(f"  {formatVector(stationaryState, decimals)}")
  print(f"\nL1 distance between x({nSteps}) and totalMass * x*: {difference:.{decimals}f}")


def printNodeLegend():
  print("Node legend:")
  for label, name in zip(nodeLabels, nodeNames):
    print(f"  {label} = {name}")


def main():
  args = parseArguments()
  initialState = np.array(args.initial, dtype = float)

  if args.normalized:
    initialState = normalizeVector(initialState)

  stationaryState = stationaryDistribution(transitionMatrix)
  trajectory = simulateTrajectory(transitionMatrix, initialState, args.steps)

  printNodeLegend()
  print()
  printTransitionMatrix(transitionMatrix, args.decimals)
  printTrajectory(trajectory, args.decimals)
  printStationarySummary(stationaryState, trajectory[-1], args.steps, args.decimals)


if __name__ == "__main__":
  main()
