import itertools

import search
import random
import math



ids = ["206100224", "313088692"]


class OnePieceProblem(search.Problem):
    """This class implements a medical problem according to problem description file"""

    def __init__(self, initial):
        """Creates the initial state, a tuple of the following variables:
        treasure_base: binary indicators for treasures in the base
        pirate_ships: tuple of tuples (ship name, location, binary indicators for treasures spots
        marine_tuple: tuple of tuples (marine name, path, forward backward indicator, index of location
        treasures: tuple of tuples (treasure name, treasure location)"""

        base = [(index, row.index('B')) for index, row in enumerate(initial['map']) if 'B' in row] #find base
        self.base_location = base[0]
        self.map = initial['map']
        treasures_base = [0] * len(initial['treasures'])
        pirate_ships = []
        for pirate in initial['pirate_ships']:
            pirate_ship = (pirate, initial['pirate_ships'][pirate], (0, 0))
            pirate_ships.append(pirate_ship)
        self.marine_ships = []
        for marine in initial['marine_ships']:
            marine_ship = [marine, initial['marine_ships'][marine] + initial['marine_ships'][marine][-2:0:-1], 0]
            self.marine_ships.append(marine_ship)
        marine_tuple = []
        for marine in initial['marine_ships']:
            marine_ship = (marine, tuple(initial['marine_ships'][marine]), 0, "f")
            marine_tuple.append(marine_ship)
        treasures = []
        for treasure in initial['treasures']:
            treasure = (treasure, initial['treasures'][treasure])
            treasures.append(treasure)
        initial_tuple = (tuple(treasures_base), tuple(pirate_ships), tuple(marine_tuple), tuple(treasures))
        search.Problem.__init__(self, initial_tuple)

    def actions(self, state):
        """Returns all the actions that can be executed in the given
        state"""

        this_turn = []
        multiple_ships = []
        for pirate in state[1]:
            actions = []
            [x, y] = pirate[1]
            """sail actions"""
            if valid_index(self.map, x + 1, y):
                if (self.map[x + 1][y] == 'S' or self.map[x + 1][y] =='B'):
                    actions.append(("sail", pirate[0], (x+1, y)))
            if valid_index(self.map, x-1, y):
                if (self.map[x - 1][y] == 'S' or self.map[x - 1][y] == 'B'):
                    actions.append(("sail", pirate[0], (x-1, y)))
            if valid_index(self.map, x, y+1):
                if (self.map[x][y + 1] == 'S' or self.map[x][y + 1] == 'B'):
                    actions.append(("sail", pirate[0], (x, y+1)))
            if valid_index(self.map, x, y-1):
                if (self.map[x][y-1] == 'S' or self.map[x][y-1] == 'B'):
                    actions.append(("sail", pirate[0], (x, y-1)))
            """Collect Treasure actions"""
            if pirate[2][0] == 0 or pirate[2][1] == 0:
                if valid_index(self.map, x+1, y):
                    if self.map[x + 1][y] == 'I':
                        for treasure in state[3]:
                            if treasure[1] == (x+1,y) and not collected(state, treasure[0], this_turn):
                                actions.append(("collect_treasure", pirate[0], treasure[0]))
                                this_turn.append(treasure[0])
                if valid_index(self.map, x - 1, y):
                    if self.map[x - 1][y] == 'I':
                        for treasure in state[3]:
                            if treasure[1] == (x - 1, y) and not collected(state, treasure[0], this_turn):
                                actions.append(("collect_treasure", pirate[0], treasure[0]))
                                this_turn.append(treasure[0])
                if valid_index(self.map, x, y+1):
                    if self.map[x][y + 1] == 'I':
                        for treasure in state[3]:
                            if treasure[1] == (x, y + 1) and not collected(state, treasure[0], this_turn):
                                actions.append(("collect_treasure", pirate[0], treasure[0]))
                                this_turn.append(treasure[0])
                if valid_index(self.map, x, y-1):
                    if self.map[x][y - 1] == 'I':
                        for treasure in state[3]:
                            if treasure[1] == (x, y - 1) and not collected(state, treasure[0], this_turn):
                                actions.append(("collect_treasure", pirate[0], treasure[0]))
                                this_turn.append(treasure[0])
            """deposit Treasure actions"""
            if self.map[pirate[1][0]][pirate[1][1]] == 'B':
                if pirate[2] != (0, 0):
                    actions.append(("deposit_treasure", pirate[0]))
            if pirate[2] != (0, 0):
                actions.append(("wait", pirate[0]))
            multiple_ships.append(actions)
        combinations = list(itertools.product(*multiple_ships))
        return combinations

    def result(self, state, actions):
        """Return the state that results from executing the given
        action in the given state. The action must be one of
        self.actions(state)."""

        # updates the location of all marines ships
        state = self.update_marines(state)
        treasure_base = list(state[0])
        pirates = list(state[1])
        new_pirates = []
        for i in range(len(pirates)):
            if actions[i][0] == "wait":
                new_pirates.append(pirates[i])

            if actions[i][0] == 'sail':
               new_pirates.append((pirates[i][0], actions[i][2], pirates[i][2]))


            if actions[i][0] == 'collect_treasure':
                if pirates[i][2][0] == 0:
                    new_pirates.append((pirates[i][0], pirates[i][1], (actions[i][2], 0)))
                elif pirates[i][2][1] == 0:
                    new_pirates.append((pirates[i][0], pirates[i][1], (pirates[i][2][0], actions[i][2])))

            if actions[i][0] == 'deposit_treasure':
                if pirates[i][2][0] != 0:
                    for j, t in enumerate(treasure_base):
                        if t == 0:
                            treasure_base[j] = pirates[i][2][0]
                            break
                if pirates[i][2][1] != 0:
                    for j, t in enumerate(treasure_base):
                        if t == 0:
                            treasure_base[j] = pirates[i][2][1]
                            break
                new_pirates.append((pirates[i][0], pirates[i][1], (0, 0)))

        state = tuple(treasure_base), tuple(new_pirates), state[2], state[3]
        # removes all treasures from pirate ship in same location as marine
        state = update_marine_pirate(state)
        return state

    def goal_test(self, state):
        """ Given a state, checks if this is the goal state.
         Returns True if it is, False otherwise."""
        for t in state[0]:
            if t == 0:
                return False
        return True

    def h(self, node):
        """ This is the heuristic. It gets a node (not a state,
        state can be accessed via node.state)
        and returns a goal distance estimate"""
        return self.h_2(node) + 3 * self.h_1(node)


    def h_1(self, node):
        num_of_uncollected = 0
        on_ship = set()
        for ship in node.state[1]:
            on_ship.add(ship[2][0])
            on_ship.add(ship[2][1])
        for treasure in node.state[3]:
            if treasure[0] not in node.state[0] and treasure[0] not in on_ship:
                num_of_uncollected += 1
        return len(node.state[1]) * num_of_uncollected/len(node.state[1])


    def h_2(self, node):
        sum_of_distances = 0
        on_ship = []
        for treasure in node.state[3]:
            for ship in node.state[1]:
                if ship[2][0] == treasure[0] or ship[2][1] == treasure[0]:
                    on_ship.append(treasure[0])
                    sum_of_distances += abs(ship[1][0] - self.base_location[0]) + abs(ship[1][1] - self.base_location[1])

        for treasure in node.state[3]:
            if not treasure[0] in node.state[0] and not treasure[0] in on_ship:
                [x, y] = treasure[1]
                adj = [(x-1,y),(x+1,y),(x, y+1), (x, y-1)]
                adj = [a for a in adj if (valid_index(self.map, a[0], a[1]) and self.map[a[0]][a[1]] == "S")]
                if not adj:
                    return float('inf')
                distances_from_base = [abs(x[0] - self.base_location[0]) + abs(x[1] - self.base_location[1]) for x in adj]
                sum_of_distances += min(distances_from_base)
            return sum_of_distances/len(node.state[1])

    def update_marines(self, state):
        """update marines"""
        new_marines_state = []
        for i, marine in enumerate (state[2]):
            if len(marine[1]) == 1:
                new_marines_state.append((marine[0], marine[1], marine[2], marine[3]))
                continue
            marine = list(marine)
            if marine[3] == 'f':
                if marine[1][marine[2]] == marine[1][-1]:
                    marine[3] = 'b'
                else:
                    marine[2] += 1
            if marine[3] == 'b':
                if marine[1][marine[2]] == marine[1][0]:
                    marine[3] = 'f'
                    marine[2] += 1
                else:
                    marine[2] -= 1
            new_marines_state.append((marine[0], marine[1], marine[2], marine[3]))
        return (state[0], state[1], tuple(new_marines_state), state[3])


    """Feel free to add your own functions
    (-2, -2, None) means there was a timeout"""



def create_onepiece_problem(game):
    return OnePieceProblem(game)


def valid_index(A, x, y):
    if x < len(A) and len(A[0]) > y >= 0 and x >=0:
        return True
    return False

def update_marine_pirate(state):
    new_pirate_state = []
    for pirate in state[1]:
        pirate = list(pirate)
        for marine in state[2]:
            if marine[1][marine[2]] == pirate[1]:
                pirate[2] = (0, 0)
        new_pirate_state.append(tuple(pirate))
    return (state[0], tuple(new_pirate_state), state[2], state[3])


def collected(state, treasure_name, this_turn):
    for pirate in state[1]:
        if pirate[2][0] == treasure_name or pirate[2][1] == treasure_name:
            return True
        if treasure_name in this_turn:
            return True
        if treasure_name in state[0]:
            return True
    return False

