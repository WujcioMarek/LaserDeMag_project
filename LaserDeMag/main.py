from PyQt6.QtWidgets import QApplication
#from LaserDeMag.ui.main_window import MainWindow
from PyQt6.QtCore import QTranslator, QLocale
import sys

def main():
    app = QApplication(sys.argv)

    # 🔁 Wczytaj tłumaczenie
    translator = QTranslator()
    if translator.load("resources/translations/pl.qm"):
        app.installTranslator(translator)
    else:
        print("❌ Nie udało się załadować tłumaczenia.")

    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
