""" Simple pygame 2D physics engine

    Author: Alastair Hughes
    Contact: <hobbitalastair at yandex dot com>
"""

import pygame, pygame.display, pygame.event, pygame.time, pygame.transform, \
    pygame.mouse
import math


class physical():
    """ Define a simple object to move in the pygame world """

    def __init__(self, x, y, surf):
        """ Create a new object at the given x/y coords """

        # Velocity and position, in pixels.
        self.pos = [x, y] # Centered position of the object.
        self.vel = [0, 0] # X/Y speed in pixels.
        self.acc = [0, 0] # Temporary acceleration value.

        # Angle and rotation velocity, in rads.
        self.angle = 0 # Current angle of the object.
        self.rot_vel = 0 # Rotation velocity.
        self.rot_acc = 0 # Temporary acceleration value.
        
        self.surf = surf
        self.size = surf.get_size()

        self.mass = 1
        # Approximated moment of intertia for rotation around the object's
        # center.
        self.moi = self.size[0] * self.size[1] * self.mass

    def render(self, display):
        """ Render self onto a display """

        surf = pygame.transform.rotate(self.surf, -math.degrees(self.angle))
        size = surf.get_size()

        display.blit(surf, [self.pos[i] - (size[i] / 2) for i in range(2)])

    def update(self, elapsed_time):
        """ Update self's position based on the elapsed time (in seconds) and
            velocity.
        """

        # Apply the acceleration.
        for i in range(2):
            self.vel[i] += self.acc[i] * elapsed_time
        self.rot_vel += (self.rot_acc * elapsed_time)
        self.acc = [0, 0]
        self.rot_acc = 0
        
        # Apply the position.
        for i in range(2):
            self.pos[i] += (self.vel[i] * elapsed_time)
            self.angle = (self.angle + (self.rot_vel * elapsed_time)) % \
                (2 * math.pi)

        # Apply the drag.
        # TODO: This is a hack. Unfortunately, proper drag is complex...
        square.vel = [square.vel[i] * .90 for i in range(2)] # Drag
        square.rot_vel *= .90 # Drag

    def anchor(self, offset):
        """ Return the new position of an anchor, taking into account
            rotation.
        """

        return [offset[0] * math.cos(self.angle) - \
                    offset[1] * math.sin(self.angle), \
                offset[0] * math.sin(self.angle) + \
                    offset[1] * math.cos(self.angle)]

    def pull(self, point, force):
        """ Apply a force vector at the given point from the center of the
            object. Note that both the force and the point are given as a
            2-tuple vector.
        """

        offset = [point[i] - self.pos[i] for i in range(2)]

        if offset[0] == 0 and offset[1] == 0:
            # Shortcut; apply the force directly.
            for i in range(2):
                self.acc[i] += force[i] / self.mass
            return

        # We start by finding offset_unit, ie the unit vector of the offset.
        offset_size = magnitude(offset)
        offset_unit = [offset[i] / offset_size for i in range(2)]
        assert .99 < magnitude(offset_unit) < 1.01
        
        # Now we find the force component parallel to the offset.
        force_par = dot_product(force, offset_unit)
        force_perp_vector = [force[i] - (force_par * offset_unit[i])
                for i in range(2)]
        force_perp = magnitude(force_perp_vector)

        # Now figure out whether the perp force is clockwise or
        # counterclockwise.
        # We use a dot product of the combined vector rotated 90 degrees
        # anticlockwise and the offset unit vector, which is 0 if the
        # perpendicular is 0, >0 if the rotation is clockwise, <0 if the
        # rotation is anticlockwise.
        combined = [offset_unit[i] + force_perp_vector[i] for i in range(2)]
        dotted = dot_product([combined[1], -combined[0]], offset_unit)
        try:
            direction = dotted / abs(dotted)
        except ZeroDivisionError:
            direction = 0
        
        # Apply the parallel force...
        for i in range(2):
            self.acc[i] += force[i] / self.mass
        # Apply the perpendicular force.
        self.rot_acc += direction * (offset_size * force_perp) / self.moi


class objectAnchor():
    """ Provide a generic 'object' anchor """

    def __init__(self, item, offset):
        """ Initialise self.
            
            'item' is the object to anchor to, and offset is the offset from
            the item's reported position - taking into account rotation.
        """

        self.item = item
        self.offset = offset

    def pos(self):
        """ Print the current absolute position of the anchor """

        return [self.item.anchor(self.offset)[i] + self.item.pos[i]
                for i in range(2)]

    def pull(self, force):
        """ Pull the given anchor """

        self.item.pull(self.pos(), force)


