#!/usr/bin/python
# -*- coding: utf-8 -*-

# Hive Schettino System
# Copyright (C) 2008-2012 Hive Solutions Lda.
#
# This file is part of Hive Schettino System.
#
# Hive Schettino System is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Hive Schettino System is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Hive Schettino System. If not, see <http://www.gnu.org/licenses/>.

__author__ = "João Magalhães <joamag@hive.pt>"
""" The author(s) of the module """

__version__ = "1.0.0"
""" The version of the module """

__revision__ = "$LastChangedRevision$"
""" The revision number of the module """

__date__ = "$LastChangedDate$"
""" The last change date of the module """

__copyright__ = "Copyright (c) 2008-2012 Hive Solutions Lda."
""" The copyright for the module """

__license__ = "GNU General Public License (GPL), Version 3"
""" The license for the module """

import time

import problems.base
import problems.file
import problems.simple
import problems.complex

problems.base
problems.file
problems.simple
problems.complex

def solve(problem, value = None, all = False, callback = None):
    solution = problems.base.Solution()
    initial = time.time()
    problem.solution = _solve(problem, solution, value, all, callback)
    problem.delta = int((time.time() - initial) * 1000)
    return problem.solution

def _solve(problem, solution, value = None, all = False, callback = None):
    # in case the provided value is not set (first execution)
    # must start some values to be able to execute
    if value == None: position = 0

    # otherwise it's a "normal" execution and the incremental
    # solution must be created and validated (backtracking)
    else:
        # updates the solution with the new value then verifies
        # if it's a valid solution for the problem, in case it's
        # not returns immediately with an invalid value
        solution = solution.try_extend(value)
        result = problem.verify(solution)
        if not result: return None

        # updates the "state" of the solution, this operation
        # should "calculate" all the "indirect" attributes that
        # will then help in the discovery of the best match for
        # the next iteration in solving process
        problem.state(solution)

        # retrieves the current solution position and in case it's
        # the last calls the callback in case one is defined and then
        # returns the solution backtracking
        position = len(solution)
        if position == problem.number_items:
            callback and callback(problem, solution)
            return solution

    # in case the current global bitmap position is not set, ther's
    # no need to allocate a person to the task
    if problem.bitmap[position] == 0:
        result = _solve(problem, solution, [-1], all, callback)
        if all: pass
        elif result: return result

    # otherwise the normal situation applies an a person (index) must
    # be allocated to the task, must be selected from a ordered list
    else:
        # retrieves the domain range in an ordered fashion so
        # that the solutions generated from these values are the
        # best possible matches (provides faster resolution speed)
        ordered = problem.get_ordered(solution)

        for index in ordered:
            result = _solve(problem, solution, index, all, callback)
            if all: continue
            if not result: continue
            return result

    # returns invalid, because there is no solution for the
    # current configuration or because the all parameter is
    # set and no result should be returned
    return None

def handler(problem, solution):
    problem.print_s(solution)

def run():
    problem = problems.simple.SimpleProblem()
    solve(problem, all = True, callback = handler)

if __name__ == "__main__":
    run()
