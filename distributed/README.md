# README

This is an attempt at a simple distributed app; specifically, a piece of data
which multiple processes can observe and edit at once.

To simplify things, the core piece of data is an integer, which the user can
set.

A more complex example would have a larger piece of data which would have a
structure and could be extended or reduced dynamically.

To achieve the goals, each component in the system is considered to be
independent, maintaining a local copy of the data.
Each component can then communicate changes through a versioning protocol,
broadcasting changes to all other clients.

Technically versioning is probably not required.
However, it allows use of a single action - a "publish" broadcast - where every
node listens in via `udp.py`.
If a node hears a "publish" with an older version than it has, it will respond
by publishing the current version it owns.

The versioning is via a variation on Lambert logical clocks, which are
imperfect in general but good enough for a small number of clients.

