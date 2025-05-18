"""
Data saving and reading support.
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
    Zapisz dane symulacji do pliku w formacie JSON lub XML.

    Args:
        params (dict): Dane do zapisania.
        file_path (str): Ścieżka do pliku (bez rozszerzenia).
        file_format (str): "json" lub "xml".
        parameter_encoder: Custom JSON encoder (np. ParameterEncoder).
        quantity_to_plain_func: Funkcja do konwersji jednostek (dla XML).
    Returns:
        str: Ścieżka zapisanego pliku.
    Raises:
        Exception: Jeśli zapis się nie powiedzie.
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
    Wczytuje dane symulacji z pliku JSON i zwraca je jako słownik.

    Args:
        file_path (str): Ścieżka do pliku .json

    Returns:
        dict: Dane do uzupełnienia formularza

    Raises:
        FileNotFoundError, json.JSONDecodeError, ValueError
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