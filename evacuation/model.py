"""Orchestratore della simulazione.

EvacuationModel crea il mondo (la griglia a partire dalla planimetria),
istanzia gli agenti statici (muri, uscite) e gli umani in posizioni
casuali, e fa avanzare la simulazione step dopo step.
"""

import random

from mesa import DataCollector, Model # DataCollector raccoglie dati durante la simulazione, Model e' la classe base per i modelli di simulazione.
from mesa.discrete_space import OrthogonalMooreGrid # OrthogonalMooreGrid e' una griglia 2D con vicini di Moore (8 celle adiacenti).

from .agents.exit import Exit
from .agents.fire import Fire
from .agents.human import Human
from .agents.wall import Wall
from .building import Building


class EvacuationModel(Model):
    """Modello di evacuazione di un edificio in fiamme."""

    def __init__(
        self,
        n_humans: int = 20,
        seed: int | None = None,
        spread_probability: float = 0.3,
    ):
        super().__init__(rng=int(seed) if seed is not None else None)

        "estrae dal generatore principale un numero intero casuale a 64 bit. Quel numero viene poi usato come seed di un nuovo generatore indipendente. "
        "dal seed (es. quello predefinito: 42) nasce il generatore principale self.random; da questo ne nascono altri due, ciascuno con il proprio flusso."
        "placement_random: per posizionare gli umani in celle calpestabili a caso, senza influenzare la propagazione del fuoco."
        "fire_random: per la propagazione del fuoco, senza influenzare il posizionamento degli umani."
        self.placement_random = random.Random(self.random.getrandbits(64))   
        self.fire_random = random.Random(self.random.getrandbits(64))

        # Il mondo: planimetria + griglia 2D.
        self.building = Building()
        self.grid = OrthogonalMooreGrid(      
            (self.building.width, self.building.height),
            torus=False,  
            random=self.random, 
        )

        self.evacuated_count = 0
        self.casualties_count = 0

        # Agenti statici: muri (ostacoli) e uscite (obiettivi).
        for coord in self.building.walls:
            Wall(self, self.grid[coord])
        for coord in self.building.exits:
            Exit(self, self.grid[coord])

        # Umani in posizioni casuali tra le celle calpestabili.
        n_humans = min(n_humans, len(self.building.spawn_points))
        for coord in self.placement_random.sample(self.building.spawn_points, k=n_humans):  
            Human(self, self.grid[coord], speed=1)

        # Incendio: nasce in un punto casuale e da li si propaga da solo.
        ignition_point = self.fire_random.choice(self.building.spawn_points)
        Fire(self, self.grid[ignition_point], spread_probability)

        self.datacollector = DataCollector(
            model_reporters={
                "Dentro l'edificio": lambda m: len(m.agents_by_type.get(Human, [])),
                "Evacuati": lambda m: m.evacuated_count,
                "Morti": lambda m: m.casualties_count,
            }
        )
        self.datacollector.collect(self)

    def step(self) -> None:
        # Il fuoco avanza di un anello prima che gli umani reagiscano.
        fires = list(self.agents_by_type.get(Fire, []))
        if fires:
            self.fire_random.shuffle(fires)
            for fire in fires:
                fire.step()

        humans = self.agents_by_type.get(Human)
        if humans:
            humans.shuffle_do("step")
        self.datacollector.collect(self)

        # Ferma la simulazione quando tutti sono usciti (o morti).
        if not self.agents_by_type.get(Human, []):
            self.running = False
