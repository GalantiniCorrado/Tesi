"""Agente statico che rappresenta un'uscita (obiettivo)."""

from mesa.discrete_space import FixedAgent


class Exit(FixedAgent):
    """Un'uscita di sicurezza: chi la raggiunge e' evacuato."""

    def __init__(self, model, cell):
        super().__init__(model)
        self.cell = cell
