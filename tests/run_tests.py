
#!/usr/bin/env python3
"""
Comprehensive test runner with coverage reporting.
"""

import sys
import subprocess
from pathlib import Path


def run_tests():
    """Run all tests with coverage."""
    project_root = Path(__file__).parent.parent
    
    print("=" * 80)
    print("Running JobFinder Pro Test Suite")
    print("=" * 80)
    
    # Run pytest with coverage
    cmd = [
        "pytest",
        "tests/",
        "-v",
        "--tb=short",
        "--cov=api",
        "--cov-report=term-missing",
        "--cov-report=html",
        "-p", "no:warnings"
    ]
    
    print(f"\nCommand: {' '.join(cmd)}\n")
    
    result = subprocess.run(cmd, cwd=project_root)
    
    if result.returncode == 0:
        print("\n" + "=" * 80)
        print("✅ All tests passed!")
        print("=" * 80)
        print("\nCoverage report generated in: htmlcov/index.html")
    else:
        print("\n" + "=" * 80)
        print("❌ Some tests failed!")
        print("=" * 80)
        sys.exit(1)


if __name__ == "__main__":
    run_tests()
