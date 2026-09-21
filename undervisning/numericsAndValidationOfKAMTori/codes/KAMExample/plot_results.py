#!/usr/bin/env python3
# Copyright (c) 2026, Jordi-Lluís Figueras.
# SPDX-License-Identifier: BSD-2-Clause
# See ../LICENSE for redistribution terms and disclaimer.

"""Run the standalone KAM example and regenerate the numerical slide figures.

Requires NumPy and Matplotlib only for post-processing. The C++ solver remains
independent of both. Run `make figures` in this directory.
"""

import argparse
import csv
import json
import math
from pathlib import Path
import re
import subprocess

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.ticker import LogLocator, NullLocator
import numpy as np


ink = "#19344A"
teal = "#007B80"
orange = "#CF662D"
muted = "#617383"
omega = np.array([1.0, (1.0+math.sqrt(5.0))/2.0])
gridSize = 64
tolerance = 1.e-12


def setPlotStyle():
  plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "font.size": 15,
    "axes.titlesize": 17,
    "axes.labelsize": 16,
    "legend.fontsize": 13,
    "xtick.labelsize": 13,
    "ytick.labelsize": 13,
    "text.color": ink,
    "axes.labelcolor": ink,
    "axes.edgecolor": muted,
    "xtick.color": ink,
    "ytick.color": ink,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.axisbelow": True,
    "grid.color": muted,
    "grid.alpha": 0.17,
    "lines.linewidth": 2.4,
    "savefig.facecolor": "white",
    "pdf.fonttype": 42,
  })


def saveFigure(figure, directory, name):
  figure.savefig(directory / f"{name}.pdf")
  figure.savefig(directory / f"{name}.png", dpi=160)
  plt.close(figure)


def writeTable(path, header, rows):
  with path.open("w", newline="", encoding="utf-8") as output:
    writer = csv.writer(output, lineterminator="\n")
    writer.writerow(header)
    writer.writerows(rows)


