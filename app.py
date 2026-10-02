from __future__ import annotations

import json
import os
import re
import sys
import time
import uuid
from collections import Counter
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path

try:
    from PySide6 import QtCore, QtGui, QtWidgets
except ImportError:
    QtCore = QtGui = QtWidgets = None

APP_NAME = "Writing Exercise Studio"
APP_VERSION = "2.6"
DATA_DIR = Path.home() / ".writing_exercise_studio"
DATA_FILE = DATA_DIR / "exercises.json"
WORD_PATTERN = re.compile(r"\b\w+(?:[\u2019'-]\w+)*\b", re.UNICODE)

LIGHT_STYLESHEET = """
QMainWindow, QDialog, QMessageBox, QWidget#appRoot, QWidget#editorPanel {
    background: #f6f8fc;
    color: #1e293b;
}

QWidget#sidebar {
    background: #ffffff;
    border-right: 1px solid #e5eaf2;
}

QLabel {
    color: #334155;
    background: transparent;
}

QLabel#pageTitle {
    color: #172033;
    font-size: 21px;
    font-weight: 700;
}

QLabel#fieldLabel {
    color: #64748b;
    font-size: 11px;
    font-weight: 700;
}

QLabel#mutedLabel, QLabel#metricLabel, QLabel#summaryLabel {
    color: #718096;
}

QLineEdit, QComboBox, QSpinBox {
    background: #ffffff;
    color: #1e293b;
    border: 1px solid #dbe2ec;
    border-radius: 8px;
    padding: 7px 10px;
    selection-background-color: #4f6fed;
    selection-color: #ffffff;
}

QLineEdit:focus, QComboBox:focus, QSpinBox:focus {
    border: 1px solid #4f6fed;
}

QComboBox::drop-down {
    border: 0;
    width: 32px;
}

QComboBox::down-arrow {
    image: none;
    width: 0;
    height: 0;
}

QSpinBox::up-button, QSpinBox::down-button {
    width: 0;
    height: 0;
    border: 0;
}

QComboBox QAbstractItemView {
    background: #ffffff;
    color: #1e293b;
    border: 1px solid #dbe2ec;
    selection-background-color: #e8edff;
    selection-color: #28469a;
    outline: 0;
}

QTextEdit, QPlainTextEdit {
    background: #ffffff;
    color: #1e293b;
    border: 1px solid #dbe2ec;
    border-radius: 12px;
    padding: 12px;
    selection-background-color: #cfd9ff;
    selection-color: #172033;
}

QTextEdit:focus, QPlainTextEdit:focus {
    border: 1px solid #9aacec;
}

QPushButton {
    background: #ffffff;
    color: #334155;
    border: 1px solid #dbe2ec;
    border-radius: 8px;
    padding: 8px 14px;
    font-weight: 600;
}

QPushButton:hover {
    background: #f1f4fa;
    border-color: #c7d1df;
}

QPushButton:pressed {
    background: #e8edf5;
}

QToolButton {
    background: #eef2f8;
    color: #42526b;
    border: 1px solid #d6deea;
    border-radius: 6px;
    font-size: 10px;
    font-weight: 700;
}

QToolButton:hover {
    background: #e3e9f3;
    color: #28469a;
}

QToolButton:checked {
    background: #e6ecff;
    color: #28469a;
    border-color: #b8c6f5;
}

QToolButton#themeButton {
    background: #f1f4fa;
    color: #42526b;
    border: 1px solid #dbe2ec;
    font-size: 16px;
}

QWidget#formatToolbar {
    background: #ffffff;
    border: 1px solid #e1e7f0;
    border-radius: 9px;
}

QPushButton#primaryButton {
    background: #4f6fed;
    color: #ffffff;
    border: 1px solid #4f6fed;
}

QPushButton#primaryButton:hover {
    background: #405fd6;
    border-color: #405fd6;
}

QPushButton#dangerButton {
    background: #fff5f6;
    color: #be4057;
    border: 1px solid #f4cbd2;
}

QPushButton#dangerButton:hover {
    background: #ffecef;
}

QTreeWidget, QTableWidget {
    background: #ffffff;
    alternate-background-color: #f8faff;
    color: #334155;
    border: 1px solid #e1e7f0;
    border-radius: 9px;
    outline: 0;
    gridline-color: #edf1f6;
    selection-background-color: #e6ecff;
    selection-color: #28469a;
}

QTreeWidget::item, QTableWidget::item {
    padding: 6px;
    border: 0;
}

QTreeWidget::item:hover, QTableWidget::item:hover {
    background: #f0f4ff;
}

QHeaderView::section {
    background: #f1f4f9;
    color: #64748b;
    border: 0;
    border-bottom: 1px solid #e1e7f0;
    padding: 7px;
    font-weight: 700;
}

QGroupBox {
    background: #ffffff;
    color: #334155;
    border: 1px solid #e1e7f0;
    border-radius: 12px;
    margin-top: 14px;
    padding-top: 10px;
    font-weight: 700;
}

QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    left: 12px;
    padding: 0 6px;
    color: #475569;
}

QProgressBar {
    background: #e7ebf3;
    border: 0;
    border-radius: 3px;
    max-height: 6px;
    min-height: 6px;
}

QProgressBar::chunk {
    background: #4f6fed;
    border-radius: 3px;
}

QSplitter::handle {
    background: #e5eaf2;
    width: 1px;
}

QStatusBar {
    background: #ffffff;
    color: #718096;
    border-top: 1px solid #e5eaf2;
}

QMessageBox QLabel {
    color: #334155;
    min-width: 260px;
}

QScrollBar:vertical {
    background: transparent;
    width: 10px;
    margin: 2px;
}

QScrollBar::handle:vertical {
    background: #cbd4e1;
    min-height: 28px;
    border-radius: 4px;
}

QScrollBar::handle:vertical:hover {
    background: #aeb9c9;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical,
QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
    background: transparent;
    border: 0;
    height: 0;
}
"""