class funcAnchor():
    """ Provide a generic anchor using 'func' for the position """

    def __init__(self, func):
        """ Initialise self """

        self.func = func

    def pos(self):
        """ Print the current value of the given function """

        return self.func()

    def pull(self, force):
        """ We ignore this; no pull func is provided """

        pass


class yank():
    """ Join two anchors with a piece of 'elastic' """

    def __init__(self, first, second, color = (255, 0, 0)):
        """ Initialies self.
            
            Join the 'first' and 'second' anchors.
        """

        self.first = first
        self.second = second
        self.color = color

    def render(self, display):
        """ Render self onto the display """
        pygame.draw.line(display, self.color, self.first.pos(),
                self.second.pos())

    def update(self, elapsed_time):
        """ Apply this anchor.
        
            We ignore the elapsed time, as "pull" only updates the
            acceleration, not applying it.
        """

        # Find the force (the diff in this case).
        force = [self.second.pos()[i] - self.first.pos()[i] for i in range(2)]
        # Pull the objects towards each other.
        self.first.pull(force)
        self.second.pull([-force[i] for i in range(2)])


def dot_product(v1, v2):
    """ Return the dot product of two vectors """
    if len(v1) != len(v2):
        raise ValueError("Cannot return the dot product of two vectors with different lengths!")
    return sum([v1[i] * v2[i] for i in range(len(v1))])

def magnitude(vector):
    """ Return the magnitude of the vector """
    return math.sqrt(sum([vector[i]**2 for i in range(len(vector))]))


