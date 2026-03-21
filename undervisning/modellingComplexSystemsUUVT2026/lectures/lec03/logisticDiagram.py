"""
 * logisticDiagram.py
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

"""Interactive bifurcation diagram for the logistic map.

This script has two layers:

1. Core pedagogical content:
   - the logistic map x_{n+1} = r x_n (1 - x_n),
   - forward iteration,
   - construction of the bifurcation diagram by discarding transients
     and plotting the long-time iterates.

2. Advanced optional content:
   - numerical detection of unstable periodic points of small period,
   - interactive overlay controls,
   - export buttons.

For classroom presentation, the most important functions are:
  - logisticMapStep()
  - iterateLogisticMap()
  - computeBifurcationDiagram()

The remaining functions enrich the visualization and connect the picture
with fixed points, periodic orbits, and stability.
"""

import time
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.widgets import Button
from matplotlib.widgets import CheckButtons

# -----------------------------
# Logistic map parameters
# -----------------------------
rMin = 0.0
rMax = 4.0
nR = 4096
nTransient = 1024
nRecorded = 1024
randomSeed = 12345
maxPeriod = 4
nPeriodicSearch = 4097
rootTolerance = 1.0e-10
periodTolerance = 1.0e-8
bisectionSteps = 60
progressStride = 4
outputStem = "logisticDiagram"


# -----------------------------
# Core model:
#   x_{n+1} = r x_n (1 - x_n)
# -----------------------------
def logisticMapStep(r, x):
  """Return one step of the logistic map."""
  return r * x * (1.0 - x)



def iterateLogisticMap(rValue, xValue, nSteps):
  """Iterate the logistic map nSteps times from xValue."""
  xIterate = xValue

  for _ in range(nSteps):
    xIterate = logisticMapStep(rValue, xIterate)

  return xIterate



def iterateLogisticMapAndMultiplier(rValue, xValue, period):
  """Return f^period(xValue) and the derivative multiplier along the orbit.

  If xValue belongs to a period-p orbit, then the returned multiplier is
  (f^p)'(xValue), i.e. the product of derivatives along one full cycle.
  This is the quantity used in the linear stability test.
  """
  xIterate = xValue
  multiplier = 1.0

  for _ in range(period):
    multiplier *= rValue * (1.0 - 2.0 * xIterate)
    xIterate = logisticMapStep(rValue, xIterate)

  return xIterate, multiplier



def computeBifurcationDiagram():
  """Compute the standard bifurcation diagram by forward iteration.

  For each sampled parameter value r:
    1. start from a random initial condition x_0,
    2. iterate long enough to remove transients,
    3. record further iterates,
    4. plot the points (r, x_n).

  This procedure reveals attracting long-time behavior.
  Unstable objects are not detected by this forward iteration alone.
  """
  rng = np.random.default_rng(randomSeed)

  rValues = np.linspace(rMin, rMax, nR)
  xValues = rng.random(nR)

  for _ in range(nTransient):
    xValues = logisticMapStep(rValues, xValues)

  rPlot = np.tile(rValues, nRecorded)
  xPlot = np.empty(nR * nRecorded)

  for i in range(nRecorded):
    xValues = logisticMapStep(rValues, xValues)
    iStart = i * nR
    iEnd = (i + 1) * nR
    xPlot[iStart:iEnd] = xValues

  return rPlot, xPlot



def computePeriodicResidual(rValue, xValue, period):
  """Return the residual f^period(x) - x."""
  return iterateLogisticMap(rValue, xValue, period) - xValue



def bisectPeriodicRoot(rValue, period, xLeft, xRight, fLeft, fRight):
  """Approximate a root of f^period(x) - x on [xLeft, xRight] by bisection."""
  aValue = xLeft
  bValue = xRight
  faValue = fLeft

  if abs(faValue) < rootTolerance:
    return aValue

  if abs(fRight) < rootTolerance:
    return xRight

  for _ in range(bisectionSteps):
    midpoint = 0.5 * (aValue + bValue)
    fMidpoint = computePeriodicResidual(rValue, midpoint, period)

    if abs(fMidpoint) < rootTolerance:
      return midpoint

    if faValue * fMidpoint <= 0.0:
      bValue = midpoint
    else:
      aValue = midpoint
      faValue = fMidpoint

  return 0.5 * (aValue + bValue)



def hasSmallerPeriod(rValue, xValue, period):
  """Check whether a candidate period actually has a smaller divisor period."""
  for candidatePeriod in range(1, period):
    if period % candidatePeriod != 0:
      continue

    if abs(iterateLogisticMap(rValue, xValue, candidatePeriod) - xValue) < periodTolerance:
      return True

  return False



def appendRootIfNew(rootList, xValue):
  """Append xValue only if it is not already represented in rootList."""
  for rootValue in rootList:
    if abs(rootValue - xValue) < periodTolerance:
      return

  rootList.append(xValue)



def findUnstablePeriodicRoots(rValue, period, xGrid, periodicIterates):
  """Find unstable points of exact period ``period`` for a fixed parameter r.

  Strategy:
    - detect roots of f^period(x) - x on a grid,
    - refine them by bisection when a sign change is found,
    - remove points of smaller period,
    - keep only the unstable ones using the multiplier test.
  """
  residual = periodicIterates[period] - xGrid
  rootList = []

  zeroIndices = np.where(np.abs(residual) < rootTolerance)[0]
  for zeroIndex in zeroIndices:
    appendRootIfNew(rootList, xGrid[zeroIndex])

  signChangeIndices = np.where(residual[:-1] * residual[1:] < 0.0)[0]
  for i in signChangeIndices:
    rootValue = bisectPeriodicRoot(
      rValue,
      period,
      xGrid[i],
      xGrid[i + 1],
      residual[i],
      residual[i + 1]
    )
    appendRootIfNew(rootList, rootValue)

  unstableRoots = []

  for xValue in rootList:
    if hasSmallerPeriod(rValue, xValue, period):
      continue

    _, multiplier = iterateLogisticMapAndMultiplier(rValue, xValue, period)
    if abs(multiplier) <= 1.0 + periodTolerance:
      continue

    unstableRoots.append(xValue)

  return unstableRoots



def computePeriodicIterates(rValue, xGrid):
  """Precompute f(x), f^2(x), ..., f^maxPeriod(x) on a grid."""
  periodicIterates = np.empty((maxPeriod + 1, xGrid.size))
  periodicIterates[0] = xGrid

  xIterate = xGrid.copy()
  for period in range(1, maxPeriod + 1):
    xIterate = logisticMapStep(rValue, xIterate)
    periodicIterates[period] = xIterate

  return periodicIterates



def computeUnstablePeriodicOverlay(progressCallback = None):
  """Compute overlay data for unstable periodic points up to maxPeriod."""
  rValues = np.linspace(rMin, rMax, nR)
  xGrid = np.linspace(0.0, 1.0, nPeriodicSearch)
  overlayByPeriod = {}

  for period in range(1, maxPeriod + 1):
    overlayByPeriod[period] = {
      "rValues": [],
      "xValues": []
    }

  nPoints = 0

  for i, rValue in enumerate(rValues):
    periodicIterates = computePeriodicIterates(rValue, xGrid)

    for period in range(1, maxPeriod + 1):
      unstableRoots = findUnstablePeriodicRoots(rValue, period, xGrid, periodicIterates)
      for xValue in unstableRoots:
        overlayByPeriod[period]["rValues"].append(rValue)
        overlayByPeriod[period]["xValues"].append(xValue)
        nPoints += 1

    if progressCallback is not None:
      if i == 0 or (i + 1) % progressStride == 0 or i + 1 == rValues.size:
        progressCallback(i + 1, rValues.size, nPoints)

  for period in range(1, maxPeriod + 1):
    overlayByPeriod[period]["rValues"] = np.array(overlayByPeriod[period]["rValues"])
    overlayByPeriod[period]["xValues"] = np.array(overlayByPeriod[period]["xValues"])

  return overlayByPeriod



def getOutputPath(showOverlay, extension):
  """Build the output path for exported figures."""
  outputDir = Path(__file__).resolve().parent
  suffix = "_withUnstableOverlay" if showOverlay else ""
  return outputDir / f"{outputStem}{suffix}.{extension}"



def saveFigure(fig, showOverlay, extension, statusText):
  """Save the current figure and display a short status message."""
  outputPath = getOutputPath(showOverlay, extension)
  fig.savefig(outputPath, dpi = 300, bbox_inches = 'tight')
  statusText.set_text(f"Saved {outputPath.name}")
  fig.canvas.draw_idle()



def styleCheckButtons(checkboxAxes, checkbox):
  """Apply a simple visual style to the checkbox panel."""
  checkboxAxes.set_facecolor('#f5f5f5')
  checkboxAxes.set_xticks([])
  checkboxAxes.set_yticks([])
  for spine in checkboxAxes.spines.values():
    spine.set_visible(False)

  for rectangle in checkbox.rectangles:
    rectangle.set_facecolor('white')
    rectangle.set_edgecolor('#666666')
    rectangle.set_linewidth(1.0)

  for lineGroup in checkbox.lines:
    for line in lineGroup:
      line.set_color('C3')
      line.set_linewidth(2.0)

  for label in checkbox.labels:
    label.set_fontsize(9)
    label.set_color('#222222')



def styleButton(button):
  """Apply a simple visual style to a button widget."""
  button.label.set_fontsize(9)
  button.label.set_color('#222222')



def main():
  """Create the interactive figure and register callbacks."""
  # Core dataset: this is the bifurcation diagram seen in class.
  rPlot, xPlot = computeBifurcationDiagram()

  fig, ax = plt.subplots(figsize = (10.5, 6.5))
  fig.subplots_adjust(top = 0.84)

  ax.plot(rPlot, xPlot, linestyle = 'None', marker = ',', color = 'black', alpha = 0.70)
  periodColors = {
    1: 'C3',
    2: 'C0',
    3: 'C2',
    4: 'C1'
  }
  unstableArtists = {}

  # These artists are initially empty. They are filled only if the user asks
  # for the advanced overlay of unstable periodic points.
  for period in range(1, maxPeriod + 1):
    unstableArtists[period], = ax.plot(
      [], [],
      linestyle = 'None',
      marker = '.',
      color = periodColors[period],
      markersize = 1.2,
      alpha = 0.45,
      visible = False,
      label = f"unstable period {period}"
    )

  ax.set_title("Bifurcation diagram of the logistic map")
  ax.set_xlabel(r"$r$")
  ax.set_ylabel(r"$x$")
  ax.set_xlim(rMin, rMax)
  ax.set_ylim(0.0, 1.0)
  ax.grid(True, linewidth = 0.3, alpha = 0.4)

  ax.text(
    0.02, 0.98,
    rf"{nR:d} parameter values" "\n"
    rf"{nTransient:d} transient iterates" "\n"
    rf"{nRecorded:d} recorded iterates",
    transform = ax.transAxes,
    ha = 'left',
    va = 'top',
    bbox = dict(facecolor = 'white', alpha = 0.88, edgecolor = 'none')
  )

  panelTitle = fig.text(
    0.12, 0.94,
    "Overlay and export tools",
    ha = 'left',
    va = 'center',
    fontsize = 10,
    color = '#222222',
    bbox = dict(facecolor = '#f5f5f5', edgecolor = 'none', boxstyle = 'round,pad=0.25')
  )
  panelTitle.set_in_layout(False)

  statusText = fig.text(
    0.44, 0.94,
    "",
    ha = 'left',
    va = 'center',
    fontsize = 9,
    color = '#333333',
    bbox = dict(facecolor = 'white', alpha = 0.85, edgecolor = 'none', boxstyle = 'round,pad=0.25')
  )
  statusText.set_in_layout(False)

  checkboxAxes = fig.add_axes([0.12, 0.865, 0.28, 0.055])
  checkbox = CheckButtons(checkboxAxes, ["Show unstable periodic points (period <= 4)"], [False])
  styleCheckButtons(checkboxAxes, checkbox)

  pngButtonAxes = fig.add_axes([0.76, 0.872, 0.10, 0.05])
  pdfButtonAxes = fig.add_axes([0.87, 0.872, 0.10, 0.05])
  pngButton = Button(pngButtonAxes, "Save PNG", color = '#f5f5f5', hovercolor = '#e6e6e6')
  pdfButton = Button(pdfButtonAxes, "Save PDF", color = '#f5f5f5', hovercolor = '#e6e6e6')
  styleButton(pngButton)
  styleButton(pdfButton)

  legendHandles = [
    plt.Line2D([], [], linestyle = 'None', marker = '.', color = periodColors[period], markersize = 6, label = f"period {period}")
    for period in range(1, maxPeriod + 1)
  ]
  legend = ax.legend(
    handles = legendHandles,
    loc = 'lower right',
    title = 'Unstable periodic points',
    framealpha = 0.9,
    fontsize = 8,
    title_fontsize = 9
  )
  legend.set_visible(False)

  overlayCache = {
    "computed": False,
    "overlayByPeriod": {}
  }

  def updateProgress(iValue, nValue, nPoints):
    """Display progress while computing the unstable overlay."""
    fraction = 100.0 * iValue / nValue
    statusText.set_text(
      f"Computing overlay: {fraction:5.1f}%   ({iValue}/{nValue} r-values, {nPoints} points)"
    )
    fig.canvas.draw_idle()
    plt.pause(0.001)

  def updateOverlay(_):
    """Toggle the advanced overlay of unstable periodic points."""
    showOverlay = checkbox.get_status()[0]

    if showOverlay and not overlayCache["computed"]:
      statusText.set_text("Computing overlay:   0.0%")
      fig.canvas.draw_idle()
      plt.pause(0.001)

      startTime = time.time()
      overlayByPeriod = computeUnstablePeriodicOverlay(progressCallback = updateProgress)
      elapsedTime = time.time() - startTime

      overlayCache["computed"] = True
      overlayCache["overlayByPeriod"] = overlayByPeriod

      nTotal = 0
      for period in range(1, maxPeriod + 1):
        rValuesPeriod = overlayByPeriod[period]["rValues"]
        xValuesPeriod = overlayByPeriod[period]["xValues"]
        unstableArtists[period].set_data(rValuesPeriod, xValuesPeriod)
        nTotal += xValuesPeriod.size

      statusText.set_text(
        f"Overlay ready: {nTotal:d} points in {elapsedTime:.1f} s"
      )

    for period in range(1, maxPeriod + 1):
      unstableArtists[period].set_visible(showOverlay)

    legend.set_visible(showOverlay)

    if not showOverlay:
      statusText.set_text("")

    fig.canvas.draw_idle()

  def savePng(_):
    """Save the current figure as PNG."""
    saveFigure(fig, checkbox.get_status()[0], 'png', statusText)

  def savePdf(_):
    """Save the current figure as PDF."""
    saveFigure(fig, checkbox.get_status()[0], 'pdf', statusText)

  checkbox.on_clicked(updateOverlay)
  pngButton.on_clicked(savePng)
  pdfButton.on_clicked(savePdf)

  plt.show()



if __name__ == "__main__":
  main()
