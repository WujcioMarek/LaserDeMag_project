import matplotlib.pyplot as plt
import udkm1Dsim as ud

def draw_structure(structure, material_name):
    num_layers = structure.get_number_of_layers()
    thicknesses = []
    names = []
    colors = []

    for i in range(num_layers):
        layer = structure.get_layer_handle(i)
        thicknesses.append(layer.thickness.to('nm').magnitude)
        names.append(layer.name)
        colors.append('red' if "CoNi" in layer.name else 'blue')

    fig, ax = plt.subplots(figsize=(3, 6))
    bottom = 0
    for thickness, name, color in zip(thicknesses, names, colors):
        ax.bar(0, thickness, bottom=bottom, width=0.5, label=name, color=color)
        ax.text(0, bottom + thickness / 2, f"{name}\n{thickness:.1f} nm", va='center', ha='center', fontsize=10, color='white')
        bottom += thickness

    ax.set_ylim(0, bottom)
    ax.set_xlim(-1, 1)
    ax.set_xticks([])
    ax.set_ylabel("Grubość [nm]")
    ax.set_title(f"Struktura: {structure.name}")
    plt.tight_layout()
    plt.show()

def plot_results(S, delays, temp_map):
    import numpy as np
    distances = S.get_distances_of_layers()[2]
    plt.figure(figsize=[6, 12])

    for i, label in enumerate(["Electrons", "Phonons", "Magnetization"]):
        plt.subplot(3, 1, i + 1)
        plt.pcolormesh(distances.to('nm').magnitude, delays.to('ps').magnitude, temp_map[:, :, i], shading='auto')
        plt.colorbar()
        plt.xlabel('Distance [nm]')
        plt.ylabel('Delay [ps]')
        plt.title(f'Temperature Map {label}')

    plt.tight_layout()
    plt.show()

    select = S.get_all_positions_per_unique_layer()['CoNi']
    plt.figure(figsize=[6, 8])
    plt.subplot(2, 1, 1)
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
