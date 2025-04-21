import sys
import qtawesome as qta
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel
from PySide6.QtCore import QTime, QTimer, Qt


class Chronopio(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Chronopio")
        self.resize(350, 300)

        self.timerLayout = QVBoxLayout()
        self.setLayout(self.timerLayout)
        self.runLayout = QHBoxLayout()

        self.label = QLabel("00:00:00", self)
        self.label.setStyleSheet('font-size: 32px; text-align: center;')
        self.label.setAlignment(Qt.AlignCenter)
        self.timerLayout.addWidget(self.label)

        self.runButton = QPushButton(" Start", self)
        self.runButton.setIcon(qta.icon("mdi.play"))
        self.runButton.clicked.connect(self.toggle_run_timer)
        self.runLayout.addWidget(self.runButton)

        self.pomodoroButton = QPushButton("Pomodoro", self)
        self.pomodoroButton.setIcon(qta.icon("mdi.food-apple"))
        self.pomodoroButton.clicked.connect(self.toggle_pomodoro_timer)
        self.runLayout.addWidget(self.pomodoroButton)
        
        
        self.timerLayout.addLayout(self.runLayout)

        self.resetButton = QPushButton("Reset", self)
        self.resetButton.clicked.connect(self.reset_timer)
        self.resetButton.setIcon(qta.icon("mdi.recycle-variant"))
        self.resetButton.setEnabled(False)    
        self.timerLayout.addWidget(self.resetButton)
    
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_time)

        self.time = QTime(0, 0, 0)
        self.running = False # General running
        self.standardTimer = False # Run standard timer Status
        self.pomodoro = False # Run Pomodoro Status

    def toggle_run_timer(self):
        if self.standardTimer:
            self.timer.stop()
            self.runButton.setText(" Continue")
            self.runButton.setIcon(qta.icon("mdi.play"))
        else: 
            self.timer.start(1000) # Update every second
            self.runButton.setText(" Stop")
            self.runButton.setIcon(qta.icon("mdi.stop"))
        self.running = not self.running
        self.standardTimer = not self.standardTimer
        self.pomodoroButton.setVisible(False)
        self.reset_disability()

    def toggle_pomodoro_timer(self):
        if self.pomodoro:
            self.timer.stop()
            self.pomodoroButton.setText(" Continue")
            self.pomodoroButton.setIcon(qta.icon("mdi.food-apple"))
        else: 
            if self.time == QTime(0, 0, 0): 
                self.label.setText("00:25:00")
                self.time = QTime(0, 25, 0)
            self.timer.start(1000)
            self.pomodoroButton.setText(" Stop")
            self.pomodoroButton.setIcon(qta.icon("mdi.stop"))
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

    def reset_disability(self):
        isEnable = (not self.running) and (self.time != QTime(0, 0, 0))
        self.resetButton.setEnabled(isEnable)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Chronopio()
    window.show()
    sys.exit(app.exec())

