"""Generate a standard-map phase portrait near golden-mean circle breakup."""

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


def plotPhasePortrait():
  parameter = 0.971635406
  orbitCount = 240
  iterationCount = 6000
  randomGenerator = np.random.default_rng(20261120)
  position = randomGenerator.random(orbitCount)
  momentum = randomGenerator.random(orbitCount)
  positions = np.empty((iterationCount, orbitCount))
  momenta = np.empty_like(positions)

  for iteration in range(iterationCount):
    momentum = (momentum+parameter/(2*np.pi)*np.sin(2*np.pi*position)) % 1
    position = (position+momentum) % 1
    positions[iteration] = position
    momenta[iteration] = momentum

  figure, axes = plt.subplots(figsize=(8, 8))
  axes.scatter(
    positions.ravel(), momenta.ravel(),
    s=0.07, color="#20252b", linewidths=0, rasterized=True,
  )
  axes.set(
    xlim=(0, 1), ylim=(0, 1), aspect="equal",
    xlabel=r"$x$", ylabel=r"$y$",
    title=r"Standard map near golden-mean breakup: $K=0.971635406$",
  )
  axes.set_xticks(np.linspace(0, 1, 5))
  axes.set_yticks(np.linspace(0, 1, 5))
  figure.tight_layout()
  figure.savefig(
    Path(__file__).with_name("standardMapGoldenMean.png"),
    dpi=180, facecolor="white",
  )
  plt.close(figure)


if(__name__ == "__main__"):
  plotPhasePortrait()
