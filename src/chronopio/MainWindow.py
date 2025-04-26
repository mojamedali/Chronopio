from PySide6.QtWidgets import QMainWindow, QTabWidget
from .Chronopio import Chronopio
from .DetailsView import DetailsView

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Chronopio")
        self.setMinimumSize(600, 400)

        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        self.init_tabs()

    def init_tabs(self):
        self.chronopio_widget = Chronopio()
        self.details_widget = DetailsView()

        self.tabs.addTab(self.chronopio_widget, "Main")
        self.tabs.addTab(self.details_widget, "Details")
