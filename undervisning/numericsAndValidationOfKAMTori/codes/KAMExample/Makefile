# Copyright (c) 2026, Jordi-Lluís Figueras.
# SPDX-License-Identifier: BSD-2-Clause
# See ../LICENSE for redistribution terms and disclaimer.

CXX ?= g++
CPPFLAGS ?=
CXXFLAGS ?= -O2 -std=c++17 -Wall -Wextra -Wpedantic
LDFLAGS ?=
LDLIBS ?=
PYTHON ?= python3

TARGET = exampleKAM.x

.PHONY: all run check figures clean

all: $(TARGET)

$(TARGET): exampleKAM.cpp ../lib/kam.cpp ../lib/kam.h
	$(CXX) $(CPPFLAGS) $(CXXFLAGS) exampleKAM.cpp ../lib/kam.cpp $(LDFLAGS) $(LDLIBS) -o $@

run: $(TARGET)
	./$(TARGET)

figures: $(TARGET) plot_results.py
	$(PYTHON) plot_results.py

check: $(TARGET)
	./$(TARGET) --self-test
	./$(TARGET) -e 0 -n 16 -o /dev/null
	./$(TARGET) -e 0.01 -n 32 -o /dev/null
	./$(TARGET) -e 0.03 -n 64 -t 1e-10 -o /dev/null

clean:
	$(RM) $(TARGET)
