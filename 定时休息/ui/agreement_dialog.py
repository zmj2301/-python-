from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QTextEdit
)


_AGREEMENT_TEXT = """
【定时休息】软件用户许可协议

版本日期：2026年5月16日

重要提示：请仔细阅读本协议全部内容。如果您不同意本协议的任何条款，请不要使用本软件。使用本软件即表示您已阅读并同意接受本协议的所有条款。

一、软件功能
本软件为定时休息工具，帮助用户定时休息，保护身体健康。

二、用户义务
1. 用户应合理安排工作和休息时间，遵守软件提醒的休息时间。
2. 本软件仅作为辅助工具，用户自愿使用。

三、特殊情况免责条款
★★★★★
重要提醒：

1. 在休息锁定期间，本软件会锁定计算机。如遇以下特殊情况，用户同意：

(1) 若休息锁定期间，用户可能无法正常解锁；
(2) 若软件锁定期间，用户无法正常使用计算机；
(3) 若软件异常导致任何问题；

★★★如遇上述情况无法解决，用户同意：
   - 方法一：等待休息时间结束；
   - 方法二：重启计算机（强制关机重启）；

四、免责声明
1. 本软件按"现状"提供，不提供任何明示或暗示的保证；
2. 软件作者不对因使用或无法使用本软件导致的任何损失承担责任；
3. 软件作者不对软件任何间接、偶然、特殊或惩罚性损害承担责任；

五、协议修改
软件作者有权随时修改本协议条款。

六、协议终止
如用户违反本协议任何条款，软件作者有权终止本协议。

七、法律适用
本协议适用中华人民共和国法律。

=========================
特别注意：使用本软件即表示理解并同意上述所有条款。
"""


class AgreementDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("定时休息 - 用户许可协议")
        self.setMinimumSize(560, 520)
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(18)

        title_label = QLabel("【定时休息】用户许可协议")
        title_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #2d7dd2;")
        layout.addWidget(title_label)

        hint_label = QLabel("请仔细阅读以下协议，然后选择【同意】或【拒绝】")
        hint_label.setStyleSheet("color: #666; font-size: 14px;")
        layout.addWidget(hint_label)

        text_edit = QTextEdit()
        text_edit.setReadOnly(True)
        text_edit.setPlainText(_AGREEMENT_TEXT)
        text_edit.setStyleSheet("""
            QTextEdit {
                background: #fafafa;
                border: 1px solid #d0d0d0;
                border-radius: 8px;
                padding: 14px;
                font-size: 13px;
                line-height: 1.7;
                selection-background-color: #4a90e2;
            }
        """)
        layout.addWidget(text_edit, 1)

        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(16)

        self._reject_btn = QPushButton("拒绝")
        self._reject_btn.setFixedHeight(40)
        self._reject_btn.setMinimumWidth(120)
        self._reject_btn.setStyleSheet("""
            QPushButton {
                background: #f0f0f0;
                color: #555;
                border: 1px solid #ccc;
                border-radius: 8px;
                padding: 8px 32px;
                font-size: 14px;
            }
            QPushButton:hover {
                background: #e0e0e0;
                border-color: #aaa;
            }
            QPushButton:pressed {
                background: #d0d0d0;
            }
        """)
        self._reject_btn.clicked.connect(self.reject)
        btn_layout.addWidget(self._reject_btn)

        btn_layout.addStretch()

        self._accept_btn = QPushButton("同意")
        self._accept_btn.setFixedHeight(40)
        self._accept_btn.setMinimumWidth(120)
        self._accept_btn.setStyleSheet("""
            QPushButton {
                background: #2d7dd2;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 8px 32px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #1f6aa5;
            }
            QPushButton:pressed {
                background: #185787;
            }
        """)
        self._accept_btn.clicked.connect(self.accept)
        btn_layout.addWidget(self._accept_btn)

        layout.addLayout(btn_layout)

        self.setStyleSheet("""
            QDialog {
                background: #f5f5f5;
            }
        """)
