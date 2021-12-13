from __future__ import annotations
from typing import Iterator, Mapping, Optional, Tuple
import math
import time
from enum import Enum

Point = Tuple[int, int]

CARDINALS: list[Point] = [(0, -1), (-1, 0), (1, 0), (0, 1)]
DIAGONALS: list[Point] = [(-1, -1), (1, -1), (-1, 1), (1, 1)]
ADJACENTS: list[Point] = [
    DIAGONALS[0], CARDINALS[0], DIAGONALS[1],
    *CARDINALS[1:3],
    DIAGONALS[2], CARDINALS[3], DIAGONALS[3],
]

class Directions(Enum):
    adjacent = ADJACENTS
    cardinals = CARDINALS
    diagonals = DIAGONALS


class Node:
    def __init__(self, value, x, y):
        self.value =  value
        self.x = x
        self.y = y

    def __repr__(self):
        return f"<Node value={self.value} position=({self.x}, {self.y})>"

    def __eq__(self, other) -> bool:
        if not isinstance(other, Node):
            raise NotImplemented
        return self.position == other.position

    def __hash__(self) -> int:
        return hash(self.position)

    @property
    def position(self) -> Point:
        return (self.x, self.y)


class Grid(Mapping):
    def __init__(self, nodes: list[Node], width: int, height: int):
        self.nodes = nodes
        self.width = width
        self.height = height

    def __repr__(self):
        ret = ""
        for y in range(self.height):
            for x in range(self.width):
                ret += self[(x, y)].value
            ret += '\n'
        return ret

    @classmethod
    def from_text(cls, text: str):
        nodes, width, height = [], 0, 0
        for y, line in enumerate(text.strip().splitlines()):
            height += 1
            width = len(line.strip())
            for x, value in enumerate(line.strip()):
                nodes.append(Node(value, x, y))
        return cls(nodes=nodes, width=width, height=height)

    def __getitem__(self, key: Point) -> Node:
        x, y = key
        index = x + self.width * y
        try:
            return self.nodes[index]
        except IndexError:
            raise KeyError

    def __iter__(self) -> Iterator[Node]:
        return iter(self.nodes)

    def __len__(self):
        return len(self.nodes)


    def neighbours(self, node: Node, directions: Directions) -> Iterator[Node]:
        points = []
        for point in directions.value:
            x, y = point
            x, y = node.x+x, node.y+y
            if x<0 or y<0:
                pass
            else:
                points.append(self.get((x, y), None))
        return filter(None, points)


    def cardinals(self, node: Node) -> Iterator[Node]:
        return self.neighbours(node, Directions.cardinals)

    def diagonals(self, node: Node) -> Iterator[Node]:
        return self.neighbours(node, Directions.diagonals)

    def adjacent(self, node: Node) -> Iterator[Optional[Node]]:
        return self.neighbours(node, Directions.adjacent)

    @staticmethod
    def distance(a: Node, b: Node) -> float:
        return math.sqrt((a.x-b.x)**2 + (a.y-b.y)**2)

    def traversable(self, node: Node) -> bool:
        return node.value != '#'

    def astar(self, start: Node, goal: Node) -> list[Node]:
        '''
        Returns the shortest path from start to goal using A* algorithm
        '''
        # first is the node it came from, second is its G+H cost
        already_visited: dict[Node, tuple[Node, float]] = {
            start: (None, self.distance(start, goal))
        }
        to_visit: dict[Node, tuple[Node, float]] = {
            start: (None, self.distance(start, goal))
        }
        path = []
        def debug():
            ret = ""
            for y in range(self.height):
                for x in range(self.width):
                    node = self[(x, y)]
                    if node in path:
                        node = f"\u001b[38;5;69m{node.value}\u001b[0m"
                    elif node in already_visited:
                        node = f"\u001b[38;5;196m{node.value}\u001b[0m"
                    elif node in to_visit:
                        node = f"\u001b[38;5;118m{node.value}\u001b[0m"
                    else:
                        node = node.value
                    ret += node
                ret += "\n"
            print("\033[2J")
            print(ret)
            time.sleep(0.25)

        visiting = start
        while to_visit:
            debug()
            nodes = self.cardinals(visiting)
            for node in nodes:
                if not self.traversable(node):
                    continue
                if node in already_visited:
                    continue
                g_cost = self.distance(visiting, node)
                h_cost = self.distance(goal, node)
                cost = g_cost + h_cost
                old_node = to_visit.get(node)
                if old_node and old_node[1] < cost:
                    continue
                to_visit[node] = (visiting, cost)
            visiting = min(to_visit, key=lambda x: to_visit[x][1])
            already_visited[visiting] = to_visit[visiting]
            del to_visit[visiting]
            if visiting == goal:
                path.append(visiting)
                node = visiting
                while True:
                    node = already_visited[node][0]
                    if node is None:
                        break
                    path.append(node)
                    debug()
                return list(reversed(path))
        return path



data = '''
..........
...#.B....
....#.....
.#########
..........
#########.
..........
..........
..A.......
..........
'''

grid = Grid.from_text(data)

A = grid[2, 8]
B = grid[5, 1]
grid.astar(A, B)
