from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLineEdit, 
    QLabel, QComboBox, QPushButton
)
from PySide6.QtCore import Qt


class NewTaskDialog(QDialog):
    def __init__(self, parent=None, taskList=None):
        super().__init__(parent)

        self.setWindowTitle("New Task")
        self.setMinimumWidth(350)

        layout = QVBoxLayout()
        self.setLayout(layout)

        # Task tike input
        self.titleEdit = QLineEdit()
        self.titleEdit.textChanged.connect(self.validate)
        layout.addWidget(QLabel("Task title:"))
        layout.addWidget(self.titleEdit)

        # Parent task selector
        self.parentCombo = QComboBox()
        layout.addWidget(QLabel("Parent task:"))
        if taskList:
            self.parentCombo.addItem("None", 0)
            for task in taskList:
                self.parentCombo.addItem(task[1], task[0])
        layout.addWidget(self.parentCombo)

        # Tags input
        self.tagsEdit = QLineEdit()
        layout.addWidget(QLabel("Tags (comma-separated):"))
        layout.addWidget(self.tagsEdit)

        # Buttons
        buttonLayout = QHBoxLayout()
        self.okButton = QPushButton("OK")
        self.okButton.clicked.connect(self.accept)
        self.okButton.setEnabled(False)
        self.cancelButton = QPushButton("Cancel")
        self.cancelButton.clicked.connect(self.reject)
        buttonLayout.addWidget(self.okButton)
        buttonLayout.addWidget(self.cancelButton)

        layout.addLayout(buttonLayout)

    def get_task_data(self):
        return {
            "title": self.titleEdit.text().strip(),
            "parent": self.parentCombo.currentData(),
            "tags": self.tagsEdit.text().strip()
        }
    
    def validate(self):
        hasText = bool(self.titleEdit.text().strip())
        self.okButton.setEnabled(hasText)
