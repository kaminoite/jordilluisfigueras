#!/usr/bin/env python3
# Copyright (c) 2026, Jordi-Lluís Figueras.
# SPDX-License-Identifier: BSD-2-Clause
# See LICENSE in the codes directory for redistribution terms and disclaimer.

"""Interactive phase projections of the exact coupled pendula in slides/slides.tex.

Run with: python3 codes/coupled_pendula.py
Dependencies: numpy, matplotlib, and an interactive Matplotlib backend.
Use --initial-state Q1 Q2 P1 P2 to select exact initial coordinates.
See codes/coupled_pendula_examples.md for examples at epsilon = 0.1.

Click either panel to replace that pendulum's selected (q, p). The two selections
form ONE initial state (q1, q2, p1, p2). Run adds its forward trajectory; Random
adds a batch of trajectories. Each orbit has the same color in both projections.
The epsilon slider affects subsequent runs. Clear stops integration and erases
the trajectories, preserving the selected initial condition.
Check Fading trail to show only the recent past, with older segments fading out.
Trail duration is in simulation-time units (default: 20). Uncheck to restore
the full trajectories. Completed or stopped trails freeze at their final time.

The separable Hamiltonian is integrated by fixed-step symplectic Störmer--Verlet.
Angles remain unwrapped during integration and are wrapped only for plotting.
These are full trajectory projections, not Poincare sections.
"""

import argparse
from dataclasses import dataclass

import matplotlib.pyplot as plt
from matplotlib.backend_bases import MouseButton
from matplotlib.collections import LineCollection
from matplotlib.colors import to_rgba
from matplotlib.transforms import Affine2D, ScaledTranslation
from matplotlib.widgets import Button, CheckButtons, Slider, TextBox
import numpy as np


@dataclass
class PendulaModel:
  """Physical parameters; the defaults ensure d(q) >= a-l1-l2 > 0."""

  m1: float = 1.0
  m2: float = 1.0
  l1: float = 1.0
  l2: float = 1.3
  a: float = 3.0
  g: float = 1.0
  k: float = 1.0

  def __post_init__(self):
    self.inertia = np.array([self.m1*self.l1**2, self.m2*self.l2**2])
    self.gravityScale = np.array([self.m1*self.g*self.l1,
                                  self.m2*self.g*self.l2])
    self.naturalLength = np.hypot(self.a, self.l1-self.l2)

  def computeSpringGeometry(self, position):
    """Return r2-r1 and its length for arrays with final dimension two."""
    deltaX = self.a+self.l2*np.sin(position[..., 1])-self.l1*np.sin(position[..., 0])
    deltaY = self.l1*np.cos(position[..., 0])-self.l2*np.cos(position[..., 1])
    distance = np.hypot(deltaX, deltaY)
    return deltaX, deltaY, distance

  def computeForce(self, position, epsilon):
    """Compute -partial_q H, including the exact length-dependent spring."""
    force = -self.gravityScale*np.sin(position)
    if(epsilon == 0.0):
      return force

    deltaX, deltaY, distance = self.computeSpringGeometry(position)
    if(np.any(distance <= 1.0e-12)):
      raise ValueError("The spring length reached zero; its force is undefined.")
    springScale = epsilon*self.k*(distance-self.naturalLength)/distance
    force[..., 0] += springScale*self.l1*(
      deltaX*np.cos(position[..., 0])+deltaY*np.sin(position[..., 0]))
    force[..., 1] -= springScale*self.l2*(
      deltaX*np.cos(position[..., 1])+deltaY*np.sin(position[..., 1]))
    return force

  def computeEnergy(self, state, epsilon):
    """Evaluate H_epsilon on states ordered (q1, q2, p1, p2)."""
    position = state[..., :2]
    momentum = state[..., 2:]
    energy = np.sum(momentum**2/(2.0*self.inertia)
                    +self.gravityScale*(1.0-np.cos(position)), axis=-1)
    if(epsilon != 0.0):
      _, _, distance = self.computeSpringGeometry(position)
      energy += 0.5*epsilon*self.k*(distance-self.naturalLength)**2
    return energy


