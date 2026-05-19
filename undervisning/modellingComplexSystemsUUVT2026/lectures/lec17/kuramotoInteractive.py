#!/usr/bin/env python3
"""Interactive Kuramoto-model demo for Lecture 17.

The script shows the all-to-all Kuramoto model

  theta_i' = omega_i + K r sin(varphi - theta_i),

where

  r exp(i varphi) = (1/N) sum_j exp(i theta_j).

Oscillators are displayed as moving points on the unit circle.  The red vector
is the complex order parameter, with length r and angle varphi.  Changing the
coupling slider resets the simulation to the current initial condition so that
different values of K can be compared directly.
"""

import argparse

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.widgets import Button, Slider


defaultNumOscillators = 80
defaultFrequencySpread = 1.0
defaultTimeStep = 0.03
defaultIntervalMs = 40
defaultKMin = 0.0
defaultKMax = 4.0
defaultKInitial = 0.5
defaultSeed = 17


def computeOrderParameter(angles):
  """Return the complex Kuramoto order parameter."""
  return np.mean(np.exp(1j*angles))


def advanceKuramoto(angles, frequencies, coupling, timeStep):
  """Advance one Euler step of the all-to-all Kuramoto model."""
  orderParameter = computeOrderParameter(angles)
  coherence = abs(orderParameter)
  meanPhase = np.angle(orderParameter)
  angularVelocity = frequencies + coupling*coherence*np.sin(meanPhase - angles)
  return (angles + timeStep*angularVelocity) % (2*np.pi)


def makeInitialData(numOscillators, frequencySpread, rng):
  """Create natural frequencies and initial phases."""
  frequencies = rng.normal(0.0, frequencySpread, numOscillators)
  frequencies -= np.mean(frequencies)
  angles = rng.uniform(0.0, 2*np.pi, numOscillators)
  return angles, frequencies


def validateArguments(parser, args):
  """Validate command-line arguments."""
  if args.num_oscillators < 2:
    parser.error("--num-oscillators must be at least 2")

  if args.frequency_spread < 0.0:
    parser.error("--frequency-spread must be nonnegative")

  if args.time_step <= 0.0:
    parser.error("--time-step must be positive")

  if args.interval < 10:
    parser.error("--interval must be at least 10 ms")

  if args.k_min >= args.k_max:
    parser.error("--k-min must be smaller than --k-max")

  if args.k_initial < args.k_min or args.k_initial > args.k_max:
    parser.error("--k-initial must lie between --k-min and --k-max")


