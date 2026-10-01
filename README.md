# Champignon Editor

A modern, lightweight code editor with **syntax highlighting** and **multi-language execution** featuring the beautiful **Champignon** font.

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Platforms: Linux & Windows](https://img.shields.io/badge/Platforms-Linux%20%7C%20Windows-brightgreen.svg)]()

## Features

✨ **Syntax Highlighting**
- 7 color-coded syntax elements
- Real-time highlighting as you type
- Support for keywords, strings, numbers, comments, functions

▶️ **Multi-Language Execution**
- Python 3, JavaScript (Node.js), C/C++, Rust, Lua, Go, Ruby, PHP, Bash, Swift, TypeScript
- Auto-language detection from file extension
- 30-second execution timeout for safety
- Real-time output in integrated terminal panel

🎨 **Beautiful Typography**
- Champignon font included (SIL Open Font License)
- Proportional rendering with proper Unicode support
- Combining mark support (e.g., é, ñ, ü)
- Adjustable font size (8-48pt)

⚙️ **Developer-Friendly**
- Cross-platform (Linux & Windows)
- File open/save with UTF-8 encoding
- Undo/redo support
- Copy/paste functionality
- Dark theme optimized for coding
- Configuration file (JSON) for customization

## Supported Languages

| Language | Run | Detect | Notes |
|----------|-----|--------|-------|
| 🐍 Python | ✅ | `.py`, `def/import` | Python 3 (usually pre-installed) |
| 🟡 JavaScript | ✅ | `.js`, `function/const` | Requires Node.js |
| 🔵 TypeScript | ✅ | `.ts` | Requires `npm install -g ts-node` |
| 🔨 C/C++ | ✅ | `.c/.cpp`, `#include` | Requires g++ compiler |
| 🦀 Rust | ✅ | `.rs`, `fn main` | Requires rustc compiler |
| 🌙 Lua | ✅ | `.lua`, `local/function` | Requires Lua 5.3+ |
| 🐹 Go | ✅ | `.go`, `func main` | Requires Go compiler |
| 💎 Ruby | ✅ | `.rb` | Requires Ruby interpreter |
| 🐘 PHP | ✅ | `.php` | Requires PHP CLI |
| 🐚 Bash | ✅ | `.sh/.bash` | Bash interpreter |
| ⚡ Swift | ✅ | `.swift` | Requires Swift compiler |
| ☕ Java | ⚠️ | `.java` | Requires special setup |
| 🎯 Kotlin | ⚠️ | `.kt` | Requires JVM setup |

## Installation

### Quick Start (Linux/macOS)

```bash
git clone https://github.com/esp32s3/champignon-editor.git
cd champignon-editor
pip install -r requirements.txt
python champignon_editor.py
```

### Windows Installation

```bash
git clone https://github.com/esp32s3/champignon-editor.git
cd champignon-editor
pip install -r requirements.txt
python champignon_editor.py
```

### Via pip (once published)

```bash
pip install champignon-editor
champignon-editor
```

## Requirements

- Python 3.8 or higher
- PyQt6 (`pip install PyQt6`)
- (Optional) Language-specific tools for running code:
  - Python: usually pre-installed
  - Node.js: `sudo apt install nodejs` or download from https://nodejs.org/
  - C/C++: `sudo apt install build-essential` (Linux) or MinGW (Windows)
  - Rust: https://www.rust-lang.org/
  - Go: https://golang.org/
  - Ruby: `sudo apt install ruby`
  - PHP: `sudo apt install php-cli`
  - Lua: `sudo apt install lua5.3`
  - Swift: https://swift.org/

## Usage

### Launch the Editor

```bash
python champignon_editor.py
```

Or use the launcher script:

```bash
./run_editor.sh           # Linux/macOS
run_editor.sh             # Windows (PowerShell)
```

### Basic Workflow

1. **Write Code** - Type or paste code into the editor
2. **Syntax Highlighting** - Colors appear automatically
3. **Click ▶ Run** - Execute code in the integrated terminal
4. **See Output** - Results appear in the green output panel
5. **Save File** - `Ctrl+S` to save (auto-detects language)

### Examples

**Python:**
```python
print("Hello from Champignon Editor!")
for i in range(5):
    print(f"Number: {i}")
```

**JavaScript (requires Node.js):**
```javascript
console.log("Hello from Node.js!");
const sum = (a, b) => a + b;
console.log("5 + 3 = " + sum(5, 3));
```

**Rust (requires rustc):**
```rust
fn main() {
    println!("Hello from Rust!");
    let numbers = vec![1, 2, 3, 4, 5];
    let sum: i32 = numbers.iter().sum();
    println!("Sum: {}", sum);
}
```

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

## Font Information

**Champignon** - A beautiful proportional script/calligraphic font
- **Designer:** Claude Pelletier
- **License:** SIL Open Font License 1.1 (included in `fonts/`)
- **Files:** 
  - `Champignon-Regular.otf` (with advanced OpenType features)
  - `Champignon-AltSwash.ttf` (decorative variant)

The editor automatically installs the fonts on first run.

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl+N` | New file |
| `Ctrl+O` | Open file |
| `Ctrl+S` | Save file |
| `Ctrl+Shift+S` | Save as |
| `Ctrl+Z` | Undo |
| `Ctrl+Y` | Redo |
| `Ctrl+A` | Select all |
| `Ctrl+C` | Copy |
| `Ctrl+V` | Paste |
| `Ctrl+X` | Cut |
| `Ctrl+Q` | Quit |
| `Tab` | Insert 4 spaces |
| `▶ Button` | Run code |

## Architecture

```
champignon-editor/
├── champignon_editor.py      # Main application (1000+ lines)
├── config.json               # Configuration
├── fonts/                    # Champignon font files
│   ├── Champignon-Regular.otf
│   └── Champignon-AltSwash.ttf
├── requirements.txt          # Python dependencies
├── setup.py                  # Installation script
└── README.md                 # This file
```

### Key Classes

- `ChamignionEditor` - Main window and application logic
- `CustomTextEdit` - Text widget with syntax highlighting
- `SyntaxHighlighter` - PyQt6 syntax highlighting
- `HarfBuzzShaper` - Text shaping interface

## Cross-Platform Support

### Linux ✅
- Tested on Ubuntu 26.04, 22.04
- Full support for all features
- Font installation automatic

### Windows ✅
- Python 3.8+ required
- PyQt6 works natively
- Compiler tools optional but recommended

### macOS
- Should work but untested
- Report issues on GitHub

## Known Limitations

1. **30-second execution timeout** - Prevents infinite loops
2. **No interactive input** - Code can't read from stdin
3. **Limited IDE features** - No debugging, autocomplete, or refactoring
4. **Java/Kotlin** - Require special build setup (contributions welcome!)

## Troubleshooting

**"ModuleNotFoundError: No module named 'PyQt6'"**
```bash
pip install PyQt6
```

**"Error: [Language] not found"**
- Install the language/runtime as shown in the Requirements section

**"Error: Code execution timed out"**
- Your code took longer than 30 seconds
- Check for infinite loops or expensive operations

**"No output"**
- Code ran but produced no output
- Add `print()` or `console.log()` statements

**Font not rendering on Windows**
- Fonts are included in `fonts/` folder
- Editor auto-installs on first run
- Manually: Copy `fonts/*.{otf,ttf}` to `C:\Windows\Fonts`

## Contributing

Contributions welcome! Areas for improvement:

- [ ] More language support (Java, Kotlin, Elixir, etc.)
- [ ] Bracket matching and auto-closing
- [ ] Search and replace
- [ ] Multiple file tabs
- [ ] Themes customization UI
- [ ] Code folding
- [ ] Plugin system

Please open an issue or submit a PR!

## License

MIT License - See [LICENSE](LICENSE) file

**Fonts:** Champignon font is licensed under the SIL Open Font License 1.1

## Acknowledgments

- **Champignon Font** - Claude Pelletier
- **PyQt6** - Riverbank Computing
- **HarfBuzz** - Behdad Esfahbod & contributors

## Contact

- **Author:** esp32s3
- **GitHub:** https://github.com/esp32s3/champignon-editor
- **Issues:** https://github.com/esp32s3/champignon-editor/issues

---

**Version:** 1.2.0  
**Last Updated:** 2026-09-30  
**Status:** ✅ Fully Functional

Happy coding with Champignon! 🎨✨