def integrateTrajectory(model, initialStates, epsilon, timeStep, stepCount):
  """Return (stepCount+1, orbitCount, 4) states using Störmer--Verlet.

  Accept one state or a batch. The input is not modified. Keeping the step fixed
  preserves the symplectic scheme; the GUI integrates in short timer batches.
  """
  state = np.array(initialStates, dtype=float, ndmin=2, copy=True)
  if(state.ndim != 2 or state.shape[1] != 4 or not np.all(np.isfinite(state))):
    raise ValueError("Initial states must be finite (q1, q2, p1, p2) rows.")
  trajectory = np.empty((stepCount+1, *state.shape))
  trajectory[0] = state
  position = state[:, :2]
  momentum = state[:, 2:]
  force = model.computeForce(position, epsilon)
  for stepIndex in range(1, stepCount+1):
    momentum += 0.5*timeStep*force
    position += timeStep*momentum/model.inertia
    force = model.computeForce(position, epsilon)
    momentum += 0.5*timeStep*force
    trajectory[stepIndex] = state
  if(not np.all(np.isfinite(trajectory))):
    raise ValueError("Non-finite trajectory; reduce the time step or initial momenta.")
  return trajectory


def wrapAngles(angle):
  """Represent angles on [-pi, pi)."""
  return (np.asarray(angle)+np.pi) % (2.0*np.pi)-np.pi


def projectTrajectory(trajectory, pendulumIndex):
  """Project one orbit and break lines that cross the angular branch cut."""
  position = wrapAngles(trajectory[:, pendulumIndex])
  momentum = trajectory[:, pendulumIndex+2]
  breaks = np.flatnonzero(np.abs(np.diff(position)) > np.pi)+1
  return np.insert(position, breaks, np.nan), np.insert(momentum, breaks, np.nan)


def projectTrail(trajectory, pendulumIndex, timeStep, trailDuration):
  """Return recent segments and age-dependent opacity, omitting branch cuts."""
  elapsed = (len(trajectory)-1)*timeStep
  cutoff = max(0.0, elapsed-trailDuration)
  startIndex = int(np.floor(cutoff/timeStep))
  points = trajectory[startIndex:, [pendulumIndex, pendulumIndex+2]].copy()
  times = np.arange(startIndex, len(trajectory))*timeStep
  if(len(points) < 2):
    return np.empty((0, 2, 2)), np.empty(0)
  # Clip the oldest segment to the time window before wrapping its angle.
  fraction = np.clip((cutoff-times[0])/timeStep, 0.0, 1.0)
  points[0] += fraction*(points[1]-points[0])
  points[:, 0] = wrapAngles(points[:, 0])
  segments = np.stack((points[:-1], points[1:]), axis=1)
  opacity = 0.8*np.clip(1.0-(elapsed-times[1:])/trailDuration, 0.0, 1.0)
  valid = np.abs(np.diff(points[:, 0])) <= np.pi
  return segments[valid], opacity[valid]


@dataclass
class TrajectoryRun:
  """Retain each run so display settings also apply to completed trajectories."""

  history: np.ndarray
  timeStep: float
  lines: list
  trails: list
  starts: list
  stepIndex: int = 0


