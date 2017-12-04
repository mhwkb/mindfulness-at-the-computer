import logging
import time
from PyQt5 import QtCore
from PyQt5 import QtGui
from PyQt5 import QtWidgets
from mc import model, mc_global
import mc.gui.breathing_dialog

BAR_WIDTH_FT = 32.0
LARGE_MARGIN_FT = 10.0
SMALL_MARGIN_FT = 2.0
POINT_SIZE_INT = 16
GRADIENT_IN_FT = 120.0
GRADIENT_OUT_FT = 150.0


class BreathingHistory(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.show()
        self.setMinimumHeight(270)
        self.setMinimumWidth(400)

        self.ib_qtimer = None
        self.ob_qtimer = None
        self.updating_gui_bool = False
        # self.breathing_rest_counter_int = 0
        # self.breath_counter_int = 0
        self.new_cycle_bool = True

        self.in_breath_graphics_qgri_list = []
        self.out_breath_graphics_qgri_list = []

        vbox_l2 = QtWidgets.QVBoxLayout()
        self.setLayout(vbox_l2)

        self.breathing_graphicsview = QtWidgets.QGraphicsView()  # QGraphicsScene
        vbox_l2.addWidget(self.breathing_graphicsview)
        self.breathing_graphicsscene = QtWidgets.QGraphicsScene()
        self.breathing_graphicsview.setScene(self.breathing_graphicsscene)
        # self.breathing_graphicsview.centerOn(QtCore.Qt.AlignRight)
        # alignment can be set with "setAlignment"
        self.breathing_graphicsview.setDragMode(QtWidgets.QGraphicsView.ScrollHandDrag)

    def add_from_dialog(self, i_ilist, i_olist):
        self.new_cycle_bool = True

        for in_length_ft, out_length_ft in zip(i_ilist, i_olist):
            # -using ob here ensures that we only add when there are complete breathing cycles
            self.add_new_breathing_rect(
                mc.mc_global.BreathingState.breathing_in,
                in_length_ft,
                mc.mc_global.BreathingVisType.popup_dialog
            )
            self.add_new_breathing_rect(
                mc.mc_global.BreathingState.breathing_out,
                out_length_ft,
                mc.mc_global.BreathingVisType.popup_dialog
            )
        self.new_cycle_bool = True

    def add_new_breathing_rect(
        self,
        i_io: mc_global.BreathingState,
        i_length: int=1,
        i_vis_type: mc_global.BreathingVisType=mc_global.BreathingVisType.mainwindow_widget,
    ):

        if i_io == mc_global.BreathingState.breathing_out:
            self.new_cycle_bool = False

        # Rectangle
        xpos = 0
        if len(self.in_breath_graphics_qgri_list) > 0:
            margin_int = SMALL_MARGIN_FT
            if self.new_cycle_bool:
                margin_int = LARGE_MARGIN_FT
            last_graphics_rect_item = self.in_breath_graphics_qgri_list[-1]
            xpos = float(last_graphics_rect_item.rect().right() + margin_int)
            if i_io == mc_global.BreathingState.breathing_out:
                xpos = float(last_graphics_rect_item.rect().left())
        width_int = BAR_WIDTH_FT
        if i_vis_type == mc_global.BreathingVisType.popup_dialog:
            width_int = mc.gui.breathing_dialog.BAR_HEIGHT_FT
        ypos = -i_length
        if i_io == mc_global.BreathingState.breathing_out:
            ypos = 0.0
        t_drawrect = QtCore.QRectF(xpos, ypos, width_int, i_length)

        # Gradient
        y_gradient = t_drawrect.y() - GRADIENT_IN_FT
        if i_io == mc_global.BreathingState.breathing_out:
            y_gradient = t_drawrect.y() + GRADIENT_OUT_FT
        t_start_qpointf = QtCore.QPointF(t_drawrect.x(), y_gradient)
        t_stop_qpointf = t_drawrect.bottomLeft()  # QtCore.QPointF(0.0, 50.0)
        t_linear_gradient = QtGui.QLinearGradient(t_start_qpointf, t_stop_qpointf)
        if i_io == mc_global.BreathingState.breathing_in:
            t_linear_gradient.setColorAt(0.0, QtGui.QColor(204, 255, 77))
            t_linear_gradient.setColorAt(1.0, QtGui.QColor(164, 230, 0))
        else:
            t_linear_gradient.setColorAt(0.0, QtGui.QColor(219, 255, 128))
            t_linear_gradient.setColorAt(1.0, QtGui.QColor(183, 255, 0))

        # Adding rectangle with gradient
        t_graphics_rect_item = self.breathing_graphicsscene.addRect(
            t_drawrect,
            pen=QtGui.QPen(QtCore.Qt.NoPen),
            brush=QtGui.QBrush(t_linear_gradient)
        )
        if i_io == mc_global.BreathingState.breathing_in:
            self.in_breath_graphics_qgri_list.append(t_graphics_rect_item)
        elif i_io == mc_global.BreathingState.breathing_out:
            self.out_breath_graphics_qgri_list.append(t_graphics_rect_item)
        # -an alternative to storing this separately might be to use ".items" and check for type
        #  as there is a QGraphicsRectItem
        # -another alternative: **http://doc.qt.io/qt-5/qgraphicsitem.html#type**
