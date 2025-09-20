Module LaserDeMag.simulation.runner
===================================
Moduł uruchamiający symulację 3TM.

Ten moduł zawiera funkcję do wykonania pełnej symulacji rozkładu temperatury z wykorzystaniem modelu 3TM
oraz przygotowania danych do wizualizacji.

---
3TM simulation runner module.

This module includes a function that executes the full temperature distribution simulation using the 3TM model
and prepares data for visualization.

Functions
---------

`run_simulation(S, params, material_name)`
:   Uruchamia symulację temperaturową dla struktury materiałowej w modelu 3TM.
    
    Args:
        S (ud.Structure): Struktura materiałowa.
        params (dict): Parametry symulacji zawierające:
            - T0: temperatura początkowa (K)
            - fluence: energia impulsu lasera (mJ/cm^2)
            - pulse_duration: czas trwania impulsu (ps)
            - laser_wavelength: długość fali lasera (nm)
        material_name (str): Nazwa materiału (np. "Ni")
    
    Returns:
        dict: Dane do wykresów (mapy temperatur i wykresy czasowe)
    
    ---
    Runs a temperature simulation for a given structure using the 3TM model.
    
    Args:
        S (ud.Structure): Material structure.
        params (dict): Simulation parameters including:
            - T0: initial temperature (K)
            - fluence: laser pulse energy (mJ/cm^2)
            - pulse_duration: pulse duration (ps)
            - laser_wavelength: laser wavelength (nm)
        material_name (str): Name of the material (e.g., "Ni")
    
    Returns:
        dict: Data for plots (temperature maps and time graphs)