class PendulaExplorer:
  """Matplotlib controls and timer-driven forward integration."""

  def __init__(self, model, epsilon=0.1, epsilonMax=1.0, duration=120.0,
               timeStep=0.01, randomCount=8, seed=None, initialState=None):
    self.model = model
    self.timeStep = timeStep
    self.randomCount = randomCount
    self.randomGenerator = np.random.default_rng(seed)
    if(initialState is None):
      initialState = [0.8, -0.4, 0.0, 0.0]
    self.selectedState = np.array(initialState, dtype=float, copy=True)
    if(self.selectedState.shape != (4,) or not np.all(np.isfinite(self.selectedState))):
      raise ValueError("Initial state must be a finite (q1, q2, p1, p2) row.")
    self.selectedState[:2] = wrapAngles(self.selectedState[:2])
    # 1.5 times the uncoupled separatrix momenta. Random seeds use this fixed
    # window even if existing trajectories have expanded the vertical axes.
    self.momentumLimits = 3.0*np.sqrt(model.inertia*model.gravityScale)
    self.trajectoryArtists = []
    self.activeLines = []
    self.runs = []
    self.trailDuration = 20.0
    self.orbitCount = 0
    self.running = False
    self.maxEnergyError = 0.0

    self.figure, self.axes = plt.subplots(1, 2, figsize=(12, 7.5))
    self.figure.subplots_adjust(left=0.075, right=0.97, bottom=0.34,
                                top=0.79, wspace=0.24)
    self.figure.canvas.manager.set_window_title("Coupled pendula: phase projections")
    self.figure.suptitle("Coupled pendula: phase-space projections", fontsize=18, y=0.97)
    self.figure.text(0.5, 0.918,
                     r"$H_\varepsilon=\sum_j[p_j^2/(2m_j\ell_j^2)"
                     r"+m_jg\ell_j(1-\cos q_j)]+\varepsilon k(d-d_0)^2/2$",
                     ha="center", fontsize=13)
    self.figure.text(0.5, 0.874,
                     f"m = ({model.m1:g}, {model.m2:g}), "
                     f"lengths = ({model.l1:g}, {model.l2:g}), "
                     f"a = {model.a:g}, g = {model.g:g}, k = {model.k:g}",
                     ha="center", fontsize=10, color="0.35")
    self.figure.text(0.5, 0.835,
                     "Click each panel to select its (q, p). "
                     "Matching colors identify the same 4D trajectory.",
                     ha="center", fontsize=10)

    self.selectionMarkers = []
    self.selectionLabels = []
    for pendulumIndex, axis in enumerate(self.axes):
      number = pendulumIndex+1
      axis.set_title(f"Pendulum {number}", fontsize=13)
      axis.set_xlabel(rf"$q_{number}$ (radians, modulo $2\pi$)")
      axis.set_ylabel(rf"$p_{number}$")
      axis.set_xticks(np.linspace(-np.pi, np.pi, 5))
      axis.set_xticklabels([r"$-\pi$", r"$-\pi/2$", "0", r"$\pi/2$", r"$\pi$"])
      axis.grid(alpha=0.2)
      axis.axhline(0.0, color="0.6", linewidth=0.6, zorder=0)
      axis.axvline(0.0, color="0.6", linewidth=0.6, zorder=0)
      marker, = axis.plot([], [], linestyle="none", marker="X", markersize=10,
                          color="#c72c76", markeredgecolor="white", zorder=5)
      self.selectionMarkers.append(marker)
      label = self.figure.text(axis.get_position().x0, 0.255, "", fontsize=10,
                               color="#9b225c")
      self.selectionLabels.append(label)
    self.resetLimits()
    self.updateSelection()

    self.epsilonSlider = Slider(self.figure.add_axes([0.14, 0.192, 0.43, 0.03]),
                                r"$\varepsilon$", 0.0, epsilonMax,
                                valinit=epsilon, valfmt="%.3f")
    self.durationBox = TextBox(self.figure.add_axes([0.79, 0.184, 0.12, 0.045]),
                               "End time T ", initial=f"{duration:g}")
    trailAxes = self.figure.add_axes([0.14, 0.125, 0.24, 0.045])
    trailAxes.set_frame_on(False)
    self.trailCheck = CheckButtons(trailAxes, ["Fading trail"], [False])
    # Older Matplotlib versions stretch checkbox patches with the widget axes.
    # Use a fixed 14-point square, including its check mark, even after resizing.
    if(trailAxes.patches):
      box = trailAxes.patches[0]
      x, y, width, height = box.get_bbox().bounds
      checkTransform = (Affine2D().translate(-x, -y-height/2.0)
                        .scale(14.0/(72.0*width), 14.0/(72.0*height))
                        +self.figure.dpi_scale_trans
                        +ScaledTranslation(x, y+height/2.0, trailAxes.transAxes))
      box.set_transform(checkTransform)
      for line in trailAxes.lines:
        line.set_transform(checkTransform)
    self.trailDurationBox = TextBox(self.figure.add_axes([0.79, 0.127, 0.12, 0.04]),
                                    "Trail duration ", initial=f"{self.trailDuration:g}")
    self.runButton = Button(self.figure.add_axes([0.14, 0.055, 0.19, 0.05]), "Run")
    self.randomButton = Button(self.figure.add_axes([0.405, 0.055, 0.19, 0.05]),
                                f"Random ({randomCount})")
    self.clearButton = Button(self.figure.add_axes([0.67, 0.055, 0.19, 0.05]), "Clear")
    self.statusLabel = self.figure.text(0.5, 0.018,
                                        "Select a point in either panel, then Run; "
                                        "or add a random batch.",
                                        ha="center", fontsize=10)
    self.runButton.on_clicked(self.runSelected)
    self.randomButton.on_clicked(self.runRandom)
    self.clearButton.on_clicked(self.clearPortrait)
    self.trailCheck.on_clicked(self.refreshTrajectories)
    self.trailDurationBox.on_submit(self.setTrailDuration)
    self.figure.canvas.mpl_connect("button_press_event", self.selectPoint)
    self.figure.canvas.mpl_connect("close_event", self.closeWindow)
    self.timer = self.figure.canvas.new_timer(interval=25)
    self.timer.add_callback(self.advanceSimulation)

  def resetLimits(self):
    for pendulumIndex, axis in enumerate(self.axes):
      axis.set_xlim(-np.pi, np.pi)
      axis.set_ylim(-self.momentumLimits[pendulumIndex],
                    self.momentumLimits[pendulumIndex])

  def updateSelection(self):
    for pendulumIndex in range(2):
      position = self.selectedState[pendulumIndex]
      momentum = self.selectedState[pendulumIndex+2]
      self.selectionMarkers[pendulumIndex].set_data([position], [momentum])
      self.selectionLabels[pendulumIndex].set_text(
        f"Selected: q{pendulumIndex+1} = {position:+.4f}, "
        f"p{pendulumIndex+1} = {momentum:+.4f}")

  def selectPoint(self, event):
    if(event.button != MouseButton.LEFT or event.inaxes not in self.axes):
      return
    toolbar = getattr(self.figure.canvas.manager, "toolbar", None)
    if(toolbar is not None and toolbar.mode):
      return
    if(event.xdata is None or event.ydata is None):
      return
    pendulumIndex = list(self.axes).index(event.inaxes)
    self.selectedState[pendulumIndex] = wrapAngles(event.xdata)
    self.selectedState[pendulumIndex+2] = event.ydata
    self.updateSelection()
    if(not self.running):
      self.statusLabel.set_text("Initial condition updated. Run adds a new trajectory.")
    self.figure.canvas.draw_idle()

  def runSelected(self, event=None):
    if(self.running):
      self.stopSimulation()
      self.updateStatus("Stopped")
    else:
      self.startSimulation(self.selectedState[np.newaxis, :])

  def runRandom(self, event=None):
    if(self.running):
      return
    initialStates = np.empty((self.randomCount, 4))
    initialStates[:, :2] = self.randomGenerator.uniform(-np.pi, np.pi,
                                                       (self.randomCount, 2))
    initialStates[:, 2:] = self.randomGenerator.uniform(-self.momentumLimits,
                                                       self.momentumLimits,
                                                       (self.randomCount, 2))
    self.startSimulation(initialStates)

  def setTrailDuration(self, text):
    try:
      duration = float(text)
      if(not np.isfinite(duration) or duration <= 0.0):
        raise ValueError
    except ValueError:
      # Restore the last valid setting without recursively submitting it.
      self.trailDurationBox.eventson = False
      try:
        self.trailDurationBox.set_val(f"{self.trailDuration:g}")
      finally:
        self.trailDurationBox.eventson = True
      self.statusLabel.set_text("Trail duration must be positive and finite.")
      self.figure.canvas.draw_idle()
      return
    self.trailDuration = duration
    self.refreshTrajectories()

  def refreshTrajectories(self, event=None):
    for run in self.runs:
      self.renderRun(run)
    self.figure.canvas.draw_idle()

  def renderRun(self, run):
    fading = self.trailCheck.get_status()[0]
    elapsed = run.stepIndex*run.timeStep
    for orbitIndex, orbitLines in enumerate(run.lines):
      trajectory = run.history[:run.stepIndex+1, orbitIndex]
      for pendulumIndex, line in enumerate(orbitLines):
        trail = run.trails[orbitIndex][pendulumIndex]
        start = run.starts[orbitIndex][pendulumIndex]
        line.set_visible(not fading)
        trail.set_visible(fading)
        start.set_alpha(max(0.0, 1.0-elapsed/self.trailDuration) if(fading) else 1.0)
        if(fading):
          segments, opacity = projectTrail(trajectory, pendulumIndex,
                                            run.timeStep, self.trailDuration)
          colors = np.tile(to_rgba(line.get_color()), (len(opacity), 1))
          colors[:, 3] = opacity
          trail.set_segments(segments)
          trail.set_color(colors)
          # Hidden full-path geometry can be reconstructed from history.
          line.set_data([], [])
        else:
          position, momentum = projectTrajectory(trajectory, pendulumIndex)
          line.set_data(position, momentum)
          trail.set_segments([])

  def startSimulation(self, initialStates):
    try:
      duration = float(self.durationBox.text)
      if(not np.isfinite(duration) or duration <= 0.0):
        raise ValueError
    except ValueError:
      self.statusLabel.set_text("End time T must be a positive, finite number.")
      self.figure.canvas.draw_idle()
      return

    self.duration = duration
    self.runEpsilon = float(self.epsilonSlider.val)
    self.stepCount = int(np.ceil(duration/self.timeStep))
    # A slightly reduced, constant step lands exactly on the requested end time.
    self.runTimeStep = duration/self.stepCount
    self.stepIndex = 0
    self.maxEnergyError = 0.0
    self.initialEnergy = self.model.computeEnergy(initialStates, self.runEpsilon)
    self.history = np.empty((self.stepCount+1, len(initialStates), 4))
    self.history[0] = initialStates
    self.activeLines = []
    run = TrajectoryRun(self.history, self.runTimeStep, self.activeLines, [], [])
    self.runs.append(run)
    colorMap = plt.get_cmap("tab10")
    for initialState in initialStates:
      color = colorMap(self.orbitCount % 10)
      orbitLines = []
      orbitTrails = []
      orbitStarts = []
      for pendulumIndex, axis in enumerate(self.axes):
        line, = axis.plot([], [], color=color, linewidth=0.8, alpha=0.8)
        trail = LineCollection([], linewidths=0.8, zorder=line.get_zorder())
        axis.add_collection(trail)
        start, = axis.plot([wrapAngles(initialState[pendulumIndex])],
                           [initialState[pendulumIndex+2]], marker="o",
                           linestyle="none", color=color, markersize=4)
        self.trajectoryArtists.extend([line, trail, start])
        orbitLines.append(line)
        orbitTrails.append(trail)
        orbitStarts.append(start)
      self.activeLines.append(orbitLines)
      run.trails.append(orbitTrails)
      run.starts.append(orbitStarts)
      self.orbitCount += 1
    self.renderRun(run)
    self.running = True
    self.runButton.label.set_text("Stop")
    self.randomButton.set_active(False)
    self.randomButton.label.set_alpha(0.4)
    self.epsilonSlider.set_active(False)
    self.durationBox.set_active(False)
    self.updateStatus("Running")
    self.timer.start()

  def advanceSimulation(self):
    if(not self.running):
      return
    chunkSteps = min(200, self.stepCount-self.stepIndex)
    try:
      chunk = integrateTrajectory(self.model, self.history[self.stepIndex],
                                  self.runEpsilon, self.runTimeStep, chunkSteps)
    except ValueError as error:
      self.stopSimulation()
      self.statusLabel.set_text(str(error))
      self.figure.canvas.draw_idle()
      return
    endIndex = self.stepIndex+chunkSteps
    self.history[self.stepIndex+1:endIndex+1] = chunk[1:]
    self.stepIndex = endIndex
    energyError = np.abs(self.model.computeEnergy(chunk, self.runEpsilon)
                         -self.initialEnergy)/(1.0+np.abs(self.initialEnergy))
    self.maxEnergyError = max(self.maxEnergyError, float(np.max(energyError)))
    # Render every step so fast rotations do not alias across the branch cut.
    self.runs[-1].stepIndex = endIndex
    self.renderRun(self.runs[-1])
    for pendulumIndex, axis in enumerate(self.axes):
      lower, upper = axis.get_ylim()
      minimum = float(np.min(chunk[..., pendulumIndex+2]))
      maximum = float(np.max(chunk[..., pendulumIndex+2]))
      margin = 0.05*(upper-lower)
      if(minimum < lower or maximum > upper):
        axis.set_ylim(min(lower, minimum-margin), max(upper, maximum+margin))
    if(self.stepIndex == self.stepCount):
      self.stopSimulation()
      self.updateStatus("Done")
    else:
      self.updateStatus("Running")

  def updateStatus(self, prefix):
    self.statusLabel.set_text(
      f"{prefix}: t = {self.stepIndex*self.runTimeStep:.2f}/{self.duration:g}   "
      f"epsilon = {self.runEpsilon:.3f}   orbits = {len(self.activeLines)}   "
      f"max |H-H(0)|/(1+|H(0)|) = {self.maxEnergyError:.2e}")
    self.figure.canvas.draw_idle()

  def stopSimulation(self):
    self.timer.stop()
    self.running = False
    self.runButton.label.set_text("Run")
    self.randomButton.set_active(True)
    self.randomButton.label.set_alpha(1.0)
    self.epsilonSlider.set_active(True)
    self.durationBox.set_active(True)

  def clearPortrait(self, event=None):
    self.stopSimulation()
    for artist in self.trajectoryArtists:
      artist.remove()
    self.trajectoryArtists.clear()
    self.activeLines.clear()
    self.runs.clear()
    self.history = None
    self.orbitCount = 0
    self.resetLimits()
    self.statusLabel.set_text("Portrait cleared. Selected initial condition retained.")
    self.figure.canvas.draw_idle()

  def closeWindow(self, event=None):
    self.timer.stop()
    self.running = False


