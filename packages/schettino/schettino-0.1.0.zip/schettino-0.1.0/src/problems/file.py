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

import os
import json

import base

class FileProblem(base.Problem):

    @staticmethod
    def create_problem(problem_p, persons_p = None, timetables_p = None):
        problem_file = open(problem_p, "r")
        try: problem = json.load(problem_file)
        finally: problem_file.close()

        persons_r = {}
        names = persons_p and os.listdir(persons_p) or []
        for name in names:
            _base, extension = os.path.splitext(name)
            if not extension == ".json": continue
            person_p = os.path.join(persons_p, name)
            person_file = open(person_p, "r")
            try: person = json.load(person_file)
            finally: person_file.close()

            person_id = person["id"]
            persons_r[person_id] = person

        timetables_r = {}
        names = timetables_p and os.listdir(timetables_p) or []
        for name in names:
            _base, extension = os.path.splitext(name)
            if not extension == ".json": continue
            timetable_p = os.path.join(timetables_p, name)
            timetable_file = open(timetable_p, "r")
            try: timetable = json.load(timetable_file)
            finally: timetable_file.close()

            # retrieves the identifier and the bitmask for the
            # timetable and then sets the bitmaks as the timetable
            # rule in the timetable rules map for the identifier
            timetable_id = timetable["id"]
            timetable_bitmask = timetable["bitmask"]
            timetables_r[timetable_id] = timetable_bitmask

        # creates a new instance of the file problem to be used
        # in the for populating the values
        object = FileProblem.__new__(FileProblem)

        # sets the various (general) project attributes from the
        # problem map in the object (attribute propagation)
        for key, value in problem.items(): setattr(object, key, value)

        # sets the persons rules and the timetables rules attributes
        # in the object, these attributes are composite and calculation
        # for them is based in multiple files
        setattr(object, "persons_r", persons_r)
        setattr(object, "timetables_r", timetables_r)

        # calls the initializer of the object, at this
        # point the calculated attributes are ready and
        # then returns the (now) initialized object
        object.__init__()
        return object
