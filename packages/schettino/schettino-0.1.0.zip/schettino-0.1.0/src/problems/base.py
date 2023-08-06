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

import copy

MAX_ALLOCATIONS = 8
""" The maximum number of allocation for a certain task
and for a certain slot (position) this value have some
impact in the performance of the engine """

class Solution(list):
    """
    The base class for the solution of a problem,
    note that it inherits from the base list type
    because all the solution are expected to be
    expressed as a list.
    """

    meta = {}
    """ The meta information map that contains information
    of calculus for the heuristics to be used in the solving """

    def __init__(self):
        self.meta = {}

    def try_extend(self, value):
        _clone = copy.copy(self)
        _clone.append(value)
        _clone.meta = self.meta
        return _clone

class Problem(object):
    """
    The base class for describing a problem for
    the schettino system.
    """

    persons = ()
    """ The persons to be allocated to the tasks
    this are the names for the domain ranges """

    persons_count = 0
    """ The number of persons available to be scheduled
    in the current problem """

    timetables = ()
    """ The sequence of timetable that are meant to be
    considered for the current schedule in case no
    timetables are set the schedule is considered detached """

    bitmap = ()
    """ The base bitmap that controls the scheduling
    of the task in a per time basis """

    rules = ()
    """ The set of rules to be executed on the verify
    method this way it's possible to control what
    kind of verification are done """

    days_off = ()
    """ The days that may be used to provide a day off
    to a target person, these are indexes relative to
    monday (zero based) """

    timetables_r = {}
    """ The map containing the various timetables, these
    are simple bitmap sequences with the definitions """

    persons_r = {}
    """ The map containing the series of "extra" rules
    to be applied to a certain variable index (person) """

    number_days = 0
    """ The number of days in the problem, this value
    is previously calculated for performance reasons """

    number_hours = 0
    """ The number of hours in the problem, this value
    is previously calculated for performance reasons """

    number_items = 0
    """ The number of items available in the bitmap
    for processing """

    solution = None
    """ The reference to the current solution, this should
    be the reference to the solution created by the last
    ran solving """

    instrumentation = {}
    """ The map containing the various debug values for
    instrumentation of the result, this values are of crucial
    importance in the debugging stage """

    delta = 0
    """ The time in milliseconds that took for the last soling
    to execute (useful for benchmark) """

    def __init__(self):
        self.persons_count = len(self.persons)
        self.number_items = self.number_days * self.number_hours
        self.instrumentation = {}
        self.set_rules()

    def set_rules(self, rules = None):
        rules = rules or self.rules

        self._rules = []

        for rule in self.rules:
            method = getattr(self, rule)
            self._rules.append(method)

    def rule_1(self, solution):
        """
        Runs the rules that constrains the execution
        of a task to certain number of hours per day.

        This rule is named - work day time rule.

        @type solution: Solution
        @param solution: The solution to be tested against
        the rule, the contents may be variable.
        """

        # iterates over all the positions available in the current
        # solution so that all the elements are accounted
        for position in xrange(len(solution)):

            # in case the current position refers a start of a day
            # the counter must be reset (new counting)
            if position % self.number_hours == 0: counter = self._list_p()

            # retrieves the current set of items for the solution item
            # in the current position
            items = solution[position]

            # iterates over all the items and adds a counting value for
            # each of them (to count their hours)
            for item in items:
                if not item == -1: counter[item] += 1

            # in case the next position refers the start of a new day
            # (this is the final day position) and so the items must be
            # counted for correct values
            if (position + 1) % self.number_hours == 0:

                # iterates over the counter value to validate the
                # counts against the working hours week
                for index in range(len(counter)):
                    # retrieves the current count value from the counter
                    # this is the number of times an item has been used
                    # during the course of the current day
                    count = counter[index]

                    # in case the  count is not set of the count is less than
                    # the maximum allowed for the current items index continue
                    # otherwise adds a failure and returns immediately in error
                    if count == 0 or count <= self.get_max_hours_day(index): continue
                    self._add_failure(self.rule_1.__name__)
                    return False

        # iterates over the counter value to validate the
        # counts against the working hours week
        for index in range(len(counter)):
            # retrieves the current count value from the counter
            # this is the number of times an item has been used
            # during the course of the current day
            count = counter[index]

            # in case the  count is not set of the count is less than
            # the maximum allowed for the current items index continue
            # otherwise adds a failure and returns immediately in error
            if count == 0 or count <= self.get_max_hours_day(index): continue
            self._add_failure(self.rule_1.__name__)
            return False

        # returns valid because the rule validation
        # process has passed with success
        return True

    def rule_2(self, solution):
        counter = self._list_p()

        for position in xrange(len(solution)):
            if position % self.number_hours == 0: _counter = self._list_p()

            items = solution[position]

            for item in items:
                if not item == -1: _counter[item] += 1

            if (position + 1) % self.number_hours == 0:
                index = 0
                for count in _counter:
                    if count > 0: counter[index] += 1
                    index += 1

        for count in counter:
            if count <= self.max_days_week: continue
            self._add_failure(self.rule_2.__name__)
            return False

        return True

    def verify(self, solution = None):
        # tries to retrieve the appropriate solution
        # (defaulting to the current set solution)
        solution = self._get_solution(solution)

        for rule in self._rules:
            result = rule(solution)
            if result: continue
            return result

        # returns valid, because all the rules have
        # passed successfully
        return True

    def state(self, solution = None):
        # tries to retrieve the appropriate solution
        # (defaulting to the current set solution)
        solution = self._get_solution(solution)

        # retrieves the current values for the meta information
        # on the solution state, this is considered to be the state
        # of the solution and so these are the values to change
        day = solution.meta.get("day", 0)
        day_sets = solution.meta.get("day_sets", self._day_sets_p())
        currents = solution.meta.get("currents", {})
        week = solution.meta.get("week", self._list_p())
        week_mask = solution.meta.get("week_mask", self._list_p())

        position = len(solution)
        _day = position / self.number_hours
        if not _day == day:
            # must create the model for the various day sets
            # to be created (this is going to be multiplied)
            day_set = range(self.persons_count)

            removal = []
            for item in day_set:
                week_count = self._week_count(week_mask[item])
                if week_count < self.max_days_week: continue
                removal.append(item)

            # iterates over all the items to be removed and
            # removes them from the day set (garbage collection)
            for item in removal: day_set.remove(item)

            # creates the various day sets to be used based on
            # the model day set that was just created
            day_sets = [copy.copy(day_set) for _index in xrange(MAX_ALLOCATIONS)]

            # creates a new map for the maintenance of the ranges
            # for the current items
            currents = {}

        # retrieves the set of items just set in the current solution
        # (this should be the last item of the solution)
        items = solution[-1]

        # iterates over all the currents values to house keep
        # them removing the ones that are no longer in use
        for key in currents.keys():
            if key in items: continue
            del currents[key]

        # iterates over all the items to update their problem oriented
        # counting values to the must up to date versions
        for item in items:
            # in case the item is not valid returns immediately
            # (not going to update the state for invalid values)
            if item == -1: continue

            # in case the current day has not been already touched
            # for the current item must do so
            if not week_mask[item] & 1 << _day:
                week[item] += 1
                week_mask[item] |= 1 << _day

            # retrieves the must updates version of the items range from the
            # currents map and increments it with one more value, in case the
            # range does not exists (first time) creates one
            _range = currents.get(item, 0)
            _range += 1
            currents[item] = _range

            # in case the maximum range has been reached
            # for the current item it must be removed from
            # the day sets (element reached starvation)
            if _range == self.get_max_hours_day(item):
                for day_set in day_sets: day_set.remove(item)

        # updates the meta information map with the must up to
        # date values so that they can be used latter for performance
        solution.meta["day"] = _day
        solution.meta["day_sets"] = day_sets
        solution.meta["currents"] = currents
        solution.meta["week"] = week
        solution.meta["week_mask"] = week_mask

    def get_ordered(self, solution = None):
        # tries to retrieve the appropriate solution
        # (defaulting to the current set solution)
        solution = self._get_solution(solution)

        # retrieves the various meta information attributes from the
        # solution structure to be able to used them in the order sequence
        # processing that will occur in this method
        day_sets = solution.meta.get("day_sets", self._day_sets_p())
        currents = solution.meta.get("currents", {})
        week = solution.meta.get("week", self._list_p())

        # retrieves the current (next) position as the
        # size of the solution sequence
        position = len(solution)

        # retrieves the current set of places for the position, this
        # value should be a map associating the timetable id with the
        # type of place for the position
        places = self.get_places(position)
        places_count = len(places)
        print "%d -> %s" % (position, places)

        # creates the list that will hold the various ordered items
        # as tuples of possible index solutions
        ordered = []

        # iterates over the range of places to be attributed for the
        # next position in solution
        for index in xrange(places_count):
            # retrieves the current place for the place count index
            # in iteration, going to be used to retrieve previous index
            place = places[index]

            # tries to retrieve the previous index associated with the
            # current place (same timetable) this allows the same person
            # to be allocated contiguously to a timetable, in case an
            # index is found the current ordered item is simple and the
            # iteration should continue immediately
            index_p = self._get_index_p(solution, place, position)
            if not index_p == None:
                _ordered = [index_p]
                ordered.append(_ordered)
                continue

            # unpacks the place into the timetable (name) and the
            # type of place and then uses the timetable to retrieve
            # the size of the current timetable chunk in evaluation
            # in order to be able to validate availability
            timetable, _type = place
            size_t = self._get_size_t(timetable, position)

            # retrieves the current day set taking into account
            # the current index in iteration
            day_set = day_sets[index]

            # starts the list that will hold the various items to be remove
            # from the day set, the items to be removed correspond to invalid
            # values that would corrupt the solution
            removal = set()

            # starts the current ordered item as a "simple" copy of the day
            # set (default and complete solution)
            _ordered = day_set

            # iterates over the ordered to check if there is a complete valid
            # person available for the task, in case it's not removes the index
            for index in _ordered:
                # retrieves the bitmap for the current index and checks
                # for the timetable size if there is availability in
                # in the bitmap for such positions, otherwise adds the
                # index to the list of removal elements
                bitmap = self.get_bitmap(index)
                for _index in range(size_t):
                    if bitmap[position + _index]: continue
                    removal.add(index)
                    break

                # retrieves the range for the current index defaulting
                # to zero in case no range is found, then validates
                # if the current range plus the size of the timetable
                # chunk is less that the maximum number of hours for
                # the work (have enough hours available)
                _range = currents.get(index) or 0
                if _range + size_t > self.get_max_hours_day(index):
                    removal.add(index)

                # retrieves the timetables for the index in the current
                # position and checks if the timetable for the current
                # place in question exists in such position and index
                # (person can work for that timetable today)
                timetables = self.get_timetables(position, index)
                if not timetable in timetables: removal.add(index)

            # in case the removal list is not empty there are
            # items to be removed so the ordered list must be
            # clones and the removal items removed
            if removal:
                _ordered = copy.copy(_ordered)
                for index in removal: _ordered.remove(index)

            def index_sort(first, second):
                # retrieves the priority values for both
                # the first and second indexes (persons)
                _name, first_p = self.persons[first]
                _name, second_p = self.persons[second]

                # retrieves the week occurrence count values
                # for both the first and second indexes (persons)
                first_w = week[first]
                second_w = week[second]

                # creates the comparison tuples for both the
                # first and second elements and then returns the
                # result of the tuple comparison (sequence comparison)
                first_t = (first_p, first_w)
                second_t = (second_p, second_w)
                return cmp(first_t, second_t)

            # sorts the partial ordered list using the composite
            # index sorter (tuple priority sorting)
            _ordered.sort(index_sort)

            # adds the current ordered item to the list of ordered values to be
            # used in the next iteration
            ordered.append(_ordered)

        # "calculates" the various linear solution for the ordered set
        # this should create the various permutations of values for the
        # next iteration, the order of priority should be preserved
        ordered = self._linear(*ordered)

        # returns the list of ordered elements for the places to be assigned
        # in the subsequent iteration of allocation
        return ordered

    def get_places(self, position):
        # in case the requested position overflows the current problem
        # (bigger than the number of items) returns an empty tuple (fallback)
        if position >= self.number_items: return ()

        # starts the list that will hold the various places that may be
        # fulfilled for the requested position
        places = []

        # retrieves the current day from the position and uses it to retrieve
        # the series of timetable available for the requested day
        day = position / self.number_hours
        timetables = self.timetables[day]

        # iterates over all the timetables to filter the ones that contain a
        # valid hour for the requested position, for this value an item will
        # be added to the places list indicating the requested action
        for timetable in timetables:
            _timetable = self.timetables_r[timetable]
            value = _timetable[position]
            if value == 0: continue
            places.append((timetable, value))

        # returns the tuple containing the various places (values) indexed by
        # the timetable that originated them
        return places

    def get_bitmap(self, index):
        id, _priority = self.persons[index]
        rules = self.persons_r.get(id, {})
        bitmap = rules.get("bitmap", None)
        if not bitmap: return self.bitmap

        _bitmap = []

        for index in xrange(self.number_items):
            first = self.bitmap[index]
            second = bitmap[index]
            final = first and second or 0
            _bitmap.append(final)

        return _bitmap

    def get_max_hours_day(self, index):
        id, _priority = self.persons[index]
        rules = self.persons_r.get(id, {})
        max_hours_day = rules.get("max_hours_day", None)
        if not max_hours_day: return self.max_hours_day
        return max_hours_day

    def get_timetables(self, position, index):
        day = position / self.number_hours
        id, _priority = self.persons[index]
        rules = self.persons_r.get(id, {})
        timetables = rules.get("timetables", None)
        if not timetables: return self.timetables[day]

        _timetables = [value for value in self.timetables[day] if value in timetables[day]]
        return _timetables

    def get_structure(self):
        # in case there is no solution it's impossible
        # to "calculate" the problem structure, returns
        # immediately with an invalid value
        if not self.solution: return None

        # starts the initial value for the structure (treated
        # solution value) and for the day and item
        structure = []
        day = {}
        item = {}

        # iterates over the range of the solution to create the various
        # items that describe a task in a contiguous approach
        for position in range(len(self.solution)):
            # retrieves the current day relative position, this is simply
            # the modules of the position with the number of hours in a day
            position_d = position % self.number_hours

            # in case the current position modulus represents a day
            # transition must reset all the structures used in the
            # structure creation (day cleanup)
            if position_d == 0:
                item = {}
                day = {}
                structure.append(day)

            # retrieve the values (indexes) from the solution these are
            # the indexes allocated to the solution at this time (position)
            values = self.solution[position]

            # creates a new map for the items in the current position of the
            # day then sets this map in the day (for reference)
            position_m = {}
            day[position_d] = position_m

            # iterates over all the value in the solution to creates the
            # appropriate representation for them in the day
            for value in values:
                # uses it to retrieve the appropriate string value using
                # the problem definition for the resolution process
                id, _priority = self.persons[value]
                person = self.persons_r[id]
                name = person.get("name", id)
                value_s = value == -1 and "&nbsp;" or self._shorten_name(name)

                # tries to retrieve the item for the current value in the
                # current position map in case it succeeds this value is
                # used otherwise a new item is used and set in the map
                # representing the current position in the day
                position_p = day.get(position_d - 1, {})
                item = position_p.get(value, None)
                if item:
                    item["size"] += 1
                else:
                    item = {
                        "index" : value,
                        "name" : value_s,
                        "position" : position,
                        "size" : 1,
                        "width" : -1,
                        "position_d" : -1
                    }

                position_m[value] = item

        # creates the list of items that will be used to store
        # the already processed items and will avoid duplicated
        # items in the final structure (redundancy removal)
        _items = []

        # iterates over all the days in the structure to trigger
        # the global item "processing"
        for day in structure:

            # iterates over all the positions in the day to process
            # all the items contained in them
            for position, position_m in day.items():

                # creates the list that will hold the various index
                # values to the items to be removed at the end of
                # the current iteration
                removal = []

                # iterates over all the items in the position map
                # to process them accordingly
                for index, item in position_m.items():

                    # in case the item already exists in the list of
                    # "processed" items must be removed (redundancy removal)
                    if item in _items:
                        # adds the index element to the list of items
                        # to be removed at the end of iteration
                        removal.append(index)

                    # otherwise it's the first "view" and a processing
                    # step must occur in the item
                    else:
                        # retrieves the current item size to be able
                        # to percolate over the "future" (next) elements
                        size = item["size"]

                        # start the item's width and position with the
                        # default values (original values)
                        width = 1
                        position_d = 1

                        # iterates over the size range to be able to inspect
                        # the next items in the day and make assumptions on the
                        # with and position
                        for _index in xrange(size):
                            # retrieves the current (future) position and retrieves
                            # the length of it to set it as the with in case it's
                            # greater than the currently set width
                            position_f = day.get(position + _index)
                            position_length = len(position_f)
                            width = position_length > width and position_length or width

                            # iterates over all the items in the future position
                            # to compare their widths and position with the current
                            for _index_f, item_f in position_f.items():
                                # retrieves both the future with and position and compares
                                # them with the currently set ones in case their are either
                                # greater (for with) or lower or equal (for position) a
                                # value substitution occurs
                                _width = item_f["width"]
                                _position_d = item_f["position_d"]
                                if not _width == -1 and _width > width: width = _width
                                if not _position_d == -1 and _position_d <= position_d:
                                    position_d = _position_d + 1

                        # updates the item's values with the newly
                        # computed ones and adds the item to the
                        # list of "processed" items
                        item["width"] = width
                        item["position_d"] = position_d
                        _items.append(item)

                # iterates over all the index in the removal
                # list and removes the values for those indexes
                # in the position map
                for index in removal: del position_m[index]

        # returns the final processed structure containing
        # the transformed items organized by days and
        # by positions (internal day positions, modulus)
        return structure

    def get_report(self):
        # initializes the various internal structures for
        # the report to the default (empty) values
        indexes = []
        hours = {}
        days = {}

        # retrieves the structure for the current solution, this
        # the value that is going to be used to construct the report
        structure = self.get_structure()

        # iterates over all the days in the structure to populate
        # the report structures
        for day in structure:

            # iterates over all the items in the day to update
            # the report structure for the items contained
            for _position, items in day.items():

                # iterates over all the items in the current position
                # to update the report structure
                for index, item in items.items():
                    # retrieves the various properties from the
                    # item to be used in the processing
                    size = item["size"]

                    # in case the index is not already present in the
                    # indexes list adds it to the list
                    if not index in indexes: indexes.append(index)

                    # retrieves the various integer updatable values and
                    # sets the values into them
                    _hours = hours.get(index, 0)
                    _days = days.get(index, 0)
                    _hours += size
                    _days += 1

                    # updates the integer values in the appropriates structure
                    # to be able to expose them in report
                    hours[index] = _hours
                    days[index] = _days

        # updates the report map with must up to date values
        # on the various values and returns this value
        report = {
            "indexes" : indexes,
            "hours" : hours,
            "days" : days
        }
        return report

    def print_s(self, solution = None):
        solution = self._get_solution(solution)
        if not solution: raise RuntimeError("No solution is available in problem")

        for index in xrange(len(solution)):
            if index % self.number_hours == 0: print "day %d ::" % (index / self.number_hours),

            hour = solution[index]
            person = hour > -1 and self.persons[hour] or "undefined"
            print "%s, " % person,

            if (index + 1) % self.number_hours == 0: print ""

    def _get_index_p(self, solution, place, position):
        """
        Retrieves the index value (person index) for the previous
        position relative to the provided one in the same timetable
        (value extracted from the place tuple).

        This method is useful to check the person that is currently
        allocated to the timetable in the place.

        @type solution: Solution
        @param solution: The solution to be used in the checking of
        the previous index (reference value).
        @type place: Tuple
        @param place: The place tuple to extract the timetable that
        will be used for the computation of the previous index.
        @type position: int
        @param position: The position index that will be used to
        calculate the previous index for computation.
        @rtype: int
        @return: The previous index for the timetable described
        in the provided place and for the provided position.
        """

        # in case the requested position is not valid returns
        # immediately an invalid value
        if position < 0: return None

        # unpacks the place into the timetable (name) an the
        # type of the place and then retrieves the
        timetable, _type = place
        places_p = self.get_places(position - 1)

        # starts the index reference values, this are the values
        # that are going to be used during the iteration cycle
        # for the saving of the relative index values
        index = 0
        _index = None

        # iterates over all the previous places to check for
        # the correct timetable and to retrieve the correct relative
        # index value for the timetable in the items sequence
        for place_p in places_p:
            # extras the previous place tuple into the timetable
            # and the type and checks for a match in such case
            # saves the current (relative) index value and breaks
            _timetable, __type = place_p
            if timetable == _timetable:
                _index = index
                break

            # increments the index value (iteration cycle)
            index += 1

        # in case the relative index reference is not defined return
        # an invalid value (timetable is starting) otherwise extracts
        # the current item from the solution and returns the index
        # relative value from the sequence of items
        if _index == None: return None
        items = solution[position - 1]
        return items[_index]

    def _get_size_t(self, timetable_n, position):
        """
        Retrieves the size of the timetable sequence starting
        at the provided position.

        The position is required because there can be multiple
        sequences in a single timetable.

        @type timetable_n: String
        @param timetable_n: The name (id) of the timetable to
        be used for the calculus of the sequence size.
        @type position: int
        @param position: The (start) position to be used in the
        calculus of the sequence size.
        @rtype: int
        @return: The size for the timetable sequence starting at
        the provided position.
        """

        # tries to retrieve the timetable (rules) using the provided
        # timetable name (id), default to invalid and returns immediately
        # in case no timetable is found
        timetable = self.timetables_r.get(timetable_n, None)
        if not timetable: return 0

        # starts the index value to zero, this value will act as a
        # counter during the loop over the timetable
        index = 0

        # iterates continuously to the count the range of the current
        # sequence, stopping either at a zero value or at the end of
        # the timetable definition
        while True:
            # in case the timetable end has been reached breaks
            # otherwise retrieves the current timetable value and
            # in case it's zero (no value) and end of sequence has
            # been reached and so breaks
            if position + index == len(timetable): break
            value = timetable[position + index]
            if value == 0: break
            index += 1

        # returns the calculated index as the length of the sequence
        # of the timetable starting at the provided position
        return index

    def _add_failure(self, name):
        failures = self.instrumentation.get("failures", {})
        failure = failures.get(name, 0)
        failures[name] = failure + 1
        self.instrumentation["failures"] = failures

    def _get_solution(self, solution):
        return solution == None and self.solution or solution

    def _week_count(self, week_mask):
        # starts the count variable that will hold the number
        # of "occupied" days in the week defined by the mask
        count = 0

        # iterates over the range of days in the week to count
        # the number of days that are filled
        for i in range(7):
            # in case the mask is not active for the current day
            # bitwise and operation continues the loop, otherwise
            # increment the count variable (one more day found)
            if not week_mask & 1 << i: continue
            count += 1

        # returns the count variable, that contains the number
        # of days counted for the provided week mask
        return count

    def _shorten_name(self, name):
        """
        Shortens the provided name so that the first name
        is shown in the complete form and the last name is
        provided only with the first letter.

        @type name: String
        @param name: The name to be shortened.
        @rtype: String
        @return: The shortened version of the provided name.
        """

        parts = name.split(" ")
        parts_length = len(parts)
        if parts_length == 1: return name
        first = parts[0]
        last = parts[-1]

        return first + " " + last[0] + "."

    def _day_sets_p(self):
        """
        Creates a new list to hold a series of sets for a day
        this is useful to maintain a list of values that are
        possible options for a given task for a day.

        @rtype: List
        @return: The generated day sets structure for the
        current problem.
        """

        return [range(self.persons_count) for _index in xrange(MAX_ALLOCATIONS)]

    def _list_p(self):
        """
        Creates a new empty list for the currently defined
        person domain problem.

        This is a utility function to be used to shorten the
        time used to create a list of counters for persons.

        @rtype: List
        @return: The newly created zeroed list of counters
        for the various persons.
        """

        return [0 for _value in range(self.persons_count)]

    def _linear(self, *args):
        """
        Runs a series of permutation on the provided sequence
        of elements, so that the returned value is the various
        combinations of values that may possible generate a
        valid solution.

        @rtype: List
        @return: The generated (valid) sequence containing the
        permutations of valuers that can possible generate a
        valid solution.
        """

        # creates the list that will hold the various permutation
        # items generated from the linearization
        items = []

        def callback(item):
            items.append(item)

        # runs the linear process using the provided arguments set
        # and then returns the resulting items list to the caller
        self.__linear([], args, callback)
        return items

    def __linear(self, current, remaining, callback):
        # in case there are no more items in the remaining
        # list the callback must be called and the recursion
        # must be terminated by returning immediately
        if not remaining:
            callback and callback(current)
            return

        # retrieves the head and the tail components of the
        # remaining set to be used in the iteration
        head = remaining[0]
        tail = remaining[1:]

        # iterates over all the element of the head component
        # and runs the linear process, but only in case the
        # element does not already exists in the current list
        # (should avoid duplicated elements in solution)
        for element in head:
            if element in current: continue
            self.__linear(current + [element], tail, callback)