DARK_STYLESHEET = """
QMainWindow, QDialog, QMessageBox, QWidget#appRoot, QWidget#editorPanel {
    background: #111827;
    color: #e5edf7;
}

QWidget#sidebar {
    background: #0f172a;
    border-right: 1px solid #263349;
}

QLabel {
    color: #d9e2ef;
}

QLabel#pageTitle {
    color: #f3f7fc;
}

QLabel#fieldLabel {
    color: #93a4ba;
}

QLabel#mutedLabel, QLabel#metricLabel, QLabel#summaryLabel {
    color: #8fa1b8;
}

QLineEdit, QComboBox, QSpinBox {
    background: #182235;
    color: #edf3fb;
    border: 1px solid #30405a;
    selection-background-color: #6f8ff2;
    selection-color: #ffffff;
}

QLineEdit:focus, QComboBox:focus, QSpinBox:focus {
    border: 1px solid #7c9cff;
}

QComboBox QAbstractItemView {
    background: #182235;
    color: #edf3fb;
    border: 1px solid #30405a;
    selection-background-color: #263d70;
    selection-color: #ffffff;
}

QTextEdit, QPlainTextEdit {
    background: #151f31;
    color: #edf3fb;
    border: 1px solid #30405a;
    selection-background-color: #405a9f;
    selection-color: #ffffff;
}

QTextEdit:focus, QPlainTextEdit:focus {
    border: 1px solid #617bc7;
}

QPushButton {
    background: #1a2639;
    color: #dce6f2;
    border: 1px solid #34445d;
}

QPushButton:hover {
    background: #223149;
    border-color: #455976;
}

QPushButton:pressed {
    background: #2a3a54;
}

QPushButton#primaryButton {
    background: #6f8ff2;
    color: #ffffff;
    border-color: #6f8ff2;
}

QPushButton#primaryButton:hover {
    background: #5e7fe2;
    border-color: #5e7fe2;
}

QPushButton#dangerButton {
    background: #321e29;
    color: #ff9daf;
    border-color: #653244;
}

QPushButton#dangerButton:hover {
    background: #422432;
}

QToolButton {
    background: #223149;
    color: #dce6f2;
    border-color: #3a4b65;
}

QToolButton:hover {
    background: #2b3d59;
    color: #ffffff;
}

QToolButton:checked {
    background: #263d70;
    color: #ffffff;
    border-color: #5872bd;
}

QToolButton#themeButton {
    background: #1a2639;
    color: #ffd56a;
    border-color: #34445d;
}

QWidget#formatToolbar {
    background: #151f31;
    border-color: #2d3b52;
}

QTreeWidget, QTableWidget {
    background: #151f31;
    alternate-background-color: #182438;
    color: #dce6f2;
    border-color: #2d3b52;
    gridline-color: #27364c;
    selection-background-color: #263d70;
    selection-color: #ffffff;
}

QTreeWidget::item:hover, QTableWidget::item:hover {
    background: #20314c;
}

QHeaderView::section {
    background: #1d2a40;
    color: #a8b7ca;
    border-bottom-color: #30405a;
}

QGroupBox {
    background: #151f31;
    color: #dce6f2;
    border-color: #2d3b52;
}

QGroupBox::title {
    color: #b8c5d5;
}

QProgressBar {
    background: #2a374c;
}

QProgressBar::chunk {
    background: #6f8ff2;
}

QSplitter::handle {
    background: #263349;
}

QStatusBar {
    background: #0f172a;
    color: #8fa1b8;
    border-top-color: #263349;
}

QMessageBox QLabel {
    color: #e5edf7;
}

QScrollBar::handle:vertical {
    background: #46556c;
}

QScrollBar::handle:vertical:hover {
    background: #607089;
}
"""


def app_stylesheet(dark: bool) -> str:
    return LIGHT_STYLESHEET + (DARK_STYLESHEET if dark else "")


def count_words(text: str) -> int:
    return len(WORD_PATTERN.findall(text))


def repeated_words(text: str) -> list[tuple[str, int]]:
    """Return case-insensitive repeated words sorted by count, then name."""
    counts = Counter(word.casefold() for word in WORD_PATTERN.findall(text))
    return sorted(
        ((word, count) for word, count in counts.items() if count > 1),
        key=lambda item: (-item[1], item[0]),
    )


def find_word_matches(text: str, query: str, exact: bool = False) -> list[tuple[int, int]]:
    """Return ranges for words matching a case-insensitive query."""
    normalized_query = query.strip().casefold()
    if not normalized_query:
        return []
    matches: list[tuple[int, int]] = []
    for word_match in WORD_PATTERN.finditer(text):
        word = word_match.group(0).casefold()
        if (word == normalized_query) if exact else (normalized_query in word):
            matches.append(word_match.span())
    return matches


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


@dataclass
class Exercise:
    id: str
    title: str
    category: str = "Uncategorized"
    content: str = ""
    content_html: str = ""
    target_words: int = 250
    elapsed_seconds: int = 0
    created_at: str = ""
    updated_at: str = ""

    @classmethod
    def create(
            cls,
            title: str = "Untitled Exercise",
            category: str = "Uncategorized",
    ) -> "Exercise":
        now = utc_now()
        return cls(
            id=str(uuid.uuid4()),
            title=title,
            category=category.strip() or "Uncategorized",
            created_at=now,
            updated_at=now,
        )

    @classmethod
    def from_dict(cls, value: dict) -> "Exercise":
        return cls(
            id=str(value.get("id") or uuid.uuid4()),
            title=str(value.get("title") or "Untitled Exercise"),
            category=str(value.get("category") or "Uncategorized"),
            content=str(value.get("content") or ""),
            content_html=str(value.get("content_html") or ""),
            target_words=max(1, int(value.get("target_words") or 250)),
            elapsed_seconds=max(0, int(value.get("elapsed_seconds") or 0)),
            created_at=str(value.get("created_at") or utc_now()),
            updated_at=str(value.get("updated_at") or utc_now()),
        )


