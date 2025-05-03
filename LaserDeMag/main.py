from ui.gui import get_input_parameters
from physics.model_3TM import get_material_properties, create_structure
from simulation.runner import run_simulation
from visual.plotter import draw_structure

def main():
    params = get_input_parameters()
    material_obj, prop = get_material_properties(params['material'], params['Tc'], params['mu'], params['ge'])
    S = create_structure(material_obj, prop)

    draw_structure(S, material_obj)
    run_simulation(S, params)

if __name__ == "__main__":
    main()