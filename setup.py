#!/usr/bin/env python3
"""
Setup script for Champignon Editor
Cross-platform installation for Linux and Windows
"""

from setuptools import setup, find_packages
from pathlib import Path
import platform

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding="utf-8")

# Platform-specific requirements
install_requires = [
    "PyQt6>=6.0.0",
]

setup(
    name="champignon-editor",
    version="1.2.0",
    author="esp32s3",
    description="A code editor with syntax highlighting and multi-language support featuring the Champignon font",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/esp32s3/champignon-editor",
    project_urls={
        "Bug Tracker": "https://github.com/esp32s3/champignon-editor/issues",
        "Documentation": "https://github.com/esp32s3/champignon-editor",
    },
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 4 - Beta",
        "Environment :: X11 Applications :: Qt",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Editors",
    ],
    python_requires=">=3.8",
    install_requires=install_requires,
    include_package_data=True,
    entry_points={
        "console_scripts": [
            "champignon-editor=champignon_editor:main",
        ],
    },
    package_data={
        "": ["fonts/*.otf", "fonts/*.ttf", "config.json"],
    },
)
