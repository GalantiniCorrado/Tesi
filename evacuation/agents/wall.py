"""Agente statico che rappresenta un muro (ostacolo)."""

from mesa.discrete_space import FixedAgent


class Wall(FixedAgent):
    """Un muro: occupa una cella e non fa nulla. Serve come ostacolo
    e per la visualizzazione."""

    def __init__(self, model, cell):
        super().__init__(model)
        self.cell = cell
