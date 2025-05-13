from LaserDeMag.physics.model_3TM import get_material_properties, create_structure
from LaserDeMag.simulation.runner import run_simulation

def main(params):
    material_obj, prop = get_material_properties(params['material'], params['Tc'], params['mu'], params['ge'])
    S = create_structure(material_obj, prop)
    material_name = material_obj.name
    return run_simulation(S, params, material_name)