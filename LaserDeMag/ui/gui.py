def get_input_parameters():
    default_params = {
        'material': 'CoNi',
        'T0': 300,
        'Tc': 1388,
        'mu': 1.5,
        'fluence': 30,
        'pulse_duration': 0.05,
        'laser_wavelength': 800,
        'ge': 4.0e18,
        'asf': 0.1
    }

    params = {}
    for key, default in default_params.items():
        val = input(f"Podaj {key} (domyślnie {default}): ") or default
        params[key] = float(val) if isinstance(default, (float, int)) else val

    return params
