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
torus. The pedagogical core is:

1. define one step of the map,
2. iterate many initial conditions forward,
3. visualize the resulting phase portrait,
4. vary the parameter k with a slider,
5. click in phase space to plot a forward orbit.
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Button, Slider

# -----------------------------
# Standard map parameters
# -----------------------------
k = 0.6
nSeedsX = 21
nSeedsY = 21
nSteps = 220
orbitSteps = 300

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
  # Use irrationally shifted seeds to avoid artificial short periods at k = 0.
  # On a rational grid, y is a rational multiple of 1, so the integrable case
  # produces misleading periodic point clouds instead of horizontal circles.
  xSeeds = np.linspace(0.0, 1.0, nSeedsX, endpoint = False)
  goldenRatioConjugate = 0.5 * (np.sqrt(5.0) - 1.0)
  ySeeds = np.mod((np.arange(nSeedsY) + 0.5) * goldenRatioConjugate, 1.0)
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


def computeForwardOrbit(x0, y0, kValue, nOrbitSteps):
  """Compute one forward orbit starting from a clicked initial condition."""
  xOrbit = np.empty(nOrbitSteps + 1)
  yOrbit = np.empty(nOrbitSteps + 1)

  xOrbit[0] = x0 % 1.0
  yOrbit[0] = y0 % 1.0

  x = xOrbit[0]
  y = yOrbit[0]

  for i in range(nOrbitSteps):
    x, y = standardMapStep(x, y, kValue)
    xOrbit[i + 1] = x
    yOrbit[i + 1] = y

  return xOrbit, yOrbit


# -----------------------------
# Initial data
# -----------------------------
xPlot, yPlot = computePhasePortrait(k)

# -----------------------------
# Figure setup
# -----------------------------
fig, ax = plt.subplots(figsize = (16, 8))
fig.subplots_adjust(left = 0.08, right = 0.70, bottom = 0.18, top = 0.95)

points = ax.scatter(
    xPlot, yPlot,
    s = 2,
    color = 'C0',
    alpha = 0.65,
    edgecolors = 'none'
)

orbitPoints = ax.scatter([], [], s = 10, color = 'C3', alpha = 0.75)
initialPoint = ax.scatter([], [], s = 70, color = 'gold', edgecolors = 'black', zorder = 5)

selectedOrbit = {
    'x0': None,
    'y0': None,
}

interactionEnabled = {'value': False}

ax.set_title("Phase portrait of the Chirikov standard map on the torus")
ax.set_xlabel(r"$x \; (\mathrm{mod}\; 1)$")
ax.set_ylabel(r"$y \; (\mathrm{mod}\; 1)$")
ax.set_xlim(0.0, 1.0)
ax.set_ylim(0.0, 1.0)
ax.grid(True)

stateText = fig.text(
    0.74, 0.83,
    rf"$k = {k:.2f}$" "\n"
    rf"{nSeedsX * nSeedsY:d} initial conditions" "\n"
    rf"{nSteps:d} iterates per orbit",
    ha = 'left',
    va = 'top',
    bbox = dict(facecolor = 'white', alpha = 0.85, edgecolor = 'none')
)

orbitText = fig.text(
    0.74, 0.62,
    "Click in phase space to plot a forward orbit",
    ha = 'left',
    va = 'top',
    bbox = dict(facecolor = 'white', alpha = 0.85, edgecolor = 'none')
)

mapText = fig.text(
    0.74, 0.38,
    r"$y_{n+1} = y_n + \frac{k}{2\pi}\sin(2\pi x_n)$" "\n"
    r"$x_{n+1} = x_n + y_{n+1}$" "\n"
    r"both coordinates taken mod $1$",
    ha = 'left',
    va = 'top',
    bbox = dict(facecolor = 'white', alpha = 0.85, edgecolor = 'none')
)

# Slider for the parameter k
axSlider = fig.add_axes([0.12, 0.06, 0.52, 0.04])
kSlider = Slider(axSlider, r"$k$", 0.0, 2.0, valinit = k, valstep = 0.01)

introText = fig.text(
    0.39, 0.55,
    "Choose the parameter with the k slider.\n"
    "Then click inside the phase-space square to choose an initial point.\n"
    "The script will compute and plot its forward iterates.",
    ha = 'center',
    va = 'center',
    fontsize = 13,
    bbox = dict(facecolor = 'white', alpha = 0.96, edgecolor = 'black', boxstyle = 'round,pad=0.7'),
    zorder = 10
)

axStartButton = fig.add_axes([0.31, 0.22, 0.16, 0.06])
startButton = Button(axStartButton, 'Start exploring')


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

  if selectedOrbit['x0'] is not None and selectedOrbit['y0'] is not None:
    updateSelectedOrbit(selectedOrbit['x0'], selectedOrbit['y0'], kValue)

  fig.canvas.draw_idle()


def updateSelectedOrbit(x0, y0, kValue):
  """Plot the forward orbit of the currently selected initial condition."""
  xOrbit, yOrbit = computeForwardOrbit(x0, y0, kValue, orbitSteps)

  orbitPoints.set_offsets(np.column_stack((xOrbit, yOrbit)))
  initialPoint.set_offsets(np.array([[xOrbit[0], yOrbit[0]]]))
  orbitText.set_text(
    rf"clicked initial condition: ({xOrbit[0]:.3f}, {yOrbit[0]:.3f})" "\n"
    rf"forward orbit: {orbitSteps:d} iterates"
  )


def onClick(event):
  """Select an initial condition by clicking in the phase portrait."""
  if not interactionEnabled['value']:
    return

  if event.inaxes != ax or event.xdata is None or event.ydata is None:
    return

  x0 = event.xdata % 1.0
  y0 = event.ydata % 1.0
  selectedOrbit['x0'] = x0
  selectedOrbit['y0'] = y0

  updateSelectedOrbit(x0, y0, kSlider.val)
  fig.canvas.draw_idle()


def enableInteraction(_):
  """Dismiss the introductory overlay and enable mouse selection."""
  interactionEnabled['value'] = True
  introText.set_visible(False)
  axStartButton.set_visible(False)
  fig.canvas.draw_idle()


kSlider.on_changed(updateParameter)
fig.canvas.mpl_connect('button_press_event', onClick)
startButton.on_clicked(enableInteraction)

plt.show()
