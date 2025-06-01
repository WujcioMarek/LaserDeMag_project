"""
Obsługa zapisu i odczytu danych symulacji.

---
Simulation data saving and loading utilities.
"""
import json, datetime, os
import xml.etree.ElementTree as ET
import xml.dom.minidom
from PyQt6.QtWidgets import QFileDialog, QMessageBox

REQUIRED_USER_FIELDS = {
    "material", "T0", "Tc", "mu", "fluence",
    "pulse_duration", "laser_wavelength", "ge", "asf"
}

ALLOWED_MATERIALS = ["Co", "Fe", "Gd", "Ni"]

def save_simulation_parameters(params, file_path, file_format, parameter_encoder, quantity_to_plain_func):
    """
    Zapisuje dane symulacji w formacie JSON lub XML.

    Args:
        params (dict): Parametry symulacji do zapisania.
        file_path (str): Ścieżka pliku docelowego (bez rozszerzenia).
        file_format (str): Format zapisu ("json" lub "xml").
        parameter_encoder (type): Niestandardowy encoder JSON.
        quantity_to_plain_func (callable): Funkcja konwertująca jednostki na wartości tekstowe.

    Returns:
        str: Pełna ścieżka zapisanego pliku.

    Raises:
        Exception: Gdy zapis się nie powiedzie.

    ---
    Saves simulation parameters to JSON or XML format.

    Args:
        params (dict): Parameters to be saved.
        file_path (str): Output file path (without extension).
        file_format (str): File format ("json" or "xml").
        parameter_encoder (type): Custom JSON encoder class.
        quantity_to_plain_func (callable): Function to convert quantities to plain values.

    Returns:
        str: Full path to the saved file.

    Raises:
        Exception: If saving fails.
    """
    if file_format == "json":
        if not file_path.lower().endswith(".json"):
            file_path += ".json"
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(params, f, indent=2, ensure_ascii=False, cls=parameter_encoder)
        return file_path

    elif file_format == "xml":
        if not file_path.lower().endswith(".xml"):
            file_path += ".xml"

        plain_params = quantity_to_plain_func(params)
        root = ET.Element("simulation_parameters")

        def add_dict_to_xml(parent, data):
            if isinstance(data, dict):
                for key, value in data.items():
                    child = ET.SubElement(parent, str(key))
                    add_dict_to_xml(child, value)
            elif isinstance(data, list):
                for item in data:
                    item_elem = ET.SubElement(parent, "item")
                    add_dict_to_xml(item_elem, item)
            else:
                parent.text = str(data)

        add_dict_to_xml(root, plain_params)

        rough_string = ET.tostring(root, 'utf-8')
        reparsed = xml.dom.minidom.parseString(rough_string)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(reparsed.toprettyxml(indent="  "))

        return file_path

    else:
        raise ValueError("Unsupported file format: " + file_format)

def load_simulation_parameters(file_path,parent_widget):
    """
       Wczytuje dane symulacji z pliku JSON.

       Args:
           file_path (str): Ścieżka do pliku .json
           parent_widget (QWidget): Rodzic do wyświetlenia komunikatów błędów.

       Returns:
           dict: Dane do wypełnienia formularza symulacji.

       Raises:
           ValueError: Gdy format pliku lub dane są niepoprawne.

       ---
       Loads simulation parameters from a JSON file.

       Args:
           file_path (str): Path to the .json file.
           parent_widget (QWidget): Parent widget for displaying error messages.

       Returns:
           dict: Parameters for simulation form filling.

       Raises:
           ValueError: If file or data is invalid.
       """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        if not isinstance(data, dict):
            error_message_format = parent_widget.error_invalid_format.format(fields=", ".join(REQUIRED_USER_FIELDS))
            raise ValueError(error_message_format)

        missing = REQUIRED_USER_FIELDS - data.keys()
        if missing:
            error_message = parent_widget.missing_fields_error.format(fields=", ".join(missing))
            raise ValueError(error_message)

        # Sprawdzenie czy wartości to liczby (zakładam, że pola numeryczne to poza "material")
        for key in REQUIRED_USER_FIELDS:
            if key == "material":
                continue  # pomijamy materiał w tym sprawdzeniu
            value = data[key]
            if not isinstance(value, (int, float)):
                raise ValueError(parent_widget.error_invalid_type.format(field=key))

        # Sprawdzenie czy materiał jest prawidłowy
        material = data.get("material")
        if material not in ALLOWED_MATERIALS:
            raise ValueError(parent_widget.error_invalid_material.format(
                material=material,
                allowed=", ".join(ALLOWED_MATERIALS)
            ))

        return {key: data[key] for key in REQUIRED_USER_FIELDS}

    except json.JSONDecodeError:
        raise ValueError(parent_widget.error_json_decode)

    except FileNotFoundError:
        raise ValueError(parent_widget.error_file_not_found.format(path=file_path))


