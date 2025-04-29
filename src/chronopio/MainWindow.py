from PySide6.QtWidgets import QMainWindow, QTabWidget, QSystemTrayIcon
from .Chronopio import Chronopio
from .DetailsView import DetailsView
from .SysTray import SysTray


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Chronopio")
        self.setMinimumSize(600, 400)

        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        self.init_tabs()
        self.init_tray()


    def closeEvent(self, event):
        event.ignore()
        self.hide()
        self.sysTray.show()
        self.sysTray.stopAction.setEnabled(self.chronopioWidget.isRunning)
        self.sysTray.show_message(
            "Chronopio",
            "Chronopio es still running in the system tray.",
            QSystemTrayIcon.Information,
            2000
        )


    def init_tabs(self):
        self.chronopioWidget = Chronopio()
        self.detailsWidget = DetailsView()

        self.tabs.addTab(self.chronopioWidget, "Main")
        self.tabs.addTab(self.detailsWidget, "Sessions Details")

    
    def init_tray(self):
        self.sysTray = SysTray(self, self.chronopioWidget)


