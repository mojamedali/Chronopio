from datetime import datetime
import qtawesome as qta
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
    QLabel, QComboBox, QGroupBox, QDialog
    )
from PySide6.QtGui import QIcon
from PySide6.QtCore import QTime, QTimer, Qt
from . import sessionlogger as sl
from . import newtaskdialog


class Chronopio(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowIcon(QIcon.fromTheme("chronopio"))

        self.setWindowTitle("Chronopio")
        self.resize(400, 400)

        self.timerLayout = QVBoxLayout()
        self.setLayout(self.timerLayout)
        self.runLayout = QHBoxLayout()

        self.logger = sl.SessionLogger()        

        self.taskCombo = QComboBox()
        self.load_tasks(False)
        self.timerLayout.addWidget(self.taskCombo)
        self.taskCombo.currentIndexChanged.connect(self.handle_task_selection)

        self.controlsPanel = QGroupBox()
        self.controlsLayout = QVBoxLayout()
        self.controlsPanel.setLayout(self.controlsLayout)
        self.controlsPanel.setEnabled(False)
        self.timerLayout.addWidget(self.controlsPanel)        

        self.label = QLabel("00:00:00", self)
        self.label.setStyleSheet('font-size: 32px; text-align: center;')
        self.label.setAlignment(Qt.AlignCenter)
        self.controlsLayout.addWidget(self.label)

        self.controlsLayout.addLayout(self.runLayout)

        self.runButton = QPushButton(" Start", self)
        self.runButton.setIcon(qta.icon("mdi.play"))
        self.runButton.clicked.connect(self.toggle_run_timer)
        self.runLayout.addWidget(self.runButton)

        self.pomodoroButton = QPushButton("Pomodoro", self)
        self.pomodoroButton.setIcon(qta.icon("mdi.food-apple"))
        self.pomodoroButton.clicked.connect(self.toggle_pomodoro_timer)
        self.runLayout.addWidget(self.pomodoroButton)
        
        self.resetButton = QPushButton("Reset", self)
        self.resetButton.clicked.connect(self.reset_timer)
        self.resetButton.setIcon(qta.icon("mdi.recycle-variant"))
        self.resetButton.setEnabled(False)    
        self.controlsLayout.addWidget(self.resetButton)
    
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_time)

        self.time = QTime(0, 0, 0)
        self.running = False # General running
        self.standardTimer = False # Run standard timer Status
        self.pomodoro = False # Run Pomodoro Status

        self.session = sl.SessionData(
                taskid=0, 
                start_time="00:00:00",
                end_time="00:00:00",
                duration=0,
                mode="",
                sessiondate=0
            )


    def toggle_run_timer(self):
        if self.standardTimer:
            self.timer.stop()
            self.runButton.setText(" Continue")
            self.runButton.setIcon(qta.icon("mdi.play"))
            self.save_data()
        else: 
            self.session.start_time = datetime.now()
            self.session.mode = "Standard"
            self.session.sessiondate = int(self.session.start_time.strftime("%Y%m%d"))
            self.timer.start(1000) # Update every second
            self.runButton.setText(" Stop")
            self.runButton.setIcon(qta.icon("mdi.stop"))
            self.taskCombo.setEnabled(False)
        self.running = not self.running
        self.standardTimer = not self.standardTimer
        self.pomodoroButton.setVisible(False)
        self.reset_disability()

    def toggle_pomodoro_timer(self):
        if self.pomodoro:
            self.timer.stop()
            self.pomodoroButton.setText(" Continue")
            self.pomodoroButton.setIcon(qta.icon("mdi.food-apple"))
            self.save_data()
        else: 
            self.session.start_time = datetime.now()
            self.session.mode = "Pomodoro"
            self.session.sessiondate = int(self.session.start_time.strftime("%Y%m%d"))
            if self.time == QTime(0, 0, 0): 
                self.label.setText("00:25:00")
                self.time = QTime(0, 25, 0)
            self.timer.start(1000)
            self.pomodoroButton.setText(" Stop")
            self.pomodoroButton.setIcon(qta.icon("mdi.stop"))
            self.taskCombo.setEnabled(False)
        self.running = not self.running
        self.pomodoro = not self.pomodoro
        self.runButton.setVisible(False)
        self.reset_disability()

    def update_time(self):
        if self.pomodoro:
            self.time = self.time.addSecs(-1)
        else: 
            self.time = self.time.addSecs(1)
        self.label.setText(self.time.toString("hh:mm:ss"))

    def reset_timer(self):
        self.time.setHMS(0, 0, 0)
        self.label.setText("00:00:00")
        self.resetButton.setEnabled(False)
        self.pomodoroButton.setVisible(True)
        self.runButton.setVisible(True)
        self.load_tasks(False)
        self.taskCombo.setEnabled(True)

    def reset_disability(self):
        isEnable = (not self.running) and (self.time != QTime(0, 0, 0))
        self.resetButton.setEnabled(isEnable)

    def save_data(self):
        self.session.end_time = datetime.now()
        self.session.duration = int((self.session.end_time - self.session.start_time).total_seconds())
        self.logger.save_session(self.session)

    def load_tasks(self, parentTask=False):
        tasks = self.logger.get_tasks(parentTask)
        
        self.taskCombo.clear()

        self.taskCombo.addItem("Select task...", None)
        self.taskCombo.addItem(" + New Task", -1)

        for task in tasks:
            id, title = task
            self.taskCombo.addItem(title, id)


    def handle_task_selection(self):
        taskId = self.taskCombo.currentData()
        isValid = taskId is not None and taskId != -1
        self.controlsPanel.setEnabled(isValid)
        if isValid:
            self.session.taskid = taskId
        elif taskId == -1: 
            self.create_new_task()

    def create_new_task(self):
        existingTasks = self.logger.get_tasks(True)

        dialog = newtaskdialog.NewTaskDialog(self, existingTasks)
        if dialog.exec() == QDialog.Accepted:
            data = dialog.get_task_data()
            if not data['title']:
                return
            
            cursor = self.logger.conn.cursor()
            cursor.execute("""
                INSERT INTO tasks (title, parent, tags)
                VALUES (?, ?, ?)
            """, 
            (
                data['title'], data['parent'], data['tags']
            ))
            self.logger.conn.commit()

        self.load_tasks()
        






