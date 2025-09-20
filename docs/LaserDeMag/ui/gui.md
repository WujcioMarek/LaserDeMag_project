Module LaserDeMag.ui.gui
========================
Moduł GUI aplikacji symulacyjnej.

Zawiera definicję głównego okna aplikacji z interfejsem użytkownika do
wprowadzania parametrów symulacji, uruchamiania symulacji, wyświetlania
wyników na wykresach oraz zarządzania motywem kolorystycznym (ciemny/jasny).

Funkcjonalności obejmują:
- Walidację i pobieranie parametrów z formularza,
- Uruchamianie symulacji z wyświetleniem paska ładowania,
- Zarządzanie wykresami (podgląd, zapisywanie, zoom),
- Obsługę zapisu i ładowania danych symulacji w formatach JSON/XML,
- Przełączanie motywów UI oraz dynamiczne dostosowywanie stylów.

Moduł wykorzystuje PyQt6 do tworzenia interfejsu oraz integruje
logikę symulacji i zapisu danych.

---

GUI module for the simulation application.

Contains the main application window class with the user interface for
inputting simulation parameters, running simulations, displaying results
via plots, and managing color themes (dark/light).

Features include:
- Validation and retrieval of form parameters,
- Running simulations with a loading dialog,
- Plot management (viewing, saving, zooming),
- Saving and loading simulation data in JSON/XML formats,
- Switching UI themes and dynamically applying styles.

This module uses PyQt6 for the interface and integrates simulation logic
and data handling.

Functions
---------

`resource_path(relative_path)`
:   PL: Zwraca absolutną ścieżkę do zasobu, działającą zarówno w trybie skryptu (.py),
    jak i po spakowaniu aplikacji do .exe za pomocą PyInstaller.
    
    Funkcja sprawdza, czy aplikacja działa w środowisku uruchomieniowym PyInstaller
    (czyli czy istnieje atrybut _MEIPASS) i na tej podstawie buduje właściwą ścieżkę
    do pliku zasobu.
    
    EN: Returns the absolute path to a resource file, working both in development
    mode (.py script) and when the application is bundled into an .exe file using PyInstaller.
    
    The function checks whether the app is running in a PyInstaller environment
    (i.e., whether the _MEIPASS attribute exists), and constructs the proper
    path to the resource accordingly.
    
    :param relative_path: relative path to the resource (e.g. 'resources/config.json')
    :return: absolute path to the resource file

Classes
-------

`CustomTitleBar(parent)`
:   Klasa CustomTitleBar implementuje niestandardowy pasek tytułu okna z przyciskami
    do zmiany motywu, zmiany języka, minimalizacji, maksymalizacji i zamknięcia okna.
    
    Funkcje:
    - Obsługa kliknięć przycisków tematu (ciemny/jasny),
    - Przełączanie języka interfejsu (polski/angielski),
    - Obsługa zdarzeń podwójnego kliknięcia (maksymalizacja/przywracanie okna),
    - Aktualizacja widoczności przycisków w zależności od stanu okna.
    
    Signals:
    - theme_changed(str): Emitowany przy zmianie motywu ('light' lub 'dark'),
    - info_clicked(): Emitowany po kliknięciu przycisku informacji.
    
    ---
    
    CustomTitleBar class implements a custom window title bar with buttons
    for theme switching, language switching, minimizing, maximizing, and closing the window.
    
    Features:
    - Handling theme toggle button clicks (dark/light),
    - Switching UI language (Polish/English),
    - Handling double-click events for maximizing/restoring the window,
    - Updating button visibility depending on the window state.
    
    Signals:
    - theme_changed(str): Emitted when the theme changes ('light' or 'dark'),
    - info_clicked(): Emitted when the info button is clicked.

    ### Ancestors (in MRO)

    * PyQt6.QtWidgets.QWidget
    * PyQt6.QtCore.QObject
    * PyQt6.sip.wrapper
    * PyQt6.QtGui.QPaintDevice
    * PyQt6.sip.simplewrapper

    ### Methods

    `info_clicked(...)`
    :

    `mouseDoubleClickEvent(self, event)`
    :   Obsługuje zdarzenie podwójnego kliknięcia myszy na oknie.
        Jeśli okno jest zmaksymalizowane, przywraca je do normalnego rozmiaru,
        w przeciwnym razie maksymalizuje okno.
        
        Handles the mouse double-click event on the window.
        If the window is maximized, restores it to normal size,
        otherwise maximizes the window.
        
        Args:
            event (QMouseEvent): Zdarzenie podwójnego kliknięcia myszy / Mouse double-click event.
        
        Returns:
            None

    `theme_changed(...)`
    :

    `toggle_theme(self)`
    :   Przełącza motyw aplikacji między jasnym a ciemnym.
        Aktualizuje ikonę przycisku i styl tytułu w zależności od motywu.
        
        Toggles the application theme between light and dark.
        Updates the button icon and title style according to the theme.
        
        Args:
            None
        
        Returns:
            None

    `window_state_changed(self, state)`
    :   Aktualizuje widoczność przycisków maksymalizacji i przywrócenia
        w zależności od aktualnego stanu okna.
        
        Updates the visibility of maximize and restore buttons
        depending on the current window state.
        
        Args:
            state (Qt.WindowState): Aktualny stan okna / Current window state.
        
        Returns:
            None

