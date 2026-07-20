"""Visualizzazione interattiva su Solara.

Avvio:  python -m solara run app.py 
"""

from matplotlib.ticker import MaxNLocator
from mesa.visualization import SolaraViz, SpaceRenderer, make_plot_component
from mesa.visualization.components import AgentPortrayalStyle

from evacuation.agents.exit import Exit
from evacuation.agents.fire import BURNING, Fire
from evacuation.agents.human import Human
from evacuation.agents.wall import Wall
from evacuation.model import EvacuationModel


def agent_portrayal(agent):
    if isinstance(agent, Wall):
        return AgentPortrayalStyle(color="black", marker="s", size=110, zorder=1) # (s -> square, o -> circle)
    if isinstance(agent, Exit):
        return AgentPortrayalStyle(color="green", marker="s", size=110, zorder=1) 
    if isinstance(agent, Fire):
        color = "tab:orange" if agent.state == BURNING else "dimgray"
        return AgentPortrayalStyle(color=color, marker="s", size=90, zorder=1)
    if isinstance(agent, Human):
        return AgentPortrayalStyle(color="red", marker="o", size=45, zorder=2) # zorder=2 -> sopra a tutti gli altri agenti
    return AgentPortrayalStyle()


def plot_post_process(ax):
    ax.xaxis.set_major_locator(MaxNLocator(integer=True))
    ax.yaxis.set_major_locator(MaxNLocator(integer=True))


model_params = {
    "n_humans": {
        "type": "SliderInt",
        "value": 20,
        "label": "Numero di persone",
        "min": 1,
        "max": 80,
        "step": 1,
    },
    "seed": {
        "type": "InputText",
        "value": 42,
        "label": "Seed casuale",
    },
    "spread_probability": {
        "type": "SliderFloat",
        "value": 0.3,
        "label": "Probabilita' di propagazione del fuoco",
        "min": 0.0,
        "max": 1.0,
        "step": 0.05,
    },
}

model = EvacuationModel(n_humans=20, seed=42)

renderer = SpaceRenderer(model, backend="matplotlib")
renderer.setup_agents(agent_portrayal)
renderer.draw_agents()

page = SolaraViz(  
    model,
    renderer,
    components=[
        make_plot_component(
            {"Dentro l'edificio": "tab:red", "Evacuati": "tab:green", "Morti": "black"},
            post_process=plot_post_process,
        ),
    ],
    model_params=model_params,
    name="Evacuazione edificio in fiamme",
)
