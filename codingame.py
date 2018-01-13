""" CodinGame sponsored contest.

    This looks a lot like a map/dungeon explorer game.
"""

import sys
import math
from random import randint

debug = lambda *args, **kargs: print(*args, **kargs, file=sys.stderr)
action = lambda abcde: print(abcde.upper()) # Actions are one of a, b, c, d, or e

def do_action(args, abcde):
    """ Do an action (actions are one of a, b, c, d, or e)
    
        Apparently a,b,c,d,e allow you to move in 4 directions or hold still;
        hence the coordinates might be helpful here...
        The last coordinates are the coordinates of "our" point.
        a (+x), e (-x), c (-y), d (+y), b does nothing.
        
        We get scores for each new location, bar the first move which doesn't seem
        to matter. Each new location is worth +2 points.
    """
    print(abcde.upper())

def can_move(args, action):
    """ Return true if we can perform the given move.
        Because we don't have any data for e, just return true.
    """
    action_view_map = {'c': 0, 'a': 1, 'd': 2, 'e': 3}
    return action == 'b' or args[-1][action_view_map[action]] == '_'
    
def next_location(args, action, x_depth, y_depth):
    """ Return the location after performing the given action """
    if not can_move(args, action):
        return (args[-1][-2], args[-1][-1])
        
    depths = (x_depth, y_depth)
    action_move_map = {
        'a': (1, 0),
        'b': (0, 0),
        'c': (0, -1),
        'd': (0, 1),
        'e': (-1, 0),
    }
    return tuple([(args[-1][-2+i] + action_move_map[action][i]) % depths[i] for i in range(2)])


def strategy_precalc(args):
    """ Follow a preset strategy (debug only) """
    cmds = ['b'] + ['e']*20 + ['a']*8 + ['c']*22 + ['a']*6 + ['d']*20 + ['b']
    if len(cmds) > loop: # Only preset commands
        do_action(args, cmds[loop])
    else:
        do_action(args, 'b')
        
def strategy_precalc_loop(args):
    """ Follow a preset strategy, looping over a command set (debug only) """
    cmds = ['b'] + ['e']*20 + ['a']*8 + ['c']*22 + ['a']*6 + ['d']*20 + ['b']
    do_action(args, cmds[loop % len(cmds)])

