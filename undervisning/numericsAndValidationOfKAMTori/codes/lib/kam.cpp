/*
 * kam.cpp
 *
 * Copyright (c) 2026, Jordi-Lluís Figueras
 *
 * Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:
 *
 * Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
 * Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
 *
 * THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
 */

/**
 * @file kam.cpp
 * @brief Shared double-precision parameterization method for a 2-DOF torus.
 *
 * H(phi,I) = |I|^2/2 + epsilon*(cos(phi1)+cos(phi2)+cos(phi1-phi2)).
 * K(theta) = (theta+u(theta), omega+v(theta)), with 2pi-periodic u,v.
 * Solve E = X_H(K)-DK*omega = 0 at a prescribed frequency omega.
 *
 * The geometric step follows TorKam's src_UTILS/KAMLagrangian.cpp:
 * compute_N_LAG, compute_invP_LAG, compute_torsion_LAG, compute_etaK,
 * solve_xi_of_K_LAG, and KAM_LAG_step (2026, same copyright/license above).
 * This is a self-contained educational reimplementation, with its own FFT,
 * fixed-size matrices, oversampling, convergence checks and CSV output.
 * Unlike that example's action-first ordering, we use the slides' (phi,I).
 * J = [0 Id; -Id 0], L_omega = -omega.dot(d_theta), eta = -P^{-1}E.
 * Numerical computation only: no interval arithmetic or existence proof.
 */

#include "kam.h"

#include <algorithm>
#include <array>
#include <cerrno>
#include <cmath>
#include <complex>
#include <cstdlib>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <limits>
#include <stdexcept>
#include <string>
#include <utility>
#include <vector>

