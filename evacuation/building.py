"""Planimetria dell'edificio: muri, uscite e mappa delle distanze.

La planimetria e' definita come ASCII art: ogni riga e' una stringa,
'#' = muro, 'E' = uscita, '.' = pavimento calpestabile.
Per cambiare edificio basta passare una nuova lista di stringhe al
costruttore di Building (o modificare DEFAULT_FLOOR_PLAN).
"""

from collections import deque

WALL = "#"
EXIT = "E"

# Planimetria di default: due stanze grandi con corridoi e due uscite.
DEFAULT_FLOOR_PLAN = [
    "####################",
    "#........#.........#",
    "#........#.........#",
    "#..###...#...###...#",
    "E........#.........#",
    "#........#.........#",
    "#...#.........#....#",
    "#...#.........#....#",
    "#...#####..#####...#",
    "#..........#.......E",
    "#..........#.......#",
    "####################",
]


class Building:
    """Rappresenta la planimetria e la conoscenza condivisa dell'edificio.

    Espone:
    - walls / exits / floors: insiemi di coordinate (x, y)
    - distance_map: distanza (in passi) di ogni cella calpestabile
      dall'uscita piu' vicina. E' la "conoscenza della planimetria"
      che gli agenti usano per orientarsi.
    """

    def __init__(self, floor_plan: list[str] | None = None):
        self.floor_plan = floor_plan if floor_plan is not None else DEFAULT_FLOOR_PLAN
        self.height = len(self.floor_plan)
        self.width = len(self.floor_plan[0])

        self.walls: set[tuple[int, int]] = set()
        self.exits: set[tuple[int, int]] = set()
        self.floors: set[tuple[int, int]] = set()
        self._parse_floor_plan()

        self.distance_map = self._compute_distance_map()

    def _parse_floor_plan(self) -> None:
        for row, line in enumerate(self.floor_plan):
            if len(line) != self.width:
                raise ValueError(f"Riga {row} della planimetria ha lunghezza diversa dalle altre")
            for col, char in enumerate(line):
                # La riga 0 dell'ASCII e' la piu' in alto
                coord = (col, self.height - 1 - row)
                if char == WALL:
                    self.walls.add(coord)
                elif char == EXIT:
                    self.exits.add(coord)
                else:
                    self.floors.add(coord)

    def is_walkable(self, coord: tuple[int, int]) -> bool:
        return coord not in self.walls

    def _compute_distance_map(self) -> dict[tuple[int, int], int]:
        """BFS multi-sorgente dalle uscite (vicinato di Moore, 8 direzioni)."""
        distances = {coord: 0 for coord in self.exits}
        queue = deque(self.exits)
        while queue:
            x, y = queue.popleft()
            for dx in (-1, 0, 1):
                for dy in (-1, 0, 1):
                    if dx == 0 and dy == 0:
                        continue
                    neighbor = (x + dx, y + dy)
                    if neighbor in self.floors and neighbor not in distances:
                        distances[neighbor] = distances[(x, y)] + 1
                        queue.append(neighbor)
        return distances

    @property
    def spawn_points(self) -> list[tuple[int, int]]:
        """Celle di pavimento da cui e' raggiungibile almeno un'uscita.

        Ordinata per rendere riproducibile il campionamento con un seed.
        """
        return sorted(self.floors & set(self.distance_map))
