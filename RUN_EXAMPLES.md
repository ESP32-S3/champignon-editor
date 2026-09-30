# Champignon Editor - Run Button Examples

## Quick Test Examples

### Example 1: Python - Hello World
Copy and paste this code, then click ▶ Run:

```python
print("Hello from Champignon Editor!")
print("Python is running inside the editor")

# Try a loop
for name in ["Alice", "Bob", "Charlie"]:
    print(f"Welcome, {name}!")
```

**Expected Output:**
```
Hello from Champignon Editor!
Python is running inside the editor
Welcome, Alice!
Welcome, Bob!
Welcome, Charlie!
```

---

### Example 2: Python - List Operations
```python
numbers = [1, 2, 3, 4, 5]
total = sum(numbers)
average = total / len(numbers)

print(f"Numbers: {numbers}")
print(f"Sum: {total}")
print(f"Average: {average}")
```

**Expected Output:**
```
Numbers: [1, 2, 3, 4, 5]
Sum: 15
Average: 3.0
```

---

### Example 3: Python - Combining Marks Test
```python
# Test Unicode combining marks with Champignon font
text = "Café, naïve, résumé, deja vu"
print("Unicode text with combining marks:")
print(text)
print(f"Length: {len(text)}")
```

**Expected Output:**
```
Unicode text with combining marks:
Café, naïve, résumé, deja vu
Length: 31
```

---

### Example 4: JavaScript - Simple Calculator
Save as `.js` file, then click ▶ Run (requires Node.js):

```javascript
function add(a, b) {
    return a + b;
}

const x = 10;
const y = 20;
const result = add(x, y);

console.log(`${x} + ${y} = ${result}`);
```

**Expected Output:**
```
10 + 20 = 30
```

---

### Example 5: C++ - Simple Program
Save as `.cpp` file, then click ▶ Run (requires g++):

```cpp
#include <iostream>
#include <string>

int main() {
    std::string name = "Champignon";
    int version = 1;
    
    std::cout << "Editor: " << name << std::endl;
    std::cout << "Version: " << version << std::endl;
    
    return 0;
}
```

**Expected Output:**
```
Editor: Champignon
Version: 1
```

---

### Example 6: Python - Champignon Font Test
```python
# Test Champignon font rendering through the editor
text = """
ABCDEFGHIJKLMNOPQRSTUVWXYZ
abcdefghijklmnopqrstuvwxyz

The quick brown fox jumps over the lazy dog.

áéíóú - combining marks
1234567890 - numbers
!@#$%^&*() - symbols
"""

print(text)
print("All Champignon glyphs rendered with syntax highlighting!")
```

---

### Example 7: Python - Error Handling Test
```python
# This demonstrates error output
try:
    result = 10 / 0
except ZeroDivisionError as e:
    print(f"Error caught: {e}")
    print("This error is handled gracefully")

print("Program continues after error")
```

**Expected Output:**
```
Error caught: division by zero
This error is handled gracefully
Program continues after error
```

---

## How to Test Run Button

1. **Launch the editor:**
   ```bash
   cd ~/champignon-editor && ./run_editor.sh
   ```

2. **Copy one of the examples above**

3. **Paste into the editor**

4. **Click the ▶ Run button** (green, in toolbar)

5. **View output in the panel below**

## Tips

- If code doesn't run, check the status bar for error messages
- Python code runs immediately
- JavaScript requires Node.js (`node --version`)
- C++ requires g++ compiler (`g++ --version`)
- Output panel shows STDOUT and STDERR
- 5-second timeout prevents infinite loops
- Use `Ctrl+S` to save code before running

## Troubleshooting

**"Error: Node.js not found"**
- Install: `sudo apt install nodejs`

**"Error: g++ compiler not found"**
- Install: `sudo apt install build-essential`

**"Code execution timed out"**
- Code took longer than 5 seconds
- Infinite loop? Check your code logic

**"No output"**
- Your code ran but produced no output
- Add `print()` or `console.log()` statements

---

**Happy coding with syntax highlighting and instant execution!** 🚀✨
