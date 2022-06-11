import sys
from turtle import right
from PyQt5.QtWidgets import QApplication, QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QGridLayout
from PyQt5.QtCore import Qt, QPoint, QRect, QDir, QSize
from PyQt5.QtGui import QPixmap, QPainter, QBrush, QPen

colors = {0: 'darkgrey', 1: 'yellow',
          2: 'darkgreen', 3: 'darkred', 4: 'lightgrey', 5: 'blue'}
qt_colors = [Qt.darkGray, Qt.yellow, Qt.darkGreen,
             Qt.darkRed, Qt.lightGray, Qt.blue]


class MyApp(QWidget):
    def __init__(self):
        super().__init__()
        self.window_width, self.window_height = 1200, 800
        self.SCALING = 80.0
        self.setMinimumSize(self.window_width, self.window_height)

        self.shapeslist = []
        self.agentposition = None
        self.selected = 0

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
        self.btn_4 = QPushButton('Delete', self)
        self.btn_5 = QPushButton('Agent', self)
        self.btn_6 = QPushButton('Export', self)
        self.btn_0.setStyleSheet(f"background-color : {colors[0]}")
        self.btn_1.setStyleSheet(f"background-color : {colors[1]}")
        self.btn_2.setStyleSheet(f"background-color : {colors[2]}")
        self.btn_3.setStyleSheet(f"background-color : {colors[3]}")
        self.btn_4.setStyleSheet(f"background-color : {colors[4]}")
        self.btn_5.setStyleSheet(f"background-color : {colors[5]}")

        self.buttons = [self.btn_0, self.btn_1,
                        self.btn_2, self.btn_3, self.btn_4, self.btn_5]

        self.btn_0.clicked.connect(lambda ch, i=0: self.genericbutton(i))
        self.btn_1.clicked.connect(lambda ch, i=1: self.genericbutton(i))
        self.btn_2.clicked.connect(lambda ch, i=2: self.genericbutton(i))
        self.btn_3.clicked.connect(lambda ch, i=3: self.genericbutton(i))
        self.btn_4.clicked.connect(lambda ch, i=4: self.genericbutton(i))
        self.btn_5.clicked.connect(lambda ch, i=5: self.genericbutton(i))

        self.btn_6.clicked.connect(self.save_to_json)

        self.rightside = QWidget()
        rightsidelayout = QGridLayout()
        rightsidelayout.setSpacing(10)
        rightsidelayout.addWidget(self.btn_0, 0, 0)
        rightsidelayout.addWidget(self.btn_1, 0, 1)
        rightsidelayout.addWidget(self.btn_2, 1, 0)
        rightsidelayout.addWidget(self.btn_3, 1, 1)
        rightsidelayout.addWidget(self.btn_4, 2, 0)
        rightsidelayout.addWidget(self.btn_5, 2, 1)
        rightsidelayout.addWidget(self.btn_6, 3, 0)
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

        self.selected = input

        # selected = 4

    def paintEvent(self, event):
        # print('paintevent')
        painter = QPainter(self)
        painter.drawPixmap(QPoint(), self.pix)
        if not self.begin.isNull() and not self.destination.isNull() and self.selected is not 5:
            rect = QRect(self.begin, self.destination)
            if self.selected is not 4:
                painter.drawRect(rect.normalized())
                painter.fillRect(rect.normalized(), QBrush(
                    qt_colors[self.selected]))
            else:
                painter.drawRect(rect.normalized())

    def mousePressEvent(self, event):
        if event.buttons() & Qt.LeftButton:
            print("Point 1")
            self.begin = event.pos()
            self.destination = self.begin
            self.update()

    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.LeftButton:
            # print("Point 2")
            self.destination = event.pos()
            self.update()

    def mouseReleaseEvent(self, event):
        print("Point 3")

        if event.button() & Qt.LeftButton:
            rect = QRect(self.begin, self.destination)

            # Delete shapes in case of painter
            # if self.selected is 4:
            #     for otherrect, typeindex in self.shapeslist:
            #         if otherrect.intersects(rect):
            if self.selected is 4:  # delete
                if any(item[0].intersects(rect) and item[1] is 5 for item in self.shapeslist):
                    self.agentposition = None
                self.shapeslist = [
                    item for item in self.shapeslist if not item[0].intersects(rect)]
            elif self.selected in [1, 2, 3]:
                # Check if there is any intersection with other tiles. In case this is true
                if not any(item[0].intersects(rect) for item in self.shapeslist):
                    self.shapeslist.append((rect, self.selected))
            elif self.selected is 0:
                if not any(item[0].intersects(rect) and item[1] is not 0 for item in self.shapeslist):
                    self.shapeslist.append((rect, self.selected))
            elif self.selected is 5:
                self.agentposition = None
                self.shapeslist = [
                    item for item in self.shapeslist if not item[1] is 5]
                print(self.destination)
                rect = self.getBoundingBox(self.destination)
                if not any(item[0].intersects(rect) for item in self.shapeslist):
                    self.shapeslist.append((rect, self.selected))
                    self.agentposition = self.destination

            self.pix = QPixmap(self.rect().size())
            self.pix.fill(Qt.white)

            painter = QPainter(self.pix)

            # self.shapeslist = sorted(self.shapeslist, key=lambda tup: tup[1])

            for shape, typeindex in self.shapeslist:
                # if typeindexis not 5:
                painter.drawRect(shape.normalized())
                painter.fillRect(shape.normalized(), QBrush(
                    qt_colors[typeindex]))

            if self.agentposition is not None:
                painter.setPen(QPen(Qt.green,  1, Qt.SolidLine))
                painter.drawEllipse(self.agentposition,
                                    self.SCALING * 0.5, self.SCALING * 0.5)
                painter.setPen(QPen())

            self.begin, self.destination = QPoint(), QPoint()
            # print(painter)

            self.update()
            print(self.shapeslist)
            # self.pix = QPixmap(self.rect().size())

    def getBoundingBox(self, point: QPoint):
        botleftpoint = point - \
            QPoint(1 * self.SCALING * 0.5, 1 * self.SCALING * 0.5)
        rect = QRect(QPoint(botleftpoint), QSize(
            1 * self.SCALING, 1 * self.SCALING))
        return rect

    def save_to_json(self):
        print('should save neef')
        # TODO Save to correct format!


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
