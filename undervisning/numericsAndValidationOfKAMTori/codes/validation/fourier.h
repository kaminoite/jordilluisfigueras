/** @file fourier.h
 * Local interval FFT and finite Fourier polynomials.
 * Copyright (c) 2026, Jordi-Lluís Figueras. BSD-2-Clause; see LICENSE.
 */
#ifndef KAM_VALIDATION_FOURIER_H
#define KAM_VALIDATION_FOURIER_H
#include "interval.h"
#include <array>
#include <vector>

namespace validation
{
using Spectrum = std::vector<Complex>;
using Grid = std::vector<Real>;
using Field = std::array<Spectrum, 4>;
using Samples = std::array<Grid, 4>;

int getMode(int index, int size);
bool isPowerOfTwo(int number);
void transform(Spectrum &data, int size, bool inverse);
Spectrum differentiate(const Spectrum &data, int size, int direction);
Spectrum resizeSpectrum(const Spectrum &data, int oldSize, int newSize);
Spectrum computeCoefficients(const Grid &values, int size);
Grid evaluate(const Spectrum &data, int size, int gridSize);
void freezeReal(Spectrum &data, int size);
Real computeNorm(const Spectrum &data, int size, const Real &rho);
Real computeGridError(int gridSize, const Real &rho, const Real &wideRho);
Real computeAverageError(int gridSize, const Real &wideRho);
Spectrum solveCohomology(const Grid &forcing, int gridSize, int retainedSize);

struct Candidate
{
  int size = 0;
  Field coefficients;
};
void validateCandidate(const Candidate &candidate);
Candidate loadCsv(const std::string &path, int retainedSize);
Candidate loadCandidate(const std::string &path);
void saveCandidate(const Candidate &candidate, const std::string &path);
std::string fingerprint(const Candidate &candidate);
Real refineCandidate(Candidate &candidate, const Real &epsilon, int steps, std::ostream &log);
}
#endif
