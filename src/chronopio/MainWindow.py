from pathlib import Path
import qtawesome as qta
from PySide6.QtWidgets import QMainWindow, QTabWidget, QSystemTrayIcon, QMenu, QApplication
from PySide6.QtGui import QIcon, QAction
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
        self.init_tray()


    def closeEvent(self, event):
        event.ignore()
        self.hide()
        self.showHideAction.setText("Show window")
        self.trayIcon.showMessage(
            "Chronopio",
            "Chronopio es still running in the system tray.",
            QSystemTrayIcon.Information,
            2000
        )


    def init_tabs(self):
        self.chronopio_widget = Chronopio()
        self.details_widget = DetailsView()

        self.tabs.addTab(self.chronopio_widget, "Main")
        self.tabs.addTab(self.details_widget, "Sessions Details")

    
    def init_tray(self):
        self.trayIcon = QSystemTrayIcon(self)
        icon = qta.icon('fa5s.clock')
        self.trayIcon.setIcon(icon)

        trayMenu = QMenu()

        self.pauseAction = QAction("Pause")
        self.resetAction = QAction("Reset")
        self.showHideAction = QAction("Hide window")
        self.exitAction = QAction("Exit")

        trayMenu.addAction(self.pauseAction)
        trayMenu.addAction(self.resetAction)
        trayMenu.addSeparator()
        trayMenu.addAction(self.showHideAction)
        trayMenu.addSeparator()
        trayMenu.addAction(self.exitAction)

        self.trayIcon.setContextMenu(trayMenu)

        self.pauseAction.triggered.connect(self.pause_clicked)
        self.resetAction.triggered.connect(self.reset_clicked)
        self.showHideAction.triggered.connect(self.toggle_visibility)
        self.exitAction.triggered.connect(self.exit_clicked)

        self.trayIcon.show()


    def pause_clicked(self):
        print("Paused")

    
    def reset_clicked(self):
        print("Reset")

    
    def toggle_visibility(self):
        if self.isVisible():
            self.hide()
            self.showHideAction.setText("Show window")
        else:
            self.show()
            self.showHideAction.setText("Hide window")

    
    def exit_clicked(self):
        QApplication.quit()

