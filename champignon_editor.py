#!/usr/bin/env python3
"""
Champignon Code Editor
A code editor with advanced OpenType shaping support for the Champignon font.
"""

import sys
import json
import os
from pathlib import Path
from typing import List, Tuple
import ctypes
import subprocess
import tempfile
from dataclasses import dataclass
from enum import Enum

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTextEdit, QPlainTextEdit, QLabel, QFileDialog, QMenu, QMenuBar,
    QStatusBar, QPushButton, QScrollArea, QComboBox, QSpinBox, QCheckBox,
    QSplitter, QDialog, QMessageBox, QLineEdit
)
from PyQt6.QtCore import Qt, QSize, QRect, QPoint, QTimer, pyqtSignal, QRegularExpression, QProcess
from PyQt6.QtGui import (
    QPainter, QFont, QFontInfo, QColor, QPen, QBrush, QPixmap,
    QTextCursor, QKeySequence, QIcon, QAction, QTextDocument,
    QSyntaxHighlighter, QTextCharFormat
)
from PyQt6.QtCore import QThread, pyqtSignal as Signal

class SyntaxHighlighter(QSyntaxHighlighter):
    """Syntax highlighter for code."""

    def __init__(self, document):
        super().__init__(document)
        self.setup_rules()

    # Control-flow / structural keywords (blue)
    KEYWORDS = {
        "def", "return", "if", "elif", "else", "for", "while", "break",
        "continue", "pass", "class", "import", "from", "as", "try",
        "except", "finally", "with", "yield", "lambda", "global",
        "nonlocal", "raise", "assert", "del", "in", "is", "and", "or",
        "not", "async", "await",
        "function", "const", "let", "var", "static", "public", "private",
        "protected", "void", "new", "switch", "case", "do", "struct", "enum",
    }
    # Literals / constants (teal)
    CONSTANTS = {"True", "False", "None", "self", "cls", "true", "false", "null", "nil", "undefined"}
    # Common builtins (soft blue)
    BUILTINS = {
        "print", "input", "int", "str", "float", "bool", "list", "dict",
        "set", "tuple", "len", "range", "enumerate", "zip", "map", "filter",
        "sum", "min", "max", "abs", "round", "sorted", "reversed", "open",
        "type", "isinstance", "super", "format",
    }

    def setup_rules(self):
        """Create reusable character formats."""
        def fmt(color, bold=False, italic=False):
            f = QTextCharFormat()
            f.setForeground(QColor(color))
            if bold:
                f.setFontWeight(700)
            if italic:
                f.setFontItalic(True)
            return f

        self.keyword_format = fmt("#569CD6", bold=True)   # blue
        self.constant_format = fmt("#4EC9B0")             # teal
        self.builtin_format = fmt("#4FC1FF")              # soft blue
        self.string_format = fmt("#CE9178")               # orange
        self.number_format = fmt("#B5CEA8")               # light green
        self.comment_format = fmt("#6A9955", italic=True)  # green
        self.function_format = fmt("#DCDCAA")             # yellow

        self.ident_re = QRegularExpression(r"[A-Za-z_][A-Za-z0-9_]*")
        self.number_re = QRegularExpression(r"\b(0[xX][0-9A-Fa-f]+|\d+\.?\d*)\b")
        self.func_re = QRegularExpression(r"\b([A-Za-z_][A-Za-z0-9_]*)\s*\(")

    def highlightBlock(self, text):
        """Highlight one line, respecting string and comment boundaries.

        A single left-to-right scan finds string spans and the comment start so
        that code rules never recolor text inside a string or comment, and the
        whole comment stays one color.
        """
        n = len(text)
        string_spans = []      # (start, length)
        comment_start = None

        i = 0
        while i < n:
            ch = text[i]
            if ch == '#' or (ch == '/' and i + 1 < n and text[i + 1] == '/'):
                comment_start = i
                break
            if ch in ('"', "'", '`'):
                quote = ch
                j = i + 1
                while j < n and text[j] != quote:
                    j += 2 if text[j] == '\\' else 1
                end = min(j + 1, n)
                string_spans.append((i, end - i))
                i = end
                continue
            i += 1

        code_end = comment_start if comment_start is not None else n

        def in_string(pos):
            return any(s <= pos < s + l for s, l in string_spans)

        # Numbers (code region only, not inside strings)
        it = self.number_re.globalMatch(text)
        while it.hasNext():
            m = it.next()
            s = m.capturedStart()
            if s < code_end and not in_string(s):
                self.setFormat(s, m.capturedLength(), self.number_format)

        # Function/method names: word immediately before '('
        it = self.func_re.globalMatch(text)
        while it.hasNext():
            m = it.next()
            s = m.capturedStart(1)
            if s < code_end and not in_string(s):
                name = m.captured(1)
                if name not in self.KEYWORDS:
                    fmt = self.builtin_format if name in self.BUILTINS else self.function_format
                    self.setFormat(s, m.capturedLength(1), fmt)

        # Identifiers: keywords / constants / builtins
        it = self.ident_re.globalMatch(text)
        while it.hasNext():
            m = it.next()
            s = m.capturedStart()
            if s >= code_end or in_string(s):
                continue
            word = m.captured()
            if word in self.KEYWORDS:
                self.setFormat(s, m.capturedLength(), self.keyword_format)
            elif word in self.CONSTANTS:
                self.setFormat(s, m.capturedLength(), self.constant_format)
            elif word in self.BUILTINS:
                self.setFormat(s, m.capturedLength(), self.builtin_format)

        # Strings (overwrite anything the code rules touched)
        for s, l in string_spans:
            self.setFormat(s, l, self.string_format)

        # Comment wins over everything, to end of line
        if comment_start is not None:
            self.setFormat(comment_start, n - comment_start, self.comment_format)