class KuramotoInteractiveApp:
  """Interactive visualization of coupled phase oscillators."""
  def __init__(self, args):
    self.numOscillators = args.num_oscillators
    self.frequencySpread = args.frequency_spread
    self.timeStep = args.time_step
    self.coupling = args.k_initial
    self.rng = np.random.default_rng(args.seed)
    self.isRunning = False
    self.stepCount = 0
    self.time = 0.0

    self.initialAngles, self.frequencies = makeInitialData(
      self.numOscillators,
      self.frequencySpread,
      self.rng,
    )
    self.angles = self.initialAngles.copy()

    self.fig = plt.figure(figsize = (12, 8))
    self.ax = self.fig.add_axes([0.06, 0.12, 0.62, 0.78])
    self.ax.set_aspect("equal", adjustable = "box")
    self.ax.set_xlim(-1.25, 1.25)
    self.ax.set_ylim(-1.25, 1.25)
    self.ax.set_xticks([])
    self.ax.set_yticks([])
    self.ax.set_title("Kuramoto oscillators on the unit circle", fontsize = 14)

    circleAngles = np.linspace(0.0, 2*np.pi, 500)
    self.ax.plot(
      np.cos(circleAngles),
      np.sin(circleAngles),
      color = "0.75",
      linewidth = 1.5,
      zorder = 1,
    )
    self.ax.axhline(0.0, color = "0.90", linewidth = 0.8, zorder = 0)
    self.ax.axvline(0.0, color = "0.90", linewidth = 0.8, zorder = 0)

    frequencyScale = max(1e-12, np.max(np.abs(self.frequencies)))
    colors = self.frequencies/frequencyScale
    self.points = self.ax.scatter(
      np.cos(self.angles),
      np.sin(self.angles),
      c = colors,
      cmap = "coolwarm",
      vmin = -1.0,
      vmax = 1.0,
      s = 35,
      edgecolor = "black",
      linewidth = 0.25,
      zorder = 3,
    )

    orderParameter = computeOrderParameter(self.angles)
    self.orderVector = self.ax.quiver(
      [0.0],
      [0.0],
      [orderParameter.real],
      [orderParameter.imag],
      angles = "xy",
      scale_units = "xy",
      scale = 1.0,
      color = "tab:red",
      width = 0.010,
      zorder = 4,
    )

    self.fig.colorbar(
      self.points,
      ax = self.ax,
      fraction = 0.046,
      pad = 0.03,
      label = "natural frequency, rescaled",
    )

    self.equationText = self.fig.text(
      0.74,
      0.80,
      "$\\dot\\theta_i = \\omega_i + K r\\sin(\\varphi - \\theta_i)$\n"
      "$r e^{i\\varphi}=N^{-1}\\sum_j e^{i\\theta_j}$",
      fontsize = 12,
      va = "top",
    )
    self.valuesText = self.fig.text(0.74, 0.70, "", fontsize = 12, va = "top")
    self.statusText = self.fig.text(
      0.06,
      0.04,
      "Use Run, Step, and the K slider.  Changing K resets to the same initial condition.",
      fontsize = 11,
    )

    self.runButton = self._makeButton([0.74, 0.37, 0.16, 0.055], "Run", self.toggleRun)
    self.stepButton = self._makeButton([0.74, 0.30, 0.16, 0.055], "Step", self.stepOnce)
    self.resetButton = self._makeButton([0.74, 0.23, 0.16, 0.055], "Reset", self.resetSimulation)
    self.randomButton = self._makeButton([0.74, 0.16, 0.16, 0.055], "Random", self.randomizeInitialData)

    sliderAxis = self.fig.add_axes([0.74, 0.08, 0.18, 0.035])
    self.couplingSlider = Slider(
      sliderAxis,
      "K",
      args.k_min,
      args.k_max,
      valinit = args.k_initial,
      valstep = args.k_step,
    )
    self.couplingSlider.on_changed(self.onCouplingChanged)

    self.timer = self.fig.canvas.new_timer(interval = args.interval)
    self.timer.add_callback(self.advanceOneStep)
    self.fig.canvas.mpl_connect("close_event", self.onClose)

    self.refreshDisplay()

  def _makeButton(self, rect, label, callback):
    """Create one Matplotlib button."""
    axis = self.fig.add_axes(rect)
    button = Button(axis, label)
    button.on_clicked(callback)
    return button

  def resetState(self):
    """Reset phases and time to the current initial condition."""
    self.angles = self.initialAngles.copy()
    self.stepCount = 0
    self.time = 0.0

  def updateStatus(self, text):
    """Update the status message."""
    self.statusText.set_text(text)
    self.fig.canvas.draw_idle()

  def refreshDisplay(self):
    """Refresh oscillator positions and numerical diagnostics."""
    offsets = np.column_stack((np.cos(self.angles), np.sin(self.angles)))
    self.points.set_offsets(offsets)

    orderParameter = computeOrderParameter(self.angles)
    coherence = abs(orderParameter)
    meanPhase = np.angle(orderParameter)
    self.orderVector.set_UVC([orderParameter.real], [orderParameter.imag])
    self.valuesText.set_text(
      f"K = {self.coupling:.3f}\n"
      f"time = {self.time:.2f}\n"
      f"step = {self.stepCount}\n\n"
      f"r = {coherence:.3f}\n"
      f"varphi = {meanPhase:.3f} rad\n"
      f"varphi = {np.degrees(meanPhase):.1f} deg\n\n"
      f"N = {self.numOscillators}\n"
      f"std(omega) = {np.std(self.frequencies):.3f}"
    )
    self.fig.canvas.draw_idle()

  def advanceOneStep(self):
    """Advance the simulation by one time step."""
    self.angles = advanceKuramoto(
      self.angles,
      self.frequencies,
      self.coupling,
      self.timeStep,
    )
    self.stepCount += 1
    self.time += self.timeStep
    self.refreshDisplay()

  def toggleRun(self, _event):
    """Start or pause the simulation."""
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

  def stepOnce(self, _event):
    """Pause and advance one step."""
    if self.isRunning:
      self.toggleRun(None)

    self.advanceOneStep()
    self.updateStatus("Advanced one time step.")

  def resetSimulation(self, _event):
    """Reset to the current initial condition."""
    self.resetState()
    self.refreshDisplay()
    self.updateStatus("Reset to the current initial condition.")

  def randomizeInitialData(self, _event):
    """Draw a new initial condition and natural frequencies."""
    if self.isRunning:
      self.toggleRun(None)

    self.initialAngles, self.frequencies = makeInitialData(
      self.numOscillators,
      self.frequencySpread,
      self.rng,
    )
    frequencyScale = max(1e-12, np.max(np.abs(self.frequencies)))
    self.points.set_array(self.frequencies/frequencyScale)
    self.resetState()
    self.refreshDisplay()
    self.updateStatus("Generated a new random initial condition.")

  def onCouplingChanged(self, value):
    """Update K and reset for direct comparison across coupling strengths."""
    self.coupling = float(value)
    self.resetState()
    self.refreshDisplay()
    self.updateStatus("K changed; reset to the same initial condition.")

  def onClose(self, _event):
    """Stop the timer when the window closes."""
    self.timer.stop()

  def show(self):
    """Show the interactive window."""
    plt.show()


def parseArguments(argv = None):
  """Parse command-line arguments."""
  parser = argparse.ArgumentParser(description = "Interactive Kuramoto-model circle demo.")
  parser.add_argument("--num-oscillators", type = int, default = defaultNumOscillators)
  parser.add_argument("--frequency-spread", type = float, default = defaultFrequencySpread)
  parser.add_argument("--time-step", type = float, default = defaultTimeStep)
  parser.add_argument("--interval", type = int, default = defaultIntervalMs, help = "animation interval in milliseconds")
  parser.add_argument("--k-min", type = float, default = defaultKMin)
  parser.add_argument("--k-max", type = float, default = defaultKMax)
  parser.add_argument("--k-initial", type = float, default = defaultKInitial)
  parser.add_argument("--k-step", type = float, default = 0.05, help = "slider step size for K")
  parser.add_argument("--seed", type = int, default = defaultSeed)
  args = parser.parse_args(argv)
  validateArguments(parser, args)
  return args


def main():
  """Run the interactive demo."""
  args = parseArguments()
  app = KuramotoInteractiveApp(args)
  app.show()


if __name__ == "__main__":
  main()