def save_simulation_report(params, material_name, material_props, plot_data, parent=None, simulation_duration=None):
    """
    Tworzy i zapisuje raport z przebiegu symulacji do pliku tekstowego.

    Args:
        params (dict): Parametry wejściowe symulacji.
        material_name (str): Nazwa materiału.
        material_props (dict): Właściwości materiału.
        plot_data (dict): Dane do wykresów (linie, mapy).
        parent (QWidget, optional): Rodzic do komunikatów GUI.
        simulation_duration (float, optional): Czas trwania symulacji w sekundach.

    Returns:
        None

    ---
    Generates and saves a simulation report to a text file.

    Args:
        params (dict): Input parameters of the simulation.
        material_name (str): Name of the material.
        material_props (dict): Material properties.
        plot_data (dict): Plot data (lines and maps).
        parent (QWidget, optional): Parent widget for error messages.
        simulation_duration (float, optional): Simulation duration in seconds.

    Returns:
        None
    """
    file_path, selected_filter = QFileDialog.getSaveFileName(
        parent,
        "Zapisz raport symulacji",
        "",
        "Pliki tekstowe (*.txt);;Wszystkie pliki (*)",
        options=QFileDialog.Option.DontUseNativeDialog
    )

    if not file_path:
        return  # Użytkownik anulował

    if not os.path.splitext(file_path)[1]:
        file_path += ".txt"

    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write("Raport z symulacji LaserDeMag\n")
            f.write(f"Data symulacji: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            if simulation_duration is not None:
                f.write(f"Czas trwania symulacji: {simulation_duration:.2f} sekund\n")
            f.write("\n--- Parametry symulacji ---\n")
            for key, val in params.items():
                f.write(f"{key}: {val}\n")

            f.write(f"\n--- Materiał ---\n")
            f.write(f"Nazwa: {material_name}\n")
            for prop_key, prop_val in material_props.items():
                f.write(f"{prop_key}: {prop_val}\n")

            f.write("\n--- Wyniki symulacji (wybrane dane) ---\n")
            if 'maps' in plot_data:
                f.write("Mapy:\n")
                for i, d in enumerate(plot_data['maps']):
                    f.write(f"  Mapa {i + 1} - {d.get('title', '')}:\n")
                    f.write(f"    x: {d.get('x', [])[:5]}... (total {len(d.get('x', []))})\n")
                    f.write(f"    y: {d.get('y', [])[:5]}... (total {len(d.get('y', []))})\n")

            if 'lines' in plot_data:
                f.write("Wykresy liniowe:\n")
                for i, d in enumerate(plot_data['lines']):
                    f.write(f"  Linia {i + 1} - {d.get('title', '')}:\n")
                    f.write(f"    x: {d.get('x', [])[:5]}... (total {len(d.get('x', []))})\n")
                    f.write(f"    y: {d.get('y', [])[:5]}... (total {len(d.get('y', []))})\n")

            f.write("\n--- Koniec raportu ---\n")

    except Exception as e:
        QMessageBox.critical(
            parent,
            "Błąd zapisu",
            f"Błąd podczas zapisywania raportu:\n{str(e)}"
        )