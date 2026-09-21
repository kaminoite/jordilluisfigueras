/** @file kamBounds.h
 * Rigorous bounds for the explicit two-rotator Hamiltonian.
 * Copyright (c) 2026, Jordi-Lluís Figueras. BSD-2-Clause; see LICENSE.
 */
#ifndef KAM_VALIDATION_BOUNDS_H
#define KAM_VALIDATION_BOUNDS_H
#include "fourier.h"
#include <map>

namespace validation
{
using Matrix2 = std::array<std::array<Real, 2>, 2>;
using BoundMap = std::map<std::string, Real>;
Matrix2 invertMatrix(const Matrix2 &matrix);
Real computeMatrixNorm(const Matrix2 &matrix);

struct Bounds
{
  BoundMap values;
  void set(const std::string &name, const Real &value);
  const Real &get(const std::string &name) const;
};
struct Parameters
{
  Real epsilon = Real("1/100");
  Real rho = Real("1/10");
  Real finalRho = Real("1/20");
  Real wideRho = Real("1/2");
  Real domainMargin = Real("1/10");
  Real sigmaFactor = Real(2);
  int gridSize = 256;
};

Bounds computeBounds(const Candidate &candidate, const Parameters &parameters, std::ostream &log);
/** Full d=n=2, canonical, tau=1 specialization; all numbers are enclosures. */
bool checkTheorem(Bounds &bounds, const Parameters &parameters, std::string &reason);
}
#endif