class HarfBuzzShaper:
    """Interface to HarfBuzz for text shaping."""

    def __init__(self, font_family: str, font_size: int, features: List[str] = None):
        self.font_family = font_family
        self.font_size = font_size
        self.features = features or ["ccmp", "liga"]
        self.hb_lib = None
        self._load_harfbuzz()

    def _load_harfbuzz(self):
        """Load HarfBuzz library."""
        try:
            self.hb_lib = ctypes.CDLL("libharfbuzz.so.0")
        except (OSError, AttributeError):
            # Fallback if library not available
            self.hb_lib = None

    def shape_text(self, text: str) -> List[Tuple[str, float, float]]:
        """
        Shape text using HarfBuzz.
        Returns list of (glyph_id, x_advance, y_advance)

        Falls back to simple character iteration if HarfBuzz unavailable.
        """
        if not text:
            return []

        # Try to use hb-shape command-line tool if HarfBuzz library unavailable
        if self.hb_lib is None:
            return self._shape_with_subprocess(text)

        # For now, do simple grapheme splitting with advance widths
        # This is a simplified implementation
        return [(c, self.font_size * 0.6, 0) for c in text]

    def _shape_with_subprocess(self, text: str) -> List[Tuple[str, float, float]]:
        """Fallback shaping using hb-shape command."""
        try:
            font_path = self._find_font()
            if not font_path:
                return [(c, self.font_size * 0.6, 0) for c in text]

            # Build feature string
            feature_str = ",".join(self.features)

            # Call hb-shape
            result = subprocess.run(
                ["hb-shape", f"--features={feature_str}", str(font_path)],
                input=text,
                capture_output=True,
                text=True,
                timeout=1
            )

            if result.returncode == 0:
                return self._parse_hb_output(result.stdout)
        except (FileNotFoundError, subprocess.TimeoutExpired, Exception):
            pass

        # Fallback
        return [(c, self.font_size * 0.6, 0) for c in text]

    def _find_font(self) -> str:
        """Find font path using fc-match."""
        try:
            result = subprocess.run(
                ["fc-match", "-f", "%{file}", self.font_family],
                capture_output=True,
                text=True,
                timeout=1
            )
            if result.returncode == 0:
                return result.stdout.strip()
        except Exception:
            pass
        return None

    def _parse_hb_output(self, output: str) -> List[Tuple[str, float, float]]:
        """Parse hb-shape output."""
        glyphs = []
        for line in output.strip().split('\n'):
            if not line:
                continue
            # hb-shape format: [glyph_name]|x_advance|y_advance|...
            parts = line.split('|')
            if len(parts) >= 3:
                try:
                    x_adv = float(parts[1])
                    y_adv = float(parts[2])
                    glyphs.append((parts[0], x_adv / 64.0, y_adv / 64.0))
                except (ValueError, IndexError):
                    glyphs.append((parts[0], self.font_size * 0.6, 0))
        return glyphs


