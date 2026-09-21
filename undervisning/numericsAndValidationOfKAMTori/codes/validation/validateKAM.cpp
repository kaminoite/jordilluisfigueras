/**
 * @file validateKAM.cpp
 * @brief Standalone MPFI validator for the KAMExample Hamiltonian.
 * Copyright (c) 2026, Jordi-Lluís Figueras. BSD-2-Clause; see LICENSE.
 */
#include "kamBounds.h"
#include <getopt.h>
#include <fstream>
#include <filesystem>
#include <sstream>

namespace
{
using namespace validation;
std::string quote(const std::string &text)
{
  std::string result = "\"";
  for(unsigned char letter : text)
  {
    if(letter == '\\' || letter == '"')
    {
      result += '\\';
    }
    if(letter < 32)
    {
      result += ' ';
    }
    else
    {
      result += static_cast<char>(letter);
    }
  }
  return result + '"';
}
int parseInteger(const char *text, int minimum, int maximum)
{
  std::string argument(text);
  size_t length;
  long value = std::stol(argument, &length);
  if(length != argument.size() || value < minimum || value > maximum)
  {
    throw std::invalid_argument("Integer option outside supported range: " + argument);
  }
  return static_cast<int>(value);
}
void printHelp()
{
  std::cout <<
    "Usage: validateKAM.x --input torus.csv --epsilon 1/100 [options]\n"
    "       validateKAM.x --candidate frozen.torus --epsilon 1/100 [options]\n"
    "  --frequency golden      Exact (1,(1+sqrt(5))/2); only supported target\n"
    "  --precision BITS        MPFI precision, default 256\n"
    "  --modes N               Fourier size for CSV import (default input size)\n"
    "  --refine STEPS          Optional seed refinement, default 0\n"
    "  --grid M                Certified evaluation grid per angle, default 256\n"
    "  --rho R                 Initial strip in radians, default 1/10\n"
    "  --rho-final R           Final strip in radians, default 1/20\n"
    "  --rho-wide R            Wider strip for alias bounds, default 1/2\n"
    "  --domain-margin R       Ambient domain reserve, default 1/10\n"
    "  --sigma-factor F        Strict geometric budget factor, default 2\n"
    "  --certificate FILE      Write JSON and exact FILE.torus sidecar\n"
    "  --candidate-out FILE    Save the exact candidate independently\n"
    "  --help                  This message\n"
    "Exit: 0 validated, 1 not certified, 2 invalid input or I/O failure.\n";
}
bool samePath(const std::string &left, const std::string &right)
{
  if(left.empty() || right.empty())
  {
    return false;
  }
  std::error_code error;
  bool sameFile = std::filesystem::equivalent(left, right, error);
  return (!error && sameFile) ||
    std::filesystem::weakly_canonical(left) == std::filesystem::weakly_canonical(right);
}
}

