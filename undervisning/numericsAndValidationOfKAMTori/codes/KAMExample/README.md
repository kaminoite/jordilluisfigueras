# A standalone KAM example

Build and run with a C++17 compiler and GNU make:

```bash
make
./exampleKAM.x
./exampleKAM.x --help
make check
```

No TorKam, FFTW, GMP, MPFR, or other numerical library is required. The only
non-standard C++ interface is POSIX/GNU `getopt_long` for command-line parsing
(available on the course's Linux environment).

The numerical routines now live in the local common library `../lib/kam.h`
and `../lib/kam.cpp`, shared with `../continuation`. The Makefile compiles that
source automatically. Keep `codes/lib/` alongside this directory when copying
the example; it is self-contained within the course repository.

## Hamiltonian and notation

The two-degree-of-freedom example is

\[
H_\varepsilon(\varphi,I)=\tfrac12(I_1^2+I_2^2)
+\varepsilon[\cos\varphi_1+\cos\varphi_2+\cos(\varphi_1-\varphi_2)].
\]

At zero coupling, `I=omega` is an invariant torus. The mixed cosine couples the
two rotators. We prescribe `omega=(1,(1+sqrt(5))/2)` by default and find

\[
K(\theta)=(\theta+u(\theta),\omega+v(\theta)),\qquad
X_H(K)-DK\,\omega=0.
\]

Both `u` and `v` are periodic; the nonperiodic lift `theta` is never sent through
the FFT. Angles have period **2 pi**, and the ordering is **(phi1,phi2,I1,I2)**.
The initial guess is `u=v=0`.

## Connection to TorKam and the slides

The geometric step follows the separately BSD-licensed
`src_UTILS/KAMLagrangian.cpp` in
`/home/figueras/work/UTILS/lib_TorKam/torkam-dev`, especially
`compute_N_LAG`, `compute_invP_LAG`, `compute_torsion_LAG`, `compute_etaK`,
`solve_xi_of_K_LAG`, and `KAM_LAG_step`. The standalone implementation replaces
its multiprecision grids and linear tools with `std::vector`, `std::complex`,
a radix-2 FFT and checked 2-by-2 matrix operations. The common source credits the
original routines and retains their copyright/license notice.

Each correction follows the slide sequence:

1. Compute `L=DK` and `E=X_H(K)-L*omega` using spectral differentiation.
2. Construct `N=-J*L*(L^T*L)^(-1)` and store `P=(L,N)` as its two blocks.
3. Use `Q=-J*P^T*J` as the approximate inverse and compute
   `eta=-Q*E=(N^T*J*E,-L^T*J*E)`.
4. Compute `T=-N^T*J*(Lie_omega N+DX_H(K)*N)`.
5. Solve the nonzero Fourier modes of `Lie_omega xiN=etaN`, where
   `Lie_omega=-omega.dot(partial_theta)` and the divisor is `-i*k.dot(omega)`.
6. Solve `<T>*c=<etaL-T*tildeXiN>` to fix `<xiN>=c`.
7. Solve `Lie_omega xiL=etaL-T*xiN`, setting `<xiL>=0` to fix the phase.
8. Update the periodic part by `Delta=L*xiL+N*xiN` and recompute the residual.

The normal equation's average vanishes geometrically; the program prints its
numerical size before projecting it out. Singular/ill-conditioned Gram or
average torsion matrices and numerically unresolved divisors cause failure.
Custom frequencies are checked only on the retained modes; this finite check
is not a Diophantine proof.

## Fourier resolution and output

`-n N` retains modes with `|k1|,|k2| < N/2`; Nyquist lines are excluded to avoid
ambiguities in real-valued interpolation. Nonlinear operations are evaluated
on a **2N by 2N** zero-padded grid. This avoids aliasing into the retained band
for quadratic products of retained series and reduces aliasing for the
nonpolynomial operations. The latter are checked through the final residual.

Convergence requires the unprojected residual to be below `--tolerance` on the
work grid **and** a **4N by 4N** check grid. The program also reports the energy
oscillation and the largest embedding coefficient in the outer quarter of the
Fourier band. These are floating-point numerical checks, not rigorous bounds
or an existence validation. A stalled iteration may need a larger `-n`, a
smaller perturbation, or a tolerance compatible with double precision.

```bash
./exampleKAM.x -e 0.01 -n 32 -t 1e-11 -o torus.csv
./exampleKAM.x -e 0.03 -n 64 -t 1e-10 -o torus-finer.csv
```

The CSV contains the base grid, the lifted embedding, its periodic parts,
the four residual components, and the energy. Its first comment line records
epsilon and omega. `phi1` and `phi2` are unwrapped; reduce modulo `2*pi` for
plots if desired. Output is written only on convergence. Exit status is zero
on success, one on numerical/I/O failure, and two for invalid options.
`make clean` removes the executable and preserves computed CSV files.

`make check` runs analytic checks of Fourier differentiation, the cohomological
inverse, dealiased multiplication and Hamiltonian derivatives, followed by
integrable and coupled end-to-end computations. The latter use `/dev/null`
instead of creating output files.

## Rigorous existence validation

The separate, self-contained C++ program in [`../validation/`](../validation/README.md)
checks the modified Figueras–Haro a posteriori theorem for this Hamiltonian and
the exact golden-ratio frequency. It requires MPFI/MPFR/GMP and does not link
TorKam or the numerical common library.

From this directory, for example:

```bash
make -C ../validation
../validation/validateKAM.x --input results/torus-eps0p01.csv \
  --epsilon 1/100 --precision 256 --refine 2 --certificate validation.json
```

The optional refinement improves the seed at multiprecision; the validator
then independently checks a frozen Fourier polynomial with interval arithmetic
and analytic tail bounds. The exact frequency and action offset are specified
algebraically, rather than treating the rounded CSV frequency as Diophantine.
See the validator's README for a successful nonzero-coupling certificate,
rechecking instructions, precise input semantics, and scope.

## Reproduce the numerical slides

The optional plotting stage requires Python 3, NumPy and Matplotlib:

```bash
python3 -m pip install numpy matplotlib
make figures
```

`plot_results.py` runs the solver at `epsilon=0.01` and `0.03`, both with
`N=64` and tolerance `1e-12`. It saves fresh torus CSV files, solver logs,
convergence histories, diagnostic tables, and `summary.json` under `results/`.
The four figures (PDF and PNG) and a small TeX file of measured values are
written to `../../slides/images/kam-*`. The standalone solver itself still
needs only C++.

The plots show:

- Sampled residual versus quasi-Newton correction count, on the `2N` work grid.
- The two action displacements over the parameter torus for `epsilon=0.03`.
- Fourier coefficient envelopes and the residual of **truncations of the same
  converged torus** to `N=8,16,32,64`, each checked on a `4N` grid. These are
  not independent Newton runs at the smaller resolutions.
- `K(theta0+omega*t)` against independent RK4 integration on `0 <= t <= 20`,
  with time-step halving to distinguish integration error from torus error.

The script independently recomputes the final fine-grid residual using NumPy
and checks the trajectory agreement before completing. Its figure labels and
slide captions refer to sampled numerical errors, not rigorous sup-norm bounds.
It leaves the default `torus.csv` from manual runs untouched.
