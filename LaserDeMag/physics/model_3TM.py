import sys, tqdm
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

def get_material_properties(material, Tc):
    """
     Tworzy obiekt materiału oraz zwraca właściwości fizyczne dla modelu 3TM.

     Args:
         material (str): Nazwa materiału (Ni).
         Tc (float): Temperatura Curie.


     Returns:
         tuple: (Atom, dict) - obiekt Atom oraz słownik właściwości fizycznych.

     Raises:
         ValueError: Jeśli materiał nie jest wspierany.

     ---
     Creates a material object and returns its physical properties for the 3TM model.

     Args:
         material (str): Material name (Ni).
         Tc (float): Curie temperature.

     Returns:
         tuple: (Atom, dict) - Atom object and a dictionary of physical properties.

     Raises:
         ValueError: If material is not supported.
     """
    if material == 'Ni':
        material_obj = ud.Atom('Ni')
    else:
        raise ValueError(f"Nieznany materiał: {material}")

    g = 4.0e18
    R = 25.3/1e-12

    prop = {
        'heat_capacity': ['0.1*T', 445 * units.J / units.kg / units.K, 1 / 8900],
        'therm_cond': [15 * units.W / (units.m * units.K), 90 * units.W / (units.m * units.K), 0],
        'sub_system_coupling': ['-{:f}*(T_0-T_1)'.format(g),
                                '{:f}*(T_0-T_1)'.format(g),
                                '{0:f}*T_2*T_1/{1:f}*(1-T_2* (1 + 2/(exp(2*T_2*{1:f}/T_0) - 1) ))'.format(R, Tc)],
        'lin_therm_exp': [0, 11.8e-6, 0],
        'sound_vel': 4.910 * units.nm / units.ps,
        'opt_ref_index': 2.9174 + 3.3545j,
    }

    return material_obj, prop

def create_structure(material_obj, prop,N):
    """
    Tworzy strukturę 1D cienkiej warstwy dla modelu 3TM.

    Args:
        material_obj (ud.Atom): Obiekt atomu materiału.
        prop (dict): Właściwości materiałowe.
        N (int): Liczba warstw materiału.

    Returns:
        ud.Structure: Struktura 1D do symulacji.

    ---
    Creates a 1D thin film structure for the 3TM simulation.

    Args:
        material_obj (ud.Atom): Material Atom object.
        prop (dict): Material properties.
        N (int): Number of material layers.

    Returns:
        ud.Structure: Structure object for simulation.
    """
    lattice_constant_Ni = 0.35241  # nm
    lattice_constant_Si = 0.5431   # nm
    N = int(N)
    Si = ud.Atom('Si')
    prop_Si = {}
    prop_Si['heat_capacity'] = [100 * units.J / units.kg / units.K, 603 * units.J / units.kg / units.K, 1]
    prop_Si['therm_cond'] = [0, 100 * units.W / (units.m * units.K), 0]

    prop_Si['sub_system_coupling'] = [0, 0, 0]

    prop_Si['lin_therm_exp'] = [0, 2.6e-6, 0]
    prop_Si['sound_vel'] = 8.433 * units.nm / units.ps
    prop_Si['opt_ref_index'] = 3.6941 + 0.0065435j


    layer = ud.AmorphousLayer(material_obj.name, material_obj.name, thickness=lattice_constant_Ni * units.nm,
                              density=8900 * units.kg / units.m ** 3, atom=material_obj, **prop)
    structure = ud.Structure(material_obj.name)
    structure.add_sub_structure(layer, N)

    layer_Si = ud.AmorphousLayer('Si', "Si amorphous", thickness=lattice_constant_Si * units.nm, density=2336 * units.kg / units.m ** 3,
                                 atom=Si, **prop_Si)
    structure.add_sub_structure(layer_Si, 50)
    return structure