def runSolver(executable, resultsDir, epsilon):
  tag = f"eps{epsilon:.2f}".replace(".", "p")
  csvPath = resultsDir / f"torus-{tag}.csv"
  command = [str(executable), "-e", str(epsilon), "-n", str(gridSize),
    "-t", str(tolerance), "-o", str(csvPath)]
  result = subprocess.run(command, text=True, capture_output=True, check=False)
  (resultsDir / f"solver-{tag}.log").write_text(
    "$ " + " ".join(command) + "\n" + result.stdout + result.stderr,
    encoding="utf-8")
  if(result.returncode != 0):
    raise RuntimeError(f"Solver failed for epsilon={epsilon}:\n{result.stdout}{result.stderr}")

  history = []
  for line in result.stdout.splitlines():
    match = re.fullmatch(r"\s*(\d+)\s+([\d.eE+\-]+)(?:\s+([\d.eE+\-]+)"
      r"\s+([\d.eE+\-]+)\s+([\d.eE+\-]+)\s+([\d.eE+\-]+))?\s*", line)
    if(match):
      history.append([int(match[1]), float(match[2]),
        *[float(value) if value is not None else math.nan for value in match.groups()[2:]]])
  if(len(history) < 2 or history[-1][1] > tolerance):
    raise RuntimeError("Missing or incomplete convergence history.")
  writeTable(resultsDir / f"history-{tag}.csv",
    ["step", "residual_2N", "correction", "normal_average", "torsion_condition", "gram_condition"],
    history)

  data = np.loadtxt(csvPath, delimiter=",", skiprows=2)
  if(data.shape != (gridSize*gridSize, 15) or not np.all(np.isfinite(data))):
    raise RuntimeError("Unexpected torus CSV contents.")
  periodic = data[:, 6:10].reshape(gridSize, gridSize, 4)
  coefficients = np.fft.fft2(periodic, axes=(0, 1), norm="forward")
  # The solver excludes Nyquist lines; omit their floating-point FFT noise.
  coefficients[gridSize//2, :, :] = 0.0
  coefficients[:, gridSize//2, :] = 0.0
  residual = computeSampledResidual(coefficients, 4*gridSize, epsilon)
  if(residual > tolerance):
    raise RuntimeError(f"Independent fine-grid residual failed: {residual:.3e}")
  return {"epsilon": epsilon, "history": np.asarray(history), "periodic": periodic,
    "coefficients": coefficients, "fineResidual": residual}


def resizeCoefficients(coefficients, newSize):
  """Transfer normalized Fourier coefficients, excluding Nyquist lines."""
  oldSize = coefficients.shape[0]
  modes = np.rint(np.fft.fftfreq(oldSize)*oldSize).astype(int)
  indices = np.flatnonzero(np.abs(modes) < min(oldSize, newSize)//2)
  targets = modes[indices] % newSize
  result = np.zeros((newSize, newSize, coefficients.shape[2]), dtype=complex)
  result[targets[:, None], targets[None, :], :] = coefficients[indices[:, None], indices[None, :], :]
  return result


def computeSampledResidual(coefficients, checkSize, epsilon):
  """Independently evaluate X_H(K)-DK*omega on an oversampled grid."""
  padded = resizeCoefficients(coefficients, checkSize)
  periodic = np.fft.ifft2(padded, axes=(0, 1), norm="forward").real
  modes = np.fft.fftfreq(checkSize)*checkSize
  divisor = modes[:, None]*omega[0]+modes[None, :]*omega[1]
  derivative = np.fft.ifft2(1j*divisor[:, :, None]*padded,
    axes=(0, 1), norm="forward").real
  angles = np.arange(checkSize)*2.0*np.pi/checkSize
  phi1 = angles[:, None]+periodic[:, :, 0]
  phi2 = angles[None, :]+periodic[:, :, 1]
  residual = np.empty_like(periodic)
  residual[:, :, :2] = periodic[:, :, 2:]-derivative[:, :, :2]
  coupling = np.sin(phi1-phi2)
  residual[:, :, 2] = epsilon*(np.sin(phi1)+coupling)-derivative[:, :, 2]
  residual[:, :, 3] = epsilon*(np.sin(phi2)-coupling)-derivative[:, :, 3]
  return float(np.max(np.abs(residual)))


def plotConvergence(runs, figuresDir):
  figure, axis = plt.subplots(figsize=(11, 4.25), layout="constrained")
  for run, color, marker in zip(runs, (teal, orange), ("o", "s")):
    history = run["history"]
    axis.semilogy(history[:, 0], history[:, 1], color=color, marker=marker,
      markersize=7, label=rf"$\varepsilon={run['epsilon']:.2f}$")
  axis.set(xlabel="Quasi-Newton correction count", ylabel="Sampled maximum residual",
    xticks=np.arange(6), ylim=(2.e-16, 0.15))
  axis.yaxis.set_major_locator(LogLocator(base=10, numticks=6))
  axis.yaxis.set_minor_locator(NullLocator())
  axis.grid(True)
  axis.legend(loc="upper right", frameon=False)
  axis.text(0.04, 0.17, "Rapid error reduction, followed by a roundoff floor",
    transform=axis.transAxes, fontsize=14, color=muted)
  saveFigure(figure, figuresDir, "kam-convergence")


def plotTorus(run, figuresDir):
  figure, axes = plt.subplots(1, 2, figsize=(11, 4.4), layout="constrained")
  actions = run["periodic"][:, :, 2:]
  bound = float(np.max(np.abs(actions)))
  levels = np.linspace(-bound, bound, 25)
  colors = LinearSegmentedColormap.from_list("torusActions", [teal, "#FFFFFF", orange])
  angles = np.linspace(0.0, 2.0*np.pi, gridSize+1)
  for component, axis in enumerate(axes):
    closed = np.pad(actions[:, :, component], ((0, 1), (0, 1)), mode="wrap")
    image = axis.contourf(angles, angles, closed.T, levels=levels, cmap=colors)
    axis.set(title=rf"$v_{component+1}(\theta)=K_{{I_{component+1}}}(\theta)-\omega_{component+1}$",
      xlabel=rf"$\theta_1$", ylabel=rf"$\theta_2$", aspect="equal")
    axis.set_xticks([0, np.pi, 2*np.pi], ["0", r"$\pi$", r"$2\pi$"])
    axis.set_yticks([0, np.pi, 2*np.pi], ["0", r"$\pi$", r"$2\pi$"])
  bar = figure.colorbar(image, ax=axes, shrink=0.85, pad=0.025)
  bar.set_label("Action displacement")
  saveFigure(figure, figuresDir, "kam-torus-deformation")


def plotResolution(runs, resultsDir, figuresDir):
  figure, axes = plt.subplots(1, 2, figsize=(11, 4.4), layout="constrained")
  modes = np.rint(np.fft.fftfreq(gridSize)*gridSize).astype(int)
  shells = np.maximum(np.abs(modes[:, None]), np.abs(modes[None, :]))
  shellNumbers = np.arange(1, gridSize//2)
  sizes = [8, 16, 32, 64]
  spectrumRows, resolutionRows = [], []
  for run, color, marker in zip(runs, (teal, orange), ("o", "s")):
    coefficients = run["coefficients"]
    envelope = np.array([np.max(np.abs(coefficients[shells == shell])) for shell in shellNumbers])
    residuals = [computeSampledResidual(resizeCoefficients(coefficients, size),
      4*size, run["epsilon"]) for size in sizes]
    spectrumRows.extend(zip([run["epsilon"]]*len(shellNumbers), shellNumbers, envelope))
    resolutionRows.extend(zip([run["epsilon"]]*len(sizes), sizes, residuals))
    label = rf"$\varepsilon={run['epsilon']:.2f}$"
    axes[0].semilogy(shellNumbers, envelope, color=color, label=label)
    axes[1].semilogy(sizes, residuals, color=color, marker=marker, markersize=6, label=label)
  axes[0].set(title="Fourier decay", xlabel=rf"Shell $m=|k|_\infty$",
    ylabel="Largest coefficient of $(u,v)$", ylim=(1.e-19, 0.2), xlim=(0, 32))
  axes[1].set(title="Effect of Fourier truncation", xlabel="Retained grid size $N$",
    ylabel="Residual sampled on $(4N)^2$ points", xticks=sizes, ylim=(1.e-16, 0.2))
  for axis in axes:
    axis.yaxis.set_major_locator(LogLocator(base=10, numticks=6))
    axis.yaxis.set_minor_locator(NullLocator())
    axis.grid(True)
    axis.legend(frameon=False, loc="upper right")
  writeTable(resultsDir / "fourier-decay.csv", ["epsilon", "shell", "max_coefficient"], spectrumRows)
  writeTable(resultsDir / "truncation-residual.csv", ["epsilon", "retained_size", "residual_4N"], resolutionRows)
  saveFigure(figure, figuresDir, "kam-resolution")


def evaluateEmbedding(coefficients, theta):
  size = coefficients.shape[0]
  modes = np.fft.fftfreq(size)*size
  phase = np.exp(1j*(modes[:, None]*theta[0]+modes[None, :]*theta[1]))
  periodic = np.einsum("ij,ijr->r", phase, coefficients).real
  return periodic+np.concatenate((theta, omega))


def evaluateVectorField(state, epsilon):
  coupling = math.sin(state[0]-state[1])
  return np.array([state[2], state[3], epsilon*(math.sin(state[0])+coupling),
    epsilon*(math.sin(state[1])-coupling)])


def integrateOrbit(initial, times, substeps, epsilon):
  orbit = np.empty((len(times), 4))
  orbit[0] = initial
  state = initial.copy()
  for index in range(1, len(times)):
    step = (times[index]-times[index-1])/substeps
    for _ in range(substeps):
      k1 = evaluateVectorField(state, epsilon)
      k2 = evaluateVectorField(state+step*k1/2, epsilon)
      k3 = evaluateVectorField(state+step*k2/2, epsilon)
      k4 = evaluateVectorField(state+step*k3, epsilon)
      state += step*(k1+2*k2+2*k3+k4)/6
    orbit[index] = state
  return orbit


def plotDynamics(run, resultsDir, figuresDir):
  times = np.linspace(0.0, 20.0, 201)
  theta0 = np.array([0.37, 1.23])
  parameterized = np.array([evaluateEmbedding(run["coefficients"], theta0+omega*time) for time in times])
  coarse = integrateOrbit(parameterized[0], times, 5, run["epsilon"])
  fine = integrateOrbit(parameterized[0], times, 10, run["epsilon"])
  coarseError = np.max(np.abs(coarse-parameterized), axis=1)
  fineError = np.max(np.abs(fine-parameterized), axis=1)
  maximumError = float(np.max(fineError))
  if(not np.isfinite(maximumError) or maximumError > 1.e-8):
    raise RuntimeError(f"Independent trajectory check failed: {maximumError:.3e}")
  if(np.max(coarseError) > 1.e-11 and maximumError > 0.5*np.max(coarseError)):
    raise RuntimeError("Halving the RK4 step did not improve the trajectory check.")
  writeTable(resultsDir / "trajectory-check.csv",
    ["time", "parameterized_I1", "integrated_I1", "error_h0p02", "error_h0p01"],
    zip(times, parameterized[:, 2], fine[:, 2], coarseError, fineError))

  figure, axes = plt.subplots(1, 2, figsize=(11, 4.4), layout="constrained")
  axes[0].plot(times, parameterized[:, 2], color=teal, label=r"$K(\theta_0+\omega t)$")
  axes[0].plot(times[::5], fine[::5, 2], linestyle="none", marker="o", markersize=5,
    markerfacecolor="none", color=orange, label="Independent RK4")
  axes[0].set(title="An action along the orbit", xlabel="$t$", ylabel="$I_1(t)$")
  for errors, color, label in [(coarseError, muted, "$h=0.02$"), (fineError, orange, "$h=0.01$")]:
    axes[1].semilogy(times[1:], np.maximum(errors[1:], 1.e-17), color=color, label=label)
  axes[1].set(title="Trajectory discrepancy", xlabel="$t$",
    ylabel=r"$\max_j |z_j(t)-K_j(\theta_0+\omega t)|$")
  for axis in axes:
    axis.grid(True)
    axis.legend(frameon=False, fontsize=12, loc="best")
  saveFigure(figure, figuresDir, "kam-dynamics")
  return maximumError


def formatLatex(value):
  mantissa, exponent = f"{value:.1e}".split("e")
  return rf"{mantissa}\times10^{{{int(exponent)}}}"


def main():
  exampleDir = Path(__file__).resolve().parent
  projectDir = exampleDir.parent.parent
  parser = argparse.ArgumentParser(description=__doc__)
  parser.add_argument("--solver", type=Path, default=exampleDir / "exampleKAM.x")
  parser.add_argument("--results-dir", type=Path, default=exampleDir / "results")
  parser.add_argument("--figures-dir", type=Path, default=projectDir / "slides" / "images")
  arguments = parser.parse_args()
  executable = arguments.solver.resolve()
  if(not executable.is_file()):
    parser.error("Build exampleKAM.x first (make).")
  resultsDir = arguments.results_dir.resolve()
  figuresDir = arguments.figures_dir.resolve()
  resultsDir.mkdir(parents=True, exist_ok=True)
  figuresDir.mkdir(parents=True, exist_ok=True)
  setPlotStyle()
  runs = [runSolver(executable, resultsDir, epsilon) for epsilon in (0.01, 0.03)]
  plotConvergence(runs, figuresDir)
  plotTorus(runs[1], figuresDir)
  plotResolution(runs, resultsDir, figuresDir)
  trajectoryError = plotDynamics(runs[1], resultsDir, figuresDir)
  summary = {
    "omega": omega.tolist(), "base_grid_size": gridSize,
    "work_grid_size": 2*gridSize, "check_grid_size": 4*gridSize,
    "tolerance": tolerance,
    "runs": [{"epsilon": run["epsilon"], "corrections": int(run["history"][-1, 0]),
      "independent_fine_grid_residual": run["fineResidual"]} for run in runs],
    "trajectory": {"epsilon": 0.03, "interval": [0.0, 20.0], "rk4_step": 0.01,
      "max_discrepancy": trajectoryError},
    "resolution_plot": "Truncations of the same converged N=64 torus; no separate Newton solves.",
  }
  (resultsDir / "summary.json").write_text(json.dumps(summary, indent=2)+"\n", encoding="utf-8")
  macros = "% Generated by codes/KAMExample/plot_results.py; do not edit.\n"
  for name, value in [("kamSmallResidual", runs[0]["fineResidual"]),
                      ("kamLargeResidual", runs[1]["fineResidual"]),
                      ("kamTrajectoryError", trajectoryError)]:
    macros += rf"\newcommand{{\{name}}}{{{formatLatex(value)}}}"+"\n"
  (figuresDir / "kam-numerics-values.tex").write_text(macros, encoding="utf-8")
  print(json.dumps(summary, indent=2))
  print(f"Figures saved to {figuresDir}")


if(__name__ == "__main__"):
  main()