def parseArguments():
  parser = argparse.ArgumentParser(description=__doc__,
                                    formatter_class=argparse.RawDescriptionHelpFormatter)
  parser.add_argument("--epsilon", type=float, default=0.1, help="initial coupling (default: 0.1)")
  parser.add_argument("--epsilon-max", dest="epsilonMax", type=float, default=1.0,
                      help="upper end of the epsilon slider (default: 1)")
  parser.add_argument("--duration", type=float, default=120.0,
                      help="forward integration time, also editable in the GUI (default: 120)")
  parser.add_argument("--dt", dest="timeStep", type=float, default=0.01,
                      help="maximum fixed integration step (default: 0.01)")
  parser.add_argument("--random-count", dest="randomCount", type=int, default=8,
                      help="number of orbits per Random click (default: 8)")
  parser.add_argument("--seed", type=int, default=None, help="optional random seed")
  parser.add_argument("--initial-state", dest="initialState", type=float, nargs=4,
                      metavar=("Q1", "Q2", "P1", "P2"),
                      help="selected initial state (default: 0.8 -0.4 0 0)")
  arguments = parser.parse_args()
  for name in ("epsilonMax", "duration", "timeStep"):
    value = getattr(arguments, name)
    if(not np.isfinite(value) or value <= 0.0):
      parser.error(f"{name} must be positive and finite")
  if(not np.isfinite(arguments.epsilon)
     or not 0.0 <= arguments.epsilon <= arguments.epsilonMax):
    parser.error("epsilon must be between zero and epsilon-max")
  if(arguments.randomCount < 1):
    parser.error("random-count must be at least one")
  if(arguments.seed is not None and arguments.seed < 0):
    parser.error("seed must be nonnegative")
  if(arguments.initialState is not None
     and not np.all(np.isfinite(arguments.initialState))):
    parser.error("initial-state coordinates must be finite")
  return arguments


def main():
  arguments = parseArguments()
  # Keep a strong reference so Matplotlib's widget callbacks remain alive.
  explorer = PendulaExplorer(PendulaModel(), **vars(arguments))
  plt.show()
  return explorer


if(__name__ == "__main__"):
  main()
