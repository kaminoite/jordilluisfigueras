"""
 * logisticDiagramEpsilon.py
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

"""Interactive bifurcation diagram for a perturbed logistic family.

This lecture-4 variant of ``logisticDiagram.py`` studies the map

  x_{n+1} = r x_n (1 - x_n) (1 + epsilon (2 x_n - 1)^2)

with an interactive slider for the parameter epsilon.
"""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.widgets import Button
from matplotlib.widgets import Slider


# -----------------------------
# Bifurcation diagram parameters
# -----------------------------
rMin = 0.0
rMax = 4.0
nR = 4096
nTransient = 1024
nRecorded = 512
randomSeed = 12345
outputStem = "logisticDiagramEpsilon"
epsilonMin = 0.0
epsilonMax = 1.0
epsilonInitial = 0.0


def perturbedLogisticMapStep(r, x, epsilon):
  """Return one step of the perturbed logistic map."""
  return r * x * (1.0 - x) * (1.0 + epsilon * (2.0 * x - 1.0) ** 2)


def computeBifurcationDiagram(epsilon):
  """Compute the bifurcation diagram for one fixed epsilon."""
  rng = np.random.default_rng(randomSeed)

  rValues = np.linspace(rMin, rMax, nR)
  xValues = rng.random(nR)

  for _ in range(nTransient):
    xValues = perturbedLogisticMapStep(rValues, xValues, epsilon)
    invalidMask = ~np.isfinite(xValues)
    xValues[invalidMask] = np.nan

  rPlot = np.tile(rValues, nRecorded)
  xPlot = np.empty(nR * nRecorded)

  for i in range(nRecorded):
    xValues = perturbedLogisticMapStep(rValues, xValues, epsilon)
    invalidMask = ~np.isfinite(xValues)
    xValues[invalidMask] = np.nan

    iStart = i * nR
    iEnd = (i + 1) * nR
    xPlot[iStart:iEnd] = xValues

  return rPlot, xPlot


def getOutputPath(extension):
  """Build the output path for exported figures."""
  outputDir = Path(__file__).resolve().parent
  return outputDir / f"{outputStem}.{extension}"


def saveFigure(fig, extension, statusText):
  """Save the current figure and display a short status message."""
  outputPath = getOutputPath(extension)
  fig.savefig(outputPath, dpi = 300, bbox_inches = 'tight')
  statusText.set_text(f"Saved {outputPath.name}")
  fig.canvas.draw_idle()


def styleButton(button):
  """Apply a simple visual style to a button widget."""
  button.label.set_fontsize(9)
  button.label.set_color('#222222')


def main():
  """Create the interactive lecture-4 figure."""
  rPlot, xPlot = computeBifurcationDiagram(epsilonInitial)

  fig, ax = plt.subplots(figsize = (10.5, 6.5))
  fig.subplots_adjust(top = 0.82, bottom = 0.20)

  bifurcationArtist, = ax.plot(
    rPlot, xPlot,
    linestyle = 'None',
    marker = ',',
    color = 'black',
    alpha = 0.70
  )

  ax.set_title(rf"Bifurcation diagram for $\varepsilon = {epsilonInitial:g}$")
  ax.set_xlabel(r"$r$")
  ax.set_ylabel(r"$x$")
  ax.set_xlim(rMin, rMax)
  ax.set_ylim(0.0, 1.02)
  ax.grid(True, linewidth = 0.3, alpha = 0.4)

  fig.suptitle(
    r"Bifurcation diagrams for $f(x) = r x (1-x) (1 + \varepsilon (2x-1)^2)$",
    fontsize = 14
  )

  fig.text(
    0.02, 0.94,
    rf"{nR:d} parameter values" "\n"
    rf"{nTransient:d} transient iterates" "\n"
    rf"{nRecorded:d} recorded iterates",
    ha = 'left',
    va = 'top',
    bbox = dict(facecolor = 'white', alpha = 0.88, edgecolor = 'none')
  )

  statusText = fig.text(
    0.34, 0.94,
    "",
    ha = 'left',
    va = 'top',
    fontsize = 9,
    color = '#333333',
    bbox = dict(facecolor = 'white', alpha = 0.85, edgecolor = 'none', boxstyle = 'round,pad=0.25')
  )

  sliderAxes = fig.add_axes([0.14, 0.08, 0.56, 0.04])
  epsilonSlider = Slider(
    sliderAxes,
    r"$\varepsilon$",
    epsilonMin,
    epsilonMax,
    valinit = epsilonInitial,
    valstep = 0.001,
    color = '#4c72b0'
  )

  pngButtonAxes = fig.add_axes([0.83, 0.90, 0.07, 0.05])
  pdfButtonAxes = fig.add_axes([0.91, 0.90, 0.07, 0.05])
  pngButton = Button(pngButtonAxes, "Save PNG", color = '#f5f5f5', hovercolor = '#e6e6e6')
  pdfButton = Button(pdfButtonAxes, "Save PDF", color = '#f5f5f5', hovercolor = '#e6e6e6')
  styleButton(pngButton)
  styleButton(pdfButton)

  def updateDiagram(epsilon):
    """Recompute the bifurcation diagram for the selected epsilon."""
    statusText.set_text(rf"Computing diagram for $\varepsilon = {epsilon:.3f}$")
    fig.canvas.draw_idle()
    plt.pause(0.001)

    rPlot, xPlot = computeBifurcationDiagram(epsilon)
    bifurcationArtist.set_data(rPlot, xPlot)
    ax.set_title(rf"Bifurcation diagram for $\varepsilon = {epsilon:g}$")

    statusText.set_text(rf"Ready for $\varepsilon = {epsilon:.3f}$")
    fig.canvas.draw_idle()

  def savePng(_):
    """Save the current figure as PNG."""
    saveFigure(fig, 'png', statusText)

  def savePdf(_):
    """Save the current figure as PDF."""
    saveFigure(fig, 'pdf', statusText)

  epsilonSlider.on_changed(updateDiagram)
  pngButton.on_clicked(savePng)
  pdfButton.on_clicked(savePdf)

  plt.show()


if __name__ == "__main__":
  main()
