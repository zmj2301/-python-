import sys
import ctypes
import threading
import time
from PySide6.QtCore import Qt, QTimer, QSettings, QObject, Signal
from PySide6.QtWidgets import QApplication, QDialog, QMessageBox

from core.logger import logger
from core.timer_manager import TimerManager, TimerState
from ui.countdown_widget import CountdownWidget
from ui.settings_dialog import SettingsDialog
from ui.agreement_dialog import AgreementDialog


_USER32 = ctypes.windll.user32
_WTSAPI32 = ctypes.windll.wtsapi32

WTS_CURRENT_SERVER_HANDLE = 0
WTS_CURRENT_SESSION = 0xFFFFFFFF

_LockWorkStation = _USER32.LockWorkStation


def _lock_screen():
    logger.info("调用Windows API锁定屏幕")
    _LockWorkStation()


class SessionMonitor(QObject):
    session_unlocked = Signal()

    def __init__(self):
        super().__init__()
        self._running = True
        self._last_locked = False
        self._poll_thread = None

    def _is_desktop_locked(self):
        try:
            hdesk = _USER32.OpenInputDesktop(0, False, 0x0100)
            if hdesk:
                _USER32.CloseDesktop(hdesk)
                return False
            return True
        except Exception:
            return True

    def _check_loop(self):
        while self._running:
            try:
                is_locked = self._is_desktop_locked()
                if self._last_locked and not is_locked:
                    logger.warning("检测到桌面解锁事件")
                    self.session_unlocked.emit()
                self._last_locked = is_locked
            except Exception as e:
                logger.warning(f"会话监控循环异常: {e}")
            finally:
                time.sleep(0.1)

    def start(self):
        if self._poll_thread is not None:
            return
        self._last_locked = self._is_desktop_locked()
        self._poll_thread = threading.Thread(target=self._check_loop, daemon=True)
        self._poll_thread.start()
        logger.info("会话监控已启动 (OpenInputDesktop 方式)")

    def stop(self):
        self._running = False


class App(QApplication):
    def __init__(self, argv):
        super().__init__(argv)
        logger.info("初始化App...")
        self.setApplicationName("定时休息")
        self.setQuitOnLastWindowClosed(False)

        self._settings = QSettings("CodersLife", "定时休息")

        self._timer_mgr = TimerManager()
        self._read_settings()

        self._session_monitor = SessionMonitor()
        self._session_monitor.session_unlocked.connect(self._on_session_unlocked)

        self._countdown_widget = CountdownWidget()

        self._connect_signals()

        self._session_monitor.start()

        if not self._show_agreement():
            logger.info("用户未同意协议，退出应用")
            return

        logger.info("显示倒计时窗口")
        self._countdown_widget.show()
        self._countdown_widget.raise_()
        self._countdown_widget.activateWindow()
        self._countdown_widget.set_idle_state()

    def _show_agreement(self):
        logger.info("显示用户协议对话框")
        dlg = AgreementDialog()
        result = dlg.exec()
        if result == QDialog.DialogCode.Accepted:
            logger.info("用户已同意协议")
            return True
        else:
            logger.info("用户未同意协议")
            return False

    def _read_settings(self):
        work = self._settings.value("work_minutes", 20, type=int)
        break_ = self._settings.value("break_minutes", 5, type=int)
        logger.info(f"读取设置: 工作={work}分钟, 休息={break_}分钟")
        self._timer_mgr.work_duration = work * 60
        self._timer_mgr.break_duration = break_ * 60

    def _save_settings(self, work_minutes: int, break_minutes: int):
        logger.info(f"保存设置: 工作={work_minutes}分钟, 休息={break_minutes}分钟")
        self._settings.setValue("work_minutes", work_minutes)
        self._settings.setValue("break_minutes", break_minutes)

    def _connect_signals(self):
        logger.debug("连接信号...")
        self._timer_mgr.state_changed.connect(self._on_state_changed)
        self._timer_mgr.time_updated.connect(self._countdown_widget.update_time)
        self._timer_mgr.work_finished.connect(self._on_work_finished)
        self._timer_mgr.break_finished.connect(self._on_break_finished)

        self._countdown_widget.settings_clicked.connect(self._show_settings)
        self._countdown_widget.start_clicked.connect(self._on_start_clicked)
        self._countdown_widget.pause_clicked.connect(self._on_pause_clicked)
        self._countdown_widget.stop_clicked.connect(self._on_stop_clicked)

        logger.debug("信号连接完成")

    def _on_state_changed(self, state: TimerState):
        logger.info(f"状态改变: {state}")
        if state == TimerState.WORKING:
            self._countdown_widget.set_running_state(True)
        elif state == TimerState.LOCKED:
            self._countdown_widget.set_running_state(True)
            self._countdown_widget.show()
        elif state == TimerState.IDLE:
            self._countdown_widget.set_running_state(False)
            self._countdown_widget.set_idle_state()

    def _on_start_clicked(self):
        logger.info("用户点击开始")
        state = self._timer_mgr.state
        if state == TimerState.IDLE:
            self._timer_mgr.start_work()
            self._countdown_widget.set_running_state(True)
        elif state == TimerState.BREAK_DONE:
            self._timer_mgr.start_work()
            self._countdown_widget.set_running_state(True)

    def _on_pause_clicked(self):
        logger.info("用户点击暂停")
        self._timer_mgr.pause()
        self._countdown_widget.set_running_state(False)

    def _on_stop_clicked(self):
        logger.info("用户点击停止")
        self._timer_mgr.stop()
        self._countdown_widget.set_running_state(False)
        self._countdown_widget.set_idle_state()

    def _show_settings(self):
        logger.debug("显示设置对话框")
        work_min = self._timer_mgr.work_duration // 60
        break_min = self._timer_mgr.break_duration // 60
        dlg = SettingsDialog(work_min, break_min, self._countdown_widget)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            logger.debug("设置被用户接受")
            self._timer_mgr.work_duration = dlg.work_minutes * 60
            self._timer_mgr.break_duration = dlg.break_minutes * 60
            self._save_settings(dlg.work_minutes, dlg.break_minutes)

    def _on_work_finished(self):
        logger.info("工作时间结束")
        self._countdown_widget.set_running_state(False)
        _lock_screen()
        QTimer.singleShot(2000, self._timer_mgr.start_break)

    def _on_break_finished(self):
        logger.info("休息时间结束")
        QMessageBox.information(
            self._countdown_widget,
            "休息结束",
            "休息时间已结束，现在可以继续工作了！",
            QMessageBox.Ok
        )

    def _on_session_unlocked(self):
        state = self._timer_mgr.state
        logger.warning(f"检测到会话解锁事件，当前状态: {state}")
        if state == TimerState.LOCKED:
            logger.warning("休息期间强制解锁，立即重新锁屏！")
            QTimer.singleShot(100, _lock_screen)