from PySide6.QtCore import Qt, QRect, QPoint, Signal
from PySide6.QtGui import QMouseEvent, QPainter, QColor, QBrush, QPen, QFont, QCursor, QGuiApplication
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton


_RESIZE_MARGIN = 8


class CountdownWidget(QWidget):
    settings_clicked = Signal()
    start_clicked = Signal()
    pause_clicked = Signal()
    stop_clicked = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._drag_pos = None
        self._resize_edge = 0
        self._remaining = 0
        self._is_work = True
        self._is_running = False
        self._state_text = "待机"

        self.setWindowFlags(
            Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool
        )
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setMinimumSize(160, 80)
        self.resize(280, 180)

        self._init_ui()
        self._position_bottom_right()

    def _position_bottom_right(self):
        screen = QGuiApplication.primaryScreen().geometry()
        size = self.frameGeometry()
        pos_x = screen.right() - self.width() - 10
        pos_y = screen.bottom() - self.height() - 10
        self.move(pos_x, pos_y)

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 10, 14, 12)
        layout.setSpacing(6)

        top_bar = QHBoxLayout()
        top_bar.setContentsMargins(0, 0, 0, 0)

        self._status_label = QLabel(self._state_text)
        self._status_label.setStyleSheet("color: rgba(255,255,255,180); font-size: 13px;")
        top_bar.addWidget(self._status_label)

        top_bar.addStretch()

        self._settings_btn = QPushButton("⚙")
        self._settings_btn.setFixedSize(24, 24)
        self._settings_btn.setStyleSheet("""
            QPushButton {
                background: rgba(60,60,60,180);
                color: white;
                border: none;
                border-radius: 12px;
                font-size: 13px;
            }
            QPushButton:hover {
                background: rgba(80,80,80,200);
            }
        """)
        self._settings_btn.setCursor(QCursor(Qt.ArrowCursor))
        self._settings_btn.clicked.connect(self.settings_clicked.emit)
        top_bar.addWidget(self._settings_btn)

        close_btn = QPushButton("✕")
        close_btn.setFixedSize(24, 24)
        close_btn.setStyleSheet("""
            QPushButton {
                background: rgba(255,80,80,150);
                color: white;
                border: none;
                border-radius: 12px;
                font-size: 11px;
            }
            QPushButton:hover {
                background: rgba(255,50,50,200);
            }
        """)
        close_btn.setCursor(QCursor(Qt.ArrowCursor))
        close_btn.clicked.connect(self.hide)
        top_bar.addWidget(close_btn)

        layout.addLayout(top_bar)

        self._time_label = QLabel("20:00")
        self._time_label.setAlignment(Qt.AlignCenter)
        self._time_label.setStyleSheet("color: white; font-size: 44px; font-weight: bold;")
        layout.addWidget(self._time_label)

        self._progress_label = QLabel("")
        self._progress_label.setAlignment(Qt.AlignCenter)
        self._progress_label.setStyleSheet("color: rgba(255,255,255,120); font-size: 10px;")
        layout.addWidget(self._progress_label)

        control_bar = QHBoxLayout()
        control_bar.setContentsMargins(0, 0, 0, 0)
        control_bar.setSpacing(6)

        self._start_btn = QPushButton("开始")
        self._start_btn.setFixedHeight(28)
        self._start_btn.setStyleSheet("""
            QPushButton {
                background: rgba(0,120,212,180);
                color: white;
                border: none;
                border-radius: 14px;
                font-size: 12px;
            }
            QPushButton:hover {
                background: rgba(0,140,232,200);
            }
        """)
        self._start_btn.setCursor(QCursor(Qt.ArrowCursor))
        self._start_btn.clicked.connect(self._on_start_pause_click)
        control_bar.addWidget(self._start_btn)

        self._stop_btn = QPushButton("停止")
        self._stop_btn.setFixedHeight(28)
        self._stop_btn.setStyleSheet("""
            QPushButton {
                background: rgba(60,60,60,180);
                color: white;
                border: none;
                border-radius: 14px;
                font-size: 12px;
            }
            QPushButton:hover {
                background: rgba(80,80,80,200);
            }
        """)
        self._stop_btn.setCursor(QCursor(Qt.ArrowCursor))
        self._stop_btn.clicked.connect(self.stop_clicked.emit)
        control_bar.addWidget(self._stop_btn)

        layout.addLayout(control_bar)

    def _on_start_pause_click(self):
        if self._is_running:
            self.pause_clicked.emit()
        else:
            self.start_clicked.emit()

    def set_running_state(self, is_running: bool):
        self._is_running = is_running
        if is_running:
            self._start_btn.setText("暂停")
            self._status_label.setText(self._state_text + " (运行中)")
        else:
            self._start_btn.setText("开始")
            if self._state_text == "休息倒计时":
                self._status_label.setText("休息中")
            elif self._state_text == "工作倒计时":
                self._status_label.setText("工作中")
            else:
                self._status_label.setText(self._state_text)

    def update_time(self, remaining_seconds: int, total_seconds: int, is_work: bool):
        self._remaining = remaining_seconds
        self._is_work = is_work
        minutes = remaining_seconds // 60
        seconds = remaining_seconds % 60
        self._time_label.setText(f"{minutes:02d}:{seconds:02d}")

        if remaining_seconds <= 60 and remaining_seconds > 0:
            self._time_label.setStyleSheet("color: #ff4747; font-size: 44px; font-weight: bold;")
        else:
            self._time_label.setStyleSheet("color: white; font-size: 44px; font-weight: bold;")

        if is_work:
            self._state_text = "工作倒计时"
            progress = (total_seconds - remaining_seconds) / total_seconds * 100 if total_seconds > 0 else 0
            self._progress_label.setText(f"已工作 {int(progress)}%")
        else:
            self._state_text = "休息倒计时"
            progress = (total_seconds - remaining_seconds) / total_seconds * 100 if total_seconds > 0 else 0
            self._progress_label.setText(f"已休息 {int(progress)}%")

        if self._is_running:
            self._status_label.setText(self._state_text + " (运行中)")
        else:
            self._status_label.setText(self._state_text)

        self.update()

    def set_idle_state(self):
        self._state_text = "待机"
        self._remaining = 0
        self._time_label.setText("20:00")
        self._progress_label.setText("")
        self._status_label.setText(self._state_text)
        self._start_btn.setText("开始")

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        rect = self.rect()
        bg_color = QColor(30, 30, 35, 220)
        painter.setBrush(QBrush(bg_color))
        painter.setPen(QPen(QColor(100, 100, 120, 100)))
        painter.drawRoundedRect(rect.adjusted(1, 1, -1, -1), 14, 14)

    def _get_resize_edge(self, pos: QPoint) -> int:
        edge = 0
        r = self.rect()
        if pos.x() < _RESIZE_MARGIN:
            edge |= Qt.LeftEdge
        if pos.x() > r.width() - _RESIZE_MARGIN:
            edge |= Qt.RightEdge
        if pos.y() < _RESIZE_MARGIN:
            edge |= Qt.TopEdge
        if pos.y() > r.height() - _RESIZE_MARGIN:
            edge |= Qt.BottomEdge
        return edge

    def _update_cursor(self, edge: int):
        if edge in (Qt.LeftEdge | Qt.TopEdge, Qt.RightEdge | Qt.BottomEdge):
            self.setCursor(QCursor(Qt.SizeFDiagCursor))
        elif edge in (Qt.RightEdge | Qt.TopEdge, Qt.LeftEdge | Qt.BottomEdge):
            self.setCursor(QCursor(Qt.SizeBDiagCursor))
        elif edge in (Qt.LeftEdge, Qt.RightEdge):
            self.setCursor(QCursor(Qt.SizeHorCursor))
        elif edge in (Qt.TopEdge, Qt.BottomEdge):
            self.setCursor(QCursor(Qt.SizeVerCursor))
        else:
            self.setCursor(QCursor(Qt.OpenHandCursor))

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            edge = self._get_resize_edge(event.position().toPoint())
            if edge:
                self._resize_edge = edge
                self._drag_pos = event.position().toPoint()
                self.setCursor(QCursor(Qt.ClosedHandCursor))
            else:
                self._resize_edge = 0
                self._drag_pos = event.position().toPoint()
                self.setCursor(QCursor(Qt.ClosedHandCursor))

    def mouseMoveEvent(self, event: QMouseEvent):
        if self._drag_pos is None:
            edge = self._get_resize_edge(event.position().toPoint())
            self._update_cursor(edge)
            return

        delta = event.position().toPoint() - self._drag_pos
        pos = self.pos()

        if self._resize_edge:
            new_rect = QRect(pos, self.size())
            if self._resize_edge & Qt.LeftEdge:
                new_rect.setLeft(new_rect.left() + delta.x())
            if self._resize_edge & Qt.RightEdge:
                new_rect.setRight(new_rect.right() + delta.x())
            if self._resize_edge & Qt.TopEdge:
                new_rect.setTop(new_rect.top() + delta.y())
            if self._resize_edge & Qt.BottomEdge:
                new_rect.setBottom(new_rect.bottom() + delta.y())

            if new_rect.width() >= self.minimumWidth() and new_rect.height() >= self.minimumHeight():
                self.setGeometry(new_rect)
                self._drag_pos = event.position().toPoint()
        else:
            self.move(pos + delta)

    def mouseReleaseEvent(self, event: QMouseEvent):
        self._drag_pos = None
        self._resize_edge = 0
        self.setCursor(QCursor(Qt.OpenHandCursor))