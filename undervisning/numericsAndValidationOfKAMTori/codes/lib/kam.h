/**
 * @file kam.h
 * @brief Shared Fourier/parameterization routines for the course's KAM codes.
 * Copyright (c) 2026, Jordi-Lluís Figueras.
 * See kam.cpp for the BSD redistribution conditions and disclaimer.
 */
#ifndef COURSE_KAM_H
#define COURSE_KAM_H

#include <array>
#include <cmath>
#include <complex>
#include <iosfwd>
#include <limits>
#include <string>
#include <vector>

namespace kam
{
constexpr double pi = 3.141592653589793238462643383279502884;
constexpr double machineEpsilon = std::numeric_limits<double>::epsilon();
using Complex = std::complex<double>;
using Grid = std::vector<double>;
using Spectrum = std::vector<Complex>;
using Vector2 = std::array<double, 2>;
using Vector4 = std::array<double, 4>;
using Matrix2 = std::array<Vector2, 2>;
using Matrix4 = std::array<Vector4, 4>;
using Field = std::array<Grid, 4>;
using Frame = std::array<std::array<Grid, 2>, 4>;
using Torsion = std::array<std::array<Grid, 2>, 2>;

struct Options
{
  int gridSize = 32;
  int maxSteps = 15;
  double epsilon = 0.01;
  double tolerance = 1.e-11;
  Vector2 omega = {1.0, (1.0+std::sqrt(5.0))/2.0};
  std::string outputPath = "torus.csv";
};

struct TorusData
{
  Frame tangent;
  Field residual;
  Grid energy;
  double residualNorm = 0.0;
};

struct StepData
{
  Field correction;
  double correctionNorm = 0.0;
  double normalAverage = 0.0;
  double torsionCondition = 0.0;
  double gramCondition = 0.0;
};

struct TorusMetrics
{
  double residualNorm = std::numeric_limits<double>::infinity();
  double energyOscillation = 0.0;
  double fourierTail = 0.0;
};

struct SolveResult
{
  bool converged = false;
  bool needsRefinement = false;
  int steps = 0;
  double workResidual = std::numeric_limits<double>::infinity();
  double normalAverage = 0.0;
  double torsionCondition = 1.0;
  double gramCondition = 1.0;
  TorusMetrics metrics;
  std::string reason;
};

Field createInitialTorus(int gridSize);
Field resampleField(const Field &values, int oldSize, int newSize);
Grid resampleGrid(const Grid &values, int oldSize, int newSize);
Spectrum computeCoefficients(const Grid &values, int gridSize);
Grid evaluateCoefficients(Spectrum coefficients, int gridSize);
Grid differentiate(const Grid &values, int gridSize, const Vector2 &direction);
Grid solveCohomology(const Grid &forcing, int gridSize, int retainedSize,
                    const Vector2 &omega);
double computeAverage(const Grid &values);
double computeMaxNorm(const Grid &values);
double computeFourierTail(const Field &periodicK, int gridSize);
Vector4 evaluateVectorField(const Vector4 &z, double epsilon);
double evaluateHamiltonian(const Vector4 &z, double epsilon);
TorusData computeTorusData(const Field &periodicK, int gridSize,
                         const Vector2 &omega, double epsilon);
StepData computeCorrection(const Field &periodicK, const Options &options);
TorusMetrics inspectTorus(const Field &periodicK, const Options &options);

/** Solve at fixed epsilon from the supplied initial guess. No files are written.
 * On failure, periodicK contains the last finite/best iterate, not a certified torus.
 * With damping, backtrack to reduce the work-grid residual at each correction.
 */
SolveResult solveTorus(Field &periodicK, const Options &options,
                      std::ostream *progress = nullptr, bool damping = false);

/** Exact phase translation of the Fourier approximation, making <u>=0. */
void normalizePhase(Field &periodicK, int gridSize);
void saveTorus(const Field &periodicK, const Options &options);
void runSelfTests();
double parseReal(const char *text);
int parseInteger(const char *text);
bool isValidGrid(int gridSize);
} // namespace kam

#endif
