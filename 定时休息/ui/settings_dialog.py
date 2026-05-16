from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QSpinBox, QPushButton, QWidget, QDialogButtonBox
)


class SettingsDialog(QDialog):
    def __init__(self, work_minutes: int, break_minutes: int, parent=None):
        super().__init__(parent)
        self.setWindowTitle("定时休息设置")
        self.setFixedSize(320, 200)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)

        self._work_minutes = work_minutes
        self._break_minutes = break_minutes
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(24, 20, 24, 20)

        layout.addStretch()

        work_row = QHBoxLayout()
        work_row.setSpacing(12)
        work_label = QLabel("工作时长（分钟）：")
        self._work_spin = QSpinBox()
        self._work_spin.setRange(1, 999)
        self._work_spin.setValue(self._work_minutes)
        self._work_spin.setFixedWidth(100)
        work_row.addWidget(work_label)
        work_row.addWidget(self._work_spin)
        work_row.addStretch()
        layout.addLayout(work_row)

        break_row = QHBoxLayout()
        break_row.setSpacing(12)
        break_label = QLabel("休息时长（分钟）：")
        self._break_spin = QSpinBox()
        self._break_spin.setRange(1, 999)
        self._break_spin.setValue(self._break_minutes)
        self._break_spin.setFixedWidth(100)
        break_row.addWidget(break_label)
        break_row.addWidget(self._break_spin)
        break_row.addStretch()
        layout.addLayout(break_row)

        layout.addStretch()

        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(12)
        cancel_btn = QPushButton("取消")
        cancel_btn.clicked.connect(self.reject)
        ok_btn = QPushButton("确定")
        ok_btn.setDefault(True)
        ok_btn.clicked.connect(self.accept)
        btn_layout.addStretch()
        btn_layout.addWidget(cancel_btn)
        btn_layout.addWidget(ok_btn)
        layout.addLayout(btn_layout)

        self.setStyleSheet("""
            QDialog {
                background: #2d2d30;
                color: #e0e0e0;
            }
            QLabel {
                color: #e0e0e0;
                font-size: 14px;
            }
            QSpinBox {
                background: #3c3c3c;
                color: white;
                border: 1px solid #555;
                border-radius: 4px;
                padding: 4px 8px;
                font-size: 14px;
            }
            QSpinBox:focus {
                border-color: #0078d4;
            }
            QPushButton {
                background: #3c3c3c;
                color: #e0e0e0;
                border: 1px solid #555;
                border-radius: 4px;
                padding: 6px 20px;
                font-size: 13px;
                min-width: 60px;
            }
            QPushButton:hover {
                background: #505050;
            }
            QPushButton[default="true"] {
                background: #0078d4;
                border-color: #0078d4;
                color: white;
            }
            QPushButton[default="true"]:hover {
                background: #1a8ad4;
            }
        """)

    @property
    def work_minutes(self) -> int:
        return self._work_spin.value()

    @property
    def break_minutes(self) -> int:
        return self._break_spin.value()