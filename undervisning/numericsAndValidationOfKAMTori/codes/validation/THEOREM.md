# Mathematical contract and theorem-to-code map

## 1. Scope and conventions

The target is Theorem 2.18 of Figueras–Haro (2024), specialized using Remarks
2.20–2.21 to `d=n=2`, no additional first integrals, canonical geometry, and
Diophantine exponent `tau=1`. The angle-action/affine-lift adaptation is the
one described in the paper's Section 2.2.

Ambient coordinates are unchanged from KAMExample:
`z=(phi1,phi2,I1,I2)`, with the physical angles of period `2 pi`. For the
paper's conventions choose

\[
\Omega=J_p=\begin{pmatrix}0&-I_2\\ I_2&0\end{pmatrix},\quad
G=I_4,\quad \alpha=I\cdot d\varphi,\quad
\Omega=d\alpha,\quad X_H=\Omega^{-1}\nabla H.
\]

Here the displayed matrix represents the two-form. Thus the vector field is
`(partial_I H,-partial_phi H)`, as in the numerical example. All constant
geometry norms are 1, their derivative bounds are 0, all additional-integral
bounds are 0, and `c_DPhi=1`.

Only the **parameter** is changed to the paper's unit torus:

\[
x=\theta/(2\pi),\qquad
K(x)=(2\pi x+u(2\pi x),\omega_r+v(2\pi x)),\qquad
\omega=\omega_r/(2\pi).
\]

Consequently

\[
L=D_xK=2\pi D_\theta K,\quad
\rho=\rho_r/(2\pi),\quad
\rho_\infty=\rho_{\infty,r}/(2\pi),\quad
\delta=(\rho-\rho_\infty)/6.
\]

The substep cuts have ratio `1/2`; an iteration spends `3 delta_j`, so the
limiting width is exactly `rho_infinity`. The constants use `a=2`. Ambient
coordinates, domain distances, the Hamiltonian and its derivatives are not
rescaled. Averages have normalization `1/M^2`, with no additional `2 pi` factor.

## 2. Exact candidate and arithmetic

All retained Fourier coefficients are exact dyadics; both Nyquist lines are
zero and conjugate symmetry holds exactly. `validateCandidate()` enforces this
contract, including for direct calls to the bounds API. The action offset is
the exact algebraic frequency. The candidate is therefore a specified real
analytic embedding once injectivity has been checked.

MPFI encloses real quantities; complex numbers are pairs of real intervals.
Every proof operation uses these intervals. `upper()` deliberately replaces an
interval evaluation of a bound by an exact dyadic majorant. `lower()` is used
for distances and positive gaps. No ambiguous interval order is used: strict
tests compare an upper endpoint with a lower endpoint. Division by an interval
containing zero, empty intervals, NaNs and infinities cannot pass a proof test.

The numerical proposal stage may take midpoints and freeze coefficients. Its
output is a new candidate, not a claimed enclosure of an unknown exact torus.
The subsequent certification is independent of the numerical proposal.

## 3. Diophantine and Rüssmann bounds

Put `phi=(1+sqrt(5))/2` and `psi=(1-sqrt(5))/2`. For nonzero integer `(p,q)`,

\[
(p+q\phi)(p+q\psi)=p^2+pq-q^2\in\mathbb Z\setminus\{0\},\qquad
|p+q\psi|\le |p|+|q|.
\]

Thus `omega_r=(1,phi)` satisfies `|k.omega_r| >= 1/|k|_1` for **every**
nonzero integer mode. In unit-parameter coordinates,

\[
\gamma=1/(2\pi),\qquad\tau=1.
\]

No finite scan of divisors is used as a replacement for this argument.

Lemma 2.14 and Corollary 2.15 specialize to the uniform constants

\[
\widehat c_R
=\sqrt{\frac{2^3\zeta(2,2)\Gamma(3)}{(2\pi)^4}}
=\frac{\sqrt{\pi^2/6-1}}{\pi^2},\qquad
\widehat c_R^1=4\widehat c_R.
\]

These hold at every strip loss used in the infinite iteration. Both are
evaluated with outward rounding, rather than approximated by finite divisor
sums. `c_R` and `c_R1` in the report are their computed upper bounds.

