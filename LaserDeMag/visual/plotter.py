# LaserDeMag/visual/plotter.py
def plot_results(S, delays, temp_map, material_name):
    import numpy as np

    distances = S.get_distances_of_layers()[2].to('nm').magnitude
    delay_ps = delays.to('ps').magnitude
    select = S.get_all_positions_per_unique_layer()[material_name]

    data = {
        "maps": [  # pcolormesh
            {
                "x": distances,
                "y": delay_ps,
                "z": temp_map[:, :, i],
                "label": label,
                "xlabel": "Distance [nm]",
                "ylabel": "Delay [ps]",
                "title": f"Temperature Map {label}"
            }
            for i, label in enumerate(["Electrons", "Phonons", "Magnetization"])
        ],
        "lines": [  # wykresy liniowe
            {
                "x": delay_ps,
                "y": np.mean(temp_map[:, select, 0], 1),
                "label": "electrons",
                "ylabel": "Temperature [K]",
                "xlabel": "Delay [ps]",
                "title": "M3TM Koopmans et. al"
            },
            {
                "x": delay_ps,
                "y": np.mean(temp_map[:, select, 1], 1),
                "label": "phonons",
                "ylabel": "Temperature [K]",
                "xlabel": "Delay [ps]",
                "title": "M3TM Koopmans et. al"
            },
            {
                "x": delay_ps,
                "y": np.mean(temp_map[:, select, 2], 1),
                "label": "M",
                "ylabel": "Magnetization",
                "xlabel": "Delay [ps]",
                "title": "Magnetization"
            }
        ]
    }

    return data
