import sys, tqdm
from pint import UnitRegistry
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
u = UnitRegistry()

density_lookup = {
    "Ni": 8900,
    "Co": 8860,
    "Gd": 7895,
    "Fe": 7874
}
def get_material_properties(material_name: str, Tc: float,ge: float):

    if material_name == "Ni":

        #R = 25.3 / 1e-12   # [1/s]
        R = 17.2e12
        C = 445  # elektronowa pojemność cieplna (przykład)


        props = {
            'heat_capacity': [
                '0.1*T',  # elektron
                C * u.J / u.kg / u.K,  # fonon
                1 / 8900  # spin (umowna stała)
            ],
            'therm_cond': [
                #90 * u.W / (u.m * u.K),  # elektron
                #15 * u.W / (u.m * u.K),  # fonon
                15 * u.W / (u.m * u.K),
                90 * u.W / (u.m * u.K),
                0
            ],
            'sub_system_coupling': [
                #f'-{g_el:.1e}*(T_0-T_1)',  # e → ph
                #f'{g_el:.1e}*(T_0-T_1)',  # ph → e
                #f'{R:.1e}*T_2*T_1/{Tc:.0f}*(1 - T_2*(1 + 2/(exp(2*T_2*{Tc:.0f}/T_0)-1)))'  # spin
                '-{:f}*(T_0-T_1)'.format(ge),
                '{:f}*(T_0-T_1)'.format(ge),
                '{0:f}*T_2*T_1/{1:f}*(1-T_2* (1 + 2/(exp(2*T_2*{1:f}/T_0) - 1) ))'.format(R, Tc)
            ],
            'lin_therm_exp': [0, 11.8e-6, 0],
            'sound_vel': 4.910 * u.nm / u.ps,
            'opt_ref_index': 2.0 + 4.0j
        }
    return props

def build_structure(params):
    density = density_lookup[params['material']] * u.kg / u.meter ** 3
    atom = ud.Atom(params['material'])

    props = get_material_properties(params['material'], params['Tc'], params['ge'])

    layer = ud.AmorphousLayer(
        id=params['material'],
        name=params['material'],
        thickness=1 * u.nm,
        density=density,
        atom=atom,
        **props
    )

    S = ud.Structure('single-layer')
    S.add_sub_structure(layer, 10)
    return S