`LoadingDialog(title, message, image_path=None)`
:   Okno dialogowe wyświetlające komunikat ładowania z opcjonalnym obrazkiem.
    
    Args:
        title (str): Tytuł okna dialogowego.
        message (str): Komunikat wyświetlany w oknie.
        image_path (str, optional): Ścieżka do obrazka do wyświetlenia. Domyślnie None.
    
    ---
    Loading dialog window displaying a message with optional image.
    
    Args:
        title (str): Dialog window title.
        message (str): Message shown in the dialog.
        image_path (str, optional): Path to an image to display. Default is None.

    ### Ancestors (in MRO)

    * PyQt6.QtWidgets.QDialog
    * PyQt6.QtWidgets.QWidget
    * PyQt6.QtCore.QObject
    * PyQt6.sip.wrapper
    * PyQt6.QtGui.QPaintDevice
    * PyQt6.sip.simplewrapper

`MainWindow()`
:   Główne okno aplikacji LaserDeMag.
    
    Okno zawiera niestandardowy pasek tytułu, panel kontrolny z formularzem
    do wprowadzania parametrów symulacji oraz obszar wykresów wyników.
    Zapewnia obsługę zmiany motywu, języka, wczytywania danych z pliku,
    czyszczenia pól, uruchamiania symulacji oraz sterowania wykresami
    (przełączanie, pobieranie, powiększanie).
    
    Elementy UI:
    - Pasek tytułu (CustomTitleBar) z przyciskami do sterowania oknem i zmianą motywu/języka,
    - Panel formularza z grupami pól: Materiał, Laser, Inne,
    - Przyciski akcji: wczytaj z pliku, wyczyść, rozpocznij symulację,
    - Obszar wykresu (PlotCanvas) wraz z przyciskami do zmiany wykresów i pobierania danych.
    
    ---
    
    Main application window for LaserDeMag.
    
    The window contains a custom title bar, a control panel with a form
    for simulation parameters input, and a plotting area for results.
    It supports theme switching, language update, loading data from file,
    clearing input fields, starting simulation, and plot controls
    (switching plots, downloading plots/data, zooming).
    
    UI Elements:
    - Custom title bar (CustomTitleBar) with window control and theme/language buttons,
    - Form panel with grouped input fields: Material, Laser, Others,
    - Action buttons: load from file, clear fields, start simulation,
    - Plot area (PlotCanvas) with buttons for switching plots and downloading data.

    ### Ancestors (in MRO)

    * PyQt6.QtWidgets.QMainWindow
    * PyQt6.QtWidgets.QWidget
    * PyQt6.QtCore.QObject
    * PyQt6.sip.wrapper
    * PyQt6.QtGui.QPaintDevice
    * PyQt6.sip.simplewrapper

    ### Methods

    `changeEvent(self, event)`
    :   Obsługuje zdarzenia zmiany stanu okna, np. maksymalizacji.
        Handles window state change events, e.g., maximization.
        
        Przekazuje zdarzenie do paska tytułu, aby zaktualizować przyciski.
        Forwards the event to the title bar to update buttons accordingly.

    `change_theme(self, theme: str)`
    :   Zmienia motyw graficzny aplikacji na ciemny lub jasny.
        
        Args:
            theme (str): Nazwa motywu, np. 'dark' lub 'light'.
        
        Changes the application's graphical theme to dark or light.
        
        Args:
            theme (str): Theme name, e.g., 'dark' or 'light'.

    `clear_fields(self)`
    :   Czyści wszystkie pola formularza i resetuje wybór materiału.
        
        Czyści również obszar wykresu, jeśli istnieje.
        
        Clears all form fields and resets material selection.
        
        Also clears the plot area if it exists.

    `collect_simulation_parameters(self)`
    :   Zbiera wszystkie parametry symulacji, łącznie z danymi formularza i właściwościami materiału.
        
        Collects all simulation parameters, including form inputs and material properties.

    `download_all_plots(self)`
    :   Otwiera dialog wyboru folderu i zapisuje wszystkie wykresy do wybranego katalogu.
        
        Opens directory selection dialog and saves all plots to the chosen folder.

    `download_current_plot(self)`
    :   Otwiera dialog zapisu i zapisuje aktualnie wyświetlany wykres do pliku.
        
        Opens save dialog and saves the currently displayed plot to a file.

    `download_data(self)`
    :   Pyta użytkownika o format (JSON lub XML), następnie zapisuje dane symulacji.
        
        Asks user for format (JSON or XML), then saves simulation data.

    `get_params_from_form(self)`
    :   Pobiera i waliduje parametry z formularza GUI.
        
        Retrieves and validates parameters from the GUI form.

    `load_user_data(self)`
    :   Otwiera dialog wyboru pliku i ładuje dane użytkownika z pliku JSON,
        następnie wypełnia formularz danymi.
        
        Opens file selection dialog and loads user data from a JSON file,
        then populates the form with the loaded data.

    `mouseMoveEvent(self, event)`
    :   Obsługuje przesuwanie myszy podczas przeciągania okna.
        
        Przesuwa okno zgodnie z ruchem myszy, jeśli wcześniej zapisana została pozycja startowa.
        
        Handles mouse move events during window dragging.
        
        Moves the window according to mouse movement if initial click position was saved.

    `mousePressEvent(self, event)`
    :   Obsługuje naciśnięcie przycisku myszy.
        
        Jeśli lewy przycisk i okno jest zmaksymalizowane, przywraca do rozmiaru normalnego
        i zapisuje pozycję kliknięcia, by umożliwić płynne przeciąganie.
        
        Handles mouse press events.
        
        If left button is pressed and window is maximized, restores to normal size
        and records click position to enable smooth dragging.

    `mouseReleaseEvent(self, event)`
    :   Obsługuje zwolnienie przycisku myszy.
        
        Jeśli okno nie jest zmaksymalizowane, a jego górna krawędź dotyka górnej krawędzi ekranu,
        automatycznie maksymalizuje okno.
        
        Handles mouse release events.
        
        If the window is not maximized and its top edge touches the top of the screen,
        automatically maximizes the window.

    `on_simulation_error(self, e)`
    :   Obsługuje błędy symulacji, zamyka dialog ładowania i wyświetla komunikat krytyczny.
        
        Handles simulation errors, closes loading dialog, and shows critical message.

    `on_simulation_finished(self, result)`
    :   Obsługuje zakończenie symulacji, aktualizuje wykres i zamyka dialog ładowania.
        
        Handles simulation finish, updates plot, and closes loading dialog.

    `populate_user_form(self, data: dict)`
    :   Wypełnia formularz GUI na podstawie danych z pliku.
        
        Fills the GUI form fields based on the loaded data.
        
        Args:
            data (dict): Dictionary with parameters to set in the form.

    `set_dark_ui(self)`
    :   Ustawia ciemny motyw interfejsu użytkownika,
        zmieniając kolory tekstów, ikon oraz paletę kolorów aplikacji.
        
        Sets the dark UI theme by changing text colors, icons,
        and the application color palette.

    `set_light_ui(self)`
    :   Ustawia jasny motyw interfejsu użytkownika,
        zmieniając kolory tekstów, ikon oraz paletę kolorów aplikacji.
        
        Sets the light UI theme by changing text colors, icons,
        and the application color palette.

    `show_info_message(self)`
    :   Wyświetla okno dialogowe z informacjami o aplikacji.
        Displays an information dialog about the application.
        
        Treść i tytuł pobierane są z tłumaczeń dla aktualnego języka.
        The content and title are loaded from translations for the current language.

    `start_simulation(self)`
    :   Uruchamia symulację na podstawie parametrów z formularza,
        pokazuje dialog ładowania i obsługuje wyniki oraz błędy.
        
        Starts the simulation based on form parameters,
        shows loading dialog, and handles results and errors.

    `switch_plot_down(self)`
    :   Przełącza wykres na poprzedni typ i aktualizuje wyświetlenie.
        
        Switches plot to the previous type and updates display.

    `switch_plot_up(self)`
    :   Przełącza wykres na następny typ i aktualizuje wyświetlenie.
        
        Switches plot to the next type and updates display.

    `update_language(self, lang)`
    :   Aktualizuje interfejs użytkownika na wybrany język.
        
        Ustawia teksty etykiet, tytuły grup, przycisków i komunikatów błędów
        na podstawie słownika tłumaczeń.
        
        Args:
            lang (str): Kod wybranego języka (np. "English", "Polski").
        
        Updates the user interface to the selected language.
        
        Sets label texts, group titles, buttons, and error messages
        based on the translation dictionary.
        
        Args:
            lang (str): Selected language code (e.g., "English", "Polski").

    `update_plot(self)`
    :   Aktualizuje wykres w GUI w zależności od aktualnego indeksu wykresu.
        
        Updates the GUI plot depending on the current plot index.

    `window_state_changed(self, state)`
    :   Aktualizuje widoczność przycisków maksymalizacji i przywracania okna
        w zależności od obecnego stanu okna (zmaksymalizowane/normalne).
        
        Updates the visibility of maximize and restore buttons depending on the window state (maximized/normal).

    `zoom_plot(self)`
    :   Otwiera aktualny wykres w trybie pełnoekranowym.
        
        Opens the current plot in fullscreen mode.

