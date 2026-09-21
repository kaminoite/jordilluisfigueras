# Numerics and validation of KAM tori

Course materials by **Jordi-Lluís Figueras**, Universitat Politècnica de
Catalunya (UPC), Barcelona, Spain.

XXVII International Workshop for Young Mathematicians “Dynamical Systems”,
20–26 September 2026, Jagiellonian University, Kraków.

## Contents

- [PDF slides](slides/slides.pdf).
- [Interactive coupled pendula](codes/coupled_pendula.py), with
  [initial-condition examples](codes/coupled_pendula_examples.md).
- [Numerical KAM example](codes/KAMExample/README.md): a double-precision
  quasi-Newton solver, its Makefile, plotting script, and example results.
- [Shared numerical library](codes/lib/README.md): the source files required
  by the numerical example, including its own FFT.
- [Rigorous KAM validation](codes/validation/README.md): an independent
  interval-arithmetic validator, tests, [theorem documentation](codes/validation/THEOREM.md),
  and a recorded certificate with its exact Fourier candidate.

Keep the directory structure intact: `codes/KAMExample` requires `codes/lib`
as a sibling directory. The two KAM programs use the coupled-rotator Hamiltonian
described in their READMEs; the pendulum GUI illustrates a different Hamiltonian.

**All commands below are run from this directory (`toWebSite`).**
The detailed component READMEs instead use their respective component directories.

## Dependencies

The commands are intended for Linux (or Linux under WSL). The C++ programs use
POSIX/GNU `getopt_long`, a C++17 compiler, and GNU make.

| Component | Dependencies |
| --- | --- |
| PDF slides | Any PDF viewer |
| Coupled-pendulum GUI | Python 3, NumPy, Matplotlib, and an interactive GUI backend such as TkAgg |
| Numerical KAM solver | C++17 compiler and GNU make; no external numerical libraries |
| Optional numerical plots | Python 3, NumPy, Matplotlib; uses the noninteractive Agg backend |
| Rigorous validator | C++17 compiler, GNU make, MPFI, MPFR, and GMP (development headers and libraries) |

On Debian/Ubuntu, install the system dependencies with:

```bash
sudo apt update
sudo apt install build-essential python3 python3-venv python3-tk libmpfi-dev libmpfr-dev libgmp-dev
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install numpy matplotlib
```

Activate `.venv` again in a new terminal before running the Python programs.
The GUI requires a graphical desktop/display. Under WSL, use WSLg or another
working graphical display. The plotting script can run headlessly.

