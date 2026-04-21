"""
 * greenbergHastingsInteractive.py
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

"""Interactive Greenberg-Hastings cellular automaton for classroom demos.

Usage:
  python greenbergHastingsInteractive.py
  python greenbergHastingsInteractive.py --size 120 --states 8 --excited 2
  python greenbergHastingsInteractive.py --seed 9

Controls:
  - Click a cell to cycle through the states 0, 1, ..., N-1.
  - Press Run to start or pause the simulation.
  - Press Step to advance one time step.
  - Press Clear to reset the grid to state 0.
  - Press Random to seed a random initial condition.
  - Press Seed to place a compact excited patch at the center.

The simulation uses zero boundary conditions outside the visible grid.
"""

import argparse

import matplotlib.colors as mcolors
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.widgets import Button


defaultSize = 100
defaultStates = 8
defaultExcited = 2
defaultIntervalMs = 120
defaultRandomOccupancy = 0.10
defaultRandomPatchScale = 0.18


def parseArguments():
  parser = argparse.ArgumentParser(description = "Interactive Greenberg-Hastings cellular automaton")
  parser.add_argument("--size", type = int, default = defaultSize, help = "grid size in each direction")
  parser.add_argument("--states", type = int, default = defaultStates, help = "number of states N")
  parser.add_argument("--excited", type = int, default = defaultExcited, help = "number of excited states e")
  parser.add_argument("--interval", type = int, default = defaultIntervalMs, help = "animation interval in milliseconds")
  parser.add_argument("--random-occupancy", type = float, default = defaultRandomOccupancy, help = "fraction of nonzero cells in random initialization")
  parser.add_argument("--random-patch-scale", type = float, default = defaultRandomPatchScale, help = "side length of the random patch as a fraction of the grid size")
  parser.add_argument("--seed", type = int, default = None, help = "random seed for reproducible demos")
  args = parser.parse_args()

  if args.size < 10:
    parser.error("--size must be at least 10")

  if args.states < 3:
    parser.error("--states must be at least 3")

  if args.excited < 1 or args.excited > args.states - 2:
    parser.error("--excited must satisfy 1 <= e <= N - 2")

  if args.interval < 10:
    parser.error("--interval must be at least 10 ms")

  if args.random_occupancy < 0.0 or args.random_occupancy > 1.0:
    parser.error("--random-occupancy must lie in [0, 1]")

  if args.random_patch_scale <= 0.0 or args.random_patch_scale > 1.0:
    parser.error("--random-patch-scale must lie in (0, 1]")

  return args


def greenbergHastingsStep(grid, nStates, nExcited):
  """Return one Greenberg-Hastings update with zero boundary conditions."""
  padded = np.pad(grid, 1, mode = "constant")
  north = padded[:-2, 1:-1]
  south = padded[2:, 1:-1]
  west = padded[1:-1, :-2]
  east = padded[1:-1, 2:]

  neighborIsExcited = (
    ((north >= 1) & (north <= nExcited)) |
    ((south >= 1) & (south <= nExcited)) |
    ((west >= 1) & (west <= nExcited)) |
    ((east >= 1) & (east <= nExcited))
  )

  nextGrid = np.zeros_like(grid)
  activeMask = grid > 0
  nextGrid[activeMask] = (grid[activeMask] + 1) % nStates
  nextGrid[(grid == 0) & neighborIsExcited] = 1
  return nextGrid


def buildColormap(nStates, nExcited):
  colors = [(0.96, 0.96, 0.98)]

  for index in range(1, nExcited + 1):
    fraction = (index - 1) / max(1, nExcited - 1)
    colors.append((1.0, 0.85 - 0.25 * fraction, 0.15 + 0.45 * fraction))

  recoveryCount = nStates - 1 - nExcited
  for index in range(recoveryCount):
    fraction = index / max(1, recoveryCount - 1) if recoveryCount > 0 else 0.0
    colors.append((0.55 - 0.20 * fraction, 0.25 + 0.35 * fraction, 0.80))

  return mcolors.ListedColormap(colors[:nStates])


class GreenbergHastingsApp:
  def __init__(self, nRows, nCols, nStates, nExcited, updateIntervalMs, randomOccupancy, randomPatchScale, randomSeed):
    self.nRows = nRows
    self.nCols = nCols
    self.nStates = nStates
    self.nExcited = nExcited
    self.randomOccupancy = randomOccupancy
    self.randomPatchScale = randomPatchScale
    self.grid = np.zeros((nRows, nCols), dtype = int)
    self.isRunning = False
    self.stepCount = 0
    self.randomSeed = randomSeed
    self.rng = np.random.default_rng(randomSeed)
    self.cmap = buildColormap(nStates, nExcited)

    self.fig = plt.figure(figsize = (12, 9))
    self.ax = self.fig.add_axes([0.05, 0.08, 0.70, 0.84])
    self.image = self.ax.imshow(
      self.grid,
      cmap = self.cmap,
      interpolation = "nearest",
      vmin = 0,
      vmax = nStates - 1,
      origin = "upper",
    )

    self.ax.set_title(
      f"Greenberg-Hastings CA (N = {nStates}, e = {nExcited}, {nRows} x {nCols})",
      fontsize = 14,
    )
    self.ax.set_xticks(np.arange(-0.5, nCols, 1), minor = True)
    self.ax.set_yticks(np.arange(-0.5, nRows, 1), minor = True)
    self.ax.grid(which = "minor", color = "lightgray", linewidth = 0.20)
    self.ax.tick_params(which = "both", bottom = False, left = False, labelbottom = False, labelleft = False)

    colorbarAxis = self.fig.add_axes([0.05, 0.94, 0.70, 0.02])
    norm = mcolors.BoundaryNorm(np.arange(-0.5, nStates + 0.5, 1), self.cmap.N)
    colorbar = plt.colorbar(
      plt.cm.ScalarMappable(norm = norm, cmap = self.cmap),
      cax = colorbarAxis,
      orientation = "horizontal",
    )
    colorbar.set_label("state", fontsize = 10)
    colorbar.set_ticks(range(nStates))

    self.statusText = self.fig.text(
      0.05,
      0.02,
      "Click cells to change state. State 0 rests, states 1..e are excited.",
      fontsize = 11,
    )

    self.stepText = self.fig.text(
      0.80,
      0.31,
      "Step: 0",
      fontsize = 11,
    )

    boundaryLabel = "Boundary: zero outside box"
    if randomSeed is not None:
      boundaryLabel += f"\nRNG seed: {randomSeed}"

    self.fig.text(
      0.80,
      0.27,
      boundaryLabel,
      fontsize = 10,
      va = "top",
    )

    self.timer = self.fig.canvas.new_timer(interval = updateIntervalMs)
    self.timer.add_callback(self.advanceOneStep)

    self.runButton = self._makeButton([0.80, 0.80, 0.15, 0.06], "Run", self.toggleRun)
    self.stepButton = self._makeButton([0.80, 0.72, 0.15, 0.06], "Step", self.stepOnce)
    self.clearButton = self._makeButton([0.80, 0.64, 0.15, 0.06], "Clear", self.clearGrid)
    self.randomButton = self._makeButton([0.80, 0.56, 0.15, 0.06], "Random", self.randomizeGrid)
    self.seedButton = self._makeButton([0.80, 0.48, 0.15, 0.06], "Seed", self.seedCenter)
    self.singleButton = self._makeButton([0.80, 0.40, 0.15, 0.06], "Single", self.seedSingleCell)

    self.fig.text(
      0.79,
      0.16,
      "Rule:\n"
      "k -> k+1 for 1 <= k <= N-2\n"
      "N-1 -> 0\n"
      "0 -> 1 if a von Neumann\n"
      "neighbor is in 1..e",
      fontsize = 10,
      va = "top",
    )

    self.fig.canvas.mpl_connect("button_press_event", self.onMousePress)
    self.fig.canvas.mpl_connect("close_event", self.onClose)

  def _makeButton(self, rect, label, callback):
    axis = self.fig.add_axes(rect)
    button = Button(axis, label)
    button.on_clicked(callback)
    return button

  def gridCoordinates(self, event):
    if event.inaxes != self.ax or event.xdata is None or event.ydata is None:
      return None

    col = int(np.floor(event.xdata + 0.5))
    row = int(np.floor(event.ydata + 0.5))

    if row < 0 or row >= self.nRows or col < 0 or col >= self.nCols:
      return None

    return row, col

  def refreshDisplay(self):
    self.image.set_data(self.grid)
    self.stepText.set_text(f"Step: {self.stepCount}")
    self.fig.canvas.draw_idle()

  def updateStatus(self, text):
    self.statusText.set_text(text)
    self.fig.canvas.draw_idle()

  def onMousePress(self, event):
    coordinates = self.gridCoordinates(event)
    if coordinates is None:
      return

    row, col = coordinates
    self.grid[row, col] = (self.grid[row, col] + 1) % self.nStates
    self.refreshDisplay()
    self.updateStatus(f"Cell ({row}, {col}) set to state {self.grid[row, col]}.")

  def resetStepCount(self):
    self.stepCount = 0

  def toggleRun(self, _event):
    if self.isRunning:
      self.isRunning = False
      self.timer.stop()
      self.runButton.label.set_text("Run")
      self.updateStatus("Simulation paused.")
    else:
      self.isRunning = True
      self.timer.start()
      self.runButton.label.set_text("Pause")
      self.updateStatus("Simulation running.")
      self.fig.canvas.draw_idle()

  def stepOnce(self, _event):
    if self.isRunning:
      self.toggleRun(None)

    self.advanceOneStep()
    self.updateStatus("Advanced one time step.")

  def advanceOneStep(self):
    self.grid = greenbergHastingsStep(self.grid, self.nStates, self.nExcited)
    self.stepCount += 1
    self.refreshDisplay()

  def clearGrid(self, _event):
    if self.isRunning:
      self.toggleRun(None)

    self.grid.fill(0)
    self.resetStepCount()
    self.refreshDisplay()
    self.updateStatus("Grid cleared to the resting state.")

  def randomizeGrid(self, _event):
    if self.isRunning:
      self.toggleRun(None)

    self.grid.fill(0)
    self.resetStepCount()

    patchHalfWidth = max(1, int(round(0.5 * self.randomPatchScale * min(self.nRows, self.nCols))))
    centerRow = self.nRows // 2
    centerCol = self.nCols // 2
    rowStart = max(0, centerRow - patchHalfWidth)
    rowStop = min(self.nRows, centerRow + patchHalfWidth + 1)
    colStart = max(0, centerCol - patchHalfWidth)
    colStop = min(self.nCols, centerCol + patchHalfWidth + 1)

    patchShape = (rowStop - rowStart, colStop - colStart)
    occupied = self.rng.random(patchShape) < self.randomOccupancy
    randomStates = self.rng.integers(1, self.nStates, size = occupied.sum())
    self.grid[rowStart:rowStop, colStart:colStop][occupied] = randomStates
    self.refreshDisplay()
    self.updateStatus("Random finite patch generated near the center.")

  def seedCenter(self, _event):
    if self.isRunning:
      self.toggleRun(None)

    self.grid.fill(0)
    self.resetStepCount()
    centerRow = self.nRows // 2
    centerCol = self.nCols // 2
    seedRadius = min(self.nRows, self.nCols) // 12

    for row in range(centerRow - seedRadius, centerRow + seedRadius + 1):
      for col in range(centerCol - seedRadius, centerCol + seedRadius + 1):
        if row < 0 or row >= self.nRows or col < 0 or col >= self.nCols:
          continue

        distance = abs(row - centerRow) + abs(col - centerCol)
        if distance <= seedRadius:
          self.grid[row, col] = 1 + (distance % max(1, self.nExcited))

    self.refreshDisplay()
    self.updateStatus("Placed a compact excited seed at the center.")

  def seedSingleCell(self, _event):
    if self.isRunning:
      self.toggleRun(None)

    self.grid.fill(0)
    self.resetStepCount()
    self.grid[self.nRows // 2, self.nCols // 2] = 1
    self.refreshDisplay()
    self.updateStatus("Placed one excited cell at the center.")

  def onClose(self, _event):
    self.timer.stop()

  def show(self):
    plt.show()


def main():
  args = parseArguments()
  app = GreenbergHastingsApp(
    nRows = args.size,
    nCols = args.size,
    nStates = args.states,
    nExcited = args.excited,
    updateIntervalMs = args.interval,
    randomOccupancy = args.random_occupancy,
    randomPatchScale = args.random_patch_scale,
    randomSeed = args.seed,
  )
  app.seedCenter(None)
  app.show()


if __name__ == "__main__":
  main()
