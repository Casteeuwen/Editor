import sys
from turtle import right
from PyQt5.QtWidgets import QApplication, QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QGridLayout
from PyQt5.QtCore import Qt, QPoint, QRect
from PyQt5.QtGui import QPixmap, QPainter


def button1():
    print('button 1 clicked i guess')


def button2():
    print('button 2 clicked i guess')


def button3():
    print('button 3 clicked i guess')


def button4():
    print('button 4 clicked i guess')


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

        self.btn_1 = QPushButton('1', self)
        self.btn_2 = QPushButton('2', self)
        self.btn_3 = QPushButton('3', self)
        self.btn_4 = QPushButton('4', self)

        self.btn_1.clicked.connect(button1)
        self.btn_2.clicked.connect(button2)
        self.btn_3.clicked.connect(button3)
        self.btn_4.clicked.connect(button4)

        self.rightside = QWidget()
        rightsidelayout = QGridLayout()
        rightsidelayout.setSpacing(0)
        rightsidelayout.addWidget(self.btn_1, 0, 0)
        rightsidelayout.addWidget(self.btn_2, 0, 1)
        rightsidelayout.addWidget(self.btn_3, 1, 0)
        rightsidelayout.addWidget(self.btn_4, 1, 1)
        self.rightside.setLayout(rightsidelayout)

        self.rightsidewrapper = QWidget()
        rightsidewrapperlayout = QVBoxLayout()
        rightsidelayout.setSpacing(0)
        rightsidewrapperlayout.addWidget(self.rightside)
        rightsidewrapperlayout.addStretch(1)
        self.rightsidewrapper.setLayout(rightsidewrapperlayout)

        layout.addWidget(self.rightsidewrapper)

        self.begin, self.destination = QPoint(), QPoint()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.drawPixmap(QPoint(), self.pix)
        if not self.begin.isNull() and not self.destination.isNull():
            rect = QRect(self.begin, self.destination)
            painter.drawRect(rect.normalized())

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