External arithmetic libraries: [MPFI](https://mpfi.org/),
[MPFR](https://www.mpfr.org/), and [GMP](https://gmplib.org/).
They are installed separately and retain their own licenses.
Neither C++ program needs TorKam or FFTW.

## 1. Explore the coupled pendula

```bash
python3 codes/coupled_pendula.py
python3 codes/coupled_pendula.py --help
```

Click either phase-space panel to select that pendulum's position and momentum,
then click **Run**. Both selections define one four-dimensional initial state.
**Random** adds a batch of trajectories; **Clear** removes them. The coupling
slider applies to subsequent runs. **Fading trail** controls the visible history.

For example:

```bash
python3 codes/coupled_pendula.py --epsilon 0.1 --duration 400 --dt 0.005 --initial-state 0.8 -0.4 0 0
```

State order is `(q1, q2, p1, p2)`, with angles in radians. Integration uses
fixed-step symplectic Störmer–Verlet. The panels are phase-space projections,
not Poincaré sections. If Matplotlib selects a noninteractive backend, try:

```bash
MPLBACKEND=TkAgg python3 codes/coupled_pendula.py
```

The simulation button embedded in the lecture PDF points to the lecturer's
local presentation server. For this download, launch the GUI with the commands above.

## 2. Compute a numerical KAM torus

```bash
make -C codes/KAMExample
codes/KAMExample/exampleKAM.x --help
make -C codes/KAMExample check
codes/KAMExample/exampleKAM.x --epsilon 0.01 --grid 64 --tolerance 1e-12 --output torus.csv
```

The Makefile compiles `exampleKAM.cpp` together with `../lib/kam.cpp`.
The default target frequency is `(1, (1+sqrt(5))/2)`. The last command writes
`torus.csv` in this directory; it contains the sampled embedding, periodic
components, residuals, and energy. `--grid` is the number of points per angle
(a power of two between 8 and 256). Nonlinear operations use a doubled grid;
the final sampled residual is checked on a grid four times as large per angle.

Exit codes: `0` means numerical convergence, `1` numerical or I/O failure,
and `2` invalid options. Numerical convergence is not an existence proof;
the next program performs the rigorous validation.

### Optional: regenerate the numerical figures

```bash
python3 codes/KAMExample/plot_results.py --results-dir numerical-results --figures-dir figures
```

This runs the solver for epsilon `0.01` and `0.03`, producing CSV data and
diagnostics under `numerical-results/`, and PNG/PDF figures under `figures/`.
It creates both directories. The plots show convergence, the embedding,
Fourier decay, truncation errors, and comparison with independent RK4 integration.
Alternatively, `make -C codes/KAMExample figures` uses the original course
locations `codes/KAMExample/results/` and `slides/images/`.

## 3. Validate a KAM torus rigorously

With Debian/Ubuntu arithmetic packages installed under `/usr`:

```bash
make -C codes/validation MPFI_PREFIX=/usr
codes/validation/validateKAM.x --help
make -C codes/validation MPFI_PREFIX=/usr check
```

For a custom MPFI installation, replace `/usr` with its installation prefix.
The Makefile defaults to `/usr/local`, adds include/library search paths and
a runtime library path, and links `-lmpfi -lmpfr -lgmp`. If changing the prefix
after a build, run `make -C codes/validation clean` before rebuilding.
Additional nonstandard MPFR/GMP locations can be supplied through `CPPFLAGS`
and `LDFLAGS`.

Validate the `torus.csv` generated above:

```bash
codes/validation/validateKAM.x --input torus.csv --epsilon 1/100 --frequency golden --precision 256 --refine 2 --certificate validation.json
```

Or use the supplied numerical dataset:

```bash
codes/validation/validateKAM.x --input codes/KAMExample/results/torus-eps0p01.csv --epsilon 1/100 --precision 256 --refine 2 --certificate validation-supplied.json
```

Each command writes a JSON report and an exact `.json.torus` sidecar. Refinement
first improves the seed; interval bounds are then recomputed independently for
the frozen Fourier polynomial. Only the exact golden-ratio frequency is supported.
Epsilon is specified exactly (`1/100` here); strip widths are in radians.
Default precision is 256 bits and the validation grid is 256 points per angle.
This calculation is substantially more expensive than the numerical solver.

To recheck the included frozen candidate without numerical refinement:

```bash
codes/validation/validateKAM.x --candidate codes/validation/results/eps0p01.json.torus --epsilon 1/100 --precision 320 --certificate validation-rechecked.json
```

The included result certifies epsilon `0.01`; see the component README for
the theorem, bounds, and their exact meaning. The epsilon `0.03` numerical
dataset is also supplied, but does not certify with the default settings.

Validator exit codes:

- `0`: **VALIDATED** — all implemented sufficient hypotheses passed.
- `1`: **NOT_CERTIFIED** — a sufficient condition failed; this does not prove nonexistence.
- `2`: invalid input, unsupported settings, or I/O failure.

For an isolated build-and-test check of the validator:

```bash
make -C codes/validation MPFI_PREFIX=/usr standalone-check
```

## Attribution and license

Copyright © 2026 **Jordi-Lluís Figueras**.
The distributed source code and Makefiles are licensed under the
**BSD 2-Clause License**; see [codes/LICENSE](codes/LICENSE).
Source headers retain the author attribution and redistribution notices.
The validator also includes its own identical `LICENSE` for standalone use.
The software license applies to the code; the lecture PDF retains the image
and source acknowledgements shown in the slides.

The validator implements the mathematics of J.-Ll. Figueras and A. Haro,
*A modified parameterization method for invariant Lagrangian tori for partially
integrable Hamiltonian systems*, Physica D 462 (2024), 134127,
[doi:10.1016/j.physd.2024.134127](https://doi.org/10.1016/j.physd.2024.134127).
