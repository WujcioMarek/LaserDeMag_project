def get_material_properties(material_name, Tc, mu, ges, asf):
    prop = {
        "Ni": {
            "Ce": 70,               # J/kg/K – elektronowa
            "Cp": 2.33e6,           # J/kg/K – fononowa
            "C": 2.5e6,             # całkowita
            "gep": 4.05e18,
            "kappa": 90.7,
            "R": 17.2,
            "Vat": 1.08e-29,
            "Ep": 1.5,
            "mu_at": 0.6,
            "dz": 1e-9,
            "nz": 10,
            "dt": 1e-15,
            "nt": 1000
        },
        "Co": {
            "Ce": 67,
            "Cp": 2.07e6,
            "C": 2.3e6,
            "gep": 4.10e18,
            "kappa": 100,
            "R": 25.3,
            "Vat": 1.09e-29,
            "Ep": 1.8,
            "mu_at": 1.7,
            "dz": 1e-9,
            "nz": 10,
            "dt": 1e-15,
            "nt": 1000
        },
        "Gd": {
            "Ce": 58,
            "Cp": 1.78e6,
            "C": 2.1e6,
            "gep": 2.01e18,
            "kappa": 10.5,
            "R": 0.092,
            "Vat": 2.59e-29,
            "Ep": 0.8,
            "mu_at": 7.5,
            "dz": 1e-9,
            "nz": 10,
            "dt": 1e-15,
            "nt": 1000
        }
    }

    values = prop[material_name].copy()
    values.update({
        "Tc": Tc,
        "mu": mu,
        "ge": ges,
        "asf": asf
    })

    # Wyliczenie Cs = C - Ce - Cp
    Ce = values["Ce"]
    Cp = values["Cp"]
    C = values["C"]
    Cs = C - Ce - Cp

    if Cs < 0:
        raise ValueError(f"Wyliczona Cs < 0 dla materiału {material_name}. Sprawdź dane wejściowe.")
    values["Cs"] = Cs

    return material_name, values
