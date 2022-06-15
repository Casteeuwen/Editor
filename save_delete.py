from email.charset import QP
import sys
from turtle import right
from PyQt5.QtWidgets import QApplication, QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QGridLayout, QInputDialog, QLineEdit
from PyQt5.QtCore import Qt, QPoint, QRect, QDir, QSize, QLine
from PyQt5.QtGui import QPixmap, QPainter, QBrush, QPen, QColor
import json

colors = {0: 'darkgrey', 1: 'yellow',
          2: 'darkgreen', 3: 'darkred', 4: 'lightgrey', 5: 'blue'}
qt_colors = [Qt.darkGray, Qt.yellow, Qt.darkGreen,
             Qt.darkRed, Qt.lightGray, Qt.blue]

to_json_mapping = {0: 'obstacles', 1: 'golds',
                   2: 'goals', 3: 'death', 5: 'agents'}


class MyApp(QWidget):
    def __init__(self):
        super().__init__()
        self.window_width, self.window_height = 1200, 800

        self.SCALING = 40.0
        self.ROOMSIZE = 15.0

        self.xmax, self.ymax = self.ROOMSIZE*self.SCALING, self.ROOMSIZE*self.SCALING

        self.setMinimumSize(self.window_width, self.window_height)

        self.shapeslist = []
        self.shapeslist.append(
            (QRect(QPoint(0, 0), QPoint(self.xmax, self.ymax)), -1))
        # self.agentposition = None
        self.selected = 0

        layout = QHBoxLayout()
        layout.addStretch(1)
        layout.setSpacing(0)
        self.setLayout(layout)
        self.pix = QPixmap(self.rect().size())
        self.pix.fill(QColor(70, 70, 70))

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
        # self.mouseReleaseEvent(None)
        self.draw()

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

    def getmaxlocations(self, rect: QRect):
        tole_x = min(rect.topLeft().x(), rect.topRight().x(),
                     rect.bottomLeft().x(), rect.bottomRight().x())
        tole_y = min(rect.topLeft().y(), rect.topRight().y(),
                     rect.bottomLeft().y(), rect.bottomRight().y())
        bori_x = max(rect.topLeft().x(), rect.topRight().x(),
                     rect.bottomLeft().x(), rect.bottomRight().x())
        bori_y = max(rect.topLeft().y(), rect.topRight().y(),
                     rect.bottomLeft().y(), rect.bottomRight().y())

        return tole_x, tole_y, bori_x, bori_y

    def wallsnap(self, rect: QRect):
        # In case of overlap snap to closest wall edge
        while any(item[0].intersects(rect) and item[1] is 0 for item in self.shapeslist):
            print('it intersects!')
            intersectlist = [item for item in self.shapeslist if item[0].intersects(
                rect) and item[1] is 0]
            rect_2: QRect = intersectlist[0][0]

            tole_x, tole_y, bori_x, bori_y = self.getmaxlocations(rect)

            tole_x_2, tole_y_2, bori_x_2, bori_y_2 = self.getmaxlocations(
                rect_2)

            # vertic_0 = QRect(rect_2.topLeft(), rect_2.bottomLeft())
            # vertic_1 = QRect(rect_2.topRight(), rect_2.bottomRight())
            # horiz_0 = QRect(rect_2.topLeft(), rect_2.topRight())
            # horiz_1 = QRect(rect_2.bottomLeft(), rect_2.bottomRight())

            vertic_0 = QRect(QPoint(tole_x_2, tole_y_2), QPoint(tole_x_2, bori_y_2))
            vertic_1 = QRect(QPoint(bori_x_2, tole_y_2), QPoint(bori_x_2, bori_y_2))
            horiz_0 = QRect(QPoint(tole_x_2, tole_y_2), QPoint(bori_x_2, tole_y_2))
            horiz_1 = QRect(QPoint(tole_x_2, bori_y_2), QPoint(bori_x_2, bori_y_2))

            if rect.intersects(vertic_0):
                # print(rect.topLeft(), rect.topRight())
                rect = QRect(QPoint(tole_x, tole_y), QPoint(
                    tole_x_2, bori_y))

            if rect.intersects(vertic_1):
                # print(rect.topLeft(), rect.topRight())
                rect = QRect(QPoint(bori_x, tole_y), QPoint(
                    bori_x_2, bori_y))

            if rect.intersects(horiz_0):
                # print(rect.topLeft(), rect.topRight())
                rect = QRect(QPoint(tole_x, tole_y), QPoint(
                    bori_x, tole_y_2))

            if rect.intersects(horiz_1):
                # print(rect.topLeft(), rect.topRight())
                rect = QRect(QPoint(bori_x, bori_y), QPoint(
                    tole_x, bori_y_2))
            break
        return rect

        # Check if any of the points is really close to another existing point, and snap this edge to that

        return

    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.LeftButton:
            # print("Point 2")
            self.destination = event.pos()
            self.update()

    def draw(self):

        self.pix = QPixmap(self.rect().size())
        self.pix.fill(QColor(70, 70, 70))

        painter = QPainter(self.pix)
        painter.setPen(QPen(Qt.black,  2))
        # self.shapeslist = sorted(self.shapeslist, key=lambda tup: tup[1])
        for shape, typeindex in self.shapeslist:
            if typeindex is -1:
                print('other typeindex')
                painter.drawRect(shape.normalized())
                painter.fillRect(shape.normalized(),
                                 QBrush(QColor(200, 200, 200)))
        for shape, typeindex in self.shapeslist:
            if typeindex is -1:
                pass
            elif typeindex is not 5:
                painter.drawRect(shape.normalized())
                painter.fillRect(shape.normalized(), QBrush(
                    qt_colors[typeindex]))
            else:
                painter.setPen(QPen(Qt.black,  3, Qt.SolidLine))
                painter.drawEllipse(shape.topLeft(
                ) + QPoint(self.SCALING * 0.5, self.SCALING * 0.5), self.SCALING * 0.5, self.SCALING * 0.5)
                painter.setPen(QPen(Qt.black,  2))

            # if self.agentposition is not None:

            self.begin, self.destination = QPoint(), QPoint()
            # print(painter)

            self.update()
            print(self.shapeslist)
            # self.pix = QPixmap(self.rect().size())

    def mouseReleaseEvent(self, event):
        print("Point 3")

        if event.button() & Qt.LeftButton:
            rect = QRect(self.clipPoint(self.begin, self.xmax, self.ymax), self.clipPoint(
                self.destination, self.xmax, self.ymax))
            rect = self.wallsnap(rect)

            # Delete shapes in case of painter
            # if self.selected is 4:
            #     for otherrect, typeindex in self.shapeslist:
            #         if otherrect.intersects(rect):
            if self.selected is 4:  # delete
                # if any(item[0].intersects(rect) and item[1] is 5 for item in self.shapeslist):
                #     self.agentposition = None
                self.shapeslist = [
                    item for item in self.shapeslist if not (item[0].intersects(rect)) or item[1] is -1]
            elif self.selected in [1, 2, 3]:
                # Check if there is any intersection with other tiles. In case this is true
                if not any(item[0].intersects(rect) and item[1] is not -1 for item in self.shapeslist):
                    self.shapeslist.append((rect, self.selected))
            elif self.selected is 0:

                if not any(item[0].intersects(rect) and item[1] is not 0 and item[1] is not -1 for item in self.shapeslist):
                    self.shapeslist.append((rect, self.selected))
            elif self.selected is 5:
                # self.agentposition = None
                # self.shapeslist = [
                #     item for item in self.shapeslist if not item[1] is 5]
                print(self.destination)
                rect = self.getBoundingBox(self.destination)
                if not any(item[0].intersects(rect) and item[1] is not -1 for item in self.shapeslist):
                    self.shapeslist.append((rect, self.selected))
                    # self.agentposition = self.destination
        self.draw()

    def clipPoint(self, point: QPoint, xmax, ymax):
        x = point.x()
        if x > xmax:
            x = xmax
        elif x < 0:
            x = 0

        y = point.y()
        if y > ymax:
            y = ymax
        elif y < 0:
            y = 0

        return QPoint(x, y)

    def getBoundingBox(self, point: QPoint):
        # Returns bounding box of the agent circle
        botleftpoint = point - \
            QPoint(1 * self.SCALING * 0.5, 1 * self.SCALING * 0.5)
        rect = QRect(QPoint(botleftpoint), QSize(
            1 * self.SCALING, 1 * self.SCALING))
        return rect

    def save_to_json(self):
        save_dict = {}
        for item in self.shapeslist:
            print(item[0].getCoords())
        # Get room coordinates
        xmax = max([max([item[0].getCoords()[0], item[0].getCoords()[2]])
                    for item in self.shapeslist])
        xmin = min([min([item[0].getCoords()[0], item[0].getCoords()[2]])
                    for item in self.shapeslist])
        ymax = max([max([item[0].getCoords()[1], item[0].getCoords()[3]])
                    for item in self.shapeslist])
        ymin = min([min([item[0].getCoords()[1], item[0].getCoords()[3]])
                    for item in self.shapeslist])

        # Hard coded the parameters here:
        xmax, xmin, ymax, ymin = self.xmax, 0.0, self.ymax, 0.0
        print([xmax, xmin, ymax, ymin])

        roomsize = [float((xmax - xmin))/self.SCALING,
                    float((ymax - ymin)) / self.SCALING]
        save_dict['roomsize'] = roomsize

        for item in self.shapeslist:
            if item[1] is not 5 and item[1] is not -1:
                itemcoords = self.get_coordinates_as_list(
                    item[0], xmax, xmin, ymax, ymin)
                save_dict.setdefault(
                    to_json_mapping[item[1]], []).append(itemcoords)
            elif item[1] is 5:
                itemcoords = self.get_coordinates_as_list(
                    item[0], xmax, xmin, ymax, ymin)
                save_dict.setdefault(
                    to_json_mapping[item[1]], []).append([float(itemcoords[0][0] + itemcoords[3][0]) / 2.0, float(itemcoords[0][1] + itemcoords[3][1]) / 2.0])

        # if self.agentposition is not None:
        #     save_dict['agent_position'] = [float(
        #         self.agentposition.x() - xmin) / self.SCALING, float(self.agentposition.y() - ymin) / self.SCALING]

        print(save_dict)

        new_filename, ok = QInputDialog().getText(self, "QInputDialog().getText()",
                                                  "Name your map:", QLineEdit.Normal,
                                                  QDir().home().dirName())

        if ok:
            with open(f'{new_filename}.json', 'w') as fp:
                json.dump(save_dict, fp)

    def get_coordinates_as_list(self, rect: QRect, xmax, xmin, ymax, ymin):
        top_left_offset = QPoint(xmin, ymin)
        coords_list = []
        for coord in [rect.topLeft(), rect.bottomLeft(), rect.topRight(), rect.bottomRight()]:
            coord: QPoint = coord - top_left_offset
            x, y = float(coord.x()) / \
                self.SCALING, float(coord.y()) / self.SCALING
            coords_list.append([x, y])
        return coords_list


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
