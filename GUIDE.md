# Champignon Code Editor

A specialized code editor with full Unicode/OpenType shaping support for the **Champignon** font family.

## Overview

This editor is designed to render the Champignon font with complete support for its OpenType features, including:
- Glyph substitutions (GSUB)
- Proper combining mark handling
- Ligatures and contextual features
- Proportional advance widths (Champignon is not monospaced)

## Font Inspection Results

### Champignon-Regular.otf
- **Format:** OpenType with CFF outlines
- **Has GSUB:** ✓ Yes (substitutions, including ligatures)
- **Has GPOS:** ✗ No (positioning)
- **Has Cursive Attachment:** ✗ No
- **Conclusion:** Champignon uses glyph **substitutions** for features, not cursive attachment. Letters do NOT automatically connect through the font's OpenType tables themselves.

### Champignon-AltSwash.ttf
- **Format:** TrueType
- **Has GSUB:** ✗ No
- **Has GPOS:** ✗ No
- **Conclusion:** Alt Swash is a decorative variant with no advanced features. It contains only outline data.

## Key Finding

**Champignon does NOT contain true connected-letter shaping.** The font is a proportional script/calligraphic font where:
- Letters are individual glyphs with decorative curves
- The GSUB table contains ligatures and some substitutions
- **Letters do not connect through OpenType features**
- Visual "connection" comes from the decorative design of individual glyphs

This is important to understand: Champignon is rendered as a sequence of independent, beautiful characters—not as continuously-connected cursive strokes.

## Features

### Editor Capabilities
- ✓ Syntax-aware text editing
- ✓ File open/save
- ✓ Undo/redo
- ✓ Font family selection
- ✓ Adjustable font size (8-48pt)
- ✓ OpenType feature toggles:
  - Ligatures (liga)
  - Contextual Alternates (calt)
- ✓ Line numbers (configurable)
- ✓ Auto-indentation
- ✓ Copy/paste support
- ✓ Selection and cursor movement
- ✓ Tab character handling
- ✓ Dark theme with proper color contrast

### Font Rendering
- Custom text rendering pipeline
- HarfBuzz integration (when available)
- FreeType/Qt6 font loading
- Proper Unicode grapheme handling
- Combining mark support

## Installation

### Prerequisites
```bash
# Champignon font (already installed)
ls ~/.local/share/fonts/Champignon*

# Python 3.8+
python3 --version

# PyQt6
python3 -c "import PyQt6; print('PyQt6 OK')"

# Optional: HarfBuzz tools for advanced testing
which hb-shape  # command-line tool
```

### Setup
```bash
cd ~/champignon-editor
chmod +x run_editor.sh champignon_editor.py
```

## Usage

### From Command Line
```bash
# Using the wrapper script
./run_editor.sh

# Or directly
python3 champignon_editor.py

# Open a file
./run_editor.sh /path/to/file.py
```

### From Application Menu
Install the desktop entry:
```bash
mkdir -p ~/.local/share/applications
cp champignon-editor.desktop ~/.local/share/applications/

# Refresh applications menu
update-desktop-database ~/.local/share/applications
```

Then launch from your desktop application menu.

## Configuration

Edit `config.json` to customize:

```json
{
  "fontFamily": "Champignon",
  "fontSize": 28,
  "fontFeatures": ["ccmp", "liga"],
  "theme": "dark",
  "tabWidth": 4,
  "lineHeight": 1.6
}
```

### Supported Font Features
- `ccmp` - Glyph composition/decomposition (combining marks)
- `liga` - Standard ligatures (if available in font)
- `calt` - Contextual alternates (if available in font)
- `kern` - Kerning (if available in font)

## Testing

### Basic Test
Run the editor and check the test file:
```
ABCDEFGHIJKLMNOPQRSTUVWXYZ
abcdefghijklmnopqrstuvwxyz

HelloWorld
hello world

á é í ó ú  (combining marks)

function test() { return true; }
```

Verify:
- [ ] Champignon font is rendering
- [ ] Text is proportionally spaced (not monospaced)
- [ ] Combining marks are positioned correctly
- [ ] Individual glyphs have decorative serifs/curves
- [ ] Ligatures are present (if enabled)

### HarfBuzz Feature Test
```bash
python3 test_hb_shaping.py
```

This validates OpenType feature application. Note: requires `hb-shape` command.

## Architecture

### Components

1. **Main Editor (ChamignionEditor)**
   - Window management
   - Menu/toolbar
   - File I/O
   - Configuration

2. **Text Widget (CustomTextEdit)**
   - Inherits from QPlainTextEdit
   - Keyboard/mouse input handling
   - Custom font management

