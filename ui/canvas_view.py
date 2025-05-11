# ui/canvas_view.py

from PyQt6.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsEllipseItem
from PyQt6.QtGui import QBrush, QPen
from PyQt6.QtCore import Qt, QPointF
from PyQt6.QtGui import QPainter

class NodeItem(QGraphicsEllipseItem):
    def __init__(self, x, y, radius=20, node_id=None):
        super().__init__(-radius, -radius, radius*2, radius*2)
        self.setBrush(QBrush(Qt.GlobalColor.cyan))
        self.setPen(QPen(Qt.GlobalColor.black, 2))
        self.setFlag(self.GraphicsItemFlag.ItemIsMovable)
        self.setFlag(self.GraphicsItemFlag.ItemIsSelectable)
        self.setPos(x, y)
        self.node_id = node_id

class CanvasView(QGraphicsView):
    def __init__(self):
        super().__init__()
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.setSceneRect(0, 0, 1000, 800)

        self.node_counter = 1
        self.adding_node = False

    def mousePressEvent(self, event):
        if self.adding_node:
            scene_pos = self.mapToScene(event.pos())
            node = NodeItem(scene_pos.x(), scene_pos.y(), node_id=self.node_counter)
            self.scene.addItem(node)
            self.node_counter += 1
            self.adding_node = False
        else:
            super().mousePressEvent(event)

    def enable_add_node_mode(self):
        self.adding_node = True
