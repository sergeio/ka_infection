# Infection

### Requirements:

  * virtualenv 1.7+
  * Python 3

## Setup

If you don't want to install Docker, you can skip steps 1-3,6 by manually
bringing up a MongoDB instance on the default port (localhost:27017).

 1. [Install docker](http://docs.docker.com/installation/)
 2. [Install docker-compose](http://docs.docker.com/compose/install/)
 3. Optionally [add your user](https://docs.docker.com/installation/ubuntulinux/#giving-non-root-access)
    to the `docker` group so you can omit `sudo` before every docker command.
 4. `$ git clone https://github.com/sergeio/ka_infection.git`
 5. `$ cd ka_infection`
 6. `$ sudo docker-compose up -d`
    * This step will take a while the first time as Docker has to download all
      the base images (ubuntu, mongo, ...)
    * If you omit the `-d` flag, you can watch mongo boot up, otherwise, you'll
      want `sudo docker-compose logs` to check the output of the container.
 7. `$ make dependencies` should set up the python virtualenv and install python
    dependencies.
 8. `$ make test` runs the tests.


`sudo docker-compose ps` shows local running containers:
```
code/ka_infection$ sudo docker-compose ps
      Name                     Command               State            Ports
-------------------------------------------------------------------------------------
kainfection_db1_1   /entrypoint.sh /bin/sh -c  ...   Up      0.0.0.0:27017->27017/tcp
```

## The algorithm

### Total Infection

I decided to do this via a sort of batch flood-fill.  Starting with a given
user, we fetch that user's connections from the database, and then repeat the
process until there are no more unseen connections.  The slight twist is that
instead of doing this one user at a time, I fetch 1000 of the users I know
about per query.

So if the initial user is connected to 10 other users (by coaching them or
being coached by them), next iteration, we get all 10 of those users'
connections, which greatly cuts down on the total amount of DB roundtrips.

DB index on `user_id`.


#### Performance

For well-connected datasets, an infection of a 100,000-user connected-component
takes 25 seconds using MongoDB inside a docker image on a 9 year old laptop.  A
production DB might be even faster.

#### Optimization

If you denormalize data, and add a `component_id` number on every user, and
maintain these groups when updating user relationships, this problem becomes
fairly easy -- doing a full infection is two DB commands:

 1. Get the initial user's `component_id`.
 2. Update all users with matching `component_id` with the new site-version.

DB index on `component_id`.

This would also eliminate the race condition between finding all the users in
the connected component and performing the update.

If you are super into denormalization, and your applications are read-heavy,
you can get this down to one query.

Alas, people don't always like it when I solve their problems assuming they
store their data in a very specific way, making the problem trivial.  So I
opted to solve it in a more "traditional" way, and add this text to be a
talking point.

### Partial Infection

This is an extension of `total_infection`.  The idea is to perform total
infections on random connected components until the sum of users in all
selected connected components is within the desired range.

If we overshoot, and go from marking-for-update less than the minimum required
amount of users, to more than the maximum, raise an exception and abort the
update.

Assuming the typical connected component size is much smaller than the allowed
range `max_num_to_infect - min_num_to_infect`, this works well.

Again, we could benefit from precomputing the connected-component-id when users
become mentors / mentees, or when they close their account, etc...  But
assuming this was the case felt a bit like cheating.

## Extras

I looked into doing exact infections.  I ran out of time before I could
actually implement it, but despite all the red flags, I think it could actually
be doable.

Let's assume that we keep track of all the connected components and their sizes
and have a compound index on `component_size + component_id`.  Getting the
information we want (`component_size` and `component_id`) would then not even
need to hit the actual database -- only the index.  I've measured such queries
to be 67 times faster than standard indexed queries.

Now, we just have what looks like an np-complete problem.

**But wait!!** For lists of positive, bounded integers, the [subset sum
problem](https://en.wikipedia.org/wiki/Subset_sum_problem) has a **linear
solution**.

The algorithm is frankly way too crazy to implement legibly within the allotted
time, but I found a completely illegible (I think) implementation online, and
did some benchmarks.  (Included in `subsequence_sum.py`)

CPython was way too slow, but PyPy performed 40x faster.

On my 9 year old laptop, I was able to run this problem with 5000 connected
components in 3.7s.

Assuming your data has something like 1 million connected components, and
linear scaling (which I confirmed for data-sets of 100 - 5000 connected
components), we could do an exact infection in 12 minutes and 100 - 200 GB RAM
minimum.  Again, production servers are probably faster than my 9 year old
laptop.

Reading over the algorithm a bit, I think we could make further optimizations
if you have many isolated users (no mentors / mentees).

Of course, this is overkill.  Nobody needs to infect *exactly* 837410 users.
But it's fun to see it just might be possible.
