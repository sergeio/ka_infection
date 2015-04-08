"""Integration tests for the database interaction layer.

See tests/integration/test_infection.py for an annotated test sample.

"""
from ka_infection.database import (
    COLLECTION,
    get_mentors_and_mentees,
    get_unmarked_user_id,
    update_users_with_site_version,
)
from tests.test_utils import _BaseDbInfectionTestCase


####
##
## get_mentors_and_mentees
##
####

class _BaseGettingMentors(_BaseDbInfectionTestCase):

    def execute(self):
        return get_mentors_and_mentees(self.uids)

    def test_returns_correct_value(self):
        self.assertEqual(self.returned, self.expected_return)


class GetMenteeFromMentor(_BaseGettingMentors):

    uids = [1]
    connection_map = {1: [2], 3: [4]}
    expected_return = {2}


class GetMentorFromMentee(_BaseGettingMentors):

    uids = [2]
    connection_map = {1: [2], 3: [4]}
    expected_return = {1}


class GetMultipleMentorMentees(_BaseGettingMentors):

    uids = [2, 3]
    connection_map = {1: [2], 3: [4]}
    expected_return = {1, 4}


class WhenUserIsMentorAndMentee(_BaseGettingMentors):

    uids = [3]
    connection_map = {1: [3], 2: [3]}
    expected_return = {1, 2}


# Normally there would be more tests here, but from the assignment description,
# it sounds like you don't need things to be perfect, just whatever is
# reasonable in the space of a few hours.

####
##
## get_unmarked_user_id
##
####

####
##
## update_users_with_site_version
##
####
