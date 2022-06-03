import sys
from turtle import right
from PyQt5.QtWidgets import QApplication, QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QGridLayout
from PyQt5.QtCore import Qt, QPoint, QRect
from PyQt5.QtGui import QPixmap, QPainter

colors = {0: 'darkgrey', 1: 'gold', 2: 'brown', 3: 'darkred'}

selected = 0


class MyApp(QWidget):
    def __init__(self):
        super().__init__()
        self.window_width, self.window_height = 1200, 800
        self.setMinimumSize(self.window_width, self.window_height)

        layout = QHBoxLayout()
        layout.addStretch(1)
        layout.setSpacing(0)
        self.setLayout(layout)
        self.pix = QPixmap(self.rect().size())
        self.pix.fill(Qt.white)

        # Buttons

        self.btn_0 = QPushButton('Wall', self)
        self.btn_1 = QPushButton('Goal', self)
        self.btn_2 = QPushButton('Dirty', self)
        self.btn_3 = QPushButton('Death', self)
        self.btn_0.setStyleSheet(f"background-color : {colors[0]}")
        self.btn_1.setStyleSheet(f"background-color : {colors[1]}")
        self.btn_2.setStyleSheet(f"background-color : {colors[2]}")
        self.btn_3.setStyleSheet(f"background-color : {colors[3]}")

        self.buttons = [self.btn_0, self.btn_1, self.btn_2, self.btn_3]

        self.btn_0.clicked.connect(lambda ch, i=0: self.genericbutton(i))
        self.btn_1.clicked.connect(lambda ch, i=1: self.genericbutton(i))
        self.btn_2.clicked.connect(lambda ch, i=2: self.genericbutton(i))
        self.btn_3.clicked.connect(lambda ch, i=3: self.genericbutton(i))

        self.rightside = QWidget()
        rightsidelayout = QGridLayout()
        rightsidelayout.setSpacing(10)
        rightsidelayout.addWidget(self.btn_0, 0, 0)
        rightsidelayout.addWidget(self.btn_1, 0, 1)
        rightsidelayout.addWidget(self.btn_2, 1, 0)
        rightsidelayout.addWidget(self.btn_3, 1, 1)
        self.rightside.setLayout(rightsidelayout)

        self.rightsidewrapper = QWidget()
        rightsidewrapperlayout = QVBoxLayout()
        rightsidelayout.setSpacing(0)
        rightsidewrapperlayout.addWidget(self.rightside)
        rightsidewrapperlayout.addStretch(1)
        self.rightsidewrapper.setLayout(rightsidewrapperlayout)

        layout.addWidget(self.rightsidewrapper)

        self.begin, self.destination = QPoint(), QPoint()

    def genericbutton(self, input):
        print(f'button {input} clicked i guess')
        for index, but in enumerate(self.buttons):
            but.setStyleSheet(f"background-color : {colors[index]}")

        self.buttons[input].setStyleSheet(
            "border :5px solid;" f"background-color : {colors[input]}")

        # selected = 4

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.drawPixmap(QPoint(), self.pix)
        if not self.begin.isNull() and not self.destination.isNull():
            rect = QRect(self.begin, self.destination)
            painter.drawRect(rect.normalized())
            # self.update()

    def mousePressEvent(self, event):
        if event.buttons() & Qt.LeftButton:
            print("Point 1")
            self.begin = event.pos()
            self.destination = self.begin
            self.update()

    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.LeftButton:
            print("Point 2")
            self.destination = event.pos()
            self.update()

    def mouseReleaseEvent(self, event):
        print("Point 3")
        if event.button() & Qt.LeftButton:
            rect = QRect(self.begin, self.destination)
            painter = QPainter(self.pix)
            painter.drawRect(rect.normalized())

            self.begin, self.destination = QPoint(), QPoint()

            self.update()


if __name__ == "__main__":
    # don't auto scale when drag app to a different monitor.
    # QApplication.setAttribute(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)

    app = QApplication(sys.argv)
    app.setStyleSheet(
        """
		QWidget {
			font-size: 30px;
		}
	"""
    )

    myApp = MyApp()
    myApp.show()

    try:
        sys.exit(app.exec_())
    except SystemExit:
        print("Closing Window...")
