"""
 * lorenzSensitivity.py
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

"""Pedagogical Lorenz-system experiment for lecture 06.

This script shows two standard features of the classical Lorenz equations:
1. the butterfly-shaped attractor in phase space,
2. sensitive dependence on initial condition.

The numerical method is a plain fourth-order Runge-Kutta scheme so that the
time stepping remains transparent to students.
"""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.animation import FuncAnimation, PillowWriter
from mpl_toolkits.mplot3d.art3d import Line3DCollection


# -----------------------------
# Classical Lorenz parameters
# -----------------------------
sigma = 10.0
rho = 28.0
beta = 8.0 / 3.0


# -----------------------------
# Numerical parameters
# -----------------------------
timeStep = 0.01
finalTime = 35.0
tailDuration = 4.0
frameStride = 5


# -----------------------------
# Nearby initial conditions
# -----------------------------
initialStateA = np.array([1.0, 1.0, 1.0])
initialStateB = np.array([1.0 + 1.0e-6, 1.0, 1.0])


def lorenzVectorField(state, sigmaValue, rhoValue, betaValue):
  """Return the right-hand side of the Lorenz equations."""
  xValue, yValue, zValue = state

  dxValue = sigmaValue * (yValue - xValue)
  dyValue = xValue * (rhoValue - zValue) - yValue
  dzValue = xValue * yValue - betaValue * zValue

  return np.array([dxValue, dyValue, dzValue])


def rungeKuttaStep(state, stepSize, sigmaValue, rhoValue, betaValue):
  """Advance one Runge-Kutta step."""
  k1Value = lorenzVectorField(state, sigmaValue, rhoValue, betaValue)
  k2Value = lorenzVectorField(
    state + 0.5 * stepSize * k1Value,
    sigmaValue,
    rhoValue,
    betaValue
  )
  k3Value = lorenzVectorField(
    state + 0.5 * stepSize * k2Value,
    sigmaValue,
    rhoValue,
    betaValue
  )
  k4Value = lorenzVectorField(
    state + stepSize * k3Value,
    sigmaValue,
    rhoValue,
    betaValue
  )

  return state + (stepSize / 6.0) * (k1Value + 2.0 * k2Value + 2.0 * k3Value + k4Value)


def integrateLorenz(initialState, stepSize, endTime, sigmaValue, rhoValue, betaValue):
  """Integrate the Lorenz system up to the final time."""
  nSteps = int(endTime / stepSize)
  times = np.linspace(0.0, nSteps * stepSize, nSteps + 1)
  orbit = np.zeros((nSteps + 1, 3))
  orbit[0] = initialState

  for i in range(nSteps):
    orbit[i + 1] = rungeKuttaStep(orbit[i], stepSize, sigmaValue, rhoValue, betaValue)

  return times, orbit


def firstLargeSeparation(separation, threshold):
  """Return the first time index where the distance exceeds threshold."""
  indices = np.where(separation >= threshold)[0]

  if indices.size == 0:
    return None

  return int(indices[0])


def setTrajectoryWindow(lineObject, orbit, startIndex, endIndex):
  """Update a 3D line with a finite-memory segment of an orbit."""
  lineObject.set_data(orbit[startIndex:endIndex, 0], orbit[startIndex:endIndex, 1])
  lineObject.set_3d_properties(orbit[startIndex:endIndex, 2])


def setMarkerPosition(markerObject, state):
  """Update a 3D marker position."""
  markerObject.set_data([state[0]], [state[1]])
  markerObject.set_3d_properties([state[2]])


def buildFadingSegments(orbit, startIndex, endIndex, colorRgb):
  """Build 3D line segments with increasing opacity toward the present."""
  points = orbit[startIndex:endIndex]

  if len(points) < 2:
    return np.empty((0, 2, 3)), np.empty((0, 4))

  segments = np.stack((points[:-1], points[1:]), axis = 1)
  nSegments = len(segments)
  alphaValues = np.linspace(0.08, 1.0, nSegments)
  colors = np.column_stack((
    np.full(nSegments, colorRgb[0]),
    np.full(nSegments, colorRgb[1]),
    np.full(nSegments, colorRgb[2]),
    alphaValues
  ))

  return segments, colors


def main():
  """Run the Lorenz sensitivity experiment and display the results."""
  times, orbitA = integrateLorenz(initialStateA, timeStep, finalTime, sigma, rho, beta)
  _, orbitB = integrateLorenz(initialStateB, timeStep, finalTime, sigma, rho, beta)

  separation = np.linalg.norm(orbitB - orbitA, axis = 1)
  threshold = 5.0
  divergenceIndex = firstLargeSeparation(separation, threshold)
  tailSteps = max(2, int(tailDuration / timeStep))
  frameIndices = np.arange(0, len(times), frameStride)

  combinedOrbit = np.vstack((orbitA, orbitB))
  xMin, yMin, zMin = np.min(combinedOrbit, axis = 0)
  xMax, yMax, zMax = np.max(combinedOrbit, axis = 0)

  xMargin = 0.05 * (xMax - xMin)
  yMargin = 0.05 * (yMax - yMin)
  zMargin = 0.05 * (zMax - zMin)

  fig = plt.figure(figsize = (13, 5.5))
  axisPhase = fig.add_subplot(1, 2, 1, projection = '3d')
  axisFilm = fig.add_subplot(1, 2, 2, projection = '3d')

  axisPhase.plot(
    orbitA[:, 0], orbitA[:, 1], orbitA[:, 2],
    lw = 0.9,
    color = 'navy',
    label = r"$u(0) = (1, 1, 1)$"
  )
  axisPhase.plot(
    orbitB[:, 0], orbitB[:, 1], orbitB[:, 2],
    lw = 0.9,
    color = 'crimson',
    alpha = 0.8,
    label = r"$v(0) = (1 + 10^{-6}, 1, 1)$"
  )
  axisPhase.set_title("Lorenz attractor and two nearby trajectories")
  axisPhase.set_xlabel(r"$x(t)$")
  axisPhase.set_ylabel(r"$y(t)$")
  axisPhase.set_zlabel(r"$z(t)$")
  axisPhase.legend(loc = 'upper left')
  axisPhase.set_xlim(xMin - xMargin, xMax + xMargin)
  axisPhase.set_ylim(yMin - yMargin, yMax + yMargin)
  axisPhase.set_zlim(zMin - zMargin, zMax + zMargin)

  axisFilm.set_title("Finite-memory film of the two trajectories")
  axisFilm.set_xlabel(r"$x(t)$")
  axisFilm.set_ylabel(r"$y(t)$")
  axisFilm.set_zlabel(r"$z(t)$")
  axisFilm.set_xlim(xMin - xMargin, xMax + xMargin)
  axisFilm.set_ylim(yMin - yMargin, yMax + yMargin)
  axisFilm.set_zlim(zMin - zMargin, zMax + zMargin)

  colorA = np.array([0.0, 0.0, 0.5])
  colorB = np.array([0.86, 0.08, 0.24])
  filmTailA = Line3DCollection([], linewidths = 2.2, label = r"recent past of $u(t)$")
  filmTailB = Line3DCollection([], linewidths = 2.2, label = r"recent past of $v(t)$")
  axisFilm.add_collection3d(filmTailA)
  axisFilm.add_collection3d(filmTailB)
  markerA, = axisFilm.plot([], [], [], 'o', color = 'navy', ms = 5)
  markerB, = axisFilm.plot([], [], [], 'o', color = 'crimson', ms = 5)
  timeLabel = axisFilm.text2D(0.04, 0.93, "", transform = axisFilm.transAxes)
  axisFilm.legend(loc = 'upper left')

  axisInset = fig.add_axes([0.39, 0.08, 0.22, 0.20])
  axisInset.semilogy(times, np.maximum(separation, 1.0e-16), color = 'darkgreen', lw = 1.6)
  axisInset.axhline(threshold, color = '0.35', ls = '--', lw = 1.0)
  currentTimeLine = axisInset.axvline(times[0], color = 'black', lw = 1.1)
  axisInset.set_title("Separation", fontsize = 10)
  axisInset.set_xlabel(r"$t$", fontsize = 9)
  axisInset.set_ylabel(r"$\|u-v\|$", fontsize = 9)
  axisInset.tick_params(labelsize = 8)
  axisInset.grid(True, which = 'both', alpha = 0.3)

  def updateFilm(frameNumber):
    frameIndex = frameIndices[frameNumber]
    startIndex = max(0, frameIndex - tailSteps)

    segmentsA, colorsA = buildFadingSegments(orbitA, startIndex, frameIndex + 1, colorA)
    segmentsB, colorsB = buildFadingSegments(orbitB, startIndex, frameIndex + 1, colorB)
    filmTailA.set_segments(segmentsA)
    filmTailA.set_color(colorsA)
    filmTailB.set_segments(segmentsB)
    filmTailB.set_color(colorsB)
    setMarkerPosition(markerA, orbitA[frameIndex])
    setMarkerPosition(markerB, orbitB[frameIndex])
    currentTimeLine.set_xdata([times[frameIndex], times[frameIndex]])

    timeLabel.set_text(
      rf"$t = {times[frameIndex]:.2f}$" + "\n" + rf"$\|u(t) - v(t)\| = {separation[frameIndex]:.3e}$"
    )

    return filmTailA, filmTailB, markerA, markerB, timeLabel, currentTimeLine

  animation = FuncAnimation(
    fig,
    updateFilm,
    frames = len(frameIndices),
    interval = 40,
    blit = False,
    repeat = True
  )

  fig.suptitle(
    rf"Lorenz equations with $(\sigma, \rho, \beta) = ({sigma:.0f}, {rho:.0f}, {beta:.3f})$",
    fontsize = 13
  )

  if divergenceIndex is not None:
    divergenceTime = times[divergenceIndex]
    footerText = (
      rf"The finite-memory film keeps only the most recent {tailDuration:.1f} time units. "
      + rf"Visible separation begins near $t = {divergenceTime:.1f}$."
    )
  else:
    footerText = rf"The finite-memory film keeps only the most recent {tailDuration:.1f} time units."

  fig.text(0.06, 0.02, footerText, fontsize = 11)
  fig.subplots_adjust(left = 0.04, right = 0.98, bottom = 0.16, top = 0.90, wspace = 0.12)

  if plt.get_backend().lower() == 'agg':
    outputPath = Path(__file__).with_name("lorenzSensitivity.gif")
    animation.save(outputPath, writer = PillowWriter(fps = 25))
    print(f"Saved animation to {outputPath}")
  else:
    plt.show()


if __name__ == "__main__":
  main()
