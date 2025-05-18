import json, os, time
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

class LoadingDialog(QDialog):
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
    def default(self, obj):
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
        self.plot_data = {}
        self.fig.clf()
        self.draw()

    def show_map_plot(self, map_data):
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
        self.plot_data = figures

    def update_messages(self, translations):
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
        QMessageBox.warning(
            self,
            "Warning",
            self.warning_message
        )

    def show_information(self):
        QMessageBox.information(
            self,
            "Information",
            self.information_message
        )

    def show_critical(self):
        QMessageBox.critical(
            self,
            "Critical Error",
            self.critical_message
        )

    def open_current_plot_fullscreen(self):
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
        self.info_button.setIcon(QIcon("../resources/images/info_light.png"))  # Upewnij się, że masz plik info.png
        self.info_button.setIconSize(QSize(32, 32))
        self.info_button.setStyleSheet("border: none;")
        self.info_button.clicked.connect(self.info_clicked.emit)

        # Theme switch button
        self.theme_switch_btn = QToolButton(self)
        self.theme_switch_btn.setIcon(QIcon('../resources/images/light_ui.png'))
        self.theme_switch_btn.clicked.connect(self.toggle_theme)

        # ENG button
        self.english_btn = QToolButton(self)
        self.english_btn.setIcon(QIcon('../resources/images/england.png'))
        self.english_btn.clicked.connect(lambda: self.window().update_language("English"))

        # PL button
        self.polish_btn = QToolButton(self)
        self.polish_btn.setIcon(QIcon('../resources/images/poland.png'))
        self.polish_btn.clicked.connect(lambda: self.window().update_language("Polski"))

        # Min button
        self.minimize_btn = QToolButton(self)
        self.minimize_btn.setIcon(QIcon('../resources/images/minimize.png'))
        self.minimize_btn.clicked.connect(self.window().showMinimized)

        # Max button
        self.maximize_btn = QToolButton(self)
        self.maximize_btn.setIcon(QIcon('../resources/images/maximize.png'))
        self.maximize_btn.clicked.connect(self.window().showMaximized)

        # Close button
        self.close_btn = QToolButton(self)
        self.close_btn.setIcon(QIcon('../resources/images/close.png'))
        self.close_btn.clicked.connect(self.window().close)

        # Normal button
        self.normal_button = QToolButton(self)
        self.normal_button.setIcon(QIcon('../resources/images/normal.png'))
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
        win = self.window()
        if win.isMaximized():
            win.showNormal()
        else:
            win.showMaximized()
        event.accept()

    def toggle_theme(self):
        """Toggles between light and dark theme."""
        pal = QApplication.palette()
        bg = pal.color(QPalette.ColorRole.Window).name()

        # Check the current theme and switch
        if pal.color(QPalette.ColorRole.Window).lightness() > 127:
            self.theme_changed.emit('dark')
            self.theme_switch_btn.setIcon(QIcon('../resources/images/dark_ui.png'))
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
            self.info_button.setIcon(QIcon("../resources/images/info_dark.png"))


        else:
            self.theme_changed.emit('light')
            self.theme_switch_btn.setIcon(QIcon('../resources/images/light_ui.png'))
            self.title.setStyleSheet(
                f"""font-weight: bold;
                   border: 2px solid {bg};
                   border-radius: 12px;
                   margin: 2px;
                   color: {bg};
                   background-color: transparent;
                """
            )
            self.info_button.setIcon(QIcon("../resources/images/info_light.png"))

    def window_state_changed(self, state):
        if state == Qt.WindowState.WindowMaximized:
            self.normal_button.setVisible(True)
            self.maximize_btn.setVisible(False)
        else:
            self.normal_button.setVisible(False)
            self.maximize_btn.setVisible(True)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("LaserDeMag App")
        self.resize(1200, 900)
        with open("../resources/translations/translations.json", "r", encoding="utf-8") as f:
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
        self.logo_pixmap = QPixmap("../resources/images/logo_light.png").scaled(90, 90, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
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
        self.load_from_file_btn.setIcon(QIcon("../resources/images/from_file_light.png"))
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
        self.up_arrow_btn.setIcon(QIcon("../resources/images/up_light.png"))
        self.down_arrow_btn = QToolButton()
        self.down_arrow_btn.setIcon(QIcon("../resources/images/down_light.png"))
        switch_plot_layout.addWidget(self.up_arrow_btn)
        switch_plot_layout.addWidget(self.down_arrow_btn)

        # Sekcja z przyciskami do pobierania danych
        download_layout = QVBoxLayout()
        self.download_current_btn = QToolButton()
        self.download_current_btn.setIcon(QIcon("../resources/images/download_photo_light.png"))  # Ikona pobierania wykresu
        self.download_current_btn.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.download_current_btn.setFixedSize(QSize(30, 30))
        self.download_current_btn.setIconSize(QSize(30, 30))
        self.download_current_btn.setStyleSheet("border: none; background-color: transparent; border-radius: 15px;")
        self.download_all_btn = QToolButton()
        self.download_all_btn.setIcon(QIcon("../resources/images/download_all_light.png"))  # Ikona pobierania wszystkich wykresów
        self.download_data_btn = QToolButton()
        self.download_data_btn.setIcon(QIcon("../resources/images/download_data_light.png"))  # Ikona pobierania danych
        self.zoom_btn = QToolButton()
        self.zoom_btn.setIcon(QIcon("../resources/images/maxGraph_light.png"))  # Ikona powiększania wykresu

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
        t = self.translations[self.current_language]
        msg = QMessageBox(self)
        msg.setWindowTitle(t["info_title"])
        msg.setTextFormat(Qt.TextFormat.RichText)
        msg.setText(f"<div style='min-width: 600px; max-width: 800px; text-align: justify;'>{t['info_message']}</div>")
        msg.exec()

    def changeEvent(self, event):
        if event.type() == QEvent.Type.WindowStateChange:
            self.title_bar.window_state_changed(self.windowState())
        super().changeEvent(event)
        event.accept()

    def window_state_changed(self, state):
        self.normal_button.setVisible(state == Qt.WindowState.WindowMaximized)
        self.maximize_btn.setVisible(state != Qt.WindowState.WindowMaximized)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            # jeśli było zmaksymalizowane, to przywróć przed ruszeniem
            if self.isMaximized():
                # pamiętaj współrzędne kliknięcia względem całego ekranu
                global_pos = event.globalPosition().toPoint()
                # przywróć okno do stanu normalnego
                self.showNormal()
                # po przywróceniu oblicz nową initial_pos tak,
                # aby mysz „złapała” okno w tym samym punkcie
                geo = self.geometry()
                # np. ustaw initial_pos tak, żeby relatywna pozycja się zachowała
                click_x = global_pos.x() - geo.x()
                click_y = global_pos.y() - geo.y()
                self.initial_pos = QPoint(click_x, click_y)
            else:
                self.initial_pos = event.position().toPoint()

        super().mousePressEvent(event)
        event.accept()

    def mouseMoveEvent(self, event):
        if self.initial_pos is not None:
            delta = event.position().toPoint() - self.initial_pos
            self.window().move(
                self.window().x() + delta.x(),
                self.window().y() + delta.y(),
            )
        super().mouseMoveEvent(event)
        event.accept()

    def mouseReleaseEvent(self, event):
        super().mouseReleaseEvent(event)
        if not self.isMaximized() and self.y() <= 0:
            self.showMaximized()
        self.initial_pos = None
        event.accept()

    def clear_fields(self):
        for field in [self.init_temp, self.curie_temp, self.mag_moment,
                      self.power, self.duration, self.wavelength,
                      self.ges, self.asf]:
            field.clear()
        self.material_type.setCurrentIndex(0)
        if hasattr(self, 'plot_canvas'):
            self.plot_canvas.clear()

    def update_language(self, lang):
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

    def change_theme(self, theme: str):
        """Zmienia motyw na ciemny lub jasny na podstawie sygnału."""
        if theme == 'dark':
            self.set_dark_ui()
        elif theme == 'light':
            self.set_light_ui()

    def set_dark_ui(self):
        """Zmienia kolor widgetów w MainWindow na ciemny."""
        # Material Box Labels (example)
        self.widgets['material_box'].setStyleSheet("color: white;")
        self.widgets['laser_box'].setStyleSheet("color: white;")
        self.widgets['others_box'].setStyleSheet("color: white;")
        self.widgets['description'].setStyleSheet("color: white;")
        self.widgets['title'].setStyleSheet("color: white;")
        new_logo = QPixmap("../resources/images/logo_dark.png").scaled(90, 90, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        self.logo_label.setPixmap(new_logo)
        self.download_current_btn.setIcon(QIcon("../resources/images/download_photo_dark.png"))
        self.download_data_btn.setIcon(QIcon("../resources/images/download_data_dark.png"))
        self.zoom_btn.setIcon(QIcon("../resources/images/maxGraph_dark.png"))
        self.down_arrow_btn.setIcon(QIcon("../resources/images/down_dark.png"))
        self.up_arrow_btn.setIcon(QIcon("../resources/images/up_dark.png"))
        self.download_all_btn.setIcon(QIcon("../resources/images/download_all_dark.png"))
        self.load_from_file_btn.setIcon(QIcon("../resources/images/from_file_dark.png"))
        self.image_path = "../resources/images/loading_dark.png"

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
        """Zmienia kolor widgetów w MainWindow na jasny."""
        # Material Box Labels (example)
        self.widgets['material_box'].setStyleSheet("color: black;")
        self.widgets['laser_box'].setStyleSheet("color: black;")
        self.widgets['others_box'].setStyleSheet("color: black;")
        self.widgets['description'].setStyleSheet("color: black;")
        self.widgets['title'].setStyleSheet("color: black;")
        new_logo = QPixmap("../resources/images/logo_light.png").scaled(90, 90, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        self.logo_label.setPixmap(new_logo)
        self.download_current_btn.setIcon(QIcon("../resources/images/download_photo_light.png"))
        self.download_data_btn.setIcon(QIcon("../resources/images/download_data_light.png"))
        self.zoom_btn.setIcon(QIcon("../resources/images/maxGraph_light.png"))
        self.down_arrow_btn.setIcon(QIcon("../resources/images/down_light.png"))
        self.up_arrow_btn.setIcon(QIcon("../resources/images/up_light.png"))
        self.download_all_btn.setIcon(QIcon("../resources/images/download_all_light.png"))
        self.load_from_file_btn.setIcon(QIcon("../resources/images/from_file_light.png"))
        self.image_path = "../resources/images/loading_light.png"

        # Buttons
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
        try:
            material = self.material_type.currentText().strip()
            if self.material_type.currentIndex() == 0:
                raise ValueError(self.error_material_not_selected)

            def validate_float(value_str, field_key):
                field_label = self.field_labels.get(field_key, field_key)
                if not value_str.strip():
                    raise ValueError(self.error_required_field.format(field=field_label))
                try:
                    return float(value_str)
                except ValueError:
                    raise ValueError(self.error_invalid_number.format(field=field_label))

            # Sprawdzenie materiału
            if self.material_type.currentIndex() == 0:
                raise ValueError(self.error_material_not_selected)
            material = self.material_type.currentText()

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
        self.plot_data = result
        self.plot_canvas.set_all_plots(self.plot_data)
        self.update_plot()
        self.loading_dialog.close()

    def on_simulation_error(self, e):
        self.loading_dialog.close()
        QMessageBox.critical(self, self.critical_title, str(e))

    def update_plot(self):
        self.plot_canvas.current_plot_index = self.current_plot_index  # zapewnia spójność z GUI
        if self.current_plot_index == 0:
            self.plot_canvas.show_map_plot(self.plot_data["maps"])
        else:
            self.plot_canvas.show_line_plot(self.plot_data["lines"])

    def switch_plot_up(self):
        self.current_plot_index = (self.current_plot_index + 1) % 2
        self.update_plot()

    def switch_plot_down(self):
        self.current_plot_index = (self.current_plot_index - 1) % 2
        self.update_plot()

    def download_current_plot(self):
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Zapisz wykres",
            "",
            "Plik PNG (*.png);;Plik PDF (*.pdf);;Plik SVG (*.svg)",
            options=QFileDialog.Option.DontUseNativeDialog
        )
        if file_path:
            self.plot_canvas.save_current_plot(file_path)

    def download_all_plots(self):
        directory = QFileDialog.getExistingDirectory(
            self,
            "Wybierz folder do zapisania wszystkich wykresów",
            options=QFileDialog.Option.ShowDirsOnly | QFileDialog.Option.DontUseNativeDialog
        )
        if directory:
            self.plot_canvas.save_all_plots(directory)

    def download_data(self):
        """
        Ask user whether JSON or XML, then save.
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

        # Wybierz format
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
        self.plot_canvas.open_current_plot_fullscreen()

    def collect_simulation_parameters(self):
        """
        Returns a dict of all parameters:
        - form inputs
        - internal simulation settings (e.g. S, ud.Heat settings, units, etc.)
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

        Args:
            data (dict): Słownik z parametrami do ustawienia
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


