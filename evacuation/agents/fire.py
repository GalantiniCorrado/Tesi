"""Agente dinamico che rappresenta il fuoco.

Ogni istanza di Fire occupa una cella fissa (non si sposta), ma finche' e'
BURNING puo' generare nuove istanze di Fire sulle celle di pavimento adiacenti
(vicinato di Moore, come la BFS di Building). 
"""

from mesa.discrete_space import FixedAgent

BURNING = "burning"



class Fire(FixedAgent):
    """Un focolaio d'incendio su una cella."""

    def __init__(self, model, cell, spread_probability: float = 0.2):
        super().__init__(model)
        self.cell = cell
        self.spread_probability = spread_probability
        self.age = 0
        self.state = BURNING

    def step(self) -> None:
        self.age += 1
        if self.state != BURNING:
            return
        self._try_spread()

    def _try_spread(self) -> None:
        """Ogni cella di pavimento vicina non ancora incendiata ha una probabilita' indipendente di incendiarsi a sua volta.
        """
        rng = self.model.fire_random
        for neighbor in self.cell.neighborhood:
            if self._is_ignitable(neighbor) and rng.random() < self.spread_probability:
                Fire(self.model, neighbor, self.spread_probability)

    def _is_ignitable(self, cell) -> bool:
        if cell.coordinate not in self.model.building.floors:  # se e' un muro o un'uscita, non si incendia
            return False
        return not any(isinstance(agent, Fire) for agent in cell.agents) # se c'e' gia' un incendio, non si incendia di nuovo
