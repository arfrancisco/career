#!/usr/bin/env python3
"""
build.py — renders content/*.yaml + content/*.md into a .tex file using
templates/resume.tex.jinja, then compiles it to a PDF with pdflatex.

Usage:
    python3 scripts/build.py [variant]

    variant   Optional. Name of a resume variant (see content/variants.yaml).
              Defaults to "general". Filters experience entries by tag.

This script is intentionally simple and dependency-light (Jinja2 + PyYAML).
No custom templating language, no hidden magic. See README.md for the
full explanation of why this approach was chosen over a heavier framework.
"""

import sys
import subprocess
from pathlib import Path

import yaml
from jinja2 import Environment, FileSystemLoader

ROOT = Path(__file__).resolve().parent.parent
CONTENT = ROOT / "content"
TEMPLATES = ROOT / "templates"
OUTPUT = ROOT / "output"


def load_yaml(name):
    path = CONTENT / name
    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return data or []


def load_text(name):
    path = CONTENT / name
    return path.read_text(encoding="utf-8").strip()


def escape_latex(value):
    """Escape LaTeX special characters in plain-text content values.

    Applied automatically to every string rendered through \\VAR{...} via
    the Jinja finalize hook below, so content files can contain normal
    characters like &, %, # without breaking compilation.
    """
    if not isinstance(value, str):
        return value
    replacements = {
        "\\": r"\textbackslash{}",
        "&": r"\&",
        "%": r"\%",
        "$": r"\$",
        "#": r"\#",
        "_": r"\_",
        "{": r"\{",
        "}": r"\}",
        "~": r"\textasciitilde{}",
        "^": r"\textasciicircum{}",
    }
    # Do backslash first so we don't double-escape the replacements we insert.
    out = value.replace("\\", "\x00BACKSLASH\x00")
    for char, repl in replacements.items():
        if char == "\\":
            continue
        out = out.replace(char, repl)
    out = out.replace("\x00BACKSLASH\x00", r"\textbackslash{}")
    return out


def get_variant_tags(variant_name):
    """Look up which experience tags a variant includes, if variants.yaml exists."""
    variants_file = CONTENT / "variants.yaml"
    if not variants_file.exists():
        return None  # no filtering — include everything
    variants = yaml.safe_load(variants_file.read_text(encoding="utf-8")) or {}
    variant = variants.get(variant_name)
    if variant is None:
        available = ", ".join(variants.keys()) or "(none defined)"
        sys.exit(
            f"Unknown resume variant '{variant_name}'. "
            f"Available variants: {available}"
        )
    return variant.get("include_tags")  # None means "include everything"


def filter_by_tags(entries, include_tags):
    if include_tags is None:
        return entries
    filtered = []
    for entry in entries:
        tags = entry.get("tags")
        if not tags or any(t in include_tags for t in tags):
            filtered.append(entry)
    return filtered


def main():
    variant_name = sys.argv[1] if len(sys.argv) > 1 else "general"
    include_tags = get_variant_tags(variant_name)

    personal = load_yaml("personal.yaml")
    summary = load_text("summary.md")
    skills = load_yaml("skills.yaml")
    experience = filter_by_tags(load_yaml("experience.yaml"), include_tags)
    education = load_yaml("education.yaml")
    projects = filter_by_tags(load_yaml("projects.yaml"), include_tags)

    env = Environment(
        loader=FileSystemLoader(str(TEMPLATES)),
        block_start_string=r"\BLOCK{",
        block_end_string="}",
        variable_start_string=r"\VAR{",
        variable_end_string="}",
        comment_start_string=r"\#{",
        comment_end_string="}",
        trim_blocks=True,
        lstrip_blocks=True,
        finalize=escape_latex,
    )
    template = env.get_template("resume.tex.jinja")

    rendered = template.render(
        personal=personal,
        summary=summary,
        skills=skills,
        experience=experience,
        education=education,
        projects=projects,
    )

    OUTPUT.mkdir(exist_ok=True)
    tex_path = OUTPUT / f"resume-{variant_name}.tex"
    tex_path.write_text(rendered, encoding="utf-8")
    print(f"Wrote {tex_path}")

    # Compile with pdflatex, run twice for stable references/margins.
    for _ in range(2):
        result = subprocess.run(
            [
                "pdflatex",
                "-interaction=nonstopmode",
                "-halt-on-error",
                f"-output-directory={OUTPUT}",
                str(tex_path),
            ],
            cwd=ROOT,
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            print(result.stdout[-4000:])
            print(result.stderr[-2000:])
            sys.exit(f"pdflatex failed for variant '{variant_name}'")

    pdf_path = OUTPUT / f"resume-{variant_name}.pdf"
    print(f"Built {pdf_path}")


if __name__ == "__main__":
    main()