## 4. Norms, Gram inverse, and embedding

Scalar functions use strip sup norms. Matrix bounds follow the paper's norm

\[
\|A\|_\rho=\max_i\sum_j\sup_{|\Im\theta_\ell|\le\rho}|A_{ij}(\theta)|.
\]

Each finite polynomial is bounded by its weighted Fourier sum. Derivative
coefficients are exactly `ik_j c_k` in radians. Matrix transpose norms are
bounded separately; a vector and its transpose do not have the same norm.

Writing `U=D_theta u` and `V=D_theta v`,

\[
L^TL=(2\pi)^2\left(I+U+U^T+U^TU+V^TV\right).
\]

At both the initial and wider strips the code checks

\[
r_B=b_U+b_{U^T}+b_{U^T}b_U+b_{V^T}b_V<1.
\]

The Banach-algebra Neumann series gives a holomorphic inverse throughout the
strip, with

\[
b_B=\frac1{(2\pi)^2(1-r_B)},\qquad
b_N\le b_L b_B,\qquad b_{N^T}\le b_B b_{L^T},\qquad N=J_pLB.
\]

This is a **transpose** Gram matrix, not a Hermitian matrix. Its inverse is
symmetric, so `B` and `B^T` share the same norm bound.

The additional sufficient test `||D_theta u|| < 1` makes the angular map
`theta+u(theta)` injective modulo the period lattice: apply the Lipschitz
estimate on the convex universal-cover strip, translating one point by a
lattice element if necessary. This proves embedding, not just immersion.
At the limit the code checks

\[
b_{D_\theta u}+r_{D_xK}/(2\pi)<1.
\]

## 5. Explicit domains and Hamiltonian bounds (H1)

The complex domain `U0` is defined by `|Im phi_i| < R0_i` and
`|I_i| < R0_(i+2)`. Its radii are upward-rounded bounds on the corresponding
candidate components, enlarged by `domainMargin`. The outer extension domain
`U` has another `domainMargin` of reserve. The record contains all eight radii
and a lower bound for `dist(K(T_rho), boundary U0)`.

For the literal functional-independence assumption in the theorem's real
setting, use the **real slice of U0 intersected with `I1>0`**. The code checks

\[
I_1\ge1-\|v_1\|_\rho>0,
\qquad 1-\|v_1\|_\rho-r_K>0.
\]

Since `partial H/partial I1 = I1`, the Hamiltonian is regular there. The total
displacement bound keeps the real iteration and its limit in this regular
domain. The normal intermediate displacement is also dominated by the full
one-step majorant. The larger complex analytic-extension domains are allowed
to contain critical points.

Let `S=max(cosh R1,cosh R2)`, `M=cosh(R1+R2)` for the outer angular radii.
Then the implementation uses

\[
\begin{aligned}
c_X&=\max(R_{I_1},R_{I_2},|\epsilon|(S+M)),\\
c_{DX}=c_{DX^T}&=\max(1,|\epsilon|(S+2M)),\\
c_{D^2X}&=|\epsilon|(S+4M),\\
c_{T_H}&=1+|\epsilon|(S+2M),\qquad c_{DT_H}=c_{D^2X}.
\end{aligned}
\]

These are componentwise derivative-sum bounds as required by H1. The equal
transpose bound for `DX` follows from the symmetry of the force Jacobian.

## 6. The theorem's torsion and its average (H2)

For

\[
A=DX_H=\begin{pmatrix}0&I\\ \epsilon C&0\end{pmatrix},\quad
C=\begin{pmatrix}
\cos\varphi_1+\cos(\varphi_1-\varphi_2)&-\cos(\varphi_1-\varphi_2)\\
-\cos(\varphi_1-\varphi_2)&\cos\varphi_2+\cos(\varphi_1-\varphi_2)
\end{pmatrix},
\]

Eq. (2.9) is

\[
T_H=\Omega A-A\Omega
=\operatorname{diag}(-(I+\epsilon C),I+\epsilon C),\qquad
T=N^TT_H(K)N.
\]

This formula is used even off invariance. The derivative-based torsion in the
double-precision course solver is a different off-torus quantity.

