import pygame.display, pygame.event, pygame.time
from pygame import Color


TARGET_FRAMERATE = 30
track_color = Color(0, 0, 0, 255)
background_color = Color(0, 255, 0, 255)
active_color = Color(255, 0, 0, 255)

class Segment:
    def __init__(self, pos):
        self.pos = pos
        # We have two potential directions, so have both sets of links.
        self.conn = ([], [])

    def __hash__(self):
        # Assume that positions are unique.
        return hash(self.pos)


class State:
    def __init__(self):
        self.links = set()
        self.segments = set()
        self.selected = None


def redraw(screen, state):
    screen.fill(background_color)
    for link in state.links:
        pygame.draw.line(screen, track_color, link[0].pos, link[2].pos)

    if state.selected != None:
        segment = state.selected[0]
        side = state.selected[1]
        if len(segment.conn[side]) == 0:
            pygame.draw.circle(screen, active_color, segment.pos, 2)
        else:
            for s2 in segment.conn[side]:
                pygame.draw.line(screen, active_color, segment.pos, s2.pos)

    pygame.display.flip()


def tick(state):
    return state


def link(state, s1, s2):
    s1.conn[0].append(s2)
    s2.conn[1].append(s1)

    state.links.add((s1, 0, s2, 1))
    state.segments.add(s1)
    state.segments.add(s2)


def init_state():
    state = State()

    s1 = Segment((5, 5))
    s2 = Segment((5, 25))
    link(state, s1, s2)
    s3 = Segment((25, 25))
    link(state, s2, s3)
    s4 = Segment((25, 5))
    link(state, s3, s4)
    link(state, s4, s1)
    s5 = Segment((5, 0))
    link(state, s4, s5)

    return state


def distance_squared(p1, p2):
    return (p1[0] - p2[0])**2 + (p1[1] - p2[1])**2


if __name__ == "__main__":
    pygame.display.init()
    screen = pygame.display.set_mode()

    state = init_state()
    clock = pygame.time.Clock()

    running = True
    while running:

        redraw(screen, state)
        state = tick(state)

        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                running = False
            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_q:
                    running = False
                if state.selected is not None:
                    if ev.key == pygame.K_RETURN:
                        state.selected[1] = (state.selected[1] + 1) % 2
                    if ev.key == pygame.K_BACKSPACE:
                        segment = state.selected[0]
                        side = state.selected[1]

                        for joined in segment.conn[side]:
                            if segment in joined.conn[0]:
                                state.links.discard((segment, side, joined, 0))
                                state.links.discard((joined, 0, segment, side))
                                joined.conn[0].remove(segment)
                            if segment in joined.conn[1]:
                                state.links.discard((segment, side, joined, 1))
                                state.links.discard((joined, 1, segment, side))
                                joined.conn[1].remove(segment)
                            segment.conn[side].remove(joined)

                        if len(segment.conn[0]) == 0 and len(segment.conn[1]) == 0:
                            state.segments.remove(segment)
                            state.selected = None

            if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                state.selected = None
                for segment in state.segments:
                    if distance_squared(ev.pos, segment.pos) <= 9:
                        state.selected = [segment, 1]


        clock.tick(TARGET_FRAMERATE)

