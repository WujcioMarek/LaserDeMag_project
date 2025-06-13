"""
Moduł główny modułu wizualizacji i symulacji.

Funkcja `main` uruchamia pełen przebieg symulacji na podstawie przekazanych parametrów:
- Pobiera właściwości materiału,
- Tworzy strukturę modelu fizycznego,
- Uruchamia symulację z wykorzystaniem przygotowanej struktury i parametrów,
- Zwraca wyniki symulacji do dalszego przetwarzania lub wizualizacji.

---

Main module of the visualization and simulation component.

The `main` function executes the full simulation workflow based on input parameters:
- Retrieves material properties,
- Creates the physical model structure,
- Runs the simulation using the prepared structure and parameters,
- Returns simulation results for further processing or visualization.
"""
from LaserDeMag.simulation.runner import run_simulation

def main(params):
    """
    Run the full LaserDeMag simulation.

    Parameters:
        params (dict): Dictionary of user-defined simulation parameters.

    Returns:
        dict: Results of the simulation (e.g., time delays, temperature maps).
    """
    return run_simulation(params)