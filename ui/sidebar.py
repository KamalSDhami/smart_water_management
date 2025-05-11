# ui/sidebar.py

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton

class Sidebar(QWidget):
    def __init__(self, canvas):
        super().__init__()
        self.canvas = canvas
        layout = QVBoxLayout()

        btn_add = QPushButton("➕ Add Node")
        btn_add.clicked.connect(self.canvas.enable_add_node_mode)

        layout.addWidget(btn_add)
        layout.addWidget(QPushButton("❌ Remove Node"))
        layout.addWidget(QPushButton("📐 Run Prim’s"))
        layout.addWidget(QPushButton("🚰 Simulate Flow"))
        layout.addWidget(QPushButton("📊 Show Graphs"))
        layout.addWidget(QPushButton("📤 Export Results"))

        layout.addStretch()
        self.setLayout(layout)
