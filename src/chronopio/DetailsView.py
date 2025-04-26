from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QTableWidget, #QTableWidgetItem, 
    QHBoxLayout, QPushButton, QDateEdit
    )
from PySide6.QtCore import Qt, QDate


class DetailsView(QWidget):
    def __init__(self):
        super().__init__()

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.init_filters()
        self.init_table()
        

    def init_filters(self):
        filterLayout = QHBoxLayout()

        self.fromDate = QDateEdit()
        self.fromDate.setCalendarPopup(True)
        self.fromDate.setDate(QDate.currentDate().addDays(-1)) # Default yesterday

        self.toDate = QDateEdit()
        self.toDate.setCalendarPopup(True)
        self.toDate.setDate(QDate.currentDate())

        self.filterButton = QPushButton("Filter")
        self.filterButton.clicked.connect(self.apply_filter)

        filterLayout.addWidget(QLabel("From:"))
        filterLayout.addWidget(self.fromDate)
        filterLayout.addWidget(QLabel("To:"))
        filterLayout.addWidget(self.toDate)
        filterLayout.addWidget(self.filterButton)

        self.layout.addLayout(filterLayout)
        

    def init_table(self):
        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(["Task", "Start Time", "End Time", "Duration", "Mode"])
        self.layout.addWidget(self.table)


    def apply_filter(self):
        # Aquí después implementamos la carga de datos según fechas
        print(f"Filtering from {self.fromDate.date().toString()} to {self.toDate.date().toString()}")
        # TODO: cargar sesiones desde SessionLogger y mostrarlas en la grilla