Grid values of `L`, `B`, `N` and `T` are enclosed with MPFI, including each
2-by-2 inverse. The sampled mean is enlarged by the analytic mean-alias bound
below **in every entry**. A direct interval inverse of this enlarged average
then bounds `||<T>^-1||`. Invertibility on a grid alone is not used to certify
strip-wide invertibility.

The strict budgets are

\[
\begin{aligned}
\sigma_L=\sigma_{L^T}&=f\max(b_L,b_{L^T}),\\
\sigma_N=\sigma_{N^T}&=f\max(b_N,b_{N^T}),\\
\sigma_B&=f b_B,\qquad \sigma_{\langle T\rangle^{-1}}=f b_{\langle T\rangle^{-1}},
\end{aligned}
\]

rounded upward, with `f=sigmaFactor>1`. Every gap between a budget and an
initial bound is required to have a strictly positive lower bound.

## 7. Rigorous FFT, interpolation and mean-alias bounds

The FFT implements

\[
\widetilde f_k=M^{-2}\sum_{i,j=0}^{M-1}
f(2\pi i/M,2\pi j/M)e^{-2\pi\mathrm i(k_1i+k_2j)/M}.
\]

It encloses the **discrete** coefficients. For a function bounded by `F` on
a wider strip `w`, its true coefficients satisfy
`|fhat_k| <= F exp(-w |k|_1)`.

Let `q=exp(-(w-rho))` and use the half-open FFT rectangle. The exact alias
identity is `ftilde_k = sum_m fhat_(k+Mm)`. Each omitted mode folds to a
representative with no larger `l1` index. Consequently

\[
\begin{aligned}
\|f-I_Mf\|_\rho
&\le2F\sum_{k\text{ outside}}q^{|k|_1}\\
&\le 8F\,q^{M/2}\frac{1+q}{(1-q)^2}.
\end{aligned}
\]

The union bound includes both axes and the Nyquist modes; its overcounting is
conservative. It is a simpler, less sharp bound derived from the same alias
identity as Figueras–Haro–Luque, Section 3. Thus

\[
b_E=\max_i\sum_{k\text{ in grid}}|\widetilde E_{i,k}|e^{\rho_r|k|_1}
       +C_{\mathrm{grid}}M_E
\]

bounds the full continuous residual. All weights and sums are enclosed.
The independent wider-strip bound `M_E` comes from

\[
E_\varphi=v-D_\theta u\,\omega_r,\qquad
E_I=\epsilon(\sin\varphi_1+\sin(\varphi_1-\varphi_2),
\sin\varphi_2-\sin(\varphi_1-\varphi_2))-D_\theta v\,\omega_r.
\]

The exact constant action offset has been canceled symbolically.

For the mean, let `q=exp(-w M)`. Only frequencies in `M Z^2` alias into zero,
so

\[
|\langle f\rangle-M^{-2}\sum f(\theta_{ij})|
\le F\left[\left(\frac{1+q}{1-q}\right)^2-1\right]
=\frac{4Fq}{(1-q)^2}.
\]

The wider-strip torsion bound is `M_T <= b_Nt(w) c_Th(w) b_N(w)`.
It bounds every matrix entry, so the above error may safely inflate each
sampled mean entry before inversion. These computations require only the
finite candidate, not an assumed analyticity width of the unknown exact torus.

## 8. Appendix B implementation map

The code uses `g=gamma*delta`,

\[
e_* = \max(b_{\eta^L},b_{\eta^N}/g),\quad
e_*'=e_*/\delta,\quad \chi=e_*/(\gamma\delta^2).
\]

The projected residual majorants are conservatively obtained as
`b_etaL=b_Nt*b_E`, `b_etaN=b_DKt*b_E`. Their exact zero-average compatibility
is the geometric identity for an exact symplectic Hamiltonian, as in the
paper; no numerical zero-mode scan is used to prove it.