class CustomTextEdit(QPlainTextEdit):
    """Custom text editor with custom rendering capabilities."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.shaper = None
        self.show_line_numbers = True
        self.line_number_width = 50
        self.current_font_size = 14

        # Configure font
        font = QFont("Champignon")
        font.setPointSize(14)
        self.setFont(font)

        # Colors
        self.bg_color = QColor("#1e1e1e")
        self.text_color = QColor("#e0e0e0")
        self.line_number_color = QColor("#858585")
        self.line_number_bg = QColor("#252526")

        self.setStyleSheet(f"""
            QPlainTextEdit {{
                background-color: {self.bg_color.name()};
                color: {self.text_color.name()};
                line-height: 1.6;
                margin: 0px;
                padding: 4px;
            }}
        """)

        self.setCursorWidth(2)
        self.setTabStopDistance(40)

        # Initialize shaper
        self.shaper = HarfBuzzShaper("Champignon", 14, ["ccmp", "liga"])

        # Add syntax highlighter
        self.highlighter = SyntaxHighlighter(self.document())

    def update_font(self, font_family: str, font_size: int, features: List[str]):
        """Update font and shaper configuration."""
        self.current_font_size = font_size
        font = QFont(font_family)
        font.setPointSize(font_size)
        font.setStyleStrategy(QFont.StyleStrategy.PreferAntialias)
        self.setFont(font)
        self.shaper = HarfBuzzShaper(font_family, font_size, features)
        # Force repaint
        self.viewport().update()

    def keyPressEvent(self, event):
        """Handle keyboard input."""
        if event.key() == Qt.Key.Key_Tab:
            # Insert spaces instead of tab
            cursor = self.textCursor()
            cursor.insertText("    ")
        elif event.key() == Qt.Key.Key_Return:
            # Smart indent
            super().keyPressEvent(event)
            self._auto_indent()
        else:
            super().keyPressEvent(event)

    def _auto_indent(self):
        """Auto-indent new lines."""
        cursor = self.textCursor()
        block = cursor.block()
        prev_block = block.previous()

        if prev_block.isValid():
            prev_text = prev_block.text()
            indent = len(prev_text) - len(prev_text.lstrip())
            cursor.insertText(" " * indent)
            self.setTextCursor(cursor)


class ChamignionEditor(QMainWindow):
    """Main editor window."""

    def __init__(self):
        super().__init__()
        self.config = self._load_config()
        self.current_file = None
        self.unsaved = False
        self.process = None
        self._temp_paths = []

        self._setup_ui()
        self._setup_menu()
        self._setup_test_content()

        self.setWindowTitle("Champignon Editor")
        self.setGeometry(100, 100, 1200, 800)
        self.show()

    def _load_config(self) -> dict:
        """Load configuration from config.json."""
        config_path = Path(__file__).parent / "config.json"
        if config_path.exists():
            with open(config_path) as f:
                return json.load(f)
        return {
            "fontFamily": "Champignon",
            "fontSize": 14,
            "fontFeatures": ["ccmp", "liga"],
            "theme": "dark"
        }

    def _setup_ui(self):
        """Setup user interface."""
        main_widget = QWidget()
        self.setCentralWidget(main_widget)

        layout = QVBoxLayout(main_widget)
        layout.setContentsMargins(0, 0, 0, 0)

        # Toolbar
        toolbar_layout = QHBoxLayout()

        # Font selector
        toolbar_layout.addWidget(QLabel("Font:"))
        font_combo = QComboBox()
        font_combo.addItems(["Champignon", "Courier", "Monospace"])
        font_combo.currentTextChanged.connect(self._on_font_changed)
        toolbar_layout.addWidget(font_combo)

        # Font size
        toolbar_layout.addWidget(QLabel("Size:"))
        size_spin = QSpinBox()
        size_spin.setMinimum(8)
        size_spin.setMaximum(48)
        size_spin.setValue(self.config.get("fontSize", 14))
        size_spin.valueChanged.connect(self._on_size_changed)
        toolbar_layout.addWidget(size_spin)

        # Features
        toolbar_layout.addWidget(QLabel("Features:"))
        self.liga_check = QCheckBox("Ligatures")
        self.liga_check.setChecked(True)
        self.liga_check.stateChanged.connect(self._on_features_changed)
        toolbar_layout.addWidget(self.liga_check)

        self.calt_check = QCheckBox("Contextual")
        self.calt_check.setChecked(False)
        self.calt_check.stateChanged.connect(self._on_features_changed)
        toolbar_layout.addWidget(self.calt_check)

        # Run button
        run_button = QPushButton("▶ Run")
        run_button.setStyleSheet("QPushButton { background-color: #27ae60; color: white; padding: 5px; border-radius: 3px; font-weight: bold; }")
        run_button.clicked.connect(self._run_code)
        toolbar_layout.addWidget(run_button)

        # Stop button
        self.stop_button = QPushButton("■ Stop")
        self.stop_button.setStyleSheet("QPushButton { background-color: #c0392b; color: white; padding: 5px; border-radius: 3px; font-weight: bold; } QPushButton:disabled { background-color: #555; }")
        self.stop_button.clicked.connect(self._stop_code)
        self.stop_button.setEnabled(False)
        toolbar_layout.addWidget(self.stop_button)

        toolbar_layout.addStretch()

        layout.addLayout(toolbar_layout)

        # Splitter for editor and output
        splitter = QSplitter(Qt.Orientation.Vertical)

        # Text editor
        self.editor = CustomTextEdit()
        self.editor.textChanged.connect(self._on_text_changed)
        splitter.addWidget(self.editor)

        # Interactive input (stdin) row
        input_row = QWidget()
        input_row_layout = QHBoxLayout(input_row)
        input_row_layout.setContentsMargins(0, 0, 0, 0)
        input_row_layout.addWidget(QLabel("stdin ▸"))
        self.input_line = QLineEdit()
        self.input_line.setPlaceholderText("Type input here and press Enter while the program is running")
        self.input_line.setStyleSheet("QLineEdit { background-color: #1e1e1e; color: #d4d4d4; font-family: Courier; font-size: 10pt; padding: 4px; }")
        self.input_line.returnPressed.connect(self._send_input)
        self.input_line.setEnabled(False)
        input_row_layout.addWidget(self.input_line)
        send_button = QPushButton("Send")
        send_button.clicked.connect(self._send_input)
        input_row_layout.addWidget(send_button)
        splitter.addWidget(input_row)

        # Output panel
        self.output_panel = QPlainTextEdit()
        self.output_panel.setReadOnly(True)
        self.output_panel.setMaximumHeight(150)
        self.output_panel.setStyleSheet("""
            QPlainTextEdit {
                background-color: #000000;
                color: #00FF00;
                font-family: Courier;
                font-size: 10pt;
            }
        """)
        self.output_panel.setPlainText("Output will appear here...\n")
        splitter.addWidget(self.output_panel)

        splitter.setStretchFactor(0, 4)
        splitter.setStretchFactor(1, 0)
        splitter.setStretchFactor(2, 2)

        layout.addWidget(splitter)

        # Status bar
        self.statusBar().showMessage("Ready")

    def _setup_menu(self):
        """Setup menu bar."""
        menubar = self.menuBar()

        # File menu
        file_menu = menubar.addMenu("&File")

        new_action = QAction("&New", self)
        new_action.setShortcut(QKeySequence.StandardKey.New)
        new_action.triggered.connect(self._new_file)
        file_menu.addAction(new_action)

        open_action = QAction("&Open", self)
        open_action.setShortcut(QKeySequence.StandardKey.Open)
        open_action.triggered.connect(self._open_file)
        file_menu.addAction(open_action)

        save_action = QAction("&Save", self)
        save_action.setShortcut(QKeySequence.StandardKey.Save)
        save_action.triggered.connect(self._save_file)
        file_menu.addAction(save_action)

        save_as_action = QAction("Save &As...", self)
        save_as_action.setShortcut(QKeySequence.StandardKey.SaveAs)
        save_as_action.triggered.connect(self._save_file_as)
        file_menu.addAction(save_as_action)

        file_menu.addSeparator()

        exit_action = QAction("E&xit", self)
        exit_action.setShortcut(QKeySequence.StandardKey.Quit)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Edit menu
        edit_menu = menubar.addMenu("&Edit")

        undo_action = QAction("&Undo", self)
        undo_action.setShortcut(QKeySequence.StandardKey.Undo)
        undo_action.triggered.connect(self.editor.undo)
        edit_menu.addAction(undo_action)

        redo_action = QAction("&Redo", self)
        redo_action.setShortcut(QKeySequence.StandardKey.Redo)
        redo_action.triggered.connect(self.editor.redo)
        edit_menu.addAction(redo_action)

        edit_menu.addSeparator()

        select_all_action = QAction("Select &All", self)
        select_all_action.setShortcut(QKeySequence.StandardKey.SelectAll)
        select_all_action.triggered.connect(self.editor.selectAll)
        edit_menu.addAction(select_all_action)

    def _setup_test_content(self):
        """Setup test content."""
        test_code = """ABCDEFGHIJKLMNOPQRSTUVWXYZ
