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
from . import selectintervaldialog 


DEFAULT_POMODORO_DURATION = QTime(0, 25, 0, 0)


class TimerMode(Enum):
    NO_MODE     = (0, "No Mode")
    STANDARD    = (1, "Focus mode")
    POMODORO    = (2, "Pomodoro mode")
    TIMER       = (3, "Timer mode")

    def __init__ (self, nvalue, label):
        self._n_value = nvalue
        self._label = label

    @property
    def label(self):
        return self._label
    
    @property
    def num(self):
        return self._n_value


class Chronopio(QWidget):
    def __init__(self):
        super().__init__()

        self.set_window()  
        self.set_controls()
        self.set_timer()
        self.set_session() 
        self.load_tasks(False)

        self.modeButtons = [
            self.standardButton,
            self.pomodoroButton,
            self.timerButton,
        ]

    def set_timer(self):
        self.timerInterval = DEFAULT_POMODORO_DURATION
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_time)

        self.time = QTime(0, 0, 0)
        self.isRunning = False


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

        self.timerLabel = QLabel("00:00:00", self)
        self.timerLabel.setStyleSheet('font-size: 32px; text-align: center;')
        self.timerLabel.setAlignment(Qt.AlignCenter)
        self.controlsLayout.addWidget(self.timerLabel)

        self.modeLabel = QLabel("", self)
        self.modeLabel.setAlignment(Qt.AlignCenter)
        self.controlsLayout.addWidget(self.modeLabel)     

        self.controlsLayout.addLayout(self.runLayout)

        self.standardButton = QPushButton(" Start", self)
        self.standardButton.setIcon(qta.icon("mdi.play"))
        self.standardButton.clicked.connect(self.toggle_standard_session)
        self.runLayout.addWidget(self.standardButton)

        self.pomodoroButton = QPushButton("Pomodoro", self)
        self.pomodoroButton.setIcon(qta.icon("mdi.food-apple"))
        self.pomodoroButton.clicked.connect(self.toggle_pomodoro_session)
        self.runLayout.addWidget(self.pomodoroButton)

        self.timerButton = QPushButton("Timer", self)
        self.timerButton.setIcon(qta.icon("mdi.timer"))
        self.timerButton.clicked.connect(self.toggle_timer_session)
        self.runLayout.addWidget(self.timerButton)
        
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
        

    def update_time(self):
        if self.timerMode != TimerMode.STANDARD:
            self.time = self.time.addSecs(-1)
            if self.time == QTime(0, 0, 11):
                self.play_alarm()                
            elif self.time <= QTime(0, 0, 0):
                if self.timerMode == TimerMode.POMODORO:
                    self.toggle_pomodoro_session()  
                else:
                    self.toggle_timer_session()
                self.time = QTime(0, 0, 0, 1) 
        else: 
            self.time = self.time.addSecs(1)
        self.timerLabel.setText(self.time.toString("hh:mm:ss"))


    def reset_timer(self):
        self.modeLabel.setText("")
        self.timerInterval = DEFAULT_POMODORO_DURATION
        self.time.setHMS(0, 0, 0)
        self.timerLabel.setText("00:00:00")
        self.timerMode = TimerMode.NO_MODE
        self.resetButton.setEnabled(False)
        for b in self.modeButtons:
            b.setVisible(True)
        self.load_tasks(False)
        self.taskCombo.setEnabled(True)


    def update_reset_button_state(self):
        isEnable = (not self.isRunning) 
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
        

    def play_alarm(self):
        self.alarmAudio = QSoundEffect()
        soundPath = Path(__file__).parent.parent.parent / 'assets' / 'sounds' / 'alarm.wav'

        self.alarmAudio.setSource(QUrl.fromLocalFile(str(soundPath.resolve())))
        self.alarmAudio.setVolume(.9)

        self.alarmAudio.play()
        

    def toggle_standard_session(self):
        self.toggle_session(TimerMode.STANDARD, self.standardButton, "mdi.play")

    def toggle_pomodoro_session(self):
        self.toggle_session(TimerMode.POMODORO, self.pomodoroButton, "mdi.food-apple")

    def toggle_timer_session(self):
        if self.timerMode == TimerMode.NO_MODE:
            timerInterval = selectintervaldialog.IntervalDialog(self)
            if timerInterval.exec() == QDialog.Accepted:
                self.timerInterval = timerInterval.get_interval()

        self.toggle_session(TimerMode.TIMER, self.timerButton, "mdi.timer")



    def toggle_session(self, mode, button, icon_name):
        for b in self.modeButtons:
            b.setVisible(b == button)

        if self.isRunning:
            self.stop_timer()
            button.setText(" Continue")
            button.setIcon(qta.icon(icon_name))
        else:
            self.timerMode = mode
            self.modeLabel.setText(mode.label)
            self.start_timer()
            button.setText(" Stop")
            button.setIcon(qta.icon("mdi.stop"))




    def start_timer(self):
        self.isRunning = True
        self.session.start_time = datetime.now()
        self.session.mode = self.timerMode.label
        self.session.sessiondate = int(self.session.start_time.strftime("%Y%m%d"))
        self.timer.start(1000)
        self.taskCombo.setEnabled(False)
        if self.time <= QTime(0, 0, 0, 1):
            self.time = self.timerInterval


    def stop_timer(self):
        self.isRunning = False
        self.timer.stop()
        self.save_data()
        self.update_reset_button_state()