lvl_map = {} # location: type, where type is one of '#' or '_'
def strategy_avoid_ghosts_mapped(args, x_depth, y_depth):
    """ Least-recently-visited plus a basic ghost avoidance mechanism... """
    
    # Add the most recent locations to the level map.
    x, y = args[-1][-2], args[-1][-1]
    lvl_map[(x, y)] = '_'
    lvl_map[(x, y-1)] = args[-1][0]
    lvl_map[(x+1, y)] = args[-1][1]
    lvl_map[(x, y+1)] = args[-1][2]
    lvl_map[(x-1, y)] = args[-1][3]
    # Include the ghost positions.
    for j in range((len(args[-1])-6)//2):
        lvl_map[(args[-1][j*2 + 4], args[-1][j*2 + 5])] = '_'
    
    visit_time = {}
    for i, arg in enumerate(args):
        # Include ghost last-visit times.
        for j in range((len(arg)-4)//2):
            pos = (arg[j*2 + 4], arg[j*2 + 5])
            visit_time[pos] = i
    
    def ghost_dist(pos, x_depth, y_depth):
        """ Return the minimum distance to a ghost (naive calculation) """
        def abs_dist(pos1, pos2):
            depth = (x_depth, y_depth)
            total = 0
            for i in range(2):
                total += min(abs((pos1[i] - pos2[i]) % depth[i]),
                             abs((pos2[i] - pos1[i]) % depth[i]))
            return total
        ghost_dists = []
        for i in range((len(arg)-6)//2): # Don't include our pos!
            ghost_pos = (arg[i*2 + 4], arg[i*2 + 5])
            ghost_dists.append(abs_dist(pos, ghost_pos))
        return min(ghost_dists)

    opts = {}
    for action in ['a', 'b', 'c', 'd', 'e']:
        next_loc = next_location(args, action, x_depth, y_depth)
        if can_move(args, action) and ghost_dist(next_loc, x_depth, y_depth) >= 2:
            time = visit_time.get(next_loc, -1)
            opts[time] = opts.get(time, []) + [action]
        
    if len(opts) == 0: opts = {-2: 'b'} # Stuck!
    debug(opts)
    final_opts = opts[min(opts.keys())]
    action = final_opts[randint(0, len(final_opts)-1)]
    do_action(args, action)
    
    for x in range(x_depth):
        for y in range(y_depth):
            char = lvl_map.get((x, y), '?')
            for unit in range((len(arg)-4)//2): # Don't include our pos!
                if arg[unit*2 + 4] == x and arg[unit*2 + 5] == y:
                    char = str(unit)
            debug(char, end='')
        debug("")


# Initial set of inputs - the size of the board and the unit counts.
y_depth = int(input())
x_depth = int(input())
unit_count = int(input())

debug("init_args: {}, {}, {}".format(y_depth, x_depth, unit_count))

args = [] # Current list of all arguments
while True:
    input_1 = input()
    input_2 = input()
    input_3 = input()
    input_4 = input()
    args.append([input_1, input_2, input_3, input_4])
    # Coordinates of units.
    for i in range(unit_count):
        args[-1] += [int(j) for j in input().split()]
    
    strategy_avoid_ghosts_mapped(args, x_depth, y_depth)
    
    debug(args[-1])""" CodinGame sponsored contest.

    This looks a lot like a map/dungeon explorer game.
"""

import sys
import math
from random import randint

debug = lambda *args, **kargs: print(*args, **kargs, file=sys.stderr)
action = lambda abcde: print(abcde.upper()) # Actions are one of a, b, c, d, or e

def do_action(args, abcde):
    """ Do an action (actions are one of a, b, c, d, or e)
    
        Apparently a,b,c,d,e allow you to move in 4 directions or hold still;
        hence the coordinates might be helpful here...
        The last coordinates are the coordinates of "our" point.
        a (+x), e (-x), c (-y), d (+y), b does nothing.
        
        We get scores for each new location, bar the first move which doesn't seem
        to matter. Each new location is worth +2 points.
    """
    print(abcde.upper())

def can_move(args, action):
    """ Return true if we can perform the given move.
        Because we don't have any data for e, just return true.
    """
    action_view_map = {'c': 0, 'a': 1, 'd': 2, 'e': 3}
    return action == 'b' or args[-1][action_view_map[action]] == '_'

add_pos = lambda p1, p2, size: tuple([(p1[i] + p2[i]) % size[i] for i in range(2)])

def next_location(args, action, x_depth, y_depth):
    """ Return the location after performing the given action """
    if not can_move(args, action):
        return (args[-1][-2], args[-1][-1])

    action_move_map = {
        'a': (1, 0),
        'b': (0, 0),
        'c': (0, -1),
        'd': (0, 1),
        'e': (-1, 0),
    }
    return add_pos(args[-1][-2:], action_move_map[action], (x_depth, y_depth))
        
def min_dist(lvl_map, size, loc):
    """ Find the minimum distances from a single point """
    
    current_set = {loc}
    current_dist = 0
    next_set = set()
    distances = {p: float('inf') for p, v in lvl_map.items() if v == '#'}
    
    directions = {(1, 0), (0, 1), (0, -1), (-1, 0)}
    while len(current_set) > 0:
        for pos in current_set:
            print(pos, distances.get(pos, -2))
            distances[pos] = current_dist
            for d in directions:
                neighbour = add_pos(pos, d, size)
                if neighbour not in distances.keys():
                    next_set.add(neighbour)
                    distances[neighbour] = -1 # Don't visit twice.
        
        print(current_set, current_dist, next_set, distances)
        current_dist += 1
        current_set = next_set
        next_set = set()
    
    return distances

def strategy_precalc(args):
    """ Follow a preset strategy (debug only) """
    cmds = ['b'] + ['e']*20 + ['a']*8 + ['c']*22 + ['a']*6 + ['d']*20 + ['b']
    if len(cmds) > loop: # Only preset commands
        do_action(args, cmds[loop])
    else:
        do_action(args, 'b')
        
def strategy_precalc_loop(args):
    """ Follow a preset strategy, looping over a command set (debug only) """
    cmds = ['b'] + ['e']*20 + ['a']*8 + ['c']*22 + ['a']*6 + ['d']*20 + ['b']
    do_action(args, cmds[loop % len(cmds)])

lvl_map = {} # location: type, where type is one of '#' or '_'
def strategy_weighted_ghosts(args, x_depth, y_depth):
    """ Avoid ghosts when they are nearby, otherwise choose the least-recent """
    
    # Add the most recent locations to the level map.
    x, y = args[-1][-2], args[-1][-1]
    lvl_map[(x, y)] = '_'
    lvl_map[(x, y-1)] = args[-1][0]
    lvl_map[(x+1, y)] = args[-1][1]
    lvl_map[(x, y+1)] = args[-1][2]
    lvl_map[(x-1, y)] = args[-1][3]
    # Include the ghost positions.
    for j in range((len(args[-1])-6)//2):
        lvl_map[(args[-1][j*2 + 4], args[-1][j*2 + 5])] = '_'
    
    visit_time = {}
    for i, arg in enumerate(args):
        visit_time[(arg[-2], arg[-1])] = i
    
    def ghost_dist(pos, x_depth, y_depth):
        """ Return the minimum distance to a ghost (naive calculation) """
        def abs_dist(pos1, pos2):
            depth = (x_depth, y_depth)
            total = 0
            for i in range(2):
                total += min(abs((pos1[i] - pos2[i]) % depth[i]),
                             abs((pos2[i] - pos1[i]) % depth[i]))
            return total
        ghost_dists = []
        for i in range((len(arg)-6)//2): # Don't include our pos!
            ghost_pos = (arg[i*2 + 4], arg[i*2 + 5])
            ghost_dists.append(abs_dist(pos, ghost_pos))
        return ghost_dists

    opts = {}
    for action in ['a', 'b', 'c', 'd', 'e']:
        next_loc = next_location(args, action, x_depth, y_depth)
        dists = ghost_dist(next_loc, x_depth, y_depth)
        if can_move(args, action) and min(dists) >= 2:
            weight = (visit_time.get(next_loc, -1) + 2) * max((7 - sorted(dists)[1]), 1)
            opts[weight] = opts.get(weight, []) + [action]
        
    if len(opts) == 0: opts = {-2: 'b'} # Stuck!
    debug(opts)
    final_opts = opts[min(opts.keys())]
    action = final_opts[randint(0, len(final_opts)-1)]
    do_action(args, action)
    
    for x in range(x_depth):
        for y in range(y_depth):
            char = lvl_map.get((x, y), '?')
            for unit in range((len(arg)-4)//2): # Don't include our pos!
                if arg[unit*2 + 4] == x and arg[unit*2 + 5] == y:
                    char = str(unit)
            debug(char, end='')
        debug("")


# Initial set of inputs - the size of the board and the unit counts.
y_depth = int(input())
x_depth = int(input())
unit_count = int(input())

debug("init_args: {}, {}, {}".format(y_depth, x_depth, unit_count))

args = [] # Current list of all arguments
while True:
    input_1 = input()
    input_2 = input()
    input_3 = input()
    input_4 = input()
    args.append([input_1, input_2, input_3, input_4])
    # Coordinates of units.
    for i in range(unit_count):
        args[-1] += [int(j) for j in input().split()]
    
    strategy_weighted_ghosts(args, x_depth, y_depth)
    
    debug(args[-1])""" CodinGame sponsored contest.

    This looks a lot like a map/dungeon explorer game.
"""

import sys
import math
from random import randint

debug = lambda *args, **kargs: print(*args, **kargs, file=sys.stderr)
action = lambda abcde: print(abcde.upper()) # Actions are one of a, b, c, d, or e

def do_action(args, abcde):
    """ Do an action (actions are one of a, b, c, d, or e)
    
        Apparently a,b,c,d,e allow you to move in 4 directions or hold still;
        hence the coordinates might be helpful here...
        The last coordinates are the coordinates of "our" point.
        a (+x), e (-x), c (-y), d (+y), b does nothing.
        
        We get scores for each new location, bar the first move which doesn't seem
        to matter. Each new location is worth +2 points.
    """
    print(abcde.upper())

def can_move(args, action):
    """ Return true if we can perform the given move.
        Because we don't have any data for e, just return true.
    """
    action_view_map = {'c': 0, 'a': 1, 'd': 2, 'e': 3}
    return action == 'b' or args[-1][action_view_map[action]] == '_'

add_pos = lambda p1, p2, size: tuple([(p1[i] + p2[i]) % size[i] for i in range(2)])

def next_location(args, action, x_depth, y_depth):
    """ Return the location after performing the given action """
    if not can_move(args, action):
        return (args[-1][-2], args[-1][-1])

    action_move_map = {
        'a': (1, 0),
        'b': (0, 0),
        'c': (0, -1),
        'd': (0, 1),
        'e': (-1, 0),
    }
    return add_pos(args[-1][-2:], action_move_map[action], (x_depth, y_depth))
        
def min_dist(lvl_map, size, loc):
    """ Find the minimum distances from a single point """
    
    current_set = {loc}
    current_dist = 0
    next_set = set()
    distances = {p: float('inf') for p, v in lvl_map.items() if v == '#'}
    
    directions = {(1, 0), (0, 1), (0, -1), (-1, 0)}
    while len(current_set) > 0:
        for pos in current_set:
            distances[pos] = current_dist
            for d in directions:
                neighbour = add_pos(pos, d, size)
                if neighbour not in distances.keys():
                    next_set.add(neighbour)
                    distances[neighbour] = -1 # Don't visit twice.
        
        current_dist += 1
        current_set = next_set
        next_set = set()
    
    return distances

def strategy_precalc(args):
    """ Follow a preset strategy (debug only) """
    cmds = ['b'] + ['e']*20 + ['a']*8 + ['c']*22 + ['a']*6 + ['d']*20 + ['b']
    if len(cmds) > loop: # Only preset commands
        do_action(args, cmds[loop])
    else:
        do_action(args, 'b')
        
def strategy_precalc_loop(args):
    """ Follow a preset strategy, looping over a command set (debug only) """
    cmds = ['b'] + ['e']*20 + ['a']*8 + ['c']*22 + ['a']*6 + ['d']*20 + ['b']
    do_action(args, cmds[loop % len(cmds)])

lvl_map = {} # location: type, where type is one of '#' or '_'
def strategy_weighted_ghosts(args, x_depth, y_depth):
    """ Avoid ghosts when they are nearby, otherwise choose the least-recent """
    
    # Add the most recent locations to the level map.
    x, y = args[-1][-2], args[-1][-1]
    lvl_map[(x, y)] = '_'
    lvl_map[(x, y-1)] = args[-1][0]
    lvl_map[(x+1, y)] = args[-1][1]
    lvl_map[(x, y+1)] = args[-1][2]
    lvl_map[(x-1, y)] = args[-1][3]
    # Include the ghost positions.
    for j in range((len(args[-1])-6)//2):
        lvl_map[(args[-1][j*2 + 4], args[-1][j*2 + 5])] = '_'
    
    visit_time = {}
    for i, arg in enumerate(args):
        visit_time[(arg[-2], arg[-1])] = i
    
    def ghost_dist(pos, x_depth, y_depth):
        """ Return the minimum distance to a ghost (naive calculation) """
        map_dists = min_dist(lvl_map, (x_depth, y_depth), pos)
        ghost_dists = []
        for i in range((len(arg)-6)//2): # Don't include our pos!
            ghost_pos = (arg[i*2 + 4], arg[i*2 + 5])
            ghost_dists.append(map_dists[ghost_pos])
        return ghost_dists

    opts = {}
    for action in ['a', 'b', 'c', 'd', 'e']:
        next_loc = next_location(args, action, x_depth, y_depth)
        dists = ghost_dist(next_loc, x_depth, y_depth)
        if can_move(args, action) and min(dists) >= 2:
            weight = (visit_time.get(next_loc, -1) + 2) * max((7 - sorted(dists)[1]), 1)
            opts[weight] = opts.get(weight, []) + [action]
        
    if len(opts) == 0: opts = {-2: 'b'} # Stuck!
    debug(opts)
    final_opts = opts[min(opts.keys())]
    action = final_opts[randint(0, len(final_opts)-1)]
    do_action(args, action)
    
    for x in range(x_depth):
        for y in range(y_depth):
            char = lvl_map.get((x, y), '?')
            for unit in range((len(arg)-4)//2): # Don't include our pos!
                if arg[unit*2 + 4] == x and arg[unit*2 + 5] == y:
                    char = str(unit)
            debug(char, end='')
        debug("")


# Initial set of inputs - the size of the board and the unit counts.
y_depth = int(input())
x_depth = int(input())
unit_count = int(input())

debug("init_args: {}, {}, {}".format(y_depth, x_depth, unit_count))

args = [] # Current list of all arguments
while True:
    input_1 = input()
    input_2 = input()
    input_3 = input()
    input_4 = input()
    args.append([input_1, input_2, input_3, input_4])
    # Coordinates of units.
    for i in range(unit_count):
        args[-1] += [int(j) for j in input().split()]
    
    strategy_weighted_ghosts(args, x_depth, y_depth)
    
    debug(args[-1])""" CodinGame sponsored contest.

    This looks a lot like a map/dungeon explorer game.
"""

import sys
import math
from random import randint

debug = lambda *args, **kargs: print(*args, **kargs, file=sys.stderr)
action = lambda abcde: print(abcde.upper()) # Actions are one of a, b, c, d, or e

def do_action(args, abcde):
    """ Do an action (actions are one of a, b, c, d, or e)
    
        Apparently a,b,c,d,e allow you to move in 4 directions or hold still;
        hence the coordinates might be helpful here...
        The last coordinates are the coordinates of "our" point.
        a (+x), e (-x), c (-y), d (+y), b does nothing.
        
        We get scores for each new location, bar the first move which doesn't seem
        to matter. Each new location is worth +2 points.
    """
    print(abcde.upper())

def can_move(args, action):
    """ Return true if we can perform the given move.
        Because we don't have any data for e, just return true.
    """
    action_view_map = {'c': 0, 'a': 1, 'd': 2, 'e': 3}
    return action == 'b' or args[-1][action_view_map[action]] == '_'

add_pos = lambda p1, p2, size: tuple([(p1[i] + p2[i]) % size[i] for i in range(2)])

action_move_map = {
        'a': (1, 0),
        'b': (0, 0),
        'c': (0, -1),
        'd': (0, 1),
        'e': (-1, 0),
    }
def next_location(args, action, x_depth, y_depth):
    """ Return the location after performing the given action """
    if not can_move(args, action):
        return (args[-1][-2], args[-1][-1])
    return add_pos(args[-1][-2:], action_move_map[action], (x_depth, y_depth))
        
def min_dist(lvl_map, size, loc):
    """ Find the minimum distances from a single point """
    
    current_set = {loc}
    current_dist = 0
    next_set = set()
    distances = {p: float('inf') for p, v in lvl_map.items() if v == '#'}
    
    directions = {(1, 0), (0, 1), (0, -1), (-1, 0)}
    while len(current_set) > 0:
        for pos in current_set:
            distances[pos] = current_dist
            for d in directions:
                neighbour = add_pos(pos, d, size)
                if neighbour not in distances.keys():
                    next_set.add(neighbour)
                    distances[neighbour] = -1 # Don't visit twice.
        
        current_dist += 1
        current_set = next_set
        next_set = set()
    
    return distances

def strategy_precalc(args):
    """ Follow a preset strategy (debug only) """
    cmds = ['b'] + ['e']*20 + ['a']*8 + ['c']*22 + ['a']*6 + ['d']*20 + ['b']
    if len(cmds) > loop: # Only preset commands
        do_action(args, cmds[loop])
    else:
        do_action(args, 'b')
        
def strategy_precalc_loop(args):
    """ Follow a preset strategy, looping over a command set (debug only) """
    cmds = ['b'] + ['e']*20 + ['a']*8 + ['c']*22 + ['a']*6 + ['d']*20 + ['b']
    do_action(args, cmds[loop % len(cmds)])
    
def path_to_intersection(lvl_map, size, orig_pos, cur_action):
    """ Return the path to travel to the next intersection """
    
    inv_actions = {'a': 'e', 'e': 'a', 'd': 'c', 'c': 'd'}
    
    pos = add_pos(orig_pos, action_move_map[cur_action], size)
        
    opts = []
    for action, delta in action_move_map.items():
        if lvl_map.get(add_pos(pos, delta, size), '_') == '_' \
            and action != 'b' and inv_actions[action] != cur_action:
            opts.append(action)

    if len(opts) == 1:
        return [(pos, opts)] + path_to_intersection(lvl_map, size, pos, opts[0])
    return [(pos, opts)] # Base case.

lvl_map = {} # location: type, where type is one of '#' or '_'
def strategy_weighted_ghosts(args, size):
    """ Avoid ghosts when they are nearby, otherwise choose the least-recent """
    
    # Add the most recent locations to the level map.
    x, y = args[-1][-2], args[-1][-1]
    lvl_map[(x, y)] = '_'
    lvl_map[(x, y-1)] = args[-1][0]
    lvl_map[(x+1, y)] = args[-1][1]
    lvl_map[(x, y+1)] = args[-1][2]
    lvl_map[(x-1, y)] = args[-1][3]
    # Include the ghost positions.
    for j in range((len(args[-1])-6)//2):
        lvl_map[(args[-1][j*2 + 4], args[-1][j*2 + 5])] = '_'
    
    visit_time = {}
    for i, arg in enumerate(args):
        visit_time[(arg[-2], arg[-1])] = i
    
    def ghost_dist(pos):
        """ Return the minimum distance to a ghost (naive calculation) """
        map_dists = min_dist(lvl_map, size, pos)
        ghost_dists = []
        for i in range((len(arg)-6)//2): # Don't include our pos!
            ghost_pos = (arg[i*2 + 4], arg[i*2 + 5])
            ghost_dists.append(map_dists[ghost_pos])
        return ghost_dists

    opts = {}
    for action in ['a', 'b', 'c', 'd', 'e']:
        next_loc = next_location(args, action, size[0], size[1])
        dists = ghost_dist(next_loc)
        path = path_to_intersection(lvl_map, size, args[-1][-2:], action)
        if can_move(args, action) and min(dists) >= 2:
            path = path_to_intersection(lvl_map, size, args[-1][-2:], action)
            weight = visit_time.get(next_loc, -1)
            debug(action, ghost_dist(path[-1][0]), len(path), path[-1][0])
            if len(path[-1][1]) > 1 and len(path) >= min(ghost_dist(path[-1][0])):
                weight += len(args)
            if len(path[-1][1]) == 0:
                weight += len(args) + 1
            opts[weight] = opts.get(weight, []) + [action]
        
    if len(opts) == 0: opts = {-2: 'b'} # Stuck!
    debug(opts)
    final_opts = opts[min(opts.keys())]
    action = final_opts[randint(0, len(final_opts)-1)]
    do_action(args, action)
    
    for x in range(x_depth):
        for y in range(y_depth):
            char = lvl_map.get((x, y), '?')
            for unit in range((len(arg)-4)//2): # Don't include our pos!
                if arg[unit*2 + 4] == x and arg[unit*2 + 5] == y:
                    char = str(unit)
            debug(char, end='')
        debug("")


# Initial set of inputs - the size of the board and the unit counts.
y_depth = int(input())
x_depth = int(input())
unit_count = int(input())

debug("init_args: {}, {}, {}".format(y_depth, x_depth, unit_count))

args = [] # Current list of all arguments
while True:
    input_1 = input()
    input_2 = input()
    input_3 = input()
    input_4 = input()
    args.append([input_1, input_2, input_3, input_4])
    # Coordinates of units.
    for i in range(unit_count):
        args[-1] += [int(j) for j in input().split()]
    
    strategy_weighted_ghosts(args, (x_depth, y_depth))
    
    debug(args[-1])""" CodinGame sponsored contest.

    This looks a lot like a map/dungeon explorer game.
"""

import sys
import math
from random import randint

debug = lambda *args, **kargs: print(*args, **kargs, file=sys.stderr)
action = lambda abcde: print(abcde.upper()) # Actions are one of a, b, c, d, or e

def do_action(args, abcde):
    """ Do an action (actions are one of a, b, c, d, or e)
    
        Apparently a,b,c,d,e allow you to move in 4 directions or hold still;
        hence the coordinates might be helpful here...
        The last coordinates are the coordinates of "our" point.
        a (+x), e (-x), c (-y), d (+y), b does nothing.
        
        We get scores for each new location, bar the first move which doesn't seem
        to matter. Each new location is worth +2 points.
    """
    print(abcde.upper())

def can_move(args, action):
    """ Return true if we can perform the given move.
        Because we don't have any data for e, just return true.
    """
    action_view_map = {'c': 0, 'a': 1, 'd': 2, 'e': 3}
    return action == 'b' or args[-1][action_view_map[action]] == '_'

add_pos = lambda p1, p2, size: tuple([(p1[i] + p2[i]) % size[i] for i in range(2)])

action_move_map = {
        'a': (1, 0),
        'b': (0, 0),
        'c': (0, -1),
        'd': (0, 1),
        'e': (-1, 0),
    }
def next_location(args, action, x_depth, y_depth):
    """ Return the location after performing the given action """
    if not can_move(args, action):
        return (args[-1][-2], args[-1][-1])
    return add_pos(args[-1][-2:], action_move_map[action], (x_depth, y_depth))

def min_dist(lvl_map, size, loc):
    """ Find the minimum distances from a single point """
    
    current_set = {loc}
    current_dist = 0
    next_set = set()
    distances = {p: float('inf') for p, v in lvl_map.items() if v == '#'}
    
    directions = {(1, 0), (0, 1), (0, -1), (-1, 0)}
    while len(current_set) > 0:
        for pos in current_set:
            distances[pos] = current_dist
            for d in directions:
                neighbour = add_pos(pos, d, size)
                if neighbour not in distances.keys():
                    next_set.add(neighbour)
                    distances[neighbour] = -1 # Don't visit twice.
        
        current_dist += 1
        current_set = next_set
        next_set = set()
    
    return distances

def strategy_precalc(args):
    """ Follow a preset strategy (debug only) """
    cmds = ['b'] + ['e']*20 + ['a']*8 + ['c']*22 + ['a']*6 + ['d']*20 + ['b']
    if len(cmds) > loop: # Only preset commands
        do_action(args, cmds[loop])
    else:
        do_action(args, 'b')
        
def strategy_precalc_loop(args):
    """ Follow a preset strategy, looping over a command set (debug only) """
    cmds = ['b'] + ['e']*20 + ['a']*8 + ['c']*22 + ['a']*6 + ['d']*20 + ['b']
    do_action(args, cmds[loop % len(cmds)])
    
def path_to_intersection(lvl_map, size, orig_pos, cur_action):
    """ Return the path to travel to the next intersection """
    
    inv_actions = {'a': 'e', 'e': 'a', 'd': 'c', 'c': 'd'}
    
    pos = add_pos(orig_pos, action_move_map[cur_action], size)
        
    opts = []
    for action, delta in action_move_map.items():
        if lvl_map.get(add_pos(pos, delta, size), '#') == '_' \
            and action != 'b' and inv_actions[action] != cur_action:
            opts.append(action)

    if len(opts) == 1:
        return [(pos, opts)] + path_to_intersection(lvl_map, size, pos, opts[0])
    return [(pos, opts)] # Base case.

lvl_map = {} # location: type, where type is one of '#' or '_'
def strategy_weighted_ghosts(args, size):
    """ Avoid ghosts when they are nearby, otherwise choose the least-recent """
    
    # Add the most recent locations to the level map.
    x, y = args[-1][-2], args[-1][-1]
    lvl_map[(x, y)] = '_'
    lvl_map[(x, y-1)] = args[-1][0]
    lvl_map[(x+1, y)] = args[-1][1]
    lvl_map[(x, y+1)] = args[-1][2]
    lvl_map[(x-1, y)] = args[-1][3]
    # Include the ghost positions.
    for j in range((len(args[-1])-6)//2):
        lvl_map[(args[-1][j*2 + 4], args[-1][j*2 + 5])] = '_'
    
    visit_time = {}
    for i, arg in enumerate(args):
        visit_time[(arg[-2], arg[-1])] = i
    
    def ghost_dist(pos):
        """ Return the distances to each ghost """
        map_dists = min_dist(lvl_map, size, pos)
        ghost_dists = []
        for i in range((len(arg)-6)//2): # Don't include our pos!
            ghost_pos = (arg[i*2 + 4], arg[i*2 + 5])
            ghost_dists.append(map_dists[ghost_pos])
        return ghost_dists

    opts = {}
    for action in ['a', 'b', 'c', 'd', 'e']:
        next_loc = next_location(args, action, size[0], size[1])
        dists = ghost_dist(next_loc)
        if can_move(args, action) and min(dists) >= 2:
            path = path_to_intersection(lvl_map, size, args[-1][-2:], action)
            weight = visit_time.get(next_loc, -1)
            if len(path[-1][1]) > 1 and len(path) >= min(ghost_dist(path[-1][0])):
                weight += len(args)
            weight *= len([d for d in dists if d < 10]) + 1
            opts[weight] = opts.get(weight, []) + [action]
        
    if len(opts) == 0: opts = {-2: 'b'} # Stuck!
    debug(opts)
    final_opts = opts[min(opts.keys())]
    action = final_opts[randint(0, len(final_opts)-1)]
    do_action(args, action)
    
    for x in range(x_depth):
        for y in range(y_depth):
            char = lvl_map.get((x, y), '?')
            for unit in range((len(arg)-4)//2):
                if arg[unit*2 + 4] == x and arg[unit*2 + 5] == y:
                    char = str(unit)
            debug(char, end='')
        debug("")


# Initial set of inputs - the size of the board and the unit counts.
y_depth = int(input())
x_depth = int(input())
unit_count = int(input())

debug("init_args: {}, {}, {}".format(y_depth, x_depth, unit_count))

args = [] # Current list of all arguments
while True:
    input_1 = input()
    input_2 = input()
    input_3 = input()
    input_4 = input()
    args.append([input_1, input_2, input_3, input_4])
    # Coordinates of units.
    for i in range(unit_count):
        args[-1] += [int(j) for j in input().split()]
    
    strategy_weighted_ghosts(args, (x_depth, y_depth))
""" CodinGame sponsored contest.

    This looks a lot like a map/dungeon explorer game.
"""

import sys
import math
from random import randint

debug = lambda *args, **kargs: print(*args, **kargs, file=sys.stderr)
action = lambda abcde: print(abcde.upper()) # Actions are one of a, b, c, d, or e

def do_action(args, abcde):
    """ Do an action (actions are one of a, b, c, d, or e)
    
        Apparently a,b,c,d,e allow you to move in 4 directions or hold still;
        hence the coordinates might be helpful here...
        The last coordinates are the coordinates of "our" point.
        a (+x), e (-x), c (-y), d (+y), b does nothing.
        
        We get scores for each new location, bar the first move which doesn't seem
        to matter. Each new location is worth +2 points.
    """
    print(abcde.upper())

def can_move(args, action):
    """ Return true if we can perform the given move.
        Because we don't have any data for e, just return true.
    """
    action_view_map = {'c': 0, 'a': 1, 'd': 2, 'e': 3}
    return action == 'b' or args[-1][action_view_map[action]] == '_'

add_pos = lambda p1, p2, size: tuple([(p1[i] + p2[i]) % size[i] for i in range(2)])

action_move_map = {
        'a': (1, 0),
        'b': (0, 0),
        'c': (0, -1),
        'd': (0, 1),
        'e': (-1, 0),
    }
def next_location(args, action, x_depth, y_depth):
    """ Return the location after performing the given action """
    if not can_move(args, action):
        return (args[-1][-2], args[-1][-1])
    return add_pos(args[-1][-2:], action_move_map[action], (x_depth, y_depth))

def min_dist(lvl_map, size, loc):
    """ Find the minimum distances from a single point """
    
    current_set = {loc}
    current_dist = 0
    next_set = set()
    distances = {p: float('inf') for p, v in lvl_map.items() if v == '#'}
    
    directions = {(1, 0), (0, 1), (0, -1), (-1, 0)}
    while len(current_set) > 0:
        for pos in current_set:
            distances[pos] = current_dist
            for d in directions:
                neighbour = add_pos(pos, d, size)
                if neighbour not in distances.keys():
                    next_set.add(neighbour)
                    distances[neighbour] = -1 # Don't visit twice.
        
        current_dist += 1
        current_set = next_set
        next_set = set()
    
    return distances

def strategy_precalc(args):
    """ Follow a preset strategy (debug only) """
    cmds = ['b'] + ['e']*20 + ['a']*8 + ['c']*22 + ['a']*6 + ['d']*20 + ['b']
    if len(cmds) > loop: # Only preset commands
        do_action(args, cmds[loop])
    else:
        do_action(args, 'b')
        
def strategy_precalc_loop(args):
    """ Follow a preset strategy, looping over a command set (debug only) """
    cmds = ['b'] + ['e']*20 + ['a']*8 + ['c']*22 + ['a']*6 + ['d']*20 + ['b']
    do_action(args, cmds[loop % len(cmds)])
    
def path_to_intersection(lvl_map, size, orig_pos, cur_action):
    """ Return the path to travel to the next intersection """
    
    inv_actions = {'a': 'e', 'e': 'a', 'd': 'c', 'c': 'd'}
    
    pos = add_pos(orig_pos, action_move_map[cur_action], size)
        
    opts = []
    for action, delta in action_move_map.items():
        if lvl_map.get(add_pos(pos, delta, size), '#') == '_' \
            and action != 'b' and inv_actions[action] != cur_action:
            opts.append(action)

    if len(opts) == 1:
        return [(pos, opts)] + path_to_intersection(lvl_map, size, pos, opts[0])
    return [(pos, opts)] # Base case.

lvl_map = {} # location: type, where type is one of '#' or '_'
def strategy_weighted_ghosts(args, size):
    """ Avoid ghosts when they are nearby, otherwise choose the least-recent """
    
    # Add the most recent locations to the level map.
    x, y = args[-1][-2], args[-1][-1]
    lvl_map[(x, y)] = '_'
    lvl_map[(x, y-1)] = args[-1][0]
    lvl_map[(x+1, y)] = args[-1][1]
    lvl_map[(x, y+1)] = args[-1][2]
    lvl_map[(x-1, y)] = args[-1][3]
    # Include the ghost positions.
    for j in range((len(args[-1])-6)//2):
        lvl_map[(args[-1][j*2 + 4], args[-1][j*2 + 5])] = '_'
    
    visit_time = {}
    for i, arg in enumerate(args):
        visit_time[(arg[-2], arg[-1])] = i
    
    def ghost_dist(pos):
        """ Return the distances to each ghost """
        map_dists = min_dist(lvl_map, size, pos)
        ghost_dists = []
        for i in range((len(arg)-6)//2): # Don't include our pos!
            ghost_pos = (arg[i*2 + 4], arg[i*2 + 5])
            ghost_dists.append(map_dists[ghost_pos])
        return ghost_dists

    opts = {}
    for action in ['a', 'b', 'c', 'd', 'e']:
        next_loc = next_location(args, action, size[0], size[1])
        dists = ghost_dist(next_loc)
        if can_move(args, action) and min(dists) >= 2:
            path = path_to_intersection(lvl_map, size, args[-1][-2:], action)
            weight = visit_time.get(next_loc, -1)
            if len(path[-1][1]) > 1 and len(path) >= min(ghost_dist(path[-1][0])):
                weight += len(args)
            weight *= len([d for d in dists if d < 7]) + 1
            weight += sum([abs(next_loc[i] - (size[i] // 2)) for i in range(2)])
            opts[weight] = opts.get(weight, []) + [action]
        
    if len(opts) == 0: opts = {-2: 'b'} # Stuck!
    debug(opts)
    final_opts = opts[min(opts.keys())]
    action = final_opts[randint(0, len(final_opts)-1)]
    do_action(args, action)
    
    for x in range(x_depth):
        for y in range(y_depth):
            char = lvl_map.get((x, y), '?')
            for unit in range((len(arg)-4)//2):
                if arg[unit*2 + 4] == x and arg[unit*2 + 5] == y:
                    char = str(unit)
            debug(char, end='')
        debug("")


# Initial set of inputs - the size of the board and the unit counts.
y_depth = int(input())
x_depth = int(input())
unit_count = int(input())

debug("init_args: {}, {}, {}".format(y_depth, x_depth, unit_count))

args = [] # Current list of all arguments
while True:
    input_1 = input()
    input_2 = input()
    input_3 = input()
    input_4 = input()
    args.append([input_1, input_2, input_3, input_4])
    # Coordinates of units.
    for i in range(unit_count):
        args[-1] += [int(j) for j in input().split()]
    
    strategy_weighted_ghosts(args, (x_depth, y_depth))
""" CodinGame sponsored contest.

    This looks a lot like a map/dungeon explorer game.
"""

import sys
import math
from random import randint

debug = lambda *args, **kargs: print(*args, **kargs, file=sys.stderr)
action = lambda abcde: print(abcde.upper()) # Actions are one of a, b, c, d, or e

def do_action(args, abcde):
    """ Do an action (actions are one of a, b, c, d, or e)
    
        Apparently a,b,c,d,e allow you to move in 4 directions or hold still;
        hence the coordinates might be helpful here...
        The last coordinates are the coordinates of "our" point.
        a (+x), e (-x), c (-y), d (+y), b does nothing.
        
        We get scores for each new location, bar the first move which doesn't seem
        to matter. Each new location is worth +2 points.
    """
    print(abcde.upper())

def can_move(args, action):
    """ Return true if we can perform the given move.
        Because we don't have any data for e, just return true.
    """
    action_view_map = {'c': 0, 'a': 1, 'd': 2, 'e': 3}
    return action == 'b' or args[-1][action_view_map[action]] == '_'

add_pos = lambda p1, p2, size: tuple([(p1[i] + p2[i]) % size[i] for i in range(2)])

action_move_map = {
        'a': (1, 0),
        'b': (0, 0),
        'c': (0, -1),
        'd': (0, 1),
        'e': (-1, 0),
    }
def next_location(args, action, x_depth, y_depth):
    """ Return the location after performing the given action """
    if not can_move(args, action):
        return (args[-1][-2], args[-1][-1])
    return add_pos(args[-1][-2:], action_move_map[action], (x_depth, y_depth))

def min_dist(lvl_map, size, loc):
    """ Find the minimum distances from a single point """
    
    current_set = {loc}
    current_dist = 0
    next_set = set()
    distances = {p: float('inf') for p, v in lvl_map.items() if v == '#'}
    
    directions = {(1, 0), (0, 1), (0, -1), (-1, 0)}
    while len(current_set) > 0:
        for pos in current_set:
            distances[pos] = current_dist
            for d in directions:
                neighbour = add_pos(pos, d, size)
                if neighbour not in distances.keys():
                    next_set.add(neighbour)
                    distances[neighbour] = -1 # Don't visit twice.
        
        current_dist += 1
        current_set = next_set
        next_set = set()
    
    return distances

def strategy_precalc(args):
    """ Follow a preset strategy (debug only) """
    cmds = ['b'] + ['e']*20 + ['a']*8 + ['c']*22 + ['a']*6 + ['d']*20 + ['b']
    if len(cmds) > loop: # Only preset commands
        do_action(args, cmds[loop])
    else:
        do_action(args, 'b')
        
def strategy_precalc_loop(args):
    """ Follow a preset strategy, looping over a command set (debug only) """
    cmds = ['b'] + ['e']*20 + ['a']*8 + ['c']*22 + ['a']*6 + ['d']*20 + ['b']
    do_action(args, cmds[loop % len(cmds)])
    
def path_to_intersection(lvl_map, size, orig_pos, cur_action):
    """ Return the path to travel to the next intersection """
    
    inv_actions = {'a': 'e', 'e': 'a', 'd': 'c', 'c': 'd'}
    
    pos = add_pos(orig_pos, action_move_map[cur_action], size)
        
    opts = []
    for action, delta in action_move_map.items():
        if lvl_map.get(add_pos(pos, delta, size), '#') == '_' \
            and action != 'b' and inv_actions[action] != cur_action:
            opts.append(action)

    if len(opts) == 1:
        return [(pos, opts)] + path_to_intersection(lvl_map, size, pos, opts[0])
    return [(pos, opts)] # Base case.

lvl_map = {} # location: type, where type is one of '#' or '_'
def strategy_weighted_ghosts(args, size):
    """ Avoid ghosts when they are nearby, otherwise choose the least-recent """
    
    # Add the most recent locations to the level map.
    x, y = args[-1][-2], args[-1][-1]
    lvl_map[(x, y)] = '_'
    lvl_map[(x, y-1)] = args[-1][0]
    lvl_map[(x+1, y)] = args[-1][1]
    lvl_map[(x, y+1)] = args[-1][2]
    lvl_map[(x-1, y)] = args[-1][3]
    # Include the ghost positions.
    for j in range((len(args[-1])-6)//2):
        lvl_map[(args[-1][j*2 + 4], args[-1][j*2 + 5])] = '_'
    
    visit_time = {}
    for i, arg in enumerate(args):
        visit_time[(arg[-2], arg[-1])] = i
    
    def ghost_dist(pos):
        """ Return the distances to each ghost """
        map_dists = min_dist(lvl_map, size, pos)
        ghost_dists = []
        for i in range((len(arg)-6)//2): # Don't include our pos!
            ghost_pos = (arg[i*2 + 4], arg[i*2 + 5])
            ghost_dists.append(map_dists[ghost_pos])
        return ghost_dists

    opts = {}
    for action in ['a', 'b', 'c', 'd', 'e']:
        next_loc = next_location(args, action, size[0], size[1])
        dists = ghost_dist(next_loc)
        if can_move(args, action) and min(dists) >= 2:
            path = path_to_intersection(lvl_map, size, args[-1][-2:], action)
            weight = visit_time.get(next_loc, -1)
            if len(path[-1][1]) > 1 and len(path) >= min(ghost_dist(path[-1][0])):
                weight += len(args) + size[0]*size[1] - len(path) # Prefer longer paths...
            weight -= int(sum([math.sqrt(d) for d in dists]) * 10 / len(dists)) # Run away from ghosts
            opts[weight] = opts.get(weight, []) + [action]
        
    if len(opts) == 0: opts = {-2: 'b'} # Stuck!
    debug(opts)
    final_opts = opts[min(opts.keys())]
    action = final_opts[randint(0, len(final_opts)-1)]
    do_action(args, action)
    
    for x in range(x_depth):
        for y in range(y_depth):
            char = lvl_map.get((x, y), '?')
            for unit in range((len(arg)-4)//2):
                if arg[unit*2 + 4] == x and arg[unit*2 + 5] == y:
                    char = str(unit)
            debug(char, end='')
        debug("")


# Initial set of inputs - the size of the board and the unit counts.
y_depth = int(input())
x_depth = int(input())
unit_count = int(input())

debug("init_args: {}, {}, {}".format(y_depth, x_depth, unit_count))

args = [] # Current list of all arguments
while True:
    input_1 = input()
    input_2 = input()
    input_3 = input()
    input_4 = input()
    args.append([input_1, input_2, input_3, input_4])
    # Coordinates of units.
    for i in range(unit_count):
        args[-1] += [int(j) for j in input().split()]
    
    strategy_weighted_ghosts(args, (x_depth, y_depth))