abcdefghijklmnopqrstuvwxyz

HelloWorld
hello world
aaaa bbbb cccc
Sphinx of black quartz, judge my vow.

function test() {
    const message = "Hello world";
    return message;
}

á é í ó ú
Á É Í Ó Ú

1234567890
!@#$%^&*()_+-=[]{};:'",.<>/?\\|
"""
        self.editor.setPlainText(test_code)

    def _on_text_changed(self):
        """Handle text changes."""
        if not self.unsaved:
            self.unsaved = True
            title = self.windowTitle()
            if not title.endswith("*"):
                self.setWindowTitle(title + "*")

    def _on_font_changed(self, font_family: str):
        """Handle font family change."""
        self.editor.update_font(
            font_family,
            self.config.get("fontSize", 14),
            self._get_features()
        )

    def _on_size_changed(self, size: int):
        """Handle font size change."""
        self.config["fontSize"] = size
        # Directly update the editor font
        font = QFont(self.config.get("fontFamily", "Champignon"))
        font.setPointSize(size)
        font.setStyleStrategy(QFont.StyleStrategy.PreferAntialias)
        self.editor.setFont(font)
        self.editor.current_font_size = size
        # Update shaper
        self.editor.shaper = HarfBuzzShaper(
            self.config.get("fontFamily", "Champignon"),
            size,
            self._get_features()
        )
        # Force repaint
        self.editor.viewport().update()

    def _on_features_changed(self):
        """Handle feature changes."""
        features = self._get_features()
        self.config["fontFeatures"] = features
        self.editor.update_font(
            self.config.get("fontFamily", "Champignon"),
            self.config.get("fontSize", 14),
            features
        )

    def _get_features(self) -> List[str]:
        """Get current feature list."""
        features = ["ccmp"]
        if self.liga_check.isChecked():
            features.append("liga")
        if self.calt_check.isChecked():
            features.append("calt")
        return features

    def _new_file(self):
        """Create new file."""
        self.editor.clear()
        self.current_file = None
        self.unsaved = False
        self.setWindowTitle("Champignon Editor")

    def _open_file(self):
        """Open file dialog."""
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Open File",
            "",
            "All Files (*);;Code Files (*.py *.js *.cpp *.h)"
        )
        if path:
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    content = f.read()
                self.editor.setPlainText(content)
                self.current_file = path
                self.unsaved = False
                self.setWindowTitle(f"Champignon Editor - {Path(path).name}")
                self.statusBar().showMessage(f"Opened: {path}")
            except Exception as e:
                self.statusBar().showMessage(f"Error opening file: {e}")

    def _save_file(self):
        """Save current file."""
        if self.current_file:
            self._save_to_path(self.current_file)
        else:
            self._save_file_as()

    def _save_file_as(self):
        """Save as dialog."""
        path, _ = QFileDialog.getSaveFileName(
            self,
            "Save File",
            "",
            "All Files (*);;Python (*.py);;JavaScript (*.js);;C++ (*.cpp)"
        )
        if path:
            self._save_to_path(path)

    def _save_to_path(self, path: str):
        """Save content to file."""
        try:
            with open(path, 'w', encoding='utf-8') as f:
                f.write(self.editor.toPlainText())
            self.current_file = path
            self.unsaved = False
            self.setWindowTitle(f"Champignon Editor - {Path(path).name}")
            self.statusBar().showMessage(f"Saved: {path}")
        except Exception as e:
            self.statusBar().showMessage(f"Error saving file: {e}")

    def _detect_language(self) -> str:
        """Detect programming language from file extension or content."""
        if self.current_file:
            ext = Path(self.current_file).suffix.lower()
            ext_map = {
                '.py': 'python',
                '.js': 'javascript',
                '.mjs': 'javascript',
                '.ts': 'typescript',
                '.cpp': 'cpp',
                '.cc': 'cpp',
                '.cxx': 'cpp',
                '.c++': 'cpp',
                '.c': 'c',
                '.h': 'c',
                '.hpp': 'cpp',
                '.rs': 'rust',
                '.lua': 'lua',
                '.java': 'java',
                '.go': 'go',
                '.rb': 'ruby',
                '.php': 'php',
                '.sh': 'bash',
                '.bash': 'bash',
                '.swift': 'swift',
                '.kt': 'kotlin',
                '.scala': 'scala',
                '.pl': 'perl',
                '.r': 'r',
                '.jl': 'julia',
                '.m': 'objc',
            }
            if ext in ext_map:
                return ext_map[ext]

        # Try to detect from content
        content = self.editor.toPlainText()[:200].lower()

        detections = [
            ('def ' or 'import ', 'python'),
            ('fn main' or 'fn ', 'rust'),
            ('local ' or 'function ', 'lua'),
            ('function ' or 'const ' or 'let ', 'javascript'),
            ('async fn', 'rust'),
            ('#include', 'cpp'),
            ('func ', 'go'),
            ('def ', 'ruby'),
            ('<?php', 'php'),
            ('#!/bin/bash', 'bash'),
        ]

        for keyword, lang in detections:
            if isinstance(keyword, str) and keyword in content:
                return lang

        return 'python'  # Default to Python

    LANG_CONFIG = {
        'python':     {'suffix': '.py',    'cmd': lambda f: ('python3', [f])},
        'javascript': {'suffix': '.js',    'cmd': lambda f: ('node', [f])},
        'typescript': {'suffix': '.ts',    'cmd': lambda f: ('npx', ['ts-node', f])},
        'lua':        {'suffix': '.lua',   'cmd': lambda f: ('lua', [f])},
        'go':         {'suffix': '.go',    'cmd': lambda f: ('go', ['run', f])},
        'ruby':       {'suffix': '.rb',    'cmd': lambda f: ('ruby', [f])},
        'php':        {'suffix': '.php',   'cmd': lambda f: ('php', [f])},
        'bash':       {'suffix': '.sh',    'cmd': lambda f: ('bash', [f])},
        'swift':      {'suffix': '.swift', 'cmd': lambda f: ('swift', [f])},
    }

    COMPILE_CONFIG = {
        'cpp':  {'suffix': '.cpp', 'compiler': lambda src, exe: ['g++', src, '-o', exe]},
        'c':    {'suffix': '.c',   'compiler': lambda src, exe: ['gcc', src, '-o', exe]},
        'rust': {'suffix': '.rs',  'compiler': lambda src, exe: ['rustc', src, '-o', exe]},
    }

    def _run_code(self):
        """Execute the code in the editor interactively."""
        if self.process is not None:
            self.output_panel.appendPlainText("\n[A program is already running - press Stop first]")
            return

        code = self.editor.toPlainText()
        if not code.strip():
            self.output_panel.setPlainText("Error: No code to run\n")
            return

        language = self._detect_language()

        if language in ('java', 'kotlin'):
            self.output_panel.setPlainText(
                f"Error: {language.title()} needs a full JVM build setup and isn't supported in quick-run mode.\n")
            return

        if language in self.COMPILE_CONFIG:
            program, args = self._compile(language, code)
            if program is None:
                return
        elif language in self.LANG_CONFIG:
            cfg = self.LANG_CONFIG[language]
            try:
                path = self._write_temp(code, cfg['suffix'])
            except Exception as e:
                self.output_panel.setPlainText(f"Error: {e}\n")
                return
            program, args = cfg['cmd'](path)
        else:
            self.output_panel.setPlainText(f"Error: Language '{language}' not supported yet\n")
            return

        self._start_process(program, args, language)

    def _write_temp(self, code: str, suffix: str) -> str:
        with tempfile.NamedTemporaryFile(mode='w', suffix=suffix, delete=False) as f:
            f.write(code)
            path = f.name
        self._temp_paths.append(path)
        return path

    def _compile(self, language: str, code: str):
        """Compile source; return (exe, []) to run, or (None, None) on failure."""
        cfg = self.COMPILE_CONFIG[language]
        try:
            src = self._write_temp(code, cfg['suffix'])
        except Exception as e:
            self.output_panel.setPlainText(f"Error: {e}\n")
            return None, None
        exe = src[: -len(cfg['suffix'])]
        self._temp_paths.append(exe)
        self.output_panel.setPlainText(f"Compiling {language}...\n")
        self.statusBar().showMessage(f"Compiling {language}...")
        QApplication.processEvents()
        compiler_cmd = cfg['compiler'](src, exe)
        try:
            result = subprocess.run(compiler_cmd, capture_output=True, text=True, timeout=60)
        except FileNotFoundError:
            self.output_panel.setPlainText(f"Error: '{compiler_cmd[0]}' not found. Install the {language} toolchain.\n")
            self._cleanup_temps()
            return None, None
        except subprocess.TimeoutExpired:
            self.output_panel.setPlainText("Error: Compilation timed out (60s limit)\n")
            self._cleanup_temps()
            return None, None
        if result.returncode != 0:
            self.output_panel.setPlainText(f"Compilation Error:\n{result.stderr}\n")
            self.statusBar().showMessage("Compilation failed")
            self._cleanup_temps()
            return None, None
        return exe, []

    def _start_process(self, program: str, args, language: str):
        self.output_panel.setPlainText("")
        self.statusBar().showMessage(f"Running {language}...")
        self.process = QProcess(self)
        self.process.setProcessChannelMode(QProcess.ProcessChannelMode.MergedChannels)
        self.process.readyReadStandardOutput.connect(self._on_process_output)
        self.process.finished.connect(self._on_process_finished)
        self.process.errorOccurred.connect(self._on_process_error)
        self.input_line.setEnabled(True)
        self.stop_button.setEnabled(True)
        self.input_line.setFocus()
        self.process.start(program, args)

    def _on_process_output(self):
        if self.process is None:
            return
        data = bytes(self.process.readAllStandardOutput()).decode(errors='replace')
        if data:
            self.output_panel.moveCursor(QTextCursor.MoveOperation.End)
            self.output_panel.insertPlainText(data)
            self.output_panel.moveCursor(QTextCursor.MoveOperation.End)

    def _send_input(self):
        if self.process is None or self.process.state() != QProcess.ProcessState.Running:
            return
        line = self.input_line.text()
        self.process.write((line + "\n").encode())
        self.output_panel.moveCursor(QTextCursor.MoveOperation.End)
        self.output_panel.insertPlainText(line + "\n")
        self.output_panel.moveCursor(QTextCursor.MoveOperation.End)
        self.input_line.clear()

    def _on_process_error(self, err):
        if self.process is None:
            return
        if err == QProcess.ProcessError.FailedToStart:
            self.output_panel.appendPlainText(
                "\n[Failed to start - is the interpreter/runtime installed and on your PATH?]")
            self._finish_run("failed to start")

    def _on_process_finished(self, exit_code, _status):
        if self.process is None:
            return
        self._on_process_output()
        self.output_panel.moveCursor(QTextCursor.MoveOperation.End)
        self.output_panel.insertPlainText(f"\n[Process finished with exit code {exit_code}]\n")
        self._finish_run(f"finished (exit {exit_code})")

    def _stop_code(self):
        if self.process is not None:
            self.process.kill()
            self.output_panel.appendPlainText("\n[Stopped by user]")
            self._finish_run("stopped")

    def _finish_run(self, status_msg: str):
        self.statusBar().showMessage(f"Program {status_msg}")
        self.input_line.setEnabled(False)
        self.stop_button.setEnabled(False)
        self.process = None
        self._cleanup_temps()

    def _cleanup_temps(self):
        for p in self._temp_paths:
            try:
                if os.path.exists(p):
                    os.unlink(p)
            except OSError:
                pass
        self._temp_paths = []




def main():
    app = QApplication(sys.argv)
    editor = ChamignionEditor()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
