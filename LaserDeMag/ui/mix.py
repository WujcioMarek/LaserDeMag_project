import json
from PyQt6.QtCore import QSize, Qt, QEvent, pyqtSignal, QPoint
from PyQt6.QtGui import QPalette, QIcon, QColor
from PyQt6.QtWidgets import (QApplication, QHBoxLayout, QLabel, QMainWindow, QToolButton, QVBoxLayout, QWidget,
QPushButton, QGroupBox, QGridLayout, QLineEdit, QComboBox, QFrame)
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure


class PlotCanvas(FigureCanvas):
    def __init__(self, parent=None):
        fig = Figure(figsize=(5, 4), dpi=100)
        self.axes = fig.add_subplot(111)
        super().__init__(fig)
        self.setParent(parent)
        self.plot_placeholder()

    def plot_placeholder(self):
        self.axes.clear()
        self.axes.set_title("Simulation Result")
        self.axes.set_xlabel("Delay (ps)")
        self.axes.set_ylabel("Value")
        self.axes.plot([], [])  # Placeholder empty plot
        self.draw()


class CustomTitleBar(QWidget):
    theme_changed = pyqtSignal(str)  # Sygnał do zmiany motywu
    def __init__(self, parent):
        super().__init__(parent)
        self.setAutoFillBackground(True)
        self.setBackgroundRole(QPalette.ColorRole.Highlight)
        self.initial_pos = None
        title_bar_layout = QHBoxLayout(self)
        title_bar_layout.setContentsMargins(5, 0, 5, 0)
        title_bar_layout.setSpacing(2)

        self.title = QLabel(f"{self.__class__.__name__}", self)
        self.title.setStyleSheet(
            """font-weight: bold;
               border: 2px solid black;
               border-radius: 12px;
               margin: 2px;
            """
        )
        self.title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        if title := parent.windowTitle():
            self.title.setText(title)
        title_bar_layout.addWidget(self.title)

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
        current_palette = QApplication.palette()

        # Check the current theme and switch
        if current_palette.color(QPalette.ColorRole.Window).lightness() > 127:
            self.theme_changed.emit('dark')  # Emitujemy sygnał zmiany na ciemny
            self.theme_switch_btn.setIcon(QIcon('../resources/images/dark_ui.png'))
            self.title.setStyleSheet(
                """font-weight: bold;
                   border: 2px solid white;
                   border-radius: 12px;
                   margin: 2px;
                """
            )
            self.setStyleSheet("background-color: #336699;")

        else:
            self.theme_changed.emit('light')  # Emitujemy sygnał zmiany na jasny
            self.theme_switch_btn.setIcon(QIcon('../resources/images/light_ui.png'))
            self.title.setStyleSheet(
                """font-weight: bold;
                   border: 2px solid black;
                   border-radius: 12px;
                   margin: 2px;
                """
            )

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
        self.setWindowTitle("Custom Title Bar")
        self.resize(1024, 768)
        with open("../resources/translations/translations.json", "r", encoding="utf-8") as f:
            self.translations = json.load(f)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)

        # Central widget and main layout
        central_widget = QWidget()
        main_layout = QHBoxLayout()  # Use HBox layout to arrange the form and plot side by side

        self.title_bar = CustomTitleBar(self)
        self.title_bar.setFixedHeight(40)  # Set a fixed height for the title bar
        # Control panel for form fields
        control_panel = QVBoxLayout()
        self.export_btn = QPushButton("Export Plot")
        self.switch_plot_btn = QPushButton("Switch Plot View")
        self.widgets = {}

        # Title and description for the form
        self.widgets['title'] = QLabel("LaserDeMag")
        self.widgets['description'] = QLabel("This is a simulation application.")
        control_panel.addWidget(self.widgets['title'])
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
        self.widgets['clear_btn'] = QPushButton("Clear Fields")
        self.widgets['start_btn'] = QPushButton("Start Simulation")
        btn_layout = QHBoxLayout()
        btn_layout.addWidget(self.widgets['clear_btn'])
        btn_layout.addWidget(self.widgets['start_btn'])

        control_panel.addWidget(material_box)
        control_panel.addWidget(laser_box)
        control_panel.addWidget(others_box)
        control_panel.addLayout(btn_layout)

        # Plot Layout (on the right side of the form)
        plot_frame = QFrame()
        plot_frame.setFrameShape(QFrame.Shape.StyledPanel)
        plot_layout = QVBoxLayout(plot_frame)
        self.canvas = PlotCanvas()
        plot_layout.addWidget(self.canvas)

        # Add the plot section to the main layout on the right
        main_layout.addLayout(control_panel, 1)  # The form goes on the left
        main_layout.addWidget(plot_frame, 4)  # The plot goes on the right

        # Set the central widget layout
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
        self.widgets['clear_btn'].clicked.connect(self.clear_fields)
        self.widgets['start_btn'].clicked.connect(self.run_simulation_placeholder)
        self.export_btn.clicked.connect(self.export_plot)
        self.switch_plot_btn.clicked.connect(self.switch_plot)

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

    def update_language(self, lang):
        t = self.translations[lang]
        self.export_btn.setText(t['Export Plot'])
        self.switch_plot_btn.setText(t['Switch Plot View'])
        self.widgets['title'].setText(t['LaserDeMag App'])
        self.widgets['description'].setText(t['Description'])
        self.widgets['material_box'].setTitle(t['Material'])
        self.widgets['material_label'].setText(t['Type of material'])
        self.material_type.clear()
        self.material_type.addItems([t['Select the type'], "Fe", "Ni", "Co"])
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

    def run_simulation_placeholder(self):
        pass

    def export_plot(self):
        pass

    def switch_plot(self):
        pass


if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.set_light_ui()
    window.show()
    app.exec()
