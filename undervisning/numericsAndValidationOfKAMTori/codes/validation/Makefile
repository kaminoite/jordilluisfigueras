# Copyright (c) 2026, Jordi-Lluís Figueras.
# SPDX-License-Identifier: BSD-2-Clause
# See LICENSE for redistribution terms and disclaimer.

CXX ?= g++
MPFI_PREFIX ?= /usr/local
CPPFLAGS ?=
CXXFLAGS ?= -O2 -std=c++17 -Wall -Wextra -Wpedantic
LDFLAGS ?=
LDLIBS = -lmpfi -lmpfr -lgmp
ARITHMETIC_FLAGS = -I$(MPFI_PREFIX)/include -L$(MPFI_PREFIX)/lib -Wl,-rpath,$(MPFI_PREFIX)/lib
SOURCES = fourier.cpp kamBounds.cpp figuerasHaro.cpp
HEADERS = interval.h fourier.h kamBounds.h

.PHONY: all check standalone-check clean
all: validateKAM.x

validateKAM.x: validateKAM.cpp $(SOURCES) $(HEADERS)
	$(CXX) $(CPPFLAGS) $(CXXFLAGS) $(ARITHMETIC_FLAGS) validateKAM.cpp $(SOURCES) $(LDFLAGS) $(LDLIBS) -o $@

tests.x: tests.cpp $(SOURCES) $(HEADERS)
	$(CXX) $(CPPFLAGS) $(CXXFLAGS) $(ARITHMETIC_FLAGS) tests.cpp $(SOURCES) $(LDFLAGS) $(LDLIBS) -o $@

check: validateKAM.x tests.x
	./tests.x

# Build AND run tests using only this directory's own source files.
TMPDIR ?= /tmp
standalone-check:
	@set -eu; work=$$(mktemp -d "$(TMPDIR)/kam-standalone-XXXXXX"); \
	trap 'rm -rf "$$work"' EXIT; \
	cp $(SOURCES) $(HEADERS) validateKAM.cpp tests.cpp Makefile LICENSE "$$work/"; \
	$(MAKE) -C "$$work" MPFI_PREFIX="$(MPFI_PREFIX)" check

clean:
	$(RM) validateKAM.x tests.x