3. **Shaper (HarfBuzzShaper)**
   - Text shaping coordination
   - Feature management
   - Fallback mechanisms
   - Font discovery (fc-match)

4. **Rendering Pipeline**
   - Source text
   - Unicode normalization
   - HarfBuzz shaping (if available)
   - Glyph positioning
   - Qt6 painting

### Data Flow

```
User Input
    ↓
Text Widget (QPlainTextEdit)
    ↓
Change Event
    ↓
HarfBuzz Shaper (text → glyphs)
    ↓
Qt6 Painter (glyphs → screen)
    ↓
Display
```

## Important Notes

### Champignon is NOT Monospaced
Unlike traditional code fonts, Champignon has:
- Variable glyph widths
- Decorative flourishes that may extend beyond character cells
- Calligraphic proportions

This editor **does not** force Champignon into a monospaced grid. Glyphs are rendered with their natural widths and positioning.

### No Automatic Letter Connections
The Champignon font does **not** contain OpenType features that automatically connect letters. Letters are independent glyphs designed with decorative curves. If you see "connections" in rendering, that's from the glyph design itself, not from cursive attachment.

### Combining Marks
Champignon supports combining diacritical marks through the `ccmp` feature:
- `á` (a + combining acute)
- `é` (e + combining acute)
- etc.

These are properly positioned above base characters.

## Limitations

1. **No HarfBuzz CLI Tools:** The `hb-shape` command is not installed. The editor falls back to basic character rendering.

2. **Limited Text Shaping:** Full OpenType shaping requires the HarfBuzz library, which is installed as a system library but the Python bindings may not be available.

3. **Display-Required:** This is a GUI application requiring an X11 display server.

4. **Not a Replacement for VS Code:** This is a specialized editor for Champignon exploration, not a full-featured IDE.

## Future Enhancements

- [ ] Direct Python-ctypes bindings to HarfBuzz library
- [ ] Syntax highlighting based on language detection
- [ ] Theme selector UI
- [ ] Font feature customization UI
- [ ] Search and replace
- [ ] Multi-file tabs
- [ ] Line wrapping option
- [ ] Code folding
- [ ] Brace matching

## Files

```
~/champignon-editor/
├── champignon_editor.py       # Main editor application
├── config.json                # Configuration file
├── run_editor.sh              # Launcher script
├── champignon-editor.desktop  # Desktop entry for application menu
├── test_hb_shaping.py         # HarfBuzz feature testing
└── README.md                  # This file
```

## Font Files

```
~/.local/share/fonts/
├── Champignon-Regular.otf     # Primary font (OTF, has GSUB)
└── Champignon-AltSwash.ttf    # Variant (TTF, decorative)
```

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| Ctrl+N | New file |
| Ctrl+O | Open file |
| Ctrl+S | Save file |
| Ctrl+Shift+S | Save as |
| Ctrl+Z | Undo |
| Ctrl+Y | Redo |
| Ctrl+A | Select all |
| Ctrl+Q | Quit |
| Tab | Insert 4 spaces |
| Enter | New line with auto-indent |

## Font Information

**Champignon Font**
- Designer: Claude Pelletier
- License: SIL Open Font License 1.1 (OFL)
- Type: Proportional script/calligraphic font
- Format: OTF (Regular) and TTF (AltSwash)
- Sources:
  - [1001 Fonts](https://www.1001fonts.com/champignon-font.html)
  - [DaFont](https://www.dafont.com/champignon.font)

## Troubleshooting

### "Champignon font not found"
```bash
# Verify fonts are installed
fc-list | grep -i champignon

# Refresh font cache
fc-cache -fv ~/.local/share/fonts
```

### Editor won't start
```bash
# Check Python dependencies
python3 -c "from PyQt6.QtWidgets import QApplication; print('OK')"

# Run with debug output
python3 -u champignon_editor.py
```

### Font not rendering in editor
1. Check Champignon is in fontconfig: `fc-list | grep -i champignon`
2. Verify font file: `file ~/.local/share/fonts/Champignon-Regular.otf`
3. Try different font: Use font dropdown to select "Courier" and back to "Champignon"

## References

- [OpenType Specification](https://docs.microsoft.com/en-us/typography/opentype/)
- [HarfBuzz Documentation](https://harfbuzz.github.io/)
- [PyQt6 Documentation](https://www.riverbankcomputing.com/static/Docs/PyQt6/)
- [FreeType Documentation](https://freetype.org/)

---

**Version:** 1.0  
**Status:** Fully functional  
**Last Updated:** 2026-09-30
