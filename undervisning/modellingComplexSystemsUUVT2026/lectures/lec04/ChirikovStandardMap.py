"""
 * ChirikovStandardMap.py
 *
 * Copyright (c) 2026, Jordi-Lluís Figueras
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

"""Interactive phase portrait for the Chirikov standard map.

This script illustrates a two-dimensional discrete dynamical system on the
torus.  The pedagogical core is:

1. define one step of the map,
2. iterate many initial conditions forward,
3. visualize the resulting phase portrait,
4. vary the parameter k with a slider.
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider

# -----------------------------
# Standard map parameters
# -----------------------------
k = 0.6
nSeedsX = 21
nSeedsY = 21
nSteps = 220

# -----------------------------
# Standard map on the torus
#   y_{n+1} = y_n + (k / 2pi) sin(2pi x_n)  (mod 1)
#   x_{n+1} = x_n + y_{n+1}                 (mod 1)
# -----------------------------
def standardMapStep(x, y, kValue):
  """Return one step of the standard map on the torus."""
  yNext = (y + (kValue / (2.0 * np.pi)) * np.sin(2.0 * np.pi * x)) % 1.0
  xNext = (x + yNext) % 1.0
  return xNext, yNext


def computePhasePortrait(kValue):
  """Compute iterates of many initial conditions for one parameter value."""
  xSeeds = np.linspace(0.0, 1.0, nSeedsX, endpoint = False)
  ySeeds = np.linspace(0.0, 1.0, nSeedsY, endpoint = False)
  X0, Y0 = np.meshgrid(xSeeds, ySeeds)

  x = X0.ravel()
  y = Y0.ravel()

  xData = np.empty((nSteps + 1, x.size))
  yData = np.empty((nSteps + 1, y.size))

  xData[0] = x
  yData[0] = y

  for i in range(nSteps):
    x, y = standardMapStep(x, y, kValue)
    xData[i + 1] = x
    yData[i + 1] = y

  return xData.reshape(-1), yData.reshape(-1)


# -----------------------------
# Initial data
# -----------------------------
xPlot, yPlot = computePhasePortrait(k)

# -----------------------------
# Figure setup
# -----------------------------
fig, ax = plt.subplots(figsize = (8, 8))
fig.subplots_adjust(bottom = 0.18)

points = ax.scatter(
    xPlot, yPlot,
    s = 2,
    color = 'C0',
    alpha = 0.65,
    edgecolors = 'none'
)

ax.set_title("Phase portrait of the Chirikov standard map on the torus")
ax.set_xlabel(r"$x \; (\mathrm{mod}\; 1)$")
ax.set_ylabel(r"$y \; (\mathrm{mod}\; 1)$")
ax.set_xlim(0.0, 1.0)
ax.set_ylim(0.0, 1.0)
ax.set_aspect('equal')
ax.grid(True)

stateText = ax.text(
    0.02, 0.98,
    rf"$k = {k:.2f}$" "\n"
    rf"{nSeedsX * nSeedsY:d} initial conditions" "\n"
    rf"{nSteps:d} iterates per orbit",
    transform = ax.transAxes,
    ha = 'left',
    va = 'top',
    bbox = dict(facecolor = 'white', alpha = 0.85, edgecolor = 'none')
)

ax.text(
    0.98, 0.02,
    r"$y_{n+1} = y_n + \frac{k}{2\pi}\sin(2\pi x_n)$" "\n"
    r"$x_{n+1} = x_n + y_{n+1}$" "\n"
    r"both coordinates taken mod $1$",
    transform = ax.transAxes,
    ha = 'right',
    va = 'bottom',
    bbox = dict(facecolor = 'white', alpha = 0.85, edgecolor = 'none')
)

# Slider for the parameter k
axSlider = fig.add_axes([0.17, 0.06, 0.66, 0.04])
kSlider = Slider(axSlider, r"$k$", 0.0, 2.0, valinit = k, valstep = 0.01)


# -----------------------------
# Slider callback
# -----------------------------
def updateParameter(_):
  """Recompute the phase portrait when the parameter k changes."""
  kValue = kSlider.val
  xUpdated, yUpdated = computePhasePortrait(kValue)

  points.set_offsets(np.column_stack((xUpdated, yUpdated)))
  stateText.set_text(
    rf"$k = {kValue:.2f}$" "\n"
    rf"{nSeedsX * nSeedsY:d} initial conditions" "\n"
    rf"{nSteps:d} iterates per orbit"
  )
  fig.canvas.draw_idle()


kSlider.on_changed(updateParameter)

plt.show()
