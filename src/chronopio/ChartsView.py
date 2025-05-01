from datetime import datetime
from collections import defaultdict
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QSizePolicy, 
    QHBoxLayout, QPushButton, QDateEdit
    )
from PySide6.QtCharts import (
    QChartView, QChart, QPieSeries, 
    QBarSet, QBarCategoryAxis, QValueAxis, QBarSeries
    )
from PySide6.QtCore import Qt, QDate
from .SessionLogger import SessionLogger


class ChartsView(QWidget):
    def __init__(self):
        super().__init__()

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.init_filters()
        self.init_charts()
        self.apply_filter()
        

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

    
    def init_charts(self):
        self.durationPerTaskCV = QChartView()
        self.layout.addWidget(self.durationPerTaskCV)

        self.durationTaskPerDayCV = QChartView()
        self.layout.addWidget(self.durationTaskPerDayCV)


    def apply_filter(self):
        fromDate = int(self.fromDate.date().toString('yyyyMMdd'))
        toDate = int(self.toDate.date().toString('yyyyMMdd'))

        logger = SessionLogger()
        sessions = logger.get_sessions_data(fromDate, toDate)

        self.duration_per_task_pie(sessions)
        self.duration_task_per_day(sessions)
            

    def duration_per_task_pie(self, sessions):
        taskDurations = {}
        for session in sessions:
            task = session[1]
            duration = session[4]
            taskDurations[task] = taskDurations.get(task, 0) + duration


        series = QPieSeries()
        for task, totalDuration in taskDurations.items():
            taskLabel = f"{task} ({totalDuration / 60:.1f} mins.)"
            series.append(taskLabel, totalDuration)

        chart = QChart()
        chart.addSeries(series)
        chart.setTitle("Duration per task")
        
        chart.legend().setVisible(True)
        chart.legend().setAlignment(Qt.AlignRight)

        chart.setAnimationOptions(QChart.SeriesAnimations)

        self.durationPerTaskCV.setChart(chart)


    def duration_task_per_day(self, sessions):
        dailyTasks = defaultdict(lambda: defaultdict(int))
        for session in sessions:
            date = session[0]
            task = session[1]
            duration = session[4]
            dailyTasks[date][task] += duration

        chart = QChart()
        series = QBarSeries()
        series.setLabelsVisible(True)

        tasks = set()
        dates = sorted(dailyTasks.keys())
        strDates = [datetime.strptime(str(d), "%Y%m%d").strftime("%d/%m/%Y") for d in dates]

        for taskOnDay in dailyTasks.values():
            tasks.update(taskOnDay.keys())
        tasks = sorted(tasks)

        barSets = {task: QBarSet(task) for task in tasks}
        #for task in tasks:
        #    barSets[task].setColor(Qt.GlobalColor.blue)

        for date in dates:
            for task in tasks:
                duration = dailyTasks[date].get(task, 0)
                barSets[task] << round(duration / 60.0, 1)

        for task in tasks:
            series.append(barSets[task])

        chart.addSeries(series)

        axisX = QBarCategoryAxis()
        axisX.append(strDates)
        chart.addAxis(axisX, Qt.AlignBottom)
        series.attachAxis(axisX)

        axisY = QValueAxis()
        axisY.setTitleText("Duration (mins)")
        chart.addAxis(axisY, Qt.AlignLeft)
        series.attachAxis(axisY)

        chart.setTitle("Duration per task per day")
        chart.setAnimationOptions(QChart.SeriesAnimations)
        chart.legend().setVisible(True)

        self.durationTaskPerDayCV.setChart(chart)
        self.durationTaskPerDayCV.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
