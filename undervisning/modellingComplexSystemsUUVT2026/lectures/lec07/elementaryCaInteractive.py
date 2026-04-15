"""
 * elementaryCaInteractive.py
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

"""Interactive elementary cellular automaton for classroom demonstrations.

Usage:
  - Click on the top row to edit the initial state.
  - Press Run to generate the spacetime diagram row by row.
  - Press Pause to stop it.
  - Step advances one time step.
  - Clear resets the initial state.
  - Random fills the initial row randomly.
  - Use the dropdown menu to switch between Rules 8, 50, 30, and 110.

The horizontal axis is the cell index, and the vertical axis is time.
The update uses zero boundary conditions outside the finite row.
"""

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.widgets import Button


nSteps = 80
nCells = 121
updateIntervalMs = 120
randomOccupancy = 0.18
allowedRules = [8, 50, 30, 110]
rulesText = (
  "Elementary cellular automata\n\n"
  "At each time step, each cell looks at the neighborhood\n"
  "(left, center, right). The 8 possible neighborhoods are:\n"
  "111, 110, 101, 100, 011, 010, 001, 000.\n\n"
  "The rule specifies the new center cell for each of these 8 cases.\n\n"
  "Rule 8:\n"
  "111->0, 110->0, 101->0, 100->0, 011->1, 010->0, 001->0, 000->0\n\n"
  "Rule 50:\n"
  "111->0, 110->0, 101->1, 100->1, 011->0, 010->0, 001->1, 000->0\n\n"
  "Rule 30:\n"
  "111->0, 110->0, 101->0, 100->1, 011->1, 010->1, 001->1, 000->0\n\n"
  "Rule 110:\n"
  "111->0, 110->1, 101->1, 100->0, 011->1, 010->1, 001->1, 000->0"
)


def ruleToTable(ruleNumber):
  table = {}
  for pattern in range(8):
    bits = ((pattern >> 2) & 1, (pattern >> 1) & 1, pattern & 1)
    table[bits] = (ruleNumber >> pattern) & 1
  return table


def elementaryStep(state, ruleNumber):
  """Return one elementary cellular automaton update with zero boundaries."""
  padded = np.pad(state, 1, mode = "constant")
  left = padded[:-2]
  center = padded[1:-1]
  right = padded[2:]
  patternIndex = 4 * left + 2 * center + right
  return ((ruleNumber >> patternIndex) & 1).astype(int)


class ElementaryCaApp:
  def __init__(self):
    self.ruleIndex = 0
    self.ruleNumber = allowedRules[self.ruleIndex]
    self.initialState = np.zeros(nCells, dtype = int)
    self.grid = np.zeros((nSteps, nCells), dtype = int)
    self.grid[0] = self.initialState
    self.currentStep = 0
    self.isRunning = False
    self.isMouseDown = False
    self.drawValue = 1
    self.rulesFigure = None
    self.ruleMenuButtons = []
    self.ruleMenuAxes = []
    self.isRuleMenuOpen = False

    self.fig = plt.figure(figsize = (11, 7))
    self.ax = self.fig.add_axes([0.05, 0.18, 0.72, 0.76])
    self.image = self.ax.imshow(
      self.grid,
      cmap = "binary",
      interpolation = "nearest",
      vmin = 0,
      vmax = 1,
      origin = "upper",
      aspect = "auto",
    )

    self.ax.set_title(f"Elementary Cellular Automaton (Rule {self.ruleNumber})", fontsize = 14)
    self.ax.set_xlabel("cell index", fontsize = 11)
    self.ax.set_ylabel("time", fontsize = 11)
    self.ax.set_xticks(np.arange(-0.5, nCells, 1), minor = True)
    self.ax.set_yticks(np.arange(-0.5, nSteps, 1), minor = True)
    self.ax.grid(which = "minor", color = "lightgray", linewidth = 0.3)
    self.ax.tick_params(which = "minor", bottom = False, left = False)

    self.statusText = self.fig.text(
      0.05,
      0.06,
      "Click the top row to edit the initial state. Press Run to evolve it.",
      fontsize = 11,
    )

    self.timer = self.fig.canvas.new_timer(interval = updateIntervalMs)
    self.timer.add_callback(self.advanceOneStep)

    self.runButton = self._makeButton([0.82, 0.80, 0.13, 0.07], "Run", self.toggleRun)
    self.stepButton = self._makeButton([0.82, 0.70, 0.13, 0.07], "Step", self.stepOnce)
    self.clearButton = self._makeButton([0.82, 0.60, 0.13, 0.07], "Clear", self.clearInitialState)
    self.randomButton = self._makeButton([0.82, 0.50, 0.13, 0.07], "Random", self.randomizeInitialState)
    self.ruleButton = self._makeButton([0.82, 0.40, 0.13, 0.07], f"Rule {self.ruleNumber}", self.toggleRuleMenu)
    self.rulesButton = self._makeButton([0.82, 0.18, 0.13, 0.07], "Rules", self.showRules)
    self._makeRuleMenu()

    self.fig.canvas.mpl_connect("button_press_event", self.onMousePress)
    self.fig.canvas.mpl_connect("button_release_event", self.onMouseRelease)
    self.fig.canvas.mpl_connect("motion_notify_event", self.onMouseMove)
    self.fig.canvas.mpl_connect("close_event", self.onClose)

  def _makeButton(self, rect, label, callback):
    axis = self.fig.add_axes(rect)
    button = Button(axis, label)
    button.on_clicked(callback)
    return button

  def _makeRuleMenu(self):
    menuTop = 0.33
    menuHeight = 0.05
    for index, ruleNumber in enumerate(allowedRules):
      axis = self.fig.add_axes([0.82, menuTop - index * menuHeight, 0.13, menuHeight])
      axis.set_visible(False)
      button = Button(axis, str(ruleNumber), hovercolor = "0.9")
      button.on_clicked(self.selectRuleFactory(index))
      self.ruleMenuAxes.append(axis)
      self.ruleMenuButtons.append(button)

  def toggleRuleMenu(self, _event):
    self.isRuleMenuOpen = not self.isRuleMenuOpen
    for axis in self.ruleMenuAxes:
      axis.set_visible(self.isRuleMenuOpen)
    self.fig.canvas.draw_idle()

  def closeRuleMenu(self):
    if not self.isRuleMenuOpen:
      return
    self.isRuleMenuOpen = False
    for axis in self.ruleMenuAxes:
      axis.set_visible(False)
    self.fig.canvas.draw_idle()

  def selectRuleFactory(self, ruleIndex):
    def callback(_event):
      self.changeRule(ruleIndex)
      self.closeRuleMenu()
    return callback

  def cellCoordinates(self, event):
    if event.inaxes != self.ax or event.xdata is None or event.ydata is None:
      return None

    col = int(np.floor(event.xdata + 0.5))
    row = int(np.floor(event.ydata + 0.5))

    if row < 0 or row >= nSteps or col < 0 or col >= nCells:
      return None

    return row, col

  def refreshDisplay(self):
    self.image.set_data(self.grid)
    self.ax.set_title(f"Elementary Cellular Automaton (Rule {self.ruleNumber})", fontsize = 14)
    self.fig.canvas.draw_idle()

  def updateStatus(self, text):
    self.statusText.set_text(text)
    self.fig.canvas.draw_idle()

  def resetEvolution(self):
    self.grid.fill(0)
    self.grid[0] = self.initialState
    self.currentStep = 0
    self.refreshDisplay()

  def paintInitialCell(self, col, value):
    if self.initialState[col] != value:
      self.initialState[col] = value
      self.resetEvolution()

  def onMousePress(self, event):
    if self.isRuleMenuOpen:
      inRuleMenu = event.inaxes in self.ruleMenuAxes
      inRuleButton = event.inaxes == self.ruleButton.ax
      if not inRuleMenu and not inRuleButton:
        self.closeRuleMenu()

    coordinates = self.cellCoordinates(event)
    if coordinates is None:
      return

    row, col = coordinates
    if row != 0:
      return

    self.isMouseDown = True
    self.drawValue = 1 - self.initialState[col]
    self.paintInitialCell(col, self.drawValue)
    self.updateStatus("Initial row edited. Press Run to generate the spacetime diagram.")

  def onMouseMove(self, event):
    if not self.isMouseDown:
      return

    coordinates = self.cellCoordinates(event)
    if coordinates is None:
      return

    row, col = coordinates
    if row != 0:
      return

    self.paintInitialCell(col, self.drawValue)

  def onMouseRelease(self, _event):
    self.isMouseDown = False

  def toggleRun(self, _event):
    if self.isRunning:
      self.isRunning = False
      self.timer.stop()
      self.runButton.label.set_text("Run")
      self.updateStatus("Simulation paused. You can keep editing the initial row.")
    else:
      if self.currentStep >= nSteps - 1:
        self.updateStatus("The time window is full. Edit, clear, or randomize to restart.")
        return

      self.isRunning = True
      self.timer.start()
      self.runButton.label.set_text("Pause")
      self.updateStatus(f"Simulation running with Rule {self.ruleNumber}.")
      self.fig.canvas.draw_idle()

  def stepOnce(self, _event):
    if self.isRunning:
      self.toggleRun(None)

    advanced = self.advanceOneStep()
    if advanced:
      self.updateStatus(f"Advanced to time {self.currentStep} with Rule {self.ruleNumber}.")

  def clearInitialState(self, _event):
    if self.isRunning:
      self.toggleRun(None)

    self.initialState.fill(0)
    self.resetEvolution()
    self.updateStatus("Initial row cleared.")

  def randomizeInitialState(self, _event):
    if self.isRunning:
      self.toggleRun(None)

    self.initialState = (np.random.random(nCells) < randomOccupancy).astype(int)
    self.resetEvolution()
    self.updateStatus("Random initial row loaded.")

  def changeRule(self, value):
    newRuleIndex = int(value)
    newRuleNumber = allowedRules[newRuleIndex]
    if newRuleNumber == self.ruleNumber:
      return

    if self.isRunning:
      self.toggleRun(None)

    self.ruleIndex = newRuleIndex
    self.ruleNumber = newRuleNumber
    self.ruleButton.label.set_text(f"Rule {self.ruleNumber}")
    self.resetEvolution()
    self.updateStatus(f"Rule changed to {self.ruleNumber}. The spacetime diagram was reset.")

  def showRules(self, _event):
    if self.rulesFigure is not None and plt.fignum_exists(self.rulesFigure.number):
      self.rulesFigure.canvas.manager.show()
      self.rulesFigure.canvas.draw_idle()
      return

    self.rulesFigure = plt.figure(figsize = (6.6, 3.8))
    self.rulesFigure.suptitle("Elementary Cellular Automata", fontsize = 13)
    rulesAxis = self.rulesFigure.add_axes([0.06, 0.08, 0.88, 0.8])
    rulesAxis.axis("off")
    rulesAxis.text(0.0, 1.0, rulesText, va = "top", fontsize = 11, wrap = True)
    self.rulesFigure.canvas.draw_idle()

  def advanceOneStep(self):
    if self.currentStep >= nSteps - 1:
      if self.isRunning:
        self.toggleRun(None)
      self.updateStatus("Reached the bottom of the time window.")
      return False

    currentState = self.grid[self.currentStep]
    self.grid[self.currentStep + 1] = elementaryStep(currentState, self.ruleNumber)
    self.currentStep += 1
    self.refreshDisplay()

    if self.currentStep >= nSteps - 1 and self.isRunning:
      self.toggleRun(None)
      self.updateStatus("Reached the bottom of the time window.")

    return True

  def onClose(self, _event):
    self.timer.stop()


def main():
  app = ElementaryCaApp()
  plt.show()


if __name__ == "__main__":
  main()
