from datetime import datetime
import qtawesome as qta
from pathlib import Path
from enum import Enum
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
    QLabel, QComboBox, QGroupBox, QDialog
    )
from PySide6.QtMultimedia import QSoundEffect 
from PySide6.QtGui import QIcon
from PySide6.QtCore import QTime, QTimer, Qt, QUrl
from . import sessionlogger as sl
from . import newtaskdialog

DEFAULT_POMODORO_DURATION = QTime(0, 0, 15)  # o 0, 0, 20 for test

class TimerMode(Enum):
    NO_MODE     = 0
    STANDARD    = 1
    POMODORO    = 2
    TIMER       = 3


class Chronopio(QWidget):
    def __init__(self):
        super().__init__()

        self.set_window()  
        self.set_controls()
        self.set_timer()
        self.set_session() 
        self.load_tasks(False)


    def set_timer(self):
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_time)

        self.time = QTime(0, 0, 0)
        self.isRunning = False
        # self.standardTimer = False # Run standard timer Status
        # self.pomodoro = False # Run Pomodoro Status


    def set_window(self):
        self.setWindowIcon(QIcon.fromTheme("chronopio"))
        self.setWindowTitle("Chronopio")
        self.resize(400, 400)

    def set_controls(self):
        self.timerLayout = QVBoxLayout()
        self.setLayout(self.timerLayout)
        self.runLayout = QHBoxLayout()     

        self.taskCombo = QComboBox()
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
        self.pomodoroButton.clicked.connect(self.toggle_pomodoro_session)
        self.runLayout.addWidget(self.pomodoroButton)
        
        self.resetButton = QPushButton("Reset", self)
        self.resetButton.clicked.connect(self.reset_timer)
        self.resetButton.setIcon(qta.icon("mdi.recycle-variant"))
        self.resetButton.setEnabled(False)    
        self.controlsLayout.addWidget(self.resetButton)


    def set_session(self):
        self.timerMode = TimerMode.NO_MODE # Default value
        self.logger = sl.SessionLogger()
        self.session = sl.SessionData(
                taskid      = 0, 
                start_time  = "00:00:00",
                end_time    = "00:00:00",
                duration    = 0,
                mode        = "",
                sessiondate = 0
            )
        

    def toggle_run_timer(self):
        if self.timerMode.STANDARD:
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
        self.update_reset_button_state()

    def toggle_pomodoro_timer(self):
        if self.timerMode.POMODORO:
            self.timer.stop()
            self.pomodoroButton.setText(" Continue")
            self.pomodoroButton.setIcon(qta.icon("mdi.food-apple"))
            self.save_data()
            # if self.time == QTime(0, 0, 10):
            #    self.play_pomodoro_alarm()
        else: 
            self.session.start_time = datetime.now()
            self.session.mode = "Pomodoro"
            self.session.sessiondate = int(self.session.start_time.strftime("%Y%m%d"))
            if self.time == QTime(0, 0, 0): 
                self.time = DEFAULT_POMODORO_DURATION
            self.timer.start(1000)
            self.pomodoroButton.setText(" Stop")
            self.pomodoroButton.setIcon(qta.icon("mdi.stop"))
            self.taskCombo.setEnabled(False)
        self.isRunning = not self.isRunning
        self.pomodoro = not self.pomodoro
        self.runButton.setVisible(False)
        self.update_reset_button_state()
        

    def update_time(self):
        if self.timerMode == TimerMode.POMODORO:
            self.time = self.time.addSecs(-1)
            if self.time == QTime(0, 0, 11):
                self.play_pomodoro_alarm()                
            elif self.time == QTime(0, 0, 0):
                self.stop_timer()                
                self.time = QTime(0, 0, 0, 1) # Add 1ms to accomplish condition in update_reset_button_state
        else: 
            self.time = self.time.addSecs(1)
        self.label.setText(self.time.toString("hh:mm:ss"))

    def reset_timer(self):
        self.time.setHMS(0, 0, 0)
        self.label.setText("00:00:00")
        self.timerMode = TimerMode.NO_MODE
        self.resetButton.setEnabled(False)
        self.pomodoroButton.setVisible(True)
        self.runButton.setVisible(True)
        self.load_tasks(False)
        self.taskCombo.setEnabled(True)

    def update_reset_button_state(self):
        isEnable = (not self.isRunning) and (self.time != QTime(0, 0, 0))
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
        

    def play_pomodoro_alarm(self):
        self.alarmAudio = QSoundEffect()
        soundPath = Path(__file__).parent.parent.parent / 'assets' / 'sounds' / 'alarm.wav'

        self.alarmAudio.setSource(QUrl.fromLocalFile(str(soundPath.resolve())))
        self.alarmAudio.setVolume(.9)

        self.alarmAudio.play()

    
    def toggle_pomodoro_session(self):
        self.runButton.setVisible(False)
        if self.isRunning:
            self.stop_timer()
            self.pomodoroButton.setText(" Continue")
            self.pomodoroButton.setIcon(qta.icon("mdi.food-apple"))
        else:
            self.start_timer()
            self.timerMode = TimerMode.POMODORO            
            self.pomodoroButton.setText(" Stop")
            self.pomodoroButton.setIcon(qta.icon("mdi.stop"))            
        if self.time == QTime(0, 0, 0): 
            self.time = DEFAULT_POMODORO_DURATION

    
    def start_timer(self):
        self.isRunning = True
        self.session.start_time = datetime.now()
        self.session.mode = self.timerMode.name
        self.session.sessiondate = int(self.session.start_time.strftime("%Y%m%d"))
        self.timer.start(1000)
        self.taskCombo.setEnabled(False)


    def stop_timer(self):
        self.isRunning = False
        self.timer.stop()
        self.save_data()
        self.update_reset_button_state()








