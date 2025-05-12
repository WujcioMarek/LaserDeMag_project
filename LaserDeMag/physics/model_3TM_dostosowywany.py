import sys
import tqdm

# Nadpisanie modułu tqdm.notebook w sys.modules, zanim załaduje go udkm1Dsim
sys.modules['tqdm.notebook'] = tqdm
import udkm1Dsim as ud
units = ud.u
import numpy as np
import matplotlib.pyplot as plt

units.setup_matplotlib()
def fake_notebook(*args, **kwargs):
    kwargs.setdefault('dynamic_ncols', True)
    return tqdm.tqdm(*args, **kwargs)

tqdm.tqdm_notebook = fake_notebook

# Zbieranie parametrów wejściowych od użytkownika

def get_input_parameters():
    """
     Funkcja do wprowadzenia parametrów przez użytkownika z opcją domyślnych wartości.
     """
    # Domyślne wartości parametrów
    default_params = {
        'material': 'Co',  # Domyślny materiał: Co
        'T0': 300,  # Temperatura początkowa (w K)
        'Tc': 1388,  # Temperatura Curie (w K)
        'mu': 1.5,  # Moment magnetyczny (np. w µB)
        'fluence': 30,  # Fluencja lasera (mJ/cm²)
        'pulse_duration': 0.05,  # Czas trwania impulsu lasera (ps)
        'laser_wavelength': 800,  # Długość fali lasera (nm)
        'ge': 4.0e18,  # Sprzężenie stałej spinowej elektronów
        'asf': 0.1  # Prawdopodobieństwo obrotu spinem (a_sf)
    }

    params = {}
    params['material'] = input(f"Podaj materiał (domyślnie {default_params['material']}): ") or default_params[
        'material']
    params['T0'] = input(f"Podaj temperaturę początkową T0 (domyślnie {default_params['T0']} K): ") or default_params[
        'T0']
    params['Tc'] = input(f"Podaj temperaturę Curie Tc (domyślnie {default_params['Tc']} K): ") or default_params['Tc']
    params['mu'] = input(f"Podaj moment magnetyczny (domyślnie {default_params['mu']} µB): ") or default_params['mu']
    params['fluence'] = input(f"Podaj moc lasera (domyślnie {default_params['fluence']} mJ/cm²): ") or default_params[
        'fluence']
    params['pulse_duration'] = input(
        f"Podaj czas trwania impulsu lasera (domyślnie {default_params['pulse_duration']} ps): ") or default_params[
                                   'pulse_duration']
    params['laser_wavelength'] = input(
        f"Podaj długość fali lasera (domyślnie {default_params['laser_wavelength']} nm): ") or default_params[
                                     'laser_wavelength']
    params['ge'] = input(f"Podaj sprzężenie stałej spinowej elektronów (domyślnie {default_params['ge']}): ") or \
                   default_params['ge']
    params['asf'] = input(f"Podaj prawdopodobieństwo obrotu spinem (domyślnie {default_params['asf']}): ") or \
                    default_params['asf']

    # Konwersja wprowadzonych danych na odpowiednie typy
    params['T0'] = float(params['T0'])
    params['Tc'] = float(params['Tc'])
    params['mu'] = float(params['mu'])
    params['fluence'] = float(params['fluence'])
    params['pulse_duration'] = float(params['pulse_duration'])
    params['laser_wavelength'] = float(params['laser_wavelength'])
    params['ge'] = float(params['ge'])
    params['asf'] = float(params['asf'])

    return params

# Tworzenie rejestru jednostek
#u = pint.UnitRegistry()

# Przygotowanie materiałów
def get_material_properties(material, Tc, mu, ge):
    if material == 'Co':
        material_obj = ud.Atom('Co')
        print(material_obj.name)
    elif material == 'Ni':
        material_obj = ud.Atom('Ni')
    elif material == 'CoNi':
        material_obj = ud.AtomMixed('CoNi')
        Co = ud.Atom('Co')
        Ni = ud.Atom('Ni')
        material_obj.add_atom(Co, 0.5)
        material_obj.add_atom(Ni, 0.5)
    else:
        raise ValueError(f"Nieznany materiał: {material}")

    # Właściwości materiału
    prop = {}
    prop['heat_capacity'] = ['0.1*T', 532 * units.J / units.kg / units.K, 1 / 7000]
    prop['therm_cond'] = [20 * units.W / (units.m * units.K), 80 * units.W / (units.m * units.K), 0]
    prop['sub_system_coupling'] = ['-{:.6f}*(T_0-T_1)'.format(ge), '{:.6f}*(T_0-T_1)'.format(ge),
                                   '{0:f}*T_2*T_1/{1:f}*(1-T_2* (1 + 2/(exp(2*T_2*{1:f}/T_0) - 1) ))'.format(
                                       25.3 / 1e-12, Tc)]
    prop['lin_therm_exp'] = [0, 11.8e-6, 0]
    prop['sound_vel'] = 4.910 * units.nm / units.ps
    prop['opt_ref_index'] = 2.9174 + 3.3545j

    return material_obj, prop