namespace kam
{
int getMode(int index, int gridSize)
{
  return index < gridSize/2 ? index : index-gridSize;
}

double computeAverage(const Grid &values)
{
  long double sum = 0.0L;
  for(double value : values)
  {
    sum += value;
  }
  return static_cast<double>(sum/static_cast<long double>(values.size()));
}

double computeMaxNorm(const Grid &values)
{
  double norm = 0.0;
  for(double value : values)
  {
    if(!std::isfinite(value))
    {
      throw std::runtime_error("Non-finite grid value; iteration diverged.");
    }
    norm = std::max(norm, std::abs(value));
  }
  return norm;
}

/** Forward FFT is normalized; inverse evaluates sum_k c_k exp(i*k*theta). */
void transformLine(Spectrum &values, bool inverse)
{
  const int size = static_cast<int>(values.size());
  for(int i = 1, j = 0; i < size; ++i)
  {
    int bit = size/2;
    for(; j & bit; bit >>= 1)
    {
      j ^= bit;
    }
    j ^= bit;
    if(i < j)
    {
      std::swap(values[i], values[j]);
    }
  }
  for(int length = 2; length <= size; length *= 2)
  {
    const Complex root = std::polar(1.0, (inverse ? 2.0 : -2.0)*pi/length);
    for(int start = 0; start < size; start += length)
    {
      Complex factor = 1.0;
      for(int j = 0; j < length/2; ++j)
      {
        const Complex even = values[start+j];
        const Complex odd = factor*values[start+j+length/2];
        values[start+j] = even+odd;
        values[start+j+length/2] = even-odd;
        factor *= root;
      }
    }
  }
  if(!inverse)
  {
    for(Complex &value : values)
    {
      value /= size;
    }
  }
}

void transformGrid(Spectrum &values, int gridSize, bool inverse)
{
  Spectrum line(gridSize);
  for(int row = 0; row < gridSize; ++row)
  {
    for(int column = 0; column < gridSize; ++column)
    {
      line[column] = values[row*gridSize+column];
    }
    transformLine(line, inverse);
    for(int column = 0; column < gridSize; ++column)
    {
      values[row*gridSize+column] = line[column];
    }
  }
  for(int column = 0; column < gridSize; ++column)
  {
    for(int row = 0; row < gridSize; ++row)
    {
      line[row] = values[row*gridSize+column];
    }
    transformLine(line, inverse);
    for(int row = 0; row < gridSize; ++row)
    {
      values[row*gridSize+column] = line[row];
    }
  }
}

Spectrum computeCoefficients(const Grid &values, int gridSize)
{
  Spectrum coefficients(values.begin(), values.end());
  transformGrid(coefficients, gridSize, false);
  return coefficients;
}

Grid evaluateCoefficients(Spectrum coefficients, int gridSize)
{
  Grid values(coefficients.size());
  double imaginaryNorm = 0.0;
  transformGrid(coefficients, gridSize, true);
  for(std::size_t i = 0; i < values.size(); ++i)
  {
    values[i] = coefficients[i].real();
    imaginaryNorm = std::max(imaginaryNorm, std::abs(coefficients[i].imag()));
  }
  if(imaginaryNorm > 1.e-10*(1.0+computeMaxNorm(values)))
  {
    throw std::runtime_error("Fourier conjugate symmetry was lost.");
  }
  return values;
}

/** Transfer normalized coefficients; discard ambiguous Nyquist lines. */
Grid resampleGrid(const Grid &values, int oldSize, int newSize)
{
  const Spectrum oldCoefficients = computeCoefficients(values, oldSize);
  Spectrum newCoefficients(newSize*newSize, 0.0);
  const int cutoff = std::min(oldSize, newSize)/2;
  for(int i = 0; i < oldSize; ++i)
  {
    const int k1 = getMode(i, oldSize);
    for(int j = 0; j < oldSize; ++j)
    {
      const int k2 = getMode(j, oldSize);
      if(std::abs(k1) < cutoff && std::abs(k2) < cutoff)
      {
        newCoefficients[((k1+newSize)%newSize)*newSize+(k2+newSize)%newSize]
          = oldCoefficients[i*oldSize+j];
      }
    }
  }
  return evaluateCoefficients(std::move(newCoefficients), newSize);
}

Field resampleField(const Field &values, int oldSize, int newSize)
{
  Field result;
  for(int component = 0; component < 4; ++component)
  {
    result[component] = resampleGrid(values[component], oldSize, newSize);
  }
  return result;
}

/** Directional derivative of a real trigonometric interpolant. */
Grid differentiate(const Grid &values, int gridSize, const Vector2 &direction)
{
  Spectrum coefficients = computeCoefficients(values, gridSize);
  for(int i = 0; i < gridSize; ++i)
  {
    const int k1 = i == gridSize/2 ? 0 : getMode(i, gridSize);
    for(int j = 0; j < gridSize; ++j)
    {
      const int k2 = j == gridSize/2 ? 0 : getMode(j, gridSize);
      coefficients[i*gridSize+j] *= Complex(0.0, k1*direction[0]+k2*direction[1]);
    }
  }
  return evaluateCoefficients(std::move(coefficients), gridSize);
}

/** Solve L_omega f = g-<g>, with <f>=0, retaining |k_j| < retainedSize/2. */
Grid solveCohomology(const Grid &forcing, int gridSize, int retainedSize,
                    const Vector2 &omega)
{
  Spectrum coefficients = computeCoefficients(forcing, gridSize);
  for(int i = 0; i < gridSize; ++i)
  {
    const int k1 = getMode(i, gridSize);
    for(int j = 0; j < gridSize; ++j)
    {
      const int k2 = getMode(j, gridSize);
      Complex &coefficient = coefficients[i*gridSize+j];
      if((k1 == 0 && k2 == 0) || std::abs(k1) >= retainedSize/2 ||
         std::abs(k2) >= retainedSize/2)
      {
        coefficient = 0.0;
        continue;
      }
      const double divisor = k1*omega[0]+k2*omega[1];
      const double scale = std::abs(k1*omega[0])+std::abs(k2*omega[1]);
      if(std::abs(divisor) <= 64.0*machineEpsilon*scale)
      {
        throw std::runtime_error("Resonant or numerically unresolved Fourier divisor.");
      }
      coefficient /= Complex(0.0, -divisor);
    }
  }
  return evaluateCoefficients(std::move(coefficients), gridSize);
}

double computeMatrixNorm(const Matrix2 &matrix)
{
  return std::max(std::abs(matrix[0][0])+std::abs(matrix[0][1]),
                  std::abs(matrix[1][0])+std::abs(matrix[1][1]));
}

/** A scaled 2x2 inverse with an infinity-norm condition estimate. */
Matrix2 invertMatrix(const Matrix2 &matrix, double &condition)
{
  const double scale = computeMatrixNorm(matrix);
  if(!(scale > 0.0) || !std::isfinite(scale))
  {
    throw std::runtime_error("Singular or non-finite 2x2 matrix.");
  }
  Matrix2 scaled = matrix;
  for(auto &row : scaled)
  {
    for(double &value : row)
    {
      value /= scale;
    }
  }
  const double determinant = scaled[0][0]*scaled[1][1]-scaled[0][1]*scaled[1][0];
  if(!std::isfinite(determinant) || std::abs(determinant) < 128.0*machineEpsilon)
  {
    throw std::runtime_error("Singular or ill-conditioned Gram/average torsion matrix.");
  }
  Matrix2 inverse = {{{scaled[1][1], -scaled[0][1]},
                      {-scaled[1][0], scaled[0][0]}}};
  for(auto &row : inverse)
  {
    for(double &value : row)
    {
      value /= determinant*scale;
    }
  }
  condition = scale*computeMatrixNorm(inverse);
  if(!std::isfinite(condition) || condition > 1.e12)
  {
    throw std::runtime_error("Gram/average torsion condition number exceeds 1e12.");
  }
  return inverse;
}

double evaluateHamiltonian(const Vector4 &z, double epsilon)
{
  return 0.5*(z[2]*z[2]+z[3]*z[3])+
    epsilon*(std::cos(z[0])+std::cos(z[1])+std::cos(z[0]-z[1]));
}

Vector4 evaluateVectorField(const Vector4 &z, double epsilon)
{
  const double coupling = std::sin(z[0]-z[1]);
  return {z[2], z[3], epsilon*(std::sin(z[0])+coupling),
          epsilon*(std::sin(z[1])-coupling)};
}

Matrix4 evaluateJacobian(const Vector4 &z, double epsilon)
{
  Matrix4 jacobian = {};
  const double coupling = epsilon*std::cos(z[0]-z[1]);
  jacobian[0][2] = 1.0;
  jacobian[1][3] = 1.0;
  jacobian[2][0] = epsilon*std::cos(z[0])+coupling;
  jacobian[2][1] = -coupling;
  jacobian[3][0] = -coupling;
  jacobian[3][1] = epsilon*std::cos(z[1])+coupling;
  return jacobian;
}

Vector4 evaluateEmbedding(const Field &periodicK, int index, int gridSize,
                          const Vector2 &omega)
{
  return {2.0*pi*(index/gridSize)/gridSize+periodicK[0][index],
          2.0*pi*(index%gridSize)/gridSize+periodicK[1][index],
          omega[0]+periodicK[2][index], omega[1]+periodicK[3][index]};
}

/** Step 1: differentiate only (u,v); restore the identity in D(theta+u). */
TorusData computeTorusData(const Field &periodicK, int gridSize,
                         const Vector2 &omega, double epsilon)
{
  TorusData data;
  const int pointCount = gridSize*gridSize;
  data.energy.resize(pointCount);
  for(int row = 0; row < 4; ++row)
  {
    data.residual[row].resize(pointCount);
    for(int column = 0; column < 2; ++column)
    {
      Vector2 direction = {0.0, 0.0};
      direction[column] = 1.0;
      data.tangent[row][column] = differentiate(periodicK[row], gridSize, direction);
      if(row == column)
      {
        for(double &value : data.tangent[row][column])
        {
          value += 1.0;
        }
      }
    }
  }
  for(int index = 0; index < pointCount; ++index)
  {
    const Vector4 z = evaluateEmbedding(periodicK, index, gridSize, omega);
    const Vector4 vectorField = evaluateVectorField(z, epsilon);
    data.energy[index] = evaluateHamiltonian(z, epsilon);
    for(int row = 0; row < 4; ++row)
    {
      data.residual[row][index] = vectorField[row]-
        data.tangent[row][0][index]*omega[0]-data.tangent[row][1][index]*omega[1];
    }
  }
  for(const Grid &component : data.residual)
  {
    data.residualNorm = std::max(data.residualNorm, computeMaxNorm(component));
  }
  return data;
}

/** Step 2: P=(L,N) is stored in two blocks; N=-JL(L^T L)^{-1}. */
Frame buildNormalFrame(const Frame &tangent, int pointCount, double &maxCondition)
{
  Frame normal;
  for(auto &row : normal)
  {
    for(Grid &entry : row)
    {
      entry.resize(pointCount);
    }
  }
  for(int index = 0; index < pointCount; ++index)
  {
    Matrix2 gram = {};
    double condition = 0.0;
    for(int a = 0; a < 2; ++a)
    {
      for(int b = 0; b < 2; ++b)
      {
        for(int row = 0; row < 4; ++row)
        {
          gram[a][b] += tangent[row][a][index]*tangent[row][b][index];
        }
      }
    }
    const Matrix2 inverseGram = invertMatrix(gram, condition);
    maxCondition = std::max(maxCondition, condition);
    for(int row = 0; row < 2; ++row)
    {
      for(int a = 0; a < 2; ++a)
      {
        for(int b = 0; b < 2; ++b)
        {
          normal[row][a][index] -= tangent[row+2][b][index]*inverseGram[b][a];
          normal[row+2][a][index] += tangent[row][b][index]*inverseGram[b][a];
        }
      }
    }
  }
  return normal;
}

/** Steps 2--5, on a doubled grid to reduce aliasing in nonlinear products. */
StepData computeCorrection(const Field &periodicK, const Options &options)
{
  StepData step;
  const int workSize = 2*options.gridSize;
  const int pointCount = workSize*workSize;
  const Field workK = resampleField(periodicK, options.gridSize, workSize);
  const TorusData data = computeTorusData(workK, workSize, options.omega, options.epsilon);
  const Frame &tangent = data.tangent;
  const Frame normal = buildNormalFrame(tangent, pointCount, step.gramCondition);
  Frame lieNormal;
  Torsion torsion;
  Field eta;
  std::array<Grid, 2> xiNormal, xiTangent, tangentForcing;
  Matrix2 averageTorsion = {};
  Vector2 averageForcing = {}, normalConstant = {};
  const Vector2 negativeOmega = {-options.omega[0], -options.omega[1]};

  for(int row = 0; row < 4; ++row)
  {
    eta[row].resize(pointCount);
    for(int a = 0; a < 2; ++a)
    {
      lieNormal[row][a] = differentiate(normal[row][a], workSize, negativeOmega);
    }
  }
  for(auto &row : torsion)
  {
    for(Grid &entry : row)
    {
      entry.resize(pointCount);
    }
  }

  // Q=[-N^T J; L^T J], eta=-Q E, T=-N^T J (Lie_omega N+DX_H N).
  for(int index = 0; index < pointCount; ++index)
  {
    const Matrix4 jacobian = evaluateJacobian(
      evaluateEmbedding(workK, index, workSize, options.omega), options.epsilon);
    std::array<Vector2, 4> imageNormal = {};
    for(int row = 0; row < 4; ++row)
    {
      for(int a = 0; a < 2; ++a)
      {
        imageNormal[row][a] = lieNormal[row][a][index];
        for(int column = 0; column < 4; ++column)
        {
          imageNormal[row][a] += jacobian[row][column]*normal[column][a][index];
        }
      }
    }
    for(int a = 0; a < 2; ++a)
    {
      for(int row = 0; row < 2; ++row)
      {
        eta[a][index] += normal[row][a][index]*data.residual[row+2][index]-
          normal[row+2][a][index]*data.residual[row][index];
        eta[a+2][index] += tangent[row+2][a][index]*data.residual[row][index]-
          tangent[row][a][index]*data.residual[row+2][index];
        for(int b = 0; b < 2; ++b)
        {
          torsion[a][b][index] += normal[row+2][a][index]*imageNormal[row][b]-
            normal[row][a][index]*imageNormal[row+2][b];
        }
      }
    }
  }

  // Normal component: solve all retained nonzero modes, initially with zero mean.
  for(int a = 0; a < 2; ++a)
  {
    step.normalAverage = std::max(step.normalAverage, std::abs(computeAverage(eta[a+2])));
    xiNormal[a] = solveCohomology(eta[a+2], workSize, options.gridSize, options.omega);
    tangentForcing[a] = eta[a];
    for(int b = 0; b < 2; ++b)
    {
      averageTorsion[a][b] = computeAverage(torsion[a][b]);
    }
  }
  for(int a = 0; a < 2; ++a)
  {
    for(int index = 0; index < pointCount; ++index)
    {
      for(int b = 0; b < 2; ++b)
      {
        tangentForcing[a][index] -= torsion[a][b][index]*xiNormal[b][index];
      }
    }
    averageForcing[a] = computeAverage(tangentForcing[a]);
  }

  // <T> c = <eta^L-T*tilde(xi^N)> fixes the missing normal average.
  const Matrix2 inverseTorsion = invertMatrix(averageTorsion, step.torsionCondition);
  for(int a = 0; a < 2; ++a)
  {
    for(int b = 0; b < 2; ++b)
    {
      normalConstant[a] += inverseTorsion[a][b]*averageForcing[b];
    }
    for(double &value : xiNormal[a])
    {
      value += normalConstant[a];
    }
  }
  // Tangent component: subtract T*c and fix <xi^L>=0 (phase normalization).
  for(int a = 0; a < 2; ++a)
  {
    for(int index = 0; index < pointCount; ++index)
    {
      for(int b = 0; b < 2; ++b)
      {
        tangentForcing[a][index] -= torsion[a][b][index]*normalConstant[b];
      }
    }
    xiTangent[a] = solveCohomology(tangentForcing[a], workSize,
                                 options.gridSize, options.omega);
  }
  for(int row = 0; row < 4; ++row)
  {
    Grid correction(pointCount, 0.0);
    for(int index = 0; index < pointCount; ++index)
    {
      for(int a = 0; a < 2; ++a)
      {
        correction[index] += tangent[row][a][index]*xiTangent[a][index]+
          normal[row][a][index]*xiNormal[a][index];
      }
    }
    step.correction[row] = resampleGrid(correction, workSize, options.gridSize);
    step.correctionNorm = std::max(step.correctionNorm, computeMaxNorm(step.correction[row]));
  }
  return step;
}

/** Magnitude of the embedding's Fourier tail (outer quarter of each band). */
double computeFourierTail(const Field &periodicK, int gridSize)
{
  double tail = 0.0;
  for(const Grid &component : periodicK)
  {
    const Spectrum coefficients = computeCoefficients(component, gridSize);
    for(int i = 0; i < gridSize; ++i)
    {
      for(int j = 0; j < gridSize; ++j)
      {
        if(std::max(std::abs(getMode(i, gridSize)), std::abs(getMode(j, gridSize))) >= 3*gridSize/8)
        {
          tail = std::max(tail, std::abs(coefficients[i*gridSize+j]));
        }
      }
    }
  }
  return tail;
}

void saveTorus(const Field &periodicK, const Options &options)
{
  std::ofstream output(options.outputPath);
  const TorusData data = computeTorusData(periodicK, options.gridSize,
                                        options.omega, options.epsilon);
  if(!output)
  {
    throw std::runtime_error("Cannot open output file: "+options.outputPath);
  }
  output << std::setprecision(17)
    << "# epsilon=" << options.epsilon << ", omega1=" << options.omega[0]
    << ", omega2=" << options.omega[1] << '\n'
    << "theta1,theta2,phi1,phi2,I1,I2,u1,u2,v1,v2,E1,E2,E3,E4,H\n";
  for(int index = 0; index < options.gridSize*options.gridSize; ++index)
  {
    const Vector4 z = evaluateEmbedding(periodicK, index, options.gridSize, options.omega);
    output << 2.0*pi*(index/options.gridSize)/options.gridSize << ','
      << 2.0*pi*(index%options.gridSize)/options.gridSize;
    for(double value : z)
    {
      output << ',' << value;
    }
    for(const Grid &component : periodicK)
    {
      output << ',' << component[index];
    }
    for(const Grid &component : data.residual)
    {
      output << ',' << component[index];
    }
    output << ',' << data.energy[index] << '\n';
  }
  output.close();
  if(!output)
  {
    throw std::runtime_error("Failed to write output file: "+options.outputPath);
  }
}

double parseReal(const char *text)
{
  char *end = nullptr;
  errno = 0;
  const double value = std::strtod(text, &end);
  if(errno != 0 || end == text || *end != '\0' || !std::isfinite(value))
  {
    throw std::invalid_argument(std::string("Invalid finite number: ")+text);
  }
  return value;
}

int parseInteger(const char *text)
{
  const double value = parseReal(text);
  if(value < 0.0 || value > 100000.0 || std::floor(value) != value)
  {
    throw std::invalid_argument(std::string("Invalid integer: ")+text);
  }
  return static_cast<int>(value);
}

void requireClose(double error, double tolerance, const char *description)
{
  if(!std::isfinite(error) || error > tolerance)
  {
    throw std::runtime_error(std::string("Self-test failed: ")+description);
  }
}

/** Analytic tests, independent of the Newton iteration and its residual. */
void runSelfTests()
{
  const int size = 16;
  const Vector2 omega = {1.0, (1.0+std::sqrt(5.0))/2.0};
  Grid wave(size*size), forcing(size*size), left(size*size), right(size*size);
  for(int i = 0; i < size; ++i)
  {
    for(int j = 0; j < size; ++j)
    {
      const int index = i*size+j;
      const double theta1 = 2.0*pi*i/size;
      const double theta2 = 2.0*pi*j/size;
      wave[index] = std::sin(2.0*theta1-3.0*theta2);
      forcing[index] = -(2.0*omega[0]-3.0*omega[1])*std::cos(2.0*theta1-3.0*theta2);
      left[index] = std::cos(7.0*theta1);
      right[index] = std::cos(6.0*theta1);
    }
  }
  const Grid roundTrip = evaluateCoefficients(computeCoefficients(wave, size), size);
  const Grid derivative = differentiate(wave, size, {-omega[0], -omega[1]});
  const Grid solution = solveCohomology(forcing, size, size, omega);
  Grid product = resampleGrid(left, size, 2*size);
  const Grid paddedRight = resampleGrid(right, size, 2*size);
  for(std::size_t index = 0; index < product.size(); ++index)
  {
    product[index] *= paddedRight[index];
  }
  product = resampleGrid(product, 2*size, size);
  for(int index = 0; index < size*size; ++index)
  {
    requireClose(std::abs(roundTrip[index]-wave[index]), 2.e-13, "FFT round trip");
    requireClose(std::abs(derivative[index]-forcing[index]), 2.e-13, "spectral derivative");
    requireClose(std::abs(solution[index]-wave[index]), 2.e-13, "cohomology sign/normalization");
    requireClose(std::abs(product[index]-0.5*std::cos(2.0*pi*(index/size)/size)),
                 2.e-13, "padded product: discard mode 13, retain mode 1");
  }
  const Vector4 z = {0.31, -0.47, 1.2, 1.7};
  const Matrix4 jacobian = evaluateJacobian(z, 0.04);
  const Vector4 vectorField = evaluateVectorField(z, 0.04);
  for(int column = 0; column < 4; ++column)
  {
    Vector4 plus = z, minus = z;
    const double increment = 1.e-6;
    plus[column] += increment;
    minus[column] -= increment;
    const Vector4 plusField = evaluateVectorField(plus, 0.04);
    const Vector4 minusField = evaluateVectorField(minus, 0.04);
    const double gradient = (evaluateHamiltonian(plus, 0.04)-
                             evaluateHamiltonian(minus, 0.04))/(2.0*increment);
    const double expectedGradient = column < 2 ? -vectorField[column+2] : vectorField[column-2];
    requireClose(std::abs(gradient-expectedGradient), 1.e-9, "Hamiltonian vector field sign");
    for(int row = 0; row < 4; ++row)
    {
      requireClose(std::abs((plusField[row]-minusField[row])/(2.0*increment)-jacobian[row][column]),
                   1.e-9, "vector field Jacobian");
    }
  }
  Field shiftedTorus = createInitialTorus(size);
  for(int index = 0; index < size*size; ++index)
  {
    const double theta1 = 2.0*pi*(index/size)/size;
    const double theta2 = 2.0*pi*(index%size)/size;
    shiftedTorus[0][index] = 0.2+0.01*std::sin(theta1);
    shiftedTorus[1][index] = -0.3;
    shiftedTorus[2][index] = 0.02*std::cos(theta1+theta2);
  }
  normalizePhase(shiftedTorus, size);
  for(int index = 0; index < size*size; ++index)
  {
    const double theta1 = 2.0*pi*(index/size)/size;
    const double theta2 = 2.0*pi*(index%size)/size;
    requireClose(std::abs(shiftedTorus[0][index]-0.01*std::sin(theta1-0.2)),
                 2.e-14, "phase translation of the angular lift");
    requireClose(std::abs(shiftedTorus[2][index]-0.02*std::cos(theta1+theta2+0.1)),
                 2.e-14, "phase translation of the action component");
  }
  requireClose(std::abs(computeAverage(shiftedTorus[0])), 2.e-14, "zero angular mean");
  requireClose(std::abs(computeAverage(shiftedTorus[1])), 2.e-14, "zero second angular mean");
  std::cout << "Self-tests passed: FFT, spectral derivative, cohomology, padded product, H, DX_H and phase translation.\n";
}

bool isValidGrid(int gridSize)
{
  return gridSize >= 8 && gridSize <= 512 && (gridSize & (gridSize-1)) == 0;
}

Field createInitialTorus(int gridSize)
{
  Field periodicK;
  if(!isValidGrid(gridSize))
  {
    throw std::invalid_argument("Grid must be a power of two in [8,512].");
  }
  for(Grid &component : periodicK)
  {
    component.assign(gridSize*gridSize, 0.0);
  }
  return periodicK;
}

TorusMetrics inspectTorus(const Field &periodicK, const Options &options)
{
  TorusMetrics metrics;
  const int checkSize = 4*options.gridSize;
  const Field checkK = resampleField(periodicK, options.gridSize, checkSize);
  const TorusData check = computeTorusData(checkK, checkSize, options.omega, options.epsilon);
  const auto energyRange = std::minmax_element(check.energy.begin(), check.energy.end());
  metrics.residualNorm = check.residualNorm;
  metrics.energyOscillation = *energyRange.second-*energyRange.first;
  metrics.fourierTail = computeFourierTail(periodicK, options.gridSize);
  return metrics;
}

void normalizePhase(Field &periodicK, int gridSize)
{
  const Vector2 shift = {-computeAverage(periodicK[0]), -computeAverage(periodicK[1])};
  for(int row = 0; row < 4; ++row)
  {
    Spectrum coefficients = computeCoefficients(periodicK[row], gridSize);
    for(int i = 0; i < gridSize; ++i)
    {
      for(int j = 0; j < gridSize; ++j)
      {
        if(i == gridSize/2 || j == gridSize/2)
        {
          coefficients[i*gridSize+j] = 0.0;
        }
        else
        {
          coefficients[i*gridSize+j] *= std::polar(1.0,
            getMode(i, gridSize)*shift[0]+getMode(j, gridSize)*shift[1]);
        }
      }
    }
    if(row < 2)
    {
      coefficients[0] += shift[row];
    }
    periodicK[row] = evaluateCoefficients(std::move(coefficients), gridSize);
  }
}

SolveResult solveTorus(Field &periodicK, const Options &options,
                      std::ostream *progress, bool damping)
{
  std::cout << progress << std::endl;
  SolveResult result;
  int slowSteps = 0;
  if(!isValidGrid(options.gridSize) || options.maxSteps < 1 ||
     !std::isfinite(options.tolerance) || options.tolerance <= 0.0 ||
     !std::isfinite(options.epsilon) || !std::isfinite(options.omega[0]) ||
     !std::isfinite(options.omega[1]))
  {
    throw std::invalid_argument("Invalid solver options.");
  }
  for(const Grid &component : periodicK)
  {
    if(component.size() != static_cast<std::size_t>(options.gridSize*options.gridSize))
    {
      throw std::invalid_argument("Initial embedding has the wrong grid size.");
    }
    computeMaxNorm(component);
  }
  // Check divisors even if the initial integrable torus has zero residual.
  solveCohomology(periodicK[0], options.gridSize, options.gridSize, options.omega);
  for(int iteration = 0; iteration <= options.maxSteps; ++iteration)
  {
    const Field workK = resampleField(periodicK, options.gridSize, 2*options.gridSize);
    const TorusData data = computeTorusData(workK, 2*options.gridSize,
                                          options.omega, options.epsilon);
    result.steps = iteration;
    result.workResidual = data.residualNorm;
    if(progress != nullptr)
    {
      *progress << std::setw(4) << iteration << "   " << std::setw(14) << data.residualNorm;
    }
    if(data.residualNorm <= options.tolerance)
    {
      result.metrics = inspectTorus(periodicK, options);
      if(progress != nullptr)
      {
        *progress << "\nFine-grid residual = " << result.metrics.residualNorm
          << "\nEnergy oscillation = " << result.metrics.energyOscillation
          << "\nFourier tail       = " << result.metrics.fourierTail << '\n';
      }
      result.converged = result.metrics.residualNorm <= options.tolerance;
      result.needsRefinement = !result.converged;
      result.reason = result.converged ? "converged" : "fine-grid residual exceeds tolerance";
      return result;
    }
    if(iteration == options.maxSteps)
    {
      if(progress != nullptr)
      {
        *progress << '\n';
      }
      result.reason = "maximum Newton steps reached";
      break;
    }
    const StepData step = computeCorrection(periodicK, options);
    result.normalAverage = std::max(result.normalAverage, step.normalAverage);
    result.torsionCondition = std::max(result.torsionCondition, step.torsionCondition);
    result.gramCondition = std::max(result.gramCondition, step.gramCondition);
    if(progress != nullptr)
    {
      *progress << "   " << step.correctionNorm << "   " << step.normalAverage
        << "   " << step.torsionCondition << "   " << step.gramCondition << '\n';
    }
    if((!damping && step.correctionNorm > 1.0) || data.residualNorm > 10.0)
    {
      result.reason = "correction left the local convergence regime";
      break;
    }
    bool accepted = false;
    double factor = 1.0;
    for(int backtrack = 0; backtrack < (damping ? 8 : 1); ++backtrack)
    {
      Field candidate = periodicK;
      for(int row = 0; row < 4; ++row)
      {
        for(std::size_t index = 0; index < periodicK[row].size(); ++index)
        {
          candidate[row][index] += factor*step.correction[row][index];
        }
      }
      double newResidual = 0.0;
      if(damping)
      {
        const Field candidateWork = resampleField(candidate, options.gridSize, 2*options.gridSize);
        newResidual = computeTorusData(candidateWork, 2*options.gridSize,
                                      options.omega, options.epsilon).residualNorm;
      }
      if(!damping || newResidual < data.residualNorm*(1.0-1.e-4*factor))
      {
        periodicK = std::move(candidate);
        result.steps = iteration+1;
        if(damping)
        {
          result.workResidual = newResidual;
        }
        slowSteps = newResidual > 0.8*data.residualNorm ? slowSteps+1 : 0;
        accepted = true;
        break;
      }
      factor *= 0.5;
    }
    if(!accepted || slowSteps >= 3)
    {
      result.reason = !accepted ? "Newton backtracking stalled" : "Newton residual stagnated";
      break;
    }
  }
  result.metrics.fourierTail = computeFourierTail(periodicK, options.gridSize);
  result.needsRefinement = result.metrics.fourierTail*options.gridSize*
    (1.0+std::abs(options.omega[0])+std::abs(options.omega[1])) > options.tolerance;
  return result;
}
} // namespace kam
