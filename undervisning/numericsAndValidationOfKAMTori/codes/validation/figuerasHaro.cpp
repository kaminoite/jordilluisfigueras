/**
 * @file figuerasHaro.cpp
 * @brief Figueras--Haro (Physica D 462, 2024, 134127), Theorem 2.18.
 * Specialization d=n=2, canonical compatible triple, tau=1, no extra integrals.
 * Tables 1--4 are evaluated by conservative common-transpose majorants.
 * Copyright (c) 2026, Jordi-Lluís Figueras. BSD-2-Clause; see LICENSE.
 */
#include "kamBounds.h"

namespace validation
{
bool checkTheorem(Bounds &bounds, const Parameters &, std::string &reason)
{
  auto record = [&](const std::string &name, const Real &expression)
  {
    Real result = upper(expression);
    bounds.set(name, result);
    return result;
  };
  auto positiveGap = [&](const std::string &name, const Real &budget, const Real &bound)
  {
    Real result = lower(budget-bound);
    bounds.set(name, result);
    if(!less(0, result))
    {
      throw NotCertified("Nonpositive theorem budget: " + name);
    }
    return result;
  };
  const Real &rho = bounds.get("rho"), &delta = bounds.get("delta");
  const Real &gamma = bounds.get("gamma");
  const Real &sL = bounds.get("sigma_L"), &sB = bounds.get("sigma_B");
  const Real &sN = bounds.get("sigma_N"), &sT = bounds.get("sigma_invT");
  const Real &cX = bounds.get("c_X"), &cDX = bounds.get("c_DX");
  const Real &cD2X = bounds.get("c_D2X"), &cTh = bounds.get("c_Th");
  const Real &cDTh = bounds.get("c_DTh");
  Real gd = gamma*delta, gd2 = gamma*square(delta);

  // Lemma 2.14: d=2,tau=1, zeta(2,2)=pi^2/6-1, Gamma(3)=2.
  Real cR = record("c_R", sqrt(square(pi())/6-1)/square(pi()));
  Real cR1 = record("c_R1", 4*cR); // Corollary 2.15.
  Real error = record("weighted_error", maxUpper(bounds.get("b_etaL"), bounds.get("b_etaN")/gd));
  Real errorPrime = error/delta;
  Real chi = record("chi", error/gd2);

  // Table 1: (3.2), (3.3), (3.7), (3.8).
  Real cOmegaL = record("C_OmegaL", 2*cR1);
  Real cOmegaN = record("C_OmegaN", square(sB)*cOmegaL);
  Real cSym = record("C_sym", maxUpper(cOmegaL, cOmegaN));
  Real nu = record("nu", cSym*errorPrime);
  if(!less(nu, 1))
  {
    reason = "Approximate symplecticity test nu < 1 failed";
    return false;
  }
  Real denominator = 1-square(nu);
  // (3.9)--(3.12). sL and sN dominate their own transpose norms.
  Real cEL = record("C_E_L", (sL+sN*nu)/denominator);
  Real cEN = record("C_E_N", (sN+sL*nu)/denominator);
  Real cE = record("C_E", cEL+gd*cEN);
  Real cEtL = record("C_Et_L", 2*cEL);
  Real cEtN = record("C_Et_N", 2*cEN);
  Real cEt = record("C_Et", cEtL+gd*cEtN);
  Real cDE = record("C_DE", 2*(1+sN*cEL+sL*cEN)*cE);
  Real cDEt = record("C_DEt", 2*(1+sN*cEtL+sL*cEtN)*cEt);
  // (3.13)--(3.19); constants multiplying additional first integrals vanish.
  record("C_LieK", cE*error+cX);
  Real cLieL = record("C_LieL", cDE*errorPrime+cDX*sL);
  Real cLieLt = record("C_LieLt", cDEt*errorPrime+cDX*sL);
  Real cLieG = record("C_LieG", (cLieL+cLieLt)*sL);
  Real cLieB = record("C_LieB", square(sB)*cLieG);
  Real cLieN = record("C_LieN", cLieL*sB+sL*cLieB);
  Real cT = record("C_T", square(sN)*cTh);
  // (3.21)--(3.24).
  record("C_redLL_L", 2+2*sN*cEL);
  record("C_redLL_N", 2*sN*cEN);
  Real cRedNLL = record("C_redNL_L", 2*sL*cEL);
  Real cRedNLN = record("C_redNL_N", 2+2*sL*cEN);
  Real cRedNNL = record("C_redNN_L", 2+2*sN*cEL);
  Real cRedNNN = record("C_redNN_N", 2*sN*cEN);
  Real cRedNN = record("C_redNN", cRedNNL+gd*cRedNNN);
  Real cRedLNL = record("C_redLN_L", square(sB)*cRedNLL);
  Real cRedLNN = record("C_redLN_N", gd*square(sB)*cRedNLN+sB*cOmegaL*cLieB);
  Real cRedLN = record("C_redLN", cRedLNL+cRedLNN);

  // Table 2: (3.44)--(3.58). Pair coefficients bound etaL and etaN/(gamma*delta).
  Real cMeanN = record("C_meanXiN_N", (delta/rho)*sT*cT*cR);
  record("C_meanXiN_L", sT);
  Real cXiNN = record("C_xiN_N", cMeanN+cR);
  record("C_xiN_L", sT);
  Real cXiN = record("C_xiN", sT+cXiNN);
  Real cBarK = record("C_barK", sN*cXiN);
  // Common derivative/transpose bound: 2n=4 dominates both d=2 and n=2
  // coefficients in Table 2. L=DK exactly in this specialization.
  Real cBarD = record("C_barDK_common", 4*sN*(sT+cMeanN+cR1));
  Real cBarE = record("C_barE", cE+gd*sN+(cDX*sN+cLieN)*cXiN);
  Real qBarN = record("Q_barEtaN", cBarD*cBarE+cRedNN*cXiN+
    delta*sL*cD2X*square(cBarK)/2);

  // Table 3: (3.60)--(3.73). The same bounds are used for L and L^T,
  // and for N and N^T, avoiding the untransposed quantities printed in (3.71).
  Real cXiLL = record("C_xiL_L", cR*(1+cT*sT));
  Real cXiLN = record("C_xiL_N", cR*cT*cXiNN);
  Real cXiL = record("C_xiL", cXiLL+cXiLN);
  Real cDeltaK = record("C_deltaK", sL*cXiL+gd*cBarK);
  Real cDeltaD = record("C_deltaDK_common", 4*sL*cXiL+gd*cBarD);
  Real cDeltaG = record("C_deltaG", 2*sL*cDeltaD);
  Real cDeltaB = record("C_deltaB", square(sB)*cDeltaG);
  Real cDeltaN = record("C_deltaN_common", cDeltaD*sB+sL*cDeltaB);
  Real cDeltaT = record("C_deltaT", 2*sN*cTh*cDeltaN+
    delta*square(sN)*cDTh*cDeltaK);
  Real cDeltaInvT = record("C_deltaInvT", square(sT)*cDeltaT);
  // (3.76)--(3.87).
  Real cLieXiL = record("C_LieXiL", 1+cT*cXiN);
  Real cNewE = record("C_newE", cBarE+sL*cLieXiL);
  Real qNewN = record("Q_etaN", 3*(1+cOmegaL*cLieXiL*chi)*qBarN);
  Real qL1 = record("Q_etaL1", cRedLN*cXiN+
    delta*sN*cD2X*square(cBarK)/2+gd*cOmegaN);
  Real qL2 = record("Q_etaL2", 2*sN*cBarE*cXiL);
  Real qL3 = record("Q_etaL3", sN*(2*sL*cXiL+gd*cBarD)*cLieXiL);
  record("Q_etaL4", 0); // No moment flow.
  Real qL5 = record("Q_etaL5", cDeltaN*cNewE);
  Real qNewL = record("Q_etaL", gd*qL1+qL2+qL3+qL5);

  // Table 4: delta=(rho-rho_infinity)/6 gives the exact ratio a=2.
  Real a = record("a", 2);
  Real qEta = record("Q_eta", maxUpper(qNewL, a*qNewN));
  Real cDist = record("C_dist", cDeltaK/bounds.get("domain_distance"));
  Real gapL = positiveGap("gap_DK", sL, bounds.get("b_DK"));
  Real gapLt = positiveGap("gap_DKt", sL, bounds.get("b_DKt"));
  Real gapB = positiveGap("gap_B", sB, bounds.get("b_B"));
  Real gapN = positiveGap("gap_N", sN, bounds.get("b_N"));
  Real gapNt = positiveGap("gap_Nt", sN, bounds.get("b_Nt"));
  Real gapT = positiveGap("gap_invT", sT, bounds.get("b_invT"));
  Real cDelta = record("C_Delta", maxUpper(maxUpper(cDeltaD/gapL, cDeltaD/gapLt),
    maxUpper(cDeltaB/gapB, maxUpper(maxUpper(cDeltaN/gapN, cDeltaN/gapNt), cDeltaInvT/gapT))));
  Real criterionSym = record("test_sym", gd*cSym*chi);
  Real criterionPhase = record("test_phase", cXiL*chi);
  Real criterionDomain = record("test_domain", (delta*cDist+a*qEta)*chi);
  Real criterionGeometry = record("test_geometry", (cDelta+square(a)*qEta)*chi);
  Real constant = record("theorem_C", maxUpper(maxUpper(gd*cSym, cXiL),
    maxUpper(delta*cDist+a*qEta, cDelta+square(a)*qEta)));
  Real condition = record("theorem_condition", constant*chi);
  Real kappa = record("kappa", square(a)*qEta*chi);
  if(!less(condition, 1) || !less(kappa, 1) || !less(criterionSym, 1) ||
     !less(criterionPhase, 1) || !less(criterionDomain, 1) || !less(criterionGeometry, 1))
  {
    reason = "Figueras--Haro smallness condition (2.24) failed";
    return false;
  }
  // (2.32)--(2.38): common transpose bounds yield conservative enclosures.
  record("distance_K", a/(a-kappa)*cDeltaK/gd*error);
  Real derivativeDistance = record("distance_DK", cDeltaD/(1-kappa)*chi);
  record("distance_DKt", derivativeDistance);
  record("distance_B", cDeltaB/(1-kappa)*chi);
  record("distance_N", cDeltaN/(1-kappa)*chi);
  record("distance_Nt", bounds.get("distance_N"));
  record("distance_invT", cDeltaInvT/(1-kappa)*chi);
  // Choose the real phase domain to be the real slice of U0 with I1>0.
  // Then dH/dI1=I1 is nonzero. The complex extension domains may contain
  // equilibria, but this additional reserve keeps all real iterates in U.
  Real regularAction = lower(bounds.get("regular_action_lower")-bounds.get("distance_K"));
  bounds.set("final_regular_action_lower", regularAction);
  if(!less(0, regularAction))
  {
    reason = "The total displacement exceeds the regular real-domain reserve";
    return false;
  }
  // Explicit global injectivity of the limiting primary torus, in addition
  // to the theorem's quantitative local geometry controls.
  Real finalAngular = record("final_angular_derivative_bound", bounds.get("b_Du")+
    derivativeDistance/(2*pi()));
  if(!less(finalAngular, 1))
  {
    reason = "Additional limiting-embedding injectivity test failed";
    return false;
  }
  reason = "All specialized theorem hypotheses and quantitative tests passed";
  return true;
}
}
