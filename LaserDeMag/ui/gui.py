"""
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
"""
import json, os, time, sys
import numpy as np
from PyQt6.QtCore import QSize, Qt, QEvent, pyqtSignal, QPoint
from PyQt6.QtGui import QPalette, QIcon, QColor, QFont, QPixmap
from PyQt6.QtWidgets import (QApplication, QHBoxLayout, QLabel, QMainWindow, QToolButton, QVBoxLayout, QWidget,
                             QPushButton, QGroupBox, QGridLayout, QLineEdit, QComboBox, QFrame, QMessageBox,
                             QSizePolicy, QSplitter, QSpacerItem, QFileDialog, QDialog)
from matplotlib import pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from LaserDeMag.physics.model_3TM import get_material_properties
from LaserDeMag.main import main
from pint import Quantity
from LaserDeMag.io.file_handler import save_simulation_parameters, load_simulation_parameters, save_simulation_report

if getattr(sys, 'frozen', False):
    sys.stdout = open(os.devnull, 'w')
    sys.stderr = open(os.devnull, 'w')

def resource_path(relative_path):
    """
    PL: Zwraca absolutną ścieżkę do zasobu, działającą zarówno w trybie skryptu (.py),
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
    """
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    return os.path.join(base_path, relative_path)

class LoadingDialog(QDialog):
    """
    Okno dialogowe wyświetlające komunikat ładowania z opcjonalnym obrazkiem.

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
    """
    def __init__(self, title, message, image_path=None):
        super().__init__()
        self.setWindowTitle(title)
        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.CustomizeWindowHint | Qt.WindowType.WindowTitleHint)
        self.setModal(True)
        layout = QVBoxLayout()

        self.label = QLabel(message)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.label)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.addSpacing(10)

        if image_path:
            self.image_label = QLabel()
            self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            pixmap = QPixmap(image_path)
            scaled_pixmap = pixmap.scaled(200, 200, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            self.image_label.setPixmap(scaled_pixmap)
            layout.addWidget(self.image_label)
        self.setLayout(layout)

class ParameterEncoder(json.JSONEncoder):
    """
    Niestandardowy enkoder JSON dla obiektów używanych w aplikacji.

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
    """
    def default(self, obj):
        """
        Konwertuje niestandardowe typy obiektów na format JSON-serializowalny.

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
        """
        # Pint Quantity
        if isinstance(obj, Quantity):
            return {"value": obj.magnitude, "unit": str(obj.units)}
        # NumPy scalar
        if isinstance(obj, (np.generic,)):
            return obj.item()
        # NumPy array
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        # Complex
        if isinstance(obj, complex):
            return {"real": obj.real, "imag": obj.imag}
        # tuple -> list
        if isinstance(obj, tuple):
            return list(obj)
        # everything else
        return super().default(obj)

class PlotCanvas(FigureCanvas):
    """
    Widget wykresu bazujący na matplotlib do wyświetlania wykresów liniowych i map danych.

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
    """
    def __init__(self, parent=None):
        self.fig = Figure(figsize=(5, 4), dpi=100)
        super().__init__(self.fig)
        self.setParent(parent)

        self.orig_parent = parent
        self.orig_layout = parent.layout() if parent else None

        self.warning_message = ""
        self.information_message = ""
        self.critical_message = ""

    def clear(self):
        """
        Czyści aktualne dane wykresu i rysuje pusty wykres.

        ---
        Clears current plot data and redraws an empty plot.
        """
        self.plot_data = {}
        self.fig.clf()
        self.draw()

    def show_map_plot(self, map_data):
        """
        Wyświetla wykres mapy danych z trzema podwykresami.

        Args:
            map_data (list of dict): Lista słowników zawierających dane do wykresu,
                                     każdy z kluczami: 'x', 'y', 'xlabel', 'ylabel', 'title', 'label'

        ---
        Shows a map plot with three subplots.

        Args:
            map_data (list of dict): List of dicts containing plot data with keys:
                                     'x', 'y', 'xlabel', 'ylabel', 'title', 'label'
        """
        self.current_plot_type = "map"
        self.current_plot_index = 0
        self.plot_data["maps"] = map_data
        self.fig.clf()
        axs = self.fig.subplots(3, 1)
        for i, ax in enumerate(axs):
            d = map_data[i]
            ax.plot(d["x"], d["y"], label=d.get("label", ""))
            ax.set_xlabel(d["xlabel"])
            ax.set_ylabel(d["ylabel"])
            ax.set_title(d["title"])
            ax.legend()
        self.fig.tight_layout()
        self.fig.subplots_adjust(hspace=0.4)
        self.draw()

    def show_line_plot(self, line_data):
        """
        Wyświetla wykres liniowy składający się z dwóch podwykresów.

        Args:
            line_data (list of dict): Lista słowników z danymi do wykresu liniowego,
                                      każdy słownik z kluczami: 'x', 'y', 'xlabel', 'ylabel', 'title', 'label'

        ---
        Shows a line plot consisting of two subplots.

        Args:
            line_data (list of dict): List of dicts with line plot data, each dict containing keys:
                                      'x', 'y', 'xlabel', 'ylabel', 'title', 'label'
        """
        self.current_plot_type = "line"
        self.current_plot_index = 0
        self.plot_data["lines"] = line_data
        self.fig.clf()
        axs = self.fig.subplots(2, 1)
        axs[0].plot(line_data[0]["x"], line_data[0]["y"], label=line_data[0]["label"])
        axs[0].plot(line_data[1]["x"], line_data[1]["y"], label=line_data[1]["label"])
        axs[0].set_title(line_data[0]["title"])
        axs[0].set_xlabel(line_data[0]["xlabel"])
        axs[0].set_ylabel(line_data[0]["ylabel"])
        axs[0].legend()

        axs[1].plot(line_data[2]["x"], line_data[2]["y"], label=line_data[2]["label"])
        axs[1].set_title(line_data[2]["title"])
        axs[1].set_xlabel(line_data[2]["xlabel"])
        axs[1].set_ylabel(line_data[2]["ylabel"])
        axs[1].legend()
        self.draw()

    def save_current_plot(self, file_path):
        """
        Zapisuje aktualny wykres do pliku.

        Args:
            file_path (str): Ścieżka pliku, do którego zostanie zapisany wykres.

        Wyświetla komunikat o sukcesie lub błędzie.

        ---
        Saves the current plot to a file.

        Args:
            file_path (str): Path to the file where the plot will be saved.

        Shows success or error message box.
        """
        try:
            self.fig.savefig(file_path, bbox_inches='tight')
            QMessageBox.information(
                self,
                self.information_message["title"],
                f"{self.information_message['message']}\n{file_path}"
            )
        except Exception as e:
            QMessageBox.critical(
                self,
                self.critical_message["title"],
                f"{self.critical_message['message']}:\n{str(e)}"
            )

    def save_all_plots(self, directory):
        """
        Zapisuje wszystkie dostępne wykresy do wskazanego katalogu.

        Args:
            directory (str): Ścieżka do katalogu, w którym zapisywane będą wykresy.

        Wyświetla komunikat o sukcesie lub błędzie.

        ---
        Saves all available plots to the specified directory.

        Args:
            directory (str): Path to the directory where plots will be saved.

        Shows success or error message box.
        """
        try:
            if not hasattr(self, "plot_data") or not self.plot_data:
                QMessageBox.warning(self, self.warning_message["title"], self.warning_message["message"])
                return
            line_groups = []
            lines = self.plot_data.get("lines", [])
            if lines:
                if len(lines) >= 3:
                    line_groups.append(lines[0:2])  # pierwszy wykres: electrons + phonons
                    line_groups.append([lines[2]])  # drugi wykres: magnetization
                else:
                    line_groups.append(lines)  # fallback: wszystko w jednym

            all_plots = [
                *[(data, "map") for data in self.plot_data.get("maps", [])],
                *[(group, "line_grouped") for group in line_groups]
            ]

            for idx, (data, kind) in enumerate(all_plots):
                fig, ax = plt.subplots()
                if kind == "map":
                    ax.plot(data["x"], data["y"], label=data.get("label", ""))
                    ax.legend()
                elif kind == "line_grouped":
                    fig, ax = plt.subplots()
                    for line in data:
                        ax.plot(line["x"], line["y"], label=line["label"])
                    ax.set_title(data[0]["title"])
                    ax.set_xlabel(data[0]["xlabel"])
                    ax.set_ylabel(data[0]["ylabel"])
                    ax.legend()
                fig.tight_layout()
                fig.savefig(os.path.join(directory, f"plot_{kind}_{idx}.png"))
                plt.close(fig)

            QMessageBox.information(self, self.information_message["title"], self.information_message["message"])


        except Exception as e:
            QMessageBox.critical(self, self.critical_message["title"], f"{self.critical_message['message']}:\n{str(e)}")


    def set_all_plots(self, figures):
        """
        Ustawia dane wykresów do wyświetlenia.

        Args:
            figures (dict): Dane wykresów.

        ---
        Sets plot data for displaying.

        Args:
            figures (dict): Plot data.
        """
        self.plot_data = figures

    def update_messages(self, translations):
        """
        Aktualizuje komunikaty ostrzeżeń, informacji i błędów.

        Args:
            translations (dict): Słownik z komunikatami z kluczami 'warning', 'info', 'critical'.

        ---
        Updates warning, information, and critical message texts.

        Args:
            translations (dict): Dictionary with keys 'warning', 'info', 'critical'.
        """
        self.warning_message = {
            "title": translations.get('warning_title', 'Warning'),
            "message": translations.get('warning_message', 'No plot data to save.')
        }
        self.information_message = {
            "title": translations.get('information_title', 'Information'),
            "message": translations.get('information_message', 'All plots saved successfully.')
        }
        self.critical_message = {
            "title": translations.get('critical_title', 'Critical Error'),
            "message": translations.get('critical_message', 'Error saving all plots')
        }
        self.fullscreen_title = translations.get('fullscreen_title', "Chart Fullscreen Preview")

    def show_warning(self):
        """
        Wyświetla okno dialogowe z ostrzeżeniem.

        Displays a warning message box.

        Args:
            None

        Returns:
            None
        """
        QMessageBox.warning(
            self,
            "Warning",
            self.warning_message
        )

    def show_information(self):
        """
        Wyświetla okno dialogowe z informacją.

        Displays an information message box.

        Args:
            None

        Returns:
            None
        """
        QMessageBox.information(
            self,
            "Information",
            self.information_message
        )

    def show_critical(self):
        """
        Wyświetla okno dialogowe z krytycznym błędem.

        Displays a critical error message box.

        Args:
            None

        Returns:
            None
        """
        QMessageBox.critical(
            self,
            "Critical Error",
            self.critical_message
        )

    def open_current_plot_fullscreen(self):
        """
        Pokazuje aktualny wykres w trybie pełnoekranowym w nowym oknie.

        ---
        Shows the current plot in fullscreen mode in a new window.
        """
        if not hasattr(self, "plot_data") or not self.plot_data:
            QMessageBox.warning(self, "Brak danych", "Brak danych wykresów do zapisu.")
            return

        # 1) Utwórz nowe pełnoekranowe okno
        w = QMainWindow(self.orig_parent)
        w.setWindowTitle(self.fullscreen_title)
        w.showFullScreen()

        # 2) Stwórz nowy PlotCanvas w tym oknie
        full_canvas = PlotCanvas(parent=w)
        full_canvas.plot_data = self.plot_data.copy()  # lub deepcopy jeśli trzeba
        full_canvas.current_plot_type = self.current_plot_type
        full_canvas.current_plot_index = self.current_plot_index

        # 3) Wywołaj odpowiednią metodę rysującą
        if full_canvas.current_plot_type == "map":
            full_canvas.show_map_plot(full_canvas.plot_data["maps"])
        else:
            full_canvas.show_line_plot(full_canvas.plot_data["lines"])

        # 4) Włóż go do okna
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.addWidget(full_canvas)
        w.setCentralWidget(container)

        # 5) Obsługa Esc
        def on_key(event):
            if event.key()  == 16777216:
                w.close()
        w.keyPressEvent = on_key

        w.show()

class CustomTitleBar(QWidget):
    """
    Klasa CustomTitleBar implementuje niestandardowy pasek tytułu okna z przyciskami
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
    """
    theme_changed = pyqtSignal(str)  # Sygnał do zmiany motywu
    info_clicked = pyqtSignal()
    def __init__(self, parent):
        super().__init__(parent)
        self.setAutoFillBackground(True)
        self.initial_pos = None
        title_bar_layout = QHBoxLayout(self)
        title_bar_layout.setContentsMargins(5, 0, 5, 0)
        title_bar_layout.setSpacing(2)

        self.title = QLabel(f"{self.__class__.__name__}", self)
        self.title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        if title := parent.windowTitle():
            self.title.setText(title)
        title_bar_layout.addWidget(self.title)

        self.info_button = QPushButton()
        self.info_button.setIcon(QIcon(resource_path('resources/images/info_light.png')))
        self.info_button.setIconSize(QSize(32, 32))
        self.info_button.setStyleSheet("border: none;")
        self.info_button.clicked.connect(self.info_clicked.emit)

        # Theme switch button
        self.theme_switch_btn = QToolButton(self)
        self.theme_switch_btn.setIcon(QIcon(resource_path('resources/images/light_ui.png')))
        self.theme_switch_btn.clicked.connect(self.toggle_theme)

        # ENG button
        self.english_btn = QToolButton(self)
        self.english_btn.setIcon(QIcon(resource_path('resources/images/england.png')))
        self.english_btn.clicked.connect(lambda: self.window().update_language("English"))

        # PL button
        self.polish_btn = QToolButton(self)
        self.polish_btn.setIcon(QIcon(resource_path('resources/images/poland.png')))
        self.polish_btn.clicked.connect(lambda: self.window().update_language("Polski"))

        # Min button
        self.minimize_btn = QToolButton(self)
        self.minimize_btn.setIcon(QIcon(resource_path('resources/images/minimize.png')))
        self.minimize_btn.clicked.connect(self.window().showMinimized)

        # Max button
        self.maximize_btn = QToolButton(self)
        self.maximize_btn.setIcon(QIcon(resource_path('resources/images/maximize.png')))
        self.maximize_btn.clicked.connect(self.window().showMaximized)

        # Close button
        self.close_btn = QToolButton(self)
        self.close_btn.setIcon(QIcon(resource_path('resources/images/close.png')))
        self.close_btn.clicked.connect(self.window().close)

        # Normal button
        self.normal_button = QToolButton(self)
        self.normal_button.setIcon(QIcon(resource_path('resources/images/normal.png')))
        self.normal_button.clicked.connect(self.window().showNormal)
        self.normal_button.setVisible(False)

        # Add buttons
        buttons = [
            self.info_button,
            self.theme_switch_btn,
            self.polish_btn,
            self.english_btn,
            self.minimize_btn,
            self.normal_button,
            self.maximize_btn,
            self.close_btn,
        ]
        for button in buttons:
            button.setFocusPolicy(Qt.FocusPolicy.NoFocus)
            button.setFixedSize(QSize(30, 30))
            button.setIconSize(QSize(30, 30))
            button.setStyleSheet("border: none; background-color: transparent; border-radius: 15px;")
            title_bar_layout.addWidget(button)



    def mouseDoubleClickEvent(self, event):
        """
        Obsługuje zdarzenie podwójnego kliknięcia myszy na oknie.
        Jeśli okno jest zmaksymalizowane, przywraca je do normalnego rozmiaru,
        w przeciwnym razie maksymalizuje okno.

        Handles the mouse double-click event on the window.
        If the window is maximized, restores it to normal size,
        otherwise maximizes the window.

        Args:
            event (QMouseEvent): Zdarzenie podwójnego kliknięcia myszy / Mouse double-click event.

        Returns:
            None
        """
        win = self.window()
        if win.isMaximized():
            win.showNormal()
        else:
            win.showMaximized()
        event.accept()

    def toggle_theme(self):
        """
        Przełącza motyw aplikacji między jasnym a ciemnym.
        Aktualizuje ikonę przycisku i styl tytułu w zależności od motywu.

        Toggles the application theme between light and dark.
        Updates the button icon and title style according to the theme.

        Args:
            None

        Returns:
            None
        """
        pal = QApplication.palette()
        bg = pal.color(QPalette.ColorRole.Window).name()

        # Check the current theme and switch
        if pal.color(QPalette.ColorRole.Window).lightness() > 127:
            self.theme_changed.emit('dark')
            self.theme_switch_btn.setIcon(QIcon(resource_path('resources/images/dark_ui.png')))
            self.title.setStyleSheet(
                f"""font-weight: bold;
                   border: 2px solid {bg};
                   border-radius: 12px;
                   margin: 2px;
                   color: {bg};
                   background-color: transparent;
                """
            )
            self.setStyleSheet("background-color: #336699;")
            self.info_button.setIcon(QIcon(resource_path('resources/images/info_dark.png')))


        else:
            self.theme_changed.emit('light')
            self.theme_switch_btn.setIcon(QIcon(resource_path('resources/images/light_ui.png')))
            self.title.setStyleSheet(
                f"""font-weight: bold;
                   border: 2px solid {bg};
                   border-radius: 12px;
                   margin: 2px;
                   color: {bg};
                   background-color: transparent;
                """
            )
            self.info_button.setIcon(QIcon(resource_path('resources/images/info_light.png')))

    def window_state_changed(self, state):
        """
        Aktualizuje widoczność przycisków maksymalizacji i przywrócenia
        w zależności od aktualnego stanu okna.

        Updates the visibility of maximize and restore buttons
        depending on the current window state.

        Args:
            state (Qt.WindowState): Aktualny stan okna / Current window state.

        Returns:
            None
        """
        if state == Qt.WindowState.WindowMaximized:
            self.normal_button.setVisible(True)
            self.maximize_btn.setVisible(False)
        else:
            self.normal_button.setVisible(False)
            self.maximize_btn.setVisible(True)


class MainWindow(QMainWindow):
    """
    Główne okno aplikacji LaserDeMag.

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
    """

    def __init__(self):
        super().__init__()
        self.setWindowTitle("LaserDeMag App")
        self.resize(1200, 900)
        #with open("../resources/translations/translations.json", "r", encoding="utf-8") as f:
        #    self.translations = json.load(f)
        with open(resource_path('resources/translations/translations.json'),"r", encoding="utf-8") as f:
            self.translations = json.load(f)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.initial_pos = None

        # Central widget and main layout
        central_widget = QWidget()
        main_layout = QHBoxLayout()  # Use HBox layout to arrange the form and plot side by side

        self.title_bar = CustomTitleBar(self)
        self.title_bar.info_clicked.connect(self.show_info_message)
        self.title_bar.setFixedHeight(40)  # Set a fixed height for the title bar
        # Control panel for form fields
        control_panel = QVBoxLayout()
        self.widgets = {}

        # Title and description for the form
        header_layout = QHBoxLayout()
        self.logo_label = QLabel()
        self.logo_pixmap = QPixmap(resource_path('resources/images/logo_light.png')).scaled(90, 90, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        self.logo_label.setPixmap(self.logo_pixmap)
        #title_label = QLabel("LaserDeMag")
        self.widgets['title'] = QLabel("LaserDeMag")
        self.widgets['title'].setFont(QFont("Arial", 16, QFont.Weight.Bold))

        # Dodanie elementów do headera
        header_layout.addWidget(self.logo_label)
        header_layout.addSpacing(10)
        header_layout.addWidget(self.widgets['title'])
        header_layout.setAlignment(self.widgets['title'], Qt.AlignmentFlag.AlignVCenter)
        header_layout.addStretch()

        # Opis
        self.widgets['description'] = QLabel("This is a simulation application.")
        self.widgets['description'].adjustSize()
        self.widgets['description'].setWordWrap(True)
        self.widgets['description'].setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Maximum)
        self.widgets['description'].setStyleSheet("color: gray; font-size: 12px; margin-top: -5px;")

        # --- Dodanie do panelu ---
        control_panel.addLayout(header_layout)
        control_panel.addWidget(self.widgets['description'])

        # Material Box
        material_box = QGroupBox("Material")
        material_layout = QGridLayout()
        self.material_type = QComboBox()
        material_layout.addWidget(QLabel("Select Material Type:"), 0, 0)
        material_layout.addWidget(self.material_type, 0, 1)
        self.widgets['material_label'] = material_layout.itemAtPosition(0, 0).widget()

        self.init_temp = QLineEdit()
        material_layout.addWidget(QLabel("Initial Temperature:"), 1, 0)
        material_layout.addWidget(self.init_temp, 1, 1)
        self.widgets['init_temp_label'] = material_layout.itemAtPosition(1, 0).widget()

        self.curie_temp = QLineEdit()
        material_layout.addWidget(QLabel("Curie Temperature:"), 2, 0)
        material_layout.addWidget(self.curie_temp, 2, 1)
        self.widgets['curie_temp_label'] = material_layout.itemAtPosition(2, 0).widget()

        self.mag_moment = QLineEdit()
        material_layout.addWidget(QLabel("Magnetic Moment:"), 3, 0)
        material_layout.addWidget(self.mag_moment, 3, 1)
        self.widgets['mag_moment_label'] = material_layout.itemAtPosition(3, 0).widget()
        material_box.setLayout(material_layout)

        # Laser Box
        laser_box = QGroupBox("Laser")
        laser_layout = QGridLayout()
        self.power = QLineEdit()
        laser_layout.addWidget(QLabel("Power (mJ/cm²):"), 0, 0)
        laser_layout.addWidget(self.power, 0, 1)
        self.widgets['power_label'] = laser_layout.itemAtPosition(0, 0).widget()

        self.duration = QLineEdit()
        laser_layout.addWidget(QLabel("Duration (fs):"), 1, 0)
        laser_layout.addWidget(self.duration, 1, 1)
        self.widgets['duration_label'] = laser_layout.itemAtPosition(1, 0).widget()

        self.wavelength = QLineEdit()
        laser_layout.addWidget(QLabel("Wavelength (nm):"), 2, 0)
        laser_layout.addWidget(self.wavelength, 2, 1)
        self.widgets['wavelength_label'] = laser_layout.itemAtPosition(2, 0).widget()
        laser_box.setLayout(laser_layout)

        # Others Box
        others_box = QGroupBox("Others")
        others_layout = QGridLayout()
        self.ges = QLineEdit()
        others_layout.addWidget(QLabel("Electron-spin constant:"), 0, 0)
        others_layout.addWidget(self.ges, 0, 1)
        self.widgets['ges_label'] = others_layout.itemAtPosition(0, 0).widget()

        self.asf = QLineEdit()
        others_layout.addWidget(QLabel("Spin-flip probability:"), 1, 0)
        others_layout.addWidget(self.asf, 1, 1)
        self.widgets['asf_label'] = others_layout.itemAtPosition(1, 0).widget()
        others_box.setLayout(others_layout)

        # Add to widgets dictionary for future reference
        self.widgets['material_box'] = material_box
        self.widgets['laser_box'] = laser_box
        self.widgets['others_box'] = others_box

        # Buttons for actions
        self.load_from_file_btn = QToolButton()
        self.load_from_file_btn.setIcon(QIcon(resource_path('resources/images/from_file_light.png')))
        self.widgets['clear_btn'] = QPushButton("Clear Fields")
        self.widgets['start_btn'] = QPushButton("Start Simulation")
        btn_layout = QHBoxLayout()
        btn_layout.addWidget(self.load_from_file_btn)
        btn_layout.addWidget(self.widgets['clear_btn'])
        btn_layout.addWidget(self.widgets['start_btn'])

        control_panel.addWidget(material_box)
        control_panel.addWidget(laser_box)
        control_panel.addWidget(others_box)
        control_panel.addLayout(btn_layout)

        # Plot Layout (on the right side of the form)
        self.plot_frame = QFrame()
        self.plot_frame.setFrameShape(QFrame.Shape.StyledPanel)
        plot_layout = QVBoxLayout(self.plot_frame)
        self.plot_canvas = PlotCanvas(self.plot_frame)
        plot_layout.addWidget(self.plot_canvas)


        right_widget = QWidget()
        right_layout = QVBoxLayout()
        buttons_panel = QVBoxLayout()
        switch_plot_layout = QVBoxLayout()
        self.up_arrow_btn = QToolButton()
        self.up_arrow_btn.setIcon(QIcon(resource_path('resources/images/up_light.png')))
        self.down_arrow_btn = QToolButton()
        self.down_arrow_btn.setIcon(QIcon(resource_path('resources/images/down_light.png')))
        switch_plot_layout.addWidget(self.up_arrow_btn)
        switch_plot_layout.addWidget(self.down_arrow_btn)

        # Sekcja z przyciskami do pobierania danych
        download_layout = QVBoxLayout()
        self.download_current_btn = QToolButton()
        self.download_current_btn.setIcon(QIcon(resource_path('resources/images/download_photo_light.png')))
        self.download_current_btn.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.download_current_btn.setFixedSize(QSize(30, 30))
        self.download_current_btn.setIconSize(QSize(30, 30))
        self.download_current_btn.setStyleSheet("border: none; background-color: transparent; border-radius: 15px;")
        self.download_all_btn = QToolButton()
        self.download_all_btn.setIcon(QIcon(resource_path('resources/images/download_all_light.png')))
        self.download_data_btn = QToolButton()
        self.download_data_btn.setIcon(QIcon(resource_path('resources/images/download_data_light.png')))
        self.zoom_btn = QToolButton()
        self.zoom_btn.setIcon(QIcon(resource_path('resources/images/maxGraph_light.png')))

        download_layout.addWidget(self.download_current_btn)
        download_layout.addWidget(self.download_all_btn)
        download_layout.addWidget(self.download_data_btn)
        download_layout.addWidget(self.zoom_btn)

        buttons_panel.addLayout(switch_plot_layout)
        buttons_panel.addItem(QSpacerItem(20, 20, QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Expanding))
        buttons_panel.addLayout(download_layout)
        right_layout.addLayout(buttons_panel)
        right_widget.setLayout(right_layout)

        control_panel_widget = QWidget()
        control_panel_widget.setLayout(control_panel)
        control_panel_widget.setFixedWidth(320)

        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.addWidget(control_panel_widget)  # Left side: control panel with form elements
        splitter.addWidget(self.plot_frame)  # Right side: plot area
        splitter.addWidget(right_widget)
        splitter.setStretchFactor(0, 1)  # Left part should not stretch
        splitter.setStretchFactor(1, 2)  # Right part (plot) should take more space
        splitter.setStretchFactor(2, 1)  # Right part (plot) should take more space

        main_layout.addWidget(splitter)
        central_widget.setLayout(main_layout)


        # Creating a main layout and adding the title bar at the top
        title_bar_layout = QVBoxLayout()
        title_bar_layout.addWidget(self.title_bar)  # Add the title bar
        title_bar_layout.addWidget(central_widget)  # Add

        # Set the main layout of the window
        main_container = QWidget()
        main_container.setLayout(title_bar_layout)
        self.setCentralWidget(main_container)

        self.title_bar.theme_changed.connect(self.change_theme)

        self.update_language("English")

        # Connect buttons to functions
        self.load_from_file_btn.clicked.connect(self.load_user_data)
        self.widgets['clear_btn'].clicked.connect(self.clear_fields)
        self.widgets['start_btn'].clicked.connect(self.start_simulation)

        self.up_arrow_btn.clicked.connect(self.switch_plot_up)
        self.down_arrow_btn.clicked.connect(self.switch_plot_down)
        self.download_current_btn.clicked.connect(self.download_current_plot)
        self.download_all_btn.clicked.connect(self.download_all_plots)
        self.download_data_btn.clicked.connect(self.download_data)
        self.zoom_btn.clicked.connect(self.zoom_plot)

    def show_info_message(self):
        """
        Wyświetla okno dialogowe z informacjami o aplikacji.
        Displays an information dialog about the application.

        Treść i tytuł pobierane są z tłumaczeń dla aktualnego języka.
        The content and title are loaded from translations for the current language.
        """
        t = self.translations[self.current_language]
        msg = QMessageBox(self)
        msg.setWindowTitle(t["info_title"])
        msg.setTextFormat(Qt.TextFormat.RichText)
        msg.setText(f"<div style='min-width: 600px; max-width: 800px; text-align: justify;'>{t['info_message']}</div>")
        msg.exec()

    def changeEvent(self, event):
        """
        Obsługuje zdarzenia zmiany stanu okna, np. maksymalizacji.
        Handles window state change events, e.g., maximization.

        Przekazuje zdarzenie do paska tytułu, aby zaktualizować przyciski.
        Forwards the event to the title bar to update buttons accordingly.
        """
        if event.type() == QEvent.Type.WindowStateChange:
            self.title_bar.window_state_changed(self.windowState())
        super().changeEvent(event)
        event.accept()

    def window_state_changed(self, state):
        """
        Aktualizuje widoczność przycisków maksymalizacji i przywracania okna
        w zależności od obecnego stanu okna (zmaksymalizowane/normalne).

        Updates the visibility of maximize and restore buttons depending on the window state (maximized/normal).
        """
        self.normal_button.setVisible(state == Qt.WindowState.WindowMaximized)
        self.maximize_btn.setVisible(state != Qt.WindowState.WindowMaximized)

    def mousePressEvent(self, event):
        """
        Obsługuje naciśnięcie przycisku myszy.

        Jeśli lewy przycisk i okno jest zmaksymalizowane, przywraca do rozmiaru normalnego
        i zapisuje pozycję kliknięcia, by umożliwić płynne przeciąganie.

        Handles mouse press events.

        If left button is pressed and window is maximized, restores to normal size
        and records click position to enable smooth dragging.
        """
        if event.button() == Qt.MouseButton.LeftButton:
            if self.isMaximized():
                global_pos = event.globalPosition().toPoint()
                self.showNormal()
                geo = self.geometry()
                click_x = global_pos.x() - geo.x()
                click_y = global_pos.y() - geo.y()
                self.initial_pos = QPoint(click_x, click_y)
            else:
                self.initial_pos = event.position().toPoint()

        super().mousePressEvent(event)
        event.accept()

    def mouseMoveEvent(self, event):
        """
        Obsługuje przesuwanie myszy podczas przeciągania okna.

        Przesuwa okno zgodnie z ruchem myszy, jeśli wcześniej zapisana została pozycja startowa.

        Handles mouse move events during window dragging.

        Moves the window according to mouse movement if initial click position was saved.
        """
        if self.initial_pos is not None:
            delta = event.position().toPoint() - self.initial_pos
            self.window().move(
                self.window().x() + delta.x(),
                self.window().y() + delta.y(),
            )
        super().mouseMoveEvent(event)
        event.accept()

    def mouseReleaseEvent(self, event):
        """
        Obsługuje zwolnienie przycisku myszy.

        Jeśli okno nie jest zmaksymalizowane, a jego górna krawędź dotyka górnej krawędzi ekranu,
        automatycznie maksymalizuje okno.

        Handles mouse release events.

        If the window is not maximized and its top edge touches the top of the screen,
        automatically maximizes the window.
        """
        super().mouseReleaseEvent(event)
        if not self.isMaximized() and self.y() <= 0:
            self.showMaximized()
        self.initial_pos = None
        event.accept()

    def clear_fields(self):
        """
        Czyści wszystkie pola formularza i resetuje wybór materiału.

        Czyści również obszar wykresu, jeśli istnieje.

        Clears all form fields and resets material selection.

        Also clears the plot area if it exists.
        """
        for field in [self.init_temp, self.curie_temp, self.mag_moment,
                      self.power, self.duration, self.wavelength,
                      self.ges, self.asf]:
            field.clear()
        self.material_type.setCurrentIndex(0)
        if hasattr(self, 'plot_canvas'):
            self.plot_canvas.clear()

    def update_language(self, lang):
        """
        Aktualizuje interfejs użytkownika na wybrany język.

        Ustawia teksty etykiet, tytuły grup, przycisków i komunikatów błędów
        na podstawie słownika tłumaczeń.

        Args:
            lang (str): Kod wybranego języka (np. "English", "Polski").

        Updates the user interface to the selected language.

        Sets label texts, group titles, buttons, and error messages
        based on the translation dictionary.

        Args:
            lang (str): Selected language code (e.g., "English", "Polski").
        """
        self.current_language = lang
        t = self.translations[lang]
        self.field_labels = {
            'init_temp_label': t['Initial temperature T0'],
            'curie_temp_label': t['Curie temperature TC'],
            'mag_moment_label': t['Magnetic moment μat'],
            'power_label': t['Power of impulse (mJ/cm²)'],
            'duration_label': t['Duration of the impulse (fs)'],
            'wavelength_label': t['Laser wavelength (nm)'],
            'ges_label': t['Electron-spin constant coupling ges'],
            'asf_label': t['Spin-flip probability asf'],
            'material_label': t['Type of material'],
        }
        self.widgets['title'].setText(t['LaserDeMag'])
        self.widgets['description'].setText(t['Description'])
        self.widgets['material_box'].setTitle(t['Material'])
        self.widgets['material_label'].setText(t['Type of material'])
        self.material_type.clear()
        self.material_type.addItems([t['Select the type'], "Fe", "Ni", "Co", "Gd"])
        self.widgets['init_temp_label'].setText(t['Initial temperature T0'])
        self.widgets['curie_temp_label'].setText(t['Curie temperature TC'])
        self.widgets['mag_moment_label'].setText(t['Magnetic moment μat'])
        self.widgets['laser_box'].setTitle(t['Laser'])
        self.widgets['power_label'].setText(t['Power of impulse (mJ/cm²)'])
        self.widgets['duration_label'].setText(t['Duration of the impulse (fs)'])
        self.widgets['wavelength_label'].setText(t['Laser wavelength (nm)'])
        self.widgets['others_box'].setTitle(t['Others'])
        self.widgets['ges_label'].setText(t['Electron-spin constant coupling ges'])
        self.widgets['asf_label'].setText(t['Spin-flip probability asf'])
        self.widgets['clear_btn'].setText(t['Clear fields'])
        self.widgets['start_btn'].setText(t['Start the simulation'])
        self.plot_canvas.update_messages(t)
        self.missing_fields_error = t['missing_fields_error']
        self.error_invalid_format = t['error_invalid_format']
        self.error_json_decode = t['error_json_decode']
        self.error_file_not_found = t['error_file_not_found']
        self.error_invalid_type= t['error_invalid_type']
        self.error_invalid_material= t['error_invalid_material']
        self.error_material_not_selected = t['error_material_not_selected']
        self.error_invalid_number = t['error_invalid_number']
        self.error_required_field = t['error_required_field']
        self.information_title = t['information_title']
        self.critical_title = t['critical_title']
        self.save_success_json = t['save_success_json']
        self.save_error_json = t['save_error_json']
        self.save_success_xml = t['save_success_xml']
        self.save_error_xml = t['save_error_xml']
        self.error_numerical_simulation = t['error_numerical_simulation']
        self.error_unknown_simulation = t['error_unknown_simulation']
        self.loading_message = t['loading_message']
        self.loading_title = t['loading_title']
        self.save_report_title = t['save_report_title']
        self.select_directory = t['select_directory']
        self.save_plot = t['save_plot']
        self.file_types = t['file_types']

    def change_theme(self, theme: str):
        """
        Zmienia motyw graficzny aplikacji na ciemny lub jasny.

        Args:
            theme (str): Nazwa motywu, np. 'dark' lub 'light'.

        Changes the application's graphical theme to dark or light.

        Args:
            theme (str): Theme name, e.g., 'dark' or 'light'.
        """
        if theme == 'dark':
            self.set_dark_ui()
        elif theme == 'light':
            self.set_light_ui()

    def set_dark_ui(self):
        """
        Ustawia ciemny motyw interfejsu użytkownika,
        zmieniając kolory tekstów, ikon oraz paletę kolorów aplikacji.

        Sets the dark UI theme by changing text colors, icons,
        and the application color palette.
        """
        self.widgets['material_box'].setStyleSheet("color: white;")
        self.widgets['laser_box'].setStyleSheet("color: white;")
        self.widgets['others_box'].setStyleSheet("color: white;")
        self.widgets['description'].setStyleSheet("color: white;")
        self.widgets['title'].setStyleSheet("color: white;")
        new_logo = QPixmap(resource_path('resources/images/logo_dark.png')).scaled(90, 90, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        self.logo_label.setPixmap(new_logo)
        self.download_current_btn.setIcon(QIcon(resource_path('resources/images/download_photo_dark.png')))
        self.download_data_btn.setIcon(QIcon(resource_path('resources/images/download_data_dark.png')))
        self.zoom_btn.setIcon(QIcon(resource_path('resources/images/maxGraph_dark.png')))
        self.down_arrow_btn.setIcon(QIcon(resource_path('resources/images/down_dark.png')))
        self.up_arrow_btn.setIcon(QIcon(resource_path('resources/images/up_dark.png')))
        self.download_all_btn.setIcon(QIcon(resource_path('resources/images/download_all_dark.png')))
        self.load_from_file_btn.setIcon(QIcon(resource_path('resources/images/from_file_dark.png')))
        self.image_path = resource_path('resources/images/loading_dark.png')

        for le in self.centralWidget().findChildren(QLineEdit):
            le.setStyleSheet("""
                QLineEdit {
                    background-color: white;
                    color: black;
                    border: 1px solid gray;
                    border-radius: 4px;
                    padding: 2px 4px;
                }
            """)

        for cb in self.findChildren(QComboBox):
            cb.setStyleSheet("""
                        QComboBox {
                            background-color: #2a2a2a;
                            color: white;
                            border: 1px solid #555;
                        }
                        QComboBox QAbstractItemView {
                            background-color: #3a3a3a;
                            color: white;
                            selection-background-color: #555;
                            selection-color: black;
                        }
                    """)
        QApplication.instance().setStyleSheet("""
            QMessageBox {
                background-color: black;
                color: white;
            }
            QMessageBox QLabel {
                color: white;
                font-size: 14px;
            }
            QMessageBox QPushButton {
                min-width: 80px;
                padding: 5px;
                background-color: black;
                border:1px solid white;
            }
        """)

        for button in self.findChildren(QToolButton):
            button.setFocusPolicy(Qt.FocusPolicy.NoFocus)
            button.setFixedSize(QSize(30, 30))
            button.setIconSize(QSize(30, 30))
            button.setStyleSheet("""
                       border: none;
                       background-color: transparent;
                       border-radius: 15px;
        """)

        # Buttons
        self.widgets['clear_btn'].setStyleSheet("background-color: #444; color: white; border-radius: 5px;")
        self.widgets['start_btn'].setStyleSheet("background-color: #444; color: white; border-radius: 5px;")

        dark_palette = QPalette()

        dark_palette.setColor(QPalette.ColorRole.Window, QColor(53, 53, 53))
        dark_palette.setColor(QPalette.ColorRole.WindowText, QColor(255, 255, 255))
        dark_palette.setColor(QPalette.ColorRole.Base, QColor(42, 42, 42))
        dark_palette.setColor(QPalette.ColorRole.AlternateBase, QColor(66, 66, 66))
        dark_palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(255, 255, 255))
        dark_palette.setColor(QPalette.ColorRole.ToolTipText, QColor(255, 255, 255))
        dark_palette.setColor(QPalette.ColorRole.Text, QColor(255, 255, 255))
        dark_palette.setColor(QPalette.ColorRole.Button, QColor(53, 53, 53))
        dark_palette.setColor(QPalette.ColorRole.ButtonText, QColor(255, 255, 255))
        dark_palette.setColor(QPalette.ColorRole.BrightText, QColor(255, 0, 0))

        QApplication.setPalette(dark_palette)

    def set_light_ui(self):
        """
        Ustawia jasny motyw interfejsu użytkownika,
        zmieniając kolory tekstów, ikon oraz paletę kolorów aplikacji.

        Sets the light UI theme by changing text colors, icons,
        and the application color palette.
        """
        self.widgets['material_box'].setStyleSheet("color: black;")
        self.widgets['laser_box'].setStyleSheet("color: black;")
        self.widgets['others_box'].setStyleSheet("color: black;")
        self.widgets['description'].setStyleSheet("color: black;")
        self.widgets['title'].setStyleSheet("color: black;")
        new_logo = QPixmap(resource_path('resources/images/logo_light.png')).scaled(90, 90, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        self.logo_label.setPixmap(new_logo)
        self.download_current_btn.setIcon(QIcon(resource_path('resources/images/download_photo_light.png')))
        self.download_data_btn.setIcon(QIcon(resource_path('resources/images/download_data_light.png')))
        self.zoom_btn.setIcon(QIcon(resource_path('resources/images/maxGraph_light.png')))
        self.down_arrow_btn.setIcon(QIcon(resource_path('resources/images/down_light.png')))
        self.up_arrow_btn.setIcon(QIcon(resource_path('resources/images/up_light.png')))
        self.download_all_btn.setIcon(QIcon(resource_path('resources/images/download_all_light.png')))
        self.load_from_file_btn.setIcon(QIcon(resource_path('resources/images/from_file_light.png')))
        self.image_path = resource_path('resources/images/loading_light.png')

        self.widgets['clear_btn'].setStyleSheet("background-color: #ddd; color: black; border-radius: 5px;")
        self.widgets['start_btn'].setStyleSheet("background-color: #ddd; color: black; border-radius: 5px;")

        for cb in self.findChildren(QComboBox):
            cb.setStyleSheet("""
                        QComboBox {
                            background-color: white;
                            color: black;
                            border: 1px solid gray;
                        }
                        QComboBox QAbstractItemView {
                            background-color: white;
                            color: black;
                            selection-background-color: #cce;
                            selection-color: black;
                        }
                    """)
        QApplication.instance().setStyleSheet("""
            QMessageBox {
                background-color: white;
                color: black;
            }
            QMessageBox QLabel {
                color: black;
                font-size: 14px;
            }
            QMessageBox QPushButton {
                min-width: 80px;
                padding: 5px;
            }
        """)

        for button in self.findChildren(QToolButton):
            button.setFocusPolicy(Qt.FocusPolicy.NoFocus)
            button.setFixedSize(QSize(30, 30))
            button.setIconSize(QSize(30, 30))
            button.setStyleSheet("""
                       border: none;
                       background-color: transparent;
                       border-radius: 15px;
        """)

        light_palette = QPalette()

        light_palette.setColor(QPalette.ColorRole.Window, QColor(240, 240, 240))
        light_palette.setColor(QPalette.ColorRole.WindowText, QColor(0, 0, 0))
        light_palette.setColor(QPalette.ColorRole.Base, QColor(255, 255, 255))
        light_palette.setColor(QPalette.ColorRole.AlternateBase, QColor(220, 220, 220))
        light_palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(255, 255, 255))
        light_palette.setColor(QPalette.ColorRole.ToolTipText, QColor(0, 0, 0))
        light_palette.setColor(QPalette.ColorRole.Text, QColor(0, 0, 0))
        light_palette.setColor(QPalette.ColorRole.Button, QColor(240, 240, 240))
        light_palette.setColor(QPalette.ColorRole.ButtonText, QColor(0, 0, 0))
        light_palette.setColor(QPalette.ColorRole.BrightText, QColor(255, 0, 0))

        QApplication.setPalette(light_palette)

    def get_params_from_form(self):
        """
        Pobiera i waliduje parametry z formularza GUI.

        Retrieves and validates parameters from the GUI form.
        """
        try:
            material = self.material_type.currentText().strip()
            if self.material_type.currentIndex() == 0:
                raise ValueError(self.error_material_not_selected)

            def validate_float(value_str, field_key):
                field_label = self.field_labels.get(field_key, field_key)
                if not value_str.strip():
                    raise ValueError(self.error_required_field.format(field=field_label))
                try:
                    val = float(value_str)
                except ValueError:
                    raise ValueError(self.error_invalid_number.format(field=field_label))
                if val <= 0:
                    raise ValueError(self.error_invalid_number.format(field=field_label))
                return val

            # Walidacja pól liczbowych
            T0 = validate_float(self.init_temp.text(), "init_temp_label")
            Tc = validate_float(self.curie_temp.text(), "curie_temp_label")
            mu = validate_float(self.mag_moment.text(), "mag_moment_label")
            fluence = validate_float(self.power.text(), "power_label")
            pulse_duration = validate_float(self.duration.text(), "duration_label") / 1000  # fs → ps
            laser_wavelength = validate_float(self.wavelength.text(), "wavelength_label")
            ge = validate_float(self.ges.text(), "ges_label")
            asf = validate_float(self.asf.text(), "asf_label")

            return {
                'material': material,
                'T0': T0,
                'Tc': Tc,
                'mu': mu,
                'fluence': fluence,
                'pulse_duration': pulse_duration,
                'laser_wavelength': laser_wavelength,
                'ge': ge,
                'asf': asf
            }

        except ValueError as e:
            QMessageBox.critical(self, self.critical_title, str(e))
            return None

    def start_simulation(self):
        """
        Uruchamia symulację na podstawie parametrów z formularza,
        pokazuje dialog ładowania i obsługuje wyniki oraz błędy.

        Starts the simulation based on form parameters,
        shows loading dialog, and handles results and errors.
        """
        self.current_plot_index = 0
        params = self.get_params_from_form()
        if params is None:
            return

        self.loading_dialog = LoadingDialog(self.loading_title, self.loading_message, self.image_path)
        self.loading_dialog.show()
        QApplication.processEvents()

        try:
            start_time = time.time()
            material_obj, prop = get_material_properties(
                params['material'], params['Tc'], params['mu'], params['ge']
            )
            self.material_props = prop
            self.material_name = material_obj.name

            self.plot_data = main(params)
            self.plot_canvas.set_all_plots(self.plot_data)
            self.update_plot()

            duration = time.time() - start_time

            save_simulation_report(params, self.material_name, self.material_props, self.plot_data, self, simulation_duration=duration)

        except FloatingPointError as e:
            QMessageBox.critical(self, self.critical_title,
                                 self.translations[self.current_language]['error_numeric'] + "\n" + str(e))
        except Exception as e:
            QMessageBox.critical(self, self.critical_title,
                                 self.translations[self.current_language]['error_unknown_simulation'] + "\n" + str(e))
        finally:
            self.loading_dialog.close()
    def on_simulation_finished(self, result):
        """
        Obsługuje zakończenie symulacji, aktualizuje wykres i zamyka dialog ładowania.

        Handles simulation finish, updates plot, and closes loading dialog.
        """
        self.plot_data = result
        self.plot_canvas.set_all_plots(self.plot_data)
        self.update_plot()
        self.loading_dialog.close()

    def on_simulation_error(self, e):
        """
        Obsługuje błędy symulacji, zamyka dialog ładowania i wyświetla komunikat krytyczny.

        Handles simulation errors, closes loading dialog, and shows critical message.
        """
        self.loading_dialog.close()
        QMessageBox.critical(self, self.critical_title, str(e))

    def update_plot(self):
        """
        Aktualizuje wykres w GUI w zależności od aktualnego indeksu wykresu.

        Updates the GUI plot depending on the current plot index.
        """
        self.plot_canvas.current_plot_index = self.current_plot_index
        if self.current_plot_index == 0:
            self.plot_canvas.show_map_plot(self.plot_data["maps"])
        else:
            self.plot_canvas.show_line_plot(self.plot_data["lines"])

    def switch_plot_up(self):
        """
        Przełącza wykres na następny typ i aktualizuje wyświetlenie.

        Switches plot to the next type and updates display.
        """
        self.current_plot_index = (self.current_plot_index + 1) % 2
        self.update_plot()

    def switch_plot_down(self):
        """
        Przełącza wykres na poprzedni typ i aktualizuje wyświetlenie.

        Switches plot to the previous type and updates display.
        """
        self.current_plot_index = (self.current_plot_index - 1) % 2
        self.update_plot()

    def download_current_plot(self):
        """
        Otwiera dialog zapisu i zapisuje aktualnie wyświetlany wykres do pliku.

        Opens save dialog and saves the currently displayed plot to a file.
        """
        t = self.translations[self.current_language]
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            t['save_plot'],
            "",
            t['file_types'],
            options=QFileDialog.Option.DontUseNativeDialog
        )
        if file_path:
            self.plot_canvas.save_current_plot(file_path)

    def download_all_plots(self):
        """
        Otwiera dialog wyboru folderu i zapisuje wszystkie wykresy do wybranego katalogu.

        Opens directory selection dialog and saves all plots to the chosen folder.
        """
        t = self.translations[self.current_language]
        directory = QFileDialog.getExistingDirectory(
            self,
            t['select_directory'],
            options=QFileDialog.Option.ShowDirsOnly | QFileDialog.Option.DontUseNativeDialog
        )
        if directory:
            self.plot_canvas.save_all_plots(directory)

    def download_data(self):
        """
        Pyta użytkownika o format (JSON lub XML), następnie zapisuje dane symulacji.

        Asks user for format (JSON or XML), then saves simulation data.
        """
        params = self.collect_simulation_parameters()
        t = self.translations[self.current_language]

        file_path, selected_filter = QFileDialog.getSaveFileName(
            self,
            t['save_dialog_title'],
            "",
            f"{t['save_filter_json']};;{t['save_filter_xml']}",
            options=QFileDialog.Option.DontUseNativeDialog
        )
        if not file_path:
            return

        def quantity_to_plain(obj):
            if hasattr(obj, 'magnitude') and hasattr(obj, 'units'):
                return f"{obj.magnitude} {obj.units}"
            if isinstance(obj, list):
                return [quantity_to_plain(x) for x in obj]
            if isinstance(obj, dict):
                return {k: quantity_to_plain(v) for k, v in obj.items()}
            return obj

        file_format = "json" if selected_filter.startswith("JSON") else "xml"

        try:
            saved_path = save_simulation_parameters(
                params=params,
                file_path=file_path,
                file_format=file_format,
                parameter_encoder=ParameterEncoder,
                quantity_to_plain_func=quantity_to_plain
            )
            success_msg = t['save_success_json'] if file_format == "json" else t['save_success_xml']
            QMessageBox.information(self, t['information_title'], success_msg.format(path=saved_path))

        except Exception as e:
            error_msg = t['save_error_json'] if file_format == "json" else t['save_error_xml']
            QMessageBox.critical(self, t['critical_title'], error_msg.format(err=str(e)))

    def zoom_plot(self):
        """
        Otwiera aktualny wykres w trybie pełnoekranowym.

        Opens the current plot in fullscreen mode.
        """
        self.plot_canvas.open_current_plot_fullscreen()

    def collect_simulation_parameters(self):
        """
        Zbiera wszystkie parametry symulacji, łącznie z danymi formularza i właściwościami materiału.

        Collects all simulation parameters, including form inputs and material properties.
        """
        params = {
            'user': self.get_params_from_form(),
            'material': {
                'name': getattr(self, 'material_name', None),
                **getattr(self, 'material_props', {})
            },
        }
        return params

    def load_user_data(self):
        """
        Otwiera dialog wyboru pliku i ładuje dane użytkownika z pliku JSON,
        następnie wypełnia formularz danymi.

        Opens file selection dialog and loads user data from a JSON file,
        then populates the form with the loaded data.
        """
        t = self.translations[self.current_language]

        file_path, _ = QFileDialog.getOpenFileName(
            self,
            t['open_dialog_title'],
            "",
            t['open_filter_json'],
            options=QFileDialog.Option.DontUseNativeDialog
        )
        if not file_path:
            return

        try:
            user_data = load_simulation_parameters(file_path,self)

            # Przekaż dane do formularza
            self.populate_user_form(user_data)

            QMessageBox.information(
                self,
                t['information_title'],
                t['load_success_json'].format(path=file_path)
            )
        except Exception as e:
            QMessageBox.critical(
                self,
                self.critical_title,
                str(e)
            )

    def populate_user_form(self, data: dict):
        """
        Wypełnia formularz GUI na podstawie danych z pliku.

        Fills the GUI form fields based on the loaded data.

        Args:
            data (dict): Dictionary with parameters to set in the form.
        """
        self.material_type.setCurrentText(data["material"])
        self.init_temp.setText(str(data["T0"]))
        self.curie_temp.setText(str(data["Tc"]))
        self.mag_moment.setText(str(data["mu"]))
        self.power.setText(str(data["fluence"]))
        self.duration.setText(str(data["pulse_duration"] / 1000))  # fs → ps
        self.wavelength.setText(str(data["laser_wavelength"]))
        self.ges.setText(str(data["ge"]))
        self.asf.setText(str(data["asf"]))


if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.set_dark_ui()
    t = window.current_language
    window.update_language(t)
    window.title_bar.toggle_theme()
    window.show()
    app.exec()


