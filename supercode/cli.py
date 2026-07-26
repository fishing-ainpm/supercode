"""
Command Line Interface for Supercode
"""

import argparse
import sys
from . import __version__
from .main import run


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="Supercode - A Python project",
        prog="supercode"
    )
    
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}"
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose output"
    )
    
    args = parser.parse_args()
    
    if args.verbose:
        print(f"Supercode v{__version__}")
        print("Verbose mode enabled")
    
    return run()


if __name__ == "__main__":
    sys.exit(main())