| Code quantities | Paper |
|---|---|
| `C_OmegaL`, `C_OmegaN`, `C_sym`, `nu` | Table 1, (3.2), (3.3), (3.7), (3.8) |
| `C_E_L/N`, `C_Et_L/N`, `C_DE`, `C_DEt` | Table 1, (3.9)–(3.12) |
| `C_LieK/L/Lt/G/B/N`, `C_T` | Table 1, (3.13)–(3.19) |
| `C_redLL/NL/NN/LN` and components | Table 1, (3.21)–(3.24) |
| `C_meanXiN`, `C_xiN`, `C_barK`, `C_barDK_common`, `C_barE`, `Q_barEtaN` | Table 2, (3.44)–(3.58) |
| `C_xiL`, `C_deltaK/DK/G/B/N/T/InvT` | Table 3, (3.60)–(3.73) |
| `C_LieXiL`, `C_newE`, `Q_etaN`, `Q_etaL1`–`Q_etaL5`, `Q_etaL` | Table 3, (3.76)–(3.87) |
| `a`, `Q_eta`, `C_dist`, `C_Delta`, `theorem_C`, `kappa` | Table 4, (3.88)–(3.99) |
| `distance_K/DK/DKt/B/N/Nt/InvT` | (2.32)–(2.38) |

Terms multiplying first-integral or nonconstant-geometry derivatives vanish
in this specialization. In particular `Q_etaL4=0`.

There are two different pair conventions in the tables. The `E`, `E^T`,
`DE`, `(DE)^T` and `redNN` coefficients combine as `C_L+g C_N`; the
already-weighted normal/tangent correction pairs and `redLN` combine as
`C_L+C_N`. The code preserves this distinction.

### Conservative common-transpose bounds

For the intermediate normal correction the code uses the common bound

\[
C_{\Delta\bar{DK},\mathrm{common}}
=4\sigma_N(C_{\widehat\xi^N_0}^L+C_{\widehat\xi^N_0}^N+c_R^1).
\]

The factor 4 dominates the factors `d=2` and `n=2` in Table 2. The final
common derivative bound uses `2n=4`, covering both (3.64) and (3.65).
Since `L=DK`, the same bound applies to changes in `L` and `L^T`.

For constant canonical geometry, directly transposing `N=J_p L B` gives

\[
C_{\Delta N^T}\le\sigma_B C_{\Delta L^T}
                  +C_{\Delta B}\sigma_{L^T}.
\]

The common budgets implement this bound and its non-transposed counterpart.
This avoids identifying row and column norms or relying on the untransposed
symbols printed in Table 3's row (3.71). Subsequent constants are enlarged
consistently. The numerical certificate therefore uses conservative majorants,
not a claim of reproducing the paper's sharpest constants.

### Final inequalities and distances

Set

\[
Q_\eta=\max(Q_{\eta^L},2Q_{\eta^N}),\qquad
\kappa=4Q_\eta\chi,
\]

and compute `C_Delta` from all six positive geometry-budget gaps. Then

\[
\mathcal C=\max\{\gamma\delta C_{sym},\ C_{\xi^L},\
\delta C_{dist}+2Q_\eta,\ C_\Delta+4Q_\eta\}.
\]

The code requires `nu<1`, `C*chi<1`, `kappa<1`, and checks each component of
the maximum explicitly. It then computes

\[
r_K=\frac{2}{2-\kappa}\frac{C_{\Delta K}}{\gamma\delta}e_*,\qquad
r_{DK}=\frac{C_{\Delta DK,\mathrm{common}}}{1-\kappa}\chi,
\]

and the analogous inverse/frame distances. The additional limiting embedding
and regular real-domain reserves must also pass. All comparisons use strict
interval endpoint inequalities.

## References checked locally

* `Figueras_Haro_A_modified_parameterization_method_for_invariant_Lagrangian_tori_for_partially_integrable_Hamiltonian_systems_Physica_D_462_2024.pdf`
  — Theorem 2.18, Remarks 2.20–2.24, Lemma 2.14, Corollary 2.15,
  Lemma 3.6, Section 3.3, Appendix B.
* `Figueras_Haro_Luque_Rigorous_Computer-Assisted_Application_of_KAM_Theory:_A_Modern_Approach_Foundations_of_Computational_Mathematics_1_71_2016.pdf`
  — Section 3 (alias identity and interpolation bounds) and Section 5
  (validation methodology). This local filename is the online-first version;
  the published volume is *Found. Comput. Math.* 17 (2017), 1123–1193.
