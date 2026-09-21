/*
 * exampleKAM.cpp
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

/** @file exampleKAM.cpp
 * @brief Single-torus example; the self-contained numerical library is in ../lib.
 */
#include "../lib/kam.h"

#include <cstdlib>
#include <getopt.h>
#include <iomanip>
#include <iostream>
#include <stdexcept>

namespace
{
struct ExampleOptions : kam::Options
{
  bool selfTest = false;
};

void printUsage(const char *program)
{
  std::cout << "Usage: " << program << " [options]\n"
    << "  -e, --epsilon VALUE     perturbation (default 0.01)\n"
    << "  -n, --grid SIZE         points/angle, power of two in [8,256] (32)\n"
    << "  -t, --tolerance VALUE   fine-grid residual tolerance (1e-11)\n"
    << "  -m, --max-steps COUNT   maximum quasi-Newton corrections (15)\n"
    << "      --omega1 VALUE      first target frequency (1)\n"
    << "      --omega2 VALUE      second target frequency ((1+sqrt(5))/2)\n"
    << "  -o, --output FILE       converged torus CSV (torus.csv)\n"
    << "  -s, --self-test         test FFT, derivatives, products and signs\n"
    << "  -h, --help              show this help\n\n"
    << "Angles have period 2*pi. Arithmetic is double precision.\n"
    << "Exit 0: converged on a 4*n check grid; 1: failure; 2: invalid options.\n";
}

ExampleOptions parseOptions(int argc, char * argv[])
{
  ExampleOptions options;
  const option longOptions[] =
  {
    {"epsilon", required_argument, nullptr, 'e'},
    {"grid", required_argument, nullptr, 'n'},
    {"tolerance", required_argument, nullptr, 't'},
    {"max-steps", required_argument, nullptr, 'm'},
    {"omega1", required_argument, nullptr, 1000},
    {"omega2", required_argument, nullptr, 1001},
    {"output", required_argument, nullptr, 'o'},
    {"self-test", no_argument, nullptr, 's'},
    {"help", no_argument, nullptr, 'h'},
    {nullptr, 0, nullptr, 0}
  };
  int choice;
  while((choice = getopt_long(argc, argv, "e:n:t:m:o:sh", longOptions, nullptr)) != -1)
  {
    switch(choice)
    {
      case 'e': options.epsilon = kam::parseReal(optarg); break;
      case 'n': options.gridSize = kam::parseInteger(optarg); break;
      case 't': options.tolerance = kam::parseReal(optarg); break;
      case 'm': options.maxSteps = kam::parseInteger(optarg); break;
      case 'o': options.outputPath = optarg; break;
      case 1000: options.omega[0] = kam::parseReal(optarg); break;
      case 1001: options.omega[1] = kam::parseReal(optarg); break;
      case 's': options.selfTest = true; break;
      case 'h': printUsage(argv[0]); std::exit(0);
      default: throw std::invalid_argument("Unknown or incomplete option; use --help.");
    }
  }
  if(optind != argc || !kam::isValidGrid(options.gridSize) || options.gridSize > 256 ||
     options.maxSteps < 1 || options.tolerance <= 0.0 || options.outputPath.empty())
  {
    throw std::invalid_argument("Invalid options; use --help.");
  }
  return options;
}
} // namespace

int main(int argc, char * argv[])
{
  try
  {
    const ExampleOptions options = parseOptions(argc, argv);
    if(options.selfTest)
    {
      kam::runSelfTests();
      return 0;
    }
    kam::Field periodicK = kam::createInitialTorus(options.gridSize);
    std::cout << std::setprecision(12)
      << "H = |I|^2/2 + epsilon*(cos(phi1)+cos(phi2)+cos(phi1-phi2))\n"
      << "epsilon = " << options.epsilon << ", omega = (" << options.omega[0]
      << ", " << options.omega[1] << "), grid = " << options.gridSize << '^' << 2 << '\n'
      << "Nonlinear work grid: 2*n; final residual check: 4*n.\n"
      << "step     residual(2*n)    correction     |<eta^N>|     cond(<T>)     cond(G)\n"
      << std::scientific << std::setprecision(5);
    const kam::SolveResult result = kam::solveTorus(periodicK, options, &std::cout);
    if(!result.converged)
    {
      std::cerr << "No convergence: " << result.reason
        << ". Increase --grid/--max-steps, relax --tolerance, or reduce --epsilon.\n";
      return 1;
    }
    kam::saveTorus(periodicK, options);
    std::cout << "Converged; torus written to " << options.outputPath << '\n';
    return 0;
  }
  catch(const std::invalid_argument &error)
  {
    std::cerr << error.what() << '\n';
    return 2;
  }
  catch(const std::exception &error)
  {
    std::cerr << "Computation failed: " << error.what() << '\n';
    return 1;
  }
}
