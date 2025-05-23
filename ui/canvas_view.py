from PyQt6.QtWidgets import QWidget, QLabel, QToolTip, QFileDialog, QMessageBox
from PyQt6.QtGui import QPainter, QPen, QBrush, QColor, QFont, QMouseEvent, QCursor, QPixmap
from PyQt6.QtCore import Qt, QPointF, QRectF
import math
from core.prim import compute_mst
from core.simulation import simulate_water_flow
from visual.plotter import show_plots
import json
import os

NODE_RADIUS = 28

class Node:
    def __init__(self, pos, label, is_source=False):
        self.pos = QPointF(pos)
        self.label = label
        self.is_source = is_source
        self.selected = False
        self.dragging = False

class Edge:
    def __init__(self, n1_idx, n2_idx, length):
        self.n1_idx = n1_idx
        self.n2_idx = n2_idx
        self.length = length
        self.is_mst = False

class CanvasView(QWidget):
    def __init__(self, sidebar):
        super().__init__()
        self.sidebar = sidebar
        self.setMouseTracking(True)
        self.setMinimumSize(900, 700)
        self.nodes = []
        self.edges = []
        self.mode = None
        self.selected_nodes = []
        self.dragged_node_idx = None
        self.mst_edges = []
        self.sim_results = None
        # Pan/zoom state
        self.pan_offset = QPointF(0, 0)
        self.zoom_factor = 1.0
        self._last_pan_pos = None
        # Grid state
        self.grid_enabled = False
        # Tooltip state
        self._last_tooltip_node = None
        # Icons (use absolute path)
        base_dir = os.path.dirname(os.path.abspath(__file__))
        self.house_icon = QPixmap(os.path.join(base_dir, '../icons/housee.png'))
        self.source_icon = QPixmap(os.path.join(base_dir, '../icons/source.png'))

    def set_mode(self, mode):
        self.mode = mode
        self.selected_nodes = []
        self.dragged_node_idx = None
        self._last_pan_pos = None
        self.update()

    def mousePressEvent(self, event: QMouseEvent):
        pos = event.position()
        if self.mode == "add_node":
            self.add_node(self.map_to_scene(pos))
        elif self.mode == "connect":
            idx = self.get_node_at(self.map_to_scene(pos))
            if idx is not None:
                if idx not in self.selected_nodes:
                    self.selected_nodes.append(idx)
                if len(self.selected_nodes) == 2:
                    self.add_edge(self.selected_nodes[0], self.selected_nodes[1])
                    self.selected_nodes = []
        elif self.mode == "remove_node":
            idx = self.get_node_at(self.map_to_scene(pos))
            if idx is not None:
                self.remove_node_at(idx)
        elif self.mode == "disconnect_edge":
            edge_idx = self.get_edge_at(self.map_to_scene(pos))
            if edge_idx is not None:
                self.disconnect_edge_at(edge_idx)
        elif self.mode == "move_node":
            idx = self.get_node_at(self.map_to_scene(pos))
            if idx is not None:
                self.dragged_node_idx = idx
                self.nodes[idx].dragging = True
                self.setCursor(QCursor(Qt.CursorShape.ClosedHandCursor))
        elif self.mode == "pan_zoom":
            self._last_pan_pos = event.position()
            self.setCursor(QCursor(Qt.CursorShape.OpenHandCursor))
        self.update()

    def mouseMoveEvent(self, event: QMouseEvent):
        pos = event.position()
        scene_pos = self.map_to_scene(pos)
        # Tooltip logic
        node_idx = self.get_node_at(scene_pos)
        if node_idx is not None:
            node = self.nodes[node_idx]
            details = f"<b>{node.label}</b>"
            if self.sim_results and node_idx in self.sim_results:
                t, p = self.sim_results[node_idx]
                details += f"<br>Time: {t:.2f}<br>Pressure: {p:.2f}"
            QToolTip.showText(event.globalPosition().toPoint(), details, self)
            self._last_tooltip_node = node_idx
        else:
            if self._last_tooltip_node is not None:
                QToolTip.hideText()
                self._last_tooltip_node = None
        if self.mode == "move_node" and self.dragged_node_idx is not None:
            self.nodes[self.dragged_node_idx].pos = scene_pos
            # Update lengths of all edges connected to the moved node
            for edge in self.edges:
                if edge.n1_idx == self.dragged_node_idx or edge.n2_idx == self.dragged_node_idx:
                    n1 = self.nodes[edge.n1_idx]
                    n2 = self.nodes[edge.n2_idx]
                    edge.length = math.hypot(n1.pos.x() - n2.pos.x(), n1.pos.y() - n2.pos.y())
            self.update()
        elif self.mode == "pan_zoom" and self._last_pan_pos is not None:
            delta = event.position() - self._last_pan_pos
            self.pan_offset += delta
            self._last_pan_pos = event.position()
            self.update()

    def mouseReleaseEvent(self, event: QMouseEvent):
        if self.mode == "move_node" and self.dragged_node_idx is not None:
            self.nodes[self.dragged_node_idx].dragging = False
            self.dragged_node_idx = None
            self.setCursor(QCursor(Qt.CursorShape.ArrowCursor))
            self.update()
        elif self.mode == "pan_zoom" and self._last_pan_pos is not None:
            self._last_pan_pos = None
            self.setCursor(QCursor(Qt.CursorShape.ArrowCursor))
            self.update()

    def wheelEvent(self, event):
        if self.mode == "pan_zoom":
            angle = event.angleDelta().y()
            factor = 1.2 if angle > 0 else 1/1.2
            self.zoom(factor, event.position())

    def zoom(self, factor, center=None):
        # Zoom relative to a point (center), default is widget center
        old_zoom = self.zoom_factor
        self.zoom_factor *= factor
        if self.zoom_factor < 0.2:
            self.zoom_factor = 0.2
        if self.zoom_factor > 5.0:
            self.zoom_factor = 5.0
        if center is None:
            center = QPointF(self.width()/2, self.height()/2)
        # Adjust pan so that zoom is centered on the mouse position
        offset_to_center = center - self.pan_offset
        self.pan_offset += offset_to_center * (1 - factor)
        self.update()

    def map_to_scene(self, pos):
        # Map from widget coordinates to scene coordinates
        return (pos - self.pan_offset) / self.zoom_factor

    def map_from_scene(self, pos):
        # Map from scene coordinates to widget coordinates
        return pos * self.zoom_factor + self.pan_offset

    def get_node_at(self, pos):
        for idx, node in enumerate(self.nodes):
            if (node.pos - pos).manhattanLength() <= NODE_RADIUS + 4:
                return idx
        return None

    def get_edge_at(self, pos):
        for idx, edge in enumerate(self.edges):
            n1 = self.nodes[edge.n1_idx]
            n2 = self.nodes[edge.n2_idx]
            # Distance from point to line segment
            p1, p2 = n1.pos, n2.pos
            line_vec = p2 - p1
            point_vec = pos - p1
            line_len = math.hypot(line_vec.x(), line_vec.y())
            if line_len == 0:
                continue
            t = max(0, min(1, (point_vec.x() * line_vec.x() + point_vec.y() * line_vec.y()) / (line_len ** 2)))
            proj = p1 + t * line_vec
            dist = (proj - pos).manhattanLength()
            if dist <= 10:  # 10px tolerance
                return idx
        return None

    def add_node(self, pos):
        if len(self.nodes) == 0:
            label = "Source"
            is_source = True
        else:
            if any(n.is_source for n in self.nodes):
                label = f"House {len(self.nodes)}"
                is_source = False
            else:
                label = "Source"
                is_source = True
        if is_source and any(n.is_source for n in self.nodes):
            self.sidebar.set_result("Only one Source node allowed.")
            return
        node = Node(pos, label, is_source)
        self.nodes.append(node)
        self.sidebar.set_result(f"Added node: {label}")
        self.update()

    def add_edge(self, idx1, idx2):
        if idx1 == idx2:
            self.sidebar.set_result("Cannot connect node to itself.")
            return
        if any((e.n1_idx == idx1 and e.n2_idx == idx2) or (e.n1_idx == idx2 and e.n2_idx == idx1) for e in self.edges):
            self.sidebar.set_result("Edge already exists.")
            return
        n1 = self.nodes[idx1]
        n2 = self.nodes[idx2]
        length = math.hypot(n1.pos.x() - n2.pos.x(), n1.pos.y() - n2.pos.y())
        edge = Edge(idx1, idx2, length)
        self.edges.append(edge)
        self.sidebar.set_result(f"Connected {n1.label} ↔ {n2.label}")
        self.update()

    def run_prim(self):
        if not self.nodes or not self.edges:
            self.show_error("Add and connect nodes before running Prim's algorithm.")
            self.sidebar.set_result("Add nodes and connect them first.")
            return
        G, edge_map = self._to_networkx()
        mst = compute_mst(G)
        self.mst_edges = []
        for u, v in mst.edges():
            idx = edge_map.get(frozenset([u, v]))
            if idx is not None:
                self.edges[idx].is_mst = True
                self.mst_edges.append(idx)
        for i, e in enumerate(self.edges):
            if i not in self.mst_edges:
                e.is_mst = False
        self.sidebar.set_result("Prim's MST computed and highlighted.")
        self.update()

    def simulate_flow(self, initial_pressure, flow_rate):
        if not self.nodes or not self.edges:
            self.show_error("Add and connect nodes before running simulation.")
            self.sidebar.set_result("Add nodes and connect them first.")
            return
        if not any(n.is_source for n in self.nodes):
            self.show_error("Add a Source node before running simulation.")
            self.sidebar.set_result("Add a Source node first.")
            return
        if not any(e.is_mst for e in self.edges):
            self.show_error("Run Prim's algorithm before running simulation.")
            self.sidebar.set_result("Run Prim's algorithm first.")
            return
        G, edge_map = self._to_networkx(mst_only=True)
        source_idx = next(i for i, n in enumerate(self.nodes) if n.is_source)
        results = simulate_water_flow(G, source_idx, initial_pressure, flow_rate)
        self.sim_results = results
        text = "Simulation Results:\n"
        low_pressure = False
        not_reached = []
        for i, n in enumerate(self.nodes):
            if not n.is_source and i not in results:
                not_reached.append(n.label)
        for node_idx, (t, p) in results.items():
            label = self.nodes[node_idx].label
            text += f"{label}: Time={t:.2f}, Pressure={p:.2f}\n"
            if not self.nodes[node_idx].is_source and p < 20:
                low_pressure = True
        if not_reached:
            self.show_error(f"Not all houses are getting water: {', '.join(not_reached)}")
        elif low_pressure:
            self.show_error("Low pressure detected in one or more houses.")
        self.sidebar.set_result(text)
        self.update()

    def show_graphs(self):
        if not self.sim_results:
            self.sidebar.set_result("Run simulation first.")
            return
        labels = [self.nodes[i].label for i in self.sim_results.keys()]
        times = [self.sim_results[i][0] for i in self.sim_results.keys()]
        pressures = [self.sim_results[i][1] for i in self.sim_results.keys()]
        show_plots(labels, times, pressures)

    def _to_networkx(self, mst_only=False):
        import networkx as nx
        G = nx.Graph()
        for i, n in enumerate(self.nodes):
            G.add_node(i)
        edge_map = {}
        for idx, e in enumerate(self.edges):
            if mst_only and not e.is_mst:
                continue
            G.add_edge(e.n1_idx, e.n2_idx, weight=e.length)
            edge_map[frozenset([e.n1_idx, e.n2_idx])] = idx
        return G, edge_map

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.save()
        painter.translate(self.pan_offset)
        painter.scale(self.zoom_factor, self.zoom_factor)
        if self.grid_enabled:
            self._draw_grid(painter)
        self._draw_edges(painter)
        self._draw_nodes(painter)
        painter.restore()

    def _draw_edges(self, painter):
        font = QFont("Arial", 12)
        for idx, edge in enumerate(self.edges):
            n1 = self.nodes[edge.n1_idx]
            n2 = self.nodes[edge.n2_idx]
            p1, p2 = n1.pos, n2.pos
            # Edge style
            if self.sim_results and edge.is_mst:
                p1_val = self.sim_results.get(edge.n1_idx, (None, 0))[1]
                p2_val = self.sim_results.get(edge.n2_idx, (None, 0))[1]
                if p1_val > 0 and p2_val > 0:
                    pen = QPen(QColor(64, 156, 255), 4)  # Blue for water flow
                else:
                    pen = QPen(QColor(120, 120, 120), 2, Qt.PenStyle.DashLine)
            elif edge.is_mst:
                pen = QPen(QColor(255, 64, 64), 4)
            else:
                pen = QPen(QColor(120, 120, 120), 2, Qt.PenStyle.DashLine)
            painter.setPen(pen)
            painter.drawLine(p1, p2)
            # Draw length
            mid = QPointF((p1.x() + p2.x()) / 2, (p1.y() + p2.y()) / 2)
            painter.setFont(font)
            painter.setPen(QColor(255, 255, 255))
            painter.drawText(mid + QPointF(0, -8), f"{edge.length:.1f}")

    def _draw_nodes(self, painter):
        font = QFont("Arial", 13, QFont.Weight.Bold)
        for idx, node in enumerate(self.nodes):
            # Node color
            if self.sim_results and idx in self.sim_results and self.sim_results[idx][1] == 0:
                color = QColor(120, 120, 120, 180)  # Grayed out if pressure is 0
            elif self.sim_results and idx not in self.sim_results:
                color = QColor(120, 120, 120, 180)  # Grayed out if no water
            elif node.is_source:
                color = QColor(56, 183, 74)
            else:
                color = QColor(0, 188, 212)
            if node.selected or idx in self.selected_nodes:
                color = QColor(255, 215, 64)
            # Draw white background ellipse
            painter.setBrush(QBrush(QColor(255, 255, 255)))
            painter.setPen(QPen(QColor(30, 32, 38), 3))
            painter.drawEllipse(node.pos, NODE_RADIUS, NODE_RADIUS)
            # Draw icon
            if node.is_source:
                icon = self.source_icon
            else:
                icon = self.house_icon
            icon_size = NODE_RADIUS * 1.7
            icon_rect = QRectF(node.pos.x() - icon_size/2, node.pos.y() - icon_size/2, icon_size, icon_size)
            painter.drawPixmap(int(icon_rect.x()), int(icon_rect.y()), int(icon_rect.width()), int(icon_rect.height()), icon)
            # Label (drawn below the icon)
            label_font = QFont("Arial", 13, QFont.Weight.Bold)
            metrics = painter.fontMetrics()
            label_width = metrics.horizontalAdvance(node.label)
            max_width = NODE_RADIUS * 1.8
            if label_width > max_width:
                shrink_factor = max_width / label_width
                label_font.setPointSizeF(13 * shrink_factor)
            painter.setFont(label_font)
            painter.setPen(QColor(30, 32, 38))
            label_rect = QRectF(node.pos.x() - NODE_RADIUS, node.pos.y() + NODE_RADIUS * 0.9, NODE_RADIUS*2, NODE_RADIUS*0.9)
            painter.drawText(label_rect, Qt.AlignmentFlag.AlignCenter, node.label)

    def remove_node_at(self, idx):
        node = self.nodes[idx]
        # Remove all edges connected to this node
        self.edges = [e for e in self.edges if e.n1_idx != idx and e.n2_idx != idx]
        # Adjust edge indices
        for e in self.edges:
            if e.n1_idx > idx:
                e.n1_idx -= 1
            if e.n2_idx > idx:
                e.n2_idx -= 1
        label = node.label
        del self.nodes[idx]
        self.sidebar.set_result(f"Removed node: {label}")
        self.update()

    def disconnect_edge_at(self, edge_idx):
        edge = self.edges[edge_idx]
        n1 = self.nodes[edge.n1_idx]
        n2 = self.nodes[edge.n2_idx]
        del self.edges[edge_idx]
        self.sidebar.set_result(f"Disconnected {n1.label} ↔ {n2.label}")
        self.update()

    def set_grid_enabled(self, enabled):
        self.grid_enabled = enabled
        self.update()

    def _draw_grid(self, painter):
        grid_spacing = 40  # in scene coordinates
        rect = self.rect()
        # Map widget rect to scene rect
        top_left = self.map_to_scene(QPointF(0, 0))
        bottom_right = self.map_to_scene(QPointF(rect.width(), rect.height()))
        left = int(top_left.x() // grid_spacing * grid_spacing)
        right = int(bottom_right.x() // grid_spacing * grid_spacing + grid_spacing)
        top = int(top_left.y() // grid_spacing * grid_spacing)
        bottom = int(bottom_right.y() // grid_spacing * grid_spacing + grid_spacing)
        pen = QPen(QColor(80, 80, 80, 120), 1)
        painter.setPen(pen)
        # Vertical lines
        x = left
        while x <= right:
            painter.drawLine(QPointF(x, top), QPointF(x, bottom))
            x += grid_spacing
        # Horizontal lines
        y = top
        while y <= bottom:
            painter.drawLine(QPointF(left, y), QPointF(right, y))
            y += grid_spacing

    def save_map(self):
        path, _ = QFileDialog.getSaveFileName(self, "Save Map", "", "JSON Files (*.json)")
        if not path:
            return
        data = {
            'nodes': [
                {
                    'x': float(node.pos.x()),
                    'y': float(node.pos.y()),
                    'label': node.label,
                    'is_source': node.is_source
                } for node in self.nodes
            ],
            'edges': [
                {
                    'n1_idx': edge.n1_idx,
                    'n2_idx': edge.n2_idx,
                    'length': edge.length
                } for edge in self.edges
            ]
        }
        with open(path, 'w') as f:
            json.dump(data, f, indent=2)
        self.sidebar.set_result(f"Map saved to {path}")

    def load_map(self):
        path, _ = QFileDialog.getOpenFileName(self, "Load Map", "", "JSON Files (*.json)")
        if not path:
            return
        with open(path, 'r') as f:
            data = json.load(f)
        self.nodes = []
        for n in data.get('nodes', []):
            node = Node(QPointF(n['x'], n['y']), n['label'], n['is_source'])
            self.nodes.append(node)
        self.edges = []
        for e in data.get('edges', []):
            edge = Edge(e['n1_idx'], e['n2_idx'], e['length'])
            self.edges.append(edge)
        self.mst_edges = []
        self.sim_results = None
        self.sidebar.set_result(f"Map loaded from {path}")
        self.update()

    def show_error(self, message):
        QMessageBox.critical(self, "Error", message)