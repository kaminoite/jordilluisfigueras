"""
 * cobWeb.py
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

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.widgets import Slider

# -----------------------------
# Logistic map parameters
# -----------------------------
r = 3.5
x0 = 0.18
nSteps = 60

# -----------------------------
# Logistic map
# -----------------------------
def f(x):
    return r * x * (1.0 - x)

def solveOrbit():
    x = np.zeros(nSteps + 1)
    x[0] = x0

    for i in range(nSteps):
        x[i + 1] = f(x[i])

    return x

# -----------------------------
# Solve trajectory
# -----------------------------
x = solveOrbit()

# -----------------------------
# Data for plots
# -----------------------------
xGrid = np.linspace(0.0, 1.0, 600)
yGrid = f(xGrid)
nGrid = np.arange(nSteps + 1)

# -----------------------------
# Figure setup
# -----------------------------
fig = plt.figure(figsize = (12, 6))
fig.subplots_adjust(bottom = 0.24)
gs = fig.add_gridspec(1, 2, width_ratios = [1.15, 1.0])

axCob = fig.add_subplot(gs[0, 0])
axOrbit = fig.add_subplot(gs[0, 1])

# Cobweb panel
mapLine, = axCob.plot(xGrid, yGrid, color = 'C0', lw = 2, label = r"$y = rx(1-x)$")
axCob.plot(xGrid, xGrid, color = '0.4', lw = 1.5, ls = '--', label = r"$y = x$")
axCob.set_title("Cobweb diagram for the logistic map")
axCob.set_xlabel(r"$x_n$")
axCob.set_ylabel(r"$x_{n+1}$")
axCob.set_xlim(0.0, 1.0)
axCob.set_ylim(0.0, 1.0)
axCob.grid(True)
axCob.legend(loc = 'lower left')

cobLine, = axCob.plot([], [], color = 'crimson', lw = 1.8)
cobPoint, = axCob.plot([], [], 'o', color = 'crimson', ms = 6)

stateText = axCob.text(
    0.03, 0.96, "", transform = axCob.transAxes,
    ha = 'left', va = 'top',
    bbox = dict(facecolor = 'white', alpha = 0.85, edgecolor = 'none')
)

# Orbit panel
axOrbit.set_title("Forward orbit")
axOrbit.set_xlabel(r"$n$")
axOrbit.set_ylabel(r"$x_n$")
axOrbit.set_xlim(0, nSteps)
axOrbit.set_ylim(0.0, 1.0)
axOrbit.grid(True)

orbitLine, = axOrbit.plot([], [], color = 'C2', lw = 2)
orbitPoint, = axOrbit.plot([], [], 'o', color = 'C2', ms = 6)

paramText = axOrbit.text(
    0.03, 0.96,
    rf"$r = {r:.2f}$" "\n" rf"$x_0 = {x0:.2f}$",
    transform = axOrbit.transAxes,
    ha = 'left', va = 'top',
    bbox = dict(facecolor = 'white', alpha = 0.85, edgecolor = 'none')
)

# Slider for the parameter r
axSlider = fig.add_axes([0.18, 0.03, 0.64, 0.04])
rSlider = Slider(axSlider, r"$r$", 0.0, 4.0, valinit = r, valstep = 0.01)

# -----------------------------
# Animation functions
# -----------------------------
def init():
    cobLine.set_data([], [])
    cobPoint.set_data([], [])
    orbitLine.set_data([], [])
    orbitPoint.set_data([], [])
    stateText.set_text("")
    return cobLine, cobPoint, orbitLine, orbitPoint, stateText, paramText

def update(frame):
    xPath = [x[0], x[0]]
    yPath = [0.0, x[1]]

    for i in range(1, frame + 1):
        xPath.extend([x[i], x[i]])
        yPath.extend([x[i], x[i + 1]])

    cobLine.set_data(xPath, yPath)
    cobPoint.set_data([x[frame]], [x[frame + 1]])

    orbitLine.set_data(nGrid[:frame + 2], x[:frame + 2])
    orbitPoint.set_data([frame + 1], [x[frame + 1]])

    stateText.set_text(
        rf"$n = {frame + 1:d}$" "\n"
        rf"$x_n = {x[frame]:.4f}$" "\n"
        rf"$x_{{n+1}} = {x[frame + 1]:.4f}$"
    )

    return cobLine, cobPoint, orbitLine, orbitPoint, stateText, paramText

def updateParameter(_):
    global r
    global x
    global yGrid

    r = rSlider.val
    x = solveOrbit()
    yGrid = f(xGrid)

    mapLine.set_data(xGrid, yGrid)
    paramText.set_text(
        rf"$r = {r:.2f}$" "\n" rf"$x_0 = {x0:.2f}$"
    )

    init()
    ani.event_source.stop()
    ani.frame_seq = ani.new_frame_seq()
    fig.canvas.draw_idle()
    ani.event_source.start()

ani = FuncAnimation(
    fig, update, frames = nSteps,
    init_func = init, interval = 500, blit = False
)

rSlider.on_changed(updateParameter)

plt.show()

# To save as MP4 (requires ffmpeg), uncomment:
# ani.save("cobweb_animation.mp4", fps = 2)
