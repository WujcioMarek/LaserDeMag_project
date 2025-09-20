Module LaserDeMag.io.file_handler
=================================
Obsługa zapisu i odczytu danych symulacji.

---
Simulation data saving and loading utilities.

Functions
---------

`generate_graph()`
:   Uruchamia graficzny interfejs do generowania wykresów z plików Excel.
    
    Funkcja otwiera okno aplikacji, w którym użytkownik może:
      - wybrać plik Excel (.xlsx, .xls),
      - wskazać arkusze do analizy,
      - wygenerować i zapisać wykresy na podstawie danych z tych arkuszy.
    
    Wykresy generowane są dla zdefiniowanych kolumn (np. elektronów, fononów, magnetyzacji),
    a następnie zapisywane w tym samym katalogu co wybrany plik Excel,
    z predefiniowanymi nazwami plików PNG. Każdy wykres zawiera dane z wielu arkuszy
    w formie osobnych linii z legendą.
    
    Obsługiwane są sytuacje wyjątkowe:
      - brak wyboru pliku lub arkusza,
      - błędy przy odczycie arkuszy,
      - błędy przy generowaniu wykresów.
    Komunikaty błędów i sukcesów wyświetlane są w oknach dialogowych.
    
    Args:
        Brak (funkcja nie przyjmuje parametrów, wszystkie dane wybierane są przez GUI).
    
    Returns:
        None
    
    Raises:
        Exception: Gdy wystąpi błąd przy odczytywaniu arkuszy lub generowaniu wykresów.
    
    ---
    Launches a graphical interface for generating plots from Excel files.
    
    The function opens a GUI window where the user can:
      - select an Excel file (.xlsx, .xls),
      - choose sheets to analyze,
      - generate and save plots based on the selected sheets.
    
    Plots are created for predefined columns (e.g., electrons, phonons, magnetization)
    and saved as PNG files in the same directory as the chosen Excel file.
    Each plot combines data from multiple sheets, displayed as separate lines with legends.
    
    The function handles exceptional situations:
      - no file or sheet selected,
      - errors reading sheets,
      - errors generating plots.
    All errors and success messages are shown in dialog boxes.
    
    Args:
        None (the function takes no parameters; all inputs are provided through the GUI).
    
    Returns:
        None
    
    Raises:
        Exception: If an error occurs while reading sheets or generating plots.

`load_simulation_parameters(file_path, parent_widget)`
:   Wczytuje dane symulacji z pliku JSON.
    
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

`save_simulation_parameters(params, file_path, file_format, parameter_encoder, quantity_to_plain_func)`
:   Zapisuje dane symulacji w formacie JSON lub XML.
    
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

`save_simulation_report(params, material_name, material_props, plot_data, parent=None, simulation_duration=None)`
:   Tworzy i zapisuje raport z przebiegu symulacji do pliku tekstowego.
    
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

`save_simulation_to_excel(params, plot_data)`
:   Zapisuje dane symulacji do pliku Excel (XLSX) w katalogu uruchomienia aplikacji.
    
    Funkcja tworzy (jeśli nie istnieje) lub otwiera plik o nazwie 'Simulations.xlsx' w folderze,
    w którym uruchamiana jest aplikacja. Dla każdej symulacji tworzony jest nowy arkusz,
    którego nazwa zawiera liczbę warstw i moc lasera, np.: 'N=4, Fluence=2.5'.
    
    Jeśli arkusz o danej nazwie już istnieje, funkcja doda numer sufiksu (np. _1, _2 itd.),
    aby uniknąć nadpisywania danych.
    
    Parametry wejściowe zapisywane są w pierwszych dwóch wierszach arkusza,
    a dane z wykresów liniowych w układzie poziomym (każdy wykres w dwóch kolumnach: x i y),
    z jedną pustą kolumną odstępu między kolejnymi wykresami.
    
    Args:
        params (dict): Parametry symulacji do zapisania. Muszą zawierać co najmniej:
                       - "liczba_warstw" (int)
                       - "moc_lasera" (float lub str)
        plot_data (dict): Dane wykresów w formacie {"lines": [{"title": ..., "x": [...], "y": [...]}]}.
    
    Returns:
        None
    
    Raises:
        Exception: Gdy zapis do pliku się nie powiedzie.
    
    ---
    Saves simulation data to an Excel (XLSX) file in the application's execution directory.
    
    The function creates (if missing) or opens 'Simulations.xlsx' and adds a new sheet for each simulation.
    The sheet name is based on the number of layers and laser fluence, e.g., 'N=4, Fluence=2.5'.
    
    If a sheet with that name already exists, the function adds a numeric suffix to avoid overwriting.
    
    The function writes input parameters in the first two rows,
    and line chart data in a horizontal layout (each chart gets two columns: x and y),
    with one empty column of spacing between charts.
    
    Args:
        params (dict): Simulation parameters to save. Must include at least:
                       - "liczba_warstw" (int)
                       - "moc_lasera" (float or str)
        plot_data (dict): Plot data in the format {"lines": [{"title": ..., "x": [...], "y": [...]}]}.
    
    Returns:
        None
    
    Raises:
        Exception: If saving the file fails.