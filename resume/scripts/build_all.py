#!/usr/bin/env python3
"""
build_all.py — builds every resume variant defined in content/variants.yaml.

If content/variants.yaml doesn't exist yet, just builds the "general"
variant, since that's all there is.
"""

import sys
import subprocess
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
CONTENT = ROOT / "content"


def main():
    variants_file = CONTENT / "variants.yaml"
    if variants_file.exists():
        variants = yaml.safe_load(variants_file.read_text(encoding="utf-8")) or {}
        names = list(variants.keys())
    else:
        names = ["general"]

    for name in names:
        print(f"\n=== Building variant: {name} ===")
        result = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "build.py"), name],
            cwd=ROOT,
        )
        if result.returncode != 0:
            sys.exit(result.returncode)


if __name__ == "__main__":
    main()
