Module LaserDeMag.physics.model_3TM
===================================

Functions
---------

`create_structure(material_obj, prop, N)`
:   Tworzy strukturę 1D cienkiej warstwy dla modelu 3TM.
    
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

`fake_notebook(*args, **kwargs)`
:   Zastępuje funkcję `tqdm.notebook` wersją terminalową.
    
    ---
    Replaces `tqdm.notebook` with terminal-compatible `tqdm`.
    
    Returns:
        tqdm.tqdm instance

`get_material_properties(material, Tc)`
:   Tworzy obiekt materiału oraz zwraca właściwości fizyczne dla modelu 3TM.
    
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