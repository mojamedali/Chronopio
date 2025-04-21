
import sys
from PySide6.QtWidgets import QApplication
from src.chronopio import Chronopio

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Chronopio()
    window.show()
    sys.exit(app.exec())
