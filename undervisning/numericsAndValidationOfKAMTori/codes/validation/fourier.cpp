/** @file fourier.cpp
 * Independently implemented radix-2 FFT; no Numerical Recipes or TorKam code.
 * Copyright (c) 2026, Jordi-Lluís Figueras. BSD-2-Clause; see LICENSE.
 */
#include "fourier.h"
#include <cstdint>
#include <fstream>
#include <iomanip>
#include <sstream>

namespace validation
{
int getMode(int index, int size)
{
  return index < size/2 ? index : index-size;
}
bool isPowerOfTwo(int number)
{
  return number >= 4 && number <= 2048 && (number & (number-1)) == 0;
}

void transform(Spectrum &data, int size, bool inverse)
{
  if(!isPowerOfTwo(size) || data.size() != static_cast<size_t>(size)*size)
  {
    throw std::invalid_argument("Invalid FFT dimensions");
  }
  std::vector<Complex> roots(size/2);
  Real circle = 2*pi();
  for(int k = 0; k < size/2; ++k)
  {
    Real angle = circle*k/size;
    roots[k] = {cos(angle), inverse ? sin(angle) : -sin(angle)};
  }
  auto transformLine = [&](int base, int stride)
  {
    for(int i = 1, j = 0; i < size; ++i)
    {
      int bit = size/2;
      for(; j & bit; bit /= 2)
      {
        j ^= bit;
      }
      j ^= bit;
      if(i < j)
      {
        std::swap(data[base+i*stride], data[base+j*stride]);
      }
    }
    for(int length = 2; length <= size; length *= 2)
    {
      for(int start = 0; start < size; start += length)
      {
        for(int k = 0; k < length/2; ++k)
        {
          int a = base+(start+k)*stride;
          int b = base+(start+k+length/2)*stride;
          Complex left = data[a];
          Complex right = data[b]*roots[k*(size/length)];
          data[a] = left+right;
          data[b] = left-right;
        }
      }
    }
  };
  for(int i = 0; i < size; ++i)
  {
    transformLine(i*size, 1);
  }
  for(int i = 0; i < size; ++i)
  {
    transformLine(i, size);
  }
  if(!inverse)
  {
    Real scale = Real(1)/(static_cast<long>(size)*size);
    for(Complex &number : data)
    {
      number = number*scale;
    }
  }
}

Spectrum differentiate(const Spectrum &data, int size, int direction)
{
  Spectrum result(data.size());
  for(int i = 0; i < size; ++i)
  {
    for(int j = 0; j < size; ++j)
    {
      long mode = getMode(direction == 0 ? i : j, size);
      int index = i*size+j;
      result[index] = {-data[index].im*mode, data[index].re*mode};
    }
  }
  return result;
}

Spectrum resizeSpectrum(const Spectrum &data, int oldSize, int newSize)
{
  Spectrum result(static_cast<size_t>(newSize)*newSize);
  for(int i = 0; i < oldSize; ++i)
  {
    for(int j = 0; j < oldSize; ++j)
    {
      int a = getMode(i, oldSize), b = getMode(j, oldSize);
      if(std::abs(a) < std::min(oldSize, newSize)/2 &&
         std::abs(b) < std::min(oldSize, newSize)/2)
      {
        result[((a+newSize)%newSize)*newSize+(b+newSize)%newSize] = data[i*oldSize+j];
      }
    }
  }
  return result;
}
Spectrum computeCoefficients(const Grid &values, int size)
{
  Spectrum result(values.size());
  for(size_t index = 0; index < values.size(); ++index)
  {
    result[index].re = values[index];
  }
  transform(result, size, false);
  return result;
}
Grid evaluate(const Spectrum &data, int size, int gridSize)
{
  if(gridSize < size)
  {
    throw std::invalid_argument("Evaluation grid must contain the polynomial support");
  }
  Spectrum work = resizeSpectrum(data, size, gridSize);
  transform(work, gridSize, true);
  Grid result(work.size());
  for(size_t index = 0; index < work.size(); ++index)
  {
    if(!containsZero(work[index].im))
    {
      throw std::invalid_argument("Polynomial is not real on the real torus");
    }
    result[index] = work[index].re;
  }
  return result;
}
/** Choose a NEW exact polynomial, not an enclosure of an unknown torus. */
void freezeReal(Spectrum &data, int size)
{
  for(int i = 0; i < size; ++i)
  {
    for(int j = 0; j < size; ++j)
    {
      int index = i*size+j;
      int opposite = ((size-i)%size)*size+(size-j)%size;
      if(i == size/2 || j == size/2)
      {
        data[index] = {};
      }
      else if(index <= opposite)
      {
        Complex center = (data[index]+conjugate(data[opposite]))*Real("1/2");
        data[index] = {midpoint(center.re), index == opposite ? Real() : midpoint(center.im)};
        data[opposite] = conjugate(data[index]);
      }
    }
  }
}
Real computeNorm(const Spectrum &data, int size, const Real &rho)
{
  std::vector<Real> weights(size+1);
  for(int k = 0; k <= size; ++k)
  {
    weights[k] = exp(rho*k);
  }
  Real result;
  for(int i = 0; i < size; ++i)
  {
    for(int j = 0; j < size; ++j)
    {
      result += magnitude(data[i*size+j])*weights[std::abs(getMode(i, size))+std::abs(getMode(j, size))];
    }
  }
  return upper(result);
}
/**
 * Two-dimensional DFT interpolation error: 2 times a union bound on the
 * exponentially decaying outside coefficients. Includes Nyquist and aliasing.
 * See README for the derivation from the alias identity in FHL, Section 3.
 */
Real computeGridError(int gridSize, const Real &rho, const Real &wideRho)
{
  if(!less(rho, wideRho))
  {
    throw std::invalid_argument("The wider strip must be strictly wider");
  }
  Real gap = wideRho-rho;
  Real q = exp(-gap);
  return upper(8*exp(-gap*(gridSize/2))*(1+q)/square(1-q));
}
Real computeAverageError(int gridSize, const Real &wideRho)
{
  Real q = exp(-wideRho*gridSize);
  return upper(4*q/square(1-q));
}

Spectrum solveCohomology(const Grid &forcing, int gridSize, int retainedSize)
{
  Spectrum result = resizeSpectrum(computeCoefficients(forcing, gridSize), gridSize, retainedSize);
  Real golden = (1+sqrt(Real(5)))/2;
  for(int i = 0; i < retainedSize; ++i)
  {
    for(int j = 0; j < retainedSize; ++j)
    {
      int index = i*retainedSize+j;
      if((i == 0 && j == 0) || i == retainedSize/2 || j == retainedSize/2)
      {
        result[index] = {};
        continue;
      }
      Real divisor = getMode(i, retainedSize)+golden*getMode(j, retainedSize);
      result[index] = {-result[index].im/divisor, result[index].re/divisor};
    }
  }
  // Only used to propose a numerical correction; final validation is independent.
  freezeReal(result, retainedSize);
  return result;
}

static double parseDiagnostic(const std::string &text)
{
  size_t end;
  double value;
  try
  {
    value = std::stod(text, &end);
  }
  catch(const std::exception &)
  {
    throw std::invalid_argument("Malformed CSV number: " + text);
  }
  if(end != text.size() || !std::isfinite(value))
  {
    throw std::invalid_argument("Nonfinite or malformed CSV number");
  }
  return value;
}
Candidate loadCsv(const std::string &path, int retainedSize)
{
  std::ifstream input(path);
  if(!input)
  {
    throw std::invalid_argument("Cannot open CSV: " + path);
  }
  std::string line;
  std::getline(input, line);
  if(line.rfind("# epsilon=", 0) != 0)
  {
    throw std::invalid_argument("Missing KAMExample CSV metadata");
  }
  auto first = line.find(", omega1="), second = line.find(", omega2=");
  if(first == std::string::npos || second == std::string::npos || second <= first)
  {
    throw std::invalid_argument("Missing frequency metadata");
  }
  parseDiagnostic(line.substr(10, first-10));
  double omega1 = parseDiagnostic(line.substr(first+9, second-first-9));
  double omega2 = parseDiagnostic(line.substr(second+9));
  if(std::abs(omega1-1) > 1e-12 || std::abs(omega2-(1+std::sqrt(5.0))/2) > 1e-12)
  {
    throw std::invalid_argument("This validator targets the exact golden frequency only");
  }
  std::getline(input, line);
  if(line != "theta1,theta2,phi1,phi2,I1,I2,u1,u2,v1,v2,E1,E2,E3,E4,H")
  {
    throw std::invalid_argument("Unsupported CSV columns");
  }
  Samples values;
  std::vector<std::array<double, 2>> angles;
  while(std::getline(input, line))
  {
    std::stringstream row(line);
    std::vector<std::string> fields;
    std::string token;
    while(std::getline(row, token, ','))
    {
      fields.push_back(token);
      parseDiagnostic(token);
    }
    if(fields.size() != 15)
    {
      throw std::invalid_argument("CSV row does not have 15 columns");
    }
    angles.push_back({parseDiagnostic(fields[0]), parseDiagnostic(fields[1])});
    for(int component = 0; component < 4; ++component)
    {
      values[component].emplace_back(fields[6+component]);
    }
    if(angles.size() > 2048UL*2048)
    {
      throw std::invalid_argument("CSV exceeds supported grid dimensions");
    }
  }
  int size = static_cast<int>(std::sqrt(static_cast<double>(angles.size())));
  if(!isPowerOfTwo(size) || static_cast<size_t>(size)*size != angles.size())
  {
    throw std::invalid_argument("CSV is not a square power-of-two grid");
  }
  for(int i = 0; i < size; ++i)
  {
    for(int j = 0; j < size; ++j)
    {
      if(std::abs(angles[i*size+j][0]-2*std::acos(-1.0)*i/size) > 1e-12 ||
         std::abs(angles[i*size+j][1]-2*std::acos(-1.0)*j/size) > 1e-12)
      {
        throw std::invalid_argument("CSV grid order or angle convention is incorrect");
      }
    }
  }
  Candidate result;
  result.size = retainedSize == 0 ? size : retainedSize;
  if(!isPowerOfTwo(result.size))
  {
    throw std::invalid_argument("Invalid retained mode size");
  }
  for(int component = 0; component < 4; ++component)
  {
    result.coefficients[component] = resizeSpectrum(computeCoefficients(values[component], size), size, result.size);
    freezeReal(result.coefficients[component], result.size);
  }
  return result;
}

void saveCandidate(const Candidate &candidate, const std::string &path)
{
  std::ofstream output(path);
  if(!output)
  {
    throw std::runtime_error("Cannot write candidate: " + path);
  }
  output << "KAM_CANDIDATE_V1 " << candidate.size << ' ' << precision << '\n';
  for(int index = 0; index < candidate.size*candidate.size; ++index)
  {
    for(int component = 0; component < 4; ++component)
    {
      const Complex &number = candidate.coefficients[component][index];
      output << printExact(number.re) << ' ' << printExact(number.im) << ' ';
    }
    output << '\n';
  }
  if(!output)
  {
    throw std::runtime_error("Failed to write candidate");
  }
}
Candidate loadCandidate(const std::string &path)
{
  std::ifstream input(path);
  std::string magic;
  int size = 0;
  long storedPrecision = 0;
  input >> magic >> size >> storedPrecision;
  if(magic != "KAM_CANDIDATE_V1" || !isPowerOfTwo(size) ||
     storedPrecision < 64 || storedPrecision > precision)
  {
    throw std::invalid_argument("Invalid native candidate, or insufficient precision");
  }
  Candidate candidate;
  candidate.size = size;
  for(Spectrum &component : candidate.coefficients)
  {
    component.resize(static_cast<size_t>(size)*size);
  }
  for(int index = 0; index < size*size; ++index)
  {
    for(Spectrum &component : candidate.coefficients)
    {
      std::string real, imaginary;
      if(!(input >> real >> imaginary))
      {
        throw std::invalid_argument("Truncated native candidate");
      }
      component[index] = {Real(real), Real(imaginary)};
      printExact(component[index].re);
      printExact(component[index].im);
    }
  }
  std::string extra;
  if(input >> extra)
  {
    throw std::invalid_argument("Unexpected native candidate data");
  }
  validateCandidate(candidate);
  return candidate;
}
void validateCandidate(const Candidate &candidate)
{
  int size = candidate.size;
  if(!isPowerOfTwo(size))
  {
    throw std::invalid_argument("Invalid candidate dimensions");
  }
  for(const Spectrum &component : candidate.coefficients)
  {
    if(component.size() != static_cast<size_t>(size)*size)
    {
      throw std::invalid_argument("Candidate component has the wrong size");
    }
    for(int i = 0; i < size; ++i)
    {
      for(int j = 0; j < size; ++j)
      {
        const Complex &a = component[i*size+j];
        const Complex &b = component[((size-i)%size)*size+(size-j)%size];
        requireFinite(a.re);
        requireFinite(a.im);
        if(mpfr_cmp(&a.re.value->left, &a.re.value->right) != 0 ||
           mpfr_cmp(&a.im.value->left, &a.im.value->right) != 0)
        {
          throw std::invalid_argument("Candidate coefficients must be exact point values");
        }
        if(!isZero(a.re-b.re) || !isZero(a.im+b.im) ||
           ((i == size/2 || j == size/2) &&
             (!isZero(a.re) || !isZero(a.im))))
        {
          throw std::invalid_argument("Candidate violates reality or Nyquist convention");
        }
      }
    }
  }
}
std::string fingerprint(const Candidate &candidate)
{
  uint64_t hash = 14695981039346656037ULL;
  auto append = [&](const std::string &text)
  {
    for(unsigned char byte : text)
    {
      hash ^= byte;
      hash *= 1099511628211ULL;
    }
  };
  append(std::to_string(candidate.size));
  for(const Spectrum &component : candidate.coefficients)
  {
    for(const Complex &number : component)
    {
      append(" " + printExact(number.re) + " " + printExact(number.im));
    }
  }
  std::ostringstream text;
  text << "fnv1a64:" << std::hex << std::setw(16) << std::setfill('0') << hash;
  return text.str();
}
}
