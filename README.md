# Evacuazione di un edificio in fiamme — simulazione multi-agente (Mesa)

Simulazione ad agenti con [Mesa]: un edificio contiene N esseri umani che conoscono la
planimetria e cercano di raggiungere l'uscita più vicina. Allo stesso tempo un incendio si propaga nell'edificio. 

## Avvio

```bash

# Interfaccia interattiva nel browser (http://localhost:8765)
python -m solara run app.py

```

## Struttura del progetto

```
app.py                     # Visualizzazione Solara 
evacuation/
    model.py               # EvacuationModel: l'ORCHESTRATORE — crea mondo e agenti
    building.py            # Building: planimetria (muri, uscite) e mappa distanze
    agents/
        human.py           # Human: agente umano che fugge verso l'uscita
        wall.py            # Wall: agente statico, ostacolo
        exit.py            # Exit: agente statico, obiettivo
        fire.py            # Fire: agente statico, nasce e si propaga
```

## Come funziona

- **`Building`** legge una planimetria ASCII (`#` muro, `E` uscita, `.` pavimento)
  e calcola con una BFS multi-sorgente la **mappa delle distanze**: per ogni cella,
  quanti passi mancano all'uscita più vicina. Questa è la "conoscenza della
  planimetria" condivisa dagli agenti.
- **`EvacuationModel`** (orchestratore) istanzia la griglia, i muri, le uscite e
  gli N umani in celle casuali; a ogni `step()` fa muovere gli umani in ordine
  casuale e raccoglie i dati (dentro / evacuati).
- **`Human`** guarda le 8 celle vicine e si sposta su quella con distanza minore
  dalla propria (discesa del gradiente sulla mappa delle distanze). Arrivato su
  un'uscita viene rimosso dalla simulazione (evacuato); se invece la sua cella
  prende fuoco, viene rimosso come vittima.
- **`Fire`** nasce (una sola istanza, su una cella casuale calpestabile) e a ogni
  `step()` prova a propagarsi con probabilità
  `spread_probability` su ogni cella di pavimento vicina non ancora incendiata,
  creando lì una nuova istanza di `Fire.

## Punti di estensione previsti

- **Caratteristiche uniche degli agenti**: attributi in
  `Human.__init__` (età, panico, mobilità ridotta...); Inoltre modificare l'intelligenza degli umani in qualche modo.  
- **Fuoco che condiziona il percorso**: oggi `Human._move_towards_exit` segue
  `building.distance_map` ignorando il fuoco; un umano può camminarci dentro
  per puro caso. Prossimo passo è far scartare a `_move_towards_exit`
  i vicini in fiamme, oppure ricalcolare periodicamente `distance_map`
  trattando le celle `BURNING` come muri.
- **Collisioni/affollamento**: limitare la capacità delle celle.
- **Metriche**: reporters al `DataCollector` in `model.py`
  (tempo medio di fuga, distanza percorsa, ...).
- **Robots**: aiutanti che dirigono e influenzano il comportamento degli agenti umani.
