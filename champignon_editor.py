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
    QSplitter, QDialog, QMessageBox
)
from PyQt6.QtCore import Qt, QSize, QRect, QPoint, QTimer, pyqtSignal, QRegularExpression
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

    def setup_rules(self):
        """Setup syntax highlighting rules."""
        # Keywords
        keyword_format = QTextCharFormat()
        keyword_format.setForeground(QColor("#569CD6"))  # Blue
        keyword_format.setFontWeight(700)

        keywords = [
            "\\bfunction\\b", "\\breturn\\b", "\\bif\\b", "\\belse\\b",
            "\\bfor\\b", "\\bwhile\\b", "\\bclass\\b", "\\bdef\\b",
            "\\bimport\\b", "\\bfrom\\b", "\\bas\\b", "\\btry\\b",
            "\\bexcept\\b", "\\bfinally\\b", "\\bwith\\b", "\\byield\\b",
            "\\blambda\\b", "\\btrue\\b", "\\bfalse\\b", "\\bTrue\\b",
            "\\bFalse\\b", "\\bNone\\b", "\\bself\\b", "\\bcls\\b",
            "\\bconst\\b", "\\blet\\b", "\\bvar\\b", "\\bint\\b",
            "\\bchar\\b", "\\bvoid\\b", "\\bstatic\\b", "\\bpublic\\b",
            "\\bprivate\\b", "\\bprotected\\b"
        ]

        self.keyword_rules = [(QRegularExpression(kw), keyword_format) for kw in keywords]

        # Strings
        string_format = QTextCharFormat()
        string_format.setForeground(QColor("#CE9178"))  # Orange

        self.string_rules = [
            (QRegularExpression('"[^"]*"'), string_format),
            (QRegularExpression("'[^']*'"), string_format),
            (QRegularExpression("`[^`]*`"), string_format),
        ]

        # Numbers
        number_format = QTextCharFormat()
        number_format.setForeground(QColor("#B5CEA8"))  # Green

        self.number_rules = [
            (QRegularExpression("\\b\\d+\\.?\\d*\\b"), number_format),
            (QRegularExpression("\\b0x[0-9A-Fa-f]+\\b"), number_format),
        ]

        # Comments
        comment_format = QTextCharFormat()
        comment_format.setForeground(QColor("#6A9955"))  # Dark green
        comment_format.setFontItalic(True)

        self.comment_rules = [
            (QRegularExpression("//[^\n]*"), comment_format),
            (QRegularExpression("#[^\n]*"), comment_format),
        ]

        # Functions/Methods
        function_format = QTextCharFormat()
        function_format.setForeground(QColor("#DCDCAA"))  # Yellow
        self.function_format = function_format

        # Operators
        operator_format = QTextCharFormat()
        operator_format.setForeground(QColor("#D4D4D4"))  # Light gray
        self.operator_format = operator_format

    def highlightBlock(self, text):
        """Highlight a block of text."""
        # Apply keyword rules
        for pattern, format in self.keyword_rules:
            iterator = pattern.globalMatch(text)
            while iterator.hasNext():
                match = iterator.next()
                self.setFormat(match.capturedStart(), match.capturedLength(), format)

        # Apply string rules
        for pattern, format in self.string_rules:
            iterator = pattern.globalMatch(text)
            while iterator.hasNext():
                match = iterator.next()
                self.setFormat(match.capturedStart(), match.capturedLength(), format)

        # Apply number rules
        for pattern, format in self.number_rules:
            iterator = pattern.globalMatch(text)
            while iterator.hasNext():
                match = iterator.next()
                self.setFormat(match.capturedStart(), match.capturedLength(), format)

        # Apply comment rules
        for pattern, format in self.comment_rules:
            iterator = pattern.globalMatch(text)
            while iterator.hasNext():
                match = iterator.next()
                self.setFormat(match.capturedStart(), match.capturedLength(), format)

        # Highlight function/method names (pattern: word followed by parenthesis)
        func_pattern = QRegularExpression("\\b([a-zA-Z_][a-zA-Z0-9_]*)\\s*\\(")
        iterator = func_pattern.globalMatch(text)
        while iterator.hasNext():
            match = iterator.next()
            self.setFormat(match.capturedStart(1), match.capturedLength(1), self.function_format)


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

        toolbar_layout.addStretch()

        layout.addLayout(toolbar_layout)

        # Splitter for editor and output
        splitter = QSplitter(Qt.Orientation.Vertical)

        # Text editor
        self.editor = CustomTextEdit()
        self.editor.textChanged.connect(self._on_text_changed)
        splitter.addWidget(self.editor)

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

        splitter.setStretchFactor(0, 3)
        splitter.setStretchFactor(1, 1)

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

    def _run_code(self):
        """Execute the code in the editor."""
        code = self.editor.toPlainText()
        if not code.strip():
            self.output_panel.setPlainText("Error: No code to run\n")
            return

        language = self._detect_language()
        self.statusBar().showMessage(f"Running {language} code...")

        try:
            language_runners = {
                'python': self._run_python,
                'javascript': self._run_javascript,
                'typescript': self._run_typescript,
                'cpp': self._run_cpp,
                'c': self._run_c,
                'rust': self._run_rust,
                'lua': self._run_lua,
                'go': self._run_go,
                'ruby': self._run_ruby,
                'php': self._run_php,
                'bash': self._run_bash,
                'java': self._run_java,
                'swift': self._run_swift,
                'kotlin': self._run_kotlin,
            }

            if language in language_runners:
                language_runners[language](code)
            else:
                self.output_panel.setPlainText(f"Error: Language '{language}' not supported yet\n")
                self.statusBar().showMessage(f"Language not supported: {language}")
        except Exception as e:
            self.output_panel.setPlainText(f"Error: {str(e)}\n")
            self.statusBar().showMessage(f"Execution failed: {e}")

    def _run_python(self, code: str):
        """Run Python code."""
        try:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                f.write(code)
                temp_file = f.name

            result = subprocess.run(
                ['python3', temp_file],
                capture_output=True,
                text=True,
                timeout=30
            )

            output = result.stdout
            if result.stderr:
                output += f"\n[STDERR]\n{result.stderr}"

            self.output_panel.setPlainText(output if output else "(No output)\n")
            self.statusBar().showMessage("Python execution complete")

            os.unlink(temp_file)
        except subprocess.TimeoutExpired:
            self.output_panel.setPlainText("Error: Code execution timed out (30s limit)\n")
        except Exception as e:
            self.output_panel.setPlainText(f"Error: {str(e)}\n")

    def _run_javascript(self, code: str):
        """Run JavaScript code."""
        try:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.js', delete=False) as f:
                f.write(code)
                temp_file = f.name

            result = subprocess.run(
                ['node', temp_file],
                capture_output=True,
                text=True,
                timeout=30
            )

            output = result.stdout
            if result.stderr:
                output += f"\n[STDERR]\n{result.stderr}"

            self.output_panel.setPlainText(output if output else "(No output)\n")
            self.statusBar().showMessage("JavaScript execution complete")

            os.unlink(temp_file)
        except FileNotFoundError:
            self.output_panel.setPlainText("Error: Node.js not found. Install with: sudo apt install nodejs\n")
        except subprocess.TimeoutExpired:
            self.output_panel.setPlainText("Error: Code execution timed out (30s limit)\n")
        except Exception as e:
            self.output_panel.setPlainText(f"Error: {str(e)}\n")

    def _run_cpp(self, code: str):
        """Run C/C++ code."""
        try:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.cpp', delete=False) as f:
                f.write(code)
                src_file = f.name
            exe_file = src_file.replace('.cpp', '')
            compile_result = subprocess.run(['g++', src_file, '-o', exe_file], capture_output=True, text=True, timeout=10)
            if compile_result.returncode != 0:
                self.output_panel.setPlainText(f"Compilation Error:\n{compile_result.stderr}\n")
                self.statusBar().showMessage("Compilation failed")
                os.unlink(src_file)
                return
            result = subprocess.run([exe_file], capture_output=True, text=True, timeout=30)
            output = result.stdout + (f"\n[STDERR]\n{result.stderr}" if result.stderr else "")
            self.output_panel.setPlainText(output if output else "(No output)\n")
            self.statusBar().showMessage("C++ execution complete")
            os.unlink(src_file)
            if os.path.exists(exe_file):
                os.unlink(exe_file)
        except FileNotFoundError:
            self.output_panel.setPlainText("Error: g++ not found. Install: sudo apt install g++\n")
        except subprocess.TimeoutExpired:
            self.output_panel.setPlainText("Error: Execution timed out (30s limit)\n")
        except Exception as e:
            self.output_panel.setPlainText(f"Error: {str(e)}\n")

    def _run_c(self, code: str):
        """Run C code."""
        try:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.c', delete=False) as f:
                f.write(code)
                src_file = f.name
            exe_file = src_file.replace('.c', '')
            compile_result = subprocess.run(['gcc', src_file, '-o', exe_file], capture_output=True, text=True, timeout=10)
            if compile_result.returncode != 0:
                self.output_panel.setPlainText(f"Compilation Error:\n{compile_result.stderr}\n")
                os.unlink(src_file)
                return
            result = subprocess.run([exe_file], capture_output=True, text=True, timeout=30)
            output = result.stdout + (f"\n[STDERR]\n{result.stderr}" if result.stderr else "")
            self.output_panel.setPlainText(output if output else "(No output)\n")
            self.statusBar().showMessage("C execution complete")
            os.unlink(src_file)
            if os.path.exists(exe_file):
                os.unlink(exe_file)
        except FileNotFoundError:
            self.output_panel.setPlainText("Error: gcc not found. Install: sudo apt install build-essential\n")
        except subprocess.TimeoutExpired:
            self.output_panel.setPlainText("Error: Execution timed out (30s limit)\n")
        except Exception as e:
            self.output_panel.setPlainText(f"Error: {str(e)}\n")

    def _run_rust(self, code: str):
        """Run Rust code."""
        try:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.rs', delete=False) as f:
                f.write(code)
                src_file = f.name
            exe_file = src_file.replace('.rs', '')
            compile_result = subprocess.run(['rustc', src_file, '-o', exe_file], capture_output=True, text=True, timeout=15)
            if compile_result.returncode != 0:
                self.output_panel.setPlainText(f"Compilation Error:\n{compile_result.stderr}\n")
                os.unlink(src_file)
                return
            result = subprocess.run([exe_file], capture_output=True, text=True, timeout=30)
            output = result.stdout + (f"\n[STDERR]\n{result.stderr}" if result.stderr else "")
            self.output_panel.setPlainText(output if output else "(No output)\n")
            self.statusBar().showMessage("Rust execution complete")
            os.unlink(src_file)
            if os.path.exists(exe_file):
                os.unlink(exe_file)
        except FileNotFoundError:
            self.output_panel.setPlainText("Error: rustc not found. Install from: https://www.rust-lang.org/\n")
        except subprocess.TimeoutExpired:
            self.output_panel.setPlainText("Error: Execution timed out (30s limit)\n")
        except Exception as e:
            self.output_panel.setPlainText(f"Error: {str(e)}\n")

    def _run_lua(self, code: str):
        """Run Lua code."""
        try:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.lua', delete=False) as f:
                f.write(code)
                temp_file = f.name
            result = subprocess.run(['lua', temp_file], capture_output=True, text=True, timeout=30)
            output = result.stdout + (f"\n[STDERR]\n{result.stderr}" if result.stderr else "")
            self.output_panel.setPlainText(output if output else "(No output)\n")
            self.statusBar().showMessage("Lua execution complete")
            os.unlink(temp_file)
        except FileNotFoundError:
            self.output_panel.setPlainText("Error: lua not found. Install: sudo apt install lua5.3\n")
        except subprocess.TimeoutExpired:
            self.output_panel.setPlainText("Error: Execution timed out (30s limit)\n")
        except Exception as e:
            self.output_panel.setPlainText(f"Error: {str(e)}\n")

    def _run_go(self, code: str):
        """Run Go code."""
        try:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.go', delete=False) as f:
                f.write(code)
                src_file = f.name
            result = subprocess.run(['go', 'run', src_file], capture_output=True, text=True, timeout=10)
            output = result.stdout + (f"\n[STDERR]\n{result.stderr}" if result.stderr else "")
            self.output_panel.setPlainText(output if output else "(No output)\n")
            self.statusBar().showMessage("Go execution complete")
            os.unlink(src_file)
        except FileNotFoundError:
            self.output_panel.setPlainText("Error: go not found. Install from: https://golang.org/\n")
        except subprocess.TimeoutExpired:
            self.output_panel.setPlainText("Error: Execution timed out (10s limit)\n")
        except Exception as e:
            self.output_panel.setPlainText(f"Error: {str(e)}\n")

    def _run_ruby(self, code: str):
        """Run Ruby code."""
        try:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.rb', delete=False) as f:
                f.write(code)
                temp_file = f.name
            result = subprocess.run(['ruby', temp_file], capture_output=True, text=True, timeout=30)
            output = result.stdout + (f"\n[STDERR]\n{result.stderr}" if result.stderr else "")
            self.output_panel.setPlainText(output if output else "(No output)\n")
            self.statusBar().showMessage("Ruby execution complete")
            os.unlink(temp_file)
        except FileNotFoundError:
            self.output_panel.setPlainText("Error: ruby not found. Install: sudo apt install ruby\n")
        except subprocess.TimeoutExpired:
            self.output_panel.setPlainText("Error: Execution timed out (30s limit)\n")
        except Exception as e:
            self.output_panel.setPlainText(f"Error: {str(e)}\n")

    def _run_php(self, code: str):
        """Run PHP code."""
        try:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.php', delete=False) as f:
                f.write(code)
                temp_file = f.name
            result = subprocess.run(['php', temp_file], capture_output=True, text=True, timeout=30)
            output = result.stdout + (f"\n[STDERR]\n{result.stderr}" if result.stderr else "")
            self.output_panel.setPlainText(output if output else "(No output)\n")
            self.statusBar().showMessage("PHP execution complete")
            os.unlink(temp_file)
        except FileNotFoundError:
            self.output_panel.setPlainText("Error: php not found. Install: sudo apt install php-cli\n")
        except subprocess.TimeoutExpired:
            self.output_panel.setPlainText("Error: Execution timed out (30s limit)\n")
        except Exception as e:
            self.output_panel.setPlainText(f"Error: {str(e)}\n")

    def _run_bash(self, code: str):
        """Run Bash script."""
        try:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.sh', delete=False) as f:
                f.write(code)
                temp_file = f.name
            os.chmod(temp_file, 0o755)
            result = subprocess.run(['bash', temp_file], capture_output=True, text=True, timeout=30)
            output = result.stdout + (f"\n[STDERR]\n{result.stderr}" if result.stderr else "")
            self.output_panel.setPlainText(output if output else "(No output)\n")
            self.statusBar().showMessage("Bash execution complete")
            os.unlink(temp_file)
        except subprocess.TimeoutExpired:
            self.output_panel.setPlainText("Error: Execution timed out (30s limit)\n")
        except Exception as e:
            self.output_panel.setPlainText(f"Error: {str(e)}\n")

    def _run_java(self, code: str):
        """Run Java code."""
        self.output_panel.setPlainText("Error: Java requires class compilation setup. Not supported in quick mode.\n")

    def _run_swift(self, code: str):
        """Run Swift code."""
        try:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.swift', delete=False) as f:
                f.write(code)
                temp_file = f.name
            result = subprocess.run(['swift', temp_file], capture_output=True, text=True, timeout=10)
            output = result.stdout + (f"\n[STDERR]\n{result.stderr}" if result.stderr else "")
            self.output_panel.setPlainText(output if output else "(No output)\n")
            self.statusBar().showMessage("Swift execution complete")
            os.unlink(temp_file)
        except FileNotFoundError:
            self.output_panel.setPlainText("Error: swift not found. Install from: https://swift.org/\n")
        except subprocess.TimeoutExpired:
            self.output_panel.setPlainText("Error: Execution timed out (10s limit)\n")
        except Exception as e:
            self.output_panel.setPlainText(f"Error: {str(e)}\n")

    def _run_kotlin(self, code: str):
        """Run Kotlin code."""
        self.output_panel.setPlainText("Error: Kotlin requires JVM setup. Not supported in quick mode.\n")

    def _run_typescript(self, code: str):
        """Run TypeScript code (via Node.js)."""
        try:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.ts', delete=False) as f:
                f.write(code)
                temp_file = f.name
            result = subprocess.run(['npx', 'ts-node', temp_file], capture_output=True, text=True, timeout=10)
            output = result.stdout + (f"\n[STDERR]\n{result.stderr}" if result.stderr else "")
            self.output_panel.setPlainText(output if output else "(No output)\n")
            self.statusBar().showMessage("TypeScript execution complete")
            os.unlink(temp_file)
        except FileNotFoundError:
            self.output_panel.setPlainText("Error: ts-node not found. Install: npm install -g ts-node\n")
        except subprocess.TimeoutExpired:
            self.output_panel.setPlainText("Error: Execution timed out (10s limit)\n")
        except Exception as e:
            self.output_panel.setPlainText(f"Error: {str(e)}\n")


def main():
    app = QApplication(sys.argv)
    editor = ChamignionEditor()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
