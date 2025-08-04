"""
Moduł uruchamiający symulację 3TM.

Ten moduł zawiera funkcję do wykonania pełnej symulacji rozkładu temperatury z wykorzystaniem modelu 3TM
oraz przygotowania danych do wizualizacji.

---
3TM simulation runner module.

This module includes a function that executes the full temperature distribution simulation using the 3TM model
and prepares data for visualization.
"""
import udkm1Dsim as ud
units = ud.u
import numpy as np

units.setup_matplotlib()
from LaserDeMag.visual.plotter import plot_results

units = ud.u

def run_simulation(S, params,material_name):
    """
    Uruchamia symulację temperaturową dla struktury materiałowej w modelu 3TM.

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
    """
    h = ud.Heat(S, True)
    h.save_data = False
    h.disp_messages = True
    h.heat_diffusion = True

    h.excitation = {
        'fluence': [params['fluence']] * units.mJ / units.cm ** 2,
        'delay_pump': [0] * units.ps,
        'pulse_width': [params['pulse_duration'] * 1e-3] * units.ps,
        'multilayer_absorption': True,
        'wavelength': params['laser_wavelength'] * units.nm,
        'theta': 45 * units.deg
    }

    h.boundary_conditions = {'top_type': 'isolator', 'bottom_type': 'isolator'}
    n = int(S.get_number_of_layers() -50)
    init_temp = np.ones([S.get_number_of_layers(), 3])
    init_temp[:, 0] = params['T0']
    init_temp[:, 1] = params['T0']
    init_temp[n:, 2] = 0

    delays = np.r_[-0.1:5:0.005] * units.ps
    _, _, distances = S.get_distances_of_layers()
    temp_map, _ = h.get_temp_map(delays, init_temp)

    return plot_results(S, delays, temp_map, material_name)

