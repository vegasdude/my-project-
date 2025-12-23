#!/usr/bin/env python3
"""
project_health.py - Lightweight project health check.

Checks for:
- Presence of README, LICENSE, and .gitignore
- Untracked large binary-like files
- Basic line-length stats on source files
"""

import os
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent

REQUIRED_FILES = ["README.md", "LICENSE", ".gitignore"]
TEXT_EXTENSIONS = {".py", ".js", ".ts", ".jsx", ".tsx", ".sh", ".md", ".txt"}
MAX_LINE_LENGTH = 100
LARGE_FILE_THRESHOLD_MB = 10


def check_required_files():
    print("== Required files ==")
    missing = []
    for name in REQUIRED_FILES:
        p = ROOT / name
        if p.exists():
            print(f"  ✓ {name}")
        else:
            print(f"  ✗ {name} (missing)")
            missing.append(name)
    return missing


def detect_large_untracked_files():
    print("
== Large untracked files ==")
    try:
        out = subprocess.check_output(
            ["git", "ls-files", "--others", "--exclude-standard"],
            cwd=ROOT,
            text=True,
        )
    except Exception:
        print("  (not a git repository or git not available)")
        return []

    large = []
    for rel in out.splitlines():
        p = ROOT / rel
        if not p.is_file():
            continue
        size_mb = p.stat().st_size / (1024 * 1024)
        if size_mb >= LARGE_FILE_THRESHOLD_MB:
            print(f"  ⚠ {rel} (~{size_mb:.1f} MB)")
            large.append((rel, size_mb))

    if not large:
        print("  None")
    return large


def scan_line_lengths():
    print("
== Line length report ==")
    over_limit = []

    for dirpath, _, filenames in os.walk(ROOT):
        # Skip VCS and dependencies
        if any(part in {".git", "node_modules", "dist", "build", "__pycache__"} 
               for part in Path(dirpath).parts):
            continue

        for fname in filenames:
            p = Path(dirpath) / fname
            if p.suffix not in TEXT_EXTENSIONS:
                continue
            try:
                with p.open(encoding="utf-8", errors="ignore") as fh:
                    for i, line in enumerate(fh, start=1):
                        if len(line.rstrip("
")) > MAX_LINE_LENGTH:
                            over_limit.append((p.relative_to(ROOT), i))
            except Exception:
                continue

    if not over_limit:
        print(f"  All checked files within {MAX_LINE_LENGTH} chars.")
    else:
        print(f"  Lines exceeding {MAX_LINE_LENGTH} chars:")
        for path, lineno in over_limit[:50]:
            print(f"   - {path}:{lineno}")
        if len(over_limit) > 50:
            print(f"  ... and {len(over_limit) - 50} more.")

    return over_limit


def main():
    missing = check_required_files()
    large = detect_large_untracked_files()
    over_limit = scan_line_lengths()

    print("
== Summary ==")
    if not missing and not large and not over_limit:
        print("  ✓ Project looks good!")
    else:
        print("  Review the issues above.")


if __name__ == "__main__":
    main()