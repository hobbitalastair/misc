#!/usr/bin/env python3
""" Convert between Z-Matrix and Cartesian coordinate representations of
    molecules.

    Author: Alastair Hughes
    Contact: hobbitalastair at yandex dot com
"""

import math
sin = lambda deg: math.sin(math.radians(deg))
cos = lambda deg: math.cos(math.radians(deg))
acos = lambda ratio: math.degrees(math.acos(ratio))
atan = lambda ratio: math.degrees(math.atan(ratio))

def polar_to_cartesian(angle, dihedral, length):
    """ Convert from polar angles in 3D to a cartesian offset.

        The given angle is taken to be between the line from the origin to the
        point (0, 0, 1) on the z-axis, and the new position.
        The dihedral is assumed to be between the x-z plane and the new plane
        formed by the new position, origin, and point (0, 0, 1) on the
        z-axis.

        >>> [round(i, 2) for i in polar_to_cartesian(0, 0, 2)]
        [0.0, 0.0, 2.0]
        >>> [round(i, 2) for i in polar_to_cartesian(345, 20, 0)]
        [-0.0, -0.0, 0.0]
        >>> [round(i, 2) for i in polar_to_cartesian(90, 0, 1)]
        [1.0, 0.0, 0.0]
        >>> [round(i, 2) for i in polar_to_cartesian(90, 90, 1)]
        [0.0, 1.0, 0.0]
        >>> [round(i, 2) for i in polar_to_cartesian(0, 59, 1)]
        [0.0, 0.0, 1.0]
        >>> [round(i, 2) for i in polar_to_cartesian(90, 45, math.sqrt(2))]
        [1.0, 1.0, 0.0]
        >>> [round(i, 2) for i in polar_to_cartesian(45, 0, math.sqrt(2))]
        [1.0, 0.0, 1.0]
        >>> [round(i, 2) for i in polar_to_cartesian(45, 90, 1)]
        [0.0, 0.71, 0.71]
        >>> [round(i, 2) for i in polar_to_cartesian(60, 30, 1)]
        [0.75, 0.43, 0.5]
        >>> [round(i, 2) for i in polar_to_cartesian(45, 45, math.sqrt(2))]
        [0.71, 0.71, 1.0]
        >>> [round(i, 2) for i in polar_to_cartesian(109, 120, 1)]
        [-0.47, 0.82, -0.33]
        >>> [round(i, 2) for i in polar_to_cartesian(30, 60, 1)]
        [0.25, 0.43, 0.87]
        >>> [round(i, 2) for i in cartesian_to_polar(*polar_to_cartesian(30, 60, 1))]
        [30.0, 60.0, 1.0]
        >>> [round(i, 2) for i in cartesian_to_polar(*polar_to_cartesian(60, 30, 1))]
        [60.0, 30.0, 1.0]
        >>> [round(i, 2) for i in cartesian_to_polar(*polar_to_cartesian(109, 120, 1))]
        [-109.0, -60.0, 1.0]
        >>> [round(i, 2) for i in polar_to_cartesian(*cartesian_to_polar(-1, 1, -1))]
        [-1.0, 1.0, -1.0]
    """

    z = cos(angle) * length # Distance along the z-axis.

    # The dihedral is the angle between the x-z plane and a new plane formed by
    # the point and the z-axis. Hence we can think of the dihedral purely in
    # terms of the x-y plane, and we can then find the distance in the x-y
    # plane from the angle, and use that to find the remaining distances.
    xy_distance = sin(angle) * length # Distance from the z-axis.
    y = sin(dihedral) * xy_distance
    x = cos(dihedral) * xy_distance # Distance along the x-axis.

    return [x, y, z]


