from datetime import datetime
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem, 
    QHBoxLayout, QPushButton, QDateEdit
    )
from PySide6.QtCore import Qt, QDate
from .SessionLogger import SessionLogger


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
        self.detailsTable = QTableWidget(0, 7)
        self.detailsTable.setHorizontalHeaderLabels(["Session Date", "Task", "Start Time", "End Time", "Duration", "Mode", "Tags"])
        self.layout.addWidget(self.detailsTable)


    def apply_filter(self):
        # Aquí después implementamos la carga de datos según fechas
        # print(f"Filtering from {self.fromDate.date().toString()} to {self.toDate.date().toString()}")
        # TODO: cargar sesiones desde SessionLogger y mostrarlas en la grilla
        fromDate = int(self.fromDate.date().toString('yyyyMMdd'))
        toDate = int(self.toDate.date().toString('yyyyMMdd'))

        logger = SessionLogger()
        sessions = logger.get_sessions_data(fromDate, toDate)

        self.detailsTable.setRowCount(0)

        for session in sessions:
            rowPosition = self.detailsTable.rowCount()
            self.detailsTable.insertRow(rowPosition)
            for column, value in enumerate(session):
                item = QTableWidgetItem(str(value))
                item.setFlags(item.flags() ^ Qt.ItemIsEditable)
                self.detailsTable.setItem(rowPosition, column, item)