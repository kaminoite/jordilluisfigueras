# Standalone MPFI validation of a KAMExample torus

This program checks **Figueras–Haro (2024), Theorem 2.18**, specialized to
`d=n=2`, the canonical compatible triple, and the exact golden-ratio frequency.
It evaluates conservative majorants of the constants in Appendix B and checks
the analytic, geometric, arithmetic, domain, and smallness hypotheses.

The implemented Hamiltonian is

\[
H_\epsilon(\varphi,I)=\tfrac12(I_1^2+I_2^2)
 +\epsilon[\cos\varphi_1+\cos\varphi_2+\cos(\varphi_1-\varphi_2)],
\qquad \omega_r=(1,(1+\sqrt5)/2).
\]

**A nonzero-coupling validation is included:** `results/eps0p01.json`, with the
exact frozen Fourier candidate in `results/eps0p01.json.torus`. Its seed is the
course's `KAMExample/results/torus-eps0p01.csv`, followed by two optional local
multiprecision refinement steps.

## Build and independence

Requirements: a C++17 compiler, GNU make, POSIX `getopt_long`, and MPFI with its
MPFR/GMP dependencies. On the course machine MPFI 1.5.4 is installed in
`/usr/local`; that prefix is the Makefile default.

```bash
make
./validateKAM.x --help
make check
make standalone-check
```

For a different arithmetic-library prefix:

```bash
make MPFI_PREFIX=/path/to/prefix
```

All interval wrappers, FFTs, candidate handling, Hamiltonian bounds, refinement,
and theorem checks are in this directory. The build links only
`-lmpfi -lmpfr -lgmp`, besides the compiler's standard runtime libraries. It does
not compile or link TorKam, `codes/lib`, FFTW, or any other numerical code.
The FFT implementation is independent, including its interval twiddle factors.

`make standalone-check` copies the source files into a fresh temporary directory,
builds there, and runs the tests without the surrounding course repository.
Its temporary parent can be selected with `TMPDIR=/path/to/tmp`.
`make clean` removes executables and preserves candidate and certificate files.

## Validate the supplied epsilon = 0.01 example

Run from this directory:

```bash
./validateKAM.x \
  --input ../KAMExample/results/torus-eps0p01.csv \
  --epsilon 1/100 \
  --frequency golden \
  --precision 256 \
  --refine 2 \
  --certificate results/eps0p01.json
```

This run uses 64 modes/points per coordinate for the candidate, a `256 x 256`
validation grid, initial strip width `1/10`, final width `1/20`, and wider
interpolation strip width `1/2`. These CLI widths are in **radians**.
The geometric budget factor is 2 and the ambient domain reserve is `1/10`.

The recorded result, rounded upward for readability, is:

| Quantity | Certified bound |
|---|---:|
| Invariance error `b_E` on the initial complex strip | `1.149e-19` |
| Approximate-symplecticity quantity `nu` | `1.907e-12 < 1` |
| Theorem smallness quantity `theorem_condition` | `0.08691 < 1` |
| Convergence quantity `kappa` | `0.08666 < 1` |
| Distance to the true invariant embedding | `3.753e-10` |
| Final analytic strip width in radians | `0.05` |

The distance is a uniform complex-strip bound in the maximum norm of the
original ambient coordinates `(phi1,phi2,I1,I2)`, with a consistent angular lift.
It concerns the **final frozen candidate**, including the specified exact action
offset. No distance to the original CSV samples or pre-refinement candidate is
asserted.

### Recheck without repeating the numerical computation

```bash
./validateKAM.x \
  --candidate results/eps0p01.json.torus \
  --epsilon 1/100 \
  --precision 320 \
  --certificate /tmp/eps0p01-rechecked.json
```

This exact candidate was successfully checked at both 256 and 320 bits, with
the same candidate fingerprint `fnv1a64:6c443ca42bd2ba62`. The fingerprint is a
convenience identifier, not a cryptographic authenticity check. The sidecar
contains the actual exact coefficients.

Increasing validation precision reduces arithmetic enclosure widths; it does
not improve the fixed polynomial. Use `--refine` or a better numerical seed
when the candidate itself is not accurate enough.

## Exact input semantics

### CSV input

`--input` accepts the 15-column format written by `KAMExample` and the course
continuation program. It checks the square power-of-two grid, ordering, header,
finite numbers, and compatibility with the default frequency.

Only `u1,u2,v1,v2` define the periodic components. The printed residual, energy,
lifted angles, and actions are not used as proof bounds. The uniform grid is
reconstructed from integer indices, rather than rounded printed angles.

The importer constructs coefficients, drops the Nyquist lines, imposes exact
conjugate symmetry, and **chooses exact dyadic coefficients** at the selected
precision. This defines a new explicit polynomial; it does not claim that a
floating-point computation encloses the unknown invariant torus.

The candidate is always

\[
K_0(\theta)=(\theta+u(\theta),\omega_r+v(\theta)),
\]

with the **exact algebraic** action offset `omega_r`, rather than the rounded
offset in the CSV. The residual is independently recomputed for this candidate.

### Parameters and frequency

`--epsilon` is required and specifies an exact decimal, hexadecimal dyadic, or
rational number: e.g. `0.03` or `3/100`. The CSV's epsilon token is not silently
converted into an intended decimal parameter. All evaluations use the explicit
target provided on the command line.

Only `--frequency golden` is supported. The exact arithmetic proof for all
integer modes is in [THEOREM.md](THEOREM.md). A rounded frequency or a scan of
finitely many divisors is not substituted for that proof.

