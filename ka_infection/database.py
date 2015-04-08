"""Database communication layer."""
from itertools import chain

from pymongo import MongoClient


CLIENT = MongoClient('localhost', 27017)
COLLECTION = CLIENT.test.users


def get_mentors_and_mentees(uids):
    """Return all the connections of students with matching `uids`.

    Connections in this context are "coaches" and "coached_by".

    Returns a set of UIDs.

    """
    docs = COLLECTION.find(
        {'uid': {'$in': uids}},
        fields={'coaches': True, 'coached_by': True, '_id': False})
    if not docs:
        return []
    docs = list(docs)
    mentees = [l.get('coaches', []) for l in docs]
    mentors = [l.get('coached_by', []) for l in docs]
    connections = mentees + mentors
    return set(chain(*connections))


def get_unmarked_user_id(marked_users):
    """Get a UID from the DB that is not one of `marked_users`.

    Return `None` if no such user exists.

    """
    marked_users = list(marked_users)
    doc = COLLECTION.find_one({'uid': {'$nin': marked_users}})
    if not doc:
        return None
    return doc.get('uid')


def update_users_with_site_version(users, site_version):
    """Update the `site_version` of all users with matching UIDs."""
    COLLECTION.update(
        spec={'uid': {'$in': users}},
        document={'$set': {'site_version': site_version}},
        multi=True)
