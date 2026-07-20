"""Agente umano: cerca di raggiungere l'uscita piu' vicina."""

from mesa.discrete_space import CellAgent

from .fire import BURNING, Fire


class Human(CellAgent):
    """Un essere umano intrappolato nell'edificio.

    Ogni istanza e' unica.
    """

    def __init__(self, model, cell, speed: int = 1):
        super().__init__(model)
        self.cell = cell
        self.speed = speed

    def step(self) -> None:
        for _ in range(self.speed):
            if self._try_escape():
                return
            if self._check_fire():
                return
            self._move_towards_exit()
        if self._try_escape():
            return
        self._check_fire()

    def _try_escape(self) -> bool:
        """Se l'agente e' su un'uscita, e' salvo: esce dalla simulazione."""
        if self.cell.coordinate in self.model.building.exits:
            self.model.evacuated_count += 1
            self.remove()
            return True
        return False

    def _check_fire(self) -> bool:
        """Se la cella e' in fiamme, l'agente muore nell'incendio."""
        if any(isinstance(agent, Fire) and agent.state == BURNING for agent in self.cell.agents):
            self.model.casualties_count += 1
            self.remove()
            return True
        return False

    def _move_towards_exit(self) -> None:
        """L'agente conosce la planimetria (building.distance_map) e si sposta sulla cella vicina piu' vicina a un'uscita. 
        In caso di parita' sceglie a caso, per non far muovere tutti in fila.
        """ 
        distances = self.model.building.distance_map
        current = distances.get(self.cell.coordinate)
        if current is None:  # cella isolata: nessuna uscita raggiungibile
            return

        candidates = [
            cell
            for cell in self.cell.neighborhood
            if distances.get(cell.coordinate, current) < current
        ]
        if not candidates:
            return

        best = min(distances[cell.coordinate] for cell in candidates)    #cerca la distanza minima tra le celle vicine
        best_cells = [c for c in candidates if distances[c.coordinate] == best]   #cerca le celle vicine con la distanza minima
        self.cell = self.random.choice(best_cells)  # sceglie a caso tra le celle vicine con la distanza minima
