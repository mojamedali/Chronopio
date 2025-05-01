from PySide6.QtWidgets import QMainWindow, QTabWidget, QSystemTrayIcon
from PySide6.QtCore import QEvent, Qt
from .Chronopio import Chronopio
from .DetailsView import DetailsView
from .SysTray import SysTray
from .ChartsView import ChartsView


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Chronopio")
        self.setMinimumSize(750, 500)

        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        self.init_tabs()
        self.init_tray()


    def changeEvent(self, event):
        if event.type() == QEvent.WindowStateChange:
            if self.isMinimized():
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

        super().changeEvent(event)


    def init_tabs(self):
        self.chronopioWidget = Chronopio()
        self.detailsWidget = DetailsView()
        self.ChartsWidget = ChartsView()

        self.tabs.addTab(self.chronopioWidget, "Main")
        self.tabs.addTab(self.detailsWidget, "Sessions Details")
        self.tabs.addTab(self.ChartsWidget, "Charts")

    
    def init_tray(self):
        self.sysTray = SysTray(self, self.chronopioWidget)


