"""
 * pendulum.py
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

# -----------------------------
# Pendulum parameters
# -----------------------------
g = 9.81          # gravitational acceleration (m/s^2)
L = 1.0           # pendulum length (m)
b = 0.          # damping coefficient
theta0 = 1.2      # initial angle (rad)
omega0 = 0.0      # initial angular velocity (rad/s)

t_max = 20.0
dt = 0.02
t = np.arange(0, t_max + dt, dt)

# -----------------------------
# Pendulum ODE
#   theta' = omega
#   omega' = -(g/L) sin(theta) - b omega
# -----------------------------
def f(theta, omega):
    dtheta = omega
    domega = -(g / L) * np.sin(theta) - b * omega
    return dtheta, domega

# -----------------------------
# RK4 integrator
# -----------------------------
def rk4_step(theta, omega, dt):
    k1_theta, k1_omega = f(theta, omega)

    k2_theta, k2_omega = f(
        theta + 0.5 * dt * k1_theta,
        omega + 0.5 * dt * k1_omega
    )

    k3_theta, k3_omega = f(
        theta + 0.5 * dt * k2_theta,
        omega + 0.5 * dt * k2_omega
    )

    k4_theta, k4_omega = f(
        theta + dt * k3_theta,
        omega + dt * k3_omega
    )

    theta_next = theta + (dt / 6.0) * (k1_theta + 2*k2_theta + 2*k3_theta + k4_theta)
    omega_next = omega + (dt / 6.0) * (k1_omega + 2*k2_omega + 2*k3_omega + k4_omega)

    return theta_next, omega_next

# -----------------------------
# Solve trajectory
# -----------------------------
theta = np.zeros_like(t)
omega = np.zeros_like(t)
theta[0] = theta0
omega[0] = omega0

for i in range(len(t) - 1):
    theta[i+1], omega[i+1] = rk4_step(theta[i], omega[i], dt)

# Wrap angle for cleaner phase portrait visualization
theta_wrapped = (theta + np.pi) % (2 * np.pi) - np.pi

# -----------------------------
# Phase portrait vector field
# -----------------------------
theta_grid = np.linspace(-2*np.pi, 2*np.pi, 33)
omega_grid = np.linspace(-8, 8, 33)
TH, OM = np.meshgrid(theta_grid, omega_grid)

theta_contour = np.linspace(-2*np.pi, 2*np.pi, 401)
omega_contour = np.linspace(-8, 8, 401)
THc, OMc = np.meshgrid(theta_contour, omega_contour)

DTH = OM
DOM = -(g / L) * np.sin(TH) - b * OM
energy = 0.5 * OMc**2 + (g / L) * (1 - np.cos(THc))

# Normalize arrows for display
M = np.hypot(DTH, DOM)
M[M == 0] = 1.0
DTHn = DTH / M
DOMn = DOM / M

# -----------------------------
# Figure setup
# -----------------------------
fig = plt.figure(figsize=(12, 6))
gs = fig.add_gridspec(1, 2, width_ratios=[1.25, 1])

ax_phase = fig.add_subplot(gs[0, 0])
ax_pend = fig.add_subplot(gs[0, 1])

# Phase portrait
energy_levels = np.r_[np.linspace(1.0, 16.0, 8), 2.0 * g / L, np.linspace(20.0, 40.0, 6)]
ax_phase.contour(
    THc, OMc, energy,
    levels = energy_levels,
    colors = '0.75',
    linewidths = 1.0
)
ax_phase.quiver(TH, OM, DTHn, DOMn, M, pivot='mid', alpha=0.7)
ax_phase.set_title("Phase portrait of the pendulum")
ax_phase.set_xlabel(r"$\theta$")
ax_phase.set_ylabel(r"$\omega$")
ax_phase.set_xlim(-2*np.pi, 2*np.pi)
ax_phase.set_ylim(-8, 8)
ax_phase.grid(True)

# Equilibria markers
ax_phase.plot([0], [0], 'ko', ms=6)
ax_phase.plot([np.pi, -np.pi], [0, 0], 'ks', ms=5, alpha=0.6)

# Trajectory and moving point
traj_line, = ax_phase.plot([], [], lw=2)
traj_point, = ax_phase.plot([], [], 'ro', ms=6)

# Pendulum panel
ax_pend.set_title("Pendulum motion")
ax_pend.set_aspect('equal')
ax_pend.set_xlim(-1.2 * L, 1.2 * L)
ax_pend.set_ylim(-1.2 * L, 0.3 * L)
ax_pend.grid(True)

# Fixed pivot
ax_pend.plot(0, 0, 'ko', ms=8)

rod_line, = ax_pend.plot([], [], lw=3)
bob_point, = ax_pend.plot([], [], 'o', ms=16)
time_text = ax_pend.text(
    0.02, 0.95, "", transform=ax_pend.transAxes,
    ha='left', va='top'
)

# Optional angle history text
state_text = ax_phase.text(
    0.02, 0.95, "", transform=ax_phase.transAxes,
    ha='left', va='top',
    bbox=dict(facecolor='white', alpha=0.8, edgecolor='none')
)

# -----------------------------
# Animation functions
# -----------------------------
def init():
    traj_line.set_data([], [])
    traj_point.set_data([], [])
    rod_line.set_data([], [])
    bob_point.set_data([], [])
    time_text.set_text("")
    state_text.set_text("")
    return traj_line, traj_point, rod_line, bob_point, time_text, state_text

def update(frame):
    # Phase portrait update
    traj_line.set_data(theta_wrapped[:frame+1], omega[:frame+1])
    traj_point.set_data([theta_wrapped[frame]], [omega[frame]])

    # Pendulum coordinates
    x = L * np.sin(theta[frame])
    y = -L * np.cos(theta[frame])

    rod_line.set_data([0, x], [0, y])
    bob_point.set_data([x], [y])

    time_text.set_text(f"t = {t[frame]:.2f} s")
    state_text.set_text(
        rf"$\theta = {theta_wrapped[frame]:.2f}$ rad" "\n"
        rf"$\omega = {omega[frame]:.2f}$ rad/s"
    )

    return traj_line, traj_point, rod_line, bob_point, time_text, state_text

ani = FuncAnimation(
    fig, update, frames=len(t),
    init_func=init, interval=1000 * dt, blit=True
)

plt.tight_layout()
plt.show()

# To save as MP4 (requires ffmpeg), uncomment:
# ani.save("pendulum_animation.mp4", fps=int(1/dt))
