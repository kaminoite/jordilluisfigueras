/** @file tests.cpp
 * Analytic, aliasing, inverse, input, and nontrivial theorem tests.
 * Copyright (c) 2026, Jordi-Lluís Figueras. BSD-2-Clause; see LICENSE.
 */
#include "kamBounds.h"
#include <filesystem>
#include <fstream>
#include <functional>
#include <iomanip>
#include <sstream>
#include <unistd.h>
#include <sys/wait.h>

using namespace validation;
namespace
{
int checks = 0;
void require(bool condition, const std::string &name)
{
  if(!condition)
  {
    throw std::runtime_error("FAILED: " + name);
  }
  ++checks;
}
void requireThrow(const std::function<void()> &operation, const std::string &name)
{
  bool rejected = false;
  try
  {
    operation();
  }
  catch(const std::exception &)
  {
    rejected = true;
  }
  require(rejected, name);
}
Candidate zeroCandidate(int size)
{
  Candidate result;
  result.size = size;
  for(Spectrum &component : result.coefficients)
  {
    component.resize(static_cast<size_t>(size)*size);
  }
  return result;
}
int indexMode(int a, int b, int size)
{
  return ((a+size)%size)*size+(b+size)%size;
}
void putMode(Spectrum &data, int size, int a, int b, const Complex &value)
{
  data[indexMode(a, b, size)] = value;
  data[indexMode(-a, -b, size)] = conjugate(value);
}
struct TemporaryDirectory
{
  std::filesystem::path path;
  TemporaryDirectory()
  {
    std::string pattern = (std::filesystem::temp_directory_path()/"kam-validation-tests-XXXXXX").string();
    std::vector<char> buffer(pattern.begin(), pattern.end());
    buffer.push_back(0);
    char *name = mkdtemp(buffer.data());
    if(!name)
    {
      throw std::runtime_error("Cannot create test directory");
    }
    path = name;
  }
  ~TemporaryDirectory()
  {
    std::error_code error;
    std::filesystem::remove_all(path, error);
  }
};
}

