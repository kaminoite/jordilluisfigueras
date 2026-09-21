# Common KAM numerical code

`kam.h` / `kam.cpp` implement the FFT, spectral differentiation, interpolation,
cohomological inverse, coupled-rotator Hamiltonian, adapted frame, torsion,
quasi-Newton correction, fine-grid checks, phase normalization and CSV output.
Both `../KAMExample` and `../continuation` compile this implementation directly
into their executables; no external numerical library is needed.

`solveTorus(Field&, Options, ostream*, bool damping)` accepts a supplied initial
torus and returns a `SolveResult` without writing files. The optional stream
receives the original example's convergence log. Damping adds residual-based
backtracking. On failure, the field may hold an improved but unconverged
iterate; callers must preserve their own last accepted torus.

The coordinate order is `(phi1,phi2,I1,I2)`. A `Field` contains only the periodic
part `(u1,u2,v1,v2)` of `K(theta)=(theta+u,omega+v)`. The conventions are
`Lie_omega=-omega.dot(partial_theta)` and `J=[0,Id;-Id,0]`.

`normalizePhase` translates the entire Fourier embedding to make `<u>=0`.
Subtracting the mean of `u` without translating the other components would
change the invariant torus and is not equivalent.

The implementation follows the separately BSD-licensed TorKam Lagrangian
solver. Attribution and the full redistribution notice are retained at the
top of `kam.cpp`; nothing from the external TorKam installation is linked.