`ParameterEncoder(*, skipkeys=False, ensure_ascii=True, check_circular=True, allow_nan=True, sort_keys=False, indent=None, separators=None, default=None)`
:   Niestandardowy enkoder JSON dla obiektów używanych w aplikacji.
    
    Obsługiwane typy:
    - Quantity (Pint)
    - NumPy scalars i tablice
    - liczby zespolone
    - krotki (zamieniane na listy)
    
    ---
    Custom JSON encoder for application-specific objects.
    
    Supports:
    - Quantity (Pint)
    - NumPy scalars and arrays
    - complex numbers
    - tuples (converted to lists)
    
    Constructor for JSONEncoder, with sensible defaults.
    
    If skipkeys is false, then it is a TypeError to attempt
    encoding of keys that are not str, int, float or None.  If
    skipkeys is True, such items are simply skipped.
    
    If ensure_ascii is true, the output is guaranteed to be str
    objects with all incoming non-ASCII characters escaped.  If
    ensure_ascii is false, the output can contain non-ASCII characters.
    
    If check_circular is true, then lists, dicts, and custom encoded
    objects will be checked for circular references during encoding to
    prevent an infinite recursion (which would cause an RecursionError).
    Otherwise, no such check takes place.
    
    If allow_nan is true, then NaN, Infinity, and -Infinity will be
    encoded as such.  This behavior is not JSON specification compliant,
    but is consistent with most JavaScript based encoders and decoders.
    Otherwise, it will be a ValueError to encode such floats.
    
    If sort_keys is true, then the output of dictionaries will be
    sorted by key; this is useful for regression tests to ensure
    that JSON serializations can be compared on a day-to-day basis.
    
    If indent is a non-negative integer, then JSON array
    elements and object members will be pretty-printed with that
    indent level.  An indent level of 0 will only insert newlines.
    None is the most compact representation.
    
    If specified, separators should be an (item_separator, key_separator)
    tuple.  The default is (', ', ': ') if *indent* is ``None`` and
    (',', ': ') otherwise.  To get the most compact JSON representation,
    you should specify (',', ':') to eliminate whitespace.
    
    If specified, default is a function that gets called for objects
    that can't otherwise be serialized.  It should return a JSON encodable
    version of the object or raise a ``TypeError``.

    ### Ancestors (in MRO)

    * json.encoder.JSONEncoder

    ### Methods

    `default(self, obj)`
    :   Konwertuje niestandardowe typy obiektów na format JSON-serializowalny.
        
        Obsługiwane typy:
        - Quantity (Pint): zwraca słownik z wartością i jednostką.
        - NumPy scalar: konwertuje na typ natywny Pythona.
        - NumPy array: konwertuje na listę.
        - Complex: zwraca słownik z częścią rzeczywistą i urojoną.
        - Tuple: konwertuje na listę.
        - Inne: wywołuje metodę bazową `default`.
        
        Args:
            obj: Obiekt do serializacji.
        
        Returns:
            JSON-serializowalny obiekt.
        
        Converts custom object types to JSON-serializable formats.
        
        Supported types:
        - Quantity (Pint): returns a dict with value and unit.
        - NumPy scalar: converts to native Python type.
        - NumPy array: converts to list.
        - Complex number: returns dict with real and imaginary parts.
        - Tuple: converts to list.
        - Others: calls base `default` method.
        
        Args:
            obj: Object to serialize.
        
        Returns:
            JSON-serializable object.

