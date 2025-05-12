from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QLabel, QSpinBox, QGroupBox, QFormLayout, QFrame, QScrollArea
)
from PyQt6.QtCore import Qt

class Sidebar(QWidget):
    def __init__(self):
        super().__init__()
        self.canvas = None
        self.setFixedWidth(260)
        self.init_ui()

    def set_canvas(self, canvas):
        self.canvas = canvas

    def init_ui(self):
        # Create a scroll area
        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setFrameShape(QFrame.Shape.NoFrame)

        # Main content widget for the scroll area
        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout.setSpacing(18)

        # Title
        title = QLabel("Smart Water\nManagement")
        title.setStyleSheet("font-size: 22px; font-weight: bold; color: #4FC3F7;")
        layout.addWidget(title)

        layout.addWidget(self._hline())

        # Controls
        self.btn_add_node = QPushButton("Add Node")
        self.btn_connect = QPushButton("Connect Nodes")
        self.btn_prim = QPushButton("Run Prim")
        self.btn_simulate = QPushButton("Simulate Flow")
        self.btn_show_graph = QPushButton("Show Graph")
        self.btn_remove_node = QPushButton("Remove Node")
        self.btn_disconnect_edge = QPushButton("Disconnect Edge")
        self.btn_move_node = QPushButton("Move Node")

        for btn in [self.btn_add_node, self.btn_connect, self.btn_prim, self.btn_simulate, self.btn_show_graph, self.btn_remove_node, self.btn_disconnect_edge, self.btn_move_node]:
            btn.setStyleSheet("font-size: 16px; padding: 8px;")
            layout.addWidget(btn)

        layout.addWidget(self._hline())

        # Parameters
        param_box = QGroupBox("Simulation Parameters")
        param_layout = QFormLayout()
        self.spin_pressure = QSpinBox()
        self.spin_pressure.setRange(1, 1000)
        self.spin_pressure.setValue(100)
        self.spin_pressure.setStyleSheet("color: white; background-color: #222; border: 1px solid #555;")
        self.spin_flow = QSpinBox()
        self.spin_flow.setRange(1, 100)
        self.spin_flow.setValue(10)
        self.spin_flow.setStyleSheet("color: white; background-color: #222; border: 1px solid #555;")
        param_layout.addRow("Initial Pressure:", self.spin_pressure)
        param_layout.addRow("Flow Rate:", self.spin_flow)
        param_box.setLayout(param_layout)
        layout.addWidget(param_box)

        layout.addWidget(self._hline())

        # Results
        self.result_label = QLabel("")
        self.result_label.setWordWrap(True)
        self.result_label.setStyleSheet("font-size: 14px; color: #FFD54F;")
        layout.addWidget(self.result_label)

        layout.addStretch(1)

        # Set the content widget to the scroll area
        scroll.setWidget(content)

        # Set the scroll area as the main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(scroll)

        # Connect signals
        self.btn_add_node.clicked.connect(self.on_add_node)
        self.btn_connect.clicked.connect(self.on_connect)
        self.btn_prim.clicked.connect(self.on_prim)
        self.btn_simulate.clicked.connect(self.on_simulate)
        self.btn_show_graph.clicked.connect(self.on_show_graph)
        self.btn_remove_node.clicked.connect(self.on_remove_node)
        self.btn_disconnect_edge.clicked.connect(self.on_disconnect_edge)
        self.btn_move_node.clicked.connect(self.on_move_node)

    def _hline(self):
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)
        line.setStyleSheet("color: #444;")
        return line

    def on_add_node(self):
        if self.canvas:
            self.canvas.set_mode("add_node")

    def on_connect(self):
        if self.canvas:
            self.canvas.set_mode("connect")

    def on_prim(self):
        if self.canvas:
            self.canvas.run_prim()

    def on_simulate(self):
        if self.canvas:
            pressure = self.spin_pressure.value()
            flow = self.spin_flow.value()
            self.canvas.simulate_flow(pressure, flow)

    def on_show_graph(self):
        if self.canvas:
            self.canvas.show_graphs()

    def on_remove_node(self):
        if self.canvas:
            self.canvas.set_mode("remove_node")

    def on_disconnect_edge(self):
        if self.canvas:
            self.canvas.set_mode("disconnect_edge")

    def on_move_node(self):
        if self.canvas:
            self.canvas.set_mode("move_node")

    def set_result(self, text):
        self.result_label.setText(text)