/**
 * @file interval.h
 * @brief Local MPFI arithmetic for the standalone KAM validator.
 * Copyright (c) 2026, Jordi-Lluís Figueras. BSD-2-Clause; see LICENSE.
 */
#ifndef KAM_VALIDATION_INTERVAL_H
#define KAM_VALIDATION_INTERVAL_H

#include <mpfi.h>
#include <algorithm>
#include <cmath>
#include <iostream>
#include <stdexcept>
#include <string>

namespace validation
{
inline mpfr_prec_t precision = 256;

struct NotCertified : std::runtime_error
{
  using std::runtime_error::runtime_error;
};

class Real
{
public:
  mpfi_t value;

  Real()
  {
    mpfi_init2(value, precision);
    mpfi_set_ui(value, 0);
  }
  Real(long number) : Real()
  {
    mpfi_set_si(value, number);
  }
  explicit Real(const std::string &text) : Real()
  {
    if(text.empty() || text.find_first_of("[] ,\t\r\n") != std::string::npos)
    {
      throw std::invalid_argument("Invalid scalar: " + text);
    }
    int status;
    if(text.find('/') != std::string::npos)
    {
      mpq_t rational;
      mpq_init(rational);
      status = mpq_set_str(rational, text.c_str(), 10);
      if(status == 0 && mpz_sgn(mpq_denref(rational)) != 0)
      {
        mpq_canonicalize(rational);
        mpfi_set_q(value, rational);
      }
      else
      {
        status = -1;
      }
      mpq_clear(rational);
    }
    else
    {
      status = mpfi_set_str(value, text.c_str(), 0);
    }
    if(status != 0 || !mpfi_bounded_p(value) || mpfi_is_empty(value))
    {
      throw std::invalid_argument("Invalid finite scalar: " + text);
    }
  }
  Real(const Real &other) : Real()
  {
    mpfi_set(value, other.value);
  }
  Real(Real &&other) noexcept : Real()
  {
    mpfi_swap(value, other.value);
  }
  ~Real()
  {
    mpfi_clear(value);
  }
  Real &operator=(Real other)
  {
    mpfi_swap(value, other.value);
    return *this;
  }
};

inline void requireFinite(const Real &number)
{
  if(!mpfi_bounded_p(number.value) || mpfi_is_empty(number.value))
  {
    throw NotCertified("Nonfinite or empty interval in a bound");
  }
}
inline bool less(const Real &left, const Real &right)
{
  requireFinite(left);
  requireFinite(right);
  return mpfr_cmp(&left.value->right, &right.value->left) < 0;
}
inline bool containsZero(const Real &number)
{
  return mpfi_has_zero(number.value) != 0;
}
inline bool isZero(const Real &number)
{
  return mpfr_zero_p(&number.value->left) && mpfr_zero_p(&number.value->right);
}
inline Real upper(const Real &number)
{
  requireFinite(number);
  Real result;
  mpfi_set_fr(result.value, &number.value->right);
  return result;
}
inline Real lower(const Real &number)
{
  requireFinite(number);
  Real result;
  mpfi_set_fr(result.value, &number.value->left);
  return result;
}
inline Real midpoint(const Real &number)
{
  requireFinite(number);
  Real result;
  mpfr_t center;
  mpfr_init2(center, precision);
  mpfi_mid(center, number.value);
  mpfi_set_fr(result.value, center);
  mpfr_clear(center);
  return result;
}
inline Real operator+(const Real &left, const Real &right)
{
  Real result;
  mpfi_add(result.value, left.value, right.value);
  return result;
}
inline Real operator-(const Real &left, const Real &right)
{
  Real result;
  mpfi_sub(result.value, left.value, right.value);
  return result;
}
inline Real operator-(const Real &number)
{
  Real result;
  mpfi_neg(result.value, number.value);
  return result;
}
inline Real operator*(const Real &left, const Real &right)
{
  Real result;
  mpfi_mul(result.value, left.value, right.value);
  return result;
}
inline Real operator/(const Real &left, const Real &right)
{
  if(containsZero(right))
  {
    throw NotCertified("A denominator interval contains zero");
  }
  Real result;
  mpfi_div(result.value, left.value, right.value);
  return result;
}
inline Real &operator+=(Real &left, const Real &right)
{
  mpfi_add(left.value, left.value, right.value);
  return left;
}
inline Real &operator-=(Real &left, const Real &right)
{
  mpfi_sub(left.value, left.value, right.value);
  return left;
}
inline Real square(const Real &number)
{
  Real result;
  mpfi_sqr(result.value, number.value);
  return result;
}
inline Real sqrt(const Real &number)
{
  if(mpfr_sgn(&number.value->left) < 0)
  {
    throw NotCertified("Negative lower endpoint in a square root");
  }
  Real result;
  mpfi_sqrt(result.value, number.value);
  return result;
}
inline Real exp(const Real &number)
{
  Real result;
  mpfi_exp(result.value, number.value);
  requireFinite(result);
  return result;
}
inline Real sin(const Real &number)
{
  Real result;
  mpfi_sin(result.value, number.value);
  return result;
}
inline Real cos(const Real &number)
{
  Real result;
  mpfi_cos(result.value, number.value);
  return result;
}
inline Real cosh(const Real &number)
{
  Real result;
  mpfi_cosh(result.value, number.value);
  return result;
}
inline Real pi()
{
  Real result;
  mpfi_const_pi(result.value);
  return result;
}
inline Real magnitude(const Real &number)
{
  Real result;
  mpfr_t bound;
  mpfr_init2(bound, precision);
  mpfi_mag(bound, number.value);
  mpfi_set_fr(result.value, bound);
  mpfr_clear(bound);
  requireFinite(result);
  return result;
}
/** Upper bound of the maximum, never the ambiguous MPFI partial comparison. */
inline Real maxUpper(const Real &left, const Real &right)
{
  requireFinite(left);
  requireFinite(right);
  return mpfr_cmp(&left.value->right, &right.value->right) >= 0 ? upper(left) : upper(right);
}
inline Real inflate(const Real &number, const Real &radius)
{
  Real result(number);
  Real bound = magnitude(radius);
  mpfi_increase(result.value, &bound.value->right);
  return result;
}
inline double approximate(const Real &number)
{
  return mpfr_get_d(&number.value->right, MPFR_RNDU);
}
inline std::string printEndpoint(mpfr_srcptr endpoint, mpfr_rnd_t rounding)
{
  if(mpfr_zero_p(endpoint))
  {
    return "0";
  }
  if(!mpfr_number_p(endpoint))
  {
    throw NotCertified("Attempt to serialize a nonfinite endpoint");
  }
  mpfr_exp_t exponent;
  char *raw = mpfr_get_str(nullptr, &exponent, 10, 32, endpoint, rounding);
  std::string digits(raw);
  mpfr_free_str(raw);
  std::string sign;
  if(digits[0] == '-')
  {
    sign = "-";
    digits.erase(0, 1);
  }
  return sign + digits.substr(0, 1) + "." + digits.substr(1) + "e" +
    std::to_string(exponent-1);
}
inline std::string printInterval(const Real &number)
{
  requireFinite(number);
  return "[\"" + printEndpoint(&number.value->left, MPFR_RNDD) + "\",\"" +
    printEndpoint(&number.value->right, MPFR_RNDU) + "\"]";
}
inline std::string printExact(const Real &number)
{
  if(mpfr_cmp(&number.value->left, &number.value->right) != 0)
  {
    throw std::invalid_argument("Candidate coefficient is not an exact point");
  }
  char *text = nullptr;
  mpfr_asprintf(&text, "%Ra", &number.value->left);
  std::string result(text);
  mpfr_free_str(text);
  return result;
}
struct Complex
{
  Real re, im;
  Complex() = default;
  Complex(const Real &real, const Real &imaginary = Real()) : re(real), im(imaginary) {}
};
inline Complex operator+(const Complex &left, const Complex &right)
{
  return {left.re+right.re, left.im+right.im};
}
inline Complex operator-(const Complex &left, const Complex &right)
{
  return {left.re-right.re, left.im-right.im};
}
inline Complex operator*(const Complex &left, const Complex &right)
{
  return {left.re*right.re-left.im*right.im, left.re*right.im+left.im*right.re};
}
inline Complex operator*(const Complex &left, const Real &right)
{
  return {left.re*right, left.im*right};
}
inline Complex conjugate(const Complex &number)
{
  return {number.re, -number.im};
}
inline Real magnitude(const Complex &number)
{
  return upper(sqrt(square(magnitude(number.re))+square(magnitude(number.im))));
}
}
#endif
