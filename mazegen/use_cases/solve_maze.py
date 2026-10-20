from collections import deque
from typing import List, Set, Optional, Dict, Tuple

from mazegen.entities import (
    DIRECTION_DELTA,
    DIRECTION_COORDINATES,
    OPPOSITE,
    Maze,
    Cell,
    WALLS
)


class MazeSolver:

    def solve(self, maze: Maze) -> List[str]:

        entry = maze.entry
        exit = maze.exit

        self.cells: List[Cell] = []
        self.queue: deque[Tuple[int, int]] = deque()
        self.visited: Set[Tuple[int, int]] = set()
        self.origin: Dict[Tuple[int, int], Optional[str]] = {}

        self.queue.append(maze.entry)
        self.visited.add(maze.entry)
        self.origin[maze.entry] = None

        for line in maze.cells:
            for cell in line:
                if cell.x == maze.entry[0] and cell.y == maze.entry[1]:
                    cell.visited = True
                else:
                    cell.visited = False
                self.cells.append(cell)

        while len(self.queue) != 0:
            coordinates = self.queue.popleft()
            if coordinates == exit:
                break
            else:
                self.visited.add(coordinates)
                to_visit = self.check_neighbor(coordinates)

                for element in to_visit:
                    coordinate = element[0]
                    direction = element[1]
                    if coordinate not in self.origin.keys():
                        self.origin[coordinate] = direction
                    if coordinate not in self.visited:
                        self.queue.append(coordinate)
                        self.visited.add(coordinate)

        solution: List[str] = []
        coordinate = exit

        while coordinate != entry:
            move = self.origin[coordinate]
            assert move is not None
            solution.append(move)
            direction_key = DIRECTION_COORDINATES[move]
            delta = DIRECTION_DELTA[OPPOSITE[direction_key]]
            coordinate = (coordinate[0] + delta[0], coordinate[1] + delta[1])
        solution = solution[::-1]

        return solution

    def check_neighbor(self, coordinates: Tuple[int, int]
                       ) -> List[Tuple[Tuple[int, int], str]]:
        """Il regarde quels murs sont ouverts pour une coordonnée

        Args:
            coordinates (tuple): coordonnées de le cellule. ex (x, y)
        """
        for cell in self.cells:
            if cell.x == coordinates[0] and cell.y == coordinates[1]:
                walls_open = WALLS[cell.walls]
                neighbor = self.find_coordinates(cell.x, cell.y, walls_open)
        self.check_visited(neighbor)
        return neighbor

    def find_coordinates(self, x: int, y: int,
                         directions: str) -> List[Tuple[Tuple[int, int], str]]:
        """A partir de coordonnées et d'une direction il trouve
        la prochaine cellule à visiter

        Args:
            x (int): coordonnée x
            y (int): coordonnée y
            directions (str): point cordinal. ex : "N" pour Nord

        Returns:
            list[tuple, str]: liste de chaque cellule à explorer avec
            le point cordinal d'arriver. ex: [[(2, 1), "N"], [(1, 1), "W"]]
        """
        coordinates: List[Tuple[Tuple[int, int], str]] = []
        for letter in directions:
            if letter.isupper():
                direction = DIRECTION_DELTA[DIRECTION_COORDINATES[letter]]
                coordinates.append(
                    ((x + direction[0], y + direction[1]), letter)
                )
        return coordinates

    def check_visited(self, neighbor: List[Tuple[Tuple[int, int], str]]
                      ) -> None:
        """Verifie si la cellule à été vérifier ou non et la met à jour

        Args:
            neighbor (list): coordonnée d'une cellule et sa direction
            d'origin. ex: [[(2, 1), "N"], [(1, 1), "W"]]
        """
        for cell in self.cells:
            for pair in neighbor:
                coordinates = pair[0]
                if coordinates not in self.visited:
                    if cell.x == coordinates[0] and cell.y == coordinates[1]:
                        cell.visited = True
