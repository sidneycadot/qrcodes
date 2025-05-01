#! /usr/bin/env python3

from typing import NamedTuple

from PySide6.QtCore import QRectF, Qt
from PySide6.QtGui import QPixmap, QPainter, QColorConstants, QPen, QBrush, QFont
from PySide6.QtWidgets import QApplication, QMainWindow, QGraphicsView, QGraphicsScene, QGraphicsItem, QWidget, QSpinBox

from gui.layout_utilities import hbox_layout, vbox_layout, grid_layout, groupbox


class PointXY(NamedTuple):
    x: float
    y: float

class GridParameters(NamedTuple):
    origin: PointXY
    h: PointXY
    v: PointXY
    version: int


class MyGrabber(QGraphicsItem):

    def __init__(self, label: str):
        super().__init__()
        self.label = label

    def boundingRect(self):
        return QRectF(-100.0, -100.0, 200.0, 200.0)

    def paint(self, painter: QPainter, option, widget):

        pen1 = QPen(Qt.NoPen)
        brush1 = QBrush(Qt.SolidPattern)
        brush1.setColor(QColorConstants.Yellow)

        painter.setPen(pen1)
        painter.setBrush(brush1)

        painter.drawEllipse(-16.0, -16.0, 32.0, 32.0)

        pen2 = QPen()
        pen2.setColor(QColorConstants.Blue)
        pen2.setWidthF(1.0)

        painter.setPen(pen2)

        font = painter.font()
        font.setPointSizeF(14.0)
        font.setWeight(QFont.Bold)
        painter.setFont(font)

        painter.drawText(-50, -50, 100, 100, Qt.AlignCenter, self.label)


class MyGrid(QGraphicsItem):

    def __init__(self):
        super().__init__()
        self.active_parameters = None

    def boundingRect(self):
        return QRectF(-1000.0, -1000.0, 2000.0, 2000.0)

    def paint(self, painter: QPainter, option, widget):

        if self.active_parameters is None:
            return

        pen = QPen(Qt.NoPen)

        brush = QBrush(Qt.SolidPattern)
        brush.setColor(QColorConstants.Red)

        painter.setPen(pen)
        painter.setBrush(brush)

        n = 17 + 4 * self.active_parameters.version

        origin = self.active_parameters.origin
        o_to_h = PointXY(self.active_parameters.h.x - origin.x, self.active_parameters.h.y - origin.y)
        o_to_v = PointXY(self.active_parameters.v.x - origin.x, self.active_parameters.v.y - origin.y)

        radius = 3
        diameter = 2.0 * radius

        for i in range(n):
            for j in range(n):

                fi = (i + 0.5) / n
                fj = (j + 0.5) / n

                x = origin.x + fi * o_to_h.x + fj * o_to_v.x
                y = origin.y + fi * o_to_h.y + fj * o_to_v.y

                painter.drawEllipse(x-radius, y-radius, diameter, diameter)

    def set_grid_parameters(self, parameters: GridParameters):
        if parameters == self.active_parameters:
            return
        self.active_parameters = parameters
        self.update()


class MyCentralWidget(QWidget):

    def __init__(self):
        super().__init__()

        pixmap = QPixmap()
        pixmap.load("example_qrcode_oralb.jpg")

        scene = QGraphicsScene()

        scene.addPixmap(pixmap)

        o_grabber = MyGrabber("O")
        o_grabber.setFlag(QGraphicsItem.ItemIsMovable)
        o_grabber.moveBy(752.0, 46.0)
        scene.addItem(o_grabber)

        h_grabber = MyGrabber("H")
        h_grabber.setFlag(QGraphicsItem.ItemIsMovable)
        h_grabber.moveBy(772.0, 761.0)
        scene.addItem(h_grabber)

        v_grabber = MyGrabber("V")
        v_grabber.setFlag(QGraphicsItem.ItemIsMovable)
        v_grabber.moveBy(40.0, 81.0)
        scene.addItem(v_grabber)

        grid = MyGrid()
        scene.addItem(grid)

        self.o_grabber = o_grabber
        self.h_grabber = h_grabber
        self.v_grabber = v_grabber
        self.grid = grid

        scene.changed.connect(self.handle_change)

        scene_view_widget = QGraphicsView()
        scene_view_widget.setScene(scene)

        version_spinbox = QSpinBox()
        version_spinbox.setRange(1, 40)
        version_spinbox.valueChanged.connect(self.handle_change)

        self.version_spinbox = version_spinbox

        toplevel_layout = vbox_layout(
            '*stretch*',
            hbox_layout(
                '*stretch*',
                scene_view_widget,
                '*stretch*',
                vbox_layout(
                    groupbox(
                        "Settings",
                        grid_layout(
                            ["version", version_spinbox]
                        )
                    ),
                    '*stretch*'
                ),
            '*stretch*'
            ),
            '*stretch*'
        )

        self.setLayout(toplevel_layout)

    def handle_change(self):

        parameters = GridParameters(
            origin=PointXY(self.o_grabber.x(), self.o_grabber.y()),
            h=PointXY(self.h_grabber.x(), self.h_grabber.y()),
            v=PointXY(self.v_grabber.x(), self.v_grabber.y()),
            version=self.version_spinbox.value()
        )

        print(parameters)
        self.grid.set_grid_parameters(parameters)


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("QRCode Lab")

        central_widget = MyCentralWidget()
        self.setCentralWidget(central_widget)


class Application(QApplication):
    def __init__(self):
        super().__init__()
        main_window = MainWindow()
        main_window.show()
        self._main_window = main_window


def main():
    app = Application()
    exitcode = app.exec()
    print(exitcode)


if __name__ == "__main__":
    main()