if __name__ == "__main__":

    # Set the FPS.
    FPS = 60

    # Initialise pygame.
    pygame.init()
    screen = pygame.display.set_mode()

    # Create the lists of objects and joints.
    objects = []
    joints = []

    # Setup.
    # Create the objects.
    surf = pygame.Surface((50, 50), flags = pygame.SRCALPHA)
    surf.fill((255, 255, 255))
    square = physical(25, 25, surf)
    square.pos = [screen.get_width() / 2, screen.get_height() / 2 - 50]
    objects.append(square)
    surf = pygame.Surface((50, 50), flags = pygame.SRCALPHA)
    surf.fill((0, 255, 0))
    square2 = physical(25, 25, surf)
    square2.pos = [screen.get_width() / 2, screen.get_height() / 2 + 40]
    objects.append(square2)
    # Create the joints.
    mouseAnchor = funcAnchor(pygame.mouse.get_pos)
    joints.append(yank(mouseAnchor, objectAnchor(square, [-25, -25])))
    joints.append(yank(mouseAnchor, objectAnchor(square, [25, -25])))

    # Move the mouse to the screen center.
    pygame.mouse.set_pos(square.pos)

    # Main loop.
    running = True
    old_time = 0
    last_time = pygame.time.get_ticks()
    while running:
        # Find the start time.
        old_time = last_time
        last_time = pygame.time.get_ticks()
        
        # Update the screen.
        pygame.display.update()

        # Render to the screen.
        screen.fill((0, 0, 0))

        # Update the objects.
        for obj in objects:
            # Move the object.
            obj.update((last_time - old_time) / 1000)
            obj.render(screen)

            # Wall collision detection.
            for i in range(2):
                new = min(max(obj.pos[i], 0), screen.get_size()[i])
                if new != obj.pos[i]:
                    obj.vel[i] = -obj.vel[i]
                obj.pos[i] = new

        # Update the joints.
        for joint in joints:
            # Update the joint.
            joint.update((last_time - old_time) / 1000)
            joint.render(screen)

        # Collision detection.
        # TODO: Move elsewhere...
        # TODO: Properly implement.
        # TODO: Either the bounding box code or the overlap code seems a bit buggy...
        bbox = lambda obj: [[obj.pos[i] + (obj.size[i] / 2) for i in range(2)],
                [obj.pos[i] - (obj.size[i] / 2) for i in range(2)]]
        def overlap(bb1, bb2):
            for i in range(2):
                if not (bb1[1][i] <= bb2[0][i] and bb2[1][i] <= bb1[0][i]):
                    return False
            return True
        def intersect(l1, l2):
            """ Return the point of intersection of two lines as given.
                Lines are pairs of (absolute) points.
                If there is no intersection, return None.
            """
            # We solve the equation [(u2 - u1) (v2 - v1)][c1 c2] = [v1 - u1],
            # where u1, u2 are the points of l1, v1, v2 are the points of l2.
            # ie: c1(u2 - u1) + u1 = c2(v2 - v1) + v1
            # The solution that we are looking for is c1(u2 - u1) + u1; that
            # should be the point of intersection.
            # We use the matrix inverse...
            u1, u2 = l1
            v1, v2 = l2
            a = u2[0] - u1[0]
            b = v2[0] - v1[0]
            c = u2[1] - u1[1]
            d = v2[1] - v1[1]
            det = a*d - b*c
            if det == 0:
                return None
            add = lambda vec1, vec2: [vec1[i] + vec2[i] for i in range(len(vec1))]
            mult = lambda scalar, vec: [scalar*i for i in vec]
            c1 = (1/det)*((v1[0] - u1[0])*d - (v1[1] - u1[1])*b)
            # Why do we need the second one??
            c2 = (1/det)*((v2[0] - u2[0])*(-c) + (v2[1] - u2[1])*a)
            # We now check that c1 is between some appropriate bounds...
            if c1 >= 1 or c1 <= 0:
                return None
            # Also check c2 (why?)
            if c2 >= 1 or c2 <= 0:
                return None
            return add(add(mult(c1, u2), mult(-c1, u1)), u1)
        def lines(obj):
            """ Return a list of lines in the given object """
            # TODO: Add rotation.
            tot = lambda pos: [int(pos[i]+obj.pos[i]) for i in range(2)]
            a1 = tot(obj.anchor((25, 25)))
            a2 = tot(obj.anchor((25, -25)))
            a3 = tot(obj.anchor((-25, -25)))
            a4 = tot(obj.anchor((-25, 25)))
            return [a1, a2], [a2, a3], [a3, a4], [a4, a1]
        for i, obj1 in enumerate(objects):
            for obj2 in objects[:i]:
                bb1 = bbox(obj1)
                bb2 = bbox(obj2)
                points = []
                if overlap(bb1, bb2):
                    pygame.draw.rect(screen, (255, 0, 0), pygame.Rect(0, 0, 10, 10))
                    for l1 in lines(obj1):
                        for l2 in lines(obj2):
                            if intersect(l1, l2) != None:
                                points.append(intersect(l1, l2))
                                pygame.draw.circle(screen, (0, 0, 255), [int(i) for i in intersect(l1, l2)], 3)
                if len(points) > 0:
                    # We have a collision!
                    # Find the center.
                    p = [int(sum(i)/len(points)) for i in zip(*points)]
                    pygame.draw.circle(screen, (255, 0, 0), p, 5)
                    # Find the two relative movements of the given point.
                    # The point velocity is the object movement added to the
                    # rotational component (the rotation velocity in
                    # rad/s * radius * the offset vector rotated 90 degrees).
                    mult = lambda scalar, vec: [scalar*i for i in vec]
                    offset1 = [p[i] - obj1.pos[i] for i in range(2)]
                    obj1vec = obj1.vel + mult(obj1.rot_vel*magnitude(offset1), \
                            [-offset1[1], offset1[0]])
                    offset2 = [p[i] - obj2.pos[i] for i in range(2)]
                    obj2vec = obj2.vel + mult(obj2.rot_vel*magnitude(offset2), \
                            [-offset2[1], offset2[0]])
                    # Calculate the relative vectors.
                    rel1vec = [obj1vec[i] - obj2vec[i] for i in range(2)]
                    rel2vec = [obj2vec[i] - obj1vec[i] for i in range(2)]
                    # Figure out what the new velocities should be.
                    # TODO: Implement this properly...
                    # This is just a hack!!
                    pygame.draw.line(screen, (255, 0, 255), p, [p[i] + rel1vec[i] for i in range(2)])
                    pygame.draw.line(screen, (255, 255, 0), p, [p[i] + rel2vec[i] for i in range(2)])
                    obj1.pull(p, [rel2vec[i]*100 for i in range(2)])
                    obj2.pull(p, [rel1vec[i]*100 for i in range(2)])


        # Handle events.
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                running = False
            elif event.type == pygame.KEYDOWN:
                pygame.quit()
                running = False

        # Wait...
        elapsed_time = pygame.time.get_ticks() - last_time
        time_per_frame = 1000 / FPS
        if elapsed_time > time_per_frame:
            print("WARNING: allowed time per frame exceeded")
        else:
            pygame.time.wait(int(time_per_frame - elapsed_time))
    
