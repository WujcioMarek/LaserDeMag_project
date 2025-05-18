import sys, tqdm, warnings
import numpy as np

sys.modules['tqdm.notebook'] = tqdm
import udkm1Dsim as ud
units = ud.u

units.setup_matplotlib()
def fake_notebook(*args, **kwargs):
    kwargs.setdefault('dynamic_ncols', True)
    return tqdm.tqdm(*args, **kwargs)

tqdm.tqdm_notebook = fake_notebook
import udkm1Dsim as ud
units = ud.u

def get_material_properties(material, Tc, mu, ge):
    if material == 'Co':
        material_obj = ud.Atom('Co')
    elif material == 'Ni':
        material_obj = ud.Atom('Ni')
    elif material == "Gd":
        material_obj = ud.Atom('Gd')
    elif material == "Fe":
        material_obj = ud.Atom('Fe')
    else:
        raise ValueError(f"Nieznany materiał: {material}")

    prop = {
        'heat_capacity': ['0.1*T', 532 * units.J / units.kg / units.K, 1 / 7000],
        'therm_cond': [20 * units.W / (units.m * units.K), 80 * units.W / (units.m * units.K), 0],
        'sub_system_coupling': ['-{:.6f}*(T_0-T_1)'.format(ge),
                                '{:.6f}*(T_0-T_1)'.format(ge),
                                '{0:f}*T_2*T_1/{1:f}*(1-T_2* (1 + 2/(exp(2*T_2*{1:f}/T_0) - 1) ))'.format(25.3 / 1e-12, Tc)],
        'lin_therm_exp': [0, 11.8e-6, 0],
        'sound_vel': 4.910 * units.nm / units.ps,
        'opt_ref_index': 2.9174 + 3.3545j
    }
    return material_obj, prop

def create_structure(material_obj, prop):
    layer = ud.AmorphousLayer(material_obj.name, f'{material_obj.name} amorphous', thickness=1 * units.nm,
                              density=7000 * units.kg / units.m ** 3, atom=material_obj, **prop)
    structure = ud.Structure(material_obj.name)
    structure.add_sub_structure(layer, 50)
    return structure