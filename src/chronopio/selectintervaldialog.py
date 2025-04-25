from PySide6.QtWidgets import QDialog, QVBoxLayout, QDialogButtonBox, QTimeEdit
from PySide6.QtCore import QTime, QTimer


class IntervalDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Select interval")
        self.resize(300, 100)

        self.timeEdit = QTimeEdit()
        self.timeEdit.setStyleSheet("font-size: 20px;")         
        self.timeEdit.setDisplayFormat("HH:mm:ss")
        self.timeEdit.setTime(QTime(0, 0, 0))

        QTimer.singleShot(0, lambda: self.timeEdit.setCurrentSection(QTimeEdit.MinuteSection))

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        layout = QVBoxLayout()
        layout.addWidget(self.timeEdit)
        layout.addWidget(buttons)
        self.setLayout(layout)

    def get_interval(self):
        return self.timeEdit.time()
    

