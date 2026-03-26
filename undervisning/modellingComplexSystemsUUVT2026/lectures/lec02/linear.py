"""
 * linear.py
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

"""Iterate the linear map from the worked example in lecture 2.

The script uses the map

  x_(n+1) = 0.8 x_n + 1

and takes the initial value x_0 from the command line.  It prints the first
100 iterates in the form

  0 x_0
  1 x_1
  ...
  99 x_99

and also shows the orbit as a plot of x_n against n.
"""

import argparse

import matplotlib.pyplot as plt
import numpy as np


a = 0.8
b = 1.0
nSteps = 100


def linearMap(x):
  """Return one iterate of the linear map."""
  return a * x + b


def solveOrbit(x0, nSteps):
  """Compute x_0, ..., x_(nSteps-1)."""
  orbit = np.zeros(nSteps)
  orbit[0] = x0

  for i in range(nSteps - 1):
    orbit[i + 1] = linearMap(orbit[i])

  return orbit


def parseArguments():
  """Read the initial condition from the command line."""
  parser = argparse.ArgumentParser(
    description = "Iterate x_(n+1) = 0.8 x_n + 1 and plot the orbit."
  )
  parser.add_argument(
    "x0",
    type = float,
    help = "Initial condition x_0"
  )
  return parser.parse_args()


def main():
  """Print the orbit and display the time-series plot."""
  args = parseArguments()
  orbit = solveOrbit(args.x0, nSteps)
  indices = np.arange(nSteps)

  for n, x in enumerate(orbit):
    print(f"{n} {x:.12g}")

  plt.figure(figsize = (9, 5))
  plt.plot(indices, orbit, marker = 'o', lw = 1.8, ms = 4, color = 'C0')
  plt.axhline(b / (1.0 - a), color = '0.4', ls = '--', lw = 1.2, label = r"fixed point $x^* = 5$")
  plt.title(r"Orbit of $x_{n+1} = 0.8x_n + 1$")
  plt.xlabel(r"$n$")
  plt.ylabel(r"$x_n$")
  plt.grid(True)
  plt.legend()
  plt.tight_layout()
  plt.show()


if __name__ == "__main__":
  main()
