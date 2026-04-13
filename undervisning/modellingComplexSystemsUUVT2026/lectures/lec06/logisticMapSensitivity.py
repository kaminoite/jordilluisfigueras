"""
 * logisticMapSensitivity.py
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

"""Pedagogical exploration of sensitivity in the logistic map.

This script is intended for master students who are seeing chaos as
an issue of predictability, not only as a geometric object.

What the script does:
1. iterates the logistic map x_(n+1) = r x_n (1 - x_n),
2. compares two initial conditions that differ by a tiny amount,
3. plots both trajectories,
4. plots the distance |x_n - y_n| on a semilogarithmic scale.

Suggested classroom experiments:
  - Keep x0 and delta0 fixed and change r.
  - Start with r = 3.2, then 3.5, then 3.8, then 4.0.
  - Observe when nearby trajectories remain similar and when they separate.
  - Change delta0 and ask how much longer predictability survives.
"""

import matplotlib.pyplot as plt
import numpy as np


# -----------------------------
# Parameters to explore
# -----------------------------
r = 4.0
x0 = 0.20000000
delta0 = 1.0e-8
nSteps = 60


def logisticMapStep(rValue, xValue):
  """Return one step of the logistic map."""
  return rValue * xValue * (1.0 - xValue)


def computeOrbit(rValue, initialValue, nIterates):
  """Compute the forward orbit from a given initial condition."""
  orbit = np.zeros(nIterates + 1)
  orbit[0] = initialValue

  for i in range(nIterates):
    orbit[i + 1] = logisticMapStep(rValue, orbit[i])

  return orbit


def firstLargeSeparation(separation, threshold):
  """Return the first index where the separation exceeds threshold."""
  indices = np.where(separation >= threshold)[0]

  if indices.size == 0:
    return None

  return int(indices[0])


def main():
  """Run the comparison experiment and display the plots."""
  y0 = x0 + delta0

  orbitX = computeOrbit(r, x0, nSteps)
  orbitY = computeOrbit(r, y0, nSteps)
  separation = np.abs(orbitY - orbitX)
  separationForLog = np.maximum(separation, 1.0e-16)
  nValues = np.arange(nSteps + 1)

  threshold = 1.0e-2
  predictabilityStep = firstLargeSeparation(separation, threshold)

  fig, axes = plt.subplots(1, 2, figsize = (12, 5))

  axes[0].plot(nValues, orbitX, 'o-', lw = 2, ms = 4, label = rf"$x_0 = {x0:.8f}$")
  axes[0].plot(nValues, orbitY, 's--', lw = 1.8, ms = 4, label = rf"$y_0 = {y0:.8f}$")
  axes[0].set_title("Two nearby trajectories")
  axes[0].set_xlabel(r"$n$")
  axes[0].set_ylabel(r"$x_n$")
  axes[0].set_ylim(0.0, 1.0)
  axes[0].grid(True)
  axes[0].legend(loc = "best")

  axes[1].semilogy(nValues, separationForLog, 'o-', color = 'crimson', lw = 2, ms = 4)
  axes[1].axhline(threshold, color = '0.35', ls = '--', lw = 1.5, label = r"threshold $10^{-2}$")
  axes[1].set_title("Growth of the separation")
  axes[1].set_xlabel(r"$n$")
  axes[1].set_ylabel(r"$|x_n - y_n|$")
  axes[1].grid(True, which = "both")

  if predictabilityStep is not None:
    axes[1].axvline(predictabilityStep, color = '0.35', ls = ':', lw = 1.5)
    axes[1].text(
      predictabilityStep + 0.7,
      threshold * 1.6,
      f"predictability lost near n = {predictabilityStep}",
      fontsize = 10
    )

  axes[1].legend(loc = "lower right")

  fig.suptitle(
    rf"Logistic map sensitivity experiment: $x_{{n+1}} = r x_n (1 - x_n)$ with $r = {r:.2f}$",
    fontsize = 13
  )

  fig.text(
    0.12,
    0.02,
    "Try changing r and delta0 to see how the predictability horizon moves.",
    fontsize = 11
  )

  plt.tight_layout(rect = [0.0, 0.05, 1.0, 0.95])
  plt.show()


if __name__ == "__main__":
  main()