class ExerciseStore:
    def __init__(self, path: Path = DATA_FILE) -> None:
        self.path = path
        # Set when an unreadable data file was moved aside during load().
        self.backup_path: Path | None = None

    def load(self) -> list[Exercise]:
        if not self.path.exists():
            return []
        try:
            payload = json.loads(self.path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            # Keep the damaged file instead of overwriting it on the next save.
            self.backup_path = self._back_up_unreadable_file()
            return []
        values = payload.get("exercises", []) if isinstance(payload, dict) else []
        exercises = []
        for value in values:
            if not isinstance(value, dict):
                continue
            try:
                exercises.append(Exercise.from_dict(value))
            except (ValueError, TypeError):
                continue
        return exercises

    def _back_up_unreadable_file(self) -> Path | None:
        stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        backup = self.path.with_name(f"{self.path.stem}.unreadable-{stamp}{self.path.suffix}")
        try:
            os.replace(self.path, backup)
        except OSError:
            return None
        return backup

    def save(self, exercises: list[Exercise]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "version": 1,
            "exercises": [asdict(exercise) for exercise in exercises],
        }
        temporary = self.path.with_suffix(".tmp")
        temporary.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        os.replace(temporary, self.path)


if QtWidgets is not None:

    class VisibleArrowComboBox(QtWidgets.QComboBox):
        """Editable combo box with a theme-aware, explicitly drawn arrow."""

        def paintEvent(self, event) -> None:
            super().paintEvent(event)
            application = QtWidgets.QApplication.instance()
            dark = bool(application.property("darkTheme")) if application else False
            painter = QtGui.QPainter(self)
            painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)
            pen = QtGui.QPen(
                QtGui.QColor("#dce6f2" if dark else "#42526b"),
                2.0,
                QtCore.Qt.PenStyle.SolidLine,
                QtCore.Qt.PenCapStyle.RoundCap,
                QtCore.Qt.PenJoinStyle.RoundJoin,
            )
            painter.setPen(pen)
            center_x = self.width() - 16
            center_y = self.height() // 2
            path = QtGui.QPainterPath()
            path.moveTo(center_x - 4, center_y - 2)
            path.lineTo(center_x, center_y + 2)
            path.lineTo(center_x + 4, center_y - 2)
            painter.drawPath(path)


    class WritingExerciseApp(QtWidgets.QMainWindow):
        def __init__(self, store: ExerciseStore | None = None) -> None:
            super().__init__()
            self.store = store or ExerciseStore()
            self.exercises = self.store.load()
            self.current_id: str | None = None
            self.loading = False
            self.timer_started_at: float | None = None
            self.highlight_query = ""
            self.highlight_exact = False
            application = QtWidgets.QApplication.instance()
            self.dark_mode = (
                bool(application.property("darkTheme")) if application else False
            )

            self.setWindowTitle(f"{APP_NAME} {APP_VERSION}")
            self.resize(1120, 720)
            self.setMinimumSize(820, 560)

            self.autosave_timer = QtCore.QTimer(self)
            self.autosave_timer.setSingleShot(True)
            self.autosave_timer.setInterval(900)
            self.autosave_timer.timeout.connect(self.save_current)

            self.clock_timer = QtCore.QTimer(self)
            self.clock_timer.setInterval(250)
            self.clock_timer.timeout.connect(self.update_timer_display)

            self._build_ui()
            self._add_shortcuts()
            self.update_theme_button()

            if not self.exercises:
                self.exercises.append(Exercise.create())
                self.store.save(self.exercises)
            self.refresh_library()
            self.load_exercise(self.exercises[0].id)

            if self.store.backup_path is not None:
                QtCore.QTimer.singleShot(0, self.show_backup_notice)

        def show_backup_notice(self) -> None:
            QtWidgets.QMessageBox.warning(
                self,
                "Saved exercises could not be read",
                "Your exercises file was damaged and could not be opened.\n\n"
                "It was kept as a backup here:\n"
                f"{self.store.backup_path}",
            )

        def _build_ui(self) -> None:
            central = QtWidgets.QWidget()
            central.setObjectName("appRoot")
            self.setCentralWidget(central)
            outer = QtWidgets.QHBoxLayout(central)
            outer.setContentsMargins(0, 0, 0, 0)
            outer.setSpacing(0)

            splitter = QtWidgets.QSplitter(QtCore.Qt.Orientation.Horizontal)
            splitter.setChildrenCollapsible(False)
            outer.addWidget(splitter)

            sidebar = QtWidgets.QWidget()
            sidebar.setObjectName("sidebar")
            sidebar.setMinimumWidth(230)
            sidebar.setMaximumWidth(330)
            sidebar_layout = QtWidgets.QVBoxLayout(sidebar)
            sidebar_layout.setContentsMargins(20, 24, 20, 20)
            sidebar_layout.setSpacing(12)

            sidebar_header = QtWidgets.QHBoxLayout()
            sidebar_header.setSpacing(8)
            library_title = QtWidgets.QLabel("My exercises")
            library_title.setObjectName("pageTitle")
            sidebar_header.addWidget(library_title)
            sidebar_header.addStretch(1)
            self.theme_button = QtWidgets.QToolButton()
            self.theme_button.setObjectName("themeButton")
            self.theme_button.setFixedSize(34, 34)
            self.theme_button.clicked.connect(self.toggle_theme)
            sidebar_header.addWidget(self.theme_button)
            sidebar_layout.addLayout(sidebar_header)

            hint = QtWidgets.QLabel("Saved automatically on this computer")
            hint.setObjectName("mutedLabel")
            hint.setWordWrap(True)
            sidebar_layout.addWidget(hint)

            new_button = QtWidgets.QPushButton("+ New exercise")
            new_button.setObjectName("primaryButton")
            new_button.clicked.connect(self.new_exercise)
            sidebar_layout.addWidget(new_button)

            self.library = QtWidgets.QTreeWidget()
            self.library.setHeaderHidden(True)
            self.library.setAlternatingRowColors(True)
            self.library.setIndentation(18)
            self.library.setRootIsDecorated(True)
            self.library.setUniformRowHeights(True)
            self.library.currentItemChanged.connect(self.library_selection_changed)
            sidebar_layout.addWidget(self.library, 1)

            delete_button = QtWidgets.QPushButton("Delete selected")
            delete_button.setObjectName("dangerButton")
            delete_button.clicked.connect(self.delete_exercise)
            sidebar_layout.addWidget(delete_button)

            editor = QtWidgets.QWidget()
            editor.setObjectName("editorPanel")
            editor_layout = QtWidgets.QVBoxLayout(editor)
            editor_layout.setContentsMargins(30, 24, 30, 20)
            editor_layout.setSpacing(14)

            form = QtWidgets.QGridLayout()
            form.setHorizontalSpacing(14)
            form.setVerticalSpacing(7)
            title_label = QtWidgets.QLabel("EXERCISE TITLE")
            title_label.setObjectName("fieldLabel")
            form.addWidget(title_label, 0, 0)
            self.title_edit = QtWidgets.QLineEdit()
            self.title_edit.setPlaceholderText("Exercise title")
            self.title_edit.setFixedHeight(38)
            self.title_edit.textChanged.connect(self.content_changed)
            form.addWidget(self.title_edit, 1, 0)

            category_label = QtWidgets.QLabel("CATEGORY")
            category_label.setObjectName("fieldLabel")
            form.addWidget(category_label, 0, 1)
            self.category_combo = VisibleArrowComboBox()
            self.category_combo.setEditable(True)
            self.category_combo.setMinimumWidth(170)
            self.category_combo.setFixedHeight(38)
            self.category_combo.setInsertPolicy(
                QtWidgets.QComboBox.InsertPolicy.NoInsert
            )
            self.category_combo.currentTextChanged.connect(self.content_changed)
            form.addWidget(self.category_combo, 1, 1)

            target_label = QtWidgets.QLabel("WORD TARGET")
            target_label.setObjectName("fieldLabel")
            form.addWidget(target_label, 0, 2)
            self.target_spin = QtWidgets.QSpinBox()
            self.target_spin.setRange(1, 100000)
            self.target_spin.setValue(250)
            self.target_spin.setMinimumWidth(96)
            self.target_spin.setFixedHeight(38)
            self.target_spin.setButtonSymbols(
                QtWidgets.QAbstractSpinBox.ButtonSymbols.NoButtons
            )
            self.target_spin.valueChanged.connect(self.content_changed)

            target_control = QtWidgets.QWidget()
            target_control.setMinimumWidth(134)
            target_layout = QtWidgets.QHBoxLayout(target_control)
            target_layout.setContentsMargins(0, 0, 0, 0)
            target_layout.setSpacing(5)
            target_layout.addWidget(self.target_spin, 1)

            arrow_stack = QtWidgets.QVBoxLayout()
            arrow_stack.setContentsMargins(0, 0, 0, 0)
            arrow_stack.setSpacing(2)
            target_up = QtWidgets.QToolButton()
            target_up.setText("▲")
            target_up.setToolTip("Increase word target")
            target_up.setFixedSize(24, 18)
            target_up.setAutoRepeat(True)
            target_up.clicked.connect(
                lambda _checked=False: self.target_spin.stepUp()
            )
            arrow_stack.addWidget(target_up)
            target_down = QtWidgets.QToolButton()
            target_down.setText("▼")
            target_down.setToolTip("Decrease word target")
            target_down.setFixedSize(24, 18)
            target_down.setAutoRepeat(True)
            target_down.clicked.connect(
                lambda _checked=False: self.target_spin.stepDown()
            )
            arrow_stack.addWidget(target_down)
            target_layout.addLayout(arrow_stack)
            form.addWidget(target_control, 1, 2)
            form.setColumnStretch(0, 1)
            editor_layout.addLayout(form)

            metric_row = QtWidgets.QHBoxLayout()
            self.word_label = QtWidgets.QLabel("0 words")
            self.word_label.setObjectName("metricLabel")
            self.character_label = QtWidgets.QLabel("0 characters")
            self.character_label.setObjectName("metricLabel")
            self.progress_label = QtWidgets.QLabel("0% of target")
            self.progress_label.setObjectName("metricLabel")
            metric_row.addWidget(self.word_label)
            metric_row.addWidget(self.character_label)
            metric_row.addStretch(1)
            metric_row.addWidget(self.progress_label)
            editor_layout.addLayout(metric_row)

            self.progress = QtWidgets.QProgressBar()
            self.progress.setRange(0, 100)
            self.progress.setTextVisible(False)
            editor_layout.addWidget(self.progress)

            format_toolbar = QtWidgets.QWidget()
            format_toolbar.setObjectName("formatToolbar")
            format_layout = QtWidgets.QHBoxLayout(format_toolbar)
            format_layout.setContentsMargins(8, 6, 8, 6)
            format_layout.setSpacing(5)

            format_label = QtWidgets.QLabel("TEXT")
            format_label.setObjectName("fieldLabel")
            format_layout.addWidget(format_label)

            size_down = QtWidgets.QToolButton()
            size_down.setText("−")
            size_down.setToolTip("Decrease font size")
            size_down.setFixedSize(30, 28)
            size_down.setAutoRepeat(True)
            size_down.clicked.connect(self.decrease_font_size)
            format_layout.addWidget(size_down)

            self.font_size_label = QtWidgets.QLabel("14 pt")
            self.font_size_label.setObjectName("summaryLabel")
            self.font_size_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
            self.font_size_label.setFixedWidth(44)
            format_layout.addWidget(self.font_size_label)

            size_up = QtWidgets.QToolButton()
            size_up.setText("+")
            size_up.setToolTip("Increase font size")
            size_up.setFixedSize(30, 28)
            size_up.setAutoRepeat(True)
            size_up.clicked.connect(self.increase_font_size)
            format_layout.addWidget(size_up)

            format_layout.addWidget(self.make_toolbar_separator())

            self.bold_button = QtWidgets.QToolButton()
            self.bold_button.setText("B")
            bold_font = self.bold_button.font()
            bold_font.setBold(True)
            self.bold_button.setFont(bold_font)
            self.bold_button.setToolTip("Bold (⌘B / Ctrl+B)")
            self.bold_button.setCheckable(True)
            self.bold_button.setFixedSize(32, 28)
            self.bold_button.toggled.connect(self.set_bold)
            format_layout.addWidget(self.bold_button)

            self.italic_button = QtWidgets.QToolButton()
            self.italic_button.setText("I")
            italic_font = self.italic_button.font()
            italic_font.setItalic(True)
            self.italic_button.setFont(italic_font)
            self.italic_button.setToolTip("Italic (⌘I / Ctrl+I)")
            self.italic_button.setCheckable(True)
            self.italic_button.setFixedSize(32, 28)
            self.italic_button.toggled.connect(self.set_italic)
            format_layout.addWidget(self.italic_button)

            self.underline_button = QtWidgets.QToolButton()
            self.underline_button.setText("U")
            underline_font = self.underline_button.font()
            underline_font.setUnderline(True)
            self.underline_button.setFont(underline_font)
            self.underline_button.setToolTip("Underline (⌘U / Ctrl+U)")
            self.underline_button.setCheckable(True)
            self.underline_button.setFixedSize(32, 28)
            self.underline_button.toggled.connect(self.set_underline)
            format_layout.addWidget(self.underline_button)

            self.color_button = QtWidgets.QToolButton()
            self.color_button.setText("Color")
            self.color_button.setToolTip("Choose font colour")
            self.color_button.setToolButtonStyle(
                QtCore.Qt.ToolButtonStyle.ToolButtonTextBesideIcon
            )
            self.color_button.setFixedHeight(28)
            self.color_button.clicked.connect(self.choose_font_color)
            format_layout.addWidget(self.color_button)

            format_layout.addWidget(self.make_toolbar_separator())

            self.ltr_button = QtWidgets.QToolButton()
            self.ltr_button.setText("LTR")
            self.ltr_button.setToolTip("Left-to-right paragraph")
            self.ltr_button.setCheckable(True)
            self.ltr_button.setFixedSize(44, 28)
            self.ltr_button.clicked.connect(
                lambda _checked=False: self.set_text_direction(False)
            )
            format_layout.addWidget(self.ltr_button)

            self.rtl_button = QtWidgets.QToolButton()
            self.rtl_button.setText("RTL")
            self.rtl_button.setToolTip("Right-to-left paragraph")
            self.rtl_button.setCheckable(True)
            self.rtl_button.setFixedSize(44, 28)
            self.rtl_button.clicked.connect(
                lambda _checked=False: self.set_text_direction(True)
            )
            format_layout.addWidget(self.rtl_button)

            self.direction_group = QtWidgets.QButtonGroup(self)
            self.direction_group.setExclusive(True)
            self.direction_group.addButton(self.ltr_button)
            self.direction_group.addButton(self.rtl_button)
            self.ltr_button.setChecked(True)
            format_layout.addStretch(1)
            editor_layout.addWidget(format_toolbar)

            search_row = QtWidgets.QHBoxLayout()
            search_label = QtWidgets.QLabel("SEARCH")
            search_label.setObjectName("fieldLabel")
            search_row.addWidget(search_label)
            self.search_edit = QtWidgets.QLineEdit()
            self.search_edit.setPlaceholderText(
                "Type part of a word, e.g. ‘write’ finds writer and rewrite"
            )
            self.search_edit.setClearButtonEnabled(True)
            self.search_edit.setFixedHeight(38)
            self.search_edit.textChanged.connect(self.search_changed)
            search_row.addWidget(self.search_edit, 1)
            self.search_summary = QtWidgets.QLabel("0 matches")
            self.search_summary.setObjectName("summaryLabel")
            self.search_summary.setMinimumWidth(80)
            search_row.addWidget(self.search_summary)
            editor_layout.addLayout(search_row)

            writing_row = QtWidgets.QHBoxLayout()
            writing_row.setSpacing(14)

            self.text_edit = QtWidgets.QTextEdit()
            self.text_edit.setPlaceholderText("Start writing here…")
            editor_font = QtGui.QFont()
            editor_font.setPointSize(14)
            self.text_edit.setFont(editor_font)
            self.text_edit.document().setDefaultFont(editor_font)
            self.text_edit.setTabChangesFocus(False)
            self.text_edit.textChanged.connect(self.text_changed)
            self.text_edit.cursorPositionChanged.connect(
                self.update_format_toolbar
            )
            writing_row.addWidget(self.text_edit, 1)

            repeated_group = QtWidgets.QGroupBox("Repeated words")
            repeated_group.setMinimumWidth(190)
            repeated_group.setMaximumWidth(260)
            repeated_layout = QtWidgets.QVBoxLayout(repeated_group)
            repeated_hint = QtWidgets.QLabel("Words used more than once")
            repeated_hint.setObjectName("mutedLabel")
            repeated_hint.setWordWrap(True)
            repeated_layout.addWidget(repeated_hint)

            self.repeated_table = QtWidgets.QTableWidget(0, 2)
            self.repeated_table.setHorizontalHeaderLabels(["Word", "Count"])
            self.repeated_table.horizontalHeader().setSectionResizeMode(
                0, QtWidgets.QHeaderView.ResizeMode.Stretch
            )
            self.repeated_table.horizontalHeader().setSectionResizeMode(
                1, QtWidgets.QHeaderView.ResizeMode.ResizeToContents
            )
            self.repeated_table.verticalHeader().setVisible(False)
            self.repeated_table.setEditTriggers(
                QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers
            )
            self.repeated_table.setSelectionBehavior(
                QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows
            )
            self.repeated_table.setAlternatingRowColors(True)
            self.repeated_table.setShowGrid(False)
            self.repeated_table.setFocusPolicy(QtCore.Qt.FocusPolicy.NoFocus)
            self.repeated_table.cellClicked.connect(self.repeated_word_clicked)
            repeated_layout.addWidget(self.repeated_table, 1)

            self.repeated_summary = QtWidgets.QLabel("No repeated words")
            self.repeated_summary.setObjectName("summaryLabel")
            repeated_layout.addWidget(self.repeated_summary)
            writing_row.addWidget(repeated_group)
            editor_layout.addLayout(writing_row, 1)

            controls = QtWidgets.QHBoxLayout()
            self.timer_label = QtWidgets.QLabel("00:00:00")
            timer_font = QtGui.QFontDatabase.systemFont(QtGui.QFontDatabase.SystemFont.FixedFont)
            timer_font.setPointSize(16)
            timer_font.setBold(True)
            self.timer_label.setFont(timer_font)
            controls.addWidget(self.timer_label)

            self.timer_button = QtWidgets.QPushButton("Start timer")
            self.timer_button.clicked.connect(self.toggle_timer)
            controls.addWidget(self.timer_button)

            reset_button = QtWidgets.QPushButton("Reset timer")
            reset_button.clicked.connect(self.reset_timer)
            controls.addWidget(reset_button)
            controls.addStretch(1)

            save_button = QtWidgets.QPushButton("Save now")
            save_button.setObjectName("primaryButton")
            save_button.clicked.connect(self.save_current)
            controls.addWidget(save_button)
            editor_layout.addLayout(controls)

            splitter.addWidget(sidebar)
            splitter.addWidget(editor)
            splitter.setSizes([270, 850])

            self.statusBar().showMessage("Ready")

        def _add_shortcuts(self) -> None:
            new_action = QtGui.QAction(self)
            new_action.setShortcut(QtGui.QKeySequence.StandardKey.New)
            new_action.triggered.connect(self.new_exercise)
            self.addAction(new_action)

            save_action = QtGui.QAction(self)
            save_action.setShortcut(QtGui.QKeySequence.StandardKey.Save)
            save_action.triggered.connect(self.save_current)
            self.addAction(save_action)

            bold_action = QtGui.QAction(self)
            bold_action.setShortcut(QtGui.QKeySequence.StandardKey.Bold)
            bold_action.triggered.connect(
                lambda: self.bold_button.toggle()
            )
            self.addAction(bold_action)

            italic_action = QtGui.QAction(self)
            italic_action.setShortcut(QtGui.QKeySequence.StandardKey.Italic)
            italic_action.triggered.connect(
                lambda: self.italic_button.toggle()
            )
            self.addAction(italic_action)

            underline_action = QtGui.QAction(self)
            underline_action.setShortcut(QtGui.QKeySequence.StandardKey.Underline)
            underline_action.triggered.connect(
                lambda: self.underline_button.toggle()
            )
            self.addAction(underline_action)

        def make_toolbar_separator(self) -> QtWidgets.QFrame:
            separator = QtWidgets.QFrame()
            separator.setFrameShape(QtWidgets.QFrame.Shape.VLine)
            separator.setFrameShadow(QtWidgets.QFrame.Shadow.Sunken)
            separator.setFixedHeight(22)
            return separator

        def merge_character_format(self, character_format: QtGui.QTextCharFormat) -> None:
            cursor = self.text_edit.textCursor()
            cursor.mergeCharFormat(character_format)
            self.text_edit.mergeCurrentCharFormat(character_format)
            self.text_edit.setFocus()
            self.update_format_toolbar()

        def current_font_size(self) -> float:
            size = self.text_edit.textCursor().charFormat().fontPointSize()
            if size <= 0:
                size = self.text_edit.currentFont().pointSizeF()
            return size if size > 0 else 14.0

        def change_font_size(self, amount: float) -> None:
            size = max(8.0, min(72.0, self.current_font_size() + amount))
            character_format = QtGui.QTextCharFormat()
            character_format.setFontPointSize(size)
            self.merge_character_format(character_format)

        def increase_font_size(self, _checked: bool = False) -> None:
            self.change_font_size(1.0)

        def decrease_font_size(self, _checked: bool = False) -> None:
            self.change_font_size(-1.0)

        def set_bold(self, enabled: bool) -> None:
            character_format = QtGui.QTextCharFormat()
            character_format.setFontWeight(
                QtGui.QFont.Weight.Bold.value
                if enabled
                else QtGui.QFont.Weight.Normal.value
            )
            self.merge_character_format(character_format)

        def set_italic(self, enabled: bool) -> None:
            character_format = QtGui.QTextCharFormat()
            character_format.setFontItalic(enabled)
            self.merge_character_format(character_format)

        def set_underline(self, enabled: bool) -> None:
            character_format = QtGui.QTextCharFormat()
            character_format.setFontUnderline(enabled)
            self.merge_character_format(character_format)

        def choose_font_color(self, _checked: bool = False) -> None:
            current = self.text_edit.textCursor().charFormat().foreground().color()
            if not current.isValid():
                current = QtGui.QColor("#edf3fb" if self.dark_mode else "#1e293b")
            dialog = QtWidgets.QColorDialog(current, self)
            dialog.setWindowTitle("Choose font colour")
            dialog.setOption(
                QtWidgets.QColorDialog.ColorDialogOption.DontUseNativeDialog,
                True,
            )
            if dialog.exec() != QtWidgets.QDialog.DialogCode.Accepted:
                return
            color = dialog.selectedColor()
            character_format = QtGui.QTextCharFormat()
            character_format.setForeground(color)
            self.merge_character_format(character_format)

        def update_color_button(self, color: QtGui.QColor | None = None) -> None:
            if color is None or not color.isValid():
                color = QtGui.QColor("#edf3fb" if self.dark_mode else "#1e293b")
            pixmap = QtGui.QPixmap(16, 16)
            pixmap.fill(QtCore.Qt.GlobalColor.transparent)
            painter = QtGui.QPainter(pixmap)
            painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)
            painter.setPen(QtGui.QPen(QtGui.QColor("#718096"), 1))
            painter.setBrush(color)
            painter.drawRoundedRect(1, 1, 14, 14, 3, 3)
            painter.end()
            self.color_button.setIcon(QtGui.QIcon(pixmap))

        def set_text_direction(self, rtl: bool) -> None:
            cursor = self.text_edit.textCursor()
            block_format = cursor.blockFormat()
            block_format.setLayoutDirection(
                QtCore.Qt.LayoutDirection.RightToLeft
                if rtl
                else QtCore.Qt.LayoutDirection.LeftToRight
            )
            block_format.setAlignment(
                QtCore.Qt.AlignmentFlag.AlignRight
                if rtl
                else QtCore.Qt.AlignmentFlag.AlignLeft
            )
            cursor.mergeBlockFormat(block_format)
            self.text_edit.setTextCursor(cursor)
            self.text_edit.setFocus()
            self.update_format_toolbar()

        def update_format_toolbar(self) -> None:
            cursor = self.text_edit.textCursor()
            character_format = cursor.charFormat()
            size = character_format.fontPointSize()
            if size <= 0:
                size = self.text_edit.currentFont().pointSizeF()
            if size <= 0:
                size = 14.0
            self.font_size_label.setText(f"{size:g} pt")

            buttons = (
                self.bold_button,
                self.italic_button,
                self.underline_button,
                self.ltr_button,
                self.rtl_button,
            )
            for button in buttons:
                button.blockSignals(True)
            self.bold_button.setChecked(character_format.fontWeight() >= 600)
            self.italic_button.setChecked(character_format.fontItalic())
            self.underline_button.setChecked(character_format.fontUnderline())
            is_rtl = (
                    cursor.blockFormat().layoutDirection()
                    == QtCore.Qt.LayoutDirection.RightToLeft
            )
            self.rtl_button.setChecked(is_rtl)
            self.ltr_button.setChecked(not is_rtl)
            for button in buttons:
                button.blockSignals(False)
            self.update_color_button(character_format.foreground().color())

        def toggle_theme(self, _checked: bool = False) -> None:
            self.dark_mode = not self.dark_mode
            application = QtWidgets.QApplication.instance()
            if application is not None:
                application.setProperty("darkTheme", self.dark_mode)
                application.setStyleSheet(app_stylesheet(self.dark_mode))
            settings = QtCore.QSettings(
                "WritingExerciseStudio",
                "Writing Exercise Studio",
            )
            settings.setValue("theme", "dark" if self.dark_mode else "light")
            self.update_theme_button()
            self.category_combo.update()
            self.update_format_toolbar()

        def update_theme_button(self) -> None:
            if self.dark_mode:
                self.theme_button.setText("☀")
                self.theme_button.setToolTip("Switch to light theme")
            else:
                self.theme_button.setText("☾")
                self.theme_button.setToolTip("Switch to dark theme")

        def ask_question(
                self,
                title: str,
                text: str,
                destructive: bool = False,
        ) -> bool:
            box = QtWidgets.QMessageBox(self)
            box.setWindowTitle(title)
            box.setText(text)
            box.setIcon(QtWidgets.QMessageBox.Icon.Question)
            box.setStandardButtons(
                QtWidgets.QMessageBox.StandardButton.Yes
                | QtWidgets.QMessageBox.StandardButton.No
            )
            box.setDefaultButton(QtWidgets.QMessageBox.StandardButton.No)
            yes_button = box.button(QtWidgets.QMessageBox.StandardButton.Yes)
            if yes_button is not None:
                yes_button.setObjectName(
                    "dangerButton" if destructive else "primaryButton"
                )
            return box.exec() == QtWidgets.QMessageBox.StandardButton.Yes

        def show_error(self, title: str, text: str) -> None:
            box = QtWidgets.QMessageBox(self)
            box.setWindowTitle(title)
            box.setText(text)
            box.setIcon(QtWidgets.QMessageBox.Icon.Critical)
            box.setStandardButtons(QtWidgets.QMessageBox.StandardButton.Ok)
            ok_button = box.button(QtWidgets.QMessageBox.StandardButton.Ok)
            if ok_button is not None:
                ok_button.setObjectName("primaryButton")
            box.exec()

        def current_exercise(self) -> Exercise | None:
            return next((item for item in self.exercises if item.id == self.current_id), None)

        def refresh_library(self) -> None:
            selected = self.current_id
            self.library.blockSignals(True)
            self.library.clear()
            groups: dict[str, list[Exercise]] = {}
            for exercise in self.exercises:
                category = exercise.category.strip() or "Uncategorized"
                groups.setdefault(category, []).append(exercise)
            selected_item = None
            for category in sorted(groups, key=str.casefold):
                exercises = sorted(
                    groups[category],
                    key=lambda item: item.updated_at,
                    reverse=True,
                )
                parent = QtWidgets.QTreeWidgetItem(
                    [f"{category} ({len(exercises)})"]
                )
                parent.setFlags(
                    parent.flags() & ~QtCore.Qt.ItemFlag.ItemIsSelectable
                )
                category_font = parent.font(0)
                category_font.setBold(True)
                parent.setFont(0, category_font)
                self.library.addTopLevelItem(parent)
                for exercise in exercises:
                    child = QtWidgets.QTreeWidgetItem([exercise.title])
                    child.setData(0, QtCore.Qt.ItemDataRole.UserRole, exercise.id)
                    parent.addChild(child)
                    if exercise.id == selected:
                        selected_item = child
            self.library.expandAll()
            if selected_item is not None:
                self.library.setCurrentItem(selected_item)
            self.library.blockSignals(False)

        def refresh_category_options(self, selected: str) -> None:
            categories = {
                exercise.category.strip() or "Uncategorized"
                for exercise in self.exercises
            }
            categories.add("Uncategorized")
            self.category_combo.blockSignals(True)
            self.category_combo.clear()
            self.category_combo.addItems(sorted(categories, key=str.casefold))
            self.category_combo.setEditText(selected)
            self.category_combo.blockSignals(False)

        def find_library_item(self, exercise_id: str) -> QtWidgets.QTreeWidgetItem | None:
            for parent_index in range(self.library.topLevelItemCount()):
                parent = self.library.topLevelItem(parent_index)
                for child_index in range(parent.childCount()):
                    child = parent.child(child_index)
                    if child.data(0, QtCore.Qt.ItemDataRole.UserRole) == exercise_id:
                        return child
            return None

        def load_exercise(self, exercise_id: str) -> None:
            exercise = next((item for item in self.exercises if item.id == exercise_id), None)
            if exercise is None:
                return
            self.pause_timer(save=False)
            self.loading = True
            self.current_id = exercise.id
            self.title_edit.setText(exercise.title)
            self.refresh_category_options(exercise.category)
            self.target_spin.setValue(exercise.target_words)
            if exercise.content_html:
                self.text_edit.setHtml(exercise.content_html)
            else:
                self.text_edit.setPlainText(exercise.content)
            self.search_edit.blockSignals(True)
            self.search_edit.clear()
            self.search_edit.blockSignals(False)
            self.highlight_query = ""
            self.highlight_exact = False
            self.text_edit.setExtraSelections([])
            self.search_summary.setText("0 matches")
            self.loading = False
            self.update_counts()
            self.update_format_toolbar()
            self.update_timer_display()
            library_item = self.find_library_item(exercise.id)
            if library_item is not None:
                self.library.blockSignals(True)
                self.library.setCurrentItem(library_item)
                self.library.blockSignals(False)
            self.text_edit.setFocus()
            self.statusBar().showMessage("Exercise opened", 2000)

        def library_selection_changed(self, current, _previous) -> None:
            if current is None:
                return
            exercise_id = current.data(0, QtCore.Qt.ItemDataRole.UserRole)
            if not exercise_id:
                return
            if exercise_id == self.current_id:
                return
            self.save_current(quiet=True)
            self.load_exercise(exercise_id)

        def new_exercise(self, _checked: bool = False) -> None:
            self.save_current(quiet=True)
            category = self.category_combo.currentText().strip() or "Uncategorized"
            exercise = Exercise.create(
                f"Writing Exercise {len(self.exercises) + 1}",
                category=category,
            )
            self.exercises.append(exercise)
            self.store.save(self.exercises)
            self.current_id = exercise.id
            self.refresh_library()
            self.load_exercise(exercise.id)
            self.title_edit.selectAll()
            self.title_edit.setFocus()
            self.statusBar().showMessage("New exercise created", 2000)

        def delete_exercise(self, _checked: bool = False) -> None:
            exercise = self.current_exercise()
            if exercise is None:
                return
            confirmed = self.ask_question(
                "Delete exercise",
                f'Delete "{exercise.title}"?\n\nThis cannot be undone.',
                destructive=True,
            )
            if not confirmed:
                return
            self.pause_timer(save=False)
            self.exercises = [item for item in self.exercises if item.id != exercise.id]
            if not self.exercises:
                self.exercises.append(Exercise.create())
            self.current_id = None
            self.store.save(self.exercises)
            next_exercise = sorted(self.exercises, key=lambda item: item.updated_at, reverse=True)[0]
            self.refresh_library()
            self.load_exercise(next_exercise.id)
            self.statusBar().showMessage("Exercise deleted", 2000)

        def text_changed(self) -> None:
            if self.loading:
                return
            self.update_counts()
            self.refresh_highlights()
            self.schedule_autosave()

        def content_changed(self, *_args) -> None:
            if self.loading:
                return
            self.update_counts()
            self.schedule_autosave()

        def update_counts(self) -> None:
            content = self.text_edit.toPlainText()
            words = count_words(content)
            characters = len(content)
            target = self.target_spin.value()
            percentage = min(100, round(words / target * 100))
            self.word_label.setText(f"{words:,} word" + ("" if words == 1 else "s"))
            self.character_label.setText(f"{characters:,} character" + ("" if characters == 1 else "s"))
            self.progress.setValue(percentage)
            self.progress_label.setText(f"{percentage}% of {target:,}-word target")
            self.update_repeated_words(content)

        def update_repeated_words(self, content: str) -> None:
            words = repeated_words(content)
            self.repeated_table.setUpdatesEnabled(False)
            self.repeated_table.setRowCount(len(words))
            for row, (word, count) in enumerate(words):
                word_item = QtWidgets.QTableWidgetItem(word)
                count_item = QtWidgets.QTableWidgetItem(str(count))
                count_item.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
                self.repeated_table.setItem(row, 0, word_item)
                self.repeated_table.setItem(row, 1, count_item)
            self.repeated_table.setUpdatesEnabled(True)
            if words:
                self.repeated_summary.setText(
                    f"{len(words):,} repeated word" + ("" if len(words) == 1 else "s")
                )
            else:
                self.repeated_summary.setText("No repeated words")

        def repeated_word_clicked(self, row: int, _column: int) -> None:
            word_item = self.repeated_table.item(row, 0)
            if word_item is None:
                return
            self.search_edit.blockSignals(True)
            self.search_edit.clear()
            self.search_edit.blockSignals(False)
            self.highlight_query = word_item.text()
            self.highlight_exact = True
            self.apply_highlights(scroll_to_first=True)

        def search_changed(self, query: str) -> None:
            self.highlight_query = query
            self.highlight_exact = False
            self.apply_highlights(scroll_to_first=bool(query.strip()))

        def refresh_highlights(self) -> None:
            if self.highlight_query:
                self.apply_highlights(scroll_to_first=False)

        def apply_highlights(self, scroll_to_first: bool = False) -> None:
            ranges = find_word_matches(
                self.text_edit.toPlainText(),
                self.highlight_query,
                exact=self.highlight_exact,
            )
            selections = []
            for start, end in ranges:
                selection = QtWidgets.QTextEdit.ExtraSelection()
                cursor = self.text_edit.textCursor()
                cursor.setPosition(start)
                cursor.setPosition(
                    end,
                    QtGui.QTextCursor.MoveMode.KeepAnchor,
                )
                selection.cursor = cursor
                selection.format.setBackground(QtGui.QColor("#ffd54f"))
                selection.format.setForeground(QtGui.QColor("#111111"))
                selections.append(selection)
            self.text_edit.setExtraSelections(selections)
            self.search_summary.setText(
                f"{len(ranges):,} match" + ("" if len(ranges) == 1 else "es")
            )
            if scroll_to_first and ranges:
                cursor = self.text_edit.textCursor()
                cursor.setPosition(ranges[0][0])
                self.text_edit.setTextCursor(cursor)
                self.text_edit.ensureCursorVisible()

        def schedule_autosave(self) -> None:
            self.statusBar().showMessage("Editing…")
            self.autosave_timer.start()

        def save_current(self, _checked: bool = False, quiet: bool = False) -> None:
            self.autosave_timer.stop()
            exercise = self.current_exercise()
            if exercise is None:
                return
            exercise.title = self.title_edit.text().strip() or "Untitled Exercise"
            exercise.category = (
                    self.category_combo.currentText().strip() or "Uncategorized"
            )
            exercise.content = self.text_edit.toPlainText()
            exercise.content_html = self.text_edit.toHtml()
            exercise.target_words = self.target_spin.value()
            if self.timer_started_at is not None:
                # Only whole seconds are stored, so keep the remainder running
                # instead of dropping it on every autosave.
                whole_seconds = int(time.monotonic() - self.timer_started_at)
                exercise.elapsed_seconds += whole_seconds
                self.timer_started_at += whole_seconds
            exercise.updated_at = utc_now()
            try:
                self.store.save(self.exercises)
                self.refresh_library()
                self.refresh_category_options(exercise.category)
                if not quiet:
                    self.statusBar().showMessage("Saved", 2000)
            except OSError as error:
                self.show_error(
                    "Save error",
                    f"The exercise could not be saved.\n\n{error}",
                )

        def elapsed_seconds(self) -> int:
            exercise = self.current_exercise()
            base = exercise.elapsed_seconds if exercise else 0
            if self.timer_started_at is not None:
                return base + int(time.monotonic() - self.timer_started_at)
            return base

        def toggle_timer(self, _checked: bool = False) -> None:
            if self.timer_started_at is None:
                self.timer_started_at = time.monotonic()
                self.timer_button.setText("Pause timer")
                self.clock_timer.start()
                self.statusBar().showMessage("Timer running")
            else:
                self.pause_timer(save=True)

        def pause_timer(self, save: bool = True) -> None:
            exercise = self.current_exercise()
            if exercise is not None and self.timer_started_at is not None:
                exercise.elapsed_seconds = self.elapsed_seconds()
            self.timer_started_at = None
            self.clock_timer.stop()
            self.timer_button.setText("Start timer")
            self.update_timer_display()
            if save and exercise is not None:
                self.save_current()

        def reset_timer(self, _checked: bool = False) -> None:
            exercise = self.current_exercise()
            if exercise is None:
                return
            if self.elapsed_seconds() > 0:
                confirmed = self.ask_question(
                    "Reset timer",
                    "Reset this exercise's timer to zero?",
                )
                if not confirmed:
                    return
            self.pause_timer(save=False)
            exercise.elapsed_seconds = 0
            self.update_timer_display()
            self.save_current()

        def update_timer_display(self) -> None:
            total = self.elapsed_seconds()
            hours, remainder = divmod(total, 3600)
            minutes, seconds = divmod(remainder, 60)
            self.timer_label.setText(f"{hours:02d}:{minutes:02d}:{seconds:02d}")

        def closeEvent(self, event: QtGui.QCloseEvent) -> None:
            self.pause_timer(save=False)
            self.save_current(quiet=True)
            event.accept()


def main() -> None:
    if QtWidgets is None:
        raise SystemExit(
            "PySide6 is required for the desktop interface.\n"
            "Install it with:\n\n"
            "    python3 -m pip install -r requirements.txt\n"
        )
    application = QtWidgets.QApplication(sys.argv)
    application.setApplicationName(APP_NAME)
    application.setStyle("Fusion")
    settings = QtCore.QSettings(
        "WritingExerciseStudio",
        "Writing Exercise Studio",
    )
    dark_mode = settings.value("theme", "light") == "dark"
    application.setProperty("darkTheme", dark_mode)
    application.setStyleSheet(app_stylesheet(dark_mode))
    window = WritingExerciseApp()
    window.show()
    raise SystemExit(application.exec())


if __name__ == "__main__":
    main()
