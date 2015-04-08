"""Integration tests for infection functions.

Test classes are structured as follows:

```
class SampleInfection(_TotalInfectionTestCase):

    start_uid = 1                     # Start the infection with uid1
    connection_map = {1: [2], 3: [4]} # uid1 coaches uid2 and uid3 coaches uid4
                                      # uid2 is coached by uid1, and so on...
    expected_updated_users = {1, 2}   # uid1 and uid2 should be infected
```

The tests create the appropriate user documents, insert them into the database,
perform the infection, and query to verify the expected users were infected.

"""
from ka_infection.database import COLLECTION
from ka_infection.infection import (
    get_all_connected_users,
    partial_infection,
    total_infection,
)
from tests.test_utils import _BaseDbInfectionTestCase


####
##
## total_infection
##
####

class _TotalInfectionTestCase(_BaseDbInfectionTestCase):

    new_version = 2

    def execute(self):
        return total_infection(self.start_uid, self.new_version)

    def test_updated_correct_elements(self):
        docs = list(COLLECTION.find({'site_version': self.new_version}))
        updated_users = set([d.get('uid') for d in docs])
        self.assertEqual(updated_users, self.expected_updated_users)


class EasyInfection(_TotalInfectionTestCase):

    start_uid = 1
    connection_map = {1: [2], 3: [4]}
    expected_updated_users = {1, 2}


class InfectIsolatedUser(_TotalInfectionTestCase):

    start_uid = 1
    connection_map = {1: [], 3: [4]}
    expected_updated_users = {1}


class InfectNonexistantUser(_TotalInfectionTestCase):

    start_uid = 0
    connection_map = {1: [2]}
    expected_updated_users = set()


class TestBigUpdateOperation(_TotalInfectionTestCase):

    def make_wheel_shaped_connection_map(levels):
        """Make map of users where every x-digit uid is connected to ten
        x+1 digit uids.

        `levels` is equivalent to "max digits uid to create".
        levels = 2 will create 1 and 2 digit uids
        levels = 3 will create 1, 2, and 3 digit uids
        ...

        """
        connection_map = {0: [i for i in range(1, 10)]}
        for _ in range(levels - 1):
            update_map = {}
            # Add new circle of users
            for v in connection_map.values():
                for uid in v:
                    if uid not in connection_map.keys():
                        update_map[uid] = [uid * 10 + j for j in range(10)]
            connection_map.update(update_map)
        return connection_map

    start_uid = 0
    levels = 4
    connection_map = make_wheel_shaped_connection_map(levels)
    expected_updated_users = set(range(10 ** levels))


####
##
## partial_infection
##
####

class _PartialInfectionTestCase(_BaseDbInfectionTestCase):

    new_version = 2

    def execute(self):
        return partial_infection(
            self.min_num_to_infect,
            self.max_num_to_infect,
            self.new_version)

    def test_updated_correct_elements(self):
        docs = list(COLLECTION.find({'site_version': self.new_version}))
        updated_users = set([d.get('uid') for d in docs])
        self.assertEqual(updated_users, self.expected_updated_users)


class PartialPartialInfection(_PartialInfectionTestCase):

    min_num_to_infect = 1
    max_num_to_infect = 10
    connection_map = {1: [2], 3: [4]}
    expected_updated_users = {1, 2}


class FullPartialInfection(_PartialInfectionTestCase):

    min_num_to_infect = 3
    max_num_to_infect = 10
    connection_map = {1: [2], 3: [4]}
    expected_updated_users = {1, 2, 3, 4}


class ManyUserPartialInfection(_PartialInfectionTestCase):

    min_num_to_infect = 100
    max_num_to_infect = 2000
    connection_map = {
        i: [i + 1, i + 2, i + 3, i + 4, i + 5] for i in range(1, 1000)}
    second_connected_component = {
        i: [i + 1, i + 2, i + 3, i + 4, i + 5] for i in range(2000, 3000)}
    connection_map.update(second_connected_component)
    expected_updated_users = set(range(1, 1005))


class CannotInfectDesiredUserRange(_BaseDbInfectionTestCase):

    new_version = 2
    min_num_to_infect = 5
    max_num_to_infect = 6
    connection_map = {
        1: [2],
        3: [4],
        5: [6, 7],
    }
    expected_updated_users = set()

    def execute(self):
        pass

    def test_raises_exception(self):
        self.assertRaises(
            Exception,
            partial_infection,
            self.min_num_to_infect,
            self.max_num_to_infect,
            self.new_version)

    def test_does_not_update(self):
        docs = list(COLLECTION.find({'site_version': self.new_version}))
        updated_users = set([d.get('uid') for d in docs])
        self.assertEqual(updated_users, self.expected_updated_users)


####
##
## get_all_connected_users
##
####

class _ConnectedUserBaseCase(_BaseDbInfectionTestCase):

    def execute(self):
        return get_all_connected_users(self.start_uid)

    def test_returned_correct(self):
        self.assertEqual(self.returned, self.expected_return)


class TestEasy(_ConnectedUserBaseCase):

    start_uid = 1
    connection_map = {1: [2, 3]}
    expected_return = {1, 2, 3}


class TestAThousandUserComponent(_ConnectedUserBaseCase):

    start_uid = 1
    connection_map = {
        i: [i + 1, i + 2, i + 3, i + 4, i + 5] for i in range(1, 1000)}
    expected_return = set(range(1, 1005))


class TestDisconnected(_ConnectedUserBaseCase):

    start_uid = 1
    connection_map = {1: [2], 3: [4]}
    expected_return = {1, 2}
