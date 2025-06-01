import sys, tqdm, warnings
import numpy as np
"""
Model fizyczny 3TM i właściwości materiałów.

Moduł wykorzystuje bibliotekę `udkm1Dsim` do budowy struktury i definicji parametrów materiału dla modelu trójtemperaturowego (3TM).

---
3TM physical model and material properties.

This module uses `udkm1Dsim` to construct the material structure and define parameters for the three-temperature model (3TM).
"""
sys.modules['tqdm.notebook'] = tqdm
import udkm1Dsim as ud
units = ud.u

units.setup_matplotlib()
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
import udkm1Dsim as ud
units = ud.u

def get_material_properties(material, Tc, mu, ge):
    """
     Tworzy obiekt materiału oraz zwraca właściwości fizyczne dla modelu 3TM.

     Args:
         material (str): Nazwa materiału (Co, Ni, Fe, Gd).
         Tc (float): Temperatura Curie.
         mu (float): Moment magnetyczny.
         ge (float): Stała sprzężenia spin-kratka.

     Returns:
         tuple: (Atom, dict) - obiekt Atom oraz słownik właściwości fizycznych.

     Raises:
         ValueError: Jeśli materiał nie jest wspierany.

     ---
     Creates a material object and returns its physical properties for the 3TM model.

     Args:
         material (str): Material name (Co, Ni, Fe, Gd).
         Tc (float): Curie temperature.
         mu (float): Magnetic moment.
         ge (float): Spin-lattice coupling constant.

     Returns:
         tuple: (Atom, dict) - Atom object and a dictionary of physical properties.

     Raises:
         ValueError: If material is not supported.
     """
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
    """
    Tworzy strukturę 1D cienkiej warstwy dla modelu 3TM.

    Args:
        material_obj (ud.Atom): Obiekt atomu materiału.
        prop (dict): Właściwości materiałowe.

    Returns:
        ud.Structure: Struktura 1D do symulacji.

    ---
    Creates a 1D thin film structure for the 3TM simulation.

    Args:
        material_obj (ud.Atom): Material Atom object.
        prop (dict): Material properties.

    Returns:
        ud.Structure: Structure object for simulation.
    """
    layer = ud.AmorphousLayer(material_obj.name, f'{material_obj.name} amorphous', thickness=1 * units.nm,
                              density=7000 * units.kg / units.m ** 3, atom=material_obj, **prop)
    structure = ud.Structure(material_obj.name)
    structure.add_sub_structure(layer, 50)
    return structure