int main()
{
  try
  {
    precision = 256;
    TemporaryDirectory temporary;
    std::ostringstream log;
    Real tolerance("1e-65");
    require(containsZero(Real("1/10")+Real("1/5")-Real("3/10")), "exact decimal/rational arithmetic");
    require(less(upper(inflate(Real(1), Real("1/10"))), maxUpper(inflate(Real(1), Real("1/10")),
      inflate(Real(1), Real("1/5")))), "maximum of overlapping intervals uses upper endpoints");
    requireThrow([] { Real invalid("nan"); }, "NaN scalar rejection");
    requireThrow([] { Real invalid("1/0"); }, "zero rational denominator rejection");
    requireThrow([] { auto invalid = Real(1)/inflate(Real(0), Real(1)); }, "zero-containing interval division");
    requireThrow([] { Matrix2 matrix = {{{1, 2}, {2, 4}}}; invertMatrix(matrix); }, "singular inverse rejection");
    Matrix2 matrix = {{{2, 1}, {1, 3}}};
    Matrix2 inverse = invertMatrix(matrix);
    require(containsZero(inverse[0][0]-Real("3/5")) &&
      containsZero(inverse[0][1]+Real("1/5")), "verified inverse of a rational matrix");

    // A polynomial with genuinely mixed, asymmetric signed modes.
    Candidate polynomial = zeroCandidate(16);
    putMode(polynomial.coefficients[0], 16, 2, -1, {Real("1/2"), 0});
    putMode(polynomial.coefficients[0], 16, 1, 3, {0, Real("-1/8")});
    validateCandidate(polynomial);
    Grid samples = evaluate(polynomial.coefficients[0], 16, 16);
    Grid derivative = evaluate(differentiate(polynomial.coefficients[0], 16, 0), 16, 16);
    Spectrum recovered = computeCoefficients(samples, 16);
    for(int i = 0; i < 16; ++i)
    {
      for(int j = 0; j < 16; ++j)
      {
        Real x = 2*pi()*i/16, y = 2*pi()*j/16;
        Real exact = cos(2*x-y)+sin(x+3*y)/4;
        Real exactDerivative = -2*sin(2*x-y)+cos(x+3*y)/4;
        require(less(magnitude(samples[i*16+j]-exact), tolerance), "2D FFT versus analytic mixed modes");
        require(less(magnitude(derivative[i*16+j]-exactDerivative), tolerance), "Fourier differentiation sign/normalization");
        require(less(magnitude(recovered[i*16+j]-polynomial.coefficients[0][i*16+j]), tolerance),
          "forward FFT encloses analytic Fourier coefficients");
      }
    }
    Candidate invalid = polynomial;
    invalid.coefficients[0][8*16].re = 1;
    requireThrow([&] { validateCandidate(invalid); }, "nonzero Nyquist line rejected by public candidate contract");
    invalid = polynomial;
    invalid.coefficients[0][2*16+15].im = 1;
    requireThrow([&] { validateCandidate(invalid); }, "broken conjugate symmetry rejection");

    Spectrum forcing(16*16);
    putMode(forcing, 16, 2, -1, {Real("1/2"), 0});
    Spectrum solution = solveCohomology(evaluate(forcing, 16, 16), 16, 16);
    Real golden = (1+sqrt(Real(5)))/2;
    require(less(magnitude(solution[indexMode(2, -1, 16)]-
      Complex(0, Real(1)/(2*(2-golden)))), tolerance), "cohomological divisor and sign");

    // cos(M theta1)-1 vanishes on EVERY grid point but is -2 between points.
    // The continuous error must include the analytic alias/tail contribution.
    Real wide("1/4");
    Real hiddenBound = computeGridError(16, Real(0), wide)*(cosh(16*wide)+1);
    require(less(2, hiddenBound), "off-grid hidden mode covered by interpolation bound");
    require(less(1, computeAverageError(16, wide)*cosh(16*wide)), "mean alias cos(M theta) covered");
    requireThrow([&] { computeGridError(16, wide, wide); }, "zero strip separation rejected");

    std::string native = (temporary.path/"roundtrip.torus").string();
    saveCandidate(polynomial, native);
    require(fingerprint(loadCandidate(native)) == fingerprint(polynomial), "exact native candidate round trip");
    {
      std::ofstream file(temporary.path/"bad.torus");
      file << "KAM_CANDIDATE_V1 16 256\n0x0p+0";
    }
    requireThrow([&] { loadCandidate((temporary.path/"bad.torus").string()); }, "truncated candidate rejection");

    std::string csv = (temporary.path/"sample.csv").string();
    {
      std::ofstream file(csv);
      file << "# epsilon=0, omega1=1, omega2=1.6180339887498949\n"
        << "theta1,theta2,phi1,phi2,I1,I2,u1,u2,v1,v2,E1,E2,E3,E4,H\n";
      file << std::setprecision(17);
      for(int i = 0; i < 4; ++i)
      {
        for(int j = 0; j < 4; ++j)
        {
          double x = 2*std::acos(-1.0)*i/4, y = 2*std::acos(-1.0)*j/4;
          file << x << ',' << y << ',' << x << ',' << y << ",1,1.6180339887498949,0,0,0,0,99,99,99,99,0\n";
        }
      }
    }
    Candidate imported = loadCsv(csv, 4);
    require(fingerprint(imported) == fingerprint(zeroCandidate(4)), "CSV importer uses periodic columns, ignores advertised residual");
    auto runCli = [&](const std::string &arguments)
    {
      int result = std::system(("./validateKAM.x " + arguments + " >/dev/null 2>&1").c_str());
      return WIFEXITED(result) ? WEXITSTATUS(result) : -1;
    };
    require(runCli("--help") == 0, "CLI help");
    require(runCli("--input " + csv + " --epsilon 0 --frequency rational") == 2,
      "CLI rejects unsupported exact frequency");
    require(runCli("--input " + csv + " --epsilon 0 --precision 63") == 2,
      "CLI rejects invalid precision");
    require(runCli("--input " + csv + " --epsilon 0 --rho-wide 0") == 2,
      "CLI rejects invalid strip widths");
    std::string alias = (temporary.path/"alias.csv").string();
    std::filesystem::create_symlink(csv, alias);
    require(runCli("--input " + csv + " --epsilon 0 --certificate " + alias) == 2,
      "CLI protects input through symlink aliases");
    std::string hardlink = (temporary.path/"hardlink.csv").string();
    std::filesystem::create_hard_link(csv, hardlink);
    require(runCli("--input " + csv + " --epsilon 0 --certificate " + hardlink) == 2,
      "CLI protects input through hard links");
    require(runCli("--input " + csv + " --epsilon 0 --grid 32 --certificate " +
      (temporary.path/"integrable.json").string()) == 0, "CLI end-to-end certificate and native sidecar");

    Parameters parameters;
    parameters.epsilon = 0;
    parameters.gridSize = 32;
    Bounds integrable = computeBounds(imported, parameters, log);
    std::string reason;
    require(isZero(integrable.get("b_E")), "symbolic exact integrable residual");
    require(containsZero(integrable.get("average_T_00")-Real(1)/square(2*pi())), "unit-parameter theorem torsion");
    require(containsZero(integrable.get("gamma")*2*pi()-1), "unit-parameter Diophantine conversion");
    require(checkTheorem(integrable, parameters, reason), "integrable theorem hypotheses");
    require(isZero(integrable.get("distance_K")), "exact integrable distance bound");
    Bounds damaged = integrable;
    damaged.set("b_etaL", 1);
    damaged.set("b_etaN", 1);
    require(!checkTheorem(damaged, parameters, reason), "large error cannot certify");
    Candidate folded = zeroCandidate(4);
    putMode(folded.coefficients[0], 4, 1, 0, {0, Real("-1/2")});
    requireThrow([&] { computeBounds(folded, parameters, log); }, "folded angular map/Gram test");
    Candidate high = zeroCandidate(4);
    high.coefficients[2][0].re = -2;
    requireThrow([&] { computeBounds(high, parameters, log); }, "regular real-domain hypothesis");

    // Entirely self-contained nonzero-coupling certificate: build a seed locally.
    Candidate coupled = zeroCandidate(16);
    parameters.epsilon = Real("1/10000");
    parameters.gridSize = 128;
    parameters.wideRho = 1;
    refineCandidate(coupled, parameters.epsilon, 5, log);
    Bounds nontrivial = computeBounds(coupled, parameters, log);
    bool success = checkTheorem(nontrivial, parameters, reason);
    if(!success)
    {
      std::cerr << log.str() << reason << '\n';
    }
    require(success, "positive-coupling theorem certificate");
    require(less(0, nontrivial.get("b_E")) && less(nontrivial.get("theorem_condition"), 1),
      "nontrivial finite certificate inequality");
    require(less(nontrivial.get("distance_K"), Real("1e-8")), "nontrivial quantitative closeness");
    std::cout << "Passed " << checks << " checks, including a nonzero-coupling certificate.\n";
    return 0;
  }
  catch(const std::exception &error)
  {
    std::cerr << error.what() << '\n';
    return 1;
  }
}
