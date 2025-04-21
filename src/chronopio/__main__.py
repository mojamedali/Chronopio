def main():
    import sys
    from PySide6.QtWidgets import QApplication
    from .chronopio import Chronopio

    app = QApplication(sys.argv)
    window = Chronopio()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