def cartesian_to_polar(x, y, z):
    """ Return the polar position of the given cartesian point.

        Note that we have to be careful here; asin and acos return the smallest
        inverse, but we may want a later value (they only work properly in the
        first corner, ie if x, y, z >= 0).
        The returned dihedral is the angle between the points in the x-y plane,
        while the returned angle is relative to the z-axis.

        >>> r2 = math.sqrt(2)
        >>> [int(i) for i in cartesian_to_polar(1, 0, 0)]
        [90, 0, 1]
        >>> [int(i) for i in cartesian_to_polar(0, 1, 0)]
        [90, 90, 1]
        >>> [int(i) for i in cartesian_to_polar(0, 0, 1)]
        [0, 0, 1]
        >>> [int(i) for i in cartesian_to_polar(-1, 0, 0)]
        [-90, 0, 1]
        >>> [int(i) for i in cartesian_to_polar(0, -1, 0)]
        [90, -90, 1]
        >>> [int(i) for i in cartesian_to_polar(0, 0, -1)]
        [180, 0, 1]
        >>> [int(i) for i in cartesian_to_polar(r2, 0, r2)]
        [45, 0, 2]
        >>> [int(i) for i in cartesian_to_polar(0, r2, r2)]
        [45, 90, 2]
        >>> [int(i) for i in cartesian_to_polar(r2, r2, 0)]
        [90, 45, 2]
        >>> [int(i) for i in cartesian_to_polar(r2, 0, -r2)]
        [135, 0, 2]
        >>> [int(i) for i in cartesian_to_polar(-r2, 0, -r2)]
        [-135, 0, 2]
        >>> [int(i) for i in cartesian_to_polar(-r2, 0, r2)]
        [-45, 0, 2]
        >>> [round(i, 2) for i in cartesian_to_polar(-1, 1, -1)]
        [-125.26, -45.0, 1.73]
    """

    length = math.sqrt(x*x + y*y + z*z)
    if length == 0: return [0, 0, 0]

    # To calculate the angle, we need the length and the distance down the
    # z-axis.
    if z != 0:
        angle = acos(z / length)
    else:
        angle = 90
    if x < 0:
        angle = -angle

    # To calculate the dihedral we just need the x and y coordinates.
    if x != 0:
        dihedral = atan(y / x)
    else:
        if y > 0:
            dihedral = 90
        elif y < 0:
            dihedral = -90
        else:
            dihedral = 0

    return [angle, dihedral, length]


def print_cartesian(atoms, coords, precision):
    """ Print the given set of atoms and corresponding positions """

    for number in sorted(atoms.keys()):
        if number >= 0:
            print("{} {} {} {}".format(
                    atoms[number],
                    round(coords[number][0] + 10**(-precision - 2), precision),
                    round(coords[number][1] + 10**(-precision - 2), precision),
                    round(coords[number][2] + 10**(-precision - 2), precision)))


