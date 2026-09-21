/** @file kamBounds.cpp
 * Standard coordinates (phi1,phi2,I1,I2), angles in radians.
 * Copyright (c) 2026, Jordi-Lluís Figueras. BSD-2-Clause; see LICENSE.
 */
#include "kamBounds.h"

namespace validation
{
void Bounds::set(const std::string &name, const Real &value)
{
  requireFinite(value);
  values[name] = value;
}
const Real &Bounds::get(const std::string &name) const
{
  return values.at(name);
}
Matrix2 invertMatrix(const Matrix2 &matrix)
{
  Real determinant = matrix[0][0]*matrix[1][1]-matrix[0][1]*matrix[1][0];
  if(containsZero(determinant))
  {
    throw NotCertified("A 2x2 determinant enclosure contains zero");
  }
  return {{{matrix[1][1]/determinant, -matrix[0][1]/determinant},
           {-matrix[1][0]/determinant, matrix[0][0]/determinant}}};
}
Real computeMatrixNorm(const Matrix2 &matrix)
{
  return maxUpper(magnitude(matrix[0][0])+magnitude(matrix[0][1]),
                  magnitude(matrix[1][0])+magnitude(matrix[1][1]));
}

struct SampleData
{
  Samples residual;
  std::array<std::array<Grid, 2>, 4> tangent, normal;
  std::array<std::array<Grid, 2>, 2> torsion;
  Matrix2 averageTorsion = {};
};

/**
 * Eq. (2.9) torsion, NOT the derivative-based off-torus numerical formula.
 * Omega=J_paper=[0,-Id;Id,0]. If F_phi=epsilon*C, then
 * T_h=Omega*A-A*Omega=diag(-(Id+epsilon*C),Id+epsilon*C).
 */
static SampleData sampleGeometry(const Candidate &candidate, const Real &epsilon,
                                int gridSize, const Real &scale, bool keepFrames)
{
  int count = gridSize*gridSize;
  Real circle = 2*pi();
  Real golden = (1+sqrt(Real(5)))/2;
  Samples values;
  std::array<std::array<Grid, 2>, 4> derivatives;
  SampleData result;
  for(int row = 0; row < 4; ++row)
  {
    values[row] = evaluate(candidate.coefficients[row], candidate.size, gridSize);
    result.residual[row].resize(count);
    for(int direction = 0; direction < 2; ++direction)
    {
      derivatives[row][direction] = evaluate(differentiate(candidate.coefficients[row],
        candidate.size, direction), candidate.size, gridSize);
      if(keepFrames)
      {
        result.tangent[row][direction].resize(count);
        result.normal[row][direction].resize(count);
      }
    }
  }
  if(keepFrames)
  {
    for(auto &row : result.torsion)
    {
      for(Grid &entry : row)
      {
        entry.resize(count);
      }
    }
  }
  for(int i = 0; i < gridSize; ++i)
  {
    for(int j = 0; j < gridSize; ++j)
    {
      int index = i*gridSize+j;
      Real phi1 = circle*i/gridSize+values[0][index];
      Real phi2 = circle*j/gridSize+values[1][index];
      Real mixedSin = sin(phi1-phi2), mixedCos = cos(phi1-phi2);
      // Cancel the identical exact golden action offset symbolically.
      result.residual[0][index] = values[2][index]-derivatives[0][0][index]-golden*derivatives[0][1][index];
      result.residual[1][index] = values[3][index]-derivatives[1][0][index]-golden*derivatives[1][1][index];
      result.residual[2][index] = epsilon*(sin(phi1)+mixedSin)-derivatives[2][0][index]-golden*derivatives[2][1][index];
      result.residual[3][index] = epsilon*(sin(phi2)-mixedSin)-derivatives[3][0][index]-golden*derivatives[3][1][index];
      std::array<std::array<Real, 2>, 4> tangent = {}, normal = {};
      Matrix2 gram = {}, torsion = {};
      Matrix2 diagonal = {{{1+epsilon*(cos(phi1)+mixedCos), -epsilon*mixedCos},
                           {-epsilon*mixedCos, 1+epsilon*(cos(phi2)+mixedCos)}}};
      for(int row = 0; row < 4; ++row)
      {
        for(int a = 0; a < 2; ++a)
        {
          tangent[row][a] = scale*(derivatives[row][a][index]+Real(row == a ? 1 : 0));
        }
      }
      for(int a = 0; a < 2; ++a)
      {
        for(int b = 0; b < 2; ++b)
        {
          for(int row = 0; row < 4; ++row)
          {
            gram[a][b] += tangent[row][a]*tangent[row][b];
          }
        }
      }
      Matrix2 inverseGram = invertMatrix(gram);
      for(int row = 0; row < 2; ++row)
      {
        for(int a = 0; a < 2; ++a)
        {
          for(int b = 0; b < 2; ++b)
          {
            normal[row][a] -= tangent[row+2][b]*inverseGram[b][a];
            normal[row+2][a] += tangent[row][b]*inverseGram[b][a];
          }
        }
      }
      for(int a = 0; a < 2; ++a)
      {
        for(int b = 0; b < 2; ++b)
        {
          for(int row = 0; row < 2; ++row)
          {
            for(int column = 0; column < 2; ++column)
            {
              torsion[a][b] += normal[row+2][a]*diagonal[row][column]*normal[column+2][b]-
                normal[row][a]*diagonal[row][column]*normal[column][b];
            }
          }
          result.averageTorsion[a][b] += torsion[a][b]/count;
          if(keepFrames)
          {
            result.torsion[a][b][index] = torsion[a][b];
          }
        }
      }
      if(keepFrames)
      {
        for(int row = 0; row < 4; ++row)
        {
          for(int a = 0; a < 2; ++a)
          {
            result.tangent[row][a][index] = tangent[row][a];
            result.normal[row][a][index] = normal[row][a];
          }
        }
      }
    }
  }
  return result;
}

Real refineCandidate(Candidate &candidate, const Real &epsilon, int steps, std::ostream &log)
{
  validateCandidate(candidate);
  Real lastError;
  int size = candidate.size, workSize = 2*size, count = workSize*workSize;
  if(!isPowerOfTwo(workSize))
  {
    throw std::invalid_argument("Refinement grid exceeds FFT capacity");
  }
  for(int step = 0; step < steps; ++step)
  {
    SampleData data = sampleGeometry(candidate, epsilon, workSize, Real(1), true);
    Samples eta, xi;
    lastError = 0;
    for(int row = 0; row < 4; ++row)
    {
      eta[row].resize(count);
      for(const Real &value : data.residual[row])
      {
        lastError = maxUpper(lastError, magnitude(value));
      }
    }
    log << "Refinement " << step << ": sampled defect <= " << approximate(lastError) << '\n';
    for(int index = 0; index < count; ++index)
    {
      for(int a = 0; a < 2; ++a)
      {
        for(int row = 0; row < 2; ++row)
        {
          eta[a][index] += data.normal[row][a][index]*data.residual[row+2][index]-
            data.normal[row+2][a][index]*data.residual[row][index];
          eta[a+2][index] += data.tangent[row+2][a][index]*data.residual[row][index]-
            data.tangent[row][a][index]*data.residual[row+2][index];
        }
      }
    }
    for(int a = 0; a < 2; ++a)
    {
      xi[a+2] = evaluate(solveCohomology(eta[a+2], workSize, size), size, workSize);
    }
    std::array<Real, 2> averageForcing = {}, normalConstant = {};
    Samples forcing;
    for(int a = 0; a < 2; ++a)
    {
      forcing[a] = eta[a];
      for(int index = 0; index < count; ++index)
      {
        for(int b = 0; b < 2; ++b)
        {
          forcing[a][index] -= data.torsion[a][b][index]*xi[b+2][index];
        }
        averageForcing[a] += forcing[a][index]/count;
      }
    }
    Matrix2 inverseTorsion = invertMatrix(data.averageTorsion);
    for(int a = 0; a < 2; ++a)
    {
      for(int b = 0; b < 2; ++b)
      {
        normalConstant[a] += inverseTorsion[a][b]*averageForcing[b];
      }
    }
    for(int a = 0; a < 2; ++a)
    {
      for(int index = 0; index < count; ++index)
      {
        xi[a+2][index] += normalConstant[a];
        for(int b = 0; b < 2; ++b)
        {
          forcing[a][index] -= data.torsion[a][b][index]*normalConstant[b];
        }
      }
      xi[a] = evaluate(solveCohomology(forcing[a], workSize, size), size, workSize);
    }
    for(int row = 0; row < 4; ++row)
    {
      Grid delta(count);
      for(int index = 0; index < count; ++index)
      {
        for(int a = 0; a < 2; ++a)
        {
          delta[index] += data.tangent[row][a][index]*xi[a][index]+
            data.normal[row][a][index]*xi[a+2][index];
        }
      }
      Spectrum correction = resizeSpectrum(computeCoefficients(delta, workSize), workSize, size);
      for(int index = 0; index < size*size; ++index)
      {
        candidate.coefficients[row][index] = candidate.coefficients[row][index]+correction[index];
      }
      freezeReal(candidate.coefficients[row], size);
    }
  }
  return lastError;
}

struct StripBounds
{
  std::array<Real, 4> component;
  std::array<std::array<Real, 2>, 4> derivative;
  Real du, duTranspose, dv, dvTranspose, tangent, tangentTranspose;
  Real gramDefect, inverseGram, normal, normalTranspose;
};
static StripBounds boundStrip(const Candidate &candidate, const Real &rho)
{
  StripBounds result;
  Real circle = 2*pi();
  for(int row = 0; row < 4; ++row)
  {
    result.component[row] = computeNorm(candidate.coefficients[row], candidate.size, rho);
    for(int a = 0; a < 2; ++a)
    {
      result.derivative[row][a] = computeNorm(differentiate(candidate.coefficients[row],
        candidate.size, a), candidate.size, rho);
    }
  }
  for(int a = 0; a < 2; ++a)
  {
    result.du = maxUpper(result.du, result.derivative[a][0]+result.derivative[a][1]);
    result.dv = maxUpper(result.dv, result.derivative[a+2][0]+result.derivative[a+2][1]);
    result.duTranspose = maxUpper(result.duTranspose, result.derivative[0][a]+result.derivative[1][a]);
    result.dvTranspose = maxUpper(result.dvTranspose, result.derivative[2][a]+result.derivative[3][a]);
    result.tangentTranspose = maxUpper(result.tangentTranspose, circle*(1+
      result.derivative[0][a]+result.derivative[1][a]+result.derivative[2][a]+result.derivative[3][a]));
  }
  result.tangent = upper(circle*maxUpper(1+result.du, result.dv));
  result.gramDefect = upper(result.du+result.duTranspose+
    result.duTranspose*result.du+result.dvTranspose*result.dv);
  if(!less(result.gramDefect, 1))
  {
    throw NotCertified("Strip-wide Gram inverse at radius " + printInterval(rho) +
      ": normalized Neumann defect " + printInterval(result.gramDefect) + " is not below one");
  }
  result.inverseGram = upper(Real(1)/(square(circle)*(1-result.gramDefect)));
  result.normal = upper(result.tangent*result.inverseGram);
  result.normalTranspose = upper(result.inverseGram*result.tangentTranspose);
  return result;
}

Bounds computeBounds(const Candidate &candidate, const Parameters &parameters, std::ostream &log)
{
  validateCandidate(candidate);
  if(!less(0, parameters.finalRho) || !less(parameters.finalRho, parameters.rho) ||
     !less(parameters.rho, parameters.wideRho) || !less(0, parameters.domainMargin) ||
     !less(1, parameters.sigmaFactor) || !isPowerOfTwo(parameters.gridSize) ||
     parameters.gridSize < 2*candidate.size)
  {
    throw std::invalid_argument("Invalid strips, domain margin, sigma factor, or validation grid");
  }
  Bounds result;
  Real circle = 2*pi(), golden = (1+sqrt(Real(5)))/2;
  Real absEpsilon = magnitude(parameters.epsilon);
  StripBounds base = boundStrip(candidate, parameters.rho);
  StripBounds wide = boundStrip(candidate, parameters.wideRho);
  if(!less(base.du, 1))
  {
    throw NotCertified("Angular projection is not certified injective");
  }
  result.set("b_Du", base.du);
  Real regularAction = lower(1-base.component[2]);
  if(!less(0, regularAction))
  {
    throw NotCertified("The regular real phase domain I1>0 is not certified");
  }
  result.set("regular_action_lower", regularAction);
  result.set("b_DK", base.tangent);
  result.set("b_DKt", base.tangentTranspose);
  result.set("b_B", base.inverseGram);
  result.set("b_N", base.normal);
  result.set("b_Nt", base.normalTranspose);
  result.set("gram_defect_rho", base.gramDefect);
  result.set("gram_defect_wide", wide.gramDefect);
  result.set("domain_distance", lower(parameters.domainMargin));
  result.set("rho_radian", parameters.rho);
  result.set("rho_final_radian", parameters.finalRho);
  result.set("rho_wide_radian", parameters.wideRho);
  result.set("rho", parameters.rho/circle);
  result.set("rho_final", parameters.finalRho/circle);
  result.set("delta", (parameters.rho-parameters.finalRho)/(6*circle));
  result.set("gamma", Real(1)/circle);
  result.set("tau", 1);

  // U0 is a complex product domain; U is larger by another domainMargin.
  std::array<Real, 4> domain0, domain;
  for(int row = 0; row < 4; ++row)
  {
    Real offset = row < 2 ? parameters.rho : (row == 2 ? Real(1) : magnitude(golden));
    domain0[row] = upper(offset+base.component[row]+parameters.domainMargin);
    domain[row] = upper(domain0[row]+parameters.domainMargin);
    result.set("U0_radius_"+std::to_string(row), domain0[row]);
    result.set("U_radius_"+std::to_string(row), domain[row]);
  }
  Real single = maxUpper(cosh(domain[0]), cosh(domain[1]));
  Real mixed = cosh(domain[0]+domain[1]);
  Real forceDerivative = upper(absEpsilon*(single+2*mixed));
  result.set("c_X", maxUpper(maxUpper(domain[2], domain[3]), absEpsilon*(single+mixed)));
  result.set("c_DX", maxUpper(1, forceDerivative));
  result.set("c_DXt", result.get("c_DX"));
  result.set("c_D2X", upper(absEpsilon*(single+4*mixed)));
  result.set("c_Th", upper(1+forceDerivative));
  result.set("c_DTh", result.get("c_D2X"));

  Real widePhi1 = parameters.wideRho+wide.component[0];
  Real widePhi2 = parameters.wideRho+wide.component[1];
  Real wideSingle = maxUpper(cosh(widePhi1), cosh(widePhi2));
  Real wideMixed = cosh(widePhi1+widePhi2);
  Real residualWide;
  for(int a = 0; a < 2; ++a)
  {
    residualWide = maxUpper(residualWide, wide.component[a+2]+
      wide.derivative[a][0]+magnitude(golden)*wide.derivative[a][1]);
    residualWide = maxUpper(residualWide, absEpsilon*(wideSingle+wideMixed)+
      wide.derivative[a+2][0]+magnitude(golden)*wide.derivative[a+2][1]);
  }
  Real torsionWide = upper(wide.normalTranspose*
    (1+absEpsilon*(wideSingle+2*wideMixed))*wide.normal);
  Real interpolation = computeGridError(parameters.gridSize, parameters.rho, parameters.wideRho);
  result.set("M_E_wide", residualWide);
  result.set("M_T_wide", torsionWide);
  result.set("C_grid", interpolation);
  result.set("residual_interpolation_error", upper(interpolation*residualWide));
  log << "Computing interval residual and torsion on " << parameters.gridSize << "^2 points\n";
  SampleData data = sampleGeometry(candidate, parameters.epsilon, parameters.gridSize, circle, false);
  Real finiteResidual;
  for(int row = 0; row < 4; ++row)
  {
    Real bound = computeNorm(computeCoefficients(data.residual[row], parameters.gridSize),
                            parameters.gridSize, parameters.rho);
    finiteResidual = maxUpper(finiteResidual, bound);
  }
  result.set("residual_finite_part", finiteResidual);
  result.set("b_E", upper(finiteResidual+result.get("residual_interpolation_error")));
  result.set("b_etaL", upper(base.normalTranspose*result.get("b_E")));
  result.set("b_etaN", upper(base.tangentTranspose*result.get("b_E")));
  Real meanError = upper(computeAverageError(parameters.gridSize, parameters.wideRho)*torsionWide);
  result.set("torsion_average_alias_error_per_entry", meanError);
  for(int a = 0; a < 2; ++a)
  {
    for(int b = 0; b < 2; ++b)
    {
      data.averageTorsion[a][b] = inflate(data.averageTorsion[a][b], meanError);
      result.set("average_T_"+std::to_string(a)+std::to_string(b), data.averageTorsion[a][b]);
    }
  }
  result.set("b_invT", computeMatrixNorm(invertMatrix(data.averageTorsion)));
  // Shared transpose budgets deliberately dominate both row- and column-sum norms.
  result.set("sigma_L", upper(parameters.sigmaFactor*maxUpper(base.tangent, base.tangentTranspose)));
  result.set("sigma_B", upper(parameters.sigmaFactor*base.inverseGram));
  result.set("sigma_N", upper(parameters.sigmaFactor*maxUpper(base.normal, base.normalTranspose)));
  result.set("sigma_invT", upper(parameters.sigmaFactor*result.get("b_invT")));
  return result;
}
}
