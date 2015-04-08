"""Functions to update the site version of connected components of users.

Connections between users are defined by the 'coaches' and 'coached_by'
relationships.

User documents are assumed to look like the following:
```
{
    'uid': int,
    'coaches': [int],     # List of uids
    'coached_by': [int],  # List of uids
    'version': int,
}
```

"""
from collections import deque

from ka_infection.database import (
    get_mentors_and_mentees,
    get_unmarked_user_id,
    update_users_with_site_version,
)


def total_infection(start, version):
    """Set site_version of all users connected to `start` to `version`."""
    users_to_infect = list(get_all_connected_users(start))
    update_users_with_site_version(users_to_infect, version)


def partial_infection(min_num_to_infect, max_num_to_infect, version):
    """Set `site_version` of users in multiple connected components.

    The amount of users updated should fall in the specified range by adding
    more connected components until the number of users to update falls within
    range.

    If we overshoot, and mark more users than we want to update, raise an
    Exception.

    """
    users_to_infect = set()
    while len(users_to_infect) < min_num_to_infect:
        start_uid = get_unmarked_user_id(users_to_infect)
        if not start_uid:
            break
        new_connected_component = get_all_connected_users(start_uid)
        users_to_infect.update(new_connected_component)

    if len(users_to_infect) > max_num_to_infect:
        raise Exception('Selected too many users to update.')

    users_to_infect = list(users_to_infect)
    update_users_with_site_version(users_to_infect, version)


def get_all_connected_users(start, batch_size=1000):
    """Get all users connected by any amount of mentor/mentee relationships.

    Performs a "batch" depth-first-search, expanding the frontier by querying
    for `batch_size` elements at a time.

    """
    frontier = deque([start])
    seen = set()

    while len(frontier):
        elements = popn(batch_size, frontier)
        elements = [e for e in elements if e not in seen]
        if elements:
            connected_users = get_mentors_and_mentees(elements)
            frontier.extendleft(connected_users)
            seen.update(elements)

    return seen


def popn(num_elements, queue):
    """Return at most the first `num_elements` elements from the queue."""
    return [queue.pop() for _ in range(min(num_elements, len(queue)))]
