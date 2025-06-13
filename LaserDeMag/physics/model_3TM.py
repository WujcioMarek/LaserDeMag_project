import sys, tqdm
from pint import UnitRegistry
sys.modules['tqdm.notebook'] = tqdm
import udkm1Dsim as ud

def fake_notebook(*args, **kwargs):
    """
    Zastępuje funkcję `tqdm.notebook` wersją terminalową.

    ---
    Replaces `tqdm.notebook` with terminal-compatible `tqdm`.

    Returns:
        tqdm.tqdm instance
    """
    kwargs.setdefault('dynamic_ncols', True)
    return tqdm.tqdm(*args, **kwargs)

tqdm.tqdm_notebook = fake_notebook
u = UnitRegistry()
import numpy as np

u = UnitRegistry()
"""
Model fizyczny 3TM i właściwości materiałów.

Moduł wykorzystuje bibliotekę `udkm1Dsim` do budowy struktury i definicji parametrów materiału dla modelu trójtemperaturowego (3TM).

---
3TM physical model and material properties.

This module uses `udkm1Dsim` to construct the material structure and define parameters for the three-temperature model (3TM).
"""
def run_model(structure, params):

    h = ud.Heat(structure, True)
    h.save_data = False
    h.disp_messages = True
    h.heat_diffusion = True

    h.excitation = {
        'fluence': [params['fluence']] * u.mJ / u.cm**2,
        'delay_pump': [0] * u.ps,
        'pulse_width': [params['pulse_duration'] * 1e-3] * u.ps,
        'multilayer_absorption': True,
        'wavelength': params['laser_wavelength'] * u.nm,
        'theta': 45 * u.deg
    }
    init_temp = np.ones([structure.get_number_of_layers(), 3])
    init_temp[:, 0] = params['T0']  # Elektrony
    init_temp[:, 1] = params['T0']  # Fonony
    init_temp[20:, 2] = 0        # Spin

    delays = np.r_[-0.1:5:0.005] * u.ps
    _, _, distances = structure.get_distances_of_layers()
    temp_map, _ = h.get_temp_map(delays, init_temp)

    return delays, temp_map