def to_cartesian(zmat):
    """ Convert the given z-matrix to cartesian coordinates.
    
        >>> atoms, coords = to_cartesian("O")
        >>> print_cartesian(atoms, coords, 2)
        O 0.0 0.0 0.0
        >>> atoms, coords = to_cartesian("O\\nH 0 1")
        >>> print_cartesian(atoms, coords, 2)
        O 0.0 0.0 0.0
        H 0.0 0.0 1.0
        >>> atoms, coords = to_cartesian("O\\nH 0 1\\nH 0 1 1 90")
        >>> print_cartesian(atoms, coords, 2)
        O 0.0 0.0 0.0
        H 0.0 0.0 1.0
        H -1.0 0.0 0.0
        >>> atoms, coords = to_cartesian("C\\nH 0 1\\nH 0 1 1 90\\nH 0 1 1 90 2 90")
        >>> print_cartesian(atoms, coords, 2)
        C 0.0 0.0 0.0
        H 0.0 0.0 1.0
        H -1.0 0.0 0.0
        H 0.0 1.0 0.0
        >>> atoms, coords = to_cartesian("C\\nH 0 1\\nH 0 1 1 109\\nH 0 1 1 109 2 120\\nH 0 1 1 109 2 -120")
        >>> print_cartesian(atoms, coords, 2)
        C 0.0 0.0 0.0
        H 0.0 0.0 1.0
        H -0.95 0.0 0.33
        H 0.47 0.82 0.33
        H 0.47 -0.82 0.33
        >>> atoms, coords = to_cartesian("O\\nO 0 1\\nH 1 1 0 0")
        >>> print_cartesian(atoms, coords, 2)
        O 0.0 0.0 0.0
        O 0.0 0.0 1.0
        H 0.0 0.0 2.0
        >>> atoms, coords = to_cartesian("O\\nO 0 1\\nH 1 1 0 180")
        >>> print_cartesian(atoms, coords, 2)
        O 0.0 0.0 0.0
        O 0.0 0.0 1.0
        H 0.0 0.0 0.0
        >>> atoms, coords = to_cartesian("O\\nO 0 1\\nH 1 1 0 45")
        >>> print_cartesian(atoms, coords, 2)
        O 0.0 0.0 0.0
        O 0.0 0.0 1.0
        H 0.71 0.0 1.71
        >>> atoms, coords = to_cartesian("O\\nO 0 1\\nO 0 1 1 90\\nH 0 1 1 -90 2 45")
        >>> print_cartesian(atoms, coords, 2)
        O 0.0 0.0 0.0
        O 0.0 0.0 1.0
        O -1.0 0.0 0.0
        H 0.71 -0.71 0.0
        >>> atoms, coords = to_cartesian("O\\nO 0 1\\nO 0 1 1 -90\\nH 2 1 0 90 1 0")
        >>> print_cartesian(atoms, coords, 2)
        O 0.0 0.0 0.0
        O 0.0 0.0 1.0
        O 1.0 0.0 0.0
        H 1.0 0.0 1.0
        >>> atoms, coords = to_cartesian("O\\nO 0 1\\nO 0 1 1 -90\\nH 2 1 0 90 1 45")
        >>> print_cartesian(atoms, coords, 2)
        O 0.0 0.0 0.0
        O 0.0 0.0 1.0
        O 1.0 0.0 0.0
        H 1.0 0.71 0.71
        >>> atoms, coords = to_cartesian("O\\nO 0 1\\nO 0 1 1 90\\nH 1 1 0 90 2 45")
        >>> print_cartesian(atoms, coords, 2)
        O 0.0 0.0 0.0
        O 0.0 0.0 1.0
        O -1.0 0.0 0.0
        H 0.71 0.71 1.0
    """

    # Initialise with dummy points; these are used to place the first few
    # atoms.
    coords = {-1: (0, 0, 0), -2: (0, 0, -1), -3: (1, 0, 0)}
    atoms = {}

    # Parse the z-matrix.
    for number, line in enumerate(zmat.splitlines()):
        # Each line in a z-matrix is of the form:
        # atom, first, distance, second, angle, third, dihedral
        # where first, second, third are the adjacent atoms, the atom
        # determining the angle, and a third atom determining the plane to
        # use when taking into account the dihedral.

        # Parse the line into the fields.
        atom = [None, -1, 0, -2, 0, -3, 0] # Set default values.
        for i, v in enumerate(line.split()):
            atom[i] = v
        name = atom[0]
        first = coords[int(atom[1])]
        distance = float(atom[2])
        second = coords[int(atom[3])]
        angle = float(atom[4])
        third = coords[int(atom[5])]
        dihedral = float(atom[6])

        # The general approach here is to start by assuming that the first
        # point is at the origin, the second point is some negative distance 
        # along the z-axis, and the third point is elsewhere in the x-z plane.
        # This lets us place the new atom easily.
        # From this we then apply transformations to actually move the other
        # points so that they fit the above description, and the apply the
        # inverse transformations in reverse order to the main point.
        # This leaves us with a point in the correct position.

        # Translate the new, second and third points so that they remain in the
        # same place relative to the first, but the first is now at the origin.
        second = [second[i] - first[i] for i in range(3)]
        third = [third[i] - first[i] for i in range(3)]
        translate = lambda pos: [pos[i] + first[i] for i in range(3)]

        # Rotate the new, second and third points so that the second point is
        # on the negative side of the z-axis (polar coordinates [180, 0, l]).
        # The rotation needs to be distance and angle-preserving; to ensure
        # that we always rotate through the dihedral first (a rotation around
        # the z-axis) and then rotate around the y-axis using the angle, since
        # the dihedral is 0 so the second point should now be on the x-z plane.
        rotation = cartesian_to_polar(*second)
        rotation[0] = 180 + rotation[0]
        third_polar = cartesian_to_polar(*third)
        third_polar[1] -= rotation[1]
        third = polar_to_cartesian(*third_polar)
        t0 = cos(-rotation[0]) * third[0] - sin(-rotation[0]) * third[2]
        t2 = cos(-rotation[0]) * third[2] + sin(-rotation[0]) * third[0]
        third[0] = t0
        third[2] = t2
        def rotate_angle(pos_polar):
            pos_polar[1] += rotation[1]
            pos = polar_to_cartesian(*pos_polar)
            p0 = cos(rotation[0]) * pos[0] - sin(rotation[0]) * pos[2]
            p2 = cos(rotation[0]) * pos[2] + sin(rotation[0]) * pos[0]
            pos[0] = p0
            pos[2] = p2
            return pos

        # Rotate the new and third points so that the third point is on the
        # x-z plane. Fortunately this is relatively simple; we just need to
        # set the dihedral to 0.
        third_polar = cartesian_to_polar(*third)
        def rotate_dihedral(pos_polar):
            pos_polar[1] += third_polar[1]
            return pos_polar

        # Apply the accumulated transformations.
        pos = translate(\
                rotate_angle(\
                rotate_dihedral([angle, dihedral, distance])))

        atoms[number] = name
        coords[number] = pos

    return atoms, coords


if __name__ == "__main__":
    import doctest
    doctest.testmod()
