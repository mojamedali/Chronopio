from PySide6.QtWidgets import QSystemTrayIcon, QMenu
from PySide6.QtGui import QAction
import qtawesome as qta


class SysTray:
    def __init__(self, parent, chronopioWidget):
        self.parent = parent
        self.chronopioWidget = chronopioWidget
        self.trayIcon = QSystemTrayIcon(parent)
        self.icon = qta.icon('fa5s.clock')
        self.trayIcon.setIcon(self.icon)

        self.trayMenu = QMenu()
        self.setup_action()
        self.trayIcon.setContextMenu(self.trayMenu)

    
    def setup_action(self):
        self.stopAction = QAction("Stop", enabled=False)
        self.hideAction = QAction("Show window")
        self.exitAction = QAction("Exit")

        self.trayMenu.addAction(self.hideAction)
        self.trayMenu.addSeparator()
        self.trayMenu.addAction(self.exitAction)

        self.hideAction.triggered.connect(self.toggle_visibility)
        self.exitAction.triggered.connect(self.exit_clicked)

    
    def show_message(self, title, message, msgtype, ms):
        self.trayIcon.showMessage(title, message, msgtype, ms)


    def toggle_visibility(self):
        self.parent.showNormal()
        self.trayIcon.hide()


    def show(self):
        self.trayIcon.show()


    def exit_clicked(self):
        from PySide6.QtWidgets import QApplication
        QApplication.quit()
