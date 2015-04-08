"""Shared utilities for tests."""
from collections import defaultdict
from itertools import chain

from unittest import TestCase

from ka_infection.database import COLLECTION


class _BaseDbInfectionTestCase(TestCase):

    def setUp(self):
        self.set_up_db()
        self.returned = self.execute()

    def tearDown(self):
        COLLECTION.drop_indexes()
        COLLECTION.remove(w=1)

    def set_up_db(self):
        self.tearDown()
        COLLECTION.ensure_index('uid', unique=True, background=False)
        COLLECTION.ensure_index('site_version', unique=False, background=False)

        # Build mentee -> mentors connections map
        reverse_connections = defaultdict(list)
        for mentor, mentees in self.connection_map.items():
            for mentee in mentees:
                reverse_connections[mentee].append(mentor)

        # Create docs of users that are mentors
        mentors = [{
            'uid': uid,
            'coaches': mentees,
            'coached_by': reverse_connections[uid],
            'version': 1,
        } for uid, mentees in self.connection_map.items()]

        # Create docs of users that are only mentees
        mentees_only = [{'uid': uid, 'coached_by': mentors, 'version': 1}
                        for uid, mentors in reverse_connections.items()
                        if uid not in self.connection_map]

        COLLECTION.insert(mentors + mentees_only, w=1)
