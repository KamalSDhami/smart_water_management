# ui/main_window.py

from PyQt6.QtWidgets import QMainWindow, QWidget, QHBoxLayout
from ui.canvas_view import CanvasView
from ui.sidebar import Sidebar

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("💧 Smart Water Management System")
        self.setGeometry(100, 100, 1200, 800)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QHBoxLayout()
        central_widget.setLayout(layout)

        self.canvas = CanvasView()
        self.sidebar = Sidebar(self.canvas)

        layout.addWidget(self.sidebar)
        layout.addWidget(self.canvas)