int main(int argc, char * argv[])
{
  using namespace validation;
  std::string inputPath, nativePath, certificatePath, candidatePath;
  std::string epsilonText, rhoText = "1/10", finalText = "1/20", wideText = "1/2";
  std::string marginText = "1/10", sigmaText = "2", frequency = "golden";
  int modes = 0, grid = 256, refinement = 0;
  static const option options[] =
  {
    {"input", required_argument, nullptr, 'i'},
    {"candidate", required_argument, nullptr, 'c'},
    {"epsilon", required_argument, nullptr, 'e'},
    {"precision", required_argument, nullptr, 'p'},
    {"modes", required_argument, nullptr, 'n'},
    {"grid", required_argument, nullptr, 'g'},
    {"refine", required_argument, nullptr, 'r'},
    {"rho", required_argument, nullptr, 1000},
    {"rho-final", required_argument, nullptr, 1001},
    {"rho-wide", required_argument, nullptr, 1002},
    {"domain-margin", required_argument, nullptr, 1003},
    {"sigma-factor", required_argument, nullptr, 1004},
    {"frequency", required_argument, nullptr, 1005},
    {"certificate", required_argument, nullptr, 'o'},
    {"candidate-out", required_argument, nullptr, 1006},
    {"help", no_argument, nullptr, 'h'},
    {nullptr, 0, nullptr, 0}
  };
  try
  {
    int choice;
    while((choice = getopt_long(argc, argv, "i:c:e:p:n:g:r:o:h", options, nullptr)) != -1)
    {
      switch(choice)
      {
        case 'i': inputPath = optarg; break;
        case 'c': nativePath = optarg; break;
        case 'e': epsilonText = optarg; break;
        case 'p': precision = parseInteger(optarg, 64, 4096); break;
        case 'n': modes = parseInteger(optarg, 4, 1024); break;
        case 'g': grid = parseInteger(optarg, 4, 2048); break;
        case 'r': refinement = parseInteger(optarg, 0, 20); break;
        case 'o': certificatePath = optarg; break;
        case 1000: rhoText = optarg; break;
        case 1001: finalText = optarg; break;
        case 1002: wideText = optarg; break;
        case 1003: marginText = optarg; break;
        case 1004: sigmaText = optarg; break;
        case 1005: frequency = optarg; break;
        case 1006: candidatePath = optarg; break;
        case 'h': printHelp(); return 0;
        default: throw std::invalid_argument("Unknown or incomplete option");
      }
    }
    if(optind != argc || inputPath.empty() == nativePath.empty() || epsilonText.empty() ||
       frequency != "golden" || (!nativePath.empty() && modes != 0))
    {
      throw std::invalid_argument("Specify one input, an exact epsilon, and the golden target frequency");
    }
    Parameters parameters;
    for(const std::string &output : {candidatePath, certificatePath,
      certificatePath.empty() ? std::string() : certificatePath+".torus"})
    {
      if(samePath(output, inputPath) || samePath(output, nativePath))
      {
        throw std::invalid_argument("An output path aliases the input");
      }
    }
    if(samePath(candidatePath, certificatePath))
    {
      throw std::invalid_argument("Candidate and certificate outputs must differ");
    }
    parameters.epsilon = Real(epsilonText);
    parameters.rho = Real(rhoText);
    parameters.finalRho = Real(finalText);
    parameters.wideRho = Real(wideText);
    parameters.domainMargin = Real(marginText);
    parameters.sigmaFactor = Real(sigmaText);
    parameters.gridSize = grid;
    if(!less(0, parameters.rho) || !less(0, parameters.finalRho) ||
       !less(parameters.finalRho, parameters.rho) || !less(parameters.rho, parameters.wideRho) ||
       !less(0, parameters.domainMargin) || !less(1, parameters.sigmaFactor) ||
       !isPowerOfTwo(grid) || (modes != 0 && !isPowerOfTwo(modes)))
    {
      throw std::invalid_argument("Invalid strip or discretization options");
    }
    std::cout << "MPFI " << mpfi_get_version() << ", precision " << precision << " bits\n";
    Candidate candidate = nativePath.empty() ? loadCsv(inputPath, modes) : loadCandidate(nativePath);
    if(grid < 2*candidate.size)
    {
      throw std::invalid_argument("Validation grid must be at least twice the candidate size");
    }
    Bounds bounds;
    bool validated = false;
    std::string reason;
    try
    {
      refineCandidate(candidate, parameters.epsilon, refinement, std::cout);
      bounds = computeBounds(candidate, parameters, std::cout);
      validated = checkTheorem(bounds, parameters, reason);
    }
    catch(const NotCertified &failure)
    {
      reason = failure.what();
    }
    std::string status = validated ? "VALIDATED" : "NOT_CERTIFIED";
    std::string signature = fingerprint(candidate);
    if(!candidatePath.empty())
    {
      if(candidatePath == inputPath || candidatePath == nativePath)
      {
        throw std::invalid_argument("Candidate output must differ from its input");
      }
      saveCandidate(candidate, candidatePath);
    }
    if(!certificatePath.empty())
    {
      if(certificatePath == inputPath || certificatePath == nativePath ||
         certificatePath+".torus" == nativePath || certificatePath+".torus" == inputPath)
      {
        throw std::invalid_argument("Certificate output must differ from its input");
      }
      std::string sidecar = certificatePath+".torus";
      saveCandidate(candidate, sidecar);
      std::ofstream report(certificatePath);
      if(!report)
      {
        throw std::runtime_error("Cannot write certificate");
      }
      report << "{\n  \"format\": \"FH2024_KAMEXAMPLE_V1\",\n"
        << "  \"status\": " << quote(status) << ",\n"
        << "  \"reason\": " << quote(reason) << ",\n"
        << "  \"theorem\": \"Figueras-Haro 2024, Theorem 2.18, d=n=2\",\n"
        << "  \"epsilon_exact\": " << quote(epsilonText) << ",\n"
        << "  \"frequency_exact\": \"(1,(1+sqrt(5))/2)\",\n"
        << "  \"action_offset\": \"exact frequency\",\n"
        << "  \"real_domain\": \"real slice of U0 intersect {I1>0}\",\n"
        << "  \"candidate\": " << quote(sidecar) << ",\n"
        << "  \"candidate_fingerprint\": " << quote(signature) << ",\n"
        << "  \"precision_bits\": " << precision << ",\n"
        << "  \"mpfi_version\": " << quote(mpfi_get_version()) << ",\n"
        << "  \"mpfr_version\": " << quote(mpfr_get_version()) << ",\n"
        << "  \"modes\": " << candidate.size << ",\n"
        << "  \"grid\": " << grid << ",\n"
        << "  \"refinement_steps\": " << refinement << ",\n"
        << "  \"bound_semantics\": \"Intervals enclose computed quantities; norm bounds are majorants, not two-sided estimates of the actual norms\",\n"
        << "  \"parameters_exact\": {\n"
        << "    \"rho_radian\": " << quote(rhoText) << ",\n"
        << "    \"rho_final_radian\": " << quote(finalText) << ",\n"
        << "    \"rho_wide_radian\": " << quote(wideText) << ",\n"
        << "    \"domain_margin\": " << quote(marginText) << ",\n"
        << "    \"sigma_factor\": " << quote(sigmaText) << "\n  },\n"
        << "  \"bounds\": {\n";
      bool first = true;
      for(const auto &entry : bounds.values)
      {
        if(!first)
        {
          report << ",\n";
        }
        first = false;
        report << "    " << quote(entry.first) << ": " << printInterval(entry.second);
      }
      report << "\n  }\n}\n";
      if(!report)
      {
        throw std::runtime_error("Failed to write certificate");
      }
    }
    std::cout << status << ": " << reason << '\n';
    for(const std::string key : {"b_E", "nu", "theorem_condition", "kappa", "distance_K", "distance_DK"})
    {
      if(bounds.values.count(key))
      {
        std::cout << key << " = " << printInterval(bounds.get(key)) << '\n';
      }
    }
    std::cout << "Candidate " << signature << '\n';
    return validated ? 0 : 1;
  }
  catch(const std::exception &error)
  {
    std::cerr << "INVALID_INPUT_OR_IO: " << error.what() << '\n';
    return 2;
  }
}