### Native candidate

`--candidate` reads `KAM_CANDIDATE_V1` files. The first line records Fourier size
and storage precision; subsequent rows contain the four complex coefficients
in FFT order, as exact hexadecimal dyadics. Both Nyquist lines are zero, and
`c[-k] = conjugate(c[k])` holds exactly. Native input is rejected if the chosen
precision is insufficient to represent its coefficients exactly.

`--candidate-out FILE` exports a frozen candidate independently. If
`--certificate FILE` is requested, `FILE.torus` is always written beside the
report. Input/output path aliases are rejected.

## Refinement and validation are separate stages

`--refine STEPS` defaults to **zero**. If requested, a local high-precision
additive quasi-Newton method proposes an improved polynomial. It solves the
normal and tangent cohomological equations, determines the normal average from
the average torsion, and fixes the tangent average to zero. Products use a
doubled grid. Each update is frozen to exact, real Fourier coefficients.

The printed refinement defects are sampled diagnostics. The proof does not
assume the refinement was exact or convergent: it starts over with the final
frozen polynomial and computes interval enclosures and analytic tail bounds.

The theorem being checked proves convergence of the **modified** update
`(K + N xiN) composed with (id + xiL)`. As explained in the paper, the numerical
seed may be produced by the additive method. A validator does not need to
execute the theorem's infinite iteration.

## Options and failures

Useful controls:

```text
--modes N             truncate or extend the CSV candidate's Fourier support
--refine STEPS        locally improve the candidate before freezing it
--grid M              rigorous evaluation/DFT grid per angle, M >= 2N
--rho R               initial analytic width (radians)
--rho-final R         positive final analytic width (radians)
--rho-wide R          wider strip for interpolation and mean-tail estimates
--domain-margin R     positive ambient analytic-domain reserve
--sigma-factor F      strictly greater than 1; geometric budget multiplier
```

FFT sizes are powers of two. The theorem uses geometrically decreasing cuts
with ratio `1/2`, fixing its first substep cut to `(rho-rho_final)/6` after
conversion to period-one parameters.

Exit statuses:

* `0`: **VALIDATED** — all implemented sufficient hypotheses passed.
* `1`: **NOT_CERTIFIED** — a sufficient bound or inequality failed. This is not
  a nonexistence conclusion.
* `2`: invalid input, unsupported settings, or I/O failure.

The Gram inverse is currently certified using a conservative Neumann bound
around the unperturbed Gram matrix. It can fail on a wide complex strip even
when a narrower-strip certificate or a better preconditioner would succeed.
In particular, the supplied epsilon `0.03` CSV **does not certify with the
default settings**: the wider-strip Gram bound fails. A positive certificate
for that dataset is not included.

## What is checked

See [THEOREM.md](THEOREM.md) for the detailed mathematical contract and the
mapping to the paper. The implementation includes:

* real and complex MPFI enclosures, strict endpoint comparisons and directed
  decimal serialization;
* a genuinely all-mode Diophantine bound and uniform Rüssmann constants;
* interval FFT residual bounds plus analytic interpolation/aliasing bounds;
* strip-wide Gram invertibility and bounds on the tangent/normal frames;
* the theorem's off-torus torsion and a rigorously enclosed average inverse;
* analytic vector-field and derivative bounds on explicit complex domains;
* embedding and regular real-domain conditions;
* all terms surviving in Appendix B, with conservative common-transpose
  majorants and the required positive budget gaps;
* the convergence, domain, geometry, and final closeness conditions.

JSON intervals enclose **computed quantities**. Fields such as `b_E` are
upper bounds on norms: their left endpoints are not lower bounds on the true
norm. Matrix-average entries, in contrast, enclose the entries themselves.

## Tests

`make check` runs 802 assertions, including:

* interval rational arithmetic and singular inverse rejection;
* analytic mixed Fourier modes, normalization, derivatives and cohomology signs;
* a function invisible on the grid but nonzero between grid points;
* aliasing of the zero Fourier mode;
* exact native serialization, CSV semantics, and invalid candidate invariants;
* CLI errors and input protection through symlinks and hard links;
* the exact integrable torus, including the unit-parameter torsion scaling;
* deliberately failing geometry and smallness conditions;
* an independently generated **nonzero-coupling** certificate at `epsilon=1/10000`.

The epsilon `0.01` CSV-to-certificate run above is a separate end-to-end
validation. The tests and standalone build need no course dataset.

## References and source organization

* `interval.h`: MPFI/MPFR wrappers and outward-rounded output.
* `fourier.cpp`: FFT, finite polynomials, alias bounds and input formats.
* `kamBounds.cpp`: explicit Hamiltonian geometry, rigorous bounds and optional
  numerical refinement.
* `figuerasHaro.cpp`: Tables 1–4 and the theorem conditions.
* `validateKAM.cpp`: command-line interface and certificate output.

J.-Ll. Figueras and A. Haro, **A modified parameterization method for invariant
Lagrangian tori for partially integrable Hamiltonian systems**, *Physica D*
462 (2024), 134127. [DOI](https://doi.org/10.1016/j.physd.2024.134127).

J.-Ll. Figueras, A. Haro and A. Luque, **Rigorous Computer-Assisted Application
of KAM Theory: A Modern Approach**, *Foundations of Computational Mathematics*
17 (2017), 1123–1193. [DOI](https://doi.org/10.1007/s10208-016-9339-3).

The sources are BSD-2-Clause licensed. They implement the cited mathematics
locally; no TorKam source or Numerical Recipes FFT code is incorporated.
