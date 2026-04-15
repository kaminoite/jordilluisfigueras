"""
 * gameOfLifeInteractive.py
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

"""Interactive Conway's Game of Life board for classroom demonstrations.

Usage:
  - Click on the grid to toggle cells before or during the simulation.
  - Press Run to start the evolution.
  - Press Pause to stop it.
  - Step advances one generation.
  - Clear resets the board.
  - Random fills the board with a random initial condition.

The default boundary condition is zero outside the finite board, which is often
easier to interpret in class than periodic wrapping.
"""

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.widgets import Button


nRows = 30
nCols = 50
updateIntervalMs = 150
randomOccupancy = 0.22
rulesText = (
  "Conway's Game of Life rules\n\n"
  "1. Survival: a live cell stays alive if it has 2 or 3 live neighbors.\n"
  "2. Birth: a dead cell becomes alive if it has exactly 3 live neighbors.\n"
  "3. Death by isolation: a live cell dies if it has fewer than 2 live neighbors.\n"
  "4. Death by overcrowding: a live cell dies if it has more than 3 live neighbors.\n\n"
  "Neighbors are the 8 surrounding cells."
)


def lifeStep(grid):
  """Return one Game-of-Life update with zero boundary conditions."""
  padded = np.pad(grid, 1, mode = "constant")
  neighbors = (
    padded[:-2, :-2] + padded[:-2, 1:-1] + padded[:-2, 2:] +
    padded[1:-1, :-2] +                         padded[1:-1, 2:] +
    padded[2:, :-2] +  padded[2:, 1:-1] +  padded[2:, 2:]
  )

  born = (grid == 0) & (neighbors == 3)
  survive = (grid == 1) & ((neighbors == 2) | (neighbors == 3))
  return (born | survive).astype(int)


class GameOfLifeApp:
  def __init__(self):
    self.grid = np.zeros((nRows, nCols), dtype = int)
    self.isRunning = False
    self.isMouseDown = False
    self.drawValue = 1
    self.rulesFigure = None

    self.fig = plt.figure(figsize = (11, 7))
    self.ax = self.fig.add_axes([0.05, 0.12, 0.72, 0.82])
    self.image = self.ax.imshow(
      self.grid,
      cmap = "binary",
      interpolation = "nearest",
      vmin = 0,
      vmax = 1,
      origin = "upper",
    )

    self.ax.set_title("Conway's Game of Life", fontsize = 14)
    self.ax.set_xticks(np.arange(-0.5, nCols, 1), minor = True)
    self.ax.set_yticks(np.arange(-0.5, nRows, 1), minor = True)
    self.ax.grid(which = "minor", color = "lightgray", linewidth = 0.45)
    self.ax.tick_params(which = "both", bottom = False, left = False, labelbottom = False, labelleft = False)

    self.statusText = self.fig.text(
      0.05,
      0.04,
      "Click cells to toggle them. Press Run to evolve the pattern.",
      fontsize = 11,
    )

    self.timer = self.fig.canvas.new_timer(interval = updateIntervalMs)
    self.timer.add_callback(self.advanceOneStep)

    self.runButton = self._makeButton([0.82, 0.78, 0.13, 0.07], "Run", self.toggleRun)
    self.stepButton = self._makeButton([0.82, 0.68, 0.13, 0.07], "Step", self.stepOnce)
    self.clearButton = self._makeButton([0.82, 0.58, 0.13, 0.07], "Clear", self.clearGrid)
    self.randomButton = self._makeButton([0.82, 0.48, 0.13, 0.07], "Random", self.randomizeGrid)
    self.rulesButton = self._makeButton([0.82, 0.38, 0.13, 0.07], "Rules", self.showRules)

    self.fig.canvas.mpl_connect("button_press_event", self.onMousePress)
    self.fig.canvas.mpl_connect("button_release_event", self.onMouseRelease)
    self.fig.canvas.mpl_connect("motion_notify_event", self.onMouseMove)
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

    if row < 0 or row >= nRows or col < 0 or col >= nCols:
      return None

    return row, col

  def refreshDisplay(self):
    self.image.set_data(self.grid)
    self.fig.canvas.draw_idle()

  def updateStatus(self, text):
    self.statusText.set_text(text)
    self.fig.canvas.draw_idle()

  def paintCell(self, row, col, value):
    if self.grid[row, col] != value:
      self.grid[row, col] = value
      self.refreshDisplay()

  def onMousePress(self, event):
    coordinates = self.gridCoordinates(event)
    if coordinates is None:
      return

    row, col = coordinates
    self.isMouseDown = True
    self.drawValue = 1 - self.grid[row, col]
    self.paintCell(row, col, self.drawValue)

  def onMouseMove(self, event):
    if not self.isMouseDown:
      return

    coordinates = self.gridCoordinates(event)
    if coordinates is None:
      return

    row, col = coordinates
    self.paintCell(row, col, self.drawValue)

  def onMouseRelease(self, _event):
    self.isMouseDown = False

  def toggleRun(self, _event):
    if self.isRunning:
      self.isRunning = False
      self.timer.stop()
      self.runButton.label.set_text("Run")
      self.updateStatus("Simulation paused. You can keep editing the grid.")
    else:
      self.isRunning = True
      self.timer.start()
      self.runButton.label.set_text("Pause")
      self.updateStatus("Simulation running. Click cells to perturb the pattern if you wish.")
      self.fig.canvas.draw_idle()

  def stepOnce(self, _event):
    if self.isRunning:
      self.toggleRun(None)

    self.advanceOneStep()
    self.updateStatus("Advanced one generation.")

  def clearGrid(self, _event):
    if self.isRunning:
      self.toggleRun(None)

    self.grid.fill(0)
    self.refreshDisplay()
    self.updateStatus("Grid cleared.")

  def randomizeGrid(self, _event):
    if self.isRunning:
      self.toggleRun(None)

    self.grid = (np.random.random((nRows, nCols)) < randomOccupancy).astype(int)
    self.refreshDisplay()
    self.updateStatus("Random initial condition loaded.")

  def showRules(self, _event):
    if self.rulesFigure is not None and plt.fignum_exists(self.rulesFigure.number):
      self.rulesFigure.canvas.manager.show()
      self.rulesFigure.canvas.draw_idle()
      return

    self.rulesFigure = plt.figure(figsize = (6.5, 3.8))
    self.rulesFigure.suptitle("Game of Life Rules", fontsize = 13)
    rulesAxis = self.rulesFigure.add_axes([0.06, 0.08, 0.88, 0.8])
    rulesAxis.axis("off")
    rulesAxis.text(0.0, 1.0, rulesText, va = "top", fontsize = 11, wrap = True)
    self.rulesFigure.canvas.draw_idle()

  def advanceOneStep(self):
    self.grid = lifeStep(self.grid)
    self.refreshDisplay()

  def onClose(self, _event):
    self.timer.stop()


def main():
  app = GameOfLifeApp()
  plt.show()


if __name__ == "__main__":
  main()
