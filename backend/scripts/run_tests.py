#!/usr/bin/env python3
"""
Test runner script for Breakout Screener V2
"""

import argparse
import subprocess
import sys
from pathlib import Path


def run_tests(
    test_path: str = "tests/",
    coverage: bool = False,
    verbose: bool = False,
    pattern: str = None,
    html_coverage: bool = False,
    markers: str = None,
) -> int:
    """Run tests with pytest"""
    
    # Base pytest command
    cmd = ["python", "-m", "pytest"]
    
    # Add test path
    cmd.append(test_path)
    
    # Add verbosity
    if verbose:
        cmd.append("-v")
    else:
        cmd.append("-q")
    
    # Add coverage
    if coverage:
        cmd.extend([
            "--cov=src/breakout_screener",
            "--cov-report=term-missing",
        ])
        
        if html_coverage:
            cmd.append("--cov-report=html:htmlcov")
    
    # Add pattern matching
    if pattern:
        cmd.extend(["-k", pattern])
    
    # Add markers
    if markers:
        cmd.extend(["-m", markers])
    
    # Add async support
    cmd.extend(["--asyncio-mode=auto"])
    
    # Show local variables on failure
    cmd.append("--tb=short")
    
    print(f"Running command: {' '.join(cmd)}")
    
    # Run tests
    try:
        result = subprocess.run(cmd, cwd=Path(__file__).parent.parent)
        return result.returncode
    except KeyboardInterrupt:
        print("\nTests interrupted by user")
        return 1
    except Exception as e:
        print(f"Error running tests: {e}")
        return 1


def run_linting() -> int:
    """Run linting checks"""
    print("Running linting checks...")
    
    commands = [
        # Ruff linting
        ["python", "-m", "ruff", "check", "src/", "tests/"],
        # Ruff formatting check
        ["python", "-m", "ruff", "format", "--check", "src/", "tests/"],
    ]
    
    for cmd in commands:
        print(f"Running: {' '.join(cmd)}")
        try:
            result = subprocess.run(cmd, cwd=Path(__file__).parent.parent)
            if result.returncode != 0:
                return result.returncode
        except Exception as e:
            print(f"Error running linting: {e}")
            return 1
    
    print("✅ All linting checks passed")
    return 0


def run_type_checking() -> int:
    """Run type checking with mypy"""
    print("Running type checking...")
    
    cmd = ["python", "-m", "mypy", "src/breakout_screener", "--ignore-missing-imports"]
    
    try:
        result = subprocess.run(cmd, cwd=Path(__file__).parent.parent)
        if result.returncode == 0:
            print("✅ Type checking passed")
        return result.returncode
    except Exception as e:
        print(f"Error running type checking: {e}")
        return 1


def main():
    """Main test runner"""
    parser = argparse.ArgumentParser(description="Run tests for Breakout Screener V2")
    
    parser.add_argument(
        "test_path",
        nargs="?",
        default="tests/",
        help="Path to tests (default: tests/)"
    )
    
    parser.add_argument(
        "--coverage",
        "-c",
        action="store_true",
        help="Run tests with coverage report"
    )
    
    parser.add_argument(
        "--html-coverage",
        action="store_true",
        help="Generate HTML coverage report"
    )
    
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Verbose output"
    )
    
    parser.add_argument(
        "--pattern",
        "-k",
        help="Run tests matching pattern"
    )
    
    parser.add_argument(
        "--markers",
        "-m",
        help="Run tests with specific markers"
    )
    
    parser.add_argument(
        "--lint",
        action="store_true",
        help="Run linting checks"
    )
    
    parser.add_argument(
        "--type-check",
        action="store_true",
        help="Run type checking"
    )
    
    parser.add_argument(
        "--all",
        action="store_true",
        help="Run tests, linting, and type checking"
    )
    
    args = parser.parse_args()
    
    exit_code = 0
    
    # Run linting if requested
    if args.lint or args.all:
        lint_result = run_linting()
        if lint_result != 0:
            exit_code = lint_result
    
    # Run type checking if requested
    if args.type_check or args.all:
        type_result = run_type_checking()
        if type_result != 0:
            exit_code = type_result
    
    # Run tests (always run unless only linting/type checking requested)
    if not (args.lint and not args.all) and not (args.type_check and not args.all):
        test_result = run_tests(
            test_path=args.test_path,
            coverage=args.coverage or args.all,
            verbose=args.verbose,
            pattern=args.pattern,
            html_coverage=args.html_coverage,
            markers=args.markers,
        )
        if test_result != 0:
            exit_code = test_result
    
    if exit_code == 0:
        print("✅ All checks passed!")
    else:
        print("❌ Some checks failed!")
    
    sys.exit(exit_code)


if __name__ == "__main__":
    main()