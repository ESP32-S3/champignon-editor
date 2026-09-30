#!/usr/bin/env python3
"""
Test HarfBuzz shaping with Champignon font.
Validates that the font features are properly passed to HarfBuzz.
"""

import subprocess
import os
from pathlib import Path

def get_champignon_path():
    """Find Champignon font file."""
    font_dir = Path.home() / ".local" / "share" / "fonts"

    # Try Regular first (has GSUB features)
    regular = font_dir / "Champignon-Regular.otf"
    if regular.exists():
        return str(regular)

    # Try Alt Swash
    altswash = font_dir / "Champignon-AltSwash.ttf"
    if altswash.exists():
        return str(altswash)

    return None

def test_shape(text, font_path, features=None):
    """Test shaping with hb-shape."""
    if not features:
        features = ["ccmp", "liga"]

    feature_str = ",".join(features)

    try:
        result = subprocess.run(
            ["hb-shape", f"--features={feature_str}", font_path],
            input=text,
            capture_output=True,
            text=True,
            timeout=2
        )

        if result.returncode == 0:
            return result.stdout
        else:
            return f"Error: {result.stderr}"
    except FileNotFoundError:
        return "hb-shape not found"
    except Exception as e:
        return f"Exception: {e}"

def main():
    font_path = get_champignon_path()

    if not font_path:
        print("ERROR: Champignon font not found!")
        return

    print("=" * 70)
    print("CHAMPIGNON FONT HARFBUZZ SHAPING TEST")
    print("=" * 70)
    print(f"\nFont: {font_path}")
    print(f"Font type: {'OTF (CFF)' if font_path.endswith('.otf') else 'TTF'}")

    # Test strings
    test_strings = [
        ("ABCDEFGHIJKLMNOPQRSTUVWXYZ", "Uppercase"),
        ("abcdefghijklmnopqrstuvwxyz", "Lowercase"),
        ("hello world", "Lowercase with space"),
        ("aaaa bbbb cccc", "Repeated letters with spaces"),
        ("HelloWorld", "Mixed case, no space"),
        ("function test() { return true; }", "Code"),
        ("áéíóú", "Combining marks"),
    ]

    # Test with different features
    feature_sets = [
        (["ccmp"], "Basic composition"),
        (["ccmp", "liga"], "With ligatures"),
        (["ccmp", "calt"], "With contextual alternates"),
        (["ccmp", "liga", "calt"], "With all features"),
    ]

    print("\n" + "-" * 70)
    print("SHAPING TESTS")
    print("-" * 70)

    for text, desc in test_strings:
        print(f"\nText: {text!r} ({desc})")
        print("-" * 70)

        for features, feat_desc in feature_sets:
            print(f"\n  Features: {feat_desc} {features}")
            output = test_shape(text, font_path, features)

            # Show first 200 chars of output
            if output.startswith("Error") or output.startswith("Exception"):
                print(f"    {output}")
            else:
                lines = output.strip().split('\n')
                for line in lines[:3]:
                    print(f"    {line}")
                if len(lines) > 3:
                    print(f"    ... ({len(lines)} glyphs total)")

    print("\n" + "=" * 70)
    print("TEST COMPLETE")
    print("=" * 70)

    # Summary
    print("\nFONT FEATURE CAPABILITIES:")
    print("-" * 70)

    # Check what features are actually supported
    capabilities = {}
    for features, feat_desc in feature_sets[1:]:  # Skip basic composition
        result = test_shape("hello world", font_path, features)
        capabilities[feat_desc] = "✓" if not result.startswith("Error") else "✗"

    for feat, status in capabilities.items():
        print(f"  {status} {feat}")

if __name__ == "__main__":
    main()
