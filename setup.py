"""
Supercode - Setup configuration
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="supercode",
    version="0.1.0",
    author="fishing-ainpm",
    author_email="",
    description="A Python project",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/fishing-ainpm/supercode",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=[
        # Add your dependencies here from requirements.txt
    ],
    entry_points={
        "console_scripts": [
            "supercode=supercode.cli:main",
        ],
    },
)
