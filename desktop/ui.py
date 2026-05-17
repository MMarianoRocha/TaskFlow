import argparse
import os
import sys
from datetime import datetime
from typing import Any

from PySide6.QtCore import QEvent, QPoint, QSettings, Qt, QTimer
from PySide6.QtGui import QMouseEvent
from PySide6.QtWidgets import (
    QApplication,
    QCheckBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from desktop.api_client import PomodoroApiClient
from desktop.session import get_session_end, remaining_time_text, session_end_from_data


API_BASE_URL = os.getenv("POMODORO_HUB_API_URL", "http://127.0.0.1:8000")


class OverlayWindow(QWidget):
    def __init__(self):
        super().__init__(None, Qt.Window | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.settings = QSettings("PomodoroHub", "DesktopClient")
        self.locked = self.settings.value("overlay/locked", False, type=bool)
        self._drag_offset: QPoint | None = None
        self._system_move_active = False

        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_ShowWithoutActivating)
        self.setWindowFlag(Qt.WindowDoesNotAcceptFocus)
        self.setFixedSize(240, 90)

        self.label = QLabel("", self)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setStyleSheet(
            "background: rgba(0, 0, 0, 0.75); color: white; border-radius: 14px; padding: 12px;"
        )
        self.label.installEventFilter(self)

        layout = QVBoxLayout(self)
        layout.addWidget(self.label)
        layout.setContentsMargins(0, 0, 0, 0)

        self.restore_position()
        self.update_cursor()

    def move_to_corner(self, save_position: bool = True) -> None:
        screen = QApplication.primaryScreen()
        if not screen:
            return
        geometry = screen.availableGeometry()
        x = geometry.right() - self.width() - 20
        y = geometry.top() + 20
        self.move(x, y)
        if save_position:
            self.save_position()

    def restore_position(self) -> None:
        x = self.settings.value("overlay/x", None, type=int)
        y = self.settings.value("overlay/y", None, type=int)
        if x is None or y is None:
            self.move_to_corner(save_position=False)
            return

        self.move(x, y)
        self.keep_inside_screen()

    def save_position(self) -> None:
        self.settings.setValue("overlay/x", self.x())
        self.settings.setValue("overlay/y", self.y())

    def keep_inside_screen(self) -> None:
        screen = QApplication.screenAt(self.geometry().center()) or QApplication.primaryScreen()
        if not screen:
            return

        geometry = screen.availableGeometry()
        x = min(max(self.x(), geometry.left()), geometry.right() - self.width())
        y = min(max(self.y(), geometry.top()), geometry.bottom() - self.height())
        if QPoint(x, y) != self.pos():
            self.move(x, y)
            self.save_position()

    def set_locked(self, locked: bool) -> None:
        self.locked = locked
        self.settings.setValue("overlay/locked", locked)
        self.update_cursor()

    def update_cursor(self) -> None:
        cursor = Qt.ArrowCursor if self.locked else Qt.SizeAllCursor
        self.setCursor(cursor)
        self.label.setCursor(cursor)

    def update_text(self, user_name: str, countdown: str) -> None:
        self.label.setText(f"{user_name}\n{countdown}")

    def eventFilter(self, watched: QWidget, event: QEvent) -> bool:
        if watched == self.label and isinstance(event, QMouseEvent):
            if event.type() == QEvent.MouseButtonPress:
                return self.start_drag(event)
            if event.type() == QEvent.MouseMove:
                return self.drag_to(event)
            if event.type() == QEvent.MouseButtonRelease:
                return self.finish_drag(event)

        return super().eventFilter(watched, event)

    def start_drag(self, event: QMouseEvent) -> bool:
        if event.button() != Qt.LeftButton or self.locked:
            return False

        self._drag_offset = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
        window_handle = self.windowHandle()
        if window_handle and window_handle.startSystemMove():
            self._system_move_active = True

        event.accept()
        return True

    def drag_to(self, event: QMouseEvent) -> bool:
        if self._drag_offset is None or self.locked:
            return False

        if not self._system_move_active:
            self.move(event.globalPosition().toPoint() - self._drag_offset)

        event.accept()
        return True

    def finish_drag(self, event: QMouseEvent) -> bool:
        if event.button() != Qt.LeftButton or self._drag_offset is None:
            return False

        self._drag_offset = None
        self._system_move_active = False
        self.keep_inside_screen()
        self.save_position()
        event.accept()
        return True

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if self.start_drag(event):
            return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        if self.drag_to(event):
            return
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        if self.finish_drag(event):
            return
        super().mouseReleaseEvent(event)


class PomodoroDesktopApp(QWidget):
    def __init__(self, api_base_url: str = API_BASE_URL):
        super().__init__()
        self.setWindowTitle("PomodoroHub")
        self.setFixedSize(320, 400)
        self.setWindowFlag(Qt.WindowStaysOnTopHint, True)
        self.setWindowFlag(Qt.WindowMinimizeButtonHint, True)

        self.api = PomodoroApiClient(base_url=api_base_url)
        self.logged_user = None
        self.logged_password = None
        self.session_end = None

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Usuário")

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Senha")
        self.password_input.setEchoMode(QLineEdit.Password)

        self.login_status_label = QLabel("Faça login ou crie uma conta para continuar")
        self.login_status_label.setWordWrap(True)

        self.login_button = QPushButton("Entrar")
        self.login_button.clicked.connect(self.handle_login)

        self.register_button = QPushButton("Criar conta")
        self.register_button.clicked.connect(self.handle_register)

        self.logout_button = QPushButton("Sair")
        self.logout_button.clicked.connect(self.handle_logout)

        self.duration_input = QSpinBox()
        self.duration_input.setRange(1, 180)
        self.duration_input.setValue(25)
        self.duration_input.setSuffix(" min")

        self.status_label = QLabel("Status: aguardando ação")
        self.status_label.setWordWrap(True)

        self.countdown_label = QLabel("Tempo restante: --:--")
        self.countdown_label.setWordWrap(True)
        self.countdown_label.setStyleSheet("font-size: 14px; font-weight: bold;")

        self.active_label = QLabel("Nenhum usuário em sessão")
        self.active_label.setWordWrap(True)
        self.active_label.setStyleSheet("font-weight: bold;")

        self.start_button = QPushButton("Iniciar Pomodoro")
        self.start_button.clicked.connect(self.handle_start)

        self.stop_button = QPushButton("Parar Pomodoro")
        self.stop_button.clicked.connect(self.handle_stop)

        self.refresh_button = QPushButton("Atualizar agora")
        self.refresh_button.clicked.connect(self.refresh_active_sessions)

        self.overlay = OverlayWindow()

        self.overlay_lock_checkbox = QCheckBox("Fixar bloco na tela")
        self.overlay_lock_checkbox.setChecked(self.overlay.locked)
        self.overlay_lock_checkbox.toggled.connect(self.overlay.set_locked)

        self.overlay_reset_button = QPushButton("Voltar bloco para o canto")
        self.overlay_reset_button.clicked.connect(lambda: self.overlay.move_to_corner())

        self.login_widget = QWidget()
        login_layout = QVBoxLayout(self.login_widget)
        login_layout.addWidget(QLabel("Usuário"))
        login_layout.addWidget(self.username_input)
        login_layout.addWidget(QLabel("Senha"))
        login_layout.addWidget(self.password_input)

        login_button_layout = QHBoxLayout()
        login_button_layout.addWidget(self.login_button)
        login_button_layout.addWidget(self.register_button)
        login_layout.addLayout(login_button_layout)
        login_layout.addWidget(self.login_status_label)

        self.pomodoro_widget = QWidget()
        pomodoro_layout = QVBoxLayout(self.pomodoro_widget)
        pomodoro_layout.addWidget(QLabel("Tempo de trabalho (minutos)"))
        pomodoro_layout.addWidget(self.duration_input)
        pomodoro_layout.addWidget(self.countdown_label)

        pomodoro_button_layout = QHBoxLayout()
        pomodoro_button_layout.addWidget(self.start_button)
        pomodoro_button_layout.addWidget(self.stop_button)
        pomodoro_layout.addLayout(pomodoro_button_layout)

        pomodoro_layout.addWidget(self.refresh_button)
        pomodoro_layout.addWidget(self.overlay_lock_checkbox)
        pomodoro_layout.addWidget(self.overlay_reset_button)
        pomodoro_layout.addWidget(self.logout_button)
        pomodoro_layout.addWidget(self.status_label)
        pomodoro_layout.addWidget(QLabel("Usuários em sessão:"))
        pomodoro_layout.addWidget(self.active_label)

        self.pomodoro_widget.hide()

        main_layout = QVBoxLayout()
        main_layout.addWidget(self.login_widget)
        main_layout.addWidget(self.pomodoro_widget)
        self.setLayout(main_layout)

        self.active_sessions: list[dict[str, Any]] = []

        self._active_timer = QTimer(self)
        self._active_timer.timeout.connect(self.refresh_active_sessions)
        self._active_timer.start(5000)

        self._countdown_timer = QTimer(self)
        self._countdown_timer.timeout.connect(self.update_countdown)
        self._countdown_timer.start(1000)

    def show_error(self, message: str, login_phase: bool = False) -> None:
        if login_phase:
            self.login_status_label.setText(f"Erro: {message}")
        else:
            self.status_label.setText(f"Erro: {message}")
        QMessageBox.critical(self, "Erro", message)

    def validate_credentials(self) -> None:
        if not self.logged_user or not self.logged_password:
            raise RuntimeError("Usuário não autenticado")

    def handle_login(self) -> None:
        name = self.username_input.text().strip()
        password = self.password_input.text().strip()

        if not name or not password:
            self.show_error("Preencha usuário e senha para entrar.", login_phase=True)
            return

        try:
            self.api.login(name, password)
            self.logged_user = name
            self.logged_password = password
            self.login_status_label.setText("Login realizado com sucesso.")
            self.show_pomodoro_screen()
        except RuntimeError as error:
            self.show_error(str(error), login_phase=True)

    def handle_register(self) -> None:
        name = self.username_input.text().strip()
        password = self.password_input.text().strip()

        if not name or not password:
            self.show_error("Preencha usuário e senha para criar a conta.", login_phase=True)
            return

        try:
            self.api.register(name, password)
            self.logged_user = name
            self.logged_password = password
            self.login_status_label.setText("Conta criada com sucesso. Você já está logado.")
            self.show_pomodoro_screen()
        except RuntimeError as error:
            self.show_error(str(error), login_phase=True)

    def handle_logout(self) -> None:
        self.logged_user = None
        self.logged_password = None
        self.session_end = None
        self.countdown_label.setText("Tempo restante: --:--")
        self.overlay.hide()
        self.pomodoro_widget.hide()
        self.login_widget.show()
        self.login_status_label.setText("Faça login ou crie uma conta para continuar")
        self.status_label.setText("Status: aguardando ação")

    def show_pomodoro_screen(self) -> None:
        self.login_widget.hide()
        self.pomodoro_widget.show()
        self.status_label.setText(f"Logado como {self.logged_user}")
        self.refresh_active_sessions()

    def handle_start(self) -> None:
        try:
            self.validate_credentials()
        except RuntimeError as error:
            self.show_error(str(error))
            return

        duration = self.duration_input.value()

        try:
            session = self.api.start(self.logged_user, self.logged_password, duration)
            self.session_end = session_end_from_data(session)
            self.status_label.setText("Pomodoro iniciado com sucesso.")
            self.refresh_active_sessions()
        except RuntimeError as error:
            self.show_error(str(error))

    def handle_stop(self) -> None:
        try:
            self.validate_credentials()
        except RuntimeError as error:
            self.show_error(str(error))
            return

        try:
            self.api.stop(self.logged_user, self.logged_password)
            self.session_end = None
            self.countdown_label.setText("Tempo restante: --:--")
            self.status_label.setText("Pomodoro parado com sucesso.")
            self.refresh_active_sessions()
        except RuntimeError as error:
            self.show_error(str(error))

    def update_countdown(self) -> None:
        if not self.active_sessions:
            self.overlay.hide()
            if self.logged_user:
                self.countdown_label.setText("Tempo restante: --:--")
            return

        self.update_overlay_text()

        if self.logged_user:
            current_session = next(
                (session for session in self.active_sessions if session.get("user_name") == self.logged_user),
                None,
            )
            if current_session:
                self.session_end = session_end_from_data(current_session)
                self.countdown_label.setText(f"Tempo restante: {remaining_time_text(self.session_end)}")
            else:
                self.countdown_label.setText("Tempo restante: --:--")
                self.session_end = None

    def update_overlay_text(self) -> None:
        if not self.active_sessions:
            self.overlay.hide()
            return

        lines = []
        for session in self.active_sessions:
            end_time = get_session_end(session)
            remaining = remaining_time_text(end_time)
            lines.append(f"{session.get('user_name', '?')} - {remaining}")

        overlay_content = "\n".join(lines)
        self.overlay.update_text("Ativos", overlay_content)
        self.overlay.show()

    def refresh_active_sessions(self) -> None:
        try:
            sessions = self.api.get_active()
            self.active_sessions = sessions
            if not sessions:
                self.active_label.setText("Nenhum usuário em sessão no momento.")
                self.status_label.setText("Nenhuma sessão ativa no momento.")
                self.overlay.hide()
                if self.logged_user:
                    self.countdown_label.setText("Tempo restante: --:--")
                return

            names = [session.get("user_name", "?") for session in sessions]
            self.active_label.setText(" | ".join(names))
            self.status_label.setText(f"{len(names)} usuário(s) em sessão")
            self.update_overlay_text()

            if self.logged_user:
                current_session = next(
                    (session for session in sessions if session.get("user_name") == self.logged_user),
                    None,
                )
                if current_session:
                    self.session_end = session_end_from_data(current_session)
                    self.countdown_label.setText(f"Tempo restante: {remaining_time_text(self.session_end)}")
                else:
                    self.countdown_label.setText("Tempo restante: --:--")
                    self.session_end = None

        except RuntimeError as error:
            self.status_label.setText("Não foi possível atualizar sessões ativas.")
            self.active_label.setText("")
            print("Erro de API:", error)


def main() -> None:
    parser = argparse.ArgumentParser(description="PomodoroHub client")
    parser.add_argument(
        "--api-url",
        default=os.getenv("POMODORO_HUB_API_URL", API_BASE_URL),
        help="URL do backend PomodoroHub (ex: http://192.168.0.10:8000)",
    )
    args = parser.parse_args()

    app = QApplication(sys.argv)
    window = PomodoroDesktopApp(api_base_url=args.api_url)
    window.show()
    sys.exit(app.exec())
