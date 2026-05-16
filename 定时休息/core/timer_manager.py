from enum import Enum, auto
from PySide6.QtCore import QObject, QTimer, Signal, QElapsedTimer


class TimerState(Enum):
    IDLE = auto()
    WORKING = auto()
    LOCKED = auto()
    BREAK_DONE = auto()


class TimerManager(QObject):
    state_changed = Signal(TimerState)
    time_updated = Signal(int, int, bool)
    work_finished = Signal()
    break_finished = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._work_duration = 20 * 60
        self._break_duration = 5 * 60
        self._state = TimerState.IDLE
        self._remaining = 0
        self._timer = QTimer(self)
        self._timer.setInterval(1000)
        self._timer.timeout.connect(self._on_tick)
        self._elapsed_timer = QElapsedTimer()

    @property
    def state(self):
        return self._state

    @property
    def work_duration(self):
        return self._work_duration

    @work_duration.setter
    def work_duration(self, seconds: int):
        self._work_duration = max(1, seconds)

    @property
    def break_duration(self):
        return self._break_duration

    @break_duration.setter
    def break_duration(self, seconds: int):
        self._break_duration = max(1, seconds)

    @property
    def remaining(self):
        return self._remaining

    def start_work(self):
        if self._state == TimerState.IDLE:
            self._remaining = self._work_duration
            self._set_state(TimerState.WORKING)
            self._timer.start()
            self._emit_time()

    def stop(self):
        if self._state != TimerState.IDLE:
            self._timer.stop()
            self._set_state(TimerState.IDLE)
            self._remaining = 0
            self._emit_time()

    def pause(self):
        if self._state == TimerState.WORKING:
            self._timer.stop()
            self._set_state(TimerState.IDLE)

    def start_break(self):
        self._remaining = self._break_duration
        self._set_state(TimerState.LOCKED)
        self._timer.start()
        self._emit_time()

    def _on_tick(self):
        if self._state == TimerState.WORKING:
            self._remaining -= 1
            self._emit_time()
            if self._remaining <= 0:
                self._timer.stop()
                self._remaining = 0
                self._emit_time()
                self.work_finished.emit()

        elif self._state == TimerState.LOCKED:
            self._remaining -= 1
            self._emit_time()
            if self._remaining <= 0:
                self._timer.stop()
                self._remaining = 0
                self._emit_time()
                self._set_state(TimerState.BREAK_DONE)
                self.break_finished.emit()

    def _set_state(self, state: TimerState):
        self._state = state
        self.state_changed.emit(state)

    def _emit_time(self):
        if self._state == TimerState.WORKING:
            self.time_updated.emit(self._remaining, self._work_duration, True)
        elif self._state == TimerState.LOCKED:
            self.time_updated.emit(self._remaining, self._break_duration, False)
        else:
            self.time_updated.emit(0, 0, True)