`PlotCanvas(parent=None)`
:   Widget wykresu bazujący na matplotlib do wyświetlania wykresów liniowych i map danych.
    
    Funkcje:
    - wyświetlanie map danych (3 wykresy)
    - wyświetlanie wykresów liniowych (2 wykresy w układzie 2x1)
    - zapisywanie aktualnego wykresu lub wszystkich wykresów do plików
    - wyświetlanie wykresu w trybie pełnoekranowym
    - aktualizacja komunikatów ostrzeżeń i informacji
    
    Args:
        parent (QWidget, optional): Rodzic widgetu. Domyślnie None.
    
    ---
    Matplotlib-based plot widget for displaying line plots and data maps.
    
    Features:
    - show map plots (3 subplots)
    - show line plots (2 subplots)
    - save current plot or all plots to files
    - fullscreen plot preview
    - update warning and info messages
    
    Args:
        parent (QWidget, optional): Parent widget. Default is None.

    ### Ancestors (in MRO)

    * matplotlib.backends.backend_qtagg.FigureCanvasQTAgg
    * matplotlib.backends.backend_agg.FigureCanvasAgg
    * matplotlib.backends.backend_qt.FigureCanvasQT
    * matplotlib.backend_bases.FigureCanvasBase
    * PyQt6.QtWidgets.QWidget
    * PyQt6.QtCore.QObject
    * PyQt6.sip.wrapper
    * PyQt6.QtGui.QPaintDevice
    * PyQt6.sip.simplewrapper

    ### Methods

    `clear(self)`
    :   Czyści aktualne dane wykresu i rysuje pusty wykres.
        
        ---
        Clears current plot data and redraws an empty plot.

    `open_current_plot_fullscreen(self)`
    :   Pokazuje aktualny wykres w trybie pełnoekranowym w nowym oknie.
        
        ---
        Shows the current plot in fullscreen mode in a new window.

    `save_all_plots(self, directory)`
    :   Zapisuje wszystkie dostępne wykresy do wskazanego katalogu.
        
        Args:
            directory (str): Ścieżka do katalogu, w którym zapisywane będą wykresy.
        
        Wyświetla komunikat o sukcesie lub błędzie.
        
        ---
        Saves all available plots to the specified directory.
        
        Args:
            directory (str): Path to the directory where plots will be saved.
        
        Shows success or error message box.

    `save_current_plot(self, file_path)`
    :   Zapisuje aktualny wykres do pliku.
        
        Args:
            file_path (str): Ścieżka pliku, do którego zostanie zapisany wykres.
        
        Wyświetla komunikat o sukcesie lub błędzie.
        
        ---
        Saves the current plot to a file.
        
        Args:
            file_path (str): Path to the file where the plot will be saved.
        
        Shows success or error message box.

    `set_all_plots(self, figures)`
    :   Ustawia dane wykresów do wyświetlenia.
        
        Args:
            figures (dict): Dane wykresów.
        
        ---
        Sets plot data for displaying.
        
        Args:
            figures (dict): Plot data.

    `show_critical(self)`
    :   Wyświetla okno dialogowe z krytycznym błędem.
        
        Displays a critical error message box.
        
        Args:
            None
        
        Returns:
            None

    `show_dimensional_effect_plot(self, dim_effect_data)`
    :   Wyświetla wykres efektu wymiarowego z możliwością podglądu wartości Y po najechaniu na punkt.
        
        Args:
            dim_effect_data (dict): Słownik z kluczami: 'x', 'y', 'xlabel', 'ylabel', 'title', 'label'.
        
        ---
        Displays dimensional effect plot with value tooltip on hover.
        
        Args:
            dim_effect_data (dict): Dictionary with keys: 'x', 'y', 'xlabel', 'ylabel', 'title', 'label'.

    `show_information(self)`
    :   Wyświetla okno dialogowe z informacją.
        
        Displays an information message box.
        
        Args:
            None
        
        Returns:
            None

    `show_line_plot(self, line_data)`
    :   Wyświetla wykres liniowy składający się z dwóch podwykresów.
        
        Args:
            line_data (list of dict): Lista słowników z danymi do wykresu liniowego,
                                      każdy słownik z kluczami: 'x', 'y', 'xlabel', 'ylabel', 'title', 'label'
        
        ---
        Shows a line plot consisting of two subplots.
        
        Args:
            line_data (list of dict): List of dicts with line plot data, each dict containing keys:
                                      'x', 'y', 'xlabel', 'ylabel', 'title', 'label'

    `show_map_plot(self, map_data)`
    :   Wyświetla wykres mapy danych z trzema podwykresami.
        
        Args:
            map_data (list of dict): Lista słowników zawierających dane do wykresu,
                                     każdy z kluczami: 'x', 'y', 'xlabel', 'ylabel', 'title', 'label'
        
        ---
        Shows a map plot with three subplots.
        
        Args:
            map_data (list of dict): List of dicts containing plot data with keys:
                                     'x', 'y', 'xlabel', 'ylabel', 'title', 'label'

    `show_warning(self)`
    :   Wyświetla okno dialogowe z ostrzeżeniem.
        
        Displays a warning message box.
        
        Args:
            None
        
        Returns:
            None

    `update_messages(self, translations)`
    :   Aktualizuje komunikaty ostrzeżeń, informacji i błędów.
        
        Args:
            translations (dict): Słownik z komunikatami z kluczami 'warning', 'info', 'critical'.
        
        ---
        Updates warning, information, and critical message texts.
        
        Args:
            translations (dict): Dictionary with keys 'warning', 'info', 'critical'.