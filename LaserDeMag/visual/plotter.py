from scipy.interpolate import interp1d
def plot_results(structure, delays, temp_map, material_name):
    import numpy as np
    """
    Prepares temperature and magnetization data for plotting based on a 3TM simulation.

    This function generates two types of visualizations:
    - Spatial temperature profiles (for electrons, phonons, and magnetization) at a central time delay.
    - Temporal evolution (line plots) of average temperatures and magnetization within a selected material layer.

    Parameters
    ----------
    S : object
        A simulation system object that provides layer information.
        Must implement `get_distances_of_layers()` and `get_all_positions_per_unique_layer()`.
    delays : pint.Quantity
        A 1D array of time delays, typically with time units (e.g., picoseconds).
    temp_map : ndarray
        A 3D NumPy array of shape (time, space, component) representing:
        - temporal evolution (axis 0),
        - spatial distribution (axis 1),
        - components (axis 2), usually [electrons, phonons, magnetization].
    material_name : str
        The name of the material layer to extract temperature profiles from.

    Returns
    -------
    dict
        A dictionary with keys:
        - `"maps"`: list of dicts, each containing data for spatial temperature plots at mid-delay.
        - `"lines"`: list of dicts, each containing average temperature or magnetization vs. delay.

    Notes
    -----
    Intended to be used as a data provider for plotting functions, not for direct visualization.

    Examples
    --------
    >>> result = plot_results(S, delays, temp_map, "Fe")
    >>> result["maps"][0]["xlabel"]
    'Distance [nm]'
    """
    def tc(n):
        return 631 * (4 + 8 * np.cos(np.pi / (n + 1))) / 12

    n_values = np.arange(1, 21)
    tc_values = tc(n_values)

    distances = structure.get_distances_of_layers()[2].to('nm').magnitude
    delay_ps = delays.to('ps').magnitude
    select = structure.get_all_positions_per_unique_layer()[material_name]

    x_ticks = np.round(np.arange(0, 10.21, 0.6), 3)
    mid_idx = temp_map.shape[0] // 2

    maps = []
    for i, label in enumerate(["Electrons", "Phonons", "Magnetization"]):
        interp_func = interp1d(distances, temp_map[mid_idx, :, i], kind='linear', bounds_error=False,
                               fill_value="extrapolate")
        y_interp = interp_func(x_ticks)

        maps.append({
            "x": x_ticks,
            "y": y_interp,
            "label": label,
            "xlabel": "Distance [nm]",
            "ylabel": "Temperature [K]" if i < 2 else "Magnetization",
            "title": f"Temperature {label}" if i < 2 else "Magnetization"
        })

    lines = [
        {
            "x": delay_ps,
            "y": np.mean(temp_map[:, select,0], 1),
            "label": "electrons",
            "ylabel": "Temperature [K]",
            "xlabel": "Delay [ps]",
            "title": "M3TM Koopmans et. al"
        },
        {
            "x": delay_ps,
            "y": np.mean(temp_map[:, select,1], 1),
            "label": "phonons",
            "ylabel": "Temperature [K]",
            "xlabel": "Delay [ps]",
            "title": "M3TM Koopmans et. al"
        },
        {
            "x": delay_ps,
            "y": np.mean(temp_map[:, select,2], 1),
            "label": "M",
            "ylabel": "Magnetization",
            "xlabel": "Delay [ps]",
            "title": "Magnetization"
        }
    ]

    dim_effect = {
        "x": n_values,
        "y": tc_values,
        "label": "Ni",
        "xlabel": "n",
        "ylabel": "TC [K]",
        "title": "Dimensional Effect"
    }

    data = {
        "maps": maps,
        "lines": lines,
        "dim_effect": dim_effect
    }

    return data