# Tworzenie struktury
def create_structure(material_obj, prop):
    layer = ud.AmorphousLayer(material_obj.name, f'{material_obj.name} amorphous', thickness=1 * units.nm,
                              density=7000 * units.kg / units.m ** 3, atom=material_obj, **prop)
    structure = ud.Structure(material_obj.name)
    structure.add_sub_structure(layer, 50)
    return structure

def draw_structure(structure, material_name):
    num_layers = structure.get_number_of_layers()
    thicknesses = []
    names = []
    colors = []

    for i in range(num_layers):
        layer = structure.get_layer_handle(i)
        thicknesses.append(layer.thickness.to('nm').magnitude)
        names.append(layer.name)

        # Możesz tutaj przypisać kolory w zależności od nazwy warstwy (materiału)
        # Na przykład:
        if "CoNi" in layer.name:
            colors.append('red')  # Czerwony dla warstw CoNi
        else:
            colors.append('blue')  # Niebieski dla innych warstw

    fig, ax = plt.subplots(figsize=(3, 6))
    bottom = 0

    for thickness, name, color in zip(thicknesses, names, colors):
        ax.bar(0, thickness, bottom=bottom, width=0.5, label=name, color=color)
        ax.text(0, bottom + thickness / 2, f"{name}\n{thickness:.1f} nm",
                va='center', ha='center', fontsize=10, color='white')
        bottom += thickness

    ax.set_ylim(0, bottom)
    ax.set_xlim(-1, 1)
    ax.set_xticks([])
    ax.set_ylabel("Grubość [nm]")

    # Tytuł z nazwą struktury i składem
    title = f"Struktura: {structure.name}"
    if isinstance(material_name, ud.AtomMixed):
        composition =[]
        for atom, fraction in material_name.atoms:
            composition.append(f"{atom.symbol} {fraction * 100:.0f}%")

        title += f" ({composition})"
    ax.set_title(title)

    plt.tight_layout()
    plt.show()


def main():
    # Parametry od użytkownika
    params = get_input_parameters()

    # Pobieramy materiał i właściwości
    material_obj, prop = get_material_properties(params['material'], params['Tc'], params['mu'], params['ge'])

    # Tworzymy strukturę materiału
    S = create_structure(material_obj, prop)
    #S.visualize()

    draw_structure(S, material_obj)

    # Symulacja
    h = ud.Heat(S, True)
    h.save_data = False
    h.disp_messages = True
    h.heat_diffusion = True

    # Ustawienia lasera
    h.excitation = {
        'fluence': [params['fluence']] * units.mJ / units.cm ** 2,
        'delay_pump': [0] * units.ps,
        'pulse_width': [params['pulse_duration']] * units.ps,
        'multilayer_absorption': True,
        'wavelength': params['laser_wavelength'] * units.nm,
        'theta': 45 * units.deg
    }

    # Wartości temperatury początkowej
    init_temp = np.ones([S.get_number_of_layers(), 3])
    init_temp[:, 0] = params['T0']  # temperatura elektronów
    init_temp[:, 1] = params['T0']  # temperatura fononów
    init_temp[:, 2] = 0.1  # magnetyzacja początkowa

    # Przeprowadzamy symulację
    delays = np.r_[-1:5:0.005] * units.ps
    temp_map, delta_temp = h.get_temp_map(delays, init_temp)
    _, _, distances = S.get_distances_of_layers()

    # Wykresy wyników
    plt.figure(figsize=[6, 12])
    plt.subplot(3, 1, 1)
    plt.pcolormesh(distances.to('nm').magnitude, delays.to('ps').magnitude, temp_map[:, :, 0],
                   shading='auto')
    plt.colorbar()
    plt.xlabel('Distance [nm]')
    plt.ylabel('Delay [ps]')
    plt.title('Temperature Map Electrons')

    plt.subplot(3, 1, 2)
    plt.pcolormesh(distances.to('nm').magnitude, delays.to('ps').magnitude, temp_map[:, :, 1],
                   shading='auto')
    plt.colorbar()
    plt.xlabel('Distance [nm]')
    plt.ylabel('Delay [ps]')
    plt.title('Temperature Map Phonons')

    plt.subplot(3, 1, 3)
    plt.pcolormesh(distances.to('nm').magnitude, delays.to('ps').magnitude,
                   temp_map[:, :, 2], shading='auto')
    plt.colorbar()
    plt.xlabel('Distance [nm]')
    plt.ylabel('Delay [ps]')
    plt.title('Magnetization')

    plt.tight_layout()
    plt.show()

    plt.figure(figsize=[6, 8])
    plt.subplot(2, 1, 1)
    print(S.get_all_positions_per_unique_layer().keys())
    select = S.get_all_positions_per_unique_layer()[material_obj.name]
    plt.plot(delays.to('ps'), np.mean(temp_map[:, select, 0], 1), label='electrons')
    plt.plot(delays.to('ps'), np.mean(temp_map[:, select, 1], 1), label='phonons')
    plt.ylabel('Temperature [K]')
    plt.xlabel('Delay [ps]')
    plt.legend()
    plt.title('M3TM Koopmans et. al')

    plt.subplot(2, 1, 2)
    plt.plot(delays.to('ps'), np.mean(temp_map[:, select, 2], 1), label='M')
    plt.ylabel('Magnetization')
    plt.xlabel('Delay [ps]')
    plt.legend()
    plt.show()


if __name__ == "__main__":
    main()