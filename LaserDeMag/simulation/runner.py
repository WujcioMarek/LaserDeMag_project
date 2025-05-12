import udkm1Dsim as ud
units = ud.u
import numpy as np

units.setup_matplotlib()
from LaserDeMag.visual.plotter import plot_results

units = ud.u

def run_simulation(S, params,material_name):
    h = ud.Heat(S, True)
    h.save_data = False
    h.disp_messages = True
    h.heat_diffusion = True

    h.excitation = {
        'fluence': [params['fluence']] * units.mJ / units.cm ** 2,
        'delay_pump': [0] * units.ps,
        'pulse_width': [params['pulse_duration']] * units.ps,
        'multilayer_absorption': True,
        'wavelength': params['laser_wavelength'] * units.nm,
        'theta': 45 * units.deg
    }

    init_temp = np.ones([S.get_number_of_layers(), 3])
    init_temp[:, 0] = params['T0']
    init_temp[:, 1] = params['T0']
    init_temp[:, 2] = 0.1

    delays = np.r_[-1:5:0.005] * units.ps
    temp_map, _ = h.get_temp_map(delays, init_temp)

    plot_results(S, delays, temp_map,material_name)
