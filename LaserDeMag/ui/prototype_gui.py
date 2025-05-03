import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QComboBox, QVBoxLayout

class MyApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Test GUI")
        self.setGeometry(100, 100, 300, 200)

        layout = QVBoxLayout()

        self.label = QLabel("Wybierz materiał:")
        layout.addWidget(self.label)

        self.combo = QComboBox()
        self.combo.addItem("Choose material")  # Placeholder
        self.combo.model().item(0).setEnabled(False)  # Wyłączenie opcji
        self.combo.addItems(["CoNi", "Fe", "Ni"])
        layout.addWidget(self.combo)

        self.setLayout(layout)

app = QApplication(sys.argv)
window = MyApp()
window.show()
sys.exit